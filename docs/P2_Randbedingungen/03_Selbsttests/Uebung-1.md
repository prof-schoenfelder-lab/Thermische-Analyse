---
title: "Übung 1: Heizungsrohr im Keller"
---

# Übung 1: Heizungsrohr im Keller

Im unbeheizten Keller verläuft ein **ungedämmtes** Heizungsrohr. Wie viel Wärme
verliert es, und welchen Anteil daran hat die Strahlung? Viele schätzen die
Strahlung bei 60 °C als unwichtig ein. Stimmt das?

<figure style="text-align:center;">
  <img src="../../images/p2_heizungsrohr.svg" alt="Heizungsrohr im Keller" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Stahl: $\lambda = 50\ \mathrm{W/(m\,K)}$
- nur für c) Dämmung: $\lambda = 0{,}035\ \mathrm{W/(m\,K)}$

**Geometrie**

- Stahlrohr DN 20: außen Ø 26,9 mm, Wanddicke 2,6 mm
- Länge **1000 mm**, damit alle Wärmeströme direkt je Meter Rohr gelten
- nur für c): Dämmung 20 mm dick um das Rohr (außen Ø 66,9 mm), zweiter Körper mit Share Topology

**Netz**

- Netzgröße global **5 mm**

**Randbedingungen**

- innen: Wasser $T = 60\ \mathrm{°C}$, $\alpha = 1000\ \mathrm{W/(m^2\,K)}$
- außen Konvektion: Kellerluft $T = 15\ \mathrm{°C}$, $\alpha = 7\ \mathrm{W/(m^2\,K)}$
- außen Strahlung: Kellerwände $T = 15\ \mathrm{°C}$, lackierte Oberfläche $\varepsilon = 0{,}9$
- Stirnflächen frei (isoliert)

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <p>Zwei Kreise um den Ursprung, Ø <strong>26,9</strong> und <strong>21,7</strong> mm. Skizze beenden, die innere Kreisfläche löschen, den Ring <strong>1000 mm</strong> ziehen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwei Randbedingungen auf der Außenfläche</p>
    <p>Innenfläche: <code>Convection</code> (Wasser). Außenfläche: <code>Convection</code> (Kellerluft) <strong>und</strong> <code>Radiation</code> (Kellerwände, Correlation <code>To Ambient</code>). Beide gelten gleichzeitig</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wärmeströme ablesen</p>
    <p>Kellerluft und Kellerwände je mit gedrückter Maustaste auf <strong>Solution</strong> ziehen (Reaction Probe), lösen. Der Wärmeverlust ist die Summe beider Beträge. Für Fall a) die Strahlung mit <code>Rechtsklick → Suppress</code> abschalten und neu lösen</p>
  </div>

</div>

## Gesucht

### a) Wärmeverlust je Meter Rohr nur mit Konvektion (ohne Strahlung) in W

<div class="numeric-question" data-answer="26.38" data-tolerance="0.4" data-points="5" data-attempts="5" data-hints="Strahlung unterdrückt (Suppress)? Reaction Probe der Konvektion außen ablesen, Betrag nehmen. Rohr 1000 mm lang? Konvektion innen 1000 bei 60 °C, außen 7 bei 15 °C.">
</div>

### b) Wärmeverlust je Meter Rohr mit Konvektion und Strahlung in W

<div class="numeric-question" data-answer="49.09" data-tolerance="0.7" data-points="5" data-attempts="5" data-hints="Beide Reaktionen der Außenfläche addieren: Konvektion und Strahlung. Strahlung To Ambient mit Emissivity 0,9 und Ambient Temperature 15 °C?">
</div>

### c) Anteil der Strahlung am Wärmeverlust aus b) in %

<div class="numeric-question" data-answer="46.7" data-tolerance="1" data-points="5" data-attempts="5" data-hints="Reaktion der Strahlung geteilt durch den gesamten Wärmeverlust aus b).">
</div>

### d) Optional: Wärmeverlust je Meter mit 20 mm Dämmung in W

<div class="numeric-question" data-answer="9.88" data-tolerance="0.2" data-points="5" data-attempts="5" data-hints="Dämmung als zweiter Körper (Ø 66,9 mm außen, No merge, Share Topology), Material Dämmung 0,035. Konvektion und Strahlung jetzt auf der Außenfläche der Dämmung.">
</div>

<div class="solution-images" markdown="1">

### Lösung

- a) nur Konvektion: **26,4 W/m**, Rohroberfläche 59,6 °C
- b) mit Strahlung: **49,1 W/m**, davon Konvektion 26,2 W/m und Strahlung 22,9 W/m
- c) Strahlung **47 %**: fast die Hälfte. Bei 60 °C ist die Strahlung so groß wie die freie Konvektion
- d) mit Dämmung: **9,9 W/m**, ein Fünftel. Deshalb verlangt das Gebäudeenergiegesetz Dämmung an Heizungsrohren in unbeheizten Räumen
- Die Rohrwand selbst spielt kaum eine Rolle: Stahl leitet gut, die Oberfläche ist weniger als 1 K kälter als das Wasser

</div>
