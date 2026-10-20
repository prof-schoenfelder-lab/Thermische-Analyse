"""LTI backend (1.3 with 1.1 fallback) for the Thermodynamik answer checker.

Hosting-neutral prototype: Flask + SQLite. OPAL launches via LTI 1.3
(/lti/login -> OIDC -> /lti/launch13) or LTI 1.1 (POST /lti/launch); the user
is pseudonymized (salted hash), receives a signed token via URL fragment and is
redirected to the static site. The site posts answer results to /api/results
with that token.

Environment variables (see .env.example):
  LTI_CONSUMER_KEY / LTI_CONSUMER_SECRET  shared with the OPAL course element
  SECRET_KEY                              signs session tokens
  USER_SALT                               salt for pseudonymization
  SITE_URL                                where to redirect after launch
  ALLOWED_ORIGINS                         comma-separated CORS origins
  DB_PATH                                 SQLite file (default: results.db)
  PCNAMES_PATH                            JSON {ip: "Pool-PC 07"} fürs Dashboard
                                          (default: pc-names.json, auto-reload)
"""

import base64
import datetime
import re
import socket
import hashlib
import json
import math
import os
import secrets
import sqlite3
import threading
import time
import urllib.parse

import jwt
import requests as http_requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from html import escape, unescape

from flask import Flask, g, jsonify, redirect, request, send_from_directory
from itsdangerous import BadSignature, URLSafeTimedSerializer
from oauthlib.oauth1 import RequestValidator, SignatureOnlyEndpoint

CONSUMER_KEY = os.environ.get("LTI_CONSUMER_KEY", "strukturmechanik")
CONSUMER_SECRET = os.environ.get("LTI_CONSUMER_SECRET", "change-me")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
USER_SALT = os.environ.get("USER_SALT", "dev-salt-change-me")
SITE_URL = os.environ.get("SITE_URL", "https://prof-schoenfelder-lab.github.io/Thermische-Analyse/")
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get(
    "ALLOWED_ORIGINS", "https://prof-schoenfelder-lab.github.io,http://localhost:8000"
).split(",") if o.strip()]
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "results.db"))
ANSWERS_PATH = os.environ.get("ANSWERS_PATH", os.path.join(os.path.dirname(__file__), "answers.json"))
TOKEN_MAX_AGE = 60 * 60 * 24 * 90  # 90 days

# LTI 1.3 platform data — in OPAL unter "Tool Konfiguration" ablesbar
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
LTI13_ISSUER = os.environ.get("LTI13_ISSUER", "https://bildungsportal.sachsen.de/opal")
LTI13_CLIENT_ID = os.environ.get("LTI13_CLIENT_ID", "")
LTI13_AUTH_URL = os.environ.get("LTI13_AUTH_URL", "https://bildungsportal.sachsen.de/opal/ltiauth/")
LTI13_KEYSET_URL = os.environ.get("LTI13_KEYSET_URL", "https://bildungsportal.sachsen.de/opal/restapi/lti/keys")
LTI13_DEPLOYMENT_ID = os.environ.get("LTI13_DEPLOYMENT_ID", "1")
LTI13_TOKEN_URL = os.environ.get("LTI13_TOKEN_URL", "https://bildungsportal.sachsen.de/opal/restapi/lti/token")
AGS_ENABLED = os.environ.get("AGS_ENABLED", "1") == "1"
DASHBOARD_TOKEN = os.environ.get("DASHBOARD_TOKEN", "")
PRIVATE_KEY_PATH = os.environ.get("PRIVATE_KEY_PATH", os.path.join(os.path.dirname(__file__), "lti_private.pem"))

app = Flask(__name__)
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="ac-session")


