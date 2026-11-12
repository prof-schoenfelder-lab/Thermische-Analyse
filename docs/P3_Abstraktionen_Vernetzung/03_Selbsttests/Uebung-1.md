---
title: "Übung 1: Vor- und Rücklauf im Erdreich"
---

# Übung 1: Vor- und Rücklauf im Erdreich

Fernwärme fließt im Kreis: Im **Vorlauf** kommt das heiße Wasser zu den Häusern,
im **Rücklauf** fließt es abgekühlt zurück zum Heizwerk. Beide Rohre liegen
nebeneinander im selben Graben. Wie viel Wärme verliert das Rohrpaar, und darf
man es als Halbmodell rechnen?

<figure style="text-align:center;">
  <img src="../../images/p3_vor_ruecklauf.excalidraw.png" alt="Bodenblock 6 m mal 3 m mit zwei Rohren 0,9 m unter der Oberfläche, rechts vergrößert Vorlauf 80 °C und Rücklauf 50 °C mit 100 mm Abstand" class="no-lightbox">
</figure>

## Gegeben

Rohre, Erdreich und Netz wie im
[Vorzeigebeispiel](../02_Vorzeigebeispiel/Fernwaermerohr/index.md).

**Material**

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Material"

**Geometrie** (2D-Querschnitt mit der Dicke 1000 mm)

- Erdreich 6 m breit und 3 m tief, die Oberfläche oben
- zwei Rohre nebeneinander, die Achsen 900 mm unter der Oberfläche
- Achsabstand 300 mm (Abstand der Mantelrohre 100 mm), mittig im Block: Vorlauf links, Rücklauf rechts
- je Rohr nur die Dämmung als Ring: innen Ø 114,3 mm, außen Ø 193,6 mm

**Netz**

- Netzgröße global 50 mm (in Mechanical 0,05 m)

**Randbedingungen**

| Wo | Randbedingung | Wert |
|---|---|---|
| Innenrand des linken Rings | Temperatur (Vorlauf) | $T = 80\ \mathrm{°C}$ |
| Innenrand des rechten Rings | Temperatur (Rücklauf) | $T = 50\ \mathrm{°C}$ |
| Oberfläche des Erdreichs (obere Kante) | Temperatur | $T = 10\ \mathrm{°C}$ |
| Seiten und Unterkante | keine (adiabat) | |

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwei Rohre zeichnen</p>
    <ul>
      <li>Neue Analyse wie in a): Material, <strong>Analysis Type</strong> <code>2D</code>, Dicke 1000 mm und Netz wie dort</li>
      <li>Der Ursprung liegt in der Mitte zwischen den Rohren: vom Ursprung je eine Hilfslinie <strong>150 mm</strong> nach links und nach rechts, an ihren Enden je zwei Kreise Ø <strong>114,3</strong> und <strong>193,6</strong> mm</li>
      <li>Das Rechteck <strong>6000 × 3000</strong> mm wie in a) über eine Hilfslinie <strong>600 mm</strong> nach unten, danach alle Hilfslinien löschen</li>
      <li>Skizze beenden (<code>Pull</code>), beide Flächen innerhalb Ø 114,3 mm löschen: Es bleiben drei Flächen, das Erdreich und zwei Dämmringe</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Die beiden Innenkanten auseinanderhalten</p>
    <ul>
      <li>Beide Innenkanten haben denselben Radius. Die Named Selection braucht deshalb eine zweite Zeile im Worksheet, die nach der Lage filtert</li>
      <li><strong>Vorlauf innen:</strong> Zeile 1 <code>Add</code>, <code>Edge</code>, <code>Radius</code>, <strong>0,05715</strong> m (57,15 mm); Zeile 2 <code>Filter</code>, <code>Edge</code>, <code>Location X</code>, <code>Less Than</code>, <strong>0</strong></li>
      <li><strong>Ruecklauf innen:</strong> genauso, in Zeile 2 <code>Greater Than</code></li>
      <li>Unter <strong>Statistics</strong> steht bei beiden <strong>1</strong> Kante</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">b) und d) Halbmodell</p>
    <ul>
      <li>Die Analyse duplizieren und in SpaceClaim wie im <a href="../../02_Vorzeigebeispiel/Fernwaermerohr/b-halbmodell/">Vorzeigebeispiel b)</a> eine senkrechte Linie durch den Ursprung ziehen</li>
      <li>Die Flächen <strong>rechts</strong> der Linie löschen, also die rechte Hälfte des Erdreichs und den Rücklauf</li>
      <li>In Mechanical <code>Rechtsklick Named Selections → Generate Named Selections</code>, die Temperatur des Rücklaufs unterdrücken (<code>Rechtsklick → Suppress</code>)</li>
      <li>Die Symmetrielinie bekommt keine Randbedingung</li>
    </ul>
  </div>

</div>

<!-- Klicktest: Filter-Zeile mit Location X im Worksheet prüfen; Sollwerte aus tools/sollwerte/p3_vor_ruecklauf.py (Abstand der Mantelrohre 100 mm), durch die ANSYS-Werte ersetzen -->

