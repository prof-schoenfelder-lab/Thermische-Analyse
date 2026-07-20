#!/usr/bin/env bash
# Deployt Backend + answers.json auf den Guacamole-Server (fing-spool).
# Aufruf vom Repo-Root oder aus backend/:  ./backend/deploy.sh
# Bei reinen Inhalts-Updates (nur answers.json) ist kein Restart nötig.
set -euo pipefail
cd "$(dirname "$0")/.."

HOST=fing-spool.htwk-leipzig.de
DEST=thermo-backend

echo "==> Site bauen (erzeugt answers.json)"
mkdocs build >/dev/null

echo "==> Dateien kopieren"
scp -q backend/app.py backend/requirements.txt answers.json "$HOST:~/$DEST/"

echo "==> Abhängigkeiten aktualisieren (falls nötig)"
ssh "$HOST" "cd ~/$DEST && .venv/bin/pip install -q -r requirements.txt"

echo "==> Fertig. Bei Änderungen an app.py noch ausführen:"
echo "    ssh $HOST 'sudo systemctl restart thermo-backend'"
