---
title: "Übung 2: Balkonplatte als Wärmebrücke"
---

# Übung 2: Balkonplatte als Wärmebrücke

Eine Balkonplatte aus Stahlbeton geht durch die gedämmte Außenwand nach
draußen. Beton leitet die Wärme rund 66-mal besser als die Dämmung: Die Platte
führt Wärme aus dem Haus ab wie die Rippe eines Kühlkörpers
([Praktikum 2, Übung 2](../../P2_Randbedingungen/03_Selbsttests/Uebung-2.md)).
Sie ist eine konstruktive [Wärmebrücke](../01_Grundlagen/Waermebruecken.md).
Wie viel Wärme verliert das Haus durch sie zusätzlich, und was bringt eine
thermische Trennung?

<figure style="text-align:center;">
  <img src="../../images/p3_balkonplatte.excalidraw.png" alt="2D-Schnitt: Außenwand aus Kalksandstein 175 mm und EPS 140 mm, 1000 mm über und unter der Platte geschnitten; Stahlbetonplatte 200 mm dick, kragt 1500 mm aus und reicht 1000 mm in den Raum; in der Dämmebene der Dämmkörper 80 mm für Teil c; außen −5 °C, innen 20 °C" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Kalksandstein: Wärmeleitfähigkeit $\lambda = 0{,}99\ \mathrm{W/(m\,K)}$ (wie in Praktikum 1)
- EPS: $\lambda = 0{,}035\ \mathrm{W/(m\,K)}$ (wie in Praktikum 1)
- Stahlbeton: $\lambda = 2{,}3\ \mathrm{W/(m\,K)}$
- Dämmkörper des Kragplattenanschlusses, nur in c): äquivalente Wärmeleitfähigkeit $\lambda_{eq} = 0{,}15\ \mathrm{W/(m\,K)}$

**Geometrie** (2D-Schnitt mit der Dicke 1000 mm, Maße im Bild)

- Außenwand wie in Praktikum 1: Kalksandstein 175 mm innen, EPS 140 mm außen
- Balkonplatte aus Stahlbeton, 200 mm dick: Sie geht durch die Wand und kragt 1500 mm aus
- Schnitte nach DIN EN ISO 10211 im Abstand 1000 mm: in der Wand über und unter der Platte und in der Platte im Raum
- Dämmkörper 80 mm breit in der Dämmebene, direkt vor dem Kalksandstein (60 bis 140 mm von der Außenfläche der Wand). In a), b) und d) ist er aus Stahlbeton, die Platte geht dann ungetrennt durch die Wand

**Netz**

- Netzgröße global 25 mm (in Mechanical 0,025 m)

**Randbedingungen**

| Wo | Randbedingung | Wert |
|---|---|---|
| Innenflächen: Wand und Platte im Raum | Konvektion | $T_i = 20\ \mathrm{°C}$, $\alpha_i = 7{,}7\ \mathrm{W/(m^2\,K)}$ ($R_{si} = 0{,}13\ \mathrm{m^2\,K/W}$) |
| Außenflächen: Wand und Balkonplatte | Konvektion | $T_e = -5\ \mathrm{°C}$, $\alpha_e = 25\ \mathrm{W/(m^2\,K)}$ ($R_{se} = 0{,}04\ \mathrm{m^2\,K/W}$) |
| die drei Schnitte | keine (adiabat) | |

Vereinfacht gilt innen überall $R_{si} = 0{,}13\ \mathrm{m^2\,K/W}$, auch am
Fußboden und an der Decke. Nach DIN EN ISO 6946 wären es dort 0,17 (Wärmestrom
nach unten) und 0,10 m²·K/W (nach oben).

**Für ψ** (b und c)

