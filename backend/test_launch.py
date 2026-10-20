"""Self-contained end-to-end test: starts the backend with a mocked OPAL
platform (local JWKS server + signed id_tokens) and tests LTI 1.3, LTI 1.1
and the results API.

Run:  .venv/bin/python test_launch.py
"""

import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse

import jwt
import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from requests_oauthlib import OAuth1

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = "http://127.0.0.1:5099"
PLATFORM = "http://127.0.0.1:5098"
CLIENT_ID = "test-client-id"
KEY = "strukturmechanik"
SECRET = "change-me"

failures = []


def check(name, cond, info=""):
    print(("PASS" if cond else "FAIL") + f"  {name}  {info}")
    if not cond:
        failures.append(name)


# --- mock OPAL platform (serves its JWKS) ------------------------------------

platform_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
platform_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(platform_key.public_key()))
platform_jwk.update({"kid": "opal-key-1", "alg": "RS256", "use": "sig"})


ags_received = []  # von der Mock-Plattform empfangene Score-Posts


class JWKSHandler(http.server.BaseHTTPRequestHandler):
    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._json({"keys": [platform_jwk]})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode()
        if self.path == "/token":
            form = dict(urllib.parse.parse_qsl(raw))
            claims = jwt.decode(form.get("client_assertion", ""), options={"verify_signature": False})
            if claims.get("iss") != CLIENT_ID:
                return self._json({"error": "bad assertion"}, 400)
            return self._json({"access_token": "mock-ags-token", "expires_in": 3600})
        if self.path.startswith("/lineitem/7/scores"):
            if self.headers.get("Authorization") != "Bearer mock-ags-token":
                return self._json({"error": "unauthorized"}, 401)
            ags_received.append(json.loads(raw))
            return self._json({"ok": True})
        return self._json({"error": "not found"}, 404)

    def log_message(self, *a):
        pass


def make_id_token(nonce, sub="opal-user-13", override=None):
    now = int(time.time())
    claims = {
        "iss": PLATFORM,
        "aud": CLIENT_ID,
        "sub": sub,
        "iat": now,
        "exp": now + 300,
        "nonce": nonce,
        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "1",
        "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "kurs-fem-2026"},
        "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
            "lineitem": PLATFORM + "/lineitem/7",
        },
    }
    if override:
        claims.update(override)
    return jwt.encode(claims, platform_key, algorithm="RS256", headers={"kid": "opal-key-1"})


