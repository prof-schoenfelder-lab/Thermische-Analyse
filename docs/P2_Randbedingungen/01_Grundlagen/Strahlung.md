---
title: Wärmestrahlung
---

# Wärmestrahlung

Jeder Körper strahlt Wärme ab, und zwar umso mehr, je wärmer er ist. Anders als
Wärmeleitung und Konvektion braucht Strahlung kein Medium: Sie geht auch durch
Vakuum. So kommt die Sonnenwärme zur Erde.

## Stefan-Boltzmann-Gesetz

Eine Fläche mit der Temperatur $T$ strahlt je Quadratmeter

$$
\dot q = \varepsilon\,\sigma\,T^4
\qquad \text{mit} \qquad \sigma = 5{,}67 \cdot 10^{-8}\ \mathrm{W/(m^2\,K^4)}
$$

ab, mit

- $\dot q$: abgestrahlte Wärmestromdichte in W/m²
- $\varepsilon$: Emissionsgrad der Fläche, 0 bis 1 (Abschnitt Emissionsgrad)
- $\sigma$: Stefan-Boltzmann-Konstante
- $T$: **absolute Temperatur** der Fläche in Kelvin. ANSYS rechnet das selbst um,
  Eingaben bleiben in °C.

Die vierte Potenz macht die Rechnung **nichtlinear**: ANSYS braucht mehrere
Durchläufe (Iterationen), bis die Lösung steht. Das sieht man in
`Solution Information`.

Was eine Fläche abstrahlt, bekommt sie zum Teil von ihrer Umgebung zurück.
Netto zählt der Unterschied:

$$
\dot q = \varepsilon\,\sigma\,\left(T^4 - T_\infty^4\right)
$$

mit der absoluten Temperatur $T_\infty$ der Umgebung, die die Strahlung empfängt.

## Emissionsgrad

Der Emissionsgrad $\varepsilon$ (0 bis 1) sagt, wie gut eine Fläche strahlt,
verglichen mit dem idealen schwarzen Körper. Er ist eine Eigenschaft der
**Oberfläche**, nicht des Materials darunter:

| Oberfläche | ε |
|---|---|
| blankes Aluminium, poliertes Kupfer | 0,03 bis 0,05 |
| selektive Absorberbeschichtung (Solarthermie) | etwa 0,05 |
| Aluminium schwarz eloxiert | etwa 0,85 |
| Glas, Lack, Ziegel, Beton | etwa 0,9 |

Ein lackiertes Stahlrohr strahlt also fast wie ein schwarzer Körper, ein
blankes Kupferrohr kaum.

!!! info "Wie groß ist Strahlung im Vergleich zur Konvektion?"
    Bei Raumtemperatur und kleinem Temperaturunterschied lässt sich die
    Strahlung wie ein Wärmeübergangskoeffizient $\alpha_{Str}$ schreiben:
    $\alpha_{Str} \approx 4\,\varepsilon\,\sigma\,T^3$ mit der mittleren absoluten
    Temperatur $T$ von Fläche und Umgebung. Bei 20 °C und
    $\varepsilon = 0{,}9$ sind das rund **5 W/(m²·K)**. Das ist so viel wie
    freie Konvektion an ruhiger Luft. Strahlung darf man also auch bei
    niedrigen Temperaturen nicht weglassen.

## Zwei Arten in ANSYS

In ANSYS gibt es nur **eine** Randbedingung `Radiation`. Im Detailfenster legt
**Correlation** fest, wohin die Fläche strahlt:

<figure style="text-align:center;">
  <img src="../../images/p2_strahlung_arten.excalidraw.png" alt="To Ambient und Surface to Surface" class="no-lightbox">
  <figcaption>Beide Seiten strahlen, die wärmere mehr (kräftige Wellen). Netto fließt Wärme von warm nach kalt.</figcaption>
</figure>

