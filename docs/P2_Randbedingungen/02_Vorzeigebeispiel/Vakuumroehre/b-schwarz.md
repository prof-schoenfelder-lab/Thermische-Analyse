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
    1. Unter **Steady-State Thermal (A5)** alle sechs Randbedingungen markieren (`Shift`), `Rechtsklick → Copy`, `Rechtsklick Steady-State Thermal 2 (B5) → Paste`
    2. Genauso die Ergebnisse von **Solution (A6)** nach **Solution (B6)**
    3. In B5 die Randbedingung **Absorber zum Glas** anklicken, **Emissivity** auf **0,9** setzen

<tutorial slug="p2-schwarz"></tutorial>

Dann `Rechtsklick Solution (B6) → Solve`.

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | a) selektiv | b) schwarz |
    |---|---|---|
    | Temperatur Absorber | 51,0 bis 52,1 °C | **50,4 bis 51,1 °C** |
    | Temperatur Glas | 15,8 bis 15,9 °C | **21,7 bis 22,2 °C** |
    | Reaktion Wasser (Nutzwärme) | −0,639 W | **−0,290 W** |
    | Reaktion Luft | +0,182 W | **−0,084 W** |
    | Reaktion Himmel | −0,223 W | **−0,358 W** |
    | Nutzwärme je Meter | 32,0 W/m | **14,5 W/m** |
    | Anteil der Sonne im Wasser | 95 % | **43 %** |

<figure style="text-align:center;">
  <img src="../../../images/p2_roehre_b_absorber.webp" alt="Fall b: Temperatur Absorber, 50,4 bis 51,1 °C" style="width:49%">
  <img src="../../../images/p2_roehre_b_glas.webp" alt="Fall b: Temperatur Glas, 21,7 bis 22,2 °C" style="width:49%">
  <figcaption>Fall b): Absorber fast so warm wie bei a), das Glas aber 6 K wärmer</figcaption>
</figure>

## Was die Zahlen zeigen

<figure style="text-align:center;">
  <img src="../../../images/p2_energiefluss.excalidraw.png" alt="Aufteilung der Sonne auf Wasser und Strahlung zum Glas für a), b) und c)" class="no-lightbox">
</figure>

- Die **Temperatur** des Absorbers ändert sich kaum: Das Wasser hält ihn bei
  rund 50 °C fest.
- Der Unterschied steckt im **Wärmestrom**: Der schwarze Absorber strahlt
  57 % der Sonne zum Glas ab. Das Glas wird wärmer als die Luft, die Reaktion
  **Luft** ist jetzt negativ.
- Im Vakuum entscheidet allein der Emissionsgrad über den Verlust: Deshalb
  sind Vakuumröhren immer selektiv beschichtet.

!!! info "Die Temperatur allein sagt wenig"
    Hätten wir nur die Temperaturen angesehen, wären beide Absorber fast
    gleich gut. Erst die **Reaktion** der Randbedingung **Wasser** zeigt den
    Unterschied. Bei Randbedingungen mit Konvektion und Strahlung lohnt sich
    deshalb immer der Blick auf die Wärmeströme.