def main():
    jwks_srv = http.server.HTTPServer(("127.0.0.1", 5098), JWKSHandler)
    threading.Thread(target=jwks_srv.serve_forever, daemon=True).start()

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "answers.json"), "w") as f:
        json.dump({
            "/T/Ueb:q0": {"answer": 7.378, "tolerance": 0.1, "points": 5, "attempts": 5,
                          "diagnose": [{"value": 7.747, "hint": "Material zugeordnet?"}]},
            "/T/Ueb:mc0": {"correct": ["a", "c"], "points": 4, "attempts": 3},
        }, f)
    env = dict(os.environ,
               ANSWERS_PATH=os.path.join(tmp, "answers.json"),
               DB_PATH=os.path.join(tmp, "test.db"),
               PRIVATE_KEY_PATH=os.path.join(tmp, "key.pem"),
               BACKEND_URL=BACKEND,
               LTI13_ISSUER=PLATFORM,
               LTI13_AUTH_URL=PLATFORM + "/auth",
               LTI13_KEYSET_URL=PLATFORM + "/keys",
               LTI13_TOKEN_URL=PLATFORM + "/token",
               LTI13_CLIENT_ID=CLIENT_ID,
               LTI_CONSUMER_KEY=KEY,
               LTI_CONSUMER_SECRET=SECRET,
               DASHBOARD_TOKEN="test-dashboard-key",
               PCNAMES_PATH=os.path.join(tmp, "pc-names.json"),
               VAPID_PATH=os.path.join(tmp, "vapid.pem"),
               HILFE_TEST="1",
               FLASK_RUN_PORT="5099")
    with open(os.path.join(tmp, "pc-names.json"), "w") as f:
        json.dump({"10.0.0.7": "N103 Platz 7", "10.0.0.8": "N103 Platz 8"}, f)
    server = subprocess.Popen(
        [sys.executable, "-c",
         "import app; app.app.run(host='127.0.0.1', port=5099)"],
        cwd=HERE, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                requests.get(BACKEND + "/api/stats", timeout=1)
                break
            except requests.ConnectionError:
                time.sleep(0.2)

        # ---- LTI 1.3 -----------------------------------------------------
        # 1. OIDC login initiation
        r = requests.get(BACKEND + "/lti/login", params={
            "iss": PLATFORM, "login_hint": "hint-1", "client_id": CLIENT_ID,
            "target_link_uri": BACKEND + "/lti/launch13",
        }, allow_redirects=False)
        check("1.3 login redirects to platform", r.status_code == 302
              and r.headers["Location"].startswith(PLATFORM + "/auth?"))
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(r.headers["Location"]).query))
        check("1.3 login passes nonce+state", bool(q.get("nonce")) and bool(q.get("state")))
        check("1.3 redirect_uri correct", q.get("redirect_uri") == BACKEND + "/lti/launch13")

        # 2. platform posts signed id_token back
        r = requests.post(BACKEND + "/lti/launch13",
                          data={"id_token": make_id_token(q["nonce"]), "state": q["state"]},
                          allow_redirects=False)
        check("1.3 launch accepted", r.status_code == 302, f"status={r.status_code} {r.text[:200]}")
        frag = urllib.parse.urlparse(r.headers.get("Location", "")).fragment
        token13 = dict(urllib.parse.parse_qsl(frag)).get("ac_token")
        check("1.3 token issued", bool(token13))

        # 3. wrong nonce rejected
        r = requests.post(BACKEND + "/lti/launch13",
                          data={"id_token": make_id_token("wrong-nonce"), "state": q["state"]},
                          allow_redirects=False)
        check("1.3 wrong nonce rejected", r.status_code == 401)

        # 4. token signed by foreign key rejected
        foreign = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        bad = jwt.encode({"iss": PLATFORM, "aud": CLIENT_ID, "sub": "x",
                          "nonce": q["nonce"], "exp": int(time.time()) + 300},
                         foreign, algorithm="RS256", headers={"kid": "opal-key-1"})
        r = requests.post(BACKEND + "/lti/launch13",
                          data={"id_token": bad, "state": q["state"]}, allow_redirects=False)
        check("1.3 foreign signature rejected", r.status_code == 401)

        # 5. tool JWKS is served
        r = requests.get(BACKEND + "/lti/jwks")
        check("tool jwks served", r.status_code == 200 and r.json()["keys"][0]["kty"] == "RSA")

        # ---- LTI 1.1 (fallback) ------------------------------------------
        params = {"lti_message_type": "basic-lti-launch-request", "lti_version": "LTI-1p0",
                  "resource_link_id": "el-1", "user_id": "opal-user-11", "context_id": "kurs"}
        r = requests.post(BACKEND + "/lti/launch", data=params,
                          auth=OAuth1(KEY, SECRET, signature_type="body"), allow_redirects=False)
        check("1.1 launch accepted", r.status_code == 302, f"status={r.status_code}")
        r = requests.post(BACKEND + "/lti/launch", data=params,
                          auth=OAuth1(KEY, "wrong", signature_type="body"), allow_redirects=False)
        check("1.1 bad signature rejected", r.status_code == 401)

        # ---- results API (with the 1.3 token) ----------------------------
        headers = {"Authorization": f"Bearer {token13}"}
        results = {"/P1/Uebung-1:q0": {"best": 5, "max": 5, "attempts": 1},
                   "/P1/Uebung-1:q1": {"best": 3, "max": 5, "attempts": 3}}
        r = requests.post(BACKEND + "/api/results", json={"results": results}, headers=headers)
        check("results stored", r.status_code == 200 and r.json().get("ok"), r.text[:100])
        r = requests.post(BACKEND + "/api/results", headers=headers,
                          json={"results": {"/P1/Uebung-1:q0": {"best": 1, "max": 5, "attempts": 2}}})
        check("downgrade request ok", r.status_code == 200)
        r = requests.get(BACKEND + "/api/results", headers=headers)
        pulled = r.json().get("results", {})
        check("results pullable for merge",
              pulled.get("/P1/Uebung-1:q0", {}).get("best") == 5 and len(pulled) == 2, str(pulled))
        me = requests.get(BACKEND + "/api/me", headers=headers).json()
        check("me total = 8 (best kept)", me.get("total_points") == 8, str(me))
        check("me is pseudonymous", "opal-user" not in str(me))
        check("no token -> 401", requests.get(BACKEND + "/api/me").status_code == 401)
        r = requests.get(BACKEND + "/api/stats")
        check("stats anonymous + solved count", r.status_code == 200 and "opal-user" not in r.text
              and all("solved" in row for row in r.json()))
        r = requests.get(BACKEND + "/api/questions")
        check("question catalog public, no answers",
              r.status_code == 200 and "/T/Ueb:q0" in r.json() and "answer" not in r.text)
        check("dashboard needs key", requests.get(BACKEND + "/dashboard").status_code == 403)
        r = requests.get(BACKEND + "/dashboard", params={"key": "test-dashboard-key"})
        check("dashboard renders overview",
              r.status_code == 200 and "Teilnehmende" in r.text and "Praktikum 1" in r.text
              and "opal-user" not in r.text)
        check("dashboard: Thermo-Kurs, ohne Knackpunkt und Spiele",
              "Angewandte FEM in der Thermodynamik" in r.text and "Strukturmechanik" not in r.text
              and "Knackpunkt" not in r.text and "spiel" not in r.text.lower()
              and "Modell-Detektiv" not in r.text and "Schwachstelle" not in r.text)
        # 405 statt 404: /api/<pfad> kennt nur OPTIONS (CORS-Preflight), wie bei jeder unbekannten API-Adresse
        check("Knackpunkt- und Spiele-Endpunkte gibt es nicht",
              all(requests.get(BACKEND + u).status_code in (404, 405) for u in
                  ("/api/kp?teil=f0", "/api/kp/meine", "/api/kp/freigabe", "/api/kp/schluessel", "/api/spiele"))
              and requests.get(BACKEND + "/dashboard-spiel-toggle", params={"key": "test-dashboard-key", "spiel": "det"}).status_code == 404)

        # ---- server-side checking (/api/check) ---------------------------
        # guest: correct within tolerance, no points but solution on success
        r = requests.post(BACKEND + "/api/check",
                          json={"qid": "/T/Ueb:q0", "value": "7,4", "attemptsUsed": 0}).json()
        check("guest numeric correct", r["correct"] and not r["authed"] and "earned" not in r, str(r))
        r = requests.post(BACKEND + "/api/check",
                          json={"qid": "/T/Ueb:q0", "value": 9.9, "attemptsUsed": 0}).json()
        check("guest wrong, no solution yet", not r["correct"] and "solution" not in r
              and "diagnosis" not in r, str(r))

        # Diagnose: aufgabenspezifischer Fehlwert vor den typischen Faktoren
        def diag(value):
            return requests.post(BACKEND + "/api/check", json={
                "qid": "/T/Ueb:q0", "value": value, "attemptsUsed": 0}).json().get("diagnosis", "")
        check("diagnosis: data-diagnose-Wert", diag("7,75") == "Material zugeordnet?")
        check("diagnosis: Faktor 1000 (Einheit)", "1000-mal zu klein" in diag(0.007378)
              and "1000-mal zu groß" in diag(7378))
        check("diagnosis: Vorzeichen", "Vorzeichen" in diag(-7.378))
        check("diagnosis: ohne Lastfaktoren der Strukturmechanik", diag(14.756) == "" and diag(3.689) == "")
        r = requests.post(BACKEND + "/api/check", json={"qid": "/T/Ueb:q0", "value": 0.007378, "attemptsUsed": 0}).json()
        check("check ohne Strukturbaum-Felder", "diagnosisKnoten" not in r and "wahrscheinlichkeit" not in r, str(r))
        p7, p8 = {"X-Forwarded-For": "10.0.0.7"}, {"X-Forwarded-For": "10.0.0.8"}

        # Hilfe-App: Schlüssel nötig, Warteschlange mit Platz, Push bei neuer Anfrage, erledigt
        import base64
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        HK = {"X-Key": "test-dashboard-key"}
        pushes = []

        class PushSink(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                pushes.append({"auth": self.headers.get("Authorization", ""), "enc": self.headers.get("Content-Encoding"),
                               "body": self.rfile.read(int(self.headers.get("Content-Length", 0)))})
                self.send_response(201)
                self.end_headers()

            def log_message(self, *a):
                pass
        sink = http.server.HTTPServer(("127.0.0.1", 5096), PushSink)
        threading.Thread(target=sink.serve_forever, daemon=True).start()
        check("hilfe: ohne Schlüssel gesperrt", requests.get(BACKEND + "/api/hilfe").status_code == 403)
        check("hilfe: Seite und Manifest", requests.get(BACKEND + "/hilfe/").status_code == 200
              and "manifest+json" in requests.get(BACKEND + "/hilfe/manifest.webmanifest").headers["Content-Type"])
        check("hilfe: App heißt Hilfe FEM-TD", "Hilfe FEM-TD" in requests.get(BACKEND + "/hilfe/").text
              and requests.get(BACKEND + "/hilfe/manifest.webmanifest").json()["name"] == "Hilfe FEM-TD")
        r = requests.get(BACKEND + "/hilfe/sw.js")
        check("hilfe: Service Worker ohne Cache", r.status_code == 200 and r.headers.get("Cache-Control") == "no-cache"
              and "/thermo/hilfe/" in r.text)
        r = requests.post(BACKEND + "/api/hilfe/schalter", headers=HK, json={"an": True}).json()
        check("hilfe: Schalter an, VAPID-Schlüssel da", r["an"] and len(base64.urlsafe_b64decode(r["vapid"] + "==")) == 65, str(r))
        geraet = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        abo = {"endpoint": "http://127.0.0.1:5096/push/1", "keys": {
            "p256dh": base64.urlsafe_b64encode(geraet).rstrip(b"=").decode(),
            "auth": base64.urlsafe_b64encode(os.urandom(16)).rstrip(b"=").decode()}}
        check("hilfe: Push-Abo gespeichert", requests.post(BACKEND + "/api/hilfe/abo", headers=HK, json={"abo": abo}).json() == {"ok": True})
        requests.post(BACKEND + "/api/help", headers=p7, json={"page": "/Thermische-Analyse/P1_Einfuehrung/03_Selbsttests/Uebung-3"})
        requests.post(BACKEND + "/api/help", headers=p8, json={"page": "/Thermische-Analyse/P1_Einfuehrung/03_Selbsttests/Uebung-1"})
        r = requests.get(BACKEND + "/dashboard", params={"key": "test-dashboard-key"})
        check("dashboard: Wartende in der Raumkarte wie in der App",
              "Raum N103" in r.text and '<span class="seat s-next" title="wartet auf Hilfe"><b>7</b>' in r.text
              and '<sup>1.</sup>' in r.text and '<span class="seat s-hilfe" title="wartet auf Hilfe"><b>8</b>' in r.text
              and '<sup>2.</sup>' in r.text and "wartet auf Hilfe</b>" in r.text)
        for _ in range(40):
            if len(pushes) >= 2:
                break
            time.sleep(0.25)
        check("hilfe: Push je neuer Anfrage, verschlüsselt mit VAPID",
              len(pushes) == 2 and all(x["enc"] == "aes128gcm" and x["auth"].startswith("vapid") for x in pushes), str(pushes)[:300])
        r = requests.get(BACKEND + "/api/hilfe", headers=HK).json()
        e = r["eintraege"]
        check("hilfe: Reihenfolge mit Raum, Platz, Seite",
              [(x["raum"], x["platz"], x["seite"]) for x in e] == [("N103", 7, "P1 Übung 3"), ("N103", 8, "P1 Übung 1")], str(r))
        check("hilfe: aktiver Raum aus den Anfragen", r["raum_aktiv"] == "N103", str(r.get("raum_aktiv")))
        r = requests.post(BACKEND + "/api/hilfe/erledigt", headers=HK, json={"id": e[0]["id"]}).json()
        check("hilfe: erledigt, Platz 8 ist der nächste", [x["platz"] for x in r["eintraege"]] == [8], str(r))
        requests.post(BACKEND + "/api/help", headers=p8, json={"page": "x"})
        check("hilfe: kein zweiter Push für offene Anfrage", len(pushes) == 2)
        # Beschreibung nachreichen, Einschätzung, schnelle Fälle rücken vor
        requests.post(BACKEND + "/api/help", headers=p8, json={"page": "x", "text": " Temperatur passt nicht,\nWert zu groß "})
        r = requests.post(BACKEND + "/api/help", headers=p7, json={"page": "y", "text": "ANSYS stürzt ab"})
        p9 = {"X-Forwarded-For": "10.0.0.9"}
        requests.post(BACKEND + "/api/help", headers=p9, json={"page": "z", "text": "Wo finde ich die Konvektion?"})
        e = requests.get(BACKEND + "/api/hilfe", headers=HK).json()["eintraege"]
        check("hilfe: Beschreibung gesäubert", e[0]["text"] == "Temperatur passt nicht, Wert zu groß", str(e))
        check("hilfe: Einschätzung und Reihenfolge",
              [(x["label"], x["art"], x["schnell"], x["vorgezogen"]) for x in e]
              == [("N103 Platz 8", "Ergebnis passt nicht", True, False), ("10.0.0.9", "Bedienung", True, True),
                  ("N103 Platz 7", "Technik", False, False)], str(e))
        for _ in range(40):
            if len(pushes) >= 5:
                break
            time.sleep(0.25)
        check("hilfe: Push auch für nachgereichte Beschreibung", len(pushes) == 5, str(len(pushes)))
        r = requests.get(BACKEND + "/dashboard", params={"key": "test-dashboard-key"})
        check("dashboard: Beschreibung und Einschätzung", "„ANSYS stürzt ab“" in r.text and "Bedienung</b>, meist schnell" in r.text)
        for x in e:
            if x["platz"] != 8:
                requests.post(BACKEND + "/api/hilfe/erledigt", headers=HK, json={"id": x["id"]})
        import sqlite3
        tdb = sqlite3.connect(os.path.join(tmp, "test.db"))
        tdb.execute("INSERT INTO results (pseudonym, qid, best, max, attempts, updated_at) VALUES (?, ?, 0, 5, 5, ?)",
                    ("test-aufgegeben", "/T/Ueb:q0", time.time()))
        tdb.execute("INSERT INTO results (pseudonym, qid, best, max, attempts, updated_at) VALUES (?, ?, 0, 5, 3, ?)",
                    ("test-haengt", "/T/Ueb:q0", time.time()))
        tdb.commit()
        r = requests.get(BACKEND + "/api/hilfe", headers=HK).json()
        check("hilfe: empfohlen mit aufgegeben vor hängt",
              [(x["aufgegeben"], x["versuche"], x["frage"]) for x in r["empfohlen"]] == [(True, 5, "T Ueb · Frage 1"), (False, 3, "T Ueb · Frage 1")]
              and r["empfohlen"][0]["label"].startswith("…"), str(r["empfohlen"]))
        tdb.execute("DELETE FROM results WHERE pseudonym IN ('test-aufgegeben', 'test-haengt')")
        tdb.commit()
        tdb.close()
        r = requests.post(BACKEND + "/api/hilfe/schalter", headers=HK, json={"an": False}).json()
        check("hilfe: ausschalten schließt offene Anfragen", not r["an"] and r["eintraege"] == [], str(r))
        sink.shutdown()

        r = requests.get(BACKEND + "/dashboard", params={"key": "test-dashboard-key"})
        check("dashboard zeigt Fehlwerte mit Ursache",
              "Häufige Fehlwerte heute" in r.text and "Material zugeordnet?" in r.text
              and "<em>unbekannt</em>" in r.text)
        r = requests.post(BACKEND + "/api/check",
                          json={"qid": "/T/Ueb:q0", "value": 9.9, "attemptsUsed": 4}).json()
        check("guest exhausted -> solution", not r["correct"] and r.get("solution") == 7.378, str(r))
        check("unknown qid -> 404", requests.post(
            BACKEND + "/api/check", json={"qid": "/nix", "value": 1}).status_code == 404)

        # authed: attempts server-tracked, points scale with attempt number
        r = requests.post(BACKEND + "/api/check", headers=headers,
                          json={"qid": "/T/Ueb:q0", "value": 9.9}).json()
        check("authed wrong attempt 1", not r["correct"] and r["attempts"] == 1 and r["authed"], str(r))
        r = requests.post(BACKEND + "/api/check", headers=headers,
                          json={"qid": "/T/Ueb:q0", "value": 7.378}).json()
        check("authed correct attempt 2 -> volle 5 P. (Mastery)",
              r["correct"] and r["attempts"] == 2 and r["earned"] == 5 and r["best"] == 5, str(r))
        r = requests.post(BACKEND + "/api/check", headers=headers,
                          json={"qid": "/T/Ueb:q0", "value": 7.378}).json()
        check("authed re-check keeps attempts/best",
              r["attempts"] == 2 and r["best"] == 5, str(r))
        r = requests.post(BACKEND + "/api/check", headers=headers,
                          json={"qid": "/T/Ueb:mc0", "selected": ["a", "c"]}).json()
        check("authed MC first try -> 4 P. + 1 Bonus",
              r["correct"] and r["earned"] == 5 and r.get("solution") == ["a", "c"], str(r))
        me2 = requests.get(BACKEND + "/api/me", headers=headers).json()
        check("checked points land in /api/me", me2["total_points"] == 18, str(me2))

        # ---- AGS: Score-Push an die Mock-Plattform -----------------------
        # Meldungen laufen nacheinander; warten, bis die letzte den Endstand trägt
        for _ in range(40):
            if ags_received and ags_received[-1].get("scoreGiven") == 18:
                break
            time.sleep(0.25)
        check("AGS score received by platform", len(ags_received) > 0, str(ags_received))
        if ags_received:
            last = ags_received[-1]
            check("AGS userId is original sub", last.get("userId") == "opal-user-13", str(last))
            check("AGS scoreGiven = total points", last.get("scoreGiven") == 18, str(last))
            # (5+1) q0 + (4+1) mc0
            check("AGS scoreMaximum incl. Bonus", last.get("scoreMaximum") == 11, str(last))
            check("AGS grading complete", last.get("gradingProgress") == "FullyGraded")

        # ---- Sollwert-Korrektur im Dashboard und Nachwertung ---------------
        # eigene Frage erst jetzt in den Katalog, damit das AGS-Maximum oben stimmt
        from itsdangerous import URLSafeTimedSerializer
        ser = URLSafeTimedSerializer(env.get("SECRET_KEY", "dev-secret-change-me"), salt="ac-session")

        def person(sub):
            return {"Authorization": "Bearer " + ser.dumps({"sub": sub})}
        QK = "/T/Korr:q0"
        with open(os.path.join(tmp, "answers.json")) as f:
            katalog = json.load(f)
        katalog[QK] = {"answer": 271.05, "tolerance": 0.5, "points": 5, "attempts": 5,
                       "titel": "Die maximale Temperatur in °C", "quelle": "T/Korr.md"}
        with open(os.path.join(tmp, "answers.json"), "w") as f:
            json.dump(katalog, f)

        def eingabe(h, wert):
            return requests.post(BACKEND + "/api/check", headers=h, json={"qid": QK, "value": wert}).json()

        def punkte(h):
            return requests.get(BACKEND + "/api/results", headers=h).json()["results"][QK]["best"]
        A, B, C = person("test-a"), person("test-b"), person("test-c")
        for wert in (300, 271.97, 1, 2, 3):  # 2. Versuch passt zum späteren Sollwert, danach nur Falsches
            eingabe(A, wert)
        eingabe(B, 271.97)                    # 1. Versuch passt zum späteren Sollwert
        check("alter Sollwert gilt noch", eingabe(B, 271.05).get("best") == 5)
        eingabe(C, 10)
        eingabe(C, 20)
        eingabe({}, 271.97)                   # Gast: wird nicht gespeichert
        tdb = sqlite3.connect(os.path.join(tmp, "test.db"))
        check("eingaben: nur gezählte Versuche mit Login",
              tdb.execute("SELECT COUNT(*) FROM eingaben WHERE qid=?", (QK,)).fetchone()[0] == 9)
        K = {"key": "test-dashboard-key"}
        check("sollwerte brauchen den Schlüssel",
              requests.get(BACKEND + "/dashboard-sollwerte").status_code == 403
              and requests.post(BACKEND + "/dashboard-sollwert",
                                data={"qid": QK, "answer": 1, "tolerance": 1}).status_code == 403)
        r = requests.get(BACKEND + "/dashboard-sollwerte", params=K)
        check("sollwerte listen Zahlenfragen mit Titel", r.status_code == 200
              and "Die maximale Temperatur in °C" in r.text and "271,05 ± 0,5" in r.text
              and "Angewandte FEM in der Thermodynamik" in r.text)
        r = requests.get(BACKEND + "/dashboard-sollwerte", params=dict(K, qid=QK, answer="271,97", tolerance="0,5"))
        check("vorschau: zwei bekommen Punkte, drei Fehlwerte passen",
              "Bekommen nachträglich Punkte: <b>2 Personen</b>" in r.text and "3 Einträge passend" in r.text)
        check("vorschau schreibt nichts", tdb.execute("SELECT COUNT(*) FROM korrekturen").fetchone()[0] == 0)
        r = requests.post(BACKEND + "/dashboard-sollwert", params=K, allow_redirects=False,
                          data={"qid": QK, "answer": "271.97", "tolerance": "0.5"})
        check("korrektur gespeichert", r.status_code == 302 and "n=2" in r.headers.get("Location", ""),
              r.headers.get("Location"))
        check("nachwertung: 2. Versuch zählt voll, auch wenn danach alles falsch war", punkte(A) == 5)
        check("nachwertung: 1. Versuch mit Bonus statt der 5 P. aus dem 2.", punkte(B) == 6)
        check("nachwertung: ohne passende Eingabe unverändert", punkte(C) == 0)
        check("fehlwert-log bereinigt", tdb.execute(
            "SELECT COUNT(*) FROM wrong_values WHERE qid=? AND ABS(value - 271.97) <= 0.5", (QK,)).fetchone()[0] == 0)
        check("korrektur gilt sofort", eingabe(person("test-d"), 271.97).get("correct") is True)
        r = requests.get(BACKEND + "/dashboard-sollwerte", params=dict(K, ok="gespeichert", qid=QK, n=2, f=3))
        check("sollwerte zeigen die aktive Korrektur", "Aktive Korrekturen" in r.text
              and '(docs/T/Korr.md): data-answer="271.97" data-tolerance="0.5"' in r.text
              and "2 Personen nachträglich gewertet" in r.text)
        check("dashboard verlinkt die Sollwerte",
              "dashboard-sollwerte?key=" in requests.get(BACKEND + "/dashboard", params=K).text)
        requests.post(BACKEND + "/dashboard-sollwert-zurueck", params=K, data={"qid": QK})
        check("zurückgenommen: alter Sollwert gilt wieder, Punkte bleiben",
              eingabe(person("test-e"), 271.05).get("correct") is True and punkte(A) == 5)
        requests.post(BACKEND + "/api/reset", headers=A)
        check("reset löscht die eigenen Eingaben", tdb.execute(
            "SELECT COUNT(*) FROM eingaben WHERE pseudonym='test-a'").fetchone()[0] == 0)
        tdb.close()

        # ---- Zurücksetzen: alter Stand aus einem anderen Browser wird abgelehnt -------------
        R = person("test-r")
        alt = requests.get(BACKEND + "/api/me", headers=R).json()["generation"]
        stand = {"results": {"/T/P3:q0": {"best": 5, "max": 5, "attempts": 1}}}
        check("ohne Zurücksetzen: Abgleich ohne Generation geht (älteres Skript)",
              requests.post(BACKEND + "/api/results", headers=R, json=stand).status_code == 200)
        r = requests.post(BACKEND + "/api/reset", headers=R).json()
        neu = requests.get(BACKEND + "/api/me", headers=R).json()["generation"]
        check("zurücksetzen: neue Generation mit Marke",
              r.get("generation") == neu and neu.startswith(alt + ":"), str(r))
        check("anderer Browser: Stand mit alter Generation abgelehnt", requests.post(
            BACKEND + "/api/results", headers=R, json=dict(stand, generation=alt)).status_code == 409)
        check("anderer Browser mit älterem Skript (ohne Generation) abgelehnt",
              requests.post(BACKEND + "/api/results", headers=R, json=stand).status_code == 409)
        check("vom alten Stand nichts gespeichert",
              requests.get(BACKEND + "/api/results", headers=R).json()["results"] == {})
        check("Abgleich mit aktueller Generation geht", requests.post(
            BACKEND + "/api/results", headers=R, json=dict(stand, generation=neu)).status_code == 200)

        # ---- Mein Spickzettel: je Person gespeichert -----------------------------------------
        S1, S2 = person("test-s1"), person("test-s2")
        check("Spickzettel ohne Anmeldung abgelehnt", requests.get(BACKEND + "/api/spickzettel").status_code == 401)
        check("Spickzettel anfangs leer", requests.get(BACKEND + "/api/spickzettel", headers=S1).json()["daten"] is None)
        zettel = {"stand": 1, "kern": {"kern-p1-x": "lang"}, "check": {}, "notizen": {"P1": "Einheiten prüfen"}}
        check("Spickzettel speichern", requests.post(BACKEND + "/api/spickzettel", headers=S1,
                                                     json={"daten": zettel}).status_code == 200)
        check("Spickzettel zurück", requests.get(BACKEND + "/api/spickzettel", headers=S1).json()["daten"] == zettel)
        check("Spickzettel nur für die eigene Person",
              requests.get(BACKEND + "/api/spickzettel", headers=S2).json()["daten"] is None)
        check("Spickzettel zu groß abgelehnt", requests.post(BACKEND + "/api/spickzettel", headers=S1,
              json={"daten": {"notizen": {"P1": "x" * 60000}}}).status_code == 400)

    finally:
        server.terminate()
        jwks_srv.shutdown()

    if failures:
        print(f"\n{len(failures)} Tests fehlgeschlagen: {failures}")
        sys.exit(1)
    print("\nAlle Tests bestanden.")


if __name__ == "__main__":
    main()
