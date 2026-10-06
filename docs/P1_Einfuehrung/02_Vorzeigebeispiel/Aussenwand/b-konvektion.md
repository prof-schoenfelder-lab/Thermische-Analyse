---
title: b) Konvektion
---

# b) Konvektion an Raum- und Außenluft

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Temperaturen durch **Konvektion** ersetzen und den **U-Wert** bestimmen
</div>

In Fall a) waren die Oberflächentemperaturen vorgegeben. In Wirklichkeit kennt
man aber die **Lufttemperaturen** innen und außen. Zwischen Luft und Wand
gibt es einen **Wärmeübergang** (Konvektion), der selbst einen Widerstand darstellt.

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Randbedingungen_b"

## Umsetzung

Material, Geometrie und Netz bleiben gleich. Deshalb wird die Analyse aus
Fall a) **dupliziert** und nur die Randbedingungen werden getauscht.

??? tip "Kurzanleitung: Analyse duplizieren"
    1. Im Projektmenü `Rechtsklick` auf den Kopf der Analyse **a) Temperaturen** `→ Duplicate`
    2. Kopie umbenennen in **b) Konvektion**
    3. `Doppelklick Model` der Kopie, Mechanical öffnet sich

??? tip "Kurzanleitung: Konvektion statt Temperatur"
    1. Beide Temperatur-Randbedingungen löschen (`Rechtsklick → Delete`)
    2. Innenfläche anklicken, dann `Reiter Environment → Convection`
    3. Im `Detailfenster`: **Film Coefficient** **7,7** W/m²·°C, **Ambient Temperature** **20** °C
    4. Umbenennen: **Konvektion innen**
    5. Genauso die Außenfläche: **25** W/m²·°C und **−10** °C, Name **Konvektion außen**
    6. `Reiter Home → Solve`, danach `Evaluate All Results`

<!-- TUTORIAL: p1-konvektion (Aufnahme Kapitel 9) -->

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Fall a) | Fall b) |
    |---|---|---|
    | Wärmestromdichte $\dot q$ | 7,18 W/m² | **6,90 W/m²** |
    | Oberflächentemperatur innen | 20,00 °C (vorgegeben) | **19,10 °C** |
    | Temperatur Trennfuge | 18,73 °C | **17,88 °C** |
    | Oberflächentemperatur außen | −10,00 °C (vorgegeben) | **−9,72 °C** |

## U-Wert

Der **Wärmedurchgangskoeffizient** (U-Wert) ist die Wärmestromdichte je Kelvin
Temperaturunterschied zwischen **Raumluft und Außenluft**:

$$U = \frac{\dot q}{T_i - T_e} = \frac{6{,}90\ \mathrm{W/m^2}}{30\ \mathrm{K}} = 0{,}230\ \mathrm{\frac{W}{m^2\,K}}$$

!!! success "Einordnung"
    Das Gebäudeenergiegesetz (GEG) verlangt bei der Erneuerung einer Außenwand
    $U \le 0{,}24\ \mathrm{W/(m^2\,K)}$. Die Wand erfüllt das knapp.

!!! question "Kurz nachdenken"
    Warum ist der Wärmestrom in Fall b) **kleiner** als in Fall a), obwohl innen
    und außen dieselben Temperaturen herrschen?

[Weiter zur analytischen Lösung →](analytische-loesung.md){ .md-button .md-button--primary }
