---
title: 1 · Modell
---

# 1 · Modell aufbauen <small>(Workbench, SpaceClaim, Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** Material, Geometrie und Netz der Röhre anlegen, wie in Praktikum 1
</div>

Material, Zuweisung und Netz kennen Sie aus Praktikum 1. Neu ist nur die
Geometrie aus Kreisen und einem Rechteck.

## Material

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Material"

??? tip "Kurzanleitung: Material"
    1. In der Toolbox links `Doppelklick Steady-State Thermal`, Analyse umbenennen in **a) Selektiv**, Projekt speichern (`File → Save As...`, Ordner `Dokumente`)
    2. `Doppelklick Engineering Data`, `Rechtsklick Structural Steel → Delete`
    3. In die leere Zeile **Glas** eintragen, in der Toolbox **Thermal** aufklappen, `Doppelklick Isotropic Thermal Conductivity`, Wert **1,1** W m⁻¹ C⁻¹
    4. Genauso **Kupfer** mit **400** W m⁻¹ C⁻¹ anlegen
    5. Oben `Project` anklicken

## Geometrie

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Geometrie"

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Vier Kreise und ein Rechteck</p>
    <p><code>Rechtsklick Geometry → New SpaceClaim Geometry...</code>. Mit <code>Circle</code> vier Kreise um den Ursprung zeichnen: Ø <strong>70</strong>, <strong>65</strong>, <strong>12</strong> und <strong>10</strong> mm (auf den Ursprung klicken, Durchmesser eintippen, <code>Enter</code>). Dann <code>Rectangle</code>, links unter <code>Options</code> <strong>Define rectangle from center</strong> einschalten, auf den Ursprung klicken, <strong>60</strong> mm × <strong>0,5</strong> mm</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Vakuum und Wasser entfernen</p>
    <p>Skizze beenden (<code>Pull</code>, Taste <code>P</code>). Die Flächen, die kein Körper werden, anklicken und mit <code>Entf</code> löschen: alles <strong>innerhalb Ø 10 mm</strong> (Wasser, drei Flächen). Liegt zwischen Rohr und Glas eine Fläche (Vakuum), diese ebenfalls löschen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwei Körper ziehen</p>
    <p>Mit <code>Pull</code> den Glasring <strong>20 mm</strong> ziehen. Danach alle Flächen von Blech und Kupferrohr mit <code>Strg</code> markieren (sechs Flächen: zwei Blechflügel, zwei Rohrhälften, zwei kleine Blechstücke in der Rohrwand) und ebenfalls <strong>20 mm</strong> ziehen. Das Blech ist nur 0,5 mm dick: stark heranzoomen, sonst trifft der Klick eine Kante statt der Fläche. Im Strukturbaum die beiden Körper umbenennen: <strong>Glas</strong> und <strong>Absorber</strong>. Share Topology ist nicht nötig, die Körper berühren sich nicht</p>
  </div>

</div>

!!! check "Checkpoint"
    Im Strukturbaum von SpaceClaim stehen genau **zwei** Körper. Besteht der
    Absorber aus mehreren Körpern, diese mit dem Werkzeug `Combine`
    (Reiter **Design**) zusammenfügen: erst einen Teil anklicken, dann mit
    `Strg` die übrigen.

## Zuweisung und Netz

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Vernetzung"

??? tip "Kurzanleitung: Zuweisung und Netz"
    1. Im Projektmenü `Rechtsklick Model → Edit...`, unten rechts das Einheitensystem **Metric (m, kg, N, s, V, A)** mit Temperatur in **Celsius** prüfen
    2. `Strukturbaum Geometry` aufklappen, Körper **Glas** anklicken, im `Detailfenster` bei **Assignment** **Glas** wählen, Körper **Absorber** mit **Kupfer**
    3. `Strukturbaum Mesh` anklicken, im `Detailfenster` bei **Element Size** **0,002** m eintragen
    4. `Rechtsklick Mesh → Generate Mesh`

Weiter mit den [Randbedingungen](02-randbedingungen.md).