| | To Ambient | Surface to Surface |
|---|---|---|
| Fläche strahlt zu | einer großen Umgebung mit **vorgegebener** Temperatur | anderen Flächen **im Modell** |
| Temperatur der Gegenseite | Eingabe (`Ambient Temperature`) | Ergebnis der Rechnung |
| Einsatz | Rohr im Raum, Bauteil im Freien | Spalte, Hohlräume, Flächen, die sich sehen |
| Zusätzliche Eingaben | | `Enclosure` (Nummer), `Enclosure Type` |

Bei **Surface to Surface** strahlen sich alle Flächen mit derselben
`Enclosure`-Nummer gegenseitig an. Was dahintersteckt, steht weiter unten.

### In welche Richtung strahlt eine Fläche?

Die Wellen im Bild oben sind vereinfacht. Jede Stelle einer Fläche strahlt in
**alle Richtungen** des Halbraums über ihr: senkrecht zur Fläche am stärksten,
flach zur Fläche kaum (Bild links).

<figure style="text-align:center;">
  <img src="../../images/p2_halbraum.excalidraw.png" alt="Links: Eine Stelle strahlt in den ganzen Halbraum, senkrecht am stärksten. Rechts: ANSYS setzt einen halben Würfel mit Feldern über das Flächenelement, das Glas fällt auf einige Felder" class="no-lightbox">
</figure>

Wie ANSYS damit rechnet, hängt von der Art ab:

- **To Ambient:** Alles, was die Fläche abstrahlt, kommt bei der Umgebung an, egal in welche Richtung. ANSYS braucht deshalb keine Richtungen und rechnet direkt mit dem Stefan-Boltzmann-Gesetz von oben, mit der `Ambient Temperature` als $T_\infty$. Das passt, solange die Fläche nur die Umgebung sieht
- **Surface to Surface:** ANSYS muss wissen, welcher Anteil auf welche Fläche trifft (Sichtfaktor, siehe unten). Dazu setzt es über jedes Flächenelement einen halben Würfel (Hemicube) aus vielen kleinen Feldern und bildet die anderen Flächen darauf ab (Bild rechts)
    - Die Felder, auf die eine Fläche fällt, ergeben den Sichtfaktor zu dieser Fläche
    - Felder über der Mitte zählen mehr als Felder am Rand, weil senkrecht mehr Strahlung abgeht
    - Der Würfel ist nur gedacht und steckt nicht im Modell. Seine Größe ist egal: Ein größerer Würfel zeigt dasselbe Bild, nur größer (Bild rechts, gestrichelt). Es zählt nur, in welcher Richtung eine Fläche liegt, wie bei einem Foto aus der Mitte des Flächenelements
    - Liegen zwei Flächen hintereinander, zählt nur die vordere: So berücksichtigt ANSYS die Verschattung
    - Wie fein die Felder sind, stellt `Hemicube Resolution` unter `Analysis Settings` > `Radiosity Controls` ein

### Welche Temperatur ist die Ambient Temperature?

Bei `To Ambient` ist die `Ambient Temperature` die Temperatur der Flächen, die
die Strahlung empfangen, **nicht** die Lufttemperatur. Die Luft lässt
Wärmestrahlung fast ungehindert durch. Die Luft gehört zur Konvektion, die
Flächen ringsum gehören zur Strahlung:

<figure style="text-align:center;">
  <img src="../../images/p2_ambient.excalidraw.png" alt="Ambient Temperature im Keller (Wände 15 °C) und draußen (Himmel 5 °C bei 20 °C Luft)" class="no-lightbox">
  <figcaption>Kräftige Wellen: Die wärmere Seite strahlt mehr. Das Glas der Röhre (Fall a: 15,8&nbsp;°C) ist wärmer als der Himmel, aber kälter als der Boden.</figcaption>
</figure>

- **a) Im Raum** ([Übung 1](../03_Selbsttests/Uebung-1.md), Heizungsrohr im Keller)
    - Das Rohr sieht Wände, Decke und Boden: Deren Temperatur ist die Ambient Temperature
    - Im Keller sind Wände und Luft etwa gleich warm, beide 15 °C
