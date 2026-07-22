#!/bin/bash
# Doppelklick-Starter (macOS): startet einen lokalen Server im Repo und öffnet
# das Kurs-Studio im Standardbrowser. Für den direkten Ordner-Zugriff (Speichern)
# bitte Chrome oder Edge als Standardbrowser verwenden.
cd "$(dirname "$0")/.." || exit 1
PORT=8765
# Server nur starten, wenn auf dem Port noch nichts antwortet
if ! curl -s "http://localhost:$PORT" >/dev/null 2>&1; then
  echo "Starte lokalen Server auf Port $PORT …"
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  sleep 1
fi
echo "Öffne Kurs-Studio …  (Tutorial-Studio: http://localhost:$PORT/tools/tutorial-studio.html)"
open "http://localhost:$PORT/tools/kurs-studio.html"
