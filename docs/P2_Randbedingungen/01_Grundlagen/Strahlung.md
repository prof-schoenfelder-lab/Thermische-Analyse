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
  <img src="../../images/p2_strahlung_arten.svg" alt="To Ambient und Surface to Surface" class="no-lightbox">
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
  strahlen sich gegenseitig an. ANSYS berechnet dafür, welchen Anteil der
  Strahlung jede Fläche von jeder anderen empfängt (**Sichtfaktor**).
  `Enclosure Type` **Perfect** heißt: Der Hohlraum ist geschlossen, keine
  Strahlung geht verloren. **Open** heißt: Was die anderen Flächen nicht
  trifft, geht an die Umgebung.

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
