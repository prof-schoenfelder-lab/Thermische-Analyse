---
title: "Übung 2: Altbau ohne Dämmung"
---

# Übung 2: Altbau ohne Dämmung

Ein Gründerzeithaus hat eine **36,5 cm** dicke Wand aus Vollziegel und keine
Dämmung. Wie viel Wärme verliert diese Wand, und wie kalt wird sie innen?

<figure style="text-align:center;">
  <img src="../../images/p1_uebung2.svg" alt="Vollziegelwand ohne Dämmung" width="560" class="no-lightbox">
</figure>

## Gegeben

- **Vollziegel**: $\lambda = 0{,}68\ \mathrm{W/(m\,K)}$, Dicke **365 mm**, nur **ein** Körper
- Wandausschnitt 1000 × 1000 mm, Netzgröße global 50 mm
- Randbedingungen wie im Vorzeigebeispiel **Fall b) Konvektion**

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Neues Material</p>
    <p>In <code>Engineering Data</code> das Material <strong>Vollziegel</strong> mit <code>Isotropic Thermal Conductivity</code> anlegen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie anpassen</p>
    <p>In SpaceClaim den Körper <strong>EPS</strong> löschen und die Außenfläche des verbleibenden Körpers mit <code>Pull</code> auf insgesamt <strong>365 mm</strong> Dicke ziehen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingung außen prüfen</p>
    <p>Die äußere Konvektion lag auf der Fläche der Dämmung. Nach dem Löschen hat sie keine Fläche mehr (gelbes Fragezeichen): neue Außenfläche auswählen und bei <strong>Geometry</strong> übernehmen</p>
  </div>

</div>

## Gesucht

### U-Wert der Wand in W/(m²·K)

<div class="numeric-question" data-answer="1.415" data-tolerance="0.01" data-points="5" data-attempts="5" data-hints="Material Vollziegel zugewiesen? Dicke 365 mm? Konvektion außen auf der neuen Außenfläche?">
</div>

### Wärmeverlust durch 1 m² Wand in W

<div class="numeric-question" data-answer="42.45" data-tolerance="0.3" data-points="5" data-attempts="5" data-hints="Bei 1 m² Wandfläche ist der Wärmestrom in W gleich der Wärmestromdichte in W/m².">
</div>

### Oberflächentemperatur innen in °C

<div class="numeric-question" data-answer="14.49" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Temperatur-Ergebnis auf die Innenfläche begrenzen (Scope).">
</div>

<div class="solution-images" markdown="1">

### Lösung

- $R_T = 0{,}130 + 0{,}365/0{,}68 + 0{,}040 = 0{,}707\ \mathrm{m^2K/W}$
- $U = 1{,}415\ \mathrm{W/(m^2K)}$, also gut **sechsmal** so viel Wärmeverlust wie die gedämmte Wand
- $T_{si} = 20 - 42{,}45 \cdot 0{,}130 = 14{,}49\ \mathrm{°C}$

Eine kalte Innenoberfläche fühlt sich unbehaglich an. In Ecken und hinter
Möbeln ist es noch kälter, dort droht **Schimmel**.

</div>
