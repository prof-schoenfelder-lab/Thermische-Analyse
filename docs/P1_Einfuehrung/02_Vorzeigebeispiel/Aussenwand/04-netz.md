---
title: 4 · Netz
---

# 4 · Vernetzung <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Netzgröße global **50 mm** einstellen und vernetzen
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Vernetzung"

## Umsetzung

ANSYS vernetzt mit Standardeinstellungen. Am Anfang geben wir die Netzgröße vor,
in Praktikum 3 geht es dann genauer um ein geeignetes Netz.

??? tip "Kurzanleitung: Globale Netzgröße"
    1. `Strukturbaum Mesh` anklicken
    2. Im `Detailfenster` unter **Defaults** bei **Element Size** **0,05** m eintragen
    3. `Rechtsklick Mesh → Generate Mesh`

<!-- TUTORIAL: p1-vernetzung (Aufnahme Kapitel 5) -->

!!! info "Reicht so ein grobes Netz?"
    Hier ja: Die Temperatur ändert sich in jeder Schicht **linear**. Das kann
    schon ein einziges Element pro Schicht exakt abbilden. Bei echten
    Bauteilen mit Ecken, Rohren oder Wärmebrücken ist das anders.

[Weiter zu Schritt 5: Randbedingungen →](05-randbedingungen.md){ .md-button .md-button--primary }