# --- database ---------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            pseudonym TEXT PRIMARY KEY,
            context_id TEXT,
            outcome_url TEXT,
            result_sourcedid TEXT,
            sub_enc TEXT,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS results (
            pseudonym TEXT NOT NULL,
            qid TEXT NOT NULL,
            best REAL NOT NULL DEFAULT 0,
            max REAL NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            updated_at REAL,
            PRIMARY KEY (pseudonym, qid)
        );
        CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            who TEXT NOT NULL,
            page TEXT,
            created_at REAL,
            done_at REAL
        );
        -- Hilfe-App: Push-Abos der Geräte (nur Dozent, per Dashboard-Schlüssel)
        CREATE TABLE IF NOT EXISTS push_abos (
            endpoint TEXT PRIMARY KEY,
            abo TEXT NOT NULL,
            created_at REAL
        );
        -- falsche Zahlenwerte, anonym (ohne Pseudonym): welche Fehler passieren?
        CREATE TABLE IF NOT EXISTS wrong_values (
            qid TEXT NOT NULL,
            value REAL NOT NULL,
            created_at REAL NOT NULL
        );
        -- gezählte Zahleneingaben je Person: Grundlage der Nachwertung nach einer Sollwert-Korrektur
        CREATE TABLE IF NOT EXISTS eingaben (
            pseudonym TEXT NOT NULL,
            qid TEXT NOT NULL,
            versuch INTEGER NOT NULL,
            value REAL NOT NULL,
            created_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS eingaben_qid ON eingaben (qid);
        -- „Mein Spickzettel“ je Person: Auswahl und eigene Notizen als JSON, der neuere Stand gewinnt
        CREATE TABLE IF NOT EXISTS spickzettel (
            pseudonym TEXT PRIMARY KEY,
            daten TEXT NOT NULL,
            updated_at REAL
        );
        -- Sollwert-Korrekturen aus dem Dashboard: liegen über answers.json, bis der Kurstext nachgezogen ist
        CREATE TABLE IF NOT EXISTS korrekturen (
            qid TEXT PRIMARY KEY,
            answer REAL NOT NULL,
            tolerance REAL NOT NULL,
            created_at REAL NOT NULL
        );
        """
    )
    db.commit()
    # Kurs-Generation: ändert sich beim Semester-Reset; Browser mit alter
    # Generation leeren ihren localStorage automatisch statt Altdaten hochzuladen
    if not db.execute("SELECT value FROM meta WHERE key='generation'").fetchone():
        db.execute("INSERT INTO meta (key, value) VALUES ('generation', ?)",
                   (secrets.token_urlsafe(8),))
        db.commit()
    # seit wann Zahleneingaben je Person gespeichert werden; ältere Versuche lassen sich nicht nachwerten
    db.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('eingaben_seit', ?)",
               (datetime.date.today().strftime("%d.%m.%Y"),))
    db.commit()
    # Migration für Bestandsdatenbanken
    for stmt in ("ALTER TABLE users ADD COLUMN sub_enc TEXT",
                 "ALTER TABLE users ADD COLUMN name_enc TEXT",
                 "ALTER TABLE help_requests ADD COLUMN text TEXT"):
        try:
            db.execute(stmt)
            db.commit()
        except sqlite3.OperationalError:
            pass
    db.close()


# --- LTI 1.1 signature validation -------------------------------------------

class LTIValidator(RequestValidator):
    enforce_ssl = False  # TLS termination happens at the reverse proxy
    client_key_length = (3, 64)
    nonce_length = (8, 64)

    @property
    def dummy_client(self):
        return "dummy-" + CONSUMER_KEY

    def validate_client_key(self, client_key, request):
        return client_key == CONSUMER_KEY

    def get_client_secret(self, client_key, request):
        if client_key == CONSUMER_KEY:
            return CONSUMER_SECRET
        return "dummy-secret"

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
                                     request, request_token=None, access_token=None):
        try:
            return abs(time.time() - int(timestamp)) < 900
        except (TypeError, ValueError):
            return False


lti_endpoint = SignatureOnlyEndpoint(LTIValidator())


def pseudonymize(user_id):
    return hashlib.sha256((USER_SALT + ":" + user_id).encode()).hexdigest()[:32]


# Verschlüsselte Ablage der OPAL-Nutzer-ID — nötig NUR für den Noten-Rückkanal
# (AGS verlangt die originale LTI-sub). Nur der Server kann sie entschlüsseln.
fernet = Fernet(base64.urlsafe_b64encode(hashlib.sha256((SECRET_KEY + ":sub-enc").encode()).digest()))


# Akademische Grade/Anreden, die OPAL vor den Namen setzt (Fallback-Pfad,
# wenn nur der zusammengesetzte "name"-Claim kommt)
_TITLES = {"master", "bachelor", "dr.", "dr", "prof.", "prof", "dipl.-ing.",
           "m.eng.", "b.eng.", "m.sc.", "b.sc.", "herr", "frau"}


def strip_titles(name):
    if not name:
        return None
    words = name.split()
    while words and words[0].lower().rstrip(",") in _TITLES:
        words = words[1:]
    return " ".join(words) or None


def finish_launch(user_id, context_id, outcome_url=None, result_sourcedid=None,
                  display_name=None):
    """Upsert the pseudonymized user and redirect to the site with a session token."""
    pseudonym = pseudonymize(user_id)
    sub_enc = fernet.encrypt(user_id.encode()).decode() if AGS_ENABLED else None
    # Klarname (falls der OPAL-Baustein ihn überträgt): verschlüsselt abgelegt,
    # entschlüsselt nur fürs Dashboard — hilft beim Namenlernen im Praktikum.
    name_enc = fernet.encrypt(display_name.encode()).decode() if display_name else None
    db = get_db()
    db.execute(
        """INSERT INTO users (pseudonym, context_id, outcome_url, result_sourcedid,
                              sub_enc, name_enc, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(pseudonym) DO UPDATE SET
             context_id=excluded.context_id,
             outcome_url=COALESCE(excluded.outcome_url, users.outcome_url),
             result_sourcedid=COALESCE(excluded.result_sourcedid, users.result_sourcedid),
             sub_enc=COALESCE(excluded.sub_enc, users.sub_enc),
             name_enc=COALESCE(excluded.name_enc, users.name_enc)""",
        (pseudonym, context_id, outcome_url, result_sourcedid, sub_enc, name_enc,
         time.time()),
    )
    db.commit()
    token = serializer.dumps({"sub": pseudonym})
    return redirect(SITE_URL + "#ac_token=" + token)


# --- AGS: Punkte als Bewertung an OPAL zurückmelden ---------------------------

_ags_token = {"value": None, "exp": 0}


def ags_access_token():
    now = time.time()
    if _ags_token["value"] and _ags_token["exp"] > now + 30:
        return _ags_token["value"]
    assertion = jwt.encode(
        {"iss": LTI13_CLIENT_ID, "sub": LTI13_CLIENT_ID, "aud": LTI13_TOKEN_URL,
         "jti": secrets.token_urlsafe(12), "iat": int(now), "exp": int(now) + 300},
        private_key, algorithm="RS256", headers={"kid": "strukturmechanik-1"},
    )
    r = http_requests.post(LTI13_TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion,
        "scope": "https://purl.imsglobal.org/spec/lti-ags/scope/score",
    }, timeout=10)
    r.raise_for_status()
    data = r.json()
    _ags_token["value"] = data["access_token"]
    _ags_token["exp"] = now + int(data.get("expires_in", 3600))
    return _ags_token["value"]


_ags_lock = threading.Lock()


def push_score_async(pseudonym):
    """Gesamtpunktzahl des Users als Score an OPAL melden (fire-and-forget)."""
    if not (AGS_ENABLED and LTI13_CLIENT_ID):
        return

    def work():
        with _ags_lock:  # nacheinander: die zuletzt gesendete Meldung trägt den aktuellen Stand
            try:
                db = sqlite3.connect(DB_PATH)
                db.row_factory = sqlite3.Row
                user = db.execute("SELECT outcome_url, sub_enc FROM users WHERE pseudonym=?",
                                  (pseudonym,)).fetchone()
                if not user or not user["outcome_url"] or not user["sub_enc"]:
                    return
                total = db.execute("SELECT COALESCE(SUM(best),0) t FROM results WHERE pseudonym=?",
                                   (pseudonym,)).fetchone()["t"]
                answers = load_answers(db)
                db.close()
                # max inkl. des möglichen +1-Volltreffer-Bonus je Frage
                score_max = sum(q.get("points", 0) + 1 for q in answers.values()) or 100
                sub = fernet.decrypt(user["sub_enc"].encode()).decode()
                lineitem = user["outcome_url"]
                base, _, query = lineitem.partition("?")
                scores_url = base.rstrip("/") + "/scores" + (("?" + query) if query else "")
                http_requests.post(scores_url, json={
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "scoreGiven": total,
                    "scoreMaximum": score_max,
                    "activityProgress": "Submitted",
                    "gradingProgress": "FullyGraded",
                    "userId": sub,
                }, headers={
                    "Authorization": "Bearer " + ags_access_token(),
                    "Content-Type": "application/vnd.ims.lis.v1.score+json",
                }, timeout=10).raise_for_status()
            except Exception as e:
                app.logger.warning("AGS-Score-Push fehlgeschlagen: %s", e)

    threading.Thread(target=work, daemon=True).start()


# --- LTI 1.3 (OIDC) ----------------------------------------------------------

def load_or_create_private_key():
    if os.path.exists(PRIVATE_KEY_PATH):
        with open(PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(pem)
    os.chmod(PRIVATE_KEY_PATH, 0o600)
    return key


private_key = load_or_create_private_key()
state_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="lti13-state")


def int_to_b64(n):
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


@app.get("/lti/jwks")
def jwks():
    """Public keyset of this tool ("Keyset URL des Tools" in OPAL)."""
    pub = private_key.public_key().public_numbers()
    return jsonify({"keys": [{
        "kty": "RSA", "use": "sig", "alg": "RS256", "kid": "strukturmechanik-1",
        "n": int_to_b64(pub.n), "e": int_to_b64(pub.e),
    }]})


@app.get("/lti/pubkey")
def pubkey():
    """Public key as PEM — zum Einfügen in OPAL (Schlüsseltyp "Schlüssel"),
    wenn OPAL die Keyset-URL nicht erreichen kann (VPN-only Backend)."""
    pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem.decode(), 200, {"Content-Type": "text/plain"}


@app.route("/lti/login", methods=["GET", "POST"])
def lti13_login():
    """OIDC third-party login initiation ("Login URL des Tools" in OPAL)."""
    p = request.values
    iss = p.get("iss")
    login_hint = p.get("login_hint")
    if iss != LTI13_ISSUER:
        return f"Unbekannter Issuer: {iss}", 400
    if not login_hint:
        return "login_hint fehlt.", 400
    nonce = secrets.token_urlsafe(16)
    state = state_serializer.dumps({"nonce": nonce})
    params = {
        "scope": "openid",
        "response_type": "id_token",
        "response_mode": "form_post",
        "prompt": "none",
        "client_id": p.get("client_id") or LTI13_CLIENT_ID,
        "redirect_uri": BACKEND_URL + "/lti/launch13",
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
    }
    if p.get("lti_message_hint"):
        params["lti_message_hint"] = p.get("lti_message_hint")
    return redirect(LTI13_AUTH_URL + "?" + urllib.parse.urlencode(params))


@app.post("/lti/launch13")
def lti13_launch():
    """OIDC launch callback ("Launch URL des Tools" in OPAL)."""
    id_token = request.form.get("id_token")
    state = request.form.get("state")
    if not id_token or not state:
        return "id_token oder state fehlt.", 400
    try:
        state_data = state_serializer.loads(state, max_age=600)
    except BadSignature:
        return "Ungültiger oder abgelaufener state.", 401
    try:
        signing_key = jwt.PyJWKClient(LTI13_KEYSET_URL).get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token, signing_key.key, algorithms=["RS256"],
            audience=LTI13_CLIENT_ID or None,
            options={"verify_aud": bool(LTI13_CLIENT_ID)},
            issuer=LTI13_ISSUER,
        )
    except Exception as e:
        return f"id_token-Validierung fehlgeschlagen: {e}", 401
    if claims.get("nonce") != state_data.get("nonce"):
        return "nonce stimmt nicht überein.", 401
    if claims.get("https://purl.imsglobal.org/spec/lti/claim/message_type") != "LtiResourceLinkRequest":
        return "Unerwarteter LTI message type.", 400

    context = claims.get("https://purl.imsglobal.org/spec/lti/claim/context") or {}
    # Assignment&Grade-Service-Endpunkt für späteren Noten-Rückkanal aufheben
    ags = claims.get("https://purl.imsglobal.org/spec/lti-ags/claim/endpoint") or {}
    # given/family bevorzugen — OPALs "name"-Claim enthält den akademischen
    # Grad ("Master Felix Kaule"), der im Sitzplan stören würde
    name = " ".join(
        s for s in (claims.get("given_name"), claims.get("family_name")) if s) \
        or strip_titles(claims.get("name")) or None
    return finish_launch(
        user_id=claims["sub"],
        context_id=context.get("id"),
        outcome_url=ags.get("lineitem") or ags.get("lineitems"),
        display_name=name,
    )


# --- LTI 1.1 (Fallback) ------------------------------------------------------

@app.post("/lti/launch")
def lti_launch():
    valid, _ = lti_endpoint.validate_request(
        request.url,
        http_method="POST",
        body=request.get_data(as_text=True),
        headers={"Content-Type": request.headers.get("Content-Type", "")},
    )
    if not valid:
        return "Ungültige LTI-Signatur. Bitte Key/Secret im OPAL-Kursbaustein prüfen.", 401

    user_id = request.form.get("user_id")
    if not user_id:
        return "LTI-Launch ohne user_id.", 400
    name = " ".join(
        s for s in (request.form.get("lis_person_name_given"),
                    request.form.get("lis_person_name_family")) if s) \
        or strip_titles(request.form.get("lis_person_name_full")) or None
    return finish_launch(
        user_id=user_id,
        context_id=request.form.get("context_id"),
        outcome_url=request.form.get("lis_outcome_service_url"),
        result_sourcedid=request.form.get("lis_result_sourcedid"),
        display_name=name,
    )


# --- API for the static site -------------------------------------------------

# Zuletzt gesehene Client-Adresse je Pseudonym — bewusst NUR im RAM
# (nach Restart leer, nichts wird gespeichert). Grundlage für die
# Pool-PC-Spalte in der Praktikums-Ansicht des Dashboards.
LAST_SEEN = {}
_HOST_CACHE = {}


def client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or ""


# Optionale feste Zuordnung IP -> Anzeigename (z.B. "Pool-PC 07 / Platz 7").
# Datei wird bei Änderung automatisch neu geladen — kein Restart nötig.
PCNAMES_PATH = os.environ.get(
    "PCNAMES_PATH", os.path.join(os.path.dirname(__file__), "pc-names.json"))
_pcnames_cache = {"mtime": None, "data": {}}


def load_pcnames():
    try:
        mtime = os.path.getmtime(PCNAMES_PATH)
    except OSError:
        return {}
    if _pcnames_cache["mtime"] != mtime:
        try:
            with open(PCNAMES_PATH) as f:
                _pcnames_cache["data"] = json.load(f)
            _pcnames_cache["mtime"] = mtime
        except (OSError, ValueError):
            pass
    return _pcnames_cache["data"]


def host_label(ip):
    """Anzeigename eines Pool-PCs: erst pc-names.json, dann Reverse-DNS."""
    if not ip:
        return ""
    name = load_pcnames().get(ip)
    if name:
        return str(name)
    if ip not in _HOST_CACHE:
        label = ip
        try:
            label = socket.gethostbyaddr(ip)[0].split(".")[0]
        except OSError:
            pass
        _HOST_CACHE[ip] = label
    return _HOST_CACHE[ip]


def current_pseudonym():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        data = serializer.loads(auth[7:], max_age=TOKEN_MAX_AGE)
        pseu = data.get("sub")
        if pseu:
            try:
                LAST_SEEN[pseu] = {"ip": client_ip(), "t": time.time()}
            except Exception:
                pass
        return pseu
    except BadSignature:
        return None


@app.after_request
def add_cors(resp):
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def cors_preflight(_any):
    return "", 204


@app.post("/api/results")
def post_results():
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    results = payload.get("results") or {}
    if not isinstance(results, dict):
        return jsonify({"error": "bad payload"}), 400

    db = get_db()
    # Stand aus einem Browser, der vor „Fortschritt zurücksetzen“ oder vor dem Semester-Reset geladen wurde:
    # nicht übernehmen, der Browser leert sich dann selbst. Ohne Generation (älteres Skript) nur ablehnen,
    # wenn die Person schon einmal zurückgesetzt hat.
    aktuell, gen = nutzer_generation(db, pseudonym), payload.get("generation")
    if (gen is not None and gen != aktuell) or (gen is None and ":" in aktuell):
        return jsonify({"error": "veraltet", "generation": aktuell}), 409
    now = time.time()
    for qid, rec in list(results.items())[:500]:
        if not isinstance(rec, dict):
            continue
        try:
            best = float(rec.get("best", 0) or 0)
            qmax = float(rec.get("max", 0) or 0)
            attempts = int(rec.get("attempts", 0) or 0)
        except (TypeError, ValueError):
            continue
        # never lower an already stored best score; updated_at nur bei echter
        # Änderung bewegen — sonst würde jeder Sammel-Sync alle Zeilen als
        # "gerade bearbeitet" stempeln (Live-Ansicht im Dashboard!)
        db.execute(
            """INSERT INTO results (pseudonym, qid, best, max, attempts, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(pseudonym, qid) DO UPDATE SET
                 best=MAX(results.best, excluded.best),
                 max=excluded.max,
                 attempts=MAX(results.attempts, excluded.attempts),
                 updated_at=CASE
                   WHEN excluded.best > results.best
                     OR excluded.attempts > results.attempts
                   THEN excluded.updated_at ELSE results.updated_at END""",
            (pseudonym, str(qid)[:200], best, qmax, attempts, now),
        )
    db.commit()
    push_score_async(pseudonym)
    return jsonify({"ok": True, "stored": len(results)})


# --- server-side answer checking ---------------------------------------------

_answers_cache = {"mtime": None, "data": {}}


def load_answers(db=None):
    """answers.json (vom MkDocs-Hook erzeugt), mit Reload bei Dateiänderung. Mit `db` liegen die
    Sollwert-Korrekturen aus dem Dashboard (Tabelle korrekturen) über den Werten der Datei."""
    try:
        mtime = os.path.getmtime(ANSWERS_PATH)
    except OSError:
        return {}
    if _answers_cache["mtime"] != mtime:
        try:
            with open(ANSWERS_PATH) as f:
                _answers_cache["data"] = json.load(f)
            _answers_cache["mtime"] = mtime
        except (OSError, ValueError):
            pass
    data = _answers_cache["data"]
    if db is not None:
        korrekturen = db.execute("SELECT qid, answer, tolerance FROM korrekturen").fetchall()
        if korrekturen:
            data = dict(data)
            for qid, answer, tolerance in korrekturen:
                if "answer" in data.get(qid, {}):
                    data[qid] = dict(data[qid], answer=answer, tolerance=tolerance)
    return data


DIAG_REL = 0.03  # Eingabe passt zu einem Fehlwert bis 3 % Abweichung (mind. Aufgabentoleranz)

# Eingabe = Faktor × Lösung → typische Ursache (gilt für alle Zahlenfragen)
DIAG_FACTORS = [
    (-1, "Der Betrag stimmt, das Vorzeichen nicht: Ist nach dem Betrag gefragt, "
         "oder ist die Richtung vertauscht?"),
    (1e3, "Genau 1000-mal zu groß: Stimmen die Einheiten?"),
    (1e-3, "Genau 1000-mal zu klein: Stimmen die Einheiten?"),
]


def diagnose(q, val):
    """Wahrscheinliche Ursache eines falschen Zahlenwerts oder None. Zuerst die aufgabenspezifischen
    Fehlwerte (data-diagnose, falls answers.json sie enthält), dann die Faktoren."""
    for d in q.get("diagnose", []):
        if abs(val - d["value"]) <= max(q.get("tolerance", 0), DIAG_REL * abs(d["value"])):
            return d["hint"]
    if q["answer"]:
        for factor, hint in DIAG_FACTORS:
            if abs(val / (factor * q["answer"]) - 1) <= DIAG_REL:
                return hint
    return None


def earned_points(points, attempt_number, attempts_allowed):
    """Mastery-Prinzip: Lösen zählt voll, egal beim wievielten Versuch.
    +1 Bonuspunkt für den Volltreffer im ersten Versuch."""
    return round(points) + (1 if attempt_number <= 1 else 0)


@app.post("/api/check")
def check_answer():
    payload = request.get_json(silent=True) or {}
    qid = str(payload.get("qid") or "")
    q = load_answers(get_db()).get(qid)
    if not q:
        return jsonify({"error": "unbekannte Frage"}), 404

    attempts_allowed = int(q.get("attempts", 5))
    diagnosis = None
    if "answer" in q:
        try:
            val = float(str(payload.get("value")).replace(",", "."))
        except (TypeError, ValueError):
            return jsonify({"error": "keine Zahl"}), 400
        correct = abs(val - q["answer"]) <= q.get("tolerance", 0)
        solution = q["answer"]
        if not correct and math.isfinite(val):
            diagnosis = diagnose(q, val)
            db = get_db()
            db.execute("INSERT INTO wrong_values (qid, value, created_at) VALUES (?, ?, ?)",
                       (qid, val, time.time()))
            db.commit()
    else:
        selected = payload.get("selected")
        if not isinstance(selected, list):
            return jsonify({"error": "keine Auswahl"}), 400
        correct = sorted(str(s) for s in selected) == sorted(q["correct"])
        solution = q["correct"]

    pseudonym = current_pseudonym()
    if pseudonym:
        db = get_db()
        row = db.execute("SELECT best, attempts FROM results WHERE pseudonym=? AND qid=?",
                         (pseudonym, qid)).fetchone()
        prev_best = row["best"] if row else 0
        attempts = (row["attempts"] if row else 0)
        exhausted = prev_best <= 0 and attempts >= attempts_allowed
        if prev_best <= 0 and not exhausted:
            attempts += 1
            if "answer" in q and math.isfinite(val):
                db.execute("INSERT INTO eingaben (pseudonym, qid, versuch, value, created_at) VALUES (?, ?, ?, ?, ?)",
                           (pseudonym, qid, attempts, val, time.time()))
        earned = earned_points(q["points"], attempts, attempts_allowed) if (correct and not exhausted) else 0
        best = max(prev_best, earned)
        db.execute(
            """INSERT INTO results (pseudonym, qid, best, max, attempts, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(pseudonym, qid) DO UPDATE SET
                 best=excluded.best, max=excluded.max,
                 attempts=excluded.attempts, updated_at=excluded.updated_at""",
            (pseudonym, qid, best, q["points"], attempts, time.time()),
        )
        db.commit()
        if best > prev_best:
            push_score_async(pseudonym)
        resp = {"authed": True, "correct": correct, "earned": earned, "best": best,
                "attempts": attempts, "attemptsAllowed": attempts_allowed}
        if correct or attempts >= attempts_allowed:
            resp["solution"] = solution
        if diagnosis:
            resp["diagnosis"] = diagnosis
        return jsonify(resp)

    # Gast: keine Speicherung, Versuche zählt der Client (Selbstbetrug erlaubt)
    attempts = min(int(payload.get("attemptsUsed", 0) or 0) + 1, attempts_allowed)
    resp = {"authed": False, "correct": correct,
            "attempts": attempts, "attemptsAllowed": attempts_allowed}
    if correct or attempts >= attempts_allowed:
        resp["solution"] = solution
    if diagnosis:
        resp["diagnosis"] = diagnosis
    return jsonify(resp)


@app.post("/api/reset")
def reset_eigener_fortschritt():
    """„Fortschritt zurücksetzen“ auf Mein Fortschritt: alle Ergebnisse und Eingaben der angemeldeten Person
    löschen; die Kursseite leert danach den Browser."""
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "nicht angemeldet"}), 401
    db = get_db()
    n = db.execute("DELETE FROM results WHERE pseudonym=?", (pseudonym,)).rowcount
    db.execute("DELETE FROM eingaben WHERE pseudonym=?", (pseudonym,))
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
               ("reset:" + pseudonym, secrets.token_urlsafe(6)))
    db.commit()
    push_score_async(pseudonym)
    return jsonify({"geloescht": n, "generation": nutzer_generation(db, pseudonym)})


@app.get("/api/results")
def get_results():
    """Full stored state of the current user — for merging into localStorage."""
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "unauthorized"}), 401
    rows = get_db().execute(
        "SELECT qid, best, max, attempts FROM results WHERE pseudonym=?", (pseudonym,)
    ).fetchall()
    return jsonify({"results": {r["qid"]: {"best": r["best"], "max": r["max"],
                                           "attempts": r["attempts"]} for r in rows}})


@app.get("/api/spickzettel")
def get_spickzettel():
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "unauthorized"}), 401
    row = get_db().execute("SELECT daten FROM spickzettel WHERE pseudonym=?", (pseudonym,)).fetchone()
    return jsonify({"daten": json.loads(row["daten"]) if row else None})


@app.post("/api/spickzettel")
def post_spickzettel():
    """Stand von „Mein Spickzettel“ speichern; der Browser schickt ihn nur, wenn er neuer ist als der vom Server."""
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "unauthorized"}), 401
    daten = (request.get_json(silent=True) or {}).get("daten")
    text = json.dumps(daten, ensure_ascii=False)
    if not isinstance(daten, dict) or len(text) > 50000:
        return jsonify({"error": "bad payload"}), 400
    db = get_db()
    db.execute("INSERT OR REPLACE INTO spickzettel (pseudonym, daten, updated_at) VALUES (?, ?, ?)",
               (pseudonym, text, time.time()))
    db.commit()
    return jsonify({"ok": True})


def course_generation():
    row = get_db().execute("SELECT value FROM meta WHERE key='generation'").fetchone()
    return row["value"] if row else "0"


def nutzer_generation(db, pseudonym):
    """Kurs-Generation, nach „Fortschritt zurücksetzen“ mit einer Marke der Person: Browser mit älterem Stand
    leeren sich dann selbst, statt ihn wieder hochzuladen (wie nach dem Semester-Reset)."""
    row = db.execute("SELECT value FROM meta WHERE key=?", ("reset:" + pseudonym,)).fetchone()
    return course_generation() + (":" + row["value"] if row else "")


@app.get("/api/me")
def me():
    pseudonym = current_pseudonym()
    if not pseudonym:
        return jsonify({"error": "unauthorized"}), 401
    row = get_db().execute(
        "SELECT COALESCE(SUM(best),0) AS total, COALESCE(SUM(max),0) AS max, COUNT(*) AS n "
        "FROM results WHERE pseudonym=?",
        (pseudonym,),
    ).fetchone()
    return jsonify({
        "pseudonym": pseudonym,
        "generation": nutzer_generation(get_db(), pseudonym),
        "total_points": row["total"],
        "max_points": row["max"],
        "questions": row["n"],
    })


@app.get("/api/stats")
def stats():
    """Anonymous aggregate per question (no auth needed, no personal data)."""
    rows = get_db().execute(
        "SELECT qid, COUNT(*) AS participants, AVG(best) AS avg_best, "
        "SUM(CASE WHEN best > 0 THEN 1 ELSE 0 END) AS solved, "
        "AVG(attempts) AS avg_attempts, MAX(max) AS max "
        "FROM results GROUP BY qid ORDER BY qid"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# --- Hilfe-Warteschlange (Mini-Ticketsystem fürs Praktikum) ------------------
# Studierende melden per Button Hilfebedarf an; das Dashboard zeigt die
# Warteschlange in Meldereihenfolge. Identität: Login-Pseudonym, sonst die
# Client-IP (im Pool = Sitzplatz). Tickets verfallen automatisch.

HELP_OPEN_MAX_AGE = 3 * 3600      # offene Tickets nach 3 h automatisch schließen
HELP_TEXT_MAX = 200               # kurze Beschreibung des Problems (freiwillig)
# Einschätzung einer Anfrage aus der Beschreibung (Stichwörter, erste passende Art gilt) und dem Stand bei der
# zuletzt bearbeiteten Aufgabe. Schnelle Fälle rücken in der Hilfe-App um HELP_VORZUG nach vorn; wer länger als
# HELP_VORN wartet, bleibt in Meldereihenfolge vorn.
HELP_ARTEN = [
    ("Technik", False, ("absturz", "abgestürzt", "stürzt", "lizenz", "startet nicht", "friert", "hängt sich",
                        "fehlermeldung", "error", "öffnet nicht", "speicher", "datei", "login", "opal", "rechner")),
    ("Ergebnis passt nicht", True, ("wert", "ergebnis", "passt nicht", "stimmt nicht", "falsch", "abweich",
                                    "einheit", "temperatur", "wärmestrom", "kelvin", "°c", "faktor", "lösung")),
    ("Bedienung", True, ("wo finde", "wo ist", "finde nicht", "wie mache", "wie geht", "wie kann", "knopf",
                         "button", "menü", "auswählen", "klick", "einstellen")),
    ("Verständnis", False, ("verstehe", "warum", "wieso", "weshalb", "erklär", "unklar", "was bedeutet", "was ist")),
]
HELP_VORZUG = 5 * 60
HELP_VORN = 10 * 60


def help_zeile(db, qr):
    """Dashboard: Beschreibung und Einschätzung einer Meldung."""
    e = help_einschaetzung(db, qr["who"], qr["text"])
    return "<br><small><b>%s</b>%s%s%s</small>" % (
        escape(e["art"]), ", meist schnell" if e["schnell"] else "",
        (" · " + escape(e["kontext"])) if e["kontext"] else "", ("<br>„%s“" % escape(qr["text"])) if qr["text"] else "")


def help_text_sauber(v):
    return re.sub(r"[\x00-\x1f\x7f]+", " ", str(v or "")).strip()[:HELP_TEXT_MAX]


def help_einschaetzung(db, who, text):
    """{art, schnell, kontext}: Art aus der Beschreibung; ohne passende Beschreibung aus den Fehlversuchen."""
    t = (text or "").lower()
    art = next(((a, schnell) for a, schnell, woerter in HELP_ARTEN if any(w in t for w in woerter)), None)
    kontext = ""
    if who and not who.startswith("ip:"):
        midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        r = db.execute("SELECT qid, best, attempts FROM results WHERE pseudonym=? AND updated_at > ? "
                       "ORDER BY updated_at DESC LIMIT 1", (who, midnight)).fetchone()
        if r and r["best"] <= 0 and r["attempts"] > 0:
            kontext = "%s: %d %s" % (unescape(short_qid(r["qid"])), r["attempts"],
                                     "Fehlversuch" if r["attempts"] == 1 else "Fehlversuche")
            if not art:
                art = ("Ergebnis passt nicht", True)
    if not art:
        art = ("Verständnis" if t else "ohne Beschreibung", False)
    return {"art": art[0], "schnell": art[1], "kontext": kontext}
HELP_DONE_KEEP = 24 * 3600        # erledigte nach einem Tag löschen


def help_enabled(db):
    """Hilfe-Button nur während der Lehrveranstaltung — Schalter im Dashboard."""
    row = db.execute("SELECT value FROM meta WHERE key='help_enabled'").fetchone()
    return bool(row and row["value"] == "1")


def _help_cleanup(db):
    now = time.time()
    db.execute("UPDATE help_requests SET done_at=? WHERE done_at IS NULL AND created_at < ?",
               (now, now - HELP_OPEN_MAX_AGE))
    db.execute("DELETE FROM help_requests WHERE done_at IS NOT NULL AND done_at < ?",
               (now - HELP_DONE_KEEP,))
    db.commit()


def _help_identity():
    pseu = current_pseudonym()
    if pseu:
        return pseu
    ip = client_ip()
    return ("ip:" + ip) if ip else None


@app.get("/api/help")
def help_status():
    who = _help_identity()
    db = get_db()
    if not help_enabled(db):
        return jsonify({"enabled": False, "open": False, "position": None, "queue": 0})
    _help_cleanup(db)
    open_rows = db.execute(
        "SELECT who FROM help_requests WHERE done_at IS NULL ORDER BY created_at").fetchall()
    pos = next((i + 1 for i, r in enumerate(open_rows) if r["who"] == who), None)
    return jsonify({"enabled": True, "open": pos is not None, "position": pos,
                    "queue": len(open_rows)})


@app.post("/api/help")
def help_request():
    payload = request.get_json(silent=True) or {}
    who = _help_identity()
    if not who:
        return jsonify({"error": "keine Identität"}), 400
    db = get_db()
    if not help_enabled(db):
        return jsonify({"enabled": False, "open": False, "position": None, "queue": 0})
    _help_cleanup(db)
    if payload.get("cancel"):
        db.execute("UPDATE help_requests SET done_at=? WHERE who=? AND done_at IS NULL",
                   (time.time(), who))
        db.commit()
    elif db.execute("SELECT id FROM help_requests WHERE who=? AND done_at IS NULL", (who,)).fetchone():
        if "text" in payload:   # Beschreibung zur offenen Meldung nachreichen oder ändern
            beschreibung = help_text_sauber(payload.get("text"))
            db.execute("UPDATE help_requests SET text=? WHERE who=? AND done_at IS NULL", (beschreibung or None, who))
            db.commit()
            if beschreibung:
                e = help_einschaetzung(db, who, beschreibung)
                threading.Thread(target=hilfe_push, args=("Hilfe FEM-TD: " + hilfe_label(who),
                                 "%s: %s" % (e["art"], beschreibung)), daemon=True).start()
    else:
        beschreibung = help_text_sauber(payload.get("text"))
        db.execute("INSERT INTO help_requests (who, page, created_at, text) VALUES (?, ?, ?, ?)",
                   (who, str(payload.get("page") or "")[:200], time.time(), beschreibung or None))
        db.commit()
        offen = db.execute("SELECT COUNT(*) FROM help_requests WHERE done_at IS NULL").fetchone()[0]
        titel = "Hilfe FEM-TD: " + hilfe_label(who)
        text = short_page(str(payload.get("page") or "")) + ("" if offen == 1 else " · %d warten" % offen)
        if beschreibung:
            text += " · " + beschreibung
        threading.Thread(target=hilfe_push, args=(titel, text), daemon=True).start()
    return help_status()


# --- Hilfe-App fürs Handy -------------------------------------------------------
# Web-App unter /hilfe/ (zum Home-Bildschirm hinzufügen): nächste Anfrage mit Raum und
# Platz, Raumkarte, „Erledigt, nächster“. Push bei jeder neuen Anfrage (Web Push,
# auf dem iPhone ab iOS 16.4 für Apps vom Home-Bildschirm; die Uhr spiegelt das).
# Zugang mit dem Dashboard-Schlüssel. Den VAPID-Schlüssel legt das Backend selbst an.
HILFE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hilfe")
VAPID_PATH = os.environ.get("VAPID_PATH", os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), "vapid_private.pem"))
VAPID_SUB = os.environ.get("VAPID_SUB", "mailto:felix.kaule@htwk-leipzig.de")
HILFE_RAEUME = {"N102": 32, "N103": 20, "N104": 16}


def vapid_public():
    """Öffentlicher VAPID-Schlüssel (base64url, unkomprimierter Punkt); legt das Schlüsselpaar bei Bedarf an."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    if not os.path.exists(VAPID_PATH):
        key = ec.generate_private_key(ec.SECP256R1())
        with open(VAPID_PATH, "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                      serialization.NoEncryption()))
        os.chmod(VAPID_PATH, 0o600)
    with open(VAPID_PATH, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), None)
    raw = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def hilfe_label(who):
    """Sitzplatz einer Hilfe-Anfrage, z. B. „N103 Platz 7“; sonst Rechnername oder Pseudonym-Anfang."""
    if who.startswith("ip:"):
        return host_label(who[3:]) or who[3:]
    seen = LAST_SEEN.get(who) or {}
    return host_label(seen.get("ip", "")) or ("…" + who[:6])


def hilfe_push(titel, text):
    """Push an alle angemeldeten Geräte; abgelaufene Abos werden entfernt. Läuft im Hintergrund."""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        return
    db = sqlite3.connect(DB_PATH)
    try:
        vapid_public()
        for endpoint, abo in db.execute("SELECT endpoint, abo FROM push_abos").fetchall():
            try:
                webpush(json.loads(abo), json.dumps({"titel": titel, "text": text}),
                        vapid_private_key=VAPID_PATH, vapid_claims={"sub": VAPID_SUB},
                        ttl=600, headers={"Urgency": "high"}, timeout=10)
            except WebPushException as e:
                if e.response is not None and e.response.status_code in (404, 410):
                    db.execute("DELETE FROM push_abos WHERE endpoint=?", (endpoint,))
                    db.commit()
            except Exception:
                pass
    finally:
        db.close()


def hilfe_key_ok():
    key = request.headers.get("X-Key") or request.args.get("key")
    return bool(DASHBOARD_TOKEN) and key == DASHBOARD_TOKEN


@app.get("/hilfe/")
def hilfe_seite():
    return send_from_directory(HILFE_DIR, "index.html")


@app.get("/hilfe/<path:datei>")
def hilfe_datei(datei):
    resp = send_from_directory(HILFE_DIR, datei)
    if datei.endswith(".webmanifest"):
        resp.mimetype = "application/manifest+json"
    if datei == "sw.js":
        resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/api/hilfe")
def hilfe_liste():
    if not hilfe_key_ok():
        return jsonify({"error": "Schlüssel falsch"}), 403
    db = get_db()
    _help_cleanup(db)
    now_ts = time.time()
    eintraege = []
    for r in db.execute("SELECT id, who, page, created_at, text FROM help_requests WHERE done_at IS NULL "
                        "ORDER BY created_at").fetchall():
        label = hilfe_label(r["who"])
        m = re.match(r"^(N\d{3}) Platz (\d+)$", label)
        eintraege.append({"id": r["id"], "label": label, "raum": m.group(1) if m else None,
                          "platz": int(m.group(2)) if m else None, "seite": short_page(r["page"] or ""),
                          "wartet": int(now_ts - r["created_at"]), "text": r["text"] or "",
                          **help_einschaetzung(db, r["who"], r["text"])})
    # Reihenfolge: wer lange wartet, zuerst; sonst rücken schnelle Fälle etwas vor
    fifo = [e["id"] for e in eintraege]
    eintraege.sort(key=lambda e: (e["wartet"] <= HELP_VORN, -(e["wartet"] + (HELP_VORZUG if e["schnell"] else 0))))
    for i, e in enumerate(eintraege):
        e["vorgezogen"] = fifo.index(e["id"]) > i
    empfohlen = []
    # Es ist immer nur ein Raum belegt: der mit den meisten in der letzten halben Stunde Aktiven,
    # sonst der mit den meisten Anfragen
    zaehler = {}
    pool = pool_status(db)["entries"]
    for e in pool:
        m = re.match(r"^(N\d{3}) Platz \d+$", e["pc"])
        if m and e["idle"] < 30 * 60:
            zaehler[m.group(1)] = zaehler.get(m.group(1), 0) + 1
    if not zaehler:
        for e in eintraege:
            if e["raum"]:
                zaehler[e["raum"]] = zaehler.get(e["raum"], 0) + 1
    raum_aktiv = max(sorted(zaehler), key=lambda r: zaehler[r]) if zaehler else None
    for e in pool:
        if e["skey"] not in ("warn", "alarm"):
            continue
        label = e["pc"].replace("&hellip;", "…")
        m = re.match(r"^(N\d{3}) Platz (\d+)$", label)
        empfohlen.append({"label": label, "raum": m.group(1) if m else None, "platz": int(m.group(2)) if m else None,
                          "aufgegeben": e["skey"] == "alarm", "versuche": e["attempts"], "frage": unescape(short_qid(e["qid"])),
                          "name": e["name"], "seit": int(e["idle"])})
    empfohlen.sort(key=lambda x: (not x["aufgegeben"], -x["versuche"], x["seit"]))
    return jsonify({"an": help_enabled(db), "eintraege": eintraege, "empfohlen": empfohlen,
                    "raeume": HILFE_RAEUME, "raum_aktiv": raum_aktiv, "vapid": vapid_public()})


@app.post("/api/hilfe/erledigt")
def hilfe_erledigt():
    if not hilfe_key_ok():
        return jsonify({"error": "Schlüssel falsch"}), 403
    db = get_db()
    db.execute("UPDATE help_requests SET done_at=? WHERE id=? AND done_at IS NULL",
               (time.time(), (request.get_json(silent=True) or {}).get("id")))
    db.commit()
    return hilfe_liste()


@app.post("/api/hilfe/schalter")
def hilfe_schalter():
    if not hilfe_key_ok():
        return jsonify({"error": "Schlüssel falsch"}), 403
    db = get_db()
    an = bool((request.get_json(silent=True) or {}).get("an"))
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('help_enabled', ?)", ("1" if an else "0",))
    if not an:
        db.execute("UPDATE help_requests SET done_at=? WHERE done_at IS NULL", (time.time(),))
    db.commit()
    return hilfe_liste()


@app.post("/api/hilfe/abo")
def hilfe_abo():
    if not hilfe_key_ok():
        return jsonify({"error": "Schlüssel falsch"}), 403
    abo = (request.get_json(silent=True) or {}).get("abo") or {}
    endpoint = abo.get("endpoint", "")
    if not endpoint.startswith("https://") and not (app.debug or os.environ.get("HILFE_TEST")):
        return jsonify({"error": "ungültig"}), 400
    db = get_db()
    db.execute("INSERT OR REPLACE INTO push_abos (endpoint, abo, created_at) VALUES (?, ?, ?)",
               (endpoint, json.dumps(abo), time.time()))
    db.commit()
    return jsonify({"ok": True})


@app.get("/dashboard-help-toggle")
def help_toggle():
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter.", 403
    db = get_db()
    new = "0" if help_enabled(db) else "1"
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('help_enabled', ?)", (new,))
    if new == "0":
        # beim Ausschalten offene Meldungen mit schließen
        db.execute("UPDATE help_requests SET done_at=? WHERE done_at IS NULL", (time.time(),))
    db.commit()
    return redirect("dashboard?key=" + DASHBOARD_TOKEN)


@app.get("/dashboard-help-done")
def help_done():
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter.", 403
    db = get_db()
    db.execute("UPDATE help_requests SET done_at=? WHERE id=? AND done_at IS NULL",
               (time.time(), request.args.get("id")))
    db.commit()
    return redirect("dashboard?key=" + DASHBOARD_TOKEN)


def wrong_value_rows(db, answers, since):
    """Häufigste falsche Eingaben seit `since`: gruppiert nach erkannter Ursache,
    ohne Diagnose nach dem auf 2 Stellen gerundeten Wert (vielleicht ist der Sollwert falsch)."""
    groups = {}
    for r in db.execute("SELECT qid, value FROM wrong_values WHERE created_at > ?", (since,)):
        q = answers.get(r["qid"])
        if not q or "answer" not in q:
            continue
        hint = diagnose(q, r["value"])
        groups.setdefault((r["qid"], hint or "", "" if hint else "%.2g" % r["value"]),
                          []).append(r["value"])
    rows = ""
    for (qid, hint, _), vals in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:10]:
        vals.sort()
        # ohne erkannte Ursache: vielleicht ist der Sollwert falsch, die Vorschau zeigt die Folgen
        pruefen = "" if hint else ('<a href="dashboard-sollwerte?key=%s&amp;qid=%s&amp;answer=%s">als Sollwert?</a>'
                                   % (DASHBOARD_TOKEN, urllib.parse.quote(qid), _zahl(vals[len(vals) // 2], False)))
        rows += ('<tr><td title="%s">%s</td><td class="num">%.4g</td><td class="num">%.4g</td>'
                 '<td class="num">%d</td><td>%s</td><td class="act"><small>%s</small></td></tr>'
                 % (escape(qid), short_qid(qid), vals[len(vals) // 2],
                    answers[qid]["answer"], len(vals), hint or "<em>unbekannt</em>", pruefen))
    return rows


# --- Dashboard: Darstellung ---------------------------------------------------
# Aufgaben und Seiten lesbar statt als Pfad; Logos von der öffentlichen Kursseite.
_QTYP = {"q": "Frage", "mc": "Frage"}


def short_page(path):
    """'P1_Einfuehrung/03_Selbsttests/Uebung-3' -> 'P1 Übung 3'."""
    parts = [x for x in path.replace("/Thermische-Analyse/", "").strip("/").split("/") if x]
    if not parts:
        return ""
    name = parts[-1]
    m = re.match(r"Uebung-?0*(\d+)-?(.*)$", name)
    name = ("Übung %s %s" % m.groups()).strip() if m else name.replace("_", " ")
    return ("%s %s" % (parts[0].split("_")[0], name)) if len(parts) > 1 else name


def short_qid(qid):
    """'.../P1_Einfuehrung/03_Selbsttests/Uebung-1:q0' -> 'P1 Übung 1 · Frage 1'."""
    page, _, q = qid.rpartition(":")
    m = re.match(r"([a-z]+)(\d+)$", q)
    if not page or not m:
        return escape(qid.replace("/Thermische-Analyse/", ""))
    return escape("%s · %s %d" % (short_page(page), _QTYP.get(m.group(1), m.group(1)), int(m.group(2)) + 1))


# Kursdesign „Campus“ wie die Kursseite (docs/styles/modern.css): Source Sans Pro und HTWK-Logo von der
# Kursseite, weiße Kopfzeile, Cyan als einziger Akzent, Dunkelblau für Überschriften, getönte Flächen;
# Ampel für den Status ohne Gelb; dunkel nach Systemeinstellung
DASH_LOGO = SITE_URL + "assets/images/HTWK_white_text.svg"
DASH_CSS = """
@font-face{font-family:"Source Sans Pro";font-weight:400;font-display:swap;src:url("{SITE}assets/fonts/source-sans-pro-400.woff2") format("woff2")}
@font-face{font-family:"Source Sans Pro";font-weight:600;font-display:swap;src:url("{SITE}assets/fonts/source-sans-pro-600.woff2") format("woff2")}
@font-face{font-family:"Source Sans Pro";font-weight:700;font-display:swap;src:url("{SITE}assets/fonts/source-sans-pro-700.woff2") format("woff2")}
:root{--bg:#fff;--panel:#f2f6f9;--text:#2e3639;--text2:#566166;--text3:#87939a;--head:#022541;--line:#e2e8ec;--line2:#cdd6dc;
--accent:#009ee3;--accent-ink:#0070a6;--accent-soft:#e3f4fc;--btn-fg:#fff;--logo:brightness(0);--foot-bg:#022541;--foot-fg:#fff;
--ok:#00964e;--ok-bg:#e2f3e9;--ok-line:#9ad3b4;--warn:#b25e00;--warn-bg:#fdeedc;--warn-line:#f1b878;
--alarm:#e53009;--alarm-bg:#fce7e2;--alarm-line:#f3a58f;--idle:#87939a;--idle-bg:#eef2f5;--r:.38rem;--r-md:.6rem;--r-lg:.85rem}
@media (prefers-color-scheme:dark){:root{--bg:#0a1621;--panel:#102231;--text:#d5dee4;--text2:#a3b1ba;--text3:#74848f;--head:#fff;
--line:#1c3142;--line2:#2a465c;--accent:#18aeef;--accent-ink:#62c9f5;--accent-soft:rgba(0,158,227,.15);--btn-fg:#022541;--logo:none;
--foot-bg:#06101a;--foot-fg:#dbe4ea;--ok:#3cc583;--ok-bg:rgba(60,197,131,.14);--ok-line:rgba(60,197,131,.45);
--warn:#ffa24a;--warn-bg:rgba(255,162,74,.14);--warn-line:rgba(255,162,74,.45);--alarm:#ff6a45;--alarm-bg:rgba(255,106,69,.14);
--alarm-line:rgba(255,106,69,.45);--idle:#74848f;--idle-bg:#13283a;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 "Source Sans Pro",-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
a{color:var(--accent-ink)}
.wrap{max-width:78rem;margin:0 auto;padding:0 1.25rem}
header.top{background:var(--bg);border-bottom:1px solid var(--line)}
.topin{display:flex;align-items:center;gap:.6rem 1.4rem;padding:.8rem 1.25rem;flex-wrap:wrap}
.logo{height:1.2rem;filter:var(--logo)}
.ttl{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}
.ttl b{font-size:1.05rem;font-weight:700;color:var(--head)}
.ttl .tag{font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:.15rem .55rem;border-radius:99px;
background:var(--accent-soft);color:var(--accent-ink)}
.stamp{margin-left:auto;text-align:right;font-size:.8rem;color:var(--text3);line-height:1.45}
.stamp b{color:var(--head)}
main{padding-top:1.25rem;padding-bottom:1rem}
h2{font-size:1.2rem;font-weight:700;color:var(--head);margin:1.6rem 0 .7rem;letter-spacing:-.01em}
h3{font-size:.98rem;font-weight:700;color:var(--head);margin:0 0 .55rem}
.kicker{font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink);margin:0 0 .3rem}
.card{background:var(--bg);border:1px solid var(--line);border-radius:var(--r-lg);padding:1rem 1.15rem;margin:0 0 1rem}
.card>h2:first-child{margin-top:0}
.row2{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:1rem;align-items:start}
.queue.busy{border-color:var(--alarm-line);box-shadow:inset 4px 0 0 var(--alarm)}
.queue.busy h2{color:var(--alarm)}
p.empty{margin:0;color:var(--text3)}
ul.sw{list-style:none;margin:0;padding:0}
ul.sw li{display:grid;grid-template-columns:1fr auto auto;gap:.6rem;align-items:center;padding:.45rem 0;border-top:1px solid var(--line)}
ul.sw li:first-child{border-top:0;padding-top:0}
.switches p{font-size:.88rem;color:var(--text2);margin:.8rem 0 0}
.hero{border-radius:var(--r-lg);padding:1.1rem 1.25rem .3rem;margin:1.6rem 0 1rem;
background:radial-gradient(90% 120% at 100% 0%,var(--accent-soft) 0%,transparent 60%),var(--panel)}
.hero h2{margin:0 0 .8rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(8.5rem,1fr));gap:.75rem;margin:0 0 1rem}
.kpi{background:var(--bg);border:1px solid var(--line);border-radius:var(--r-md);padding:.75rem .95rem}
.kpi b{display:block;font-size:1.9rem;line-height:1.1;color:var(--head);font-weight:700;font-variant-numeric:tabular-nums}
.kpi span{display:block;font-size:.72rem;color:var(--text3);text-transform:uppercase;letter-spacing:.06em;margin-top:.25rem}
.kpi.good b{color:var(--ok)}
.kpi.alarm{background:var(--alarm-bg);border-color:var(--alarm-line)}.kpi.alarm b{color:var(--alarm)}
.pill,b.ok,b.done,b.warn,b.alarm,b.idle,b.hilfe,b.next{display:inline-block;border-radius:99px;padding:.12rem .55rem;font-size:.7rem;font-weight:700;
letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
b.ok,.pill.on{background:var(--ok-bg);color:var(--ok)}
b.done{background:var(--ok);color:#fff}
b.warn{background:var(--warn-bg);color:var(--warn)}
b.alarm{background:var(--alarm-bg);color:var(--alarm)}
b.idle,.pill.off{background:var(--idle-bg);color:var(--idle)}
a.btn,button.btn{display:inline-block;padding:.3rem .8rem;border-radius:.5rem;font-size:.85rem;font-weight:600;text-decoration:none;
border:1px solid var(--line2);color:var(--head);background:var(--bg);white-space:nowrap}
button.btn{font-family:inherit;cursor:pointer}
a.btn:hover,button.btn:hover{background:var(--panel)}
a.btn.go,button.btn.go{background:var(--accent);border-color:var(--accent);color:var(--btn-fg)}
a.btn.go:hover,button.btn.go:hover,a.btn.done:hover{filter:brightness(1.07)}
form.sw{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;justify-content:flex-end;margin:0}
.vorschau form.sw{justify-content:flex-start}
input.num{width:6.5rem;padding:.25rem .45rem;border:1px solid var(--line2);border-radius:.4rem;font:inherit;font-size:.9rem;
background:var(--bg);color:var(--text);font-variant-numeric:tabular-nums}
input.num.tol{width:4.5rem}
.card.vorschau{border-color:var(--accent);box-shadow:inset 4px 0 0 var(--accent)}
.card.ok{border-color:var(--ok-line);box-shadow:inset 4px 0 0 var(--ok)}
.card.ok h3{color:var(--ok)}
p.hinweis{color:var(--warn);font-weight:600}
code{font-size:.82rem;background:var(--panel);border-radius:.3rem;padding:.05rem .3rem;white-space:nowrap}
code.kopie{white-space:normal;user-select:all;cursor:copy}
a.btn.done{background:var(--ok);border-color:var(--ok);color:#fff}
.alert{background:var(--alarm-bg);border:1px solid var(--alarm-line);box-shadow:inset 4px 0 0 var(--alarm);border-radius:var(--r-md);
padding:.8rem 1rem;margin:0 0 1rem}
.alert h3{color:var(--alarm)}
ul.chips{display:flex;flex-wrap:wrap;gap:.45rem;list-style:none;margin:0;padding:0}
ul.chips li{background:var(--bg);border:1px solid var(--alarm-line);border-radius:var(--r);padding:.25rem .65rem;font-size:.9rem}
ul.chips li span{color:var(--alarm);font-weight:600;margin-left:.3rem}
p.spans{font-size:.9rem;color:var(--text2);margin:0 0 1rem}
p.spans b{color:var(--head)}
.rooms{display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-start}
.room{margin:0}
.roommap{display:grid;grid-template-columns:repeat(2,6.2rem) 1.1rem repeat(2,6.2rem);gap:.35rem}
.seat{border:1px solid var(--line);border-radius:var(--r);padding:.25rem .4rem;font-size:.74rem;min-height:2.7rem;
background:var(--panel);color:var(--text3);font-variant-numeric:tabular-nums;position:relative}
.seat b{display:block;font-size:.78rem;color:inherit}
.seat u{display:block;text-decoration:none;font-weight:600;font-size:.76rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.seat.s-ok{background:var(--ok-bg);border-color:var(--ok-line);color:var(--ok)}
.seat.s-done{background:var(--ok);border-color:var(--ok);color:#fff}
.seat.s-warn{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.seat.s-alarm{background:var(--alarm-bg);border-color:var(--alarm-line);color:var(--alarm)}
.seat.s-idle{background:var(--idle-bg);border-style:dashed;color:var(--idle)}
.seat.s-hilfe{background:#e5007d;border-color:#e5007d;border-style:solid;color:#fff}
.seat.s-next{background:var(--accent);border-color:var(--accent);border-style:solid;color:var(--btn-fg);box-shadow:inset 0 0 0 2px var(--bg)}
.seat sup{position:absolute;top:.2rem;right:.3rem;font-size:.72rem;font-weight:800}
b.hilfe{background:#e5007d;color:#fff}
b.next{background:var(--accent);color:var(--btn-fg)}
p.front{font-size:.76rem;color:var(--text3);margin:.5rem 0 0;text-align:center}
p.legend{display:flex;flex-wrap:wrap;gap:.4rem;margin:0 0 1rem}
.tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%}
th{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text3);font-weight:700;text-align:left;
padding:.4rem .6rem;border-bottom:1px solid var(--line2);white-space:nowrap}
td{padding:.45rem .6rem;border-bottom:1px solid var(--line);font-size:.92rem;vertical-align:middle}
tr:last-child td{border-bottom:0}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
td.act{text-align:right}
small{color:var(--text3);font-size:.82rem}
tr.lowq td{background:var(--alarm-bg)}
.bar{display:inline-block;width:11rem;height:.5rem;background:var(--panel);border-radius:99px;vertical-align:middle;
margin-right:.6rem;overflow:hidden}
.bar span{display:block;height:100%;background:var(--accent);border-radius:99px}
em{font-style:normal;color:var(--text3);font-size:.86rem}
details.card{padding:0}
details.card summary{cursor:pointer;font-weight:700;color:var(--head);padding:.85rem 1.15rem;list-style:none}
details.card summary::-webkit-details-marker{display:none}
details.card summary::before{content:"▸";display:inline-block;width:1.1em;color:var(--accent);transition:transform .15s}
details.card[open] summary::before{transform:rotate(90deg)}
details.card>.tablewrap,details.card>p{margin:0 1.15rem 1rem}
p.note{font-size:.84rem;color:var(--text3)}
footer{background:var(--foot-bg);color:var(--foot-fg);font-size:.82rem;margin-top:1.5rem}
footer .wrap{padding-top:1.1rem;padding-bottom:1.3rem;opacity:.85}
@media (max-width:760px){
.row2{grid-template-columns:minmax(0,1fr)}
.stamp{margin-left:0;text-align:left}
.kpi b{font-size:1.5rem}
.roommap{grid-template-columns:repeat(2,minmax(2.9rem,1fr)) .7rem repeat(2,minmax(2.9rem,1fr))}
.seat{font-size:.64rem;padding:.2rem .25rem}
.bar{width:6rem}
td,th{padding:.35rem .45rem;font-size:.84rem}
}
""".replace("{SITE}", SITE_URL)


def pool_status(db):
    """Heute Aktive je Pool-PC mit Status (arbeitet, hängt, aufgegeben, pausiert, fertig);
    gemeinsam für Dashboard und Hilfe-App."""
    answers = load_answers(db)
    total_q = len(answers) or 1
    praktika = [("P1_Einfuehrung", "Praktikum 1"), ("P2_Randbedingungen", "Praktikum 2"),
                ("P3_Abstraktionen_Vernetzung", "Praktikum 3"), ("P4_Instationaer", "Praktikum 4")]
    q_per_p = {key: sum(1 for qid in answers if "/" + key + "/" in qid) or 1 for key, _ in praktika}

    rows = [r for r in db.execute("SELECT pseudonym, qid, best, attempts FROM results")
            if r["qid"] in answers]
    per_user = {}
    for r in rows:
        u = per_user.setdefault(r["pseudonym"], {"solved": 0, "points": 0, "per_p": {}})
        if r["best"] > 0:
            u["solved"] += 1
            u["points"] += r["best"]
            for key, _ in praktika:
                if "/" + key + "/" in r["qid"]:
                    u["per_p"][key] = u["per_p"].get(key, 0) + 1

    # --- Praktikums-Ansicht: heute Aktive einzeln, mit Pool-PC statt Name ---
    # Pro Person zählt die zuletzt bearbeitete Aufgabe als "ist gerade hier".
    now_ts = time.time()
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    today_raw = db.execute(
        "SELECT pseudonym, qid, best, attempts, updated_at FROM results WHERE updated_at > ?",
        (midnight,)).fetchall()
    today_raw = [r for r in today_raw if r["qid"] in answers]
    latest = {}
    for r in today_raw:
        prev = latest.get(r["pseudonym"])
        if prev is None or r["updated_at"] > prev["updated_at"]:
            latest[r["pseudonym"]] = r
    active_now = sum(1 for r in latest.values() if now_ts - r["updated_at"] < 15 * 60)

    # Klarnamen (nur vorhanden, wenn der OPAL-Baustein sie überträgt)
    names = {}
    for u in db.execute("SELECT pseudonym, name_enc FROM users WHERE name_enc IS NOT NULL"):
        try:
            names[u["pseudonym"]] = fernet.decrypt(u["name_enc"].encode()).decode()
        except Exception:
            pass

    entries = []
    for pseu, r in latest.items():
        pk = next((k for k, _ in praktika if "/" + k + "/" in r["qid"]), None)
        psolved = per_user.get(pseu, {"per_p": {}})["per_p"].get(pk, 0)
        ptotal = q_per_p.get(pk, 0)
        allowed = int(answers.get(r["qid"], {}).get("attempts", 5))
        idle = now_ts - r["updated_at"]
        if pk and ptotal and psolved >= ptotal:
            skey, status = "done", '<b class="done">Praktikum fertig</b>'
        elif r["best"] <= 0 and r["attempts"] >= allowed:
            skey, status = "alarm", '<b class="alarm">aufgegeben, Hilfe anbieten</b>'
        elif r["best"] <= 0 and r["attempts"] >= 3:
            skey, status = "warn", '<b class="warn">hängt, %d. Versuch</b>' % r["attempts"]
        elif idle > 15 * 60:
            skey, status = "idle", '<b class="idle">pausiert</b>'
        else:
            skey, status = "ok", '<b class="ok">arbeitet</b>'
        seen = LAST_SEEN.get(pseu) or {}
        pc = host_label(seen.get("ip", "")) or ("&hellip;" + pseu[:6])
        pname = next((nm for k, nm in praktika if k == pk), "")
        entries.append({"pc": pc, "pname": pname, "pk": pk, "solved": psolved,
                        "total": ptotal, "qid": r["qid"], "attempts": r["attempts"],
                        "idle": idle, "status": status, "skey": skey,
                        "name": names.get(pseu, ""),
                        "pshort": pk.split("_")[0] if pk else ""})
    entries.sort(key=lambda e: (-e["solved"], e["idle"]))
    return dict(answers=answers, total_q=total_q, praktika=praktika, q_per_p=q_per_p, rows=rows,
                per_user=per_user, now_ts=now_ts, midnight=midnight, today_raw=today_raw, latest=latest,
                active_now=active_now, names=names, entries=entries)


@app.get("/dashboard")
def dashboard():
    """Lehrenden-Übersicht: wie viele sind wie weit (aggregiert, pseudonym).
    Zugriff nur mit ?key=<DASHBOARD_TOKEN>."""
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter (DASHBOARD_TOKEN).", 403

    db = get_db()
    ps = pool_status(db)
    answers, total_q, praktika, q_per_p, rows = ps["answers"], ps["total_q"], ps["praktika"], ps["q_per_p"], ps["rows"]
    per_user, now_ts, midnight, today_raw = ps["per_user"], ps["now_ts"], ps["midnight"], ps["today_raw"]
    latest, active_now, names, entries = ps["latest"], ps["active_now"], ps["names"], ps["entries"]

    # KPI-Kacheln: die Zahlen, die man im Praktikum ständig braucht.
    # Spannweite bezieht sich aufs dominante Praktikum (typisch läuft eins).
    by_pk = {}
    for e in entries:
        if e["pk"]:
            by_pk.setdefault(e["pk"], []).append(e["solved"])
    kpis = [("%d" % active_now, "gerade aktiv", ""), ("%d" % len(latest), "heute aktiv", "")]
    if by_pk:
        dom = max(by_pk, key=lambda k: len(by_pk[k]))
        vals = sorted(by_pk[dom])
        dom_name = next(nm for k, nm in praktika if k == dom)
        kpis += [("%d/%d" % (vals[-1], q_per_p.get(dom, 0)), "Spitze, " + dom_name, ""),
                 ("%d" % vals[len(vals) // 2], "Median", ""),
                 ("%d" % vals[0], "Schlusslicht", "")]
    need_help = [e for e in entries if e["skey"] in ("warn", "alarm")]
    kpis.append(("%d" % len(need_help), "Hilfe empfohlen", " alarm" if need_help else " good"))
    kpi_html = '<div class="kpis">%s</div>' % "".join(
        '<div class="kpi%s"><b>%s</b><span>%s</span></div>' % (c, v, l) for v, l, c in kpis)

    # Hilfe-Warteschlange (aktiv gemeldete), in Meldereihenfolge
    _help_cleanup(db)
    h_on = help_enabled(db)
    queue_rows = db.execute(
        "SELECT id, who, page, created_at, text FROM help_requests WHERE done_at IS NULL "
        "ORDER BY created_at").fetchall()
    items = ""
    for i, qr in enumerate(queue_rows, start=1):
        label = hilfe_label(qr["who"])
        who_name = "" if qr["who"].startswith("ip:") else names.get(qr["who"], "")
        wait_min = max(0, round((now_ts - qr["created_at"]) / 60))
        items += ('<tr><td class="num"><b>%d.</b></td><td><b>%s</b>%s</td>'
                  '<td>%s<br><small>wartet %d min</small>%s</td>'
                  '<td class="act"><a class="btn done" href="dashboard-help-done?key=%s&amp;id=%d">erledigt</a></td></tr>'
                  % (i, escape(label), ("<br><small>%s</small>" % escape(who_name)) if who_name else "",
                     escape(short_page(qr["page"] or "")), wait_min, help_zeile(db, qr), DASHBOARD_TOKEN, qr["id"]))
    if items:
        queue_body = ('<div class="tablewrap"><table><tr><th></th><th>Platz</th><th>Seite</th><th></th></tr>%s'
                      '</table></div>' % items)
    else:
        queue_body = ('<p class="empty">%s</p>' % ("Keine offenen Meldungen." if h_on else
                      "Der Hilfe-Button ist aus. Einschalten unter „Schalter auf der Kursseite“."))
    queue_html = ('<section class="card queue%s"><h2>Hilfe-Warteschlange%s</h2>%s</section>'
                  % (" busy" if queue_rows else "", " (%d)" % len(queue_rows) if queue_rows else "", queue_body))

    # Schalter auf der Kursseite: Hilfe-Button
    switches = [("Hilfe-Button", h_on, "dashboard-help-toggle?key=%s" % DASHBOARD_TOKEN, "einschalten")]
    switch_html = ('<section class="card switches"><h2>Schalter auf der Kursseite</h2><ul class="sw">%s</ul></section>'
                   % "".join('<li><span>%s</span><b class="pill %s">%s</b><a class="btn%s" href="%s">%s</a></li>'
                             % (name, "on" if on else "off", "AN" if on else "AUS", "" if on else " go", url,
                                "ausschalten" if on else verb)
                             for name, on, url, verb in switches))
    switch_html = switch_html.replace("</section>", '<p><a href="dashboard-sollwerte?key=%s">Sollwerte korrigieren</a>: '
                                      "gilt sofort, gespeicherte Eingaben werden nachgewertet</p></section>"
                                      % DASHBOARD_TOKEN, 1)

    # Direkt handlungsleitend: wo hingehen?
    help_html = ""
    if need_help:
        help_html = ('<div class="alert"><h3>Hilfe empfohlen</h3><ul class="chips">%s</ul></div>'
                     % "".join('<li><b>%s</b>%s <span>%s</span></li>'
                               % (e["pc"], (" " + escape(e["name"])) if e["name"] else "",
                                  "aufgegeben" if e["skey"] == "alarm" else "%d. Versuch" % e["attempts"])
                               for e in need_help[:10]))

    # Arbeiten Leute in unterschiedlichen Praktika (Vorzieher/Nachzügler),
    # bekommt jedes aktive Praktikum seine eigene Spannweiten-Zeile.
    multi_html = ""
    if len(by_pk) > 1:
        parts = []
        for k in sorted(by_pk, key=lambda k: -len(by_pk[k])):
            v = sorted(by_pk[k])
            nm = next(nm for kk, nm in praktika if kk == k)
            if len(v) == 1:
                parts.append("%s: <b>%d/%d</b> (1 Person)" % (nm, v[0], q_per_p.get(k, 0)))
            else:
                parts.append("%s: Spitze <b>%d/%d</b> · Median <b>%d</b> · Schlusslicht <b>%d</b> (%d Personen)"
                             % (nm, v[-1], q_per_p.get(k, 0), v[len(v) // 2], v[0], len(v)))
        multi_html = '<p class="spans">Parallel aktiv: ' + " &nbsp;|&nbsp; ".join(parts) + "</p>"

    # Brennpunkt heute: an welcher Aufgabe arbeiten/hingen heute die meisten?
    # Lohnt sich für eine Ansage an alle statt zehn Einzelerklärungen.
    hot = {}
    for r in today_raw:
        d = hot.setdefault(r["qid"], {"n": 0, "solved": 0, "att": 0})
        d["n"] += 1
        d["att"] += r["attempts"]
        if r["best"] > 0:
            d["solved"] += 1
    hot_rows = "".join(
        '<tr><td title="%s">%s</td><td class="num">%d</td><td class="num">%d</td><td class="num">%.1f</td></tr>'
        % (escape(qid), short_qid(qid), d["n"], d["solved"], d["att"] / d["n"])
        for qid, d in sorted(hot.items(), key=lambda kv: -kv[1]["n"])[:8])
    hot_html = ""
    if hot_rows:
        hot_html = ('<div class="card"><h3>Brennpunkt heute: meistbearbeitete Aufgaben</h3>'
                    '<div class="tablewrap"><table><tr><th>Aufgabe</th><th>Personen heute</th>'
                    '<th>davon gelöst</th><th>ø Versuche</th></tr>%s</table></div></div>' % hot_rows)

    # Häufige Fehlwerte heute: welcher Fehler passiert gerade vielen? (Ansage an alle)
    wrong_head = ('<tr><th>Aufgabe</th><th>typische Eingabe</th><th>Lösung</th>'
                  '<th>Anzahl</th><th>erkannte Ursache</th><th></th></tr>')
    wrong_today = wrong_value_rows(db, answers, midnight)
    wrong_html = ""
    if wrong_today:
        wrong_html = ('<div class="card"><h3>Häufige Fehlwerte heute</h3><div class="tablewrap"><table>%s%s'
                      '</table></div></div>' % (wrong_head, wrong_today))

    # Raumkarte: Plätze örtlich wie im Pool (vorn unten; pro Reihe zwei
    # Zweiergruppen mit Mittelgang; Platz 1 vorne rechts, dann 2/3/4 nach
    # links, nächste Reihe dahinter zählt weiter).
    ROOMS = {"N102": 32, "N103": 20, "N104": 16}
    seat_of = {}
    for e in entries:
        m = re.match(r"^(N\d{3}) Platz (\d+)$", e["pc"])
        if m and m.group(1) in ROOMS:
            seat_of[(m.group(1), int(m.group(2)))] = e
    # Hilfe-Warteschlange wie in der Handy-App: der nächste Platz cyan, die übrigen magenta mit Nummer;
    # der Raum erscheint auch, wenn dort nur jemand wartet
    warte = {}
    for i, qr in enumerate(queue_rows, start=1):
        m = re.match(r"^(N\d{3}) Platz (\d+)$", hilfe_label(qr["who"]))
        if m and m.group(1) in ROOMS:
            warte.setdefault((m.group(1), int(m.group(2))), i)
    map_html = ""
    for room in sorted(ROOMS):
        if not any(k[0] == room for k in list(seat_of) + list(warte)):
            continue
        total_seats = ROOMS[room]
        n_rows = (total_seats + 3) // 4
        cells = ""
        for row in range(n_rows, 0, -1):          # hinterste Reihe zuerst
            base = (row - 1) * 4
            for offset in (4, 3, 0, 2, 1):        # links: 4,3 · Gang · rechts: 2,1
                if offset == 0:
                    cells += '<i class="aisle"></i>'
                    continue
                seat = base + offset
                if seat > total_seats:
                    cells += '<i class="aisle"></i>'
                    continue
                e = seat_of.get((room, seat))
                w = warte.get((room, seat))
                hilfe = (" s-next" if w == 1 else " s-hilfe") if w else ""
                marke = "<sup>%d.</sup>" % w if w else ""
                if e:
                    cells += ('<span class="seat s-%s%s" title="%s%s · zuletzt %s · vor %d min%s">'
                              '<b>%d</b><u>%s</u>%s%d/%d%s</span>'
                              % (e["skey"], hilfe,
                                 escape(e["name"]) + " · " if e["name"] else "", e["pname"],
                                 escape(short_qid(e["qid"])), max(0, round(e["idle"] / 60)),
                                 " · wartet auf Hilfe" if w else "",
                                 seat, escape(e["name"]) or "&nbsp;",
                                 ("%s " % e["pshort"]) if e["pshort"] else "",
                                 e["solved"], e["total"], marke))
                elif w:
                    cells += ('<span class="seat%s" title="wartet auf Hilfe"><b>%d</b><u>wartet</u>%s</span>'
                              % (hilfe, seat, marke))
                else:
                    cells += '<span class="seat"><b>%d</b></span>' % seat
        map_html += ('<div class="card room"><h3>Raum %s</h3><div class="roommap">%s</div>'
                     '<p class="front">▲ vorne, Tafel</p></div>' % (room, cells))
    if map_html:
        map_html = ('<div class="rooms">%s</div><p class="legend"><b class="ok">arbeitet</b>'
                    '<b class="done">Praktikum fertig</b><b class="warn">hängt</b><b class="alarm">aufgegeben</b>'
                    '<b class="idle">pausiert</b>%s</p>'
                    % (map_html, '<b class="next">als Nächstes</b><b class="hilfe">wartet auf Hilfe</b>' if warte else ""))

    person_rows = "".join(
        '<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td class="num">%d/%d</td><td title="%s">%s</td>'
        '<td class="num">%d</td><td class="num">vor %d min</td><td>%s</td></tr>'
        % (e["pc"], escape(e["name"]), e["pname"], e["solved"], e["total"],
           escape(e["qid"]), short_qid(e["qid"]), e["attempts"],
           max(0, round(e["idle"] / 60)), e["status"])
        for e in entries[:60])
    live_html = (
        '<div class="row2">' + queue_html + switch_html + "</div>"
        + '<section class="hero"><p class="kicker">Praktikum heute</p><h2>Wer ist wie weit?</h2>' + kpi_html + "</section>"
        + help_html
        + multi_html
        + map_html
        + hot_html
        + wrong_html
        + ('<div class="card"><h3>Alle heute Aktiven</h3><div class="tablewrap"><table>'
           "<tr><th>Platz</th><th>Name</th><th>Praktikum</th><th>gelöst</th><th>zuletzt an</th>"
           "<th>Versuche</th><th>zuletzt aktiv</th><th>Status</th></tr>%s</table></div></div>"
           % person_rows
           if person_rows else '<div class="card"><p class="empty">Heute war noch niemand aktiv.</p></div>'))

    n = len(per_user)
    buckets = [("noch nichts gelöst", 0, 0), ("bis 25 %", 0.0001, 0.25), ("bis 50 %", 0.25, 0.5),
               ("bis 75 %", 0.5, 0.75), ("bis 99 %", 0.75, 0.9999), ("alles gelöst", 0.9999, 10)]
    dist = []
    for label, lo, hi in buckets:
        c = sum(1 for u in per_user.values() if lo <= u["solved"] / total_q <= hi)
        dist.append((label, c))

    def bar(count):
        pct = int(100 * count / n) if n else 0
        return ('<span class="bar"><span style="width:%d%%"></span></span><em>%d (%d %%)</em>'
                % (max(pct, 1) if count else 0, count, pct))

    p_rows = ""
    for key, name in praktika:
        started = sum(1 for u in per_user.values() if u["per_p"].get(key, 0) > 0)
        done = sum(1 for u in per_user.values() if u["per_p"].get(key, 0) >= q_per_p[key])
        p_rows += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (name, bar(started), bar(done))

    # Pro Aufgabe: Lösequote und Volltreffer-Quote (= im 1. Versuch gelöst,
    # erkennbar am Bonuspunkt) zeigen, welche Aufgaben zu schwer/leicht sind.
    qagg = {}
    for r in rows:
        d = qagg.setdefault(r["qid"], {"n": 0, "solved": 0, "att": 0, "first": 0})
        d["n"] += 1
        d["att"] += r["attempts"]
        if r["best"] > 0:
            d["solved"] += 1
            if r["best"] > answers.get(r["qid"], {}).get("points", 1):
                d["first"] += 1
    q_rows = ""
    for qid in sorted(qagg):
        d = qagg[qid]
        quote = 100 * d["solved"] / d["n"] if d["n"] else 0
        cls = ' class="lowq"' if d["n"] >= 5 and quote < 40 else ""
        q_rows += ('<tr%s><td title="%s">%s</td><td class="num">%d/%d</td><td class="num">%d %%</td>'
                   '<td class="num">%.1f</td><td class="num">%s</td></tr>'
                   % (cls, escape(qid), short_qid(qid), d["solved"], d["n"],
                      quote, d["att"] / d["n"] if d["n"] else 0,
                      "%d %%" % (100 * d["first"] / d["solved"]) if d["solved"] else ""))

    dist_rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (label, bar(c)) for label, c in dist)
    html = """<!doctype html><html lang="de"><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thermo-Kurs Dashboard</title>
<style>""" + DASH_CSS + """</style>
<header class="top"><div class="wrap topin">
<img src="%s" alt="HTWK Leipzig" class="logo">
<div class="ttl"><b>Angewandte FEM in der Thermodynamik</b><span class="tag">Dashboard</span></div>
<div class="stamp"><b>%d</b> Teilnehmende mit Login · <b>%d</b> Aufgaben im Katalog<br>Stand %s · aktualisiert sich alle 30 s</div>
</div></header>
<main class="wrap">
%s
<h2>Kurs gesamt</h2>
<details class="card" open><summary>Wie weit ist der Kurs? Anteil gelöster Aufgaben pro Person</summary>
<div class="tablewrap"><table>%s</table></div></details>
<details class="card"><summary>Pro Praktikum: begonnen und komplett</summary>
<div class="tablewrap"><table><tr><th></th><th>mind. 1 Aufgabe gelöst</th><th>komplett gelöst</th></tr>%s</table></div></details>
<details class="card"><summary>Pro Aufgabe: Lösequote, ø Versuche, Volltreffer im 1. Versuch</summary>
<div class="tablewrap"><table><tr><th>Aufgabe</th><th>gelöst</th><th>Lösequote</th><th>ø Versuche</th><th>Volltreffer</th></tr>%s</table></div>
<p class="note">Rot hinterlegt: Lösequote unter 40 %% (ab 5 Personen), Kandidaten zum Nachschärfen.</p></details>
<details class="card"><summary>Häufige Fehlwerte, gesamt und anonym</summary>
<div class="tablewrap"><table>%s%s</table></div>
<p class="note">Ohne erkannte Ursache: Häufen sich gleiche Werte, ist vielleicht der Sollwert falsch („als Sollwert?“).</p></details>
</main>
<footer><div class="wrap">PC-Namen stehen nur im Arbeitsspeicher, Namen nur hinter dem Schlüssel. Nicht am Beamer zeigen.</div></footer>
</html>""" % (DASH_LOGO, n, len(answers), datetime.datetime.now().strftime("%d.%m.%Y, %H:%M"),
              live_html, dist_rows, p_rows, q_rows, wrong_head,
              wrong_value_rows(db, answers, 0)
              or '<tr><td colspan="6"><p class="empty">Noch keine falschen Eingaben.</p></td></tr>')
    return html


# --- Sollwert-Korrektur im Dashboard ------------------------------------------
# Eine Korrektur gilt sofort und liegt in der Tabelle korrekturen über answers.json, bis der Kurstext
# nachgezogen ist; dann verschwindet sie beim nächsten Öffnen der Seite. Nach jeder Änderung werden die
# gespeicherten Eingaben nachgewertet: Der erste Versuch, der zum neuen Sollwert passt, zählt, als wäre er
# damals richtig gewesen (volle Punkte, Bonus im 1. Versuch). Punkte steigen dabei nur, sie sinken nie.

def _float(v):
    try:
        x = float(str(v).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _zahl(x, komma=True):
    s = format(x, ".10g")
    return s.replace(".", ",") if komma else s


def _anzahl(n, eins, mehr):
    return "%d %s" % (n, eins if n == 1 else mehr)


def _praktikum(qid):
    teil = qid.replace("/Thermische-Analyse/", "").strip("/").split("/")[0]
    m = re.match(r"P(\d+)_", teil)
    return "Praktikum " + m.group(1) if m else teil.replace("_", " ")


def nachwertung(db, qid, q):
    """Was eine Nachwertung mit Sollwert q["answer"] ± q["tolerance"] ändert, ohne zu schreiben:
    gespeicherte Eingaben, Personen, Treffer, {pseudonym: neue Punkte} und passende Fehlwert-Einträge."""
    tol = q.get("tolerance", 0)
    erster, eingaben, personen = {}, 0, set()
    for r in db.execute("SELECT pseudonym, versuch, value FROM eingaben WHERE qid=? ORDER BY versuch", (qid,)):
        eingaben += 1
        personen.add(r["pseudonym"])
        if r["pseudonym"] not in erster and abs(r["value"] - q["answer"]) <= tol:
            erster[r["pseudonym"]] = r["versuch"]
    best = dict(db.execute("SELECT pseudonym, best FROM results WHERE qid=?", (qid,)).fetchall())
    punkte = {p: earned_points(q["points"], v, q.get("attempts", 5)) for p, v in erster.items()}
    fehlwerte = db.execute("SELECT COUNT(*) FROM wrong_values WHERE qid=? AND ABS(value - ?) <= ?",
                           (qid, q["answer"], tol)).fetchone()[0]
    return {"eingaben": eingaben, "personen": len(personen), "treffer": len(erster), "fehlwerte": fehlwerte,
            "gewinner": {p: n for p, n in punkte.items() if p in best and n > best[p]}}


def nachwerten(db, qid, q):
    """Nachwertung schreiben: höhere Punkte eintragen und Fehlwert-Einträge entfernen, die zum Sollwert passen.
    updated_at bleibt, sonst stünden alle Nachgewerteten im Dashboard als „heute aktiv“. Der Aufrufer committet."""
    v = nachwertung(db, qid, q)
    for p, n in v["gewinner"].items():
        db.execute("UPDATE results SET best=? WHERE pseudonym=? AND qid=? AND best<?", (n, p, qid, n))
    db.execute("DELETE FROM wrong_values WHERE qid=? AND ABS(value - ?) <= ?",
               (qid, q["answer"], q.get("tolerance", 0)))
    return v


def _nachwerten_und_zurueck(db, qid, q, ok):
    v = nachwerten(db, qid, q)
    db.commit()
    for p in v["gewinner"]:
        push_score_async(p)
    return redirect("dashboard-sollwerte?" + urllib.parse.urlencode(
        {"key": DASHBOARD_TOKEN, "ok": ok, "qid": qid, "n": len(v["gewinner"]), "f": v["fehlwerte"]}))


@app.post("/dashboard-sollwert")
def sollwert_setzen():
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter.", 403
    qid = request.form.get("qid", "")
    q = load_answers().get(qid)
    answer, tolerance = _float(request.form.get("answer")), _float(request.form.get("tolerance"))
    if not q or "answer" not in q or answer is None or tolerance is None or tolerance < 0:
        return "Ungültige Korrektur.", 400
    db = get_db()
    if answer == q["answer"] and tolerance == q.get("tolerance", 0):
        db.execute("DELETE FROM korrekturen WHERE qid=?", (qid,))  # wieder der Wert aus dem Kurstext
    else:
        db.execute("INSERT OR REPLACE INTO korrekturen (qid, answer, tolerance, created_at) VALUES (?, ?, ?, ?)",
                   (qid, answer, tolerance, time.time()))
    return _nachwerten_und_zurueck(db, qid, dict(q, answer=answer, tolerance=tolerance), "gespeichert")


@app.post("/dashboard-sollwert-zurueck")
def sollwert_zuruecknehmen():
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter.", 403
    qid = request.form.get("qid", "")
    db = get_db()
    db.execute("DELETE FROM korrekturen WHERE qid=?", (qid,))
    q = load_answers().get(qid)
    if not q or "answer" not in q:
        db.commit()
        return redirect("dashboard-sollwerte?key=" + DASHBOARD_TOKEN)
    return _nachwerten_und_zurueck(db, qid, q, "zurueckgenommen")


@app.get("/dashboard-sollwerte")
def sollwerte():
    """Sollwerte der Zahlenfragen ansehen und korrigieren, mit Vorschau der Nachwertung. Eigene Seite ohne das
    automatische Neuladen des Dashboards, sonst gingen Eingaben beim Tippen verloren."""
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter.", 403
    db, key = get_db(), escape(DASHBOARD_TOKEN)
    datei = load_answers()
    for r in db.execute("SELECT qid, answer, tolerance FROM korrekturen").fetchall():
        q = datei.get(r["qid"], {})
        if q.get("answer") == r["answer"] and q.get("tolerance", 0) == r["tolerance"]:
            db.execute("DELETE FROM korrekturen WHERE qid=?", (r["qid"],))  # im Kurstext nachgezogen
    db.commit()
    korr = {r["qid"]: r for r in db.execute("SELECT qid, answer, tolerance, created_at FROM korrekturen")}
    answers = load_answers(db)
    zahl_eingaben = dict(db.execute("SELECT qid, COUNT(*) FROM eingaben GROUP BY qid").fetchall())
    seit = db.execute("SELECT value FROM meta WHERE key='eingaben_seit'").fetchone()

    def aufgabe(qid):
        titel = answers.get(qid, {}).get("titel", "")
        return '%s%s' % (short_qid(qid), ("<br><small>%s</small>" % escape(titel)) if titel else "")

    teile = ['<section class="hero"><p class="kicker">Zahlenfragen</p><h2>Sollwerte prüfen und korrigieren</h2>'
             '<p>Eine Korrektur gilt sofort, ohne Deploy. Danach werden die gespeicherten Eingaben nachgewertet: '
             'Wer den neuen Sollwert in einem seiner Versuche eingegeben hat, bekommt die Punkte, als wäre die '
             'Eingabe damals richtig gewesen. Punkte werden nur erhöht, nie abgezogen.%s</p></section>'
             % (" Eingaben werden seit %s gespeichert, ältere Versuche lassen sich nicht nachwerten." % escape(seit[0])
                if seit else "")]

    ok = request.args.get("ok")
    if ok in ("gespeichert", "zurueckgenommen"):
        n, f = _float(request.args.get("n")) or 0, _float(request.args.get("f")) or 0
        teile.append('<div class="card ok"><h3>Korrektur %s</h3><p>%s: %s nachträglich gewertet, %s aus dem '
                     'Fehlwert-Log entfernt.</p></div>'
                     % ("gespeichert" if ok == "gespeichert" else "zurückgenommen",
                        short_qid(request.args.get("qid", "")), _anzahl(int(n), "Person", "Personen"),
                        _anzahl(int(f), "Eintrag", "Einträge")))

    vq = request.args.get("qid") if not ok else None
    if vq and "answer" in answers.get(vq, {}) and request.args.get("answer") is not None:
        alt = answers[vq]
        neu_a = _float(request.args.get("answer"))
        neu_t = _float(request.args.get("tolerance", alt.get("tolerance", 0)))
        if neu_a is None or neu_t is None or neu_t < 0:
            teile.append('<div class="alert"><h3>Keine gültige Zahl</h3><p>Sollwert und Toleranz als Zahl '
                         'eingeben, die Toleranz nicht negativ.</p></div>')
        else:
            v = nachwertung(db, vq, dict(alt, answer=neu_a, tolerance=neu_t))
            d = datei.get(vq, {})
            wie_kurstext = neu_a == d.get("answer") and neu_t == d.get("tolerance", 0)
            teile.append(
                '<div class="card vorschau"><p class="kicker">Vorschau</p><h3>%s</h3>'
                '<p>Sollwert %s ± %s &rarr; <b>%s ± %s</b>%s</p><ul>'
                '<li>Gespeicherte Eingaben: %d von %s</li>'
                '<li>Passend zum neuen Sollwert: Eingaben von %s</li>'
                '<li>Bekommen nachträglich Punkte: <b>%s</b></li>'
                '<li>Fehlwert-Log: %s passend zum neuen Sollwert, %s entfernt</li></ul>%s'
                '<form method="post" action="dashboard-sollwert?key=%s" class="sw">'
                '<input type="hidden" name="qid" value="%s"><input type="hidden" name="answer" value="%s">'
                '<input type="hidden" name="tolerance" value="%s"><button class="btn go">Übernehmen</button>'
                '<a class="btn" href="dashboard-sollwerte?key=%s">Abbrechen</a></form></div>'
                % (aufgabe(vq), _zahl(alt["answer"]), _zahl(alt.get("tolerance", 0)), _zahl(neu_a), _zahl(neu_t),
                   " (Wert im Kurstext, die Korrektur wird aufgehoben)" if wie_kurstext else "",
                   v["eingaben"], _anzahl(v["personen"], "Person", "Personen"),
                   _anzahl(v["treffer"], "Person", "Personen"), _anzahl(len(v["gewinner"]), "Person", "Personen"),
                   _anzahl(v["fehlwerte"], "Eintrag", "Einträge"), "wird" if v["fehlwerte"] == 1 else "werden",
                   '<p class="hinweis">Die Toleranz ist größer als 10 % des Sollwerts.</p>'
                   if neu_t > 0.1 * abs(neu_a) else "",
                   key, escape(vq), _zahl(neu_a, False), _zahl(neu_t, False), key))

    if korr:
        zeilen = "".join(
            '<tr><td title="%s">%s</td><td class="num">%s ± %s</td><td class="num"><b>%s ± %s</b></td><td>%s</td>'
            '<td><code class="kopie">%s%s: data-answer="%s" data-tolerance="%s"</code></td>'
            '<td class="act"><form method="post" action="dashboard-sollwert-zurueck?key=%s">'
            '<input type="hidden" name="qid" value="%s"><button class="btn">zurücknehmen</button></form></td></tr>'
            % (escape(qid), aufgabe(qid), _zahl(datei.get(qid, {}).get("answer", 0)),
               _zahl(datei.get(qid, {}).get("tolerance", 0)), _zahl(r["answer"]), _zahl(r["tolerance"]),
               datetime.datetime.fromtimestamp(r["created_at"]).strftime("%d.%m.%Y"), short_qid(qid),
               " (docs/%s)" % escape(datei[qid]["quelle"]) if datei.get(qid, {}).get("quelle") else "",
               _zahl(r["answer"], False), _zahl(r["tolerance"], False), key, escape(qid))
            for qid, r in korr.items())
        teile.append('<section class="card"><h2>Aktive Korrekturen</h2><p class="note">Im Kurstext (Markdown) '
                     'nachziehen, dann verschwindet die Korrektur hier von selbst. Ein Klick markiert die Zeile zum Kopieren. '
                     'Zurücknehmen stellt den Wert '
                     'aus dem Kurstext wieder her, vergebene Punkte bleiben.</p><div class="tablewrap"><table>'
                     '<tr><th>Aufgabe</th><th>Kurstext</th><th>Korrektur</th><th>seit</th><th>im Markdown</th>'
                     '<th></th></tr>%s</table></div></section>' % zeilen)

    gruppen = {}
    for qid, q in answers.items():
        if "answer" in q:
            gruppen.setdefault(_praktikum(qid), []).append(qid)
    for name, qids in gruppen.items():
        zeilen = "".join(
            '<tr><td title="%s">%s</td><td class="num">%s ± %s%s</td><td class="num">%d</td>'
            '<td class="act"><form method="get" action="dashboard-sollwerte" class="sw">'
            '<input type="hidden" name="key" value="%s"><input type="hidden" name="qid" value="%s">'
            '<input class="num" name="answer" value="%s" aria-label="Sollwert"> ± '
            '<input class="num tol" name="tolerance" value="%s" aria-label="Toleranz">'
            '<button class="btn">Vorschau</button></form></td></tr>'
            % (escape(qid), aufgabe(qid), _zahl(answers[qid]["answer"]), _zahl(answers[qid].get("tolerance", 0)),
               ' <b class="pill on">korrigiert</b>' if qid in korr else "", zahl_eingaben.get(qid, 0),
               key, escape(qid), _zahl(answers[qid]["answer"]), _zahl(answers[qid].get("tolerance", 0)))
            for qid in qids)
        teile.append('<details class="card"%s><summary>%s: %s</summary><div class="tablewrap"><table>'
                     '<tr><th>Aufgabe</th><th>Sollwert</th><th>Eingaben</th><th>ändern</th></tr>%s</table></div>'
                     '</details>' % (" open" if vq in qids else "", name,
                                     _anzahl(len(qids), "Zahlenfrage", "Zahlenfragen"), zeilen))

    kopf = ('<!doctype html><html lang="de"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Thermo-Kurs Sollwerte</title><style>' + DASH_CSS + '</style>')
    return kopf + """
<header class="top"><div class="wrap topin">
<img src="%s" alt="HTWK Leipzig" class="logo">
<div class="ttl"><b>Angewandte FEM in der Thermodynamik</b><span class="tag">Sollwerte</span></div>
<div class="stamp"><a href="dashboard?key=%s">zurück zum Dashboard</a></div>
</div></header>
<main class="wrap">%s</main>
<footer><div class="wrap">Korrekturen gelten sofort. Punkte werden nachträglich nur erhöht, nie abgezogen.</div></footer>
</html>""" % (DASH_LOGO, key, "\n".join(teile))


@app.get("/api/questions")
def questions():
    """Public question catalog: qid -> max points/attempts (keine Antworten!).
    Grundlage für die Fortschrittsanzeige (wie viele Fragen gibt es je Praktikum)."""
    out = {}
    for qid, q in load_answers().items():
        out[qid] = {"points": q.get("points", 1), "attempts": q.get("attempts", 5)}
    return jsonify(out)


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
