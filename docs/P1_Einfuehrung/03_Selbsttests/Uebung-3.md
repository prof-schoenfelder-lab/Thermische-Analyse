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

**Material**

- Zementestrich: $\lambda = 1{,}4\ \mathrm{W/(m\,K)}$

**Geometrie**

- Estrich **65 mm** dick
- Heizrohr: Ø **16 mm**, Mitte **20 mm** über der Dämmung, Rohrabstand **150 mm**
- Ausschnitt: ein Rohrabstand breit (150 mm), **20 mm** lang in Rohrrichtung

**Netz**

- Netzgröße global **2 mm**

**Randbedingungen**

- Rohr innen: Konvektion, Wasser $T = 35\ \mathrm{°C}$, $\alpha = 1000\ \mathrm{W/(m^2\,K)}$ (strömendes Wasser, Rohrwand vernachlässigt)
- Oberseite: Raumluft $T_i = 20\ \mathrm{°C}$, $\alpha = 10{,}8\ \mathrm{W/(m^2\,K)}$ (Konvektion und Strahlung zusammen nach DIN EN 1264)
- Unterseite (Dämmung) und Seitenflächen: adiabat

!!! info "Warum sind die Seitenflächen adiabat?"
    Links und rechts folgen weitere Rohre mit gleichem Abstand. Genau in der
    Mitte zwischen zwei Rohren fließt deshalb keine Wärme zur Seite: Das ist eine
    Symmetrieebene. Mehr dazu in Praktikum 3.

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <p>Ursprung = Mitte der Unterkante, links und rechts je ein Rechteck 75 × 65 mm. Mit <code>Line</code> vom Ursprung 20 mm nach oben (Endpunkt = Rohrmitte), dort mit <code>Circle</code> Ø 16 mm. Skizze beenden, die Kreisflächen mit <code>Rechtsklick → Delete</code> löschen, die übrigen Flächen mit <code>Strg</code> markieren und 20 mm ziehen</p>
    <p class="hinweis-bilder"><img src="../../images/p1_uebung3_linie.png" alt="Linie 20 mm nach oben"><img src="../../images/p1_uebung3_kreis.png" alt="Kreis Ø 16 mm"><img src="../../images/p1_uebung3_kreis_loeschen.png" alt="Kreisflächen löschen"></p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingungen</p>
    <p>Lochfläche: <code>Convection</code> 1000 W/m²·°C, 35 °C. Oberseite: <code>Convection</code> 10,8 W/m²·°C, 20 °C. Alle anderen Flächen bleiben frei</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Temperatur über dem Rohr (Pfad)</p>
    <p><code>Rechtsklick Model → Insert → Construction Geometry → Path</code>, Start (0, 0, 0) und Ende (0, 0,065, 0) m, senkrecht durch die Rohrmitte (Lage des Koordinatensystems: <code>Display → Show → All Coordinate Systems</code>). Dann <code>Insert → Thermal → Temperature</code>, <strong>Scoping Method</strong> <code>Path</code>, den Pfad wählen. Der Wert am Pfadende ist die Oberfläche über dem Rohr</p>
    <p class="hinweis-bilder"><img src="../../images/p1_uebung3_pfad_einfuegen.png" alt="Path einfügen"><img src="../../images/p1_uebung3_pfad_punkte.png" alt="Start- und Endpunkt"><img src="../../images/p1_uebung3_pfad_scoping.png" alt="Scoping Method Path"><img src="../../images/p1_uebung3_pfad_auswahl.png" alt="Pfad wählen"></p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwischen den Rohren und Wärmestromdichte</p>
    <p>Temperatur auf der Oberseite: Das Minimum liegt an den Seitenkanten, genau in der Mitte zwischen zwei Rohren. Wärmestromdichte: <code>Insert → Thermal → Directional Heat Flux</code> auf der Oberseite, Richtung senkrecht zur Oberfläche (hier <code>Y Axis</code>), abzulesen ist der Mittelwert (<strong>Average</strong>)</p>
  </div>

</div>


## Gesucht

### Temperatur der Estrichoberfläche über dem Rohr in °C

<div class="numeric-question" data-answer="29.87" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Temperatur am Ende des Pfads durch die Rohrmitte (Oberseite). Im Rohr Convection 1000 bei 35 °C, oben Convection 10,8 bei 20 °C?">
</div>

### Temperatur der Estrichoberfläche genau in der Mitte zwischen zwei Rohren in °C

<div class="numeric-question" data-answer="28.78" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Die kälteste Stelle der Oberseite liegt an ihren Seitenkanten (75 mm neben der Rohrmitte, dort beginnt der Bereich des nächsten Rohrs): Minimum der Temperatur auf der Oberseite.">
</div>

### Mittlere Wärmestromdichte an der Estrichoberfläche (Wärmeabgabe je m² Fußboden) in W/m²

<div class="numeric-question" data-answer="100.2" data-tolerance="3" data-points="5" data-attempts="5" data-hints="Directional Heat Flux auf der Oberseite, Richtung senkrecht zur Oberfläche, Mittelwert (Average). Nicht entlang eines Pfads mitteln: Über dem Rohr tritt mehr Wärme aus.">
</div>

### Wird der Grenzwert von 29 °C an der Oberfläche eingehalten?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="2">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u3a" name="u3">
      <label for="u3a">Ja, überall</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u3b" name="u3">
      <label for="u3b">Nein, über dem Rohr liegt die Oberfläche darüber</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Oberfläche über dem Rohr **29,87 °C**, zwischen den Rohren **28,78 °C**: rund 1,1 K Unterschied
- Wärmestromdichte nach oben **100,2 W/m²**: Das liegt an der Grenze dessen, was eine Fußbodenheizung im Aufenthaltsbereich bei höchstens 29 °C Oberfläche abgeben kann (etwa 100 W/m²)
- Der Grenzwert von 29 °C wird über dem Rohr überschritten. Abhilfe: niedrigere Vorlauftemperatur oder ein Bodenbelag, der etwas dämmt
- Die Rohrwand aus Kunststoff ist hier vernachlässigt. Sie leitet schlecht und würde die Oberfläche noch um gut 1 K kühler machen: Ob der Grenzwert eingehalten wird, hängt also auch an dieser Vereinfachung
- Mit dem Modell lässt sich das schnell ausprobieren, z. B. mit einer niedrigeren Wassertemperatur

</div>
