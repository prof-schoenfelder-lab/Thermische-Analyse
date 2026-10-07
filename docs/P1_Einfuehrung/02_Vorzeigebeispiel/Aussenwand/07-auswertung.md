---
title: 7 · Auswertung
---

# 7 · Auswertung <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** **Temperatur**, **Wärmestromdichte** und **Temperatur in der Trennfuge** auswerten
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Gesucht"

## Umsetzung

Vor der Auswertung überlegen: **Was** (Temperatur, Wärmestromdichte) wird
**wo** (ganzes Modell, Fläche, Pfad) und **wie** (Farbbild, Min/Max, Tabelle)
gebraucht?

??? tip "Kurzanleitung: Temperatur und Wärmestromdichte im ganzen Modell"
    1. `Rechtsklick Solution → Insert → Thermal → Temperature`
    2. `Rechtsklick Solution → Insert → Thermal → Total Heat Flux`
    3. `Rechtsklick Solution → Evaluate All Results`
    4. Ergebnis anklicken: Farbbild im Grafikfenster, Min und Max in der Legende

??? tip "Kurzanleitung: Temperaturverlauf über die Wanddicke (Pfad)"
    1. Oben `Edge` anklicken (Kanten auswählen)
    2. Eine Kante quer durch den Kalksandstein anklicken, mit gedrückter `Strg` die anschließende Kante durch die Dämmung dazunehmen
    3. `Rechtsklick Solution → Insert → Thermal → Temperature`
    4. `Rechtsklick Temperature 2 → Convert To Path Result`
    5. `Rechtsklick Temperature 2 → Retrieve This Result`
    6. Im Fenster **Graph** erscheint der Verlauf von innen nach außen, daneben die Werte als Tabelle

<tutorial slug="p1-auswertung"></tutorial>

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Wert |
    |---|---|
    | Wärmestromdichte $\dot q$ (überall gleich) | 7,18 W/m² |
    | Temperatur Trennfuge (Knick im Pfad) | 18,73 °C |

    Die Wärmestromdichte ist im ganzen Modell **gleich groß**: Was innen
    hineinfließt, muss außen wieder hinaus (stationär, keine Wärmequellen).

!!! question "Kurz nachdenken"
    Die Trennfuge liegt bei **18,7 °C**, also fast bei der Innentemperatur.
    Fast der gesamte Temperaturabfall (rund 29 von 30 K) passiert in der
    Dämmung. Warum? Vergleich mit der [analytischen Lösung](analytische-loesung.md).