- **b) Draußen** ([Vorzeigebeispiel](../02_Vorzeigebeispiel/Vakuumroehre/index.md), Vakuumröhre)
    - Die obere Hälfte der Röhre sieht vor allem den Himmel, die untere vor allem den Boden: insgesamt je zur Hälfte
    - Der Himmel ist bei klarem Wetter etwa 15 bis 20 K kälter als die Luft (im Beispiel 5 °C bei 20 °C Luft), bei bedecktem Himmel nur wenige Kelvin
    - Der Boden ist etwa so warm wie die Luft
    - Genauer: zwei Strahlungsrandbedingungen, die obere Hälfte zum Himmel, die untere zum Boden
    - Oder den Boden mitmodellieren und `Surface to Surface` mit `Open` verwenden: Was nicht auf den Boden trifft, geht an die `Ambient Temperature` des Himmels
    - Das Vorzeigebeispiel vereinfacht: Die ganze Röhre strahlt zum Himmel. Die Nutzwärme ändert das kaum, das Glas wäre etwa 2 K wärmer
    - Für eine senkrechte Wand gilt dasselbe: halb Himmel, halb Boden

## Surface to Surface: Sichtfaktor und Enclosure {: #sichtfaktor }

Bei `Surface to Surface` rechnet ANSYS selbst aus, wie viel Strahlung von
jeder Fläche auf jede andere trifft. Das Beispiel ist die Vakuumröhre aus dem
Vorzeigebeispiel.

### Sichtfaktor

Der **Sichtfaktor** $F_{12}$ gibt an, welcher Anteil der Strahlung, die
Fläche 1 abgibt, direkt auf Fläche 2 trifft. In der langen Vakuumröhre sieht
der Absorber fast nur Glas, das Glas zu 60 % den Absorber und zu 40 % die
gegenüberliegende Glaswand (Bild unten, obere Balken).

Die übrigen 8 % des Absorbers treffen wieder den Absorber, aber nie dieselbe
Stelle: Die Blechflügel strahlen seitlich auf das Rohr in der Mitte, das Rohr
strahlt auf die Flügel. Ein ebenes Blech allein sieht sich nicht selbst, eine
gewölbte Fläche wie die Innenseite des Glases schon.

Probieren Sie es aus: Wählen Sie, ob der Absorber oder das Glas strahlt. Die
Strahlen starten an zufälligen Stellen in zufällige Richtungen, senkrecht zur
Fläche häufiger als flach. Gezählt wird, was jeder Strahl zuerst trifft. Mit
vielen Strahlen nähern sich die Anteile den Sichtfaktoren.

<div class="strahlenzaehler"></div>

