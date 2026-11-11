---
title: 1 · Modell
---

# 1 · Modell aufbauen <small>(Workbench, SpaceClaim, Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** Material anlegen, den Querschnitt als 2D-Skizze zeichnen, die Dicke 1000 mm setzen und vernetzen
</div>

Material und Netz kennen Sie aus Praktikum 1 und 2. Neu ist das **2D-Modell**:
Die Geometrie ist eine Fläche statt eines Körpers, und Workbench wird vor dem
Zeichnen auf 2D umgestellt.

<!-- Klickanleitungen nach dem Klicktest (23. bis 29.11.) einfügen: <tutorial slug="p3-…"></tutorial> -->

## Material

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Material"

??? tip "Kurzanleitung: Material"
    1. In der Toolbox links `Doppelklick Steady-State Thermal`, Analyse umbenennen in **a) Querschnitt**, Projekt speichern (`File → Save As...`, Ordner `Dokumente`)
    2. `Doppelklick Engineering Data`, `Rechtsklick Structural Steel → Delete`
    3. In die leere Zeile **PUR** eintragen, in der Toolbox **Thermal** aufklappen, `Doppelklick Isotropic Thermal Conductivity`, Wert **0,027** W m⁻¹ C⁻¹
    4. Genauso **Erdreich** mit **1** W m⁻¹ C⁻¹ anlegen
    5. Oben `Project` anklicken

## 2D einstellen

Workbench muss wissen, dass die Geometrie zweidimensional ist, **bevor**
SpaceClaim geöffnet wird.

??? tip "Kurzanleitung: Analysis Type 2D"
    1. Im Projektmenü `Rechtsklick Geometry → Properties`
    2. Im Fenster **Properties** bei **Analysis Type** `2D` wählen

## Geometrie

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Geometrie"

Der Ursprung liegt in der Rohrachse. Die Oberfläche liegt dann bei
y = 900 mm, die Unterkante bei y = −2100 mm, die Mitte des Blocks also
600 mm unter der Rohrachse.

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Zwei Kreise und ein Rechteck in der x-y-Ebene</p>
    <ul>
      <li><code>Rechtsklick Geometry → New SpaceClaim Geometry...</code>, die Skizze liegt in der <strong>x-y-Ebene</strong></li>
      <li>Mit <code>Circle</code> zwei Kreise um den Ursprung: Ø <strong>114,3</strong> und <strong>193,6</strong> mm</li>
      <li>Vom Ursprung mit <code>Line</code> eine Hilfslinie <strong>600 mm</strong> nach unten</li>
      <li>An ihrem Ende <code>Rectangle</code> mit <strong>Define rectangle from center</strong> (links unter <code>Options</code>): <strong>6000 × 3000</strong> mm</li>
      <li>Die Hilfslinie vor dem Beenden der Skizze löschen, sonst teilt sie die Flächen</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Rohrinneres entfernen</p>
    <ul>
      <li>Skizze beenden (<code>Pull</code>, Taste <code>P</code>), aus der Skizze werden Flächen</li>
      <li>Die Fläche <strong>innerhalb Ø 114,3 mm</strong> anklicken und mit <code>Entf</code> löschen: Stahlrohr und Wasser sind nicht im Modell</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Share Topology und Namen</p>
    <ul>
      <li><code>Rechtsklick Design1 → Properties</code>, unter <strong>Analysis</strong> bei <strong>Share Topology</strong> den Wert <strong>Share</strong> wählen</li>
      <li>Im Strukturbaum die beiden Flächen umbenennen: <strong>Erdreich</strong> und <strong>Daemmung</strong></li>
    </ul>
  </div>

</div>

!!! check "Checkpoint"
    Im Strukturbaum von SpaceClaim stehen genau **zwei** Flächen (Surface), der
    Ring und das Erdreich mit dem Loch. Innerhalb des kleinen Kreises ist nichts.

## Dicke

Das 2D-Modell steht für eine Scheibe. Mit der Dicke 1000 mm ist jeder
Wärmestrom gleich der Wert **je Meter** Rohr, siehe
[Abstraktionen](../../01_Grundlagen/Abstraktionen.md#von-3d-zu-2d).

??? tip "Kurzanleitung: Dicke 1000 mm"
    1. Im Projektmenü `Rechtsklick Model → Edit...`, unten rechts das Einheitensystem **Metric (m, kg, N, s, V, A)** mit Temperatur in **Celsius** prüfen
    2. `Strukturbaum Geometry` anklicken: Im `Detailfenster` steht **2D Behavior** `Plane Stress`, so lassen
    3. Fläche **Erdreich** anklicken, im `Detailfenster` bei **Thickness** **1** m eintragen (= 1000 mm)
    4. Genauso bei der Fläche **Daemmung**

## Zuweisung und Netz

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Vernetzung"

??? tip "Kurzanleitung: Zuweisung und Netz"
    1. Fläche **Erdreich** anklicken, im `Detailfenster` bei **Assignment** **Erdreich** wählen, Fläche **Daemmung** mit **PUR**
    2. `Strukturbaum Mesh` anklicken, im `Detailfenster` bei **Element Size** **0,05** m eintragen (= 50 mm)
    3. `Rechtsklick Mesh → Generate Mesh`

!!! check "Checkpoint"
    Unter `Connections` gibt es **keine** Kontakte (dank Share Topology). Steht
    dort doch ein Kontakt, wurde in SpaceClaim Share Topology nicht auf
    *Share* gestellt.

Weiter mit den [Randbedingungen](02-randbedingungen.md).
