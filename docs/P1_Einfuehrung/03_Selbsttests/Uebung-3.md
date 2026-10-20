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
    <p class="step-title" role="heading" aria-level="2">Zwei Rechtecke für den Estrich</p>
    <p>Ursprung = Mitte der Unterkante. Links und rechts davon je ein Rechteck 75 × 65 mm, zusammen 150 × 65 mm</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Mittelpunkt des Rohrs</p>
    <p>Mit <code>Line</code> vom Ursprung aus 20 mm senkrecht nach oben: Der Endpunkt der Linie ist der Mittelpunkt des Rohrs</p>
    <img src="../../images/p1_uebung3_linie.png" alt="Linie 20 mm vom Ursprung nach oben">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Kreis für das Rohr</p>
    <p>Mit <code>Circle</code> auf den Endpunkt der Linie klicken und Ø 16 mm eingeben</p>
    <img src="../../images/p1_uebung3_kreis.png" alt="Kreis Ø 16 mm am Ende der Linie">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Kreis entfernen und ziehen</p>
    <p>Skizze beenden, die beiden Kreisflächen markieren und mit <code>Rechtsklick → Delete</code> löschen. Dann die übrigen Estrichflächen mit <code>Strg</code> markieren und mit <code>Pull</code> 20 mm ziehen: Es entsteht der Estrich mit einem Loch für das Rohr</p>
    <img src="../../images/p1_uebung3_kreis_loeschen.png" alt="Kreisflächen markiert, Rechtsklick, Delete">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingungen</p>
    <p>Innenfläche des Lochs: <code>Convection</code> mit 1000 W/m²·°C und 35 °C (Wasser). Oberseite: <code>Convection</code> mit 10,8 W/m²·°C und 20 °C. Alle anderen Flächen bleiben frei</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Pfad durch das Rohr anlegen</p>
    <p>Für die Temperatur genau über dem Rohr: <code>Rechtsklick Strukturbaum Model → Insert → Construction Geometry → Path</code></p>
    <img src="../../images/p1_uebung3_pfad_einfuegen.png" alt="Model, Insert, Construction Geometry, Path">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Start- und Endpunkt des Pfads</p>
    <p>Im <code>Detailfenster</code> senkrecht durch die Rohrmitte von der Unterseite bis zur Oberseite, hier Start (0, 0, 0) und Ende (0, 0,065, 0) in m. Die Werte hängen davon ab, wo das Koordinatensystem liegt: anzeigen mit <code>Reiter Display → Show → All Coordinate Systems</code></p>
    <img src="../../images/p1_uebung3_pfad_punkte.png" alt="Pfad mit Start- und Endpunkt im Detailfenster">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Temperatur entlang des Pfads</p>
    <p><code>Rechtsklick Solution → Insert → Thermal → Temperature</code>, im <code>Detailfenster</code> bei <strong>Scoping Method</strong> <code>Path</code> wählen und darunter bei <strong>Path</strong> den eben angelegten Pfad (er heißt ebenfalls „Path“). Der Wert am Pfadende ist die Oberfläche über dem Rohr</p>
    <img src="../../images/p1_uebung3_pfad_scoping.png" alt="Scoping Method auf Path">
    <img src="../../images/p1_uebung3_pfad_auswahl.png" alt="Pfad auswählen">
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwischen den Rohren und Wärmestrom</p>
    <p>Temperatur auf der Oberseite: Das Minimum liegt zwischen den Rohren. Wärmestrom: <code>Rechtsklick Solution → Insert → Probe → Reaction</code>, dort die Konvektion der Oberseite auswählen, und durch die Fläche teilen</p>
  </div>

</div>

<!-- TODO: Reaction Probe mit ANSYS 2025 R2 prüfen (Vorzeichen); Datei P1_Fussbodenheizung.scdoc ablegen -->

## Gesucht

### Oberflächentemperatur über dem Rohr in °C

<div class="numeric-question" data-answer="29.87" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Temperatur am Ende des Pfads durch die Rohrmitte (Oberseite). Im Rohr Convection 1000 bei 35 °C, oben Convection 10,8 bei 20 °C?">
</div>

### Oberflächentemperatur zwischen den Rohren in °C

<div class="numeric-question" data-answer="28.78" data-tolerance="0.15" data-points="5" data-attempts="5" data-hints="Minimum der Temperatur auf der Oberseite, also an den Seitenkanten.">
</div>

### Wärmestromdichte nach oben in W/m²

<div class="numeric-question" data-answer="100.2" data-tolerance="3" data-points="5" data-attempts="5" data-hints="Reaction Probe der Konvektion an der Oberseite liefert den Wärmestrom in W. Durch die Oberfläche 0,15 m × 0,02 m teilen.">
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
