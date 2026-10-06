---
title: Simulationssoftware
icon: material/alpha-a-box
hide:
  - toc
---

# Simulationssoftware

Wir verwenden **ANSYS Workbench 2025 R2**. Workbench verbindet mehrere Programme
zu einem Ablauf:

| Programm | Aufgabe |
|---|---|
| **Workbench** (Projektmenü) | Analysen anlegen, Materialien definieren (Engineering Data) |
| **SpaceClaim** | Geometrie erstellen und vereinfachen |
| **Mechanical** | Vernetzen, Randbedingungen, Lösen, Auswerten |

Für die Wärmeleitung gibt es zwei Analysesysteme:

- **Steady-State Thermal**: stationär, die Temperaturen ändern sich nicht mehr mit der Zeit (Praktikum 1 bis 3)
- **Transient Thermal**: zeitabhängig, z. B. Aufheizen oder Abkühlen (Praktikum 4 und 5)

<div class="steps" markdown="1" data-kategorie="Setup">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Start von ANSYS Workbench</p>
    <p>Im Windows-Startmenü unter Lehre auf <code>ANSYS Workbench 2025 R2</code> klicken</p>
  </div>

</div>

!!! warning "Einheiten in Mechanical"
    Die Werte in diesem Kurs sind in **m** und **°C** angegeben. In Mechanical
    deshalb das Einheitensystem **Metric (m, kg, N, s, V, A)** wählen (unten in
    der Statusleiste). Sonst erscheint die Wärmestromdichte in W/mm², also um den
    Faktor 10⁶ kleiner.

Der weitere Ablauf folgt im Vorzeigebeispiel.
