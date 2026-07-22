# content/ — Inhalts-Datenmodell (Quelle der Wahrheit)

Dieser Ordner ist die **Quelle der Wahrheit** für den Kursinhalt. Das
Kurs-Studio liest und schreibt diese JSON-Dateien; der Generator erzeugt
daraus die Markdown-Seiten unter `docs/`, die Übersichtsseiten und den
Nav-Block in `mkdocs.yml` (zwischen `# >>> AUTO-NAV` / `# <<< AUTO-NAV`).

**Nichts hier wird deployt.** Nur `docs/` geht in die Site.

Konflikt-Minimierung (§5b.2 des Plans): **ein Baum-File pro Praktikum**, dazu
eine kleine Top-Datei nur für die Praktika-Reihenfolge.

---

## 1. `content/course.json` — nur Reihenfolge der Praktika

```json
{
  "praktika": ["P1_Einfuehrung", "P2_Geometrie_Randbedingungen",
               "P3_Vernetzung", "P4_Abstraktionen"]
}
```

Die Einträge sind Ordnernamen unter `content/`. Reihenfolge = Reihenfolge in
der Navigation. Praktikum hinzufügen/verschieben berührt nur diese Datei.

---

## 2. `content/<slug>/praktikum.json` — Struktur eines Praktikums

```json
{
  "slug": "P2_Geometrie_Randbedingungen",
  "nav": "GEOMETRIE & RANDBEDINGUNGEN",
  "titel": "Geometrieaufbereitung und Randbedingungen",
  "icon": "material/cube",
  "lernziele": [
    "Grundlegende Methoden zur Veränderung von CAD-Geometrien mit SpaceClaim",
    "Lagerungs- und Belastungsmethoden in ANSYS Mechanical"
  ],
  "sektionen": [
    {
      "titel": "Lagerungen",
      "einheiten": [
        { "typ": "theorie", "id": "einfuehrung-lagerungen" },
        { "typ": "uebung",  "id": "uebung-3" },
        { "typ": "extern",  "pfad": "P2_Geometrie_Randbedingungen/02_Lagerungen/Cylindrical.md",
          "titel": "Zylindrische Lager" }
      ]
    }
  ]
}
```

- `slug` — Ordnername unter `docs/` (Ausgabeziel).
- `nav` — Beschriftung in der oberen Navigationsleiste (Großbuchstaben-Konvention).
- `icon` — Material-Icon der Übersichtsseite.
- `lernziele` — Liste von Inline-Markdown-Strings → Lernziele-Box der Übersicht.
- `sektionen[].titel` — Zwischenüberschrift der Übersicht + Nav-Gruppe.
- `einheiten[]` — geordnete Liste; `typ` ∈ {theorie, uebung, beispiel, extern}.
  - Für generierte Einheiten: `id` → Datei `content/<slug>/<id>.json`.
  - Für `extern` (nicht migrierte Bestandsseite): `pfad` (docs-relativ) + `titel`.

---

## 3. Gemeinsames Block-Modell

Fließinhalt (Theorie-Body, Übungs-Bereiche, Beispiel-Schritte) ist eine Liste
von Blöcken. Inline gilt die Kurs-Syntax: Backticks → Chips/Klick-Pillen/
Tastenkappen, `>` (oder `→`) → Pfeil, `**fett**`/`*kursiv*`.

```json
{ "art": "text",     "md": "Lagerungen verhindern … `Strukturbaum Rechtsklick Mesh > Suppress`" }
{ "art": "bild",     "datei": "images/lager.png", "alt": "…", "breite": 700 }
{ "art": "box",      "typ": "abstract|question|check|tip|warning|info|success",
                     "titel": "…", "blocks": [ …geschachtelte Blöcke… ] }
{ "art": "tutorial", "slug": "festlager-anbringen", "offen": false }
{ "art": "tabelle",  "kopf": ["Größe","Wert"], "zeilen": [["E","210 GPa"], …] }
{ "art": "trenner" }
```

Bilder liegen unter `docs/<slug>/images/` (Studio kopiert sie dorthin).

---

## 4. Einheit `theorie` — `content/<slug>/<id>.json`

