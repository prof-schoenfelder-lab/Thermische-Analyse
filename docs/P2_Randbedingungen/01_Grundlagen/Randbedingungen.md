---
title: Randbedingungen im Überblick
---

# Randbedingungen im Überblick

Randbedingungen beantworten die Frage: **Wo kommt die Wärme her, und wo geht
sie hin?** Nach dem Ort, an dem sie wirken, gibt es zwei Gruppen: an der
Systemgrenze und im ganzen Körper. Die Bilder
zeigen die [Vakuumröhre eines Solarkollektors](../02_Vorzeigebeispiel/Vakuumroehre/index.md)
aus dem Vorzeigebeispiel und das [Erdkabel im Windpark](../03_Selbsttests/Uebung-3.md)
aus Übung 3.

<figure style="text-align:center;">
  <img src="../../images/p2_rb_gruppen.excalidraw.png" alt="Randbedingungen an der Systemgrenze und im ganzen Körper" class="no-lightbox">
</figure>

## An der Systemgrenze

Wärme geht über die Oberfläche in das Modell hinein oder aus ihm heraus, oder
die Temperatur der Oberfläche steht fest. Dazu gehören alle Randbedingungen
außer der Wärmeerzeugung:

<figure style="text-align:center;">
  <img src="../../images/p2_rb_anwendung.excalidraw.png" alt="Wann welche Randbedingung an der Systemgrenze passt: Konvektion, Strahlung, Wärmestromdichte, Wärmestrom" class="no-lightbox">
</figure>

| Randbedingung | Anwendung | Beispiel in diesem Praktikum | in ANSYS (Eingabe) |
|---|---|---|---|
| Konvektion | Fluide bewegen sich entlang einer Grenzfläche | Wasser im Rohr, Luft außen (alle) | `Convection`<br>W/(m²·K) und °C |
| Strahlung | Flächen sehen andere Flächen oder die Umgebung, durch Luft oder Vakuum | Glas zum Himmel, Absorber zum Glas (Vorzeigebeispiel) | `Radiation`<br>ε und °C |
| Wärmestromdichte | Leistung je Fläche ist bekannt und hängt nicht von der Temperatur der Fläche ab | Sonne auf dem Absorber (Vorzeigebeispiel) | `Heat Flux`<br>W/m² |
| Wärmestrom | Gesamtleistung über eine Fläche ist bekannt, z. B. aus einem Datenblatt | Verlustleistung eines Halbleiters (Übung 2) | `Heat Flow`<br>W |
| Feste Temperatur | Festkörper werden geschnitten, und an der Schnittfläche ist die Temperatur bekannt | Erdreich in 3 m Tiefe (Übung 3) | `Temperature`<br>°C |

### Feste Temperatur

**Anwendung:** Festkörper werden geschnitten, und an der Schnittfläche ist die
Temperatur bekannt, z. B. das Erdreich in 3 m Tiefe (Übung 3). Das passt nur,
wenn die Temperatur dort fest bleibt, egal wie viel Wärme fließt. An einer
Oberfläche zur Luft ist eine feste Temperatur meist falsch (siehe Praktikum 1,
Fall a).

<figure style="text-align:center;">
  <img src="../../images/p2_rb_schnitt.excalidraw.png" alt="Schnitt durch Erdreich und Rohr: feste Temperatur, wo sie bekannt ist, sonst frei lassen" class="no-lightbox">
  <figcaption>Wo das Modell einen Festkörper schneidet: feste Temperatur oder frei lassen</figcaption>
</figure>

In ANSYS hält `Temperature` die Temperatur in °C fest. Setzen lässt sie sich
auch auf Kanten, Punkte oder ganze Körper, gebraucht wird sie aber an Flächen
der Systemgrenze. In 2D-Modellen (Praktikum 3) sind das Kanten.

## Im ganzen Körper: Wärmeerzeugung

**Anwendung:** Wärme entsteht im Material selbst, z. B. durch elektrischen
Strom im Leiter des Erdkabels (Übung 3).

