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

??? tip "Kurzanleitung: Lösen"
    1. `Rechtsklick Solution → Solve`
    2. Mit Strahlung dauert das etwas länger: ANSYS berechnet zuerst die Sichtfaktoren und braucht dann mehrere Iterationen
    3. Wer zusehen will: `Solution Information` anklicken, unter **Solution Output** **Temperature Convergence** wählen

## Temperaturen

??? tip "Kurzanleitung: Temperatur je Körper"
    1. Oben `Body` anklicken, den **Absorber** anklicken, `Rechtsklick Solution → Insert → Thermal → Temperature`, umbenennen in **Temperatur Absorber**
    2. Genauso für das **Glas**
    3. `Rechtsklick Solution → Evaluate All Results`, Min und Max stehen in der Legende und im Detailfenster

## Wärmeströme der Randbedingungen

??? tip "Kurzanleitung: Reaction Probe per Drag & Drop"
    1. Die Randbedingung **Wasser** im Strukturbaum mit gedrückter Maustaste auf **Solution** ziehen: Es entsteht eine **Reaction Probe**
    2. Genauso **Luft** und **Himmel**. Für die **Sonne** gibt es keine Reaction Probe: Ihr Wärmestrom ist vorgegeben, 700 W/m² · 9,6·10⁻⁴ m² = 0,672 W
    3. `Rechtsklick Solution → Evaluate All Results`, den Wärmestrom (**Heat**) im Detailfenster der jeweiligen Probe ablesen

Negative Werte heißen: Die Wärme verlässt das Modell über diese Randbedingung.

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

!!! info "Warum geht die Bilanz nicht genau auf?"
    Unser 20 mm langes Stück ist vorn und hinten offen. Vom Glas gehen dort
    rund 61 % der Strahlung hinaus, vom Absorber 54 %. **Perfect** rechnet
    die Sichtfaktoren **jeder Fläche einzeln** wieder auf 100 % hoch, das Glas
    dabei stärker als den Absorber. Dadurch nimmt das Glas rund 20 % mehr
    Strahlung auf, als der Absorber abgibt: Der Absorber gibt 0,033 W ab,
    beim Glas kommen 0,041 W an. Ausführlich mit Bild steht das unter
    [Wärmestrahlung: Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect).

    Ein feineres Netz ändert daran nichts. Ein längeres Stück schon: Bei
    200 mm sinkt die Lücke auf ein Drittel, und Luft und Himmel liegen nur
    noch 1 bis 2 % neben den Werten der unendlich langen Röhre
    (+0,188 W und −0,219 W). Dafür rechnet ANSYS viel länger.

    Je stärker Absorber und Glas Strahlung tauschen, desto größer die Lücke:
    Bei b) sind es −0,060 W, bei c) −0,115 W. Das Glas gibt jeweils
    rund 15 bis 25 % mehr ab, als der Absorber zu ihm strahlt. Für den
    Vergleich von a), b) und c) reichen die 20 mm trotzdem: Die Unterschiede
    zwischen den Fällen sind viel größer.

## Was die Zahlen zeigen

- **Nutzwärme je Meter Röhre:** 0,639 W je 20 mm, also **32,0 W/m**.
- **95 %** der aufgenommenen Sonne kommen im Wasser an
  (0,639 W von 0,672 W). Nur rund 0,03 W strahlt der Absorber zum Glas ab.
- **Das Glas ist kälter als die Luft** (15,8 °C bei 20 °C Luft): Es strahlt zum
  kalten Himmel und bekommt vom Absorber kaum Wärme. Die Luft wärmt das Glas
  sogar (Reaktion Luft positiv). Deshalb taut auf Vakuumröhren im Winter kein
  Schnee.
- Der Absorber ist nur rund 1 bis 2 K wärmer als das Wasser: Kupfer leitet so
  gut, dass die Wärme fast ohne Temperaturunterschied ins Rohr fließt.

!!! question "Und wenn der Absorber nicht beschichtet wäre?"
    Das klärt [Fall b)](b-schwarz.md).
