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

ab. Zwei Dinge sind dabei wichtig:

- $T$ ist die **absolute Temperatur** in Kelvin. ANSYS rechnet das selbst um,
  Eingaben bleiben in °C.
- Die vierte Potenz macht die Rechnung **nichtlinear**: ANSYS braucht mehrere
  Durchläufe (Iterationen), bis die Lösung steht. Das sieht man in
  `Solution Information`.

Was eine Fläche abstrahlt, bekommt sie zum Teil von ihrer Umgebung zurück.
Netto zählt der Unterschied:

$$
\dot q = \varepsilon\,\sigma\,\left(T^4 - T_\infty^4\right)
$$

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
    Strahlung wie ein Wärmeübergangskoeffizient schreiben:
    $\alpha_{Str} \approx 4\,\varepsilon\,\sigma\,T^3$. Bei 20 °C und
    $\varepsilon = 0{,}9$ sind das rund **5 W/(m²·K)**. Das ist so viel wie
    freie Konvektion an ruhiger Luft. Strahlung darf man also auch bei
    niedrigen Temperaturen nicht weglassen.

## Zwei Arten in ANSYS

In ANSYS gibt es nur **eine** Randbedingung `Radiation`. Im Detailfenster legt
**Correlation** fest, wohin die Fläche strahlt:

<figure style="text-align:center;">
  <img src="../../images/p2_strahlung_arten.excalidraw.png" alt="To Ambient und Surface to Surface" class="no-lightbox">
</figure>

| | To Ambient | Surface to Surface |
|---|---|---|
| Fläche strahlt zu | einer großen Umgebung mit **vorgegebener** Temperatur | anderen Flächen **im Modell** |
| Temperatur der Gegenseite | Eingabe (`Ambient Temperature`) | Ergebnis der Rechnung |
| Einsatz | Rohr im Raum, Bauteil im Freien | Spalte, Hohlräume, Flächen, die sich sehen |
| Zusätzliche Eingaben | | `Enclosure` (Nummer), `Enclosure Type` |

- **Ambient Temperature** bei `To Ambient` ist die Temperatur der Flächen, die
  die Strahlung empfangen, **nicht** die Lufttemperatur. Im Keller sind Wände
  und Luft etwa gleich warm. Unter freiem Himmel ist der Himmel deutlich
  kälter als die Luft, bei klarem Wetter etwa 15 K.
- **Surface to Surface:** Alle Flächen mit derselben `Enclosure`-Nummer
  strahlen sich gegenseitig an. Was dahintersteckt, steht im nächsten
  Abschnitt.

## Surface to Surface: Sichtfaktor und Enclosure {: #sichtfaktor }

Bei `Surface to Surface` rechnet ANSYS selbst aus, wie viel Strahlung von
jeder Fläche auf jede andere trifft. Dafür braucht es zwei Begriffe: den
Sichtfaktor und das Enclosure. Das Beispiel ist die Vakuumröhre aus dem
Vorzeigebeispiel.

### Sichtfaktor

Der **Sichtfaktor** $F_{12}$ gibt an, welcher Anteil der Strahlung, die
Fläche 1 abgibt, direkt auf Fläche 2 trifft. Anschaulich: Wie viel ihres
Blickfelds nimmt Fläche 2 ein, wenn man von Fläche 1 aus schaut?

In der langen Vakuumröhre:

| Strahlung vom … | trifft den Absorber | trifft das Glas |
|---|---|---|
| Absorber | 8 % | 92 % |
| Glas (innen) | 60 % | 40 % |

- Der Absorber sieht fast nur Glas. Den kleinen Rest sieht er von sich
  selbst, in den Ecken zwischen Blech und Rohr.
- Das Glas sieht zu 60 % den Absorber und zu 40 % die gegenüberliegende
  Glaswand.

Zwei Regeln gelten immer:

1. **Alles kommt irgendwo an.** In einem geschlossenen Raum ergeben die
   Sichtfaktoren einer Fläche zusammen 100 % (jede Zeile der Tabelle).
2. **Reziprozität:** $A_1\,F_{12} = A_2\,F_{21}$. Die große Glasfläche sieht
   den kleinen Absorber zu einem kleineren Anteil als umgekehrt, und zwar
   genau im Verhältnis der Flächen. Je 20 mm Röhre:
   $4080\ \mathrm{mm^2} \cdot 0{,}60 \approx 2670\ \mathrm{mm^2} \cdot 0{,}92 \approx 2450\ \mathrm{mm^2}$.

