---
title: 4 · Netz
---

# 4 · Vernetzung <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Netzgröße global **10 mm** einstellen und vernetzen
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Vernetzung"

## Umsetzung

ANSYS vernetzt mit Standardeinstellungen. Am Anfang geben wir die Netzgröße vor,
in Praktikum 3 geht es dann genauer um ein geeignetes Netz.

??? tip "Kurzanleitung: Globale Netzgröße"
    1. `Strukturbaum Mesh` anklicken
    2. Im `Detailfenster` unter **Defaults** bei **Element Size** **0,01** m eintragen
    3. `Rechtsklick Mesh → Generate Mesh`

<tutorial slug="p1-vernetzung"></tutorial>

!!! info "Warum nur 100 mm breit, aber 10 mm Netz?"
    Die Temperatur ändert sich nur **über die Dicke**, quer dazu nicht. Die
    Breite des Ausschnitts spielt deshalb keine Rolle, und das Netz gehört
    dorthin, wo sich etwas ändert: Mit 10 mm liegen 18 Elemente im
    Kalksandstein und 14 in der Dämmung, die Verläufe werden glatt.
    Weil der Verlauf je Schicht linear ist, wäre das Ergebnis hier sogar mit
    einem Element je Schicht schon exakt. Bei Ecken, Rohren oder
    Wärmebrücken ist das anders (Praktikum 3).
