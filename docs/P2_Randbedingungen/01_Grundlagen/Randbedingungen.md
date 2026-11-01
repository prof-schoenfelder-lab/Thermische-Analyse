---
title: Randbedingungen im Überblick
---

# Randbedingungen im Überblick

Randbedingungen beantworten die Frage: **Wo kommt die Wärme her, und wo geht
sie hin?** Nach dem Ort, an dem sie wirken, gibt es drei Gruppen. Die Bilder
stammen aus dem Vorzeigebeispiel und aus Übung 3.

<figure style="text-align:center;">
  <img src="../../images/p2_rb_gruppen.excalidraw.png" alt="Drei Gruppen von Randbedingungen: an der Systemgrenze, im ganzen Körper, überall" class="no-lightbox">
</figure>

## An der Systemgrenze

Wärme geht über die Oberfläche in das Modell hinein oder aus ihm heraus. Dazu
gehören die meisten Randbedingungen:

| Randbedingung | ANSYS | Eingabe | Beispiel in diesem Praktikum |
|---|---|---|---|
| Konvektion | `Convection` | W/(m²·K) und °C | Wasser im Rohr, Luft außen (alle) |
| Strahlung | `Radiation` | ε und °C | Glas zum Himmel, Absorber zum Glas (Vorzeigebeispiel) |
| Wärmestromdichte | `Heat Flux` | W/m² | Sonne auf dem Absorber (Vorzeigebeispiel) |
| Wärmestrom | `Heat Flow` | W | Verlustleistung eines Halbleiters (Übung 2) |
| Isoliert | `Perfectly Insulated` | | Seiten des Erdreichs (Übung 3) |

`Heat Flux` passt, wenn die Leistung **je Fläche** bekannt ist, wie bei der
Sonne. `Heat Flow` passt, wenn die **Gesamtleistung** bekannt ist, etwa aus
einem Datenblatt.

## Im ganzen Körper

Die Wärme entsteht im Material selbst, zum Beispiel durch elektrischen Strom.
`Internal Heat Generation` gibt die Leistung je Volumen in W/m³ vor und wird
auf einen ganzen Körper gesetzt, etwa auf den Leiter des Erdkabels (Übung 3).

## Überall: feste Temperatur

`Temperature` hält die Temperatur in °C fest, auf einer Fläche, einer Kante,
einem Punkt oder einem ganzen Körper. Das passt nur, wenn der Ort seine
Temperatur wirklich behält, egal wie viel Wärme fließt: tiefes Erdreich
(Übung 3), siedendes oder kondensierendes Wasser. An einer Oberfläche zur Luft
ist eine feste Temperatur meist falsch (siehe Praktikum 1, Fall a).

## Was vorgegeben wird, was herauskommt

Jede Randbedingung legt **eine** Größe am Rand fest, die andere rechnet ANSYS aus:

- **Temperatur:** Die Temperatur steht fest, der Wärmestrom über die Fläche ist Ergebnis.
- **Wärmestrom, Wärmestromdichte, Isoliert:** Der Wärmestrom steht fest, die Temperatur der Fläche ist Ergebnis.
- **Konvektion und Strahlung:** Weder Temperatur noch Wärmestrom stehen fest. Vorgegeben ist ein **Gesetz**, das beide verknüpft. Je wärmer die Fläche, desto mehr Wärme gibt sie ab.

## Zwei Randbedingungen auf derselben Fläche

Konvektion und Strahlung wirken an einer Oberfläche immer gleichzeitig. In
ANSYS setzt man dafür einfach **beide** auf dieselbe Fläche: Ihre
Wärmeströme addieren sich. Das gilt für alle Randbedingungen, die einen
Wärmestrom beschreiben. Eine **Temperatur** dagegen schlägt alles andere auf
der Fläche: Mit fester Temperatur sind Konvektion oder Strahlung dort wirkungslos.

## Flächen ohne Randbedingung

Freie Flächen sind in ANSYS automatisch **isoliert** (adiabat): Über sie
fließt keine Wärme. `Perfectly Insulated` muss man also nicht setzen, es macht
die Annahme aber im Strukturbaum sichtbar. Isoliert ist richtig, wenn

- die Fläche wirklich gedämmt ist, oder
- der Modellrand **weit genug** von der Wärmequelle entfernt ist, oder
- es eine Schnittfläche in einem langen Bauteil ist, über die nichts fließt
  (wie die Stirnflächen eines Rohrstücks).

## Wie viel Wärme geht über eine Randbedingung?

Jede Randbedingung kann man nach der Rechnung fragen, wie viel Wärme über sie
geflossen ist: Die Randbedingung mit gedrückter Maustaste auf **Solution**
ziehen. ANSYS legt eine **Reaction Probe** an, nach `Evaluate All Results`
steht der Wärmestrom in W im Detailfenster.

- **Vorzeichen:** positiv heißt, Wärme geht über diese Randbedingung **in** das
  Modell, negativ heißt, sie verlässt das Modell.
- **Energiebilanz:** Im stationären Zustand ist die Summe aller Reaktionen null.
  Das ist die schnellste Kontrolle, ob alle Randbedingungen richtig sitzen.
