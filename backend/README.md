# Backend: OPAL-Login (LTI 1.3, Fallback 1.1) + anonyme Ergebnisspeicherung

Kleiner Flask-Dienst, der die statische MkDocs-Seite um zwei Dinge ergänzt:

1. **Login über OPAL** — im OPAL-Kurs wird ein Kursbaustein „LTI-Seite" angelegt.
   OPAL startet den LTI-1.3/OIDC-Flow, der Dienst validiert das signierte
   id_token gegen den OPAL-Keyset, **pseudonymisiert** die Nutzer-ID (salted
   SHA-256, kein Klartext-Login wird gespeichert) und leitet mit einem
   Session-Token im URL-Fragment auf die Seite weiter. Die Optik der Seite
   bleibt unberührt — OPAL öffnet sie im neuen Fenster.
2. **Ergebnisspeicherung** — `backend-sync.js` auf der Seite schickt den
   localStorage-Punktestand (`answer_best_*`, `answer_attempts_*`) an
   `POST /api/results`. Ohne Token/Backend-URL läuft die Seite wie bisher rein
   lokal weiter.

## Lokal ausprobieren

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py                 # startet auf http://127.0.0.1:5000
.venv/bin/python test_launch.py         # simuliert einen OPAL-Launch, prüft alles
```

## Endpunkte

| Endpunkt | Zweck |
|---|---|
| `GET/POST /lti/login` | LTI 1.3: OIDC-Login-Initiation („Login URL des Tools") |
| `POST /lti/launch13` | LTI 1.3: Launch-Callback mit id_token („Launch URL des Tools") → Redirect zur Seite mit `#ac_token=…` |
| `GET /lti/jwks` | LTI 1.3: öffentlicher Schlüsselsatz des Tools („Keyset URL des Tools") |
| `POST /lti/launch` | LTI-1.1-Fallback (OAuth1-signiert) |
| `POST /api/results` | Punktestand speichern (Bearer-Token; Best-Score wird nie verschlechtert) |
| `GET /api/me` | eigener Punktestand (pseudonym) |
| `GET/POST /api/spickzettel` | „Mein Spickzettel“: Auswahl und eigene Notizen je Person (Bearer-Token; der Browser schickt nur einen neueren Stand) |
| `GET /api/stats` | anonyme Aggregatstatistik pro Frage (für Lehr-Analytik) |
| `POST /api/reset` | „Fortschritt zurücksetzen“ auf „Mein Fortschritt“: eigene Ergebnisse und Eingaben löschen (Bearer-Token) |
| `GET/POST /api/help` | „Hand heben“ auf der Kursseite: Meldung mit kurzer Beschreibung (freiwillig), Platz in der Warteschlange |
| `GET /hilfe/` | Hilfe-App fürs Handy (zum Home-Bildschirm hinzufügen), Zugang mit dem Dashboard-Schlüssel |
| `GET /api/hilfe` | Hilfe-App: offene Anfragen mit Raum, Platz und Einschätzung, „Hilfe empfohlen“ (Header `X-Key`) |
| `POST /api/hilfe/erledigt`, `/api/hilfe/schalter`, `/api/hilfe/abo` | Hilfe-App: Anfrage erledigt, Hilfe-Knopf an/aus, Web-Push-Abo des Geräts speichern |
| `GET /dashboard?key=…` | Lehrenden-Dashboard (siehe unten) |
| `GET /dashboard-sollwerte?key=…` | Sollwerte der Zahlenfragen, Korrektur mit Vorschau der Nachwertung |
| `POST /dashboard-sollwert?key=…` | Sollwert-Korrektur speichern und gespeicherte Eingaben nachwerten |
| `POST /dashboard-sollwert-zurueck?key=…` | Korrektur zurücknehmen (Wert aus dem Kurstext gilt wieder) |

## Konfiguration (Umgebungsvariablen)

| Variable | Bedeutung |
|---|---|
| `BACKEND_URL` | öffentliche URL dieses Dienstes (für die OIDC redirect_uri) |
| `LTI13_ISSUER` | „Issuer ID (ISS)" aus OPAL (Default: `https://bildungsportal.sachsen.de/opal`) |
| `LTI13_CLIENT_ID` | „Client ID" aus OPAL (wird beim Speichern des Bausteins vergeben) |
| `LTI13_AUTH_URL` | „OIDC Auth URL" aus OPAL |
| `LTI13_KEYSET_URL` | „Keyset URL" aus OPAL (Plattform-Schlüssel) |
| `LTI13_DEPLOYMENT_ID` | „Deployment-ID" aus OPAL |
| `PRIVATE_KEY_PATH` | RSA-Schlüssel des Tools (wird beim ersten Start automatisch erzeugt) |
| `SECRET_KEY` | signiert die Session-Tokens (zufälligen Wert setzen!) |
| `USER_SALT` | Salt für die Pseudonymisierung (zufälligen Wert setzen, danach nie ändern) |
| `SITE_URL` | Ziel-URL nach dem Launch (die GitHub-Pages-Seite) |
| `ALLOWED_ORIGINS` | CORS-Origins, kommagetrennt |
| `DB_PATH` | SQLite-Datei (Default: `backend/results.db`) |
| `LTI_CONSUMER_KEY` / `LTI_CONSUMER_SECRET` | nur für den LTI-1.1-Fallback |
| `DASHBOARD_TOKEN` | Schlüssel für Dashboard und Hilfe-App |
| `VAPID_PATH` | Schlüssel für Web-Push der Hilfe-App (Default: `vapid_private.pem` neben der Datenbank, wird beim ersten Aufruf angelegt) |
| `VAPID_SUB` | Kontakt im Web-Push (Default: `mailto:felix.kaule@htwk-leipzig.de`) |

## OPAL-Einrichtung (Kursbaustein „LTI-Seite", Tab „Konfiguration")

| OPAL-Feld | Wert |
|---|---|
| LTI Version | **LTI 1.3**, Tool: „Eigenes Tool" |
| Login URL des Tools | `https://<backend-host>/lti/login` |
| Launch URL des Tools | `https://<backend-host>/lti/launch13` |
| Schlüsseltyp | „Schlüsselsatz-URL" mit `https://<backend-host>/lti/jwks` — **oder**, wenn das Backend nur per VPN erreichbar ist: „Schlüssel" und den PEM-Text von `https://<backend-host>/lti/pubkey` einfügen |
| ClientID des Tools | frei wählbar bzw. von OPAL vergeben — derselbe Wert muss in `LTI13_CLIENT_ID` stehen |
| Anzeige | **„Neues Fenster öffnen"** (sonst klemmt die Seite im OPAL-iFrame) |

Nach dem Speichern zeigt OPAL unter „Tool Konfiguration" Issuer, OIDC Auth URL,
OAuth2 Token URL, Keyset URL und Deployment-ID an — diese Werte in die
gleichnamigen `LTI13_*`-Umgebungsvariablen übernehmen. Anschließend in
`docs/assets/js/backend-config.js` die Backend-URL eintragen.

## Frontend-Aktivierung

In [docs/assets/js/backend-config.js](../docs/assets/js/backend-config.js) die
Backend-URL setzen — leer = Sync deaktiviert, Seite läuft rein lokal.

## Serverseitige Antwortprüfung

Der MkDocs-Hook `scripts/answers_hook.py` entfernt beim Build alle
`data-answer`/`data-correct`-Attribute aus dem HTML und schreibt sie in
`answers.json` im Projektroot. Diese Datei muss nach jedem Inhalts-Update
mit aufs Backend:

```bash
mkdocs build   # erzeugt answers.json
scp answers.json fing-spool.htwk-leipzig.de:~/thermo-backend/
```

Kein Neustart nötig — die Datei wird bei Änderung automatisch neu geladen.

**Neue Übungsaufgaben im laufenden Semester** sind unproblematisch: Nach dem
Deploy passen sich Fortschrittsringe, Navigations-Zähler, Kurs-Statistik und
AGS-Maximum automatisch an. Bereits verdiente Abzeichen (z.B. „Halbzeit")
bleiben erhalten, auch wenn die Quote durch neue Aufgaben rechnerisch sinkt;
Level können nur steigen, nie fallen.
`POST /api/check` prüft die Antworten: mit Login werden Versuche und Punkte
serverseitig geführt, Gäste bekommen nur richtig/falsch-Feedback.
(Die Antworten stehen weiterhin in den Markdown-Quellen im öffentlichen Repo —
bewusste Entscheidung, es sind Übungen.)

**Fehlwerte:** Jede falsche Zahl wird **anonym** (Frage, Wert, Zeit; ohne
Pseudonym) in `wrong_values` gespeichert. Das Dashboard zeigt daraus „Häufige
Fehlwerte“ (heute und gesamt) mit erkannter Ursache (Vorzeichen, Faktor 1000
für Einheiten); `/api/check` liefert sie zusätzlich als `diagnosis`.

**Sollwert-Korrektur und Nachwertung:** Mit Login speichert `/api/check` jede
gezählte Zahleneingabe mit Pseudonym und Versuchsnummer (Tabelle `eingaben`).
Im Dashboard unter „Sollwerte korrigieren“ (`/dashboard-sollwerte`) lässt sich
ein Sollwert samt Toleranz ändern. Die Korrektur liegt in der Tabelle
`korrekturen` über `answers.json` und gilt sofort; ein späteres Deploy
überschreibt sie nicht. Steht derselbe Wert im Kurstext, verschwindet sie beim
nächsten Öffnen der Seite. Nach jeder Änderung werden die gespeicherten
Eingaben nachgewertet: Der erste passende Versuch zählt, als wäre er damals
richtig gewesen (volle Punkte, Bonus im 1. Versuch), die Note geht neu an
OPAL. Punkte steigen nur, sie sinken nie. Passende Einträge im Fehlwert-Log
werden entfernt. Vorher zeigt eine Vorschau, wer nachträglich Punkte bekommt.
„Fortschritt zurücksetzen“ löscht auch die eigenen Eingaben. Score-Pushes an
OPAL laufen nacheinander, damit die zuletzt gesendete Meldung immer den
aktuellen Stand trägt.

## Hilfe im Praktikum

Auf der Kursseite gibt es den Knopf „Hand heben“ (`docs/assets/js/help-button.js`),
solange er im Dashboard eingeschaltet ist. Nach dem Melden kann man das Problem
kurz beschreiben; das Backend schätzt daraus die Art (Technik, Ergebnis passt
nicht, Bedienung, Verständnis) und ob es meist schnell geht.

Die **Hilfe-App** unter `https://<backend-host>/thermo/hilfe/` zeigt auf dem Handy
die nächste Anfrage mit Raum und Platz, eine Raumkarte, „Hilfe empfohlen“
(wer hängt oder aufgegeben hat) und „Erledigt, nächster“. Einmal den
Dashboard-Schlüssel eingeben, dann in Safari „Zum Home-Bildschirm“; aus der App
vom Home-Bildschirm lassen sich Benachrichtigungen einschalten (Web-Push, iPhone
ab iOS 16.4, die Uhr spiegelt sie). Den VAPID-Schlüssel legt das Backend selbst
an (`VAPID_PATH`), dafür braucht der Dienst Schreibrecht im Ordner der Datenbank.
Push braucht `pywebpush` (steht in `requirements.txt`); fehlt es, läuft alles
andere ohne Push weiter.

## Noten-Rückkanal zu OPAL (AGS)

Bei jeder Punkteverbesserung meldet das Backend die Gesamtpunktzahl als
Score an OPAL (LTI Assignment & Grade Services): Access-Token per signierter
JWT-Assertion gegen `LTI13_TOKEN_URL`, dann POST auf den beim Launch
mitgelieferten Lineitem-Endpunkt. Voraussetzungen:

1. Im OPAL-Kursbaustein die **Bewertung aktivieren** (Tab „Bewertung") —
   erst dann schickt OPAL beim Launch den AGS-Endpunkt mit.
2. `LTI13_TOKEN_URL` in der `.env` (Default: OPAL „OAuth2 Access Token URL").
3. `AGS_ENABLED=1` (Default an; `0` schaltet den Rückkanal komplett ab).

**Datenschutz-Hinweis:** Für AGS muss die originale OPAL-Nutzer-ID gespeichert
werden — sie liegt **verschlüsselt** (Fernet, Schlüssel aus `SECRET_KEY`) in
der Spalte `users.sub_enc` und wird ausschließlich für den Score-Push
entschlüsselt. Ohne `SECRET_KEY` ist keine Re-Identifikation möglich. Mit
`AGS_ENABLED=0` wird sie gar nicht erst gespeichert.

## Betrieb

- **Deploy:** `./backend/deploy.sh` baut die Site (erzeugt `answers.json`) und
  kopiert Backend + Antworten auf den Server; Restart nur bei app.py-Änderungen
  nötig (`sudo systemctl restart thermo-backend`).
- **Backup:** Auf dem Server läuft täglich 3:17 Uhr `~/thermo-backend/backup.sh`
  (Cron des Users `guacamole`), behält die letzten 14 Stände der Datenbank
  unter `~/thermo-backend/backups/`.

## Lehrenden-Dashboard

`https://<backend-host>/thermo/dashboard?key=<DASHBOARD_TOKEN>` zeigt aggregiert
(pseudonym, keine Namen): Hilfe-Warteschlange, Schalter für den Hilfe-Button,
Tagesüberblick (wer ist heute wie weit, Raumkarte, Brennpunkt, häufige
Fehlwerte), Verteilung „wie viele sind wie weit", Fortschritt pro
Praktikum (begonnen/komplett) und Lösungsquote je Aufgabe, dazu den Link
„Sollwerte korrigieren“ (siehe oben). Der Token steht in
der `.env` auf dem Server. Namentliche Einzelstände gibt es stattdessen direkt
in OPAL: im Kursbaustein die **Bewertung aktivieren**, dann erscheinen die per
AGS gemeldeten Punktestände pro Kursmitglied im OPAL-Bewertungswerkzeug.

## Kurs-Reset (Semesterende)

`~/thermo-backend/reset-course.sh` auf dem Server ausführen: legt ein Backup an
und leert danach Ergebnisse, Eingaben und Nutzer, die neue Kohorte startet bei null.

**Alte Stände in anderen Browsern:** Die Seite schickt beim Abgleich ihre Generation mit
(`/api/me` liefert sie). `POST /api/results` lehnt Stände aus der Zeit vor dem
Semester-Reset oder vor „Fortschritt zurücksetzen“ mit 409 ab, der Browser leert sich
dann selbst. „Fortschritt zurücksetzen“ setzt dafür eine Marke je Person (Tabelle `meta`,
Schlüssel `reset:<pseudonym>`), die in die Generation eingeht. Ohne Generation (älteres
Skript im Browser-Cache) wird nur abgelehnt, wenn die Person schon einmal zurückgesetzt hat.

## Bewusste Prototyp-Grenzen / nächste Schritte
- SQLite reicht für einen Kurs locker; bei Bedarf `DB_PATH` auf ein Volume legen
  oder auf Postgres wechseln.
- Deployment hosting-neutral: läuft überall, wo Python läuft (HTWK-VM, Docker,
  `gunicorn -w 2 app:app` hinter einem Reverse-Proxy mit TLS).
