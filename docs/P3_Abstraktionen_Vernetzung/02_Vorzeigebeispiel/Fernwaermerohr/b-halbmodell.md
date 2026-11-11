---
title: b) Halbmodell
---

# b) Halbmodell mit Symmetrie

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** dasselbe Rohr nur zur Hälfte rechnen und das Ergebnis mit a) vergleichen
</div>

Das Rohr liegt mittig im Block: Geometrie, Material und Randbedingungen sind
spiegelbildlich zur senkrechten Linie durch die Rohrachse. Damit reicht die
rechte Hälfte (siehe [Abstraktionen](../../01_Grundlagen/Abstraktionen.md#symmetrie)).

<figure style="text-align:center;">
  <img src="../../../images/p3_halbmodell.excalidraw.png" alt="Rechte Hälfte des Bodenblocks mit halbem Rohr, die Symmetrielinie durch die Rohrachse ist adiabat, die linke Hälfte ist weggelassen" class="no-lightbox">
</figure>

<!-- Klickanleitung nach dem Klicktest einfügen: <tutorial slug="p3-halbmodell"></tutorial> -->

??? tip "Kurzanleitung: zweite Analyse mit eigener Geometrie"
    1. Im Projektmenü `Rechtsklick` auf die Kopfzeile der Analyse a) → `Duplicate`, die Kopie in **b) Halbmodell** umbenennen
    2. `Rechtsklick Geometry (B3) → Edit Geometry in SpaceClaim...`
    3. Mit `Line` eine senkrechte Linie durch den Ursprung zeichnen, von der Oberkante bis zur Unterkante des Blocks. Skizze beenden (`Pull`, Taste `P`): Die Linie teilt Erdreich und Dämmung
    4. Die beiden Flächen **links** der Linie anklicken und mit `Entf` löschen
    5. Im Strukturbaum prüfen: zwei Flächen, **Erdreich** und **Daemmung**. SpaceClaim schließen

??? tip "Kurzanleitung: Mechanical"
    1. `Rechtsklick Model (B4) → Edit...`
    2. Bei beiden Flächen **Thickness** (1 m) und **Assignment** prüfen, nach dem Teilen der Geometrie neu eintragen, wenn nötig
    3. Die Named Selections **Rohr innen** und **Oberflaeche** finden über das Worksheet jetzt die halben Kanten: `Rechtsklick Named Selections → Generate Named Selections`
    4. `Rechtsklick Mesh → Generate Mesh`, dann `Rechtsklick Solution (B6) → Solve`

Die neue senkrechte Kante, die **Symmetrielinie**, bekommt **keine**
Randbedingung: Ohne Randbedingung ist sie adiabat, und genau das ist sie bei
Symmetrie.

<!-- Werte aus tools/sollwerte/p3_fernwaermerohr.py (Halbmodell 3 m × 3 m), im Klicktest durch die ANSYS-Werte ersetzen -->
!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | a) Querschnitt | b) Halbmodell |
    |---|---|---|
    | Reaktion Vorlauf | +19,5 W | **+9,73 W** |
    | Wärmeverlust je Meter Rohr | 19,5 W/m | **2 · 9,73 = 19,5 W/m** |
    | Elemente | | **etwa halb so viele** |

## Was die Zahlen zeigen

- Das Halbmodell liefert **genau die Hälfte** des Wärmestroms. Für das ganze
  Rohr wird die Reaktion **verdoppelt**.
- Es braucht etwa halb so viele Elemente. Bei diesem kleinen 2D-Modell spielt
  das kaum eine Rolle, bei großen 3D-Modellen spart es Stunden.
- Symmetrie gilt nur, wenn **alles** spiegelbildlich ist: Geometrie, Material
  und Randbedingungen. Ob das zutrifft, ist vor jedem Halbmodell zu prüfen,
  siehe [Übung 1](../../03_Selbsttests/Uebung-1.md).

Weiter mit [c) Netzstudie](c-netzstudie.md).
