---
title: Abstraktionen
---

# Abstraktionen

Ein FE-Modell bildet nicht das ganze Bauteil ab, sondern so viel, wie die
gesuchte Größe braucht. In diesem Praktikum kommen vier Abstraktionen vor:

- **3D zu 2D:** lange Bauteile mit gleichem Querschnitt im Schnitt rechnen
- **Symmetrie:** nur eine Hälfte rechnen, wenn beide Hälften gleich sind
- **Rotationssymmetrie:** einen Drehkörper als Halbschnitt rechnen
- **Weglassen und Ersatzwerte:** Schichten ohne Gewicht weglassen, verwickelte
  Bauteile durch ein Ersatzmaterial ersetzen

Alle vier sparen Elemente und Rechenzeit. Sie gelten aber nur unter
Bedingungen, die man vorher prüft.

## Von 3D zu 2D

Wenn ein Bauteil lang ist, überall den gleichen Querschnitt hat und die Wärme
nur quer zur Länge fließt, ändert sich die Temperatur entlang der Länge nicht.
Dann reicht der Querschnitt als 2D-Modell. Beispiele sind das Fernwärmerohr im
Erdreich, eine Wand oder eine Balkonplatte im Schnitt.

<figure style="text-align:center;">
  <img src="../../images/p3_fernwaermerohr.excalidraw.png" alt="Bodenblock 6 m mal 3 m mit dem Fernwärmerohr 0,9 m unter der Oberfläche, rechts das Rohr im Modell vergrößert" class="no-lightbox">
  <figcaption>Fernwärmerohr im Erdreich als 2D-Querschnitt (Vorzeigebeispiel)</figcaption>
</figure>

Das 2D-Modell steht für eine Scheibe mit einer bestimmten Dicke. ANSYS rechnet
den Wärmestrom durch genau diese Scheibe:

- Mit der Dicke **1000 mm** ist der Wärmestrom direkt der Wert **je Meter**
  Länge, also in W/m.
- In ANSYS steht die Dicke bei der Fläche: Fläche im Strukturbaum auswählen,
  dann `Detailfenster → Thickness`.

Wie viel 2D spart, zeigt der Vergleich mit einem 1000 mm langen 3D-Stück
desselben Rohrs, bei gleicher Netzfeinheit am Rohr:

<!-- Zahlen aus tools/sollwerte/p3_3d_vergleich.py, im Klicktest durch die ANSYS-Werte ersetzen -->
| Modell | Wärmeverlust | Elemente |
|---|---|---|
| 2D-Querschnitt | 19,41 W/m | 1 766 |
| 3D-Stück, 1000 mm lang | 19,43 W/m | 61 341 |

Der Wärmeverlust ist gleich, das 3D-Modell braucht aber 35-mal so viele
Elemente.

## Symmetrie

Ist ein Modell spiegelbildlich zu einer Linie, reicht eine Hälfte. Dafür müssen
beim Spiegeln drei Dinge gleich bleiben:

- [ ] Geometrie
- [ ] Material
- [ ] Randbedingungen

Dann ist auch das Temperaturfeld spiegelbildlich. Auf der Symmetrielinie hat es
deshalb kein Gefälle quer zur Linie, und ohne Gefälle fließt keine Wärme
hindurch: Die Symmetrielinie ist **adiabat**. In ANSYS bekommt sie einfach
**keine** Randbedingung, denn Ränder ohne Randbedingung sind schon adiabat
(siehe [Praktikum 2](../../P2_Randbedingungen/01_Grundlagen/Randbedingungen.md)).

<figure style="text-align:center;">
  <img src="../../images/p3_halbmodell.excalidraw.png" alt="Rechte Hälfte des Bodenblocks mit halbem Rohr, die Symmetrielinie durch die Rohrachse ist adiabat, die linke Hälfte ist weggelassen" class="no-lightbox">
  <figcaption>Halbmodell des Fernwärmerohrs</figcaption>
</figure>

- ANSYS rechnet nur die Hälfte. Der Wärmestrom des ganzen Modells ist der
  **doppelte** Wert.