In ANSYS gibt `Internal Heat Generation` die Leistung je Volumen in W/m³ vor
und wird auf einen ganzen Körper gesetzt.

## Was vorgegeben wird, was herauskommt

Jede Randbedingung legt **eine** Größe am Rand fest, die andere rechnet ANSYS aus:

<figure style="text-align:center;">
  <img src="../../images/p2_rb_kennlinien.excalidraw.png" alt="Wärmestrom über Temperatur der Fläche: feste Temperatur senkrecht, fester Wärmestrom waagerecht, Konvektion und Strahlung als Kennlinien" class="no-lightbox">
  <figcaption>Beispiel: Luft und Umgebung 20&nbsp;°C, α&nbsp;=&nbsp;10&nbsp;W/(m²·K), ε&nbsp;=&nbsp;0,9</figcaption>
</figure>

- **Temperatur:** Die Temperatur steht fest, der Wärmestrom über die Fläche ist Ergebnis.
- **Wärmestrom, Wärmestromdichte:** Der Wärmestrom steht fest, die Temperatur der Fläche ist Ergebnis.
- **Konvektion und Strahlung:** Weder Temperatur noch Wärmestrom stehen fest. Vorgegeben ist ein **Gesetz**, das beide verknüpft. Je wärmer die Fläche, desto mehr Wärme gibt sie ab.

## Zwei Randbedingungen auf derselben Fläche

Konvektion und Strahlung wirken an einer Oberfläche immer gleichzeitig. In
ANSYS setzt man dafür einfach **beide** auf dieselbe Fläche: Ihre
Wärmeströme addieren sich (im Bild oben die Linie „beide zusammen“). Das gilt für alle Randbedingungen, die einen
Wärmestrom beschreiben. Eine **Temperatur** dagegen schlägt alles andere auf
der Fläche: Mit fester Temperatur sind Konvektion oder Strahlung dort wirkungslos.

## Flächen ohne Randbedingung

Freie Flächen sind in ANSYS automatisch **isoliert** (adiabat): Über sie
fließt keine Wärme. Das ist richtig, wenn

- die Fläche wirklich gedämmt ist, oder
- der Modellrand **weit genug** von der Wärmequelle entfernt ist, oder
- es eine Schnittfläche in einem langen Bauteil ist, über die nichts fließt
  (wie die Stirnflächen eines Rohrstücks, Bild oben bei der festen Temperatur).

!!! info "Hinweis: Isoliert muss man nicht setzen"
    - Jede Fläche ohne Randbedingung ist schon isoliert
    - In ANSYS gibt es dafür zwar `Perfectly Insulated`, das braucht man aber nur in einem Fall: Eine Last sitzt auf einem ganzen Körper, und einzelne Flächen sollen davon ausgenommen werden
    - Beispiel: Konvektion auf dem ganzen Körper, nur die Standfläche liegt auf und gibt keine Wärme ab

## Wie viel Wärme geht über eine Randbedingung?

Bei Temperatur, Konvektion und Strahlung zur Umgebung rechnet ANSYS aus, wie
viel Wärme über die Randbedingung geflossen ist: Die Randbedingung mit
gedrückter Maustaste auf **Solution** ziehen. ANSYS legt eine
**Reaction Probe** an, nach `Evaluate All Results` steht der Wärmestrom in W
im Detailfenster. Bei Wärmestromdichte, Wärmestrom und Wärmeerzeugung ist der
Wärmestrom vorgegeben: Wert mal Fläche oder Volumen. Eine Reaction Probe
braucht es dafür nicht, für `Heat Flux` bietet ANSYS auch keine an.

- **Vorzeichen:** positiv heißt, Wärme geht über diese Randbedingung **in** das
  Modell, negativ heißt, sie verlässt das Modell.
- **Energiebilanz:** Im stationären Zustand ergeben die vorgegebenen
  Wärmeströme und alle Reaktionen zusammen null.
  Das ist die schnellste Kontrolle, ob alle Randbedingungen richtig sitzen.
