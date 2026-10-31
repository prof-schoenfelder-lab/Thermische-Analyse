---
title: Randbedingungen im Überblick
---

# Randbedingungen im Überblick

Eine thermische Rechnung braucht neben Geometrie und Material immer die
Antwort auf die Frage: **Wo kommt die Wärme her, und wo geht sie hin?** Genau
das beschreiben die Randbedingungen. ANSYS bietet in der stationären Analyse
(Steady-State Thermal) sieben Arten an:

| Randbedingung | ANSYS | Einheit | wirkt auf | Beispiel in diesem Praktikum |
|---|---|---|---|---|
| Temperatur | `Temperature` | °C | Fläche, Kante, Punkt, Körper | Erdreich in 3 m Tiefe (Übung 3) |
| Konvektion | `Convection` | W/(m²·K) und °C | Fläche | Wasser im Rohr, Luft außen (alle) |
| Strahlung | `Radiation` | ε und °C | Fläche | Glas zum Himmel, Absorber zum Glas (Vorzeigebeispiel) |
| Wärmestrom | `Heat Flow` | W | Fläche, Kante, Punkt | Verlustleistung eines Halbleiters (Übung 2) |
| Wärmestromdichte | `Heat Flux` | W/m² | Fläche | Sonne auf dem Absorber (Vorzeigebeispiel) |
| Isoliert | `Perfectly Insulated` | | Fläche | Seiten des Erdreichs (Übung 3) |
| Wärmeerzeugung | `Internal Heat Generation` | W/m³ | Körper | Stromwärme im Kabelleiter (Übung 3) |

## Was vorgegeben wird, was herauskommt

Jede Randbedingung legt **eine** Größe am Rand fest, die andere rechnet ANSYS aus:

- **Temperatur:** Die Temperatur steht fest, der Wärmestrom über die Fläche ist Ergebnis.
- **Wärmestrom, Wärmestromdichte, Isoliert:** Der Wärmestrom steht fest, die Temperatur der Fläche ist Ergebnis.
- **Konvektion und Strahlung:** Weder Temperatur noch Wärmestrom stehen fest. Vorgegeben ist ein **Gesetz**, das beide verknüpft. Je wärmer die Fläche, desto mehr Wärme gibt sie ab.

!!! abstract "Wann welche Randbedingung?"
    - Eine feste **Temperatur** passt nur, wenn der Rand seine Temperatur
      wirklich behält, egal wie viel Wärme fließt: tiefes Erdreich, siedendes
      oder kondensierendes Wasser. An einer Oberfläche zur Luft ist sie meist
      falsch (siehe Praktikum 1, Fall a).
    - **Wärmestrom** (W), wenn die **Gesamtleistung** bekannt ist, z. B. die
      Verlustleistung aus einem Datenblatt.
    - **Wärmestromdichte** (W/m²), wenn die Leistung **je Fläche** bekannt
      ist, z. B. die Sonneneinstrahlung.
    - **Wärmeerzeugung** (W/m³), wenn die Wärme **im Körper** entsteht, z. B.
      durch elektrischen Strom.

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