## Gesucht

### a) Vorlauf: Wärmeverlust in W/m

<div class="numeric-question" data-answer="18.55" data-tolerance="0.4" data-points="5" data-attempts="5" data-hints="Reaction Probe der Temperatur am Vorlauf ablesen; Dicke 1000 mm bei allen drei Flächen?; Vorlauf links mit 80 °C, Rücklauf rechts mit 50 °C, Oberfläche 10 °C?">
</div>

### a) Rücklauf: Wärmeverlust in W/m

<div class="numeric-question" data-answer="9.45" data-tolerance="0.25" data-points="5" data-attempts="5" data-hints="Reaction Probe der Temperatur am Rücklauf ablesen; Named Selection Ruecklauf innen mit Location X größer 0?">
</div>

### Darf man das Rohrpaar als Halbmodell rechnen, mit der Symmetrielinie in der Mitte zwischen den Rohren?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="p3u1a" name="p3u1">
      <label for="p3u1a">Ja, Geometrie und Material sind spiegelbildlich</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="p3u1b" name="p3u1">
      <label for="p3u1b">Nein, die beiden Rohre haben verschiedene Temperaturen</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="p3u1c" name="p3u1">
      <label for="p3u1c">Ja, wenn man den Wärmeverlust des Halbmodells danach verdoppelt</label>
    </div>
  </div>
</div>

### b) Zur Probe: Halbmodell mit dem Vorlauf, Wärmeverlust verdoppelt, in W/m

<div class="numeric-question" data-answer="35.64" data-tolerance="0.7" data-points="5" data-attempts="5" data-hints="Linke Hälfte mit dem Vorlauf behalten, Temperatur am Rücklauf unterdrückt; Symmetrielinie ohne Randbedingung; Reaktion am Vorlauf mal 2">
</div>

### c) Um wie viel Prozent verliert das Rohrpaar weniger Wärme als zwei einzeln verlegte Rohre?

Ein einzeln verlegtes Rohr verliert bei 80 °C 19,5 W/m (Vorzeigebeispiel).
Sein Wärmeverlust ist proportional zur Differenz zwischen Rohrtemperatur und
Oberflächentemperatur (10 °C).

<div class="numeric-question" data-answer="8.5" data-tolerance="1" data-points="5" data-attempts="5" data-hints="Einzelner Rücklauf: 19,5 W/m mal 40 K / 70 K; Summe der Einzelrohre mit der Summe aus a) vergleichen; Ergebnis in Prozent der Einzelrohre">
</div>

### d) Optional: Halbmodell mit der Mitteltemperatur 65 °C, Wärmeverlust verdoppelt, in W/m

<div class="numeric-question" data-answer="28.0" data-tolerance="0.5" data-points="5" data-attempts="5" data-hints="Halbmodell aus b), am Vorlauf 65 °C statt 80 °C; Reaktion am Vorlauf mal 2; mit der Summe aus a) vergleichen">
</div>

<div class="solution-images" markdown="1">

### Lösung

- a) Vorlauf **18,6 W/m**, Rücklauf **9,5 W/m**, zusammen 28,0 W/m. Eine Handrechnung für Rohrpaare nach EN 13941 ergibt 28,5 W/m
- **Kein Halbmodell:** Symmetrie verlangt spiegelbildliche Geometrie, Material **und** Randbedingungen. Hier hat das rechte Rohr 50 statt 80 °C
- b) Das Halbmodell rechnet zwei Vorläufe nebeneinander: 2 · 17,8 = **35,6 W/m**, 27 % zu viel
- c) Einzeln verlegt verliert der Rücklauf 19,5 · 40/70 = 11,1 W/m, beide Rohre zusammen 30,6 W/m. Das Paar verliert **8 % weniger**: Jedes Rohr wärmt das Erdreich um das andere an. Der Vorlauf verliert 18,6 statt 19,5 W/m, der Rücklauf 9,5 statt 11,1 W/m
- d) Mit 65 °C trifft das Halbmodell die Summe aus a): 2 · 14,0 = **28,0 W/m**. Wenn die Wärmeleitfähigkeit nicht von der Temperatur abhängt, lassen sich Temperaturfelder addieren. Das Feld mit 80 und 50 °C ist dann die Summe aus zwei Feldern:
    - beide Rohre 65 °C, Oberfläche 10 °C: symmetrisch, das Halbmodell ist erlaubt
    - Vorlauf +15 K, Rücklauf −15 K, Oberfläche 0 K: Die Wärme fließt vom Vorlauf zum Rücklauf, an der Oberfläche kommt netto nichts an
- Für die Summe zählt deshalb nur das erste Feld. Wie sich der Verlust auf Vorlauf und Rücklauf aufteilt, zeigt das Halbmodell aber nicht. Hersteller geben den Verlust eines Rohrpaars deshalb für die Mitteltemperatur an

</div>
