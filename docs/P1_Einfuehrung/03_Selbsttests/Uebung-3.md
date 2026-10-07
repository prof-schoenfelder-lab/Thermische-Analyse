---
title: "Übung 3: Fußbodenheizung"
---

# Übung 3: Fußbodenheizung

Ein Heizrohr liegt im Estrich. Über dem Rohr wird der Boden wärmer als zwischen
den Rohren. Wie groß ist dieser Unterschied, wie viel Wärme gibt der Boden ab,
und bleibt die Oberfläche unter dem Grenzwert von **29 °C**, ab dem es an den
Füßen unangenehm wird? Eine Handrechnung gibt es dafür nicht.

<figure style="text-align:center;">
  <img src="../../images/p1_uebung3.svg" alt="Schnitt durch die Fußbodenheizung" class="no-lightbox">
</figure>

## Gegeben

- **Zementestrich**: $\lambda = 1{,}4\ \mathrm{W/(m\,K)}$, Dicke **65 mm**
- **Heizrohr**: Ø **16 mm**, Mitte **20 mm** über der Dämmung, Rohrabstand **150 mm**
- Ausschnitt: ein Rohrabstand breit (150 mm), **20 mm** tief
- Netzgröße global **2 mm**
- Randbedingungen:
    - Rohroberfläche: Temperatur **35 °C** (Rohrwand vernachlässigt)
    - Oberseite: Raum **20 °C**, $\alpha = 10{,}8\ \mathrm{W/(m^2K)}$ (Konvektion und Strahlung zusammen nach DIN EN 1264)
    - Unterseite (Dämmung) und Seitenflächen: adiabat

!!! info "Warum sind die Seitenflächen adiabat?"
    Links und rechts folgen weitere Rohre mit gleichem Abstand. Genau in der
    Mitte zwischen zwei Rohren fließt deshalb keine Wärme zur Seite: Das ist eine
    Symmetrieebene. Mehr dazu in Praktikum 3.

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Skizze mit Loch</p>
    <p>Rechteck 150 × 65 mm, dazu mit <code>Circle</code> einen Kreis Ø 16 mm, Mittelpunkt 20 mm über der Mitte der Unterkante</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Nur den Estrich ziehen</p>
    <p>Mit <code>Pull</code> nur die Fläche <strong>um</strong> den Kreis 20 mm ziehen. Der Kreis bleibt frei: Es entsteht ein Körper mit Loch</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingungen</p>
    <p>Innenfläche des Lochs: <code>Temperature</code> 35 °C. Oberseite: <code>Convection</code>. Alle anderen Flächen bleiben frei</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswerten</p>
    <p>Temperatur auf der Oberseite (Maximum und Minimum). Wärmestrom: <code>Rechtsklick Solution → Insert → Probe → Reaction</code>, dort die Konvektion auswählen, und durch die Fläche teilen</p>
  </div>

</div>

<!-- TODO: Hinweise zu Circle und Reaction Probe mit ANSYS 2025 R2 prüfen; Datei P1_Fussbodenheizung.scdoc ablegen -->

## Gesucht

### Oberflächentemperatur über dem Rohr in °C

<div class="numeric-question" data-answer="30.10" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Maximum der Temperatur auf der Oberseite. Rohr 35 °C als Temperature auf der Lochfläche, oben Convection 10,8 bei 20 °C?">
</div>

### Oberflächentemperatur zwischen den Rohren in °C

<div class="numeric-question" data-answer="28.97" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Minimum der Temperatur auf der Oberseite, also an den Seitenkanten.">
</div>

### Wärmestromdichte nach oben in W/m²

<div class="numeric-question" data-answer="102.5" data-tolerance="3" data-points="5" data-attempts="5" data-hints="Reaction Probe der Konvektion liefert den Wärmestrom in W. Durch die Oberfläche 0,15 m × 0,02 m teilen.">
</div>

### Wird der Grenzwert von 29 °C an der Oberfläche eingehalten?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="2">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="checkbox" id="u3a" name="u3">
      <label for="u3a">Ja, überall</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="checkbox" id="u3b" name="u3">
      <label for="u3b">Nein, über dem Rohr liegt die Oberfläche darüber</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Oberfläche über dem Rohr **30,1 °C**, zwischen den Rohren **29,0 °C**: rund 1,1 K Unterschied
- Wärmestromdichte nach oben rund **102 W/m²**, das ist eine typische Heizleistung für Fußbodenheizungen
- Der Grenzwert von 29 °C wird über dem Rohr überschritten. Abhilfe: niedrigere Vorlauftemperatur oder ein Bodenbelag, der etwas dämmt
- Mit dem Modell lässt sich das schnell ausprobieren: andere Rohrabstände, mehr Estrich darüber, niedrigere Rohrtemperatur

</div>
