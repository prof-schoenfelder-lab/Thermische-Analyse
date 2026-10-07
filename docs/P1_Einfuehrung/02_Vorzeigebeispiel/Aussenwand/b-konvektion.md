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

## Was gibt man bei der Konvektion ein?

Bei der Konvektion gibt man **keine Wandtemperatur** vor, sondern zwei andere
Größen. So heißen sie in ANSYS:

| Feld in ANSYS | Bedeutung | innen | außen |
|---|---|---|---|
| **Film Coefficient** | Wärmeübergangskoeffizient $h$: wie leicht Wärme zwischen Luft und Wand übergeht, in W/m²·°C (= W/(m²·K)) | 7,7 | 25 |
| **Ambient Temperature** | Lufttemperatur in einigem Abstand von der Wand (nicht die Wandtemperatur) | 20 °C | −10 °C |

Über die Fläche fließt dann so viel Wärme, wie der Temperaturunterschied
zwischen Luft und Wand erlaubt:

$$\dot q = h\,(T_{Luft} - T_{Wand})$$

Die **Wandtemperatur ist jetzt Ergebnis**. Sie stellt sich so ein, dass der
Wärmeübergang an der Oberfläche und die Wärmeleitung durch die Wand zueinander
passen. Innen ist $h$ klein (ruhende Raumluft), außen groß (Wind). Die Werte
entsprechen den Normwerten $R_{si} = 0{,}13$ und $R_{se} = 0{,}04\ \mathrm{m^2K/W}$
nach DIN EN ISO 6946, in denen die Wärmestrahlung schon enthalten ist.

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

## Ausprobieren: Wie hängt die Wandtemperatur von h ab?

Die Grafik rechnet dieselbe Wand von Hand. Ziehen Sie $h$ innen oder außen
sehr groß: Die Oberfläche nimmt dann die Lufttemperatur an, und es kommt genau
**Fall a)** heraus. Bei kleinem $h$ fällt ein großer Teil der Temperatur schon
vor der Wand in der Luftschicht ab.

<div class="wand-rechner"></div>

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
