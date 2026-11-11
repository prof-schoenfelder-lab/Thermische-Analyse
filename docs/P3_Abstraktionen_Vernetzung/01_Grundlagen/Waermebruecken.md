---
title: Wärmebrücken
---

# Wärmebrücken

Eine **Wärmebrücke** ist eine Stelle in der Gebäudehülle, an der mehr Wärme
verloren geht als durch die ungestörte Wand daneben:

- **Geometrisch:** Die Außenfläche ist größer als die Innenfläche, z. B. an
  einer Gebäudeecke ([Praktikum 1, Übung 2](../../P1_Einfuehrung/03_Selbsttests/Uebung-2.md))
- **Konstruktiv:** Ein gut leitendes Bauteil durchstößt die Dämmung, z. B. eine
  Balkonplatte aus Stahlbeton ([Übung 2](../03_Selbsttests/Uebung-2.md))

Eine Wärmebrücke hat zwei Folgen, und für jede gibt es einen Kennwert:

| Folge | Kennwert | Wärmeübergangswiderstand innen |
|---|---|---|
| zusätzlicher Wärmeverlust | längenbezogener Wärmedurchgangskoeffizient $\psi$ | 0,13 m²·K/W an Wänden (DIN EN ISO 6946) |
| kalte Innenoberfläche, Gefahr von Schimmel | Temperaturfaktor $f_{Rsi}$ | 0,25 m²·K/W (DIN 4108-2) |

Beide Kennwerte lassen sich nur mit einer 2D- oder 3D-Rechnung genau bestimmen.
Wie das Modell dafür aussieht, regelt DIN EN ISO 10211.

## Das Modell nach DIN EN ISO 10211

- **Ausschnitt:** Die Wärmebrücke liegt in der Mitte des Modells. Die
  anschließenden Bauteile werden erst im Abstand $d_\mathrm{min}$ abgeschnitten,
  dem größeren Wert von 1 m und der dreifachen Dicke des Bauteils. Liegt eine
  Symmetrieebene näher, darf dort geschnitten werden.
- **Schnitte adiabat:** Die Schnitte bekommen keine Randbedingung. In diesem
  Abstand fließt die Wärme wieder fast nur quer durch das Bauteil, wie in der
  ungestörten Wand, und nicht über den Schnitt.
