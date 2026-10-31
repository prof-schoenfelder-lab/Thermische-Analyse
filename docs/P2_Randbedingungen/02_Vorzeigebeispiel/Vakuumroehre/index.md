---
title: "Vorzeigebeispiel: Vakuumröhre"
icon: material/help-box
---

# Vorzeigebeispiel: Vakuumröhre eines Solarkollektors

<div class="task-tabs-src" data-tabs="Aufgabe=./|a) Selektiv=01-modell/|b) Schwarz=b-schwarz/|c) Stillstand=c-stillstand/" hidden></div>

In einer Vakuumröhre liegt ein Absorberblech mit einem Wasserrohr in einem
Glasrohr. Dazwischen ist **Vakuum**: Es gibt keine Luft, also auch keine
Konvektion. Der Absorber kann Wärme nur noch über **Strahlung** verlieren.
Darum ist er mit einer selektiven Schicht beschichtet, die Sonnenlicht gut
aufnimmt, aber kaum Wärme abstrahlt.

In diesem Beispiel kommen fast alle Randbedingungen vor:

- **Wärmestromdichte:** Sonne auf dem Absorber
- **Konvektion:** Wasser im Rohr, Luft außen am Glas
- **Strahlung To Ambient:** Glas zum Himmel
- **Strahlung Surface to Surface:** Absorber und Glas strahlen sich gegenseitig an

!!! question "Die Aufgabe"
    Für ein 20 mm langes Stück der Röhre die **Temperaturen** von Absorber und
    Glas und die **Nutzwärme** an das Wasser bestimmen, für drei Fälle:

    - **a)** Absorber **selektiv** beschichtet, ε = 0,05
    - **b)** Absorber **schwarz** lackiert, ε = 0,9
    - **c)** **Stillstand**: Das Wasser steht, die Pumpe ist aus (optional)

<figure style="text-align:center;">
  <img src="../../images/p2_roehre.svg" alt="Querschnitt der Vakuumröhre" class="no-lightbox">
</figure>

## Gegeben

### Material

<!-- --8<-- [start:Material] -->
| Körper | Wärmeleitfähigkeit |
|---|---|
| Glas (Borosilikatglas) | $\lambda = 1{,}1\ \mathrm{W/(m\,K)}$ |
| Kupfer (Absorberblech und Rohr) | $\lambda = 400\ \mathrm{W/(m\,K)}$ |
<!-- --8<-- [end:Material] -->

### Geometrie

<!-- --8<-- [start:Geometrie] -->
Querschnitt, 20 mm lang ausgezogen:

- Glasrohr Ø 70 mm, Wanddicke 2,5 mm (innen Ø 65 mm)
- Kupferrohr Ø 12 mm, Wanddicke 1 mm (innen Ø 10 mm), in der Mitte
- Absorberblech 60 mm × 0,5 mm, mittig durch das Rohr

Absorberblech und Rohr sind **ein** Körper. Glas und Absorber berühren sich nicht.
<!-- --8<-- [end:Geometrie] -->

### Vernetzung

<!-- --8<-- [start:Vernetzung] -->
- Netzgröße global: 2 mm
<!-- --8<-- [end:Vernetzung] -->

### Randbedingungen

<!-- --8<-- [start:Randbedingungen] -->
| Wo | Randbedingung | Werte |
|---|---|---|
| Oberseite der beiden Blechflügel | Wärmestromdichte (Sonne) | $\dot q = 800 \cdot 0{,}92 \cdot 0{,}95 \approx 700\ \mathrm{W/m^2}$ |
| Innenseite Kupferrohr | Konvektion (Wasser) | $\alpha = 1000\ \mathrm{W/(m^2\,K)}$, $T = 50\ \mathrm{°C}$ |
| Außenseite Glas | Konvektion (Luft) | $\alpha = 10\ \mathrm{W/(m^2\,K)}$, $T = 20\ \mathrm{°C}$ |
| Außenseite Glas | Strahlung To Ambient (Himmel) | $\varepsilon = 0{,}9$, $T = 5\ \mathrm{°C}$ |
| Absorber außen und Glas innen | Strahlung Surface to Surface | Absorber $\varepsilon = 0{,}05$, Glas $\varepsilon = 0{,}9$ |

Die beiden Stirnflächen (Schnitt durch die lange Röhre) bleiben frei, also isoliert.
<!-- --8<-- [end:Randbedingungen] -->

Die Sonne trifft in diesem Modell nur die Blechflügel. Das Rohr selbst und die
kleine Aufnahme im Glas vernachlässigen wir.

## Gesucht

<!-- --8<-- [start:Gesucht] -->
1. Temperatur von Absorber und Glas
2. Nutzwärme an das Wasser je 20 mm Röhre und je Meter Röhre
3. Anteil der aufgenommenen Sonne, der im Wasser ankommt
<!-- --8<-- [end:Gesucht] -->

## Lösungswege

<div class="grid cards" markdown>

-   <a class="card-link" href="01-modell/">
    __a) Selektiv__: Modell aufbauen, alle Randbedingungen, auswerten
    </a>

-   <a class="card-link" href="b-schwarz/">
    __b) Schwarz__: nur den Emissionsgrad ändern
    </a>

-   <a class="card-link" href="c-stillstand/">
    __c) Stillstand__: Was passiert ohne Wasserstrom? (optional)
    </a>

</div>