??? info "Zwei Regeln für Sichtfaktoren"
    1. **Alles kommt irgendwo an.** Gezählt wird je Fläche, die strahlt: Ihre
       Sichtfaktoren zu allen Flächen, auch zu sich selbst, ergeben zusammen
       100 %, wenn der Raum geschlossen ist. In der langen Röhre mit dem
       Absorber als Fläche 1 und dem Glas als Fläche 2:
        - Absorber: $F_{11} + F_{12}$ = 8 % + 92 % = 100 %
        - Glas: $F_{21} + F_{22}$ = 60 % + 40 % = 100 %
        - $F_{11}$ und $F_{22}$: Anteil, der die strahlende Fläche selbst wieder trifft
    2. **Reziprozität:** $A_1\,F_{12} = A_2\,F_{21}$ mit den Flächen $A_1$, $A_2$ und den
       Sichtfaktoren $F_{12}$ (von 1 nach 2) und $F_{21}$ (von 2 nach 1). Gleich
       sind also nicht die Sichtfaktoren, sondern Fläche mal Sichtfaktor (Flächen je 20 mm Röhre):
        - Absorber: $2670\ \mathrm{mm^2} \cdot 0{,}92 \approx 2450\ \mathrm{mm^2}$
        - Glas: $4080\ \mathrm{mm^2} \cdot 0{,}60 \approx 2450\ \mathrm{mm^2}$
        - Das große Glas schickt nur 60 % zum Absorber, der kleine Absorber 92 % zum Glas. Weil das Glas größer ist, ist beides gleich viel (Bild)

    <figure style="text-align:center;">
      <img src="../../images/p2_reziprozitaet.excalidraw.png" alt="Balken so lang wie die Fläche: Absorber 2670 mm², davon 92 % zum Glas; Glas 4080 mm², davon 60 % zum Absorber; beide Teile gleich lang" class="no-lightbox">
    </figure>

    **Warum das so sein muss:** Zwischen zwei schwarzen Flächen geht Strahlung
    hin und zurück. Netto fließt

    $$
    \dot Q_{12} = \sigma\,A_1\,F_{12}\,T_1^4 - \sigma\,A_2\,F_{21}\,T_2^4
    $$

    mit dem Wärmestrom $\dot Q_{12}$ von Fläche 1 zu Fläche 2, der
    Stefan-Boltzmann-Konstante $\sigma$ und den absoluten Temperaturen $T_1$,
    $T_2$ der beiden Flächen.

    - Sind beide gleich warm, muss $\dot Q_{12}$ null sein, sonst flösse Wärme von allein zwischen gleich warmen Flächen. Das geht nur mit $A_1\,F_{12} = A_2\,F_{21}$
    - Dann gilt $\dot Q_{12} = \sigma\,A_1\,F_{12}\,\left(T_1^4 - T_2^4\right)$, und was der Absorber abgibt, kommt beim Glas an

### Enclosure

Ein **Enclosure** (Hohlraum) ist eine Gruppe von Flächen, die sich
gegenseitig anstrahlen. Dazu gehören alle Strahlungsrandbedingungen mit
derselben `Enclosure`-Nummer. ANSYS berechnet vor dem Lösen die Sichtfaktoren
zwischen allen Flächenelementen dieser Gruppe, samt Verschattung: Das Rohr
verdeckt zum Beispiel einen Teil des Blechs. Flächen in verschiedenen
Enclosures sehen sich nicht, auch wenn sie sich gegenüberliegen.

### Open oder Perfect: Was passiert mit dem Rest?

Das Modell der Röhre ist nur **20 mm** lang und vorn und hinten offen: Gut die
Hälfte der Strahlung trifft gar nichts im Modell (mittlere Balken).

<figure style="text-align:center;">
  <img src="../../images/p2_sichtfaktor.excalidraw.png" alt="Längsschnitt: 20-mm-Stück mit offenen Enden und lange Röhre mit Nachbarstücken" class="no-lightbox">
</figure>

In der Seitenansicht unten liegt oben und unten das Glas, in der Mitte der
Absorber, links und rechts sind die offenen Enden. Wählen Sie, was strahlt: Was
vorn oder hinten hinausgeht, wird grau. Treffer auf der vorderen oder hinteren
Glaswand liegen im Bild zwischen den beiden Glasstreifen. Vergleichen Sie
20 mm mit 200 mm Länge.

<div class="strahlenzaehler" data-ansicht="laengs"></div>

<figure style="text-align:center;">
  <img src="../../images/p2_sichtfaktor_balken.excalidraw.png" alt="Sichtfaktoren von Absorber und Glas: lange Röhre, 20-mm-Stück, mit Perfect" class="no-lightbox">
  <figcaption>Sichtfaktoren der Röhre, eigene Abschätzung mit Strahlverfolgung</figcaption>
</figure>

Was mit dem Rest passiert, legt `Enclosure Type` fest:

- **Open:** Der Rest geht an eine Umgebung mit der eingetragenen
  **Ambient Temperature**. Das passt, wenn die Öffnung wirklich ins Freie
  zeigt, z. B. zwischen den Rippen eines Kühlkörpers.
