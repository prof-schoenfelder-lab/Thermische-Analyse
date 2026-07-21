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
from flask import Flask, g, jsonify, redirect, request
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
        """
    )
    db.commit()
    # Kurs-Generation: ändert sich beim Semester-Reset; Browser mit alter
    # Generation leeren ihren localStorage automatisch statt Altdaten hochzuladen
    if not db.execute("SELECT value FROM meta WHERE key='generation'").fetchone():
        db.execute("INSERT INTO meta (key, value) VALUES ('generation', ?)",
                   (secrets.token_urlsafe(8),))
        db.commit()
    # Migration für Bestandsdatenbanken
    for stmt in ("ALTER TABLE users ADD COLUMN sub_enc TEXT",
                 "ALTER TABLE users ADD COLUMN name_enc TEXT"):
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


def push_score_async(pseudonym):
    """Gesamtpunktzahl des Users als Score an OPAL melden (fire-and-forget)."""
    if not (AGS_ENABLED and LTI13_CLIENT_ID):
        return

    def work():
        try:
            db = sqlite3.connect(DB_PATH)
            db.row_factory = sqlite3.Row
            user = db.execute("SELECT outcome_url, sub_enc FROM users WHERE pseudonym=?",
                              (pseudonym,)).fetchone()
            if not user or not user["outcome_url"] or not user["sub_enc"]:
                return
            total = db.execute("SELECT COALESCE(SUM(best),0) t FROM results WHERE pseudonym=?",
                               (pseudonym,)).fetchone()["t"]
            db.close()
            answers = load_answers()
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


def load_answers():
    """answers.json (vom MkDocs-Hook erzeugt), mit Reload bei Dateiänderung."""
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
            return _answers_cache["data"]
    return _answers_cache["data"]


def earned_points(points, attempt_number, attempts_allowed):
    """Mastery-Prinzip: Lösen zählt voll, egal beim wievielten Versuch.
    +1 Bonuspunkt für den Volltreffer im ersten Versuch."""
    return round(points) + (1 if attempt_number <= 1 else 0)


@app.post("/api/check")
def check_answer():
    payload = request.get_json(silent=True) or {}
    qid = str(payload.get("qid") or "")
    q = load_answers().get(qid)
    if not q:
        return jsonify({"error": "unbekannte Frage"}), 404

    attempts_allowed = int(q.get("attempts", 5))
    if "answer" in q:
        try:
            val = float(str(payload.get("value")).replace(",", "."))
        except (TypeError, ValueError):
            return jsonify({"error": "keine Zahl"}), 400
        correct = abs(val - q["answer"]) <= q.get("tolerance", 0)
        solution = q["answer"]
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
        return jsonify(resp)

    # Gast: keine Speicherung, Versuche zählt der Client (Selbstbetrug erlaubt)
    attempts = min(int(payload.get("attemptsUsed", 0) or 0) + 1, attempts_allowed)
    resp = {"authed": False, "correct": correct,
            "attempts": attempts, "attemptsAllowed": attempts_allowed}
    if correct or attempts >= attempts_allowed:
        resp["solution"] = solution
    return jsonify(resp)


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


def course_generation():
    row = get_db().execute("SELECT value FROM meta WHERE key='generation'").fetchone()
    return row["value"] if row else "0"


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
        "generation": course_generation(),
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
    elif not db.execute("SELECT id FROM help_requests WHERE who=? AND done_at IS NULL",
                        (who,)).fetchone():
        db.execute("INSERT INTO help_requests (who, page, created_at) VALUES (?, ?, ?)",
                   (who, str(payload.get("page") or "")[:200], time.time()))
        db.commit()
    return help_status()


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


@app.get("/dashboard")
def dashboard():
    """Lehrenden-Übersicht: wie viele sind wie weit (aggregiert, pseudonym).
    Zugriff nur mit ?key=<DASHBOARD_TOKEN>."""
    if not DASHBOARD_TOKEN or request.args.get("key") != DASHBOARD_TOKEN:
        return "Zugriff nur mit gültigem key-Parameter (DASHBOARD_TOKEN).", 403

    db = get_db()
    answers = load_answers()
    total_q = len(answers) or 1
    praktika = [("P1_Einfuehrung", "Praktikum 1"), ("P2_Modellierung_Vernetzung", "Praktikum 2"),
                ("P3_Randbedingungen_Postprocessing", "Praktikum 3"), ("P4_Transient", "Praktikum 4")]
    q_per_p = {key: sum(1 for qid in answers if "/" + key + "/" in qid) or 1 for key, _ in praktika}

    rows = db.execute("SELECT pseudonym, qid, best, attempts FROM results").fetchall()
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
            skey, status = "done", '<b class="ok">✓ Praktikum fertig</b>'
        elif r["best"] <= 0 and r["attempts"] >= allowed:
            skey, status = "alarm", '<b class="alarm">Aufgabe aufgegeben — Hilfe anbieten?</b>'
        elif r["best"] <= 0 and r["attempts"] >= 3:
            skey, status = "warn", '<b class="warn">hängt (%d. Versuch)</b>' % r["attempts"]
        elif idle > 15 * 60:
            skey, status = "idle", '<b class="idle">pausiert</b>'
        else:
            skey, status = "ok", '<b class="ok">arbeitet</b>'
        seen = LAST_SEEN.get(pseu) or {}
        pc = host_label(seen.get("ip", "")) or ("&hellip;" + pseu[:6])
        pname = next((nm for k, nm in praktika if k == pk), "—")
        entries.append({"pc": pc, "pname": pname, "pk": pk, "solved": psolved,
                        "total": ptotal, "qid": r["qid"], "attempts": r["attempts"],
                        "idle": idle, "status": status, "skey": skey,
                        "name": names.get(pseu, ""),
                        "pshort": pk.split("_")[0] if pk else ""})
    entries.sort(key=lambda e: (-e["solved"], e["idle"]))

    # KPI-Kacheln: die Zahlen, die man im Praktikum ständig braucht.
    # Spannweite bezieht sich aufs dominante Praktikum (typisch läuft eins).
    by_pk = {}
    for e in entries:
        if e["pk"]:
            by_pk.setdefault(e["pk"], []).append(e["solved"])
    kpis = [("%d" % active_now, "gerade aktiv"), ("%d" % len(latest), "heute aktiv")]
    dom_name = ""
    if by_pk:
        dom = max(by_pk, key=lambda k: len(by_pk[k]))
        vals = sorted(by_pk[dom])
        dom_name = next(nm for k, nm in praktika if k == dom)
        kpis += [("%d/%d" % (vals[-1], q_per_p.get(dom, 0)), "Spitze (%s)" % dom_name),
                 ("%d" % vals[len(vals) // 2], "Median"),
                 ("%d" % vals[0], "Schlusslicht")]
    need_help = [e for e in entries if e["skey"] in ("warn", "alarm")]
    kpis.append(('<span class="%s">%d</span>' % ("alarmnum" if need_help else "oknum",
                                                 len(need_help)), "Hilfe empfohlen"))
    kpi_html = '<div class="kpis">%s</div>' % "".join(
        '<div class="kpi"><b>%s</b><span>%s</span></div>' % (v, l) for v, l in kpis)

    # Hilfe-Warteschlange (aktiv gemeldete) — in Meldereihenfolge
    _help_cleanup(db)
    h_on = help_enabled(db)
    toggle_html = (
        '<p class="helptoggle">🙋 Hilfe-Button auf der Kursseite: '
        '<strong>%s</strong> · <a class="donebtn%s" href="dashboard-help-toggle?key=%s">%s</a></p>'
        % ("AN" if h_on else "AUS", "" if h_on else " onbtn", DASHBOARD_TOKEN,
           "ausschalten" if h_on else "für die Lehrveranstaltung einschalten"))
    queue_rows = db.execute(
        "SELECT id, who, page, created_at FROM help_requests WHERE done_at IS NULL "
        "ORDER BY created_at").fetchall()
    queue_html = toggle_html
    if queue_rows:
        items = ""
        for i, qr in enumerate(queue_rows, start=1):
            if qr["who"].startswith("ip:"):
                label = host_label(qr["who"][3:]) or qr["who"][3:]
                who_name = ""
            else:
                seen = LAST_SEEN.get(qr["who"]) or {}
                label = host_label(seen.get("ip", "")) or ("…" + qr["who"][:6])
                who_name = names.get(qr["who"], "")
            wait_min = max(0, round((now_ts - qr["created_at"]) / 60))
            page = (qr["page"] or "").replace("/Thermische-Analyse/", "").strip("/")
            items += ("<tr><td><b>%d.</b></td><td>%s</td><td>%s</td><td>%s</td>"
                      "<td>wartet %d min</td>"
                      "<td><a class=\"donebtn\" href=\"dashboard-help-done?key=%s&amp;id=%d\">✓ erledigt</a></td></tr>"
                      % (i, label, who_name or "—", page or "—", wait_min,
                         DASHBOARD_TOKEN, qr["id"]))
        queue_html = ('<div class="queue"><h2>🙋 Hilfe-Warteschlange (%d)</h2>'
                      '<div class="tablewrap"><table><tr><th></th><th>PC</th><th>Name</th>'
                      '<th>Seite</th><th></th><th></th></tr>%s</table></div>%s</div>'
                      % (len(queue_rows), items, toggle_html))

    # Direkt handlungsleitend: wo hingehen?
    help_html = ""
    if need_help:
        help_html = ('<p class="helpline">🚨 Hilfe empfohlen: %s</p>'
                     % " · ".join("<strong>%s</strong>%s (%s)"
                                  % (e["pc"],
                                     " — " + e["name"] if e["name"] else "",
                                     "aufgegeben" if e["skey"] == "alarm"
                                     else "%d. Versuch" % e["attempts"])
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
                parts.append("%s: <strong>%d/%d</strong> (1 Person)"
                             % (nm, v[0], q_per_p.get(k, 0)))
            else:
                parts.append("%s: Spitze <strong>%d/%d</strong> · Median <strong>%d</strong>"
                             " · Schlusslicht <strong>%d</strong> (%d Personen)"
                             % (nm, v[-1], q_per_p.get(k, 0), v[len(v) // 2], v[0], len(v)))
        multi_html = ('<p class="spans">Parallel aktiv: ' + " &nbsp;·&nbsp; ".join(parts)
                      + "</p>")

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
        "<tr><td>%s</td><td>%d</td><td>%d</td><td>%.1f</td></tr>"
        % (qid.replace("/Thermische-Analyse/", ""), d["n"], d["solved"], d["att"] / d["n"])
        for qid, d in sorted(hot.items(), key=lambda kv: -kv[1]["n"])[:8])
    hot_html = ""
    if hot_rows:
        hot_html = ('<h3>Brennpunkt heute — meistbearbeitete Aufgaben</h3>'
                    '<div class="tablewrap"><table><tr><th>Aufgabe</th><th>Personen heute</th>'
                    '<th>davon gelöst</th><th>ø Versuche</th></tr>%s</table></div>' % hot_rows)

    # Raumkarte: Plätze örtlich wie im Pool (vorn unten; pro Reihe zwei
    # Zweiergruppen mit Mittelgang; Platz 1 vorne rechts, dann 2/3/4 nach
    # links, nächste Reihe dahinter zählt weiter).
    ROOMS = {"N102": 32, "N103": 20, "N104": 16}
    seat_of = {}
    for e in entries:
        m = re.match(r"^(N\d{3}) Platz (\d+)$", e["pc"])
        if m and m.group(1) in ROOMS:
            seat_of[(m.group(1), int(m.group(2)))] = e
    map_html = ""
    for room in sorted(ROOMS):
        if not any(k[0] == room for k in seat_of):
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
                if e:
                    first = e["name"] or ""
                    cells += ('<span class="seat s-%s" title="%s%s · zuletzt: %s · vor %d min">'
                              '<b>%d</b>%s%s%d/%d</span>'
                              % (e["skey"],
                                 e["name"] + " · " if e["name"] else "", e["pname"],
                                 e["qid"].replace("/Thermische-Analyse/", ""),
                                 max(0, round(e["idle"] / 60)),
                                 seat,
                                 '<u>%s</u>' % first if first else "",
                                 ("%s " % e["pshort"]) if e["pshort"] else "",
                                 e["solved"], e["total"]))
                else:
                    cells += '<span class="seat"><b>%d</b></span>' % seat
        map_html += ('<h3>Raum %s</h3><div class="roommap">%s</div>'
                     '<p class="front">▲ vorne (Tafel)</p>' % (room, cells))
    if map_html:
        map_html += ('<p><em>Legende: <b class="ok">gr&uuml;n</b> arbeitet/fertig · '
                     '<b class="warn">orange</b> h&auml;ngt · <b class="alarm">rot</b> '
                     'aufgegeben · grau/gestrichelt pausiert bzw. leer</em></p>')

    person_rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d/%d</td><td>%s</td><td>%d</td>"
        "<td>vor %d min</td><td>%s</td></tr>"
        % (e["pc"], e["name"] or "—", e["pname"], e["solved"], e["total"],
           e["qid"].replace("/Thermische-Analyse/", ""), e["attempts"],
           max(0, round(e["idle"] / 60)), e["status"])
        for e in entries[:60])
    live_html = (
        queue_html
        + "<h2>Praktikums-Ansicht — wer ist heute wie weit?</h2>"
        + kpi_html
        + help_html
        + multi_html
        + map_html
        + hot_html
        + ("<h3>Alle heute Aktiven</h3><div class=\"tablewrap\"><table>"
           "<tr><th>PC</th><th>Name</th><th>Praktikum</th><th>gelöst</th><th>zuletzt an</th>"
           "<th>Versuche</th><th>zuletzt aktiv</th><th>Status</th></tr>%s</table></div>"
           % person_rows
           if person_rows else "<p><em>Heute war noch niemand aktiv.</em></p>"))

    n = len(per_user)
    buckets = [("noch nichts gelöst", 0, 0), ("bis 25 %", 0.0001, 0.25), ("bis 50 %", 0.25, 0.5),
               ("bis 75 %", 0.5, 0.75), ("bis 99 %", 0.75, 0.9999), ("alles gelöst", 0.9999, 10)]
    dist = []
    for label, lo, hi in buckets:
        c = sum(1 for u in per_user.values() if lo <= u["solved"] / total_q <= hi)
        dist.append((label, c))

    def bar(count):
        pct = int(100 * count / n) if n else 0
        return ('<div class="bar"><span style="width:%d%%"></span></div><em>%d (%d %%)</em>'
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
        q_rows += ("<tr%s><td>%s</td><td>%d/%d</td><td>%d %%</td><td>%.1f</td><td>%s</td></tr>"
                   % (cls, qid.replace("/Thermische-Analyse/", ""), d["solved"], d["n"],
                      quote, d["att"] / d["n"] if d["n"] else 0,
                      "%d %%" % (100 * d["first"] / d["solved"]) if d["solved"] else "—"))

    dist_rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (label, bar(c)) for label, c in dist)
    html = """<!doctype html><html lang="de"><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thermo-Kurs Dashboard</title>
