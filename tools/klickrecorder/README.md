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
python3 aufnahme2tutorial.py aufnahmen/2026-10-07_1030_P1_Aussenwand --kategorie Setup
```

Je Kapitel entsteht `aufnahmen/.../tutorial/<slug>-kN/` mit `tutorial.json`,
`step-N.png` (Ausschnitt mit nummerierten Markern) und `entwurf.md`.
Schritte mit `[PRÜFEN]` brauchen Nacharbeit (Klick ins Grafikfenster, Feld ohne Namen,
Ergebnisfoto). Fertige Ordner nach `docs/tutorials/` kopieren, dann
`python3 scripts/reindex_tutorials.py`.

## Was erfasst wird

- Klick, Doppelklick, Rechtsklick, Ziehen (mittlere Taste = Drehen)
- Name und Typ des Elements unter der Maus (Windows UI Automation), Fenstertitel
- Bildschirmfoto des Monitors unter der Maus im Moment des Drückens

Zusammengefasst wird: `Rechtsklick X → Insert → Y` (ein Bild, Marker 1 bis 3) und
`Reiter Environment → Temperature`.

## Virenscanner (Sophos)

Tools, die Tastatur und Bildschirm mitschneiden, sehen für Sophos wie Keylogger aus.
Deshalb:
- **keine Tastatur-Aufzeichnung**: eingetippte Werte fehlen in der Aufnahme und kommen beim
  Nacharbeiten aus der Aufgabenstellung (Schritt „Wert eingeben [PRÜFEN]")
- **keine Hooks**: Maustasten werden abgefragt, die vier Kürzel sind normale Windows-Hotkeys
- **Foto nur beim Klick**, kein Dauermitschnitt

Schlägt Sophos trotzdem an: Meldung notieren (welche Regel, welcher Prozess) und eine
Ausnahme für den Ordner bei der IT anfragen. Ausweichlösung ohne eigenes Tool ist die
Windows-Schrittaufzeichnung (`psr.exe`, von Microsoft signiert), sofern auf dem Rechner vorhanden.
