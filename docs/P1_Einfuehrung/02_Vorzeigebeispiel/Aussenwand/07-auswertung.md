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

??? tip "Kurzanleitung: Temperatur in der Trennfuge"
    1. Mit dem **Flächenauswahltool** die Trennfuge anklicken (dafür die Dämmung
       ausblenden: `Rechtsklick EPS → Hide Body`)
    2. `Rechtsklick Solution → Insert → Thermal → Temperature`, die Fläche ist
       dann schon als **Scope** eingetragen
    3. `Rechtsklick Temperature → Rename`: **Temperatur Trennfuge**
    4. `Evaluate All Results`, Wert im `Detailfenster` unter **Results** ablesen

<!-- TUTORIAL: p1-auswertung (Aufnahme Kapitel 8) -->
<!-- TODO: Pfad über die Wanddicke ergänzen (Construction Geometry → Path), Verlauf als Diagramm -->

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Wert |
    |---|---|
    | Wärmestromdichte $\dot q$ (überall gleich) | 7,18 W/m² |
    | Temperatur Trennfuge | 18,73 °C |

    Die Wärmestromdichte ist im ganzen Modell **gleich groß**: Was innen
    hineinfließt, muss außen wieder hinaus (stationär, keine Wärmequellen).

!!! question "Kurz nachdenken"
    Die Trennfuge liegt bei **18,7 °C**, also fast bei der Innentemperatur.
    Fast der gesamte Temperaturabfall (rund 29 von 30 K) passiert in der
    Dämmung. Warum? Vergleich mit der [analytischen Lösung](analytische-loesung.md).
