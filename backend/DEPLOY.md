# Deployment auf dem Guacamole-Server

Das Backend läuft als eigener kleiner Dienst (gunicorn auf 127.0.0.1:8100)
neben Guacamole und wird vom vorhandenen Webserver unter dem Pfad **`/thermo/`**
mitbedient — das vorhandene TLS-Zertifikat wird einfach mitbenutzt, an der
Guacamole-Konfiguration ändert sich nichts.

**VPN-only reicht:** Der Server muss nur für die Studierenden erreichbar sein
(HTWK-Netz/VPN) — der komplette Login-Flow läuft über Browser-Redirects.
Einzige Konsequenz: In OPAL als Schlüsseltyp **„Schlüssel"** wählen (statt
„Schlüsselsatz-URL") und den öffentlichen Schlüssel von
`https://<host>/thermo/lti/pubkey` hineinkopieren, denn die Keyset-URL kann OPAL
von außen nicht abrufen.

## 1. Backend installieren

```bash
sudo mkdir -p /opt/thermo-backend/data
sudo chown $USER /opt/thermo-backend /opt/thermo-backend/data
# app.py, requirements.txt, env.example hierher kopieren (z.B. per scp oder git)
cd /opt/thermo-backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt gunicorn
cp env.example .env        # und Werte anpassen! (Secrets, BACKEND_URL, Client-ID)
```

## 2. systemd-Dienst

`/etc/systemd/system/thermo-backend.service`:

```ini
[Unit]
Description=FEM Thermische-Analyse LTI-Backend
After=network.target

[Service]
WorkingDirectory=/opt/thermo-backend
EnvironmentFile=/opt/thermo-backend/.env
# SCRIPT_NAME sorgt dafür, dass die App unter dem Präfix /thermo läuft
Environment=SCRIPT_NAME=/thermo
ExecStart=/opt/thermo-backend/.venv/bin/gunicorn -w 2 -b 127.0.0.1:8100 app:app
Restart=on-failure
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /opt/thermo-backend/data
sudo systemctl daemon-reload
sudo systemctl enable --now thermo-backend
curl -s http://127.0.0.1:8100/thermo/api/stats   # → [] wenn alles läuft
```

## 3. Reverse-Proxy-Eintrag

**nginx** (in den bestehenden `server { … ssl … }`-Block, in dem auch
Guacamole steckt):

```nginx
location /thermo/ {
    proxy_pass http://127.0.0.1:8100;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto https;
}
```

**Apache** (falls Guacamole hinter Apache läuft; Module `proxy`,
`proxy_http` sind für Guacamole ohnehin aktiv):

```apache
ProxyPass        /thermo/ http://127.0.0.1:8100/thermo/
ProxyPassReverse /thermo/ http://127.0.0.1:8100/thermo/
RequestHeader set X-Forwarded-Proto "https"
```

Danach `sudo nginx -t && sudo systemctl reload nginx` bzw.
`sudo apachectl configtest && sudo systemctl reload apache2`.

## 4. Funktionstest von außen

```bash
curl -s https://GUAC-HOST/thermo/lti/jwks      # → {"keys":[{"kty":"RSA",…}]}
curl -s https://GUAC-HOST/thermo/api/stats     # → []
```

Wenn beides antwortet, in OPAL den LTI-Baustein anlegen (URLs siehe README:
`…/thermo/lti/login`, `…/thermo/lti/launch13`, `…/thermo/lti/jwks`), die von OPAL
vergebene Client-ID in `.env` eintragen, `sudo systemctl restart thermo-backend`,
und in `docs/assets/js/backend-config.js` die URL `https://GUAC-HOST/thermo`
setzen.

## Updates einspielen

```bash
# neue app.py nach /opt/thermo-backend kopieren, dann:
sudo systemctl restart thermo-backend
```

Die Datenbank (`data/results.db`) und der LTI-Schlüssel (`data/lti_private.pem`)
bleiben dabei unangetastet. Backup = diese zwei Dateien plus `.env` sichern.
