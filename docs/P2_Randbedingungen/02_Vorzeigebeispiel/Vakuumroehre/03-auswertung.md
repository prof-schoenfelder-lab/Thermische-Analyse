---
title: 3 · Lösen und Auswerten
---

# 3 · Lösen und Auswerten <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** lösen, Temperaturen ablesen und die **Wärmeströme** jeder Randbedingung bilanzieren
</div>

## Aufgabenstellung

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Gesucht"

## Lösen

??? tip "Lösen"
    1. `Rechtsklick Solution → Solve`
    2. Mit Strahlung dauert das etwas länger: ANSYS berechnet zuerst die Sichtfaktoren und braucht dann mehrere Iterationen
    3. Wer zusehen will: `Solution Information` anklicken, unter **Solution Output** **Temperature Convergence** wählen

## Temperaturen

??? tip "Kurzanleitung: Temperatur je Körper"
    1. Zwei Named Selections für die Körper: **Entity Type** `Body`, **Criterion** `Material`, **Value** `Kupfer`, umbenennen in **Koerper Absorber**; genauso mit `Glas`: **Koerper Glas**
    2. `Rechtsklick Solution → Insert → Thermal → Temperature`, **Scoping Method** `Named Selection`, **Named Selection** `Koerper Absorber`, umbenennen in **Temperatur Absorber**
    3. Genauso **Temperatur Glas**
    4. `Rechtsklick Solution → Evaluate All Results`, Min und Max stehen in der Legende und im Detailfenster

<tutorial slug="p2-temperatur-koerper"></tutorial>

!!! tip "Tipp: Körper direkt wählen, ohne Named Selection"
    - Nach `Insert → Thermal → Temperature` den Auswahlfilter in der Symbolleiste über dem Grafikfenster von Face auf `Body` umstellen
    - Den Körper anklicken, im Detailfenster bei **Geometry** `Apply`
    - Das Glas verdeckt den Absorber: Glas vorher ausblenden (`Rechtsklick Glas im Strukturbaum → Hide Body`), danach `Show All Bodies`
    - Die beiden Named Selections für die Körper braucht man dann nicht

## Wärmeströme der Randbedingungen

??? tip "Kurzanleitung: Reaction Probe"
    1. `Rechtsklick Solution → Insert → Probe → Reaction`, bei **Boundary Condition** **Wasser** wählen, umbenennen in **Reaktion Wasser**. Schneller: die Randbedingung mit gedrückter Maustaste auf **Solution** ziehen
    2. Genauso **Luft** und **Himmel**. Für die **Sonne** gibt es keine Reaction Probe: Ihr Wärmestrom ist vorgegeben, 700 W/m² · 9,6·10⁻⁴ m² = 0,672 W
    3. `Rechtsklick Solution → Evaluate All Results`, den Wärmestrom (**Heat**) im Detailfenster der jeweiligen Probe ablesen

<tutorial slug="p2-reaction-probe"></tutorial>

Negative Werte heißen: Die Wärme verlässt das Modell über diese Randbedingung.

!!! info "Sonne: keine Reaction Probe, sondern Wert mal Fläche"
    Für eine Wärmestromdichte (`Heat Flux`) bietet ANSYS keine Reaction Probe
    an. Ihr Wärmestrom steht aber schon fest, er ist die Eingabe mal die Fläche:

    $$
    \dot Q_\mathrm{Sonne} = \dot q \cdot A = 700\ \mathrm{W/m^2} \cdot 9{,}6 \cdot 10^{-4}\ \mathrm{m^2} = 0{,}672\ \mathrm{W}
    $$

    - $\dot Q_\mathrm{Sonne}$: Wärmestrom, den die Sonne in den Absorber bringt
    - $\dot q$: Wärmestromdichte der Sonne, 700 W/m² (Eingabe bei `Heat Flux`)
    - $A$: Fläche der beiden Blechoberseiten: zwei Flügel, je 24 mm breit (von 6 bis 30 mm) und 20 mm lang, also 2 · 24 mm · 20 mm = 960 mm² = 9,6·10⁻⁴ m²
    - Die Fläche zeigt auch ANSYS: Im Detailfenster der Named Selection **Oberseiten Blech** steht sie als **Surface Area**

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Wert |
    |---|---|
    | Temperatur Absorber | 51,0 bis 52,1 °C |
    | Temperatur Glas | 15,8 bis 15,9 °C |
    | Sonne (vorgegeben) | +0,672 W |
    | Reaktion Wasser (Nutzwärme) | −0,639 W |
    | Reaktion Luft | +0,182 W |
    | Reaktion Himmel | −0,223 W |

    Sonne und Reaktionen ergeben zusammen fast null: Was die Sonne hineinbringt,
    geht über Wasser und Glas wieder hinaus. Es bleiben rund −0,008 W übrig,
    das liegt am kurzen Stück (siehe unten).

<figure style="text-align:center;">
  <img src="../../../images/p2_roehre_a_absorber.webp" alt="Fall a: Temperatur Absorber, 51,0 bis 52,1 °C" style="width:49%">
  <img src="../../../images/p2_roehre_a_glas.webp" alt="Fall a: Temperatur Glas, 15,8 bis 15,9 °C" style="width:49%">
  <figcaption>Fall a): Die Blechkanten sind am wärmsten, das Rohr am kühlsten. Das Glas ist kälter als die Luft</figcaption>
</figure>

??? info "Warum geht die Bilanz nicht genau auf?"
    Unser 20 mm langes Stück ist vorn und hinten offen. **Perfect** rechnet die
    Sichtfaktoren **jeder Fläche einzeln** wieder auf 100 % hoch, das Glas
    stärker als den Absorber. Dadurch nimmt das Glas rund 20 % mehr Strahlung
    auf, als der Absorber abgibt (0,041 W statt 0,033 W). Bild und Zahlen:
    [Wärmestrahlung: Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect).

    Ein feineres Netz ändert daran nichts, ein längeres Stück schon: Bei 200 mm
    sinkt die Lücke auf ein Drittel. Für den Vergleich von a), b) und c)
    reichen die 20 mm, die Unterschiede zwischen den Fällen sind viel größer.

## Was die Zahlen zeigen

- **Nutzwärme je Meter Röhre:** 0,639 W je 20 mm, also **32,0 W/m**.
- **95 %** der aufgenommenen Sonnenleistung kommen im Wasser an
  (0,639 W von 0,672 W). Nur rund 0,03 W strahlt der Absorber zum Glas ab.
- **Das Glas ist kälter als die Luft** (15,8 °C bei 20 °C Luft): Es strahlt zum
  kalten Himmel und bekommt vom Absorber kaum Wärme. Die Luft wärmt das Glas
  sogar (Reaktion Luft positiv). Deshalb taut auf Vakuumröhren im Winter kein
  Schnee.
- Der Absorber ist nur rund 1 bis 2 K wärmer als das Wasser: Kupfer leitet so
  gut, dass die Wärme fast ohne Temperaturunterschied ins Rohr fließt.

!!! question "Und wenn der Absorber nicht beschichtet wäre?"
    Das klärt [Fall b)](b-schwarz.md).
