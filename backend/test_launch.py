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
            "/T/Ueb:q0": {"answer": 7.378, "tolerance": 0.1, "points": 5, "attempts": 5},
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
               FLASK_RUN_PORT="5099")
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

        # ---- server-side checking (/api/check) ---------------------------
        # guest: correct within tolerance, no points but solution on success
        r = requests.post(BACKEND + "/api/check",
                          json={"qid": "/T/Ueb:q0", "value": "7,4", "attemptsUsed": 0}).json()
        check("guest numeric correct", r["correct"] and not r["authed"] and "earned" not in r, str(r))
        r = requests.post(BACKEND + "/api/check",
                          json={"qid": "/T/Ueb:q0", "value": 9.9, "attemptsUsed": 0}).json()
        check("guest wrong, no solution yet", not r["correct"] and "solution" not in r, str(r))
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
        for _ in range(40):
            if ags_received:
                break
            time.sleep(0.25)
        check("AGS score received by platform", len(ags_received) > 0, str(ags_received))
        if ags_received:
            last = ags_received[-1]
            check("AGS userId is original sub", last.get("userId") == "opal-user-13", str(last))
            check("AGS scoreGiven = total points", last.get("scoreGiven") == 18, str(last))
            check("AGS scoreMaximum incl. Bonus", last.get("scoreMaximum") == 11, str(last))
            check("AGS grading complete", last.get("gradingProgress") == "FullyGraded")

    finally:
        server.terminate()
        jwks_srv.shutdown()

    if failures:
        print(f"\n{len(failures)} Tests fehlgeschlagen: {failures}")
        sys.exit(1)
    print("\nAlle Tests bestanden.")


if __name__ == "__main__":
    main()