<style>body{font-family:system-ui,sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;color:#222;background:#fff}
h1{font-size:1.4rem} h2{font-size:1.05rem;margin-top:2rem} table{border-collapse:collapse;width:100%%;min-width:32rem}
td,th{padding:.35rem .6rem;border-bottom:1px solid #ddd;text-align:left;font-size:.9rem;vertical-align:middle}
.tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.bar{display:inline-block;width:12rem;height:.7rem;background:#eee;border-radius:.35rem;vertical-align:middle;margin-right:.5rem}
.bar span{display:block;height:100%%;background:#3f51b5;border-radius:.35rem}
em{font-style:normal;color:#555;font-size:.85rem}
b.ok{color:#2e7d32} b.warn{color:#e65100} b.alarm{color:#c62828} b.idle{color:#888}
b{font-weight:600}
.kpis{display:flex;flex-wrap:wrap;gap:.5rem;margin:.7rem 0}
.kpi{background:#f4f5fa;border-radius:.55rem;padding:.5rem .85rem;min-width:5rem;flex:0 1 auto}
.kpi b{display:block;font-size:1.3rem;line-height:1.2}
.kpi span{font-size:.72rem;color:#666}
.kpi .alarmnum{color:#c62828} .kpi .oknum{color:#2e7d32}
p.helpline{background:#fff3f3;border:1px solid #ffcdd2;border-radius:.5rem;padding:.5rem .7rem;font-size:.9rem}
p.spans{font-size:.85rem;color:#444}
.queue{background:#fffde7;border:1px solid #ffe082;border-radius:.6rem;padding:.2rem .8rem .6rem;margin:1rem 0}
.queue h2{margin-top:.6rem}
.queue table{min-width:24rem}
a.donebtn{display:inline-block;background:#2e7d32;color:#fff;border-radius:.4rem;
  padding:.2rem .6rem;text-decoration:none;font-size:.8rem}
a.donebtn.onbtn{background:#e65100}
p.helptoggle{font-size:.85rem}
.roommap{display:grid;grid-template-columns:repeat(2,5.6rem) 1.4rem repeat(2,5.6rem);gap:.3rem;margin:.4rem 0}
.seat{border:1px solid #ccc;border-radius:.3rem;padding:.2rem .3rem;font-size:.72rem;
  min-height:2.1rem;background:#fafafa;color:#999}
.seat b{display:block;font-size:.8rem;color:inherit}
.seat u{display:block;text-decoration:none;font-weight:600;font-size:.66rem;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.seat.s-ok{background:#c8e6c9;border-color:#66bb6a;color:#1b5e20}
.seat.s-done{background:#2e7d32;border-color:#2e7d32;color:#fff}
.seat.s-warn{background:#ffe0b2;border-color:#ffa726;color:#e65100}
.seat.s-alarm{background:#ffcdd2;border-color:#e53935;color:#b71c1c}
.seat.s-idle{background:#eee;border-style:dashed;color:#888}
p.front{font-size:.75rem;color:#888;margin:.1rem 0 1rem}
h3{font-size:.95rem;margin:1.2rem 0 .2rem}
tr.lowq td{background:#fff8e1}
details{margin:.6rem 0}
details summary{cursor:pointer;font-weight:600;font-size:1rem;padding:.3rem 0}
@media (max-width:640px){
  body{margin:.8rem auto}
  h1{font-size:1.1rem}
  td,th{padding:.28rem .4rem;font-size:.78rem}
  table{min-width:26rem}
  .bar{width:6rem}
  .kpi{padding:.4rem .6rem;min-width:4.1rem}
  .kpi b{font-size:1.1rem}
  .roommap{grid-template-columns:repeat(2,minmax(2.9rem,1fr)) .8rem repeat(2,minmax(2.9rem,1fr));max-width:22rem}
  .seat{font-size:.6rem;min-height:1.8rem;padding:.15rem .2rem}
  .seat b{font-size:.72rem}
}</style>
<h1>FEM in der Thermodynamik — Fortschritts-Dashboard</h1>
<p><strong>%d</strong> Teilnehmende mit Login · <strong>%d</strong> Aufgaben im Katalog · Stand: %s
· <em>aktualisiert sich alle 30 s selbst · PC-Namen nur im RAM</em></p>
%s
<h2>Kurs gesamt</h2>
<details open><summary>Wie weit ist der Kurs? (Anteil gelöster Aufgaben pro Person)</summary>
<div class="tablewrap"><table>%s</table></div></details>
<details><summary>Pro Praktikum (begonnen / komplett)</summary>
<div class="tablewrap"><table><tr><th></th><th>mind. 1 Aufgabe gelöst</th><th>komplett gelöst</th></tr>%s</table></div></details>
<details><summary>Pro Aufgabe (Lösequote · ø Versuche · Volltreffer im 1. Versuch)</summary>
<div class="tablewrap"><table><tr><th>Aufgabe</th><th>gelöst</th><th>Lösequote</th><th>ø Versuche</th><th>Volltreffer</th></tr>%s</table></div>
<p><em>Gelb hinterlegt: Lösequote unter 40 %% (ab 5 Personen) — Kandidaten zum Nachschärfen.</em></p></details>
</html>""" % (n, len(answers), datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
              live_html, dist_rows, p_rows, q_rows)
    return html


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