- **Innen und außen Konvektion** mit $\alpha = 1/R_s$ aus den
  [Normwerten der Bauphysik](../../P2_Randbedingungen/01_Grundlagen/Konvektion.md#normwerte-der-bauphysik-enthalten-strahlung):
  außen $R_{se} = 0{,}04\ \mathrm{m^2\,K/W}$, innen je nach Kennwert wie in
  der Tabelle oben.
- **Verwickelte Bauteile** wie ein Kragplattenanschluss gehen als Ersatzmaterial
  mit $\lambda_{eq}$ ein (siehe [Abstraktionen](Abstraktionen.md#ersatzmaterial)).

mit

- $d_\mathrm{min}$: Mindestabstand der Schnitte von der Wärmebrücke in m
- $R_s$: Wärmeübergangswiderstand in m²·K/W, $R_{si}$ innen und $R_{se}$ außen
- $\alpha$: Wärmeübergangskoeffizient in W/(m²·K)
- $\lambda_{eq}$: äquivalente Wärmeleitfähigkeit in W/(m·K)

## Längenbezogener Wärmedurchgangskoeffizient ψ

Die Rechnung liefert den Wärmestrom durch den ganzen Ausschnitt. Ein Teil davon
ginge auch ohne Wärmebrücke verloren, durch die ungestörte Wand. $\psi$ ist
der Rest, der Zuschlag der Wärmebrücke:

<figure style="text-align:center;">
  <img src="../../images/p3_psi_prinzip.excalidraw.png" alt="Links das 2D-Modell mit Balkonplatte, durch die zusätzlich Wärme fließt, rechts die ungestörte Wand mit derselben Höhe l außen gemessen; psi ist der Leitwert des 2D-Modells minus U mal l" class="no-lightbox">
</figure>

$$
\psi = L_{2D} - \sum_j U_j\,l_j
\qquad\text{mit}\qquad
L_{2D} = \frac{\dot Q'}{T_i - T_e}
$$

mit

- $\psi$: längenbezogener Wärmedurchgangskoeffizient in W/(m·K)
- $L_{2D}$: thermischer Leitwert des 2D-Modells in W/(m·K), der Wärmestrom je
  Meter und je Kelvin Temperaturdifferenz
- $\dot Q'$: Wärmestrom durch das 2D-Modell in W/m, die Reaktion an den
  Innenflächen mit der Dicke 1000 mm
- $T_i$, $T_e$: Lufttemperatur innen und außen in °C
- $U_j$: Wärmedurchgangskoeffizient des ungestörten Bauteils $j$ in W/(m²·K),
  aus der Handrechnung wie in
  [Praktikum 1](../../P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/analytische-loesung.md)
- $l_j$: Länge in m, über die $U_j$ im Modell gilt

Dazu:

- **Eine Innentemperatur:** Die Formel für $L_{2D}$ gilt, wenn alle Räume im
  Modell dieselbe Lufttemperatur haben.
- **Außenmaß:** Die Längen $l_j$ misst man so wie die Flächen im
  Wärmeschutznachweis, in Deutschland mit den Außenmaßen der Gebäudehülle. Das
  Ergebnis heißt dann $\psi_e$ (e für external).
- **Im ganzen Gebäude** verliert die Wärmebrücke zusätzlich
  $\dot Q_\mathrm{WB} = \psi \cdot l_\mathrm{WB} \cdot (T_i - T_e)$, mit dem
  Wärmestrom $\dot Q_\mathrm{WB}$ in W und der Länge $l_\mathrm{WB}$ der
  Wärmebrücke in m, z. B. der Breite des Balkons.

## Temperaturfaktor f<sub>Rsi</sub>

Wie in [Praktikum 1, Übung 2](../../P1_Einfuehrung/03_Selbsttests/Uebung-2.md)
fordert DIN 4108-2 als Mindestwärmeschutz bei 20 °C innen und −5 °C außen:

$$
f_{Rsi} = \frac{T_{si} - T_e}{T_i - T_e} \ge 0{,}70
$$

mit

- $f_{Rsi}$: Temperaturfaktor (1 = so warm wie die Raumluft, 0 = so kalt wie
  draußen)
- $T_{si}$: tiefste Temperatur der Innenoberfläche in °C
- $T_i$, $T_e$: Lufttemperatur innen und außen in °C

In ANSYS ist das innen eine Konvektion mit $\alpha = 1/R_{si} = 4\ \mathrm{W/(m^2\,K)}$.

!!! warning "Zwei Kennwerte, zwei Rechnungen"
    - Für $\psi$ gilt innen $R_{si} = 0{,}13$, für $f_{Rsi}$ dagegen $R_{si} = 0{,}25\ \mathrm{m^2\,K/W}$
    - Der größere Widerstand bildet ab, dass in Ecken und hinter Möbeln weniger Wärme an die Oberfläche kommt. Die Oberfläche wird dadurch kälter, die Prüfung liegt auf der sicheren Seite
    - Wenn beide Kennwerte gesucht sind, braucht es deshalb zwei Rechnungen mit verschiedener Konvektion innen

## Quellen

- DIN EN ISO 10211: Wärmebrücken im Hochbau, Wärmeströme und Oberflächentemperaturen, detaillierte Berechnungen (Ausschnitt, Schnitte, ψ)
- DIN EN ISO 6946: Bauteile, Wärmedurchlasswiderstand und Wärmedurchgangskoeffizient (Wärmeübergangswiderstände)
- DIN 4108-2: Wärmeschutz und Energie-Einsparung in Gebäuden, Mindestanforderungen an den Wärmeschutz (Temperaturfaktor)
