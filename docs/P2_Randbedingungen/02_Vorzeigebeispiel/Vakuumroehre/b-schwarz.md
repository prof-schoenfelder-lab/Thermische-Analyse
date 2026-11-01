---
title: b) Schwarz
---

# b) Schwarzer statt selektiver Absorber

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** zweite Analyse mit **ε = 0,9** am Absorber, Nutzwärme vergleichen
</div>

Was bringt die teure selektive Beschichtung? Dazu rechnen wir dieselbe Röhre
mit einem schwarz lackierten Absorber. Schwarzer Lack nimmt Sonnenlicht genauso
gut auf, strahlt aber auch Wärme fast wie ein schwarzer Körper ab: ε = 0,9.

??? tip "Kurzanleitung: zweite Analyse mit gemeinsamem Modell"
    1. Im Projektmenü in der Toolbox **Steady-State Thermal** mit gedrückter Maustaste auf die Zelle **Model** der Analyse A ziehen
    2. Die neue Analyse in **b) Schwarz** umbenennen
    3. `Rechtsklick Setup (B) → Edit...`: Im Strukturbaum stehen beide Analysen

??? tip "Kurzanleitung: Randbedingungen und Ergebnisse übernehmen"
    1. Unter **Steady-State Thermal (A5)** alle sechs Randbedingungen markieren (`Shift`) und auf **Steady-State Thermal 2 (B5)** ziehen
    2. Unter **Solution (A6)** alle Ergebnisse markieren und auf **Solution (B6)** ziehen
    3. In B5 die Randbedingung **Absorber zum Glas** anklicken, **Emissivity** auf **0,9** setzen
    4. `Rechtsklick Solution (B6) → Solve`

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | a) selektiv | b) schwarz |
    |---|---|---|
    | Temperatur Absorber | 51,0 bis 52,1 °C | **50,4 bis 51,0 °C** |
    | Temperatur Glas | 15,8 bis 15,9 °C | **20,8 bis 22,1 °C** |
    | Reaktion Wasser (Nutzwärme) | −0,639 W | **−0,290 W** |
    | Reaktion Luft | +0,182 W | **−0,084 W** |
    | Reaktion Himmel | −0,223 W | **−0,358 W** |
    | Nutzwärme je Meter | 32,0 W/m | **14,5 W/m** |
    | Anteil der Sonne im Wasser | 95 % | **43 %** |

## Was die Zahlen zeigen

- Die **Temperatur** des Absorbers ändert sich kaum: Das Wasser hält ihn bei
  rund 50 °C fest.
- Der Unterschied steckt im **Wärmestrom**: Der schwarze Absorber strahlt
  rund 60 % der aufgenommenen Sonne zum Glas ab, statt sie ans Wasser zu geben.
  Das Glas wird dabei wärmer als die Luft: Die Reaktion **Luft** ist jetzt
  negativ, die Luft kühlt das Glas.
- Im Vakuum gibt es keine Konvektion. Der Emissionsgrad entscheidet hier
  allein über den Verlust: Deshalb sind Vakuumröhren immer selektiv
  beschichtet.

!!! info "Die Temperatur allein sagt wenig"
    Hätten wir nur die Temperaturen angesehen, wären beide Absorber fast
    gleich gut. Erst die **Reaktion** der Randbedingung **Wasser** zeigt den
    Unterschied. Bei Randbedingungen mit Konvektion und Strahlung lohnt sich
    deshalb immer der Blick auf die Wärmeströme.
