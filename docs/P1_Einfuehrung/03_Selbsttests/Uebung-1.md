---
title: "Übung 1: Altbau sanieren"
---

# Übung 1: Altbau sanieren

Ein Gründerzeithaus hat eine **36,5 cm** dicke Wand aus Vollziegel und keine
Dämmung. Sie soll außen gedämmt werden. Nach dem Gebäudeenergiegesetz (GEG)
darf die sanierte Außenwand höchstens $U = 0{,}24\ \mathrm{W/(m^2K)}$ haben.

Diese Übung ist noch eindimensional: Der Ablauf aus dem Vorzeigebeispiel wird
wiederholt, und jedes Ergebnis lässt sich von Hand prüfen.

<figure style="text-align:center;">
  <img src="../../images/p1_uebung1.svg" alt="Vollziegelwand mit Dämmung der Dicke d" class="no-lightbox">
</figure>

## Gegeben

- **Vollziegel**: $\lambda = 0{,}68\ \mathrm{W/(m\,K)}$, Dicke **365 mm**
- **EPS**: $\lambda = 0{,}035\ \mathrm{W/(m\,K)}$, Mindestdicke $d$ gesucht, eingebaut werden **140 mm**
- Wandausschnitt 100 × 100 mm, Netzgröße global 10 mm
- Randbedingungen wie im Vorzeigebeispiel **Fall b) Konvektion**

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">a) Erst ohne Dämmung</p>
    <p>Material <strong>Vollziegel</strong> anlegen, eine Wand aus <strong>einem</strong> Körper (365 mm) aufbauen und den U-Wert bestimmen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">b) Mindestdicke von Hand</p>
    <p>Welcher Gesamtwiderstand $R_T$ gehört zu $U = 0{,}24$? Wie viel davon fehlt noch? Daraus folgt $d$</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">c) Sanierte Wand mit FEM</p>
    <p>Eingebaut wird die handelsübliche Dicke <strong>140 mm</strong>. Eine zweite Analyse anlegen und die Wand genau wie im Vorzeigebeispiel aus zwei Körpern aufbauen: Vollziegel 365 mm, EPS 140 mm. Die Geometrie aus a) bleibt unverändert</p>
  </div>

</div>

## Gesucht

### a) U-Wert der ungedämmten Wand in W/(m²·K)

<div class="numeric-question" data-answer="1.415" data-tolerance="0.01" data-points="5" data-attempts="5" data-hints="Material Vollziegel zugewiesen? Dicke 365 mm? Konvektion innen und außen wie im Vorzeigebeispiel?">
</div>

### b) Mindestdicke der Dämmung in mm

<div class="numeric-question" data-answer="121.1" data-tolerance="1.5" data-points="5" data-attempts="5" data-hints="R_T = 1/U = 4,167 m²K/W. Davon Übergänge (0,130 + 0,040) und Vollziegel (0,537) abziehen, Rest mal λ der Dämmung.">
</div>

### c) Wärmestromdichte der sanierten Wand (140 mm EPS) in W/m²

<div class="numeric-question" data-answer="6.37" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Zwei Körper mit Share Topology? EPS 140 mm dick und Material EPS zugewiesen? Konvektion innen und außen wie im Vorzeigebeispiel?">
</div>

<div class="solution-images" markdown="1">

### Lösung

- a) $R_T = 0{,}130 + 0{,}365/0{,}68 + 0{,}040 = 0{,}707\ \mathrm{m^2K/W}$, also $U = 1{,}415\ \mathrm{W/(m^2K)}$ und $\dot q = 42{,}5\ \mathrm{W/m^2}$
- b) fehlender Widerstand $1/0{,}24 - 0{,}707 = 3{,}460\ \mathrm{m^2K/W}$, also $d = 3{,}460 \cdot 0{,}035 = 0{,}121\ \mathrm{m}$. 12 cm reichen knapp nicht ($U = 0{,}242$), deshalb die nächste handelsübliche Dicke **14 cm**
- c) $R_T = 0{,}707 + 0{,}140/0{,}035 = 4{,}707\ \mathrm{m^2K/W}$, also $U = 0{,}212 \le 0{,}24$ und $\dot q = 30/4{,}707 = 6{,}37\ \mathrm{W/m^2}$: **85 % weniger** Wärmeverlust als vorher

</div>