- Wärmedurchgangskoeffizient der ungestörten Wand: $U = 0{,}230\ \mathrm{W/(m^2\,K)}$ aus der Handrechnung in [Praktikum 1](../../P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/analytische-loesung.md)
- Länge $l = 2{,}2\ \mathrm{m}$: die Höhe der Wand im Modell, außen gemessen ([Außenmaß](../01_Grundlagen/Waermebruecken.md#langenbezogener-warmedurchgangskoeffizient))

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Sechs Rechtecke, sieben Flächen</p>
    <ul>
      <li>Neue Analyse wie im Vorzeigebeispiel a): vier Materialien anlegen, <strong>Analysis Type</strong> <code>2D</code>, erst dann SpaceClaim öffnen</li>
      <li>Der Ursprung liegt an der Außenfläche der Wand am unteren Schnitt, x zeigt in den Raum, y nach oben</li>
      <li>Rechtecke, Breite × Höhe in mm ab der linken unteren Ecke:<ul><li>EPS 140 × 1000 ab (0, 0) und ab (0, 1200)</li><li>Kalksandstein 175 × 1000 ab (140, 0) und ab (140, 1200)</li><li>Platte 2815 × 200 ab (−1500, 1000)</li><li>Dämmkörper 80 × 200 ab (60, 1000)</li></ul></li>
      <li>Skizze beenden (<code>Pull</code>): Der Dämmkörper teilt die Platte, es entstehen <strong>sieben</strong> Flächen. Share Topology auf <strong>Share</strong> wie im Vorzeigebeispiel</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Dicke und Material für sieben Flächen</p>
    <ul>
      <li>In Mechanical alle sieben Flächen im Strukturbaum markieren (die erste anklicken, die letzte mit <code>Umschalt</code>) und im Detailfenster <strong>Thickness</strong> 1 m eintragen: Das gilt für alle markierten Flächen</li>
      <li>Das Material je Fläche zuweisen, die angeklickte Fläche leuchtet in der Grafik auf. In a), b) und d) bekommt auch der Dämmkörper <strong>Stahlbeton</strong></li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Kanten innen und außen</p>
    <ul>
      <li>Oben <code>Edge</code> wählen und mit <code>Strg</code> die <strong>vier</strong> Kanten zum Raum anklicken: die Wand über und unter der Platte, Ober- und Unterseite der Platte im Raum</li>
      <li><code>Rechtsklick → Create Named Selection</code>, Name <strong>innen</strong></li>
      <li>Genauso die <strong>fünf</strong> Kanten zur Außenluft: die Wand über und unter der Platte, Ober-, Unter- und Stirnseite der Balkonplatte, Name <strong>aussen</strong></li>
      <li>Auf beide Named Selections je eine <code>Convection</code>, die drei Schnitte bekommen keine Randbedingung</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswerten</p>
    <ul>
      <li>Die Konvektion <strong>innen</strong> auf <strong>Solution</strong> ziehen (Reaction Probe): Mit der Dicke 1000 mm ist der Wärmestrom (<strong>Heat</strong>) der Wert je Meter Wand. Die Reaktion an <strong>aussen</strong> ist gleich groß mit umgekehrtem Vorzeichen</li>
      <li>Für c) und d) die Analyse ohne Trennung duplizieren wie im <a href="../../02_Vorzeigebeispiel/Fernwaermerohr/b-halbmodell/">Vorzeigebeispiel b)</a>. In der Kopie nur ändern, was die Frage verlangt</li>
      <li>Tiefste Temperatur innen: <code>Rechtsklick Solution → Insert → Thermal → Temperature</code>, <strong>Scoping Method</strong> <code>Named Selection</code>, <strong>innen</strong>. Im Detailfenster steht dann das <strong>Minimum</strong> der Innenflächen</li>
    </ul>
  </div>

</div>

<!-- Klicktest: Skizze aus sechs Rechtecken (entstehen sieben Flächen?), Thickness und Assignment für mehrere Flächen auf einmal, Reaction Probe der Konvektion innen (Vorzeichen), Temperatur auf der Named Selection innen mit Minimum; Sollwerte aus tools/sollwerte/p3_balkonplatte.py, durch die ANSYS-Werte ersetzen -->

## Gesucht

### a) Ohne Trennung: Wärmestrom an den Innenflächen in W/m

<div class="numeric-question" data-answer="35.86" data-tolerance="0.7" data-points="5" data-attempts="5" data-hints="Reaction Probe der Konvektion innen ablesen; Vier Kanten in innen, fünf Kanten in aussen, die Schnitte ohne Randbedingung?; Dämmkörper in a) aus Stahlbeton?; Dicke 1000 mm bei allen sieben Flächen?">
</div>

### b) Ohne Trennung: längenbezogener Wärmedurchgangskoeffizient $\psi_e$ in W/(m·K)

