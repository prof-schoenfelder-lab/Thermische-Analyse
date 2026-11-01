---
title: c) Stillstand
---

# c) Stillstand: Die Pumpe ist aus <small>(optional)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** ohne Wasserstrom rechnen: Wie heiß wird der Absorber?
</div>

Im Sommer ist der Speicher oft schon voll, die Solarpumpe schaltet ab. Die
Sonne scheint trotzdem weiter. Ohne Wasserstrom kann der Absorber seine Wärme
nur noch durch Strahlung loswerden.

??? tip "Kurzanleitung: Wasser abschalten"
    1. Wie in Fall b) eine dritte Analyse **c) Stillstand** an die Zelle **Model** hängen und Randbedingungen und Ergebnisse aus Fall a) übernehmen
    2. Unter **Steady-State Thermal 3 (C5)**: `Rechtsklick Wasser → Suppress`. Die Randbedingung bleibt im Baum, wirkt aber nicht mehr: Die Rohrinnenseite ist jetzt isoliert
    3. `Rechtsklick Solution (C6) → Solve`
    4. Zum Vergleich: In Analyse C bei **Absorber zum Glas** die **Emissivity** auf **0,9** setzen und noch einmal lösen

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | selektiv, ε = 0,05 | schwarz, ε = 0,9 |
    |---|---|---|
    | Temperatur Absorber | **287 °C** | **68 °C** |
    | Temperatur Glas | 26,5 bis 27,6 °C | 24,3 bis 26,3 °C |

## Was die Zahlen zeigen

- Die selektive Beschichtung, die im Betrieb so gut ist, wird im Stillstand
  zum Problem: Der Absorber wird **fast 300 °C** heiß, bevor er so viel
  abstrahlt, wie er von der Sonne aufnimmt.
- Das Glas ist in beiden Fällen gleich warm: Es muss genau die aufgenommene
  Sonne an Luft und Himmel abgeben, egal wie heiß der Absorber dafür wird.
  Die Reaktionen **Luft** und **Himmel** zusammen sollten also −0,672 W
  ergeben. ANSYS kommt auf rund −0,79 W (Luft −0,309 W, Himmel −0,479 W):
  Das ist die Bilanzlücke des 20 mm langen Stücks, siehe Infobox
  „Warum geht die Bilanz nicht genau auf?“ in der [Auswertung](03-auswertung.md).
- In der Praxis verdampft dabei das Wasser in der Röhre. Solaranlagen brauchen
  deshalb ein Ausdehnungsgefäß und hitzefeste Bauteile.
