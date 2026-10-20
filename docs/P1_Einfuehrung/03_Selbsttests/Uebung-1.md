---
title: "Übung 1: Altbau sanieren"
---

# Übung 1: Altbau sanieren

Ein Gründerzeithaus hat eine **36,5 cm** dicke Wand aus Vollziegel. Sie wird
außen mit **14 cm** EPS gedämmt. Nach dem Gebäudeenergiegesetz (GEG) darf die
sanierte Außenwand höchstens $U = 0{,}24\ \mathrm{W/(m^2\,K)}$ haben. Reicht das?

Diese Übung wiederholt den Ablauf aus dem Vorzeigebeispiel **Schritt für
Schritt**, nur mit anderen Zahlen: zwei Körper, Konvektion innen und außen. Jedes
Ergebnis lässt sich von Hand prüfen.

<figure style="text-align:center;">
  <img src="../../images/p1_uebung1.svg" alt="Vollziegelwand mit 140 mm Dämmung" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Vollziegel: $\lambda = 0{,}68\ \mathrm{W/(m\,K)}$
- EPS: $\lambda = 0{,}035\ \mathrm{W/(m\,K)}$

**Geometrie**

- Wandausschnitt 100 mm × 100 mm
- Vollziegel innen **365 mm**, EPS außen **140 mm**

**Netz**

- Netzgröße global **10 mm**

**Randbedingungen** (wie im Vorzeigebeispiel **Fall b) Konvektion**)

- innen: Raumluft $T_i = 20\ \mathrm{°C}$, $\alpha_i = 7{,}7\ \mathrm{W/(m^2\,K)}$
- außen: Außenluft $T_e = -10\ \mathrm{°C}$, $\alpha_e = 25\ \mathrm{W/(m^2\,K)}$

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wie im Vorzeigebeispiel</p>
    <p>Neues Projekt, Material <strong>Vollziegel</strong> statt Kalksandstein anlegen, Wand aus zwei Körpern (365 mm und 140 mm, <code>No merge</code>, <code>Share</code>), Material zuweisen, vernetzen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Konvektion und auswerten</p>
    <p>Innen und außen je eine <code>Convection</code> wie in Fall b), lösen, Temperatur und Wärmestromdichte auswerten</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">U-Wert ausrechnen</p>
    <p>Der U-Wert (Wärmedurchgangskoeffizient) ist die Wärmestromdichte je Kelvin Temperaturunterschied zwischen <strong>Raumluft und Außenluft</strong>: \(U = \dot q / (T_i - T_e)\). Hier also die Wärmestromdichte aus ANSYS durch 30 K teilen. Je kleiner U, desto besser dämmt die Wand (<a href="../../02_Vorzeigebeispiel/Aussenwand/b-konvektion/#u-wert">U-Wert im Vorzeigebeispiel</a>)</p>
  </div>

</div>

## Gesucht

### Wärmestromdichte durch die sanierte Wand in W/m²

<div class="numeric-question" data-answer="6.37" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Zwei Körper mit Share Topology? Vollziegel 365 mm und EPS 140 mm, Materialien richtig zugewiesen? Konvektion innen 7,7 bei 20 °C, außen 25 bei −10 °C? Einheitensystem Metric (m)?">
</div>

### U-Wert der sanierten Wand in W/(m²·K)

<div class="numeric-question" data-answer="0.212" data-tolerance="0.003" data-points="5" data-attempts="5" data-hints="U ist die Wärmestromdichte je Kelvin Temperaturunterschied zwischen Raumluft und Außenluft (30 K).">
</div>

### Oberflächentemperatur innen in °C

<div class="numeric-question" data-answer="19.17" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Temperatur auf der Innenfläche des Vollziegels auswerten, nicht die Raumluft.">
</div>

### Erfüllt die sanierte Wand das GEG ($U \le 0{,}24\ \mathrm{W/(m^2\,K)}$)?

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u1a" name="u1">
      <label for="u1a">Ja</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u1b" name="u1">
      <label for="u1b">Nein</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- $R_T = 0{,}130 + 0{,}365/0{,}68 + 0{,}140/0{,}035 + 0{,}040 = 4{,}707\ \mathrm{m^2\,K/W}$
- $U = 1/R_T = 0{,}212\ \mathrm{W/(m^2\,K)} \le 0{,}24$: Das GEG ist erfüllt
- $\dot q = U \cdot 30\ \mathrm{K} = 6{,}37\ \mathrm{W/m^2}$
- $T_{si} = 20 - 6{,}37 \cdot 0{,}130 = 19{,}17\ \mathrm{°C}$
- Zum Vergleich der Altbau ohne Dämmung: $U = 1{,}415\ \mathrm{W/(m^2\,K)}$, $\dot q = 42{,}5\ \mathrm{W/m^2}$, innen nur 14,5 °C an der Wand. Die Dämmung spart **85 %** des Wärmeverlusts

</div>
