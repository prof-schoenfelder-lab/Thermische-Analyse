---
title: Zusammenfassung
icon: material/head-snowflake
hide:
  - toc
---

# :material-head-snowflake: Zusammenfassung

In diesem Praktikum wurde die erste thermische Analyse mit ANSYS Workbench
durchgeführt: eine Außenwand, einmal mit vorgegebenen Oberflächentemperaturen
und einmal mit Konvektion.

Die wichtigsten Kernaussagen:

<div class="steps" markdown="1">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Jede Simulation durchläuft dieselben 7 Schritte</p>
    <p>Material, Geometrie, Zuweisung, Netz, Randbedingungen, Lösen, Auswertung</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Ein Freiheitsgrad je Knoten: die Temperatur</p>
    <p>Für stationäre Rechnungen genügt als Materialwert die Wärmeleitfähigkeit λ</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Flächen ohne Randbedingung sind adiabat</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Konvektion ist ein zusätzlicher Widerstand</p>
    <p>Mit Konvektion statt fester Oberflächentemperatur sinkt der Wärmestrom, aus ihm folgt der U-Wert</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Ergebnisse immer auf Plausibilität prüfen</p>
    <p>Bei der ebenen Wand stimmen FEM und Handrechnung exakt überein</p>
  </div>

</div>

Im nächsten Praktikum geht es um alle **Randbedingungen** in ANSYS, darunter die
**Wärmestrahlung**, am Beispiel eines Solarkollektors.