- Das Halbmodell braucht etwa halb so viele Elemente.

## Rotationssymmetrie

Entsteht ein Körper, indem man einen Querschnitt um eine Achse dreht, und ist
rundum alles gleich, reicht dieser Querschnitt als 2D-Modell: der **Halbschnitt**
von der Achse bis zum Rand. Ein Beispiel ist der
[Pufferspeicher](../02_Vorzeigebeispiel/Fernwaermerohr/d-pufferspeicher.md) im
Vorzeigebeispiel.

<figure style="text-align:center;">
  <img src="../../images/p3_pufferspeicher.excalidraw.png" alt="Halbschnitt eines Pufferspeichers rechts der Drehachse: Wasser 65 °C, Dämmung an Deckel, Mantel und Boden, außen Raumluft" class="no-lightbox">
  <figcaption>Pufferspeicher im Halbschnitt</figcaption>
</figure>

Rundum gleich sein müssen wieder Geometrie, Material und Randbedingungen:

- **Geht:** alles, was im Halbschnitt liegt, z. B. verschiedene Dämmdicken an
  Mantel, Deckel und Boden oder ein Anschluss genau auf der Achse
- **Geht nicht:** alles, was nur an einer Stelle des Umfangs sitzt, z. B.
  seitliche Anschlüsse oder die Füße eines Speichers

In ANSYS:

- Die Drehachse ist immer die **y-Achse**, x ist der Radius. Der Halbschnitt
  liegt rechts der Achse.
- In Mechanical `Geometry` auswählen, dann
  `Detailfenster → 2D Behavior: Axisymmetric`. Eine Dicke gibt es dann nicht.
- Die Achse braucht keine Randbedingung.
- Wärmeströme gibt ANSYS für den ganzen Umfang (360°) aus.

## Weglassen und Ersatzwerte

### Schichten weglassen

Eine Schicht darf weg, wenn sie kaum zum Wärmewiderstand beiträgt. Ob das so
ist, zeigt eine Handrechnung vorab. Beim Fernwärmerohr liegen die Schichten wie
Widerstände in Reihe, jede Schicht ein Hohlzylinder, dazu das Erdreich:

$$
R_\mathrm{Schicht} = \frac{\ln(r_a/r_i)}{2\pi\,\lambda}
\qquad
R_\mathrm{Erdreich} = \frac{\operatorname{arcosh}(2H/D)}{2\pi\,\lambda_E}
$$

mit

- $R$: Wärmewiderstand je Meter Rohr in m·K/W
- $r_a$, $r_i$: Außen- und Innenradius der Schicht
- $\lambda$: Wärmeleitfähigkeit der Schicht in W/(m·K)
- $H$: Tiefe der Rohrachse unter der Oberfläche
- $D$: Außendurchmesser des Rohrs
- $\lambda_E$: Wärmeleitfähigkeit des Erdreichs in W/(m·K)

Die Anteile am gesamten Widerstand:

| Schicht | Anteil am Widerstand |
|---|---|
| Dämmung (PUR) | 86,8 % |
| Erdreich | 12,8 % |
| PE-Mantel | 0,4 % |
| Stahlrohr | 0,0 % |

Stahlrohr und PE-Mantel tragen zusammen 0,4 % bei. Im Modell fallen sie weg:
Die 80 °C liegen direkt an der Innenseite der Dämmung, und das Erdreich schließt
direkt an die Dämmung an. Der Wärmeverlust ändert sich dadurch um 0,2 %.

### Ersatzmaterial

Manche Bauteile bestehen aus vielen kleinen Teilen, z. B. ein
Kragplattenanschluss aus Stahlstäben in einem Dämmkörper. Statt jedes Teil zu
modellieren, bekommt der ganze Körper eine **äquivalente Wärmeleitfähigkeit**
$\lambda_{eq}$, die der Hersteller angibt. So rechnet
[Übung 2](../03_Selbsttests/Uebung-2.md) die Balkonplatte mit thermischer
Trennung.
