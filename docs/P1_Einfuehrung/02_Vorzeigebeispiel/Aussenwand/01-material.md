---
title: 1 · Material
---

# 1 · Analyse und Material <small>(Workbench)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Steady-State-Thermal-Analyse anlegen und **Kalksandstein** und **EPS** definieren
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Material"

## Umsetzung

??? tip "Kurzanleitung: Analyse anlegen"
    1. ANSYS Workbench öffnen und das Projekt gleich speichern (`File → Save As...`, [ohne Umlaute im Pfad](../../abspeichern.md))
    2. In der Toolbox links `Doppelklick Steady-State Thermal`
    3. Analyse umbenennen in **a) Temperaturen** (Doppelklick auf den Namen unter dem Analysesystem)

<!-- TUTORIAL: p1-analyse-anlegen (Aufnahme Kapitel 1) -->

??? tip "Kurzanleitung: Material anlegen"
    1. `Doppelklick Engineering Data`
    2. In der leeren Zeile unter den Materialien den Namen **Kalksandstein** eintragen
    3. Aus der Toolbox links `Thermal → Isotropic Thermal Conductivity` auf das neue Material ziehen
    4. Wert **0,99** W m⁻¹ C⁻¹ eintragen
    5. Genauso **EPS** mit **0,035** W m⁻¹ C⁻¹ anlegen
    6. Oben `Project` anklicken, um zurück ins Projektmenü zu kommen

<!-- TUTORIAL: p1-material-anlegen (Aufnahme Kapitel 2) -->

!!! info "Warum nur λ?"
    Für eine **stationäre** Rechnung braucht ANSYS nur die Wärmeleitfähigkeit.
    Dichte und spezifische Wärmekapazität kommen erst bei instationären Rechnungen (in ANSYS: transient)
    (Praktikum 4) dazu.
