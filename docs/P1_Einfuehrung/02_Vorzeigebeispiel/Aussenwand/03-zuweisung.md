---
title: 3 · Zuweisung
---

# 3 · Materialzuweisung <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Mechanical öffnen, Einheiten auf **m und °C**, Materialien den Körpern zuweisen
</div>

## Umsetzung

??? tip "Kurzanleitung: Mechanical öffnen und Einheiten einstellen"
    1. Im Projektmenü `Rechtsklick Model → Edit...`, Mechanical öffnet sich
    2. Unten rechts in der Statusleiste das Einheitensystem **Metric (m, kg, N, s, V, A)** wählen, Temperatur in **Celsius**

??? tip "Kurzanleitung: Material zuweisen"
    1. `Strukturbaum Geometry` und **SYS** aufklappen
    2. Körper **Kalksandstein** anklicken
    3. Im `Detailfenster` bei **Assignment** auf den Pfeil klicken und **Kalksandstein** wählen
    4. Für den Körper **EPS** genauso das Material **EPS** wählen

<tutorial slug="p1-material-zuweisen"></tutorial>

!!! check "Checkpoint"
    - Unter `Geometry` stehen zwei Körper, beide mit grünem Haken
    - Unter `Connections` gibt es **keine** Kontakte (dank Share Topology). Steht
      dort doch ein Kontakt, wurde in SpaceClaim nicht *Share* ausgeführt.
