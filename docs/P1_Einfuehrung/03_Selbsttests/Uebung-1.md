---
title: "Übung 1: Mehr Dämmung"
---

# Übung 1: Mehr Dämmung

Die Wand aus dem Vorzeigebeispiel bekommt statt 14 cm nun **20 cm** Dämmung.
Wie stark sinkt der Wärmeverlust?

<figure style="text-align:center;">
  <img src="../../images/p1_uebung1.svg" alt="Wand mit 20 cm Dämmung" class="no-lightbox">
</figure>

## Gegeben

- Material, Netz und Randbedingungen wie im Vorzeigebeispiel **Fall b) Konvektion**
- Kalksandstein 175 mm, **EPS 200 mm**

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Analyse duplizieren</p>
    <p>Im Projektmenü <code>Rechtsklick</code> auf den Kopf der Analyse <strong>b) Konvektion</strong> und <code>Duplicate</code>, Kopie in <strong>Übung 1</strong> umbenennen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Dämmung dicker machen</p>
    <p><code>Rechtsklick Geometry → Edit Geometry in SpaceClaim...</code>, die Außenfläche der Dämmung mit <code>Pull</code> um <strong>60 mm</strong> nach außen ziehen, SpaceClaim schließen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Aktualisieren und lösen</p>
    <p>Im Projektmenü <code>Rechtsklick Model → Refresh</code>, dann Mechanical öffnen. Die Randbedingungen bleiben erhalten, nur noch lösen und auswerten.</p>
  </div>

</div>

## Gesucht

### U-Wert der Wand in W/(m²·K)

<div class="numeric-question" data-answer="0.1650" data-tolerance="0.002" data-points="5" data-attempts="5" data-hints="U = Wärmestromdichte geteilt durch (20 °C − (−10 °C)) = 30 K. Einheitensystem Metric (m, ...)? Konvektion statt Temperatur auf beiden Seiten?">
</div>

### Oberflächentemperatur innen in °C

<div class="numeric-question" data-answer="19.36" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Temperatur-Ergebnis auf die Innenfläche begrenzen (Scope). Liegt die Konvektion innen bei 7,7 W/(m²·K) und 20 °C?">
</div>

<div class="solution-images" markdown="1">

### Lösung

- $R_T = 0{,}130 + 0{,}177 + 0{,}200/0{,}035 + 0{,}040 = 6{,}061\ \mathrm{m^2K/W}$
- $U = 1/R_T = 0{,}165\ \mathrm{W/(m^2K)}$, $\dot q = 4{,}95\ \mathrm{W/m^2}$
- $T_{si} = 20 - 4{,}95 \cdot 0{,}130 = 19{,}36\ \mathrm{°C}$

6 cm mehr Dämmung senken den Wärmeverlust um etwa **28 %**.

</div>