- **Perfect:** Es gibt keinen Rest. ANSYS rechnet die Sichtfaktoren jeder
  Fläche so hoch, dass sie zusammen wieder 100 % ergeben.

Für die Röhre ist **Perfect** richtig: In der langen Röhre trifft, was vorn
hinausgeht, das Nachbarstück, und genauso viel Strahlung kommt von dort zurück.
Mit Open sähe das Glas durch die Enden eine Umgebung von z. B. 22 °C, die es
im Vakuum nicht gibt.

### Der Haken an Perfect {: #haken-perfect }

Perfect rechnet jede Fläche **für sich** hoch (untere Balken, rot umrandet,
was zu viel ist): Das Glas sieht
danach mehr Absorber als in der langen Röhre (67 % statt 60 %), der Absorber
weniger Glas (86 % statt 92 %). Damit gilt die Reziprozität nicht mehr
(Glas $4080\ \mathrm{mm^2} \cdot 0{,}67 \approx 2730\ \mathrm{mm^2}$, Absorber
$2670\ \mathrm{mm^2} \cdot 0{,}86 \approx 2300\ \mathrm{mm^2}$): Das Glas nimmt
rund 20 % mehr Strahlung auf, als der Absorber abgibt. Im Modell entsteht
Energie, und die Bilanz der Reaktionen geht nicht mehr auf. Genau das zeigt
die Vakuumröhre: Das Glas gibt in allen drei Fällen 16 bis 24 % mehr an Luft
und Himmel ab, als der Absorber zu ihm strahlt.

<figure style="text-align:center;">
  <img src="../../images/p2_reziprozitaet_perfect.excalidraw.png" alt="Fläche mal Sichtfaktor: in der langen Röhre gleich lang, mit Perfect nimmt das Glas rund 20 % mehr auf, als der Absorber abgibt" class="no-lightbox">
  <figcaption>Balken so lang wie die Fläche, dick umrandet der Teil, der die andere Fläche trifft</figcaption>
</figure>

Was man daraus mitnimmt:

- Bei `Surface to Surface` immer die **Bilanz der Reaktionen** prüfen. Die
  Summe sollte fast null sein.
- Je länger das Stück, desto kleiner der Fehler. Bei 200 mm gehen nur noch
  rund 10 % (Glas) und 8 % (Absorber) hinaus, dafür rechnet ANSYS viel länger.
- Ein **2D-Modell** hat keine offenen Enden: Der Querschnitt gilt dort als
  unendlich lang.
- Hält nichts die Temperaturen fest und tauschen die Flächen viel Strahlung,
  kann der Fehler sogar zu unsinnigen Lösungen führen: siehe
  [Vakuumröhre, Fall c)](../02_Vorzeigebeispiel/Vakuumroehre/c-stillstand.md) mit schwarzem Absorber.

## Sonne ist keine Strahlungsrandbedingung

Die Sonne ist so weit weg und so heiß, dass ihre Einstrahlung nicht von der
Temperatur des Bauteils abhängt. Man gibt sie deshalb als **Wärmestromdichte**
(`Heat Flux`) vor, und zwar nur den Teil, der wirklich aufgenommen wird:

$$
\dot q_{Sonne} = G \cdot \tau \cdot \alpha_S
$$

mit der Einstrahlung $G$ (an einem klaren Tag bis etwa 1000 W/m²), der
Durchlässigkeit $\tau$ einer Glasabdeckung und dem Absorptionsgrad $\alpha_S$
der Oberfläche für Sonnenlicht.

!!! info "Warum Glas wärmt: der Treibhauseffekt"
    Glas lässt das kurzwellige Sonnenlicht fast ganz durch, die langwellige
    Wärmestrahlung eines warmen Körpers aber nicht: Für sie ist Glas
    undurchsichtig und hat ε ≈ 0,9. Deshalb heizt sich ein Raum hinter einer
    Scheibe auf, und deshalb gibt der Absorber im Vorzeigebeispiel seine
    Strahlung an das Glas ab und nicht an den Himmel.
