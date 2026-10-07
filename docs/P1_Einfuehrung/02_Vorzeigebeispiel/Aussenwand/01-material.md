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

<tutorial slug="p1-analyse-anlegen"></tutorial>

??? tip "Kurzanleitung: Material anlegen"
    1. `Doppelklick Engineering Data`
    2. Structural Steel wird nicht gebraucht: `Rechtsklick Structural Steel → Delete`
    3. In die leere Zeile **Kalksandstein** eintragen
    4. In der Toolbox links **Thermal** aufklappen, `Doppelklick Isotropic Thermal Conductivity`
    5. Wert **0,99** W m⁻¹ C⁻¹ eintragen
    6. Genauso **EPS** mit **0,035** W m⁻¹ C⁻¹ anlegen
    7. Oben `Project` anklicken, um zurück ins Projektmenü zu kommen

<tutorial slug="p1-material-anlegen"></tutorial>

!!! info "Warum nur λ?"
    Für eine **stationäre** Rechnung braucht ANSYS nur die Wärmeleitfähigkeit.
    Dichte und spezifische Wärmekapazität kommen erst bei instationären Rechnungen (in ANSYS: transient)
    (Praktikum 4) dazu.
