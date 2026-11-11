---
title: Vernetzung
---

# Vernetzung

Das Netz zerlegt das Modell in Elemente, die über Knoten verbunden sind (siehe
[Grundprinzip der FEM](../../P1_Einfuehrung/01_Grundlagen/Grundprinzipien-FEM.md)).
In der Außenwand aus Praktikum 1 war das Netz Nebensache: Die Temperatur
verläuft dort je Schicht linear, und das gibt schon ein grobes Netz exakt wieder.
Um ein Rohr, an einer Ecke oder an einer Wärmebrücke verläuft sie gekrümmt.
Dann hängt das Ergebnis vom Netz ab, und ob es fein genug ist, sieht man dem
Ergebnisbild nicht an. Das zeigt erst eine **Netzstudie**.

## Netz und Elemente

- **Elementform:** In 2D besteht das Netz aus Vierecken und Dreiecken, in 3D
  aus Hexaedern (Quadern) und Tetraedern.
- **Mittelknoten:** ANSYS Mechanical setzt standardmäßig auch in die Mitte jeder
  Elementkante einen Knoten. Die Temperatur verläuft im Element dann als Parabel
  statt als Gerade, und die Kanten schmiegen sich an runde Ränder wie das Rohr an.
- **Elementgröße:** die ungefähre Kantenlänge der Elemente. In Mechanical:
  `Strukturbaum Mesh` anklicken, dann `Detailfenster → Element Size`.

<!-- Im Klicktest prüfen: Element Order steht auf Program Controlled und ergibt im 2D-Modell Elemente mit Mittelknoten (Mesh → Statistics, Knoten gegen Elemente) -->

## Was ANSYS aus dem Netz rechnet

Unbekannt sind nur die Temperaturen an den Knoten. Alle anderen Ergebnisse
leitet ANSYS daraus ab:

| Ergebnis | So bestimmt ANSYS es |
|---|---|
| Temperatur | direkt an jedem Knoten, im Element dazwischen ergänzt |
| Wärmestromdichte | aus dem Gefälle der Temperatur im Element |
| Wärmestrom an einem Rand (Reaktion) | als Summe der Knotenwärmeströme über alle Knoten des Randes |

Die Wärmestromdichte folgt aus dem Fourierschen Gesetz:

$$
\dot{\vec q} = -\lambda\,\operatorname{grad} T
$$

mit

- $\dot{\vec q}$: Wärmestromdichte in W/m²
- $\lambda$: Wärmeleitfähigkeit in W/(m·K)
- $\operatorname{grad} T$: Gefälle der Temperatur in K/m

## Netzstudie: halbieren, bis sich nichts mehr ändert

Bei einer Netzstudie (auch Sensitivitätsanalyse) rechnet man dasselbe Modell mit
immer kleineren Elementen und vergleicht das Ergebnis:

<figure style="text-align:center;">
  <img src="../../images/p3_netzstudie_ablauf.excalidraw.png" alt="Schleife: Modell mit Startnetz rechnen, Elementgröße halbieren und rechnen, bis sich das Ergebnis um weniger als 1 % ändert, erst überall, dann im Dämmring" class="no-lightbox">
</figure>

Nach jeder Halbierung wird die Änderung gegenüber dem vorigen Netz bestimmt:

$$
\Delta = \left|\frac{x_\mathrm{neu} - x_\mathrm{alt}}{x_\mathrm{neu}}\right| \cdot 100\ \%
$$

mit

- $\Delta$: Änderung in %
- $x_\mathrm{neu}$: Ergebnis mit der halbierten Elementgröße
- $x_\mathrm{alt}$: Ergebnis mit der Elementgröße davor

Ändert sich das Ergebnis um weniger als etwa 1 %, gilt es als **konvergiert**:
Ein noch feineres Netz ändert es kaum noch.

- **Jede Größe getrennt:** Wenn mehrere Ergebnisse gebraucht werden, muss jedes
  für sich die 1 % erreichen. Ein Netz, das für die Temperatur reicht, reicht
  nicht automatisch für die Wärmestromdichte.
- **Gefälle braucht mehr:** Die Temperatur rechnet die FEM direkt, die
  Wärmestromdichte kommt aus ihrer Ableitung. Wenn ein Ergebnis aus dem Gefälle
  kommt, konvergiert es deshalb in der Regel langsamer als die Temperatur.
- **Aufwand:** Jede Halbierung macht in 2D etwa 4-mal so viele Elemente, in 3D
  etwa 8-mal so viele.

## Global oder lokal verfeinern

| | Global | Lokal |
|---|---|---|
| Einstellung | `Strukturbaum Mesh → Detailfenster → Element Size` | `Rechtsklick Mesh → Insert → Sizing` auf einen Körper, eine Kante oder einen Punkt |
| Wirkt | überall im Modell | nur in der Auswahl, der Rest bleibt grob |
| Elemente je Halbierung (2D) | überall etwa 4-mal so viele | nur in der Auswahl etwa 4-mal so viele |

- Wenn sich die Temperatur überall im Modell ähnlich stark ändert, reicht es,
  global zu verfeinern.
- Wenn sie sich in einem kleinen Bereich stark ändert und im Rest kaum, erreicht
  man dieselbe Genauigkeit mit lokaler Verfeinerung und viel weniger Elementen.
- Wo sich die Temperatur stark ändert, zeigt schon ein erster Lauf: Dort liegen
  die Farbbänder der Temperatur eng beieinander, und die Wärmestromdichte ist
  hoch.

Beim Fernwärmerohr liegt der größte Teil des Temperaturabfalls im 40 mm dicken
Dämmring (siehe [Abstraktionen](Abstraktionen.md#schichten-weglassen)). In
[c) Netzstudie](../02_Vorzeigebeispiel/Fernwaermerohr/c-netzstudie.md) wird das
Netz deshalb erst überall und dann nur im Dämmring verfeinert.

<!-- Nach dem Klicktest: zwei Netzbilder aus ANSYS nebeneinander, global 50 mm und global 200 mm mit 10 mm im Dämmring -->
