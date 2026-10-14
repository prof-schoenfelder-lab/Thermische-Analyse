---
title: "Übung 2: Außenecke"
---

# Übung 2: Außenecke

Die Wand aus dem Vorzeigebeispiel bildet jetzt eine **Gebäudeecke**. Für die
ebene Wand gibt es eine Handrechnung, für die Ecke nicht: Innen steht dort
wenig warme Fläche einer großen kalten Außenfläche gegenüber. Die Ecke ist eine
**geometrische Wärmebrücke**. Wie kalt wird sie, und droht dort Schimmel?

<figure style="text-align:center;">
  <img src="../../images/p1_uebung2.svg" alt="Außenecke in der Draufsicht" class="no-lightbox">
</figure>

!!! info "Schimmelnachweis kurz erklärt"
    - Raumluft enthält Wasserdampf. Kühlt sie an einer kalten Wand ab, steigt
      dort die **relative Luftfeuchte**.
    - Ab etwa **80 %** relativer Feuchte an der Oberfläche kann Schimmel wachsen,
      auch ohne sichtbares Tauwasser.
    - Bei normaler Raumluft (20 °C, 50 % Feuchte) ist das bei einer
      Oberflächentemperatur von etwa **12,6 °C** erreicht. Die kälteste Stelle
      innen muss also wärmer sein.
    - DIN 4108-2 prüft das mit dem **Temperaturfaktor**: Er sagt, welcher Anteil
      des Temperaturunterschieds innen an der Oberfläche noch ankommt
      (1 = so warm wie die Raumluft, 0 = so kalt wie draußen):

        $$f_{Rsi} = \frac{T_{si} - T_e}{T_i - T_e} \ge 0{,}70$$

      $T_i$ und $T_e$ sind die **Lufttemperaturen** innen (Raum) und außen,
      $T_{si}$ ist die Temperatur der **Wandoberfläche** innen (s für surface).

    - Bei 20 °C innen und −5 °C außen heißt das: $T_{si} \ge 12{,}5\ \mathrm{°C}$.

    In den Normen heißen Temperaturen in °C $\theta$ statt $T$.

## Gegeben

- Wandaufbau wie im Vorzeigebeispiel: Kalksandstein 175 mm innen, EPS 140 mm außen
- Beide Schenkel **1000 mm** lang (außen gemessen), Höhe des Ausschnitts **100 mm**
- Netzgröße global **20 mm**
- Randbedingungen für den **Mindestwärmeschutz nach DIN 4108-2**:
    - innen: Raumluft $T_i = 20\ \mathrm{°C}$, $\alpha_i = 4\ \mathrm{W/(m^2K)}$ (entspricht $R_{si} = 0{,}25\ \mathrm{m^2K/W}$)
    - außen: Außenluft $T_e = -5\ \mathrm{°C}$, $\alpha_e = 25\ \mathrm{W/(m^2K)}$
    - Schnittenden der Schenkel, Ober- und Unterseite: adiabat (keine Randbedingung)

!!! info "Warum andere Randbedingungen als im Vorzeigebeispiel?"
    Für den Nachweis gegen Schimmel rechnet man innen mit einem kleineren
    Wärmeübergang ($R_{si} = 0{,}25$ statt $0{,}13$): In Ecken und hinter Möbeln
    zirkuliert die Raumluft schlechter. Die Außentemperatur ist auf −5 °C
    festgelegt.

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Vier Rechtecke in der Draufsicht</p>
    <p>Jedes Rechteck an einer Ecke des vorigen ansetzen (Fangpunkt), Maße mit <code>Tab</code>:
    EPS 1000 × 140, EPS 140 × 860, Kalksandstein 860 × 175, Kalksandstein 175 × 685</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Körper erzeugen</p>
    <p>Die beiden EPS-Flächen mit <code>Pull</code> 100 mm hochziehen, dann die Kalksandstein-Flächen mit <code>No merge</code>. <code>Reiter Workbench → Share</code></p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Material und Randbedingungen</p>
    <p>Jedem Körper das richtige Material zuweisen. Die beiden Außenflächen und die beiden Innenflächen jeweils gemeinsam auswählen (<code>Strg</code> gedrückt halten) und je eine <code>Convection</code> anbringen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswerten</p>
    <p>Temperatur auf den Innenflächen auswerten. Das Minimum liegt an der Innenkante der Ecke</p>
  </div>

</div>

<!-- TODO: Datei P1_Aussenecke.scdoc als Download ablegen; Hinweise zu den Fangpunkten mit SpaceClaim 2025 R2 prüfen -->

## Gesucht

### Oberflächentemperatur innen in der Ecke $T_{si}$ in °C

<div class="numeric-question" data-answer="17.39" data-tolerance="0.1" data-points="5" data-attempts="5" data-hints="Minimum der Temperatur auf den Innenflächen. Innen α = 4 und 20 °C, außen α = 25 und −5 °C? Alle vier Körper mit Material und Share Topology?">
</div>

### Temperaturfaktor $f_{Rsi} = \dfrac{T_{si} - T_e}{T_i - T_e}$ in der Ecke

<div class="numeric-question" data-answer="0.896" data-tolerance="0.005" data-points="5" data-attempts="5" data-hints="T_i = 20 °C, T_e = −5 °C, also durch 25 K teilen.">
</div>

### Erfüllt die Ecke den Mindestwärmeschutz ($f_{Rsi} \ge 0{,}70$)?

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="2">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="checkbox" id="u2a" name="u2">
      <label for="u2a">Ja, deutlich</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="checkbox" id="u2b" name="u2">
      <label for="u2b">Nur knapp</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="checkbox" id="u2c" name="u2">
      <label for="u2c">Nein</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Ebene Wand mit denselben Randbedingungen (Handrechnung): $T_{si} = 18{,}60\ \mathrm{°C}$
- Ecke (FEM): $T_{si} = 17{,}39\ \mathrm{°C}$, also **1,2 K kälter** als die ebene Wand
- $f_{Rsi} = (17{,}39 + 5)/25 = 0{,}896 \ge 0{,}70$: Mit 14 cm Dämmung ist die Ecke unkritisch. Bei einem ungedämmten Altbau sieht das anders aus (gern ausprobieren)
- Die Störung durch die Ecke reicht weit: Am Ende der 1 m langen Schenkel liegt die Innenoberfläche noch 0,1 K unter dem Wert der ebenen Wand, weil der Kalksandstein die Wärme gut entlang der Wand leitet

</div>
