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
| **Film Coefficient** | Wärmeübergangskoeffizient $\alpha$: wie leicht Wärme zwischen Luft und Wand übergeht, in W/m²·°C (= W/(m²·K)) | 7,7 | 25 |
| **Ambient Temperature** | Lufttemperatur in einigem Abstand von der Wand (nicht die Wandtemperatur) | 20 °C | −10 °C |

Über die Fläche fließt dann so viel Wärme, wie der Temperaturunterschied
zwischen Luft und Wand erlaubt:

$$\dot q = \alpha\,(T_{Luft} - T_{Wand})$$

Die **Wandtemperatur ist jetzt Ergebnis**. Sie stellt sich so ein, dass der
Wärmeübergang an der Oberfläche und die Wärmeleitung durch die Wand zueinander
passen. Innen ist $\alpha$ klein (ruhende Raumluft), außen groß (Wind). Die Werte
entsprechen den Normwerten $R_{si} = 0{,}13$ und $R_{se} = 0{,}04\ \mathrm{m^2K/W}$
nach DIN EN ISO 6946, in denen die Wärmestrahlung schon enthalten ist.

!!! info "Was bedeutet α anschaulich? Umrechnung in Wind"
    Der Normwert setzt sich aus Konvektion und Wärmestrahlung zusammen:
    $\alpha = \alpha_K + \alpha_S$ mit $\alpha_S \approx 5\ \mathrm{W/(m^2K)}$.
    Für die Konvektion außen nennt DIN EN ISO 6946 die Näherung
    $\alpha_K = 4 + 4\,v$ mit der Windgeschwindigkeit $v$ in m/s:

    | Wind außen | $v$ in m/s | $\alpha$ in W/(m²·K) |
    |---|---|---|
    | windstill | 0 | 9 |
    | leiser Zug | 1 | 13 |
    | schwacher Wind (**Normwert außen**) | 4 | 25 |
    | frischer Wind | 10 | 49 |
    | stürmischer Wind | 20 | 89 |

    Innen bewegt sich die Raumluft kaum: Konvektion etwa 2,5 plus Strahlung
    etwa 5,1 ergibt die 7,7 W/(m²·K). Werte gerundet.

## Umsetzung

Material, Geometrie und Netz bleiben gleich. Deshalb bekommt Fall b) eine
**zweite Analyse, die das Modell von Fall a) mitnutzt**. Beide Analysen stehen
dann in **einem** Mechanical, und die Ergebnisse lassen sich direkt
nebeneinanderlegen.

??? tip "Kurzanleitung: Zweite Analyse mit gemeinsamem Modell"
    1. In der Toolbox **Steady-State Thermal** mit gedrückter Maustaste auf die Zelle **Model** der Analyse A ziehen
    2. Die neue Analyse B in **b) Konvektion** umbenennen
    3. `Rechtsklick Setup (B) → Edit...`: Im Strukturbaum stehen jetzt beide Analysen

<tutorial slug="p1-konvektion-anlegen"></tutorial>

??? tip "Kurzanleitung: Konvektion anbringen und vergleichen"
    1. Außenfläche anklicken, `Rechtsklick Steady-State Thermal 2 (B5) → Insert → Convection`
    2. Im `Detailfenster`: **Film Coefficient** **25** W/m²·°C, **Ambient Temperature** **−10** °C
    3. Genauso die Innenfläche: **7,7** W/m²·°C und **20** °C
    4. Die Ergebnisse aus Fall a) übernehmen: unter **Solution (A6)** alle Ergebnisse markieren (`Shift`) und auf **Solution (B6)** ziehen
    5. `Rechtsklick Solution (B6) → Solve`
    6. Vergleich: beide Pfad-Ergebnisse (**Temperature 2** unter A6 und B6) mit `Strg` markieren, der Graph zeigt beide Verläufe

<tutorial slug="p1-konvektion"></tutorial>

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Fall a) | Fall b) |
    |---|---|---|
    | Wärmestromdichte $\dot q$ | 7,18 W/m² | **6,90 W/m²** |
    | Oberflächentemperatur innen | 20,00 °C (vorgegeben) | **19,10 °C** |
    | Temperatur Trennfuge | 18,73 °C | **17,88 °C** |
    | Oberflächentemperatur außen | −10,00 °C (vorgegeben) | **−9,72 °C** |

!!! question "Verständnisfrage"
    Auf die **Innenfläche** werden gleichzeitig beide Randbedingungen gesetzt:
    die **Temperatur 20 °C** aus Fall a) und die **Konvektion**
    $\alpha = 7{,}7\ \mathrm{W/(m^2K)}$ bei 20 °C Luft aus Fall b). Die Außenseite
    bleibt wie in Fall b). Welche Temperatur hat die Innenfläche?

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="2">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="checkbox" id="vfa" name="vf">
      <label for="vfa">20,00 °C</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="checkbox" id="vfb" name="vf">
      <label for="vfb">19,10 °C wie in Fall b)</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="checkbox" id="vfc" name="vf">
      <label for="vfc">ein Wert zwischen 19,10 °C und 20,00 °C</label>
    </div>
    <div class="mc-option" data-value="D">
      <input type="checkbox" id="vfd" name="vf">
      <label for="vfd">ANSYS kann das nicht rechnen</label>
    </div>
  </div>
</div>

??? success "Auflösung"
    **20,00 °C.** Die Temperatur-Randbedingung legt den Wert an den Knoten der
    Fläche fest, daran kann keine andere Randbedingung mehr etwas ändern. Die
    Konvektion wirkt zwar weiter, sie verändert aber nur den Wärmestrom, den
    ANSYS an dieser Fläche zuführen muss, um die 20 °C zu halten. An der
    Innenfläche verhält sich die Wand deshalb wie in Fall a). Merke: Auf eine Fläche gehört entweder
    eine Temperatur **oder** ein Wärmeübergang, nicht beides.

## Ausprobieren: Wie hängt die Wandtemperatur von α ab?

Die Grafik rechnet dieselbe Wand von Hand. Ziehen Sie $\alpha$ innen oder außen
sehr groß: Die Oberfläche nimmt dann die Lufttemperatur an, und es kommt genau
**Fall a)** heraus. Bei kleinem $\alpha$ fällt ein großer Teil der Temperatur schon
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
