# Angewandte FEM in der Thermodynamik

Praktikums-Website des Master-Kurses „Angewandte FEM in der Thermodynamik"
(HTWK Leipzig, Fakultät Ingenieurwissenschaften): Temperaturfeldberechnung
mit der Finite-Elemente-Methode in ANSYS Workbench — stationäre Wärmeleitung,
Abstraktionen & Vernetzung, Randbedingungen & Postprocessing, transiente
Analysen und Wärmestrahlung.

**Live-Site:** https://prof-schoenfelder-lab.github.io/Thermische-Analyse/

## Technik

- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/), Deployment
  automatisch via GitHub Actions bei Push auf `main`
- Aufbau und Werkzeuge (Antwort-Checker, Fortschrittsseite, Abzeichen,
  3D-Startseite) analog zum Schwester-Repo
  [Strukturmechanik](https://github.com/prof-schoenfelder-lab/Strukturmechanik) —
  dort liegt auch die ausführliche `ANLEITUNG.md` zum Betrieb
- Punkteprüfung läuft **serverseitig** über das Backend auf
  `fing-spool.htwk-leipzig.de/thermo/` (nur HTWK-Netz/VPN; eigene Instanz,
  Code in `backend/`). Nach Inhalts-Updates mit neuen Fragen `answers.json`
  aufs Backend kopieren (`backend/deploy.sh`).

## Lokal bauen

```bash
pip install -r requirements.txt
mkdocs serve
```

## Inhalt bearbeiten

Die Seiten liegen unter `docs/`. Übungsfragen wie folgt einbauen:

```html
<div class="numeric-question" data-answer="7.378" data-tolerance="0.1"
     data-points="5" data-attempts="5" data-hints="Hinweis 1|Hinweis 2"></div>
```

Der Ordner `notion-export/` (lokal, nicht im Repo) enthält den
Original-Export der alten Notion-Unterlagen als Referenz.

## Offene Punkte

- **Praktikum 1**: Inhalte fehlen im Notion-Export (nur als Links
  referenziert) — nachexportieren oder neu schreiben
- **Praktikum 2 / Vernetzung**: neuer Abschnitt (Netz-Vertiefung) ausarbeiten
- **Praktikum 3 / Strahlung**: neues Beispiel Cerankochfeld (Surface-to-
  Surface-Strahlung, anisotrope Wärmeleitung) ausarbeiten
- **Übungen**: aus den bisherigen ONYX-Tests in die Kursseiten migrieren
- **OPAL**: LTI-Baustein im neuen Kurs anlegen (Login/Launch-URLs unter
  `/thermo/lti/...`, ClientID `thermische-analyse-fem`, PEM von
  `/thermo/lti/pubkey`) und danach `AC_OPAL_URL` in `backend-config.js`
  eintragen
