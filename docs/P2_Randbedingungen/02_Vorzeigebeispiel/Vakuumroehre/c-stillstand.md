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
    4. Den Vergleich mit schwarzem Absorber (**Emissivity** 0,9 bei **Absorber zum Glas**) nicht selbst rechnen: Die Werte stehen im Checkpoint, warum, steht in der Warnung darunter

!!! warning "Abbruch oder Temperaturen von Tausenden Grad?"
    Beim schwarzen Absorber bricht ANSYS ab („Temperatur zu hoch“) oder
    liefert Unsinn, z. B. 800 000 °C am Glas. Grund ist die
    Bilanzlücke des 20 mm langen Stücks (siehe
    [Wärmestrahlung: Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect)): Der
    Strahlungsraum erzeugt etwas Energie, und zwar umso mehr, je heißer es
    ist ($\sim T^4$). Dadurch gibt es neben der echten Lösung eine zweite bei
    absurd hohen Temperaturen. Ohne Wasser hält nichts den Absorber fest, und
    mit $\varepsilon = 0{,}9$ ist die Kopplung so stark, dass der Löser dorthin
    springen kann.

    Die Werte im Checkpoint haben wir mit vielen kleinen Schritten erzwungen:
    **Initial Temperature** 50 °C und unter `Analysis Settings → Step Controls`
    100 bis 1000 **Substeps**. Dann bringt ANSYS die Sonne stufenweise auf und
    bleibt bei der echten Lösung, rechnet aber sehr lange. Nachrechnen lohnt
    sich nicht, zum Vergleich reicht der Checkpoint.

    Merke: Ein Ergebnis immer an der Physik prüfen. Glas mit Tausenden Grad
    unter 700 W/m² Sonne kann nicht stimmen, egal wie bunt das Bild ist.

!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | selektiv, ε = 0,05 | schwarz, ε = 0,9 |
    |---|---|---|
    | Temperatur Absorber | **287 °C** | **72 °C** |
    | Temperatur Glas | 26,5 bis 27,6 °C | 26,5 bis 27,4 °C |

<figure style="text-align:center;">
  <img src="../../../images/p2_roehre_c_absorber.webp" alt="Fall c selektiv: Temperatur Absorber, 287 °C" style="width:49%">
  <img src="../../../images/p2_roehre_c_glas.webp" alt="Fall c selektiv: Temperatur Glas, 26,5 bis 27,6 °C" style="width:49%">
  <figcaption>Fall c) selektiv: Ohne Wasser wird der Absorber fast 300 °C heiß</figcaption>
</figure>

<figure style="text-align:center;">
  <img src="../../../images/p2_roehre_c_schwarz_absorber.webp" alt="Fall c schwarz: Temperatur Absorber, 72 °C" style="width:49%">
  <img src="../../../images/p2_roehre_c_schwarz_glas.webp" alt="Fall c schwarz: Temperatur Glas, 26,5 bis 27,4 °C" style="width:49%">
  <figcaption>Fall c) schwarz: Der Absorber bleibt bei 72 °C, das Glas ist so warm wie beim selektiven Absorber</figcaption>
</figure>

## Was die Zahlen zeigen

- Die selektive Beschichtung, die im Betrieb so gut ist, wird im Stillstand
  zum Problem: Der Absorber wird **fast 300 °C** heiß, bevor er so viel
  abstrahlt, wie er von der Sonne aufnimmt. Der schwarze Absorber strahlt so
  gut ab, dass ihm schon **72 °C** reichen.
- Das Glas ist in beiden Fällen gleich warm: Es muss genau die aufgenommene
  Sonne an Luft und Himmel abgeben, egal wie heiß der Absorber dafür wird.
  Die Reaktionen **Luft** und **Himmel** zusammen sollten also −0,672 W
  ergeben. ANSYS kommt auf rund −0,78 bis −0,79 W (selektiv: Luft −0,309 W,
  Himmel −0,479 W; schwarz: Luft −0,304 W, Himmel −0,476 W):
  Das ist die Bilanzlücke des 20 mm langen Stücks, siehe Infobox
  „Warum geht die Bilanz nicht genau auf?“ in der [Auswertung](03-auswertung.md).
- In der Praxis verdampft dabei das Wasser in der Röhre. Solaranlagen brauchen
  deshalb ein Ausdehnungsgefäß und hitzefeste Bauteile.
