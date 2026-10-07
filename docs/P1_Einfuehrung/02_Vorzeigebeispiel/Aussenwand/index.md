---
title: "Vorzeigebeispiel: Außenwand"
icon: material/help-box
---

# Vorzeigebeispiel: Außenwand mit Wärmedämmung

<div class="task-tabs-src" data-tabs="Aufgabe=./|a) Temperaturen=01-material/|b) Konvektion=b-konvektion/|Analytische Lösung=analytische-loesung/" hidden></div>

Wie viel Wärme geht durch eine gedämmte Außenwand verloren, und wie warm ist
die Wand innen? Das Beispiel ist bewusst einfach: Die Temperatur ändert sich
nur über die Wanddicke (eindimensional). Dafür gibt es eine exakte
Handrechnung, mit der wir die FEM-Ergebnisse prüfen können.

!!! question "Die Aufgabe"
    Eine **Steady-State-Thermal**-Analyse in ANSYS Workbench anlegen und für die
    gegebene Wand den **Temperaturverlauf** und die **Wärmestromdichte** von innen
    nach außen bestimmen, und zwar für zwei Arten von Randbedingungen:

    - **a)** vorgegebene **Oberflächentemperaturen**
    - **b)** **Konvektion** an Raumluft und Außenluft, daraus der **U-Wert**

<div class="grid" markdown>

<figure style="text-align:center;">
  <img src="../../images/p1_aussenwand_a.svg" alt="Fall a: Oberflächentemperaturen" style="width:100%">
  <figcaption>Fall a) Oberflächentemperaturen</figcaption>
</figure>

<figure style="text-align:center;">
  <img src="../../images/p1_aussenwand_b.svg" alt="Fall b: Konvektion" style="width:100%">
  <figcaption>Fall b) Konvektion</figcaption>
</figure>

</div>

## Gegeben

### Material

<!-- --8<-- [start:Material] -->
| Schicht | Wärmeleitfähigkeit |
|---|---|
| Kalksandstein (innen) | $\lambda_{KS} = 0{,}99\ \mathrm{W/(m\,K)}$ |
| EPS-Dämmung (außen) | $\lambda_{EPS} = 0{,}035\ \mathrm{W/(m\,K)}$ |

Beide isotrop (*Isotropic Thermal Conductivity*).
<!-- --8<-- [end:Material] -->

### Geometrie

<!-- --8<-- [start:Geometrie] -->
Wandausschnitt **100 mm × 100 mm**, zwei Schichten:

- Kalksandstein $d_{KS} = 175\ \mathrm{mm}$
- EPS-Dämmung $d_{EPS} = 140\ \mathrm{mm}$

Beide Körper teilen sich die Fläche in der Trennfuge (**Share Topology**).
<!-- --8<-- [end:Geometrie] -->

### Vernetzung

<!-- --8<-- [start:Vernetzung] -->
- Netzgröße global: 10 mm
<!-- --8<-- [end:Vernetzung] -->

### Randbedingungen

<!-- --8<-- [start:Randbedingungen_a] -->
Fall a) Oberflächentemperaturen

- Innenseite (Kalksandstein): $T_i = 20\ \mathrm{°C}$
- Außenseite (EPS): $T_e = -10\ \mathrm{°C}$
<!-- --8<-- [end:Randbedingungen_a] -->

<!-- --8<-- [start:Randbedingungen_b] -->
Fall b) Konvektion

- Innenseite: Raumluft $T_i = 20\ \mathrm{°C}$, Wärmeübergangskoeffizient $h_i = 7{,}7\ \mathrm{W/(m^2\,K)}$
- Außenseite: Außenluft $T_e = -10\ \mathrm{°C}$, $h_e = 25\ \mathrm{W/(m^2\,K)}$
<!-- --8<-- [end:Randbedingungen_b] -->

Alle übrigen Flächen sind adiabat (keine Randbedingung nötig).

## Gesucht

<!-- --8<-- [start:Gesucht] -->
1. Temperaturverlauf über die Wanddicke
2. Wärmestromdichte $\dot q$ in W/m² (= Wärmeverlust je m² Wand)
3. Temperatur in der Trennfuge zwischen Kalksandstein und Dämmung
4. Fall b) zusätzlich: Oberflächentemperatur innen und U-Wert $U = \dot q / (T_i - T_e)$
<!-- --8<-- [end:Gesucht] -->

## Lösungswege

<div class="grid cards" markdown>

-   <a class="card-link" href="01-material/">
    __a) Temperaturen__: der komplette Ablauf in 7 Schritten
    </a>

-   <a class="card-link" href="b-konvektion/">
    __b) Konvektion__: Randbedingungen tauschen, U-Wert bestimmen
    </a>

-   <a class="card-link" href="analytische-loesung/">
    __Analytische Lösung__: Handrechnung zum Vergleich
    </a>

</div>
