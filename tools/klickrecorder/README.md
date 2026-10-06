# Klickrecorder

Nimmt Klickfolgen in ANSYS (Workbench, SpaceClaim, Mechanical) auf und baut
daraus Klickanleitungen für die Tutorial-Datenbank (`docs/tutorials/<slug>/`).
Ersetzt FolgeMe.

## Aufnehmen (Windows-Rechner mit ANSYS)

1. Einmalig `uv` installieren (ohne Adminrechte):
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. `start_klickrecorder.bat` doppelklicken, Namen eingeben (z.B. `P1_Aussenwand`).
   Beim ersten Start lädt uv die Pakete (mss, Pillow, uiautomation).
3. In ANSYS ganz normal arbeiten. Das Konsolenfenster zeigt jeden erkannten Schritt.

| Tasten | Wirkung |
|---|---|
| `Strg + Alt + F` | Foto ohne Klick (z.B. Ergebnisbild) |
| `Strg + Alt + K` | neues Kapitel, je Kapitel eine Anleitung (z.B. Material, Geometrie, Netz) |
| `Strg + Alt + Z` | letzten Klick verwerfen (mehrfach drücken: weiter zurück) |
| `Strg + Alt + P` | Pause und weiter (Umwege, Passwörter) |
| `Strg + Alt + S` | Aufnahme beenden und speichern |

Ergebnis: `aufnahmen/<Datum>_<Name>/` mit `events.json` und `frames/*.png`.

Tipps
- Per Remote Desktop vom Mac: den Recorder **im Windows-Rechner** starten (nur dort gibt es
  Elementnamen). Kürzel mit `ctrl + option` drücken. RDP-Fenster nicht minimieren, sonst
  werden die Fotos schwarz
- Ruhig klicken: über Menüeinträgen mit Untermenü kurz verweilen (wird als Zwischenschritt erkannt)
- Ein Kapitel pro Arbeitsschritt (7 Schritte des Workflows) ergibt kurze Anleitungen

## Anleitung bauen (Mac oder Windows)

```bash
python3 aufnahme2tutorial.py aufnahmen/2026-10-07_1030_P1_Aussenwand --kategorie Setup --gif
```

Je Kapitel entsteht `aufnahmen/.../tutorial/<slug>-kN/` mit `tutorial.json`,
`step-N.png` (Ausschnitt mit nummerierten Markern) und `entwurf.md`.
Schritte mit `[PRÜFEN]` brauchen Nacharbeit (Klick ins Grafikfenster, Feld ohne Namen,
Ergebnisfoto). Fertige Ordner nach `docs/tutorials/` kopieren, dann
`python3 scripts/reindex_tutorials.py`.

## Was erfasst wird

- Klick, Doppelklick, Rechtsklick, Ziehen mit Ablageziel (mittlere Taste = Drehen,
  mit `Strg` Verschieben, mit `Shift` Zoomen)
- Steuertasten `Strg`, `Shift`, `Alt` (gehalten beim Klick), `Leertaste`, `Tab`, `Enter`,
  `Esc`, `Entf`, `F2`; **keine Buchstaben und Ziffern**
- Name und Typ des Elements unter der Maus (Windows UI Automation), Fenstertitel
- Bildschirmfoto beim Drücken, beim Loslassen nach dem Ziehen und bei `Leertaste`,
  `Tab` und `Enter` (das Foto bei `Enter` zeigt den eingetippten Wert)
- **Eingegebene Werte** (Längen in SpaceClaim, Werte im Detailfenster, neue Namen): bei
  `Enter`/`Tab` wird der Inhalt des aktiven Feldes über UI Automation gelesen, 0,3 s später
  der übernommene Wert mit Einheit und die Zeilenbeschriftung im Detailfenster.
  Passwortfelder werden nie gelesen
- Fenster unter der Maus: Im Bild bleibt nur die aktive Anwendung samt offenen Menüs,
  alles andere wird ausgegraut

Maus und Tasten laufen durch **eine** Abfrageschleife mit einer Uhr: Die Reihenfolge
stimmt auch bei schnellen Folgen wie in SpaceClaim „Pull ziehen, `Leertaste`, Maß
tippen, `Enter`".

Zusammengefasst wird:
- `Rechtsklick X → Insert → Y` (ein Bild, Marker 1 bis 3), `Reiter Environment → Temperature`
- Klick ins Feld, Wert tippen, `Enter`: ein Schritt, Bild zeigt den Wert
- Ziehen mit `Leertaste` und Maßeingabe: ein Schritt, Bild nach der Eingabe
- `F2`, Namen tippen, `Enter`: ein Schritt
- Kam ein Foto erst nach dem Loslassen (Menü schon zu), steht der Schritt auf `[PRÜFEN]`
- Rechtsklick und dann `Esc` (Menü abgebrochen) ergibt keinen Schritt, verworfene Klicks
  (`Strg + Alt + Z`) fallen weg; übrige Fehlklicks beim Nacharbeiten in `entwurf.md` streichen

Mit `--gif` entsteht je Kapitel zusätzlich `ablauf.gif`: alle Fotos des Kapitels mit
gleichem Ausschnitt, Markern und Zähler „3 / 9" (gut für Abläufe wie die Geometrieerstellung).

## Virenscanner (Sophos)

Tools, die Tastatur und Bildschirm mitschneiden, sehen für Sophos wie Keylogger aus.
Deshalb:
- **kein Text-Mitschnitt**: nur die oben genannten Steuertasten, keine Buchstaben und
  Ziffern; Werte werden erst beim Bestätigen aus dem Feld gelesen (wie ein Screenreader)
- **keine Hooks**: Maus und Steuertasten werden abgefragt, die vier Kürzel sind normale
  Windows-Hotkeys
- Schlägt Sophos wegen der Tastenabfrage an: `uv run klickrecorder.py <Name> --ohne-tasten`
  fragt nur die Maus ab
- **Foto nur beim Klick**, kein Dauermitschnitt

Schlägt Sophos trotzdem an: Meldung notieren (welche Regel, welcher Prozess) und eine
Ausnahme für den Ordner bei der IT anfragen. Ausweichlösung ohne eigenes Tool ist die
Windows-Schrittaufzeichnung (`psr.exe`, von Microsoft signiert), sofern auf dem Rechner vorhanden.