```json
{ "typ": "theorie", "titel": "Einführung in Lagerungen",
  "icon": "material/information-variant-box", "blocks": [ …Block-Modell… ] }
```
→ generiert `docs/<slug>/<sektion-ordner>/<id>.md` mit Titel + Blöcken.

---

## 5. Einheit `uebung`

```json
{ "typ": "uebung", "titel": "Übung 3 — Lineal über Kante",
  "gegeben":  [ …blocks… ],
  "gesucht":  [ …blocks… ],
  "hinweise": [ …blocks… ],
  "loesung":  [ …blocks… ],
  "fragen": [
    { "typ": "numerisch", "frage": "Maximale Durchbiegung u_max in mm?",
      "antwort": 7.378, "toleranz": 0.1, "einheit": "mm",
      "punkte": 5, "versuche": 5,
      "hinweise": "Einheit auf mm gewechselt? Kraft -5000 N in z auf der Kante?" },
    { "typ": "mc", "frage": "Welche Lagerung ist statisch bestimmt?",
      "optionen": ["Fest-Fest", "Fest-Los", "Los-Los"], "richtig": [1],
      "punkte": 3, "versuche": 3 }
  ] }
```
→ generiert das bestehende Übungs-Muster: Gegeben/Gesucht/Hinweise (als Box),
Lösung (als aufklappbares `details`), und je Frage das
`div.numeric-question` / `div.multiple-choice-question`-Markup mit
`data-answer`/`data-tolerance`/`data-points`/`data-attempts`/`data-hints`.
`scripts/answers_hook.py` extrahiert die Antworten beim Build unverändert.

---

## 6. Einheit `beispiel` (Vorzeigebeispiel mit Tabs + Stepper)

```json
{ "typ": "beispiel", "titel": "Zweiseitig gelagerter Balken",
  "basisordner": "losung-mit-ansys",
  "tabs": [
    { "label": "Aufgabe",           "seite": "Aufgabenstellung" },
    { "label": "Lösung mit ANSYS",  "seite": "losung-mit-ansys" },
    { "label": "Analytische Lösung","seite": "analytische-loesung" }
  ],
  "aufgabe":    [ …blocks… ],
  "schritte": [
    { "slug": "material", "label": "Material",
      "banner": "Material **E = 210 GPa** anlegen", "blocks": [ …blocks… ] }
  ],
  "analytisch": [ …blocks… ] }
```
→ generiert die Aufgabenseite, die Schrittseiten (`<basisordner>/<slug>.md`)
mit `.task-banner`/`.task-tabs-src`-Markup **und** einen passenden Eintrag in
`docs/assets/wf-groups.json` (Slugs = `""` für die Übersicht + `schritte[].slug`,
Labels = `schritte[].label`, `base` = `basisordner`, `tabs`/`tabsIndex` aus
`tabs`). Der klickbare Stepper und die Varianten-Tabs entstehen daraus.

---

## 7. Generator-Regeln (Kurzfassung)

- Jede generierte `.md` beginnt mit
  `<!-- GENERIERT aus content/<slug>/<id>.json · sha:<checksumme> · Kurs-Studio -->`.
  Weicht der Datei-Inhalt (ohne Kopfzeile) von der Checksumme ab → das Studio
  warnt vor Hand-Änderungen statt stumm zu überschreiben.
- Übersichtsseite je Praktikum: H1 + Lernziele-Box + `prakt-cards`-Raster je
  Sektion (aus den Einheiten; Bilder/Titel automatisch, `extern` inklusive).
- Nav-Block (zwischen den `AUTO-NAV`-Markern in `mkdocs.yml`): je Praktikum ein
  `- <nav>:`-Knoten mit Übersichtsseite + Sektionen + Einheiten in Reihenfolge.
- `extern`-Einheiten werden referenziert, nie verändert.

## 8. Status

Phase 0 (dieses Schema + wf-groups.json-Auslagerung + AUTO-NAV-Marker) ist
umgesetzt. Die content/-Dateien selbst entstehen ab Phase 1 (Studio) bzw. bei
der Migration (Phase 5). Siehe `planning/kurs-studio-plan.md`.
