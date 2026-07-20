#!/usr/bin/env bash
# Kurs-Reset zum Semesterende: sichert die Datenbank und leert danach alle
# Ergebnisse und Nutzer. Die neue Kohorte startet bei null; beim nächsten
# OPAL-Login werden neue Pseudonyme angelegt.
# Aufruf auf dem Server:  ~/thermo-backend/reset-course.sh
set -eu
cd "$(dirname "$0")"

[ -f data/results.db ] || { echo "Keine Datenbank gefunden — nichts zu tun."; exit 0; }

n=$(.venv/bin/python -c "import sqlite3;print(sqlite3.connect('data/results.db').execute('SELECT COUNT(DISTINCT pseudonym) FROM results').fetchone()[0])")
echo "Achtung: Es werden die Ergebnisse von $n Teilnehmenden gelöscht (Backup wird vorher angelegt)."
read -r -p "Kurs wirklich zurücksetzen? [ja/N] " answer
[ "$answer" = "ja" ] || { echo "Abgebrochen."; exit 1; }

mkdir -p backups
ts=$(date +%F-%H%M)
cp data/results.db "backups/results-vor-reset-$ts.db"
.venv/bin/python - <<'PY'
import sqlite3
db = sqlite3.connect('data/results.db')
import secrets
db.execute('DELETE FROM results')
db.execute('DELETE FROM users')
db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('generation', ?)", (secrets.token_urlsafe(8),))
db.commit()
db.execute('VACUUM')
print('Datenbank geleert, neue Kurs-Generation gesetzt.')
print('Browser mit alten Daten raeumen sich beim naechsten Besuch selbst auf.')
PY
echo "Kurs zurückgesetzt. Backup: backups/results-vor-reset-$ts.db"