$\psi_e$ ist der Zuschlag der Wärmebrücke zur ungestörten Wand (siehe
[Wärmebrücken](../01_Grundlagen/Waermebruecken.md#langenbezogener-warmedurchgangskoeffizient)):

$$
\psi_e = \frac{\dot Q'}{T_i - T_e} - U\,l
$$

mit

- $\psi_e$: längenbezogener Wärmedurchgangskoeffizient, Längen außen gemessen, in W/(m·K)
- $\dot Q'$: Wärmestrom an den Innenflächen aus a) in W/m
- $T_i$, $T_e$: Lufttemperatur innen und außen in °C
- $U$: Wärmedurchgangskoeffizient der ungestörten Wand in W/(m²·K)
- $l$: Höhe der Wand im Modell, außen gemessen, in m

<div class="numeric-question" data-answer="0.928" data-tolerance="0.03" data-points="5" data-attempts="5" data-hints="Temperaturdifferenz 20 °C − (−5 °C) = 25 K; Wärmestrom aus a) durch 25 K teilen; Davon U · l = 0,230 · 2,2 abziehen">
</div>

### c) Mit Trennung: $\psi_e$ in W/(m·K)

Bei einer thermischen Trennung trägt ein **Kragplattenanschluss** die Platte:
Stahlstäbe führen durch einen Dämmkörper, der den Beton in der Dämmebene
ersetzt. Im Modell wird er ein
[Ersatzmaterial](../01_Grundlagen/Abstraktionen.md#ersatzmaterial): Nur der
Dämmkörper bekommt $\lambda_{eq} = 0{,}15\ \mathrm{W/(m\,K)}$, alles andere
bleibt wie in a).

<div class="numeric-question" data-answer="0.234" data-tolerance="0.02" data-points="5" data-attempts="5" data-hints="In der Kopie nur dem Dämmkörper das neue Material zuweisen; Wärmestrom an den Innenflächen neu ablesen; ψ_e wie in b), U und l bleiben gleich">
</div>

### d) Optional: tiefste Temperatur der Innenoberfläche $T_{si}$ ohne Trennung in °C

Wie in [Praktikum 1, Übung 2](../../P1_Einfuehrung/03_Selbsttests/Uebung-2.md)
prüft DIN 4108-2 den Mindestwärmeschutz an der kältesten Stelle innen, mit
$R_{si} = 0{,}25\ \mathrm{m^2\,K/W}$, also innen
$\alpha_i = 4\ \mathrm{W/(m^2\,K)}$:

$$
f_{Rsi} = \frac{T_{si} - T_e}{T_i - T_e} \ge 0{,}70
$$

mit

- $f_{Rsi}$: Temperaturfaktor (1 = so warm wie die Raumluft, 0 = so kalt wie draußen)
- $T_{si}$: tiefste Temperatur der Innenoberfläche in °C
- $T_i$, $T_e$: Lufttemperatur innen und außen in °C

<div class="numeric-question" data-answer="13.67" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Kopie der Analyse ohne Trennung, bei der Konvektion innen 4 statt 7,7; Temperatur nur auf der Named Selection innen auswerten, das Minimum ablesen; Die kälteste Stelle liegt in der Ecke zwischen Wand und Platte">
</div>

### d) Optional: Temperaturfaktor $f_{Rsi}$ ohne Trennung

<div class="numeric-question" data-answer="0.747" data-tolerance="0.007" data-points="5" data-attempts="5" data-hints="Zähler: T_si − (−5 °C) = T_si + 5 K; Nenner: 20 °C − (−5 °C) = 25 K">
</div>

<div class="solution-images" markdown="1">

### Lösung

- a) Ohne Trennung fließen **35,9 W/m** durch die Innenflächen. Die ungestörte Wand derselben Höhe verliert 0,230 · 2,2 · 25 = 12,7 W/m: Mit der Platte ist es fast dreimal so viel
- b) $\psi_e$ = 35,86/25 − 0,230 · 2,2 = 1,434 − 0,506 = **0,93 W/(m·K)**. Ein 5 m breiter Balkon verliert damit zusätzlich 0,93 · 5 · 25 = 116 W, so viel wie rund 20 m² der ungestörten Wand
- c) Mit Trennung sind es 18,5 W/m und $\psi_e$ = **0,23 W/(m·K)**, 75 % weniger. Der Dämmkörper ist nur 80 mm breit, unterbricht aber den Beton, über den ohne Trennung die meiste Wärme abfließt
- Wie viel die Trennung bringt, hängt von den Stahlstäben ab: Je nach Tragstufe gibt ein Hersteller für diese Plattendicke $\lambda_{eq}$ = 0,08 bis 0,26 W/(m·K) an, $\psi_e$ liegt dann zwischen 0,12 und 0,36 W/(m·K)
- Das Ersatzmaterial kennt die einzelnen Stäbe nicht, nur ihre Wirkung im Mittel. Wenn der Wärmestrom gesucht ist, reicht das. Die Temperatur direkt an einem Stab zeigt es nicht
- d) Die kälteste Stelle liegt in der Ecke zwischen Wand und Platte: $T_{si}$ = **13,7 °C**, $f_{Rsi}$ = (13,67 + 5)/25 = **0,75**. Ohne Trennung ist der Mindestwärmeschutz damit nur **knapp** erfüllt, mit Trennung deutlich (17,6 °C, $f_{Rsi}$ = 0,90)
- Mit $R_{si}$ = 0,13 aus a) ist dieselbe Ecke 15,3 °C warm. Der größere Widerstand nach DIN 4108-2 macht die Oberfläche kälter, die Prüfung liegt damit auf der sicheren Seite
- Mit $R_{si}$ = 0,13 an allen Innenflächen ist das Modell spiegelbildlich zur Mittelebene der Platte, ein Halbmodell wäre also erlaubt. Mit den Normwerten 0,17 am Fußboden und 0,10 an der Decke gilt das nicht mehr

</div>

<!-- Nach dem Merge von Wandschnitt 2D (TD-21): in der Lösung die Gegenprobe mit der Vorlage Balkonplatte verlinken (ψ_e 0,93 ohne, 0,23 mit Trennung) -->