Die zweite Regel sorgt dafür, dass die Energie stimmt. Zwischen zwei
schwarzen Flächen fließt netto

$$
\dot Q_{12} = \sigma\,A_1\,F_{12}\,\left(T_1^4 - T_2^4\right)
$$

Nur weil $A_1 F_{12} = A_2 F_{21}$ ist, rechnen beide Flächen mit demselben
Wärmestrom: Was der Absorber abgibt, kommt beim Glas an. Bei grauen Flächen
kommen Reflexionen dazu, an den beiden Regeln ändert das nichts.

### Enclosure

Ein **Enclosure** (Hohlraum) ist eine Gruppe von Flächen, die sich
gegenseitig anstrahlen. Dazu gehören alle Radiation-Randbedingungen mit
derselben `Enclosure`-Nummer. ANSYS berechnet vor dem Lösen die Sichtfaktoren
zwischen allen Flächenelementen dieser Gruppe, samt Verschattung: Das Rohr
verdeckt zum Beispiel einen Teil des Blechs. Flächen in verschiedenen
Enclosures sehen sich nicht, auch wenn sie sich gegenüberliegen.

### Open oder Perfect: Was passiert mit dem Rest?

Das Modell der Röhre ist nur **20 mm** lang. Vorn und hinten ist es offen,
dort ist keine Fläche. Ein großer Teil der Strahlung trifft deshalb gar
nichts im Modell:

<figure style="text-align:center;">
  <img src="../../images/p2_sichtfaktor.excalidraw.png" alt="Längsschnitt: 20-mm-Stück mit offenen Enden und lange Röhre mit Nachbarstücken" class="no-lightbox">
</figure>

| Strahlung vom … | trifft den Absorber | trifft das Glas | geht vorn und hinten hinaus |
|---|---|---|---|
| Absorber | 6 % | 40 % | **54 %** |
| Glas (innen) | 26 % | 13 % | **61 %** |

<!-- Quelle der Prozentwerte: tools/sollwerte/p2_sichtfaktoren.py -->

Die Zahlen sind eine eigene Abschätzung mit Strahlverfolgung. Was mit dem
Rest passiert, legt `Enclosure Type` fest:

- **Open:** Der Rest geht an eine Umgebung mit der eingetragenen
  **Ambient Temperature**. Das passt, wenn die Öffnung wirklich ins Freie
  zeigt, z. B. zwischen den Rippen eines Kühlkörpers.
- **Perfect:** Es gibt keinen Rest. ANSYS rechnet die Sichtfaktoren jeder
  Fläche so hoch, dass sie zusammen wieder 100 % ergeben.

Für die Röhre ist **Perfect** richtig. In der langen Röhre trifft, was vorn
hinausgeht, das Nachbarstück. Das ist genauso warm, und genauso viel Strahlung
kommt von dort zurück (Bild rechts). Mit Open sähe das Glas durch die Enden
eine Umgebung von z. B. 22 °C, die es im Vakuum nicht gibt.

### Der Haken an Perfect {: #haken-perfect }

Perfect rechnet jede Fläche **für sich** hoch. Das Glas behält nur 39 % und
wird mit dem Faktor 2,5 hochgerechnet, der Absorber behält 46 % und bekommt
den Faktor 2,2:

| nach dem Hochrechnen | trifft den Absorber | trifft das Glas |
|---|---|---|
| Absorber | 14 % (lange Röhre: 8 %) | 86 % (lange Röhre: 92 %) |
| Glas (innen) | 67 % (lange Röhre: 60 %) | 33 % (lange Röhre: 40 %) |

Damit gilt die Reziprozität nicht mehr: Das Glas rechnet mit
$4080\ \mathrm{mm^2} \cdot 0{,}67 \approx 2730\ \mathrm{mm^2}$, der Absorber
mit $2670\ \mathrm{mm^2} \cdot 0{,}86 \approx 2300\ \mathrm{mm^2}$. Das Glas
nimmt also rund 20 % mehr Strahlung auf, als der Absorber abgibt. Im Modell
entsteht Energie, und die Bilanz der Reaktionen geht nicht mehr auf. Genau
das zeigt die Vakuumröhre: Das Glas gibt in allen drei Fällen 16 bis 24 %
mehr an Luft und Himmel ab, als der Absorber zu ihm strahlt.

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
