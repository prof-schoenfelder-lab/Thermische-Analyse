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
    2. Genauso **Sonne**, **Luft** und **Himmel**
    3. `Rechtsklick Solution → Evaluate All Results`, den Wärmestrom (**Heat**) im Detailfenster der jeweiligen Probe ablesen

Negative Werte heißen: Die Wärme verlässt das Modell über diese Randbedingung.

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Wert |
    |---|---|
    | Temperatur Absorber | 51,0 bis 52,1 °C |
    | Temperatur Glas | 15,8 bis 15,9 °C |
    | Reaktion Sonne | +0,672 W |
    | Reaktion Wasser (Nutzwärme) | −0,639 W |
    | Reaktion Luft | +0,182 W |
    | Reaktion Himmel | −0,223 W |

    Die Summe aller Reaktionen ist fast null: Was die Sonne hineinbringt,
    geht über Wasser und Glas wieder hinaus. Es bleiben rund −0,008 W übrig,
    das ist gewollt (siehe unten).

!!! info "Warum geht die Bilanz nicht genau auf?"
    Absorber und Glas tauschen Strahlung über **Sichtfaktoren** aus. Unser
    20 mm langes Stück ist vorn und hinten offen: Ein Teil der Strahlung
    würde dort hinausgehen. **Perfect** schließt den Raum, indem ANSYS die
    Sichtfaktoren **jeder Fläche einzeln** hochrechnet, bis sie zusammen 1
    ergeben. Glas und Absorber verlieren aber unterschiedlich viel an die
    Enden und werden deshalb unterschiedlich stark hochgerechnet. Dann gilt
    die Reziprozität $A_1 F_{12} = A_2 F_{21}$ nicht mehr genau: Der Absorber
    gibt 0,033 W ab, beim Glas kommen 0,041 W an.

    Ein feineres Netz ändert daran nichts. Ein längeres Stück schon: Bei
    200 mm sinkt die Lücke auf ein Drittel, und Luft und Himmel liegen nur
    noch 1 bis 2 % neben den Werten der unendlich langen Röhre
    (+0,188 W und −0,219 W). Dafür rechnet ANSYS viel länger. Für den
    Vergleich von a), b) und c) reichen die 20 mm.

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
