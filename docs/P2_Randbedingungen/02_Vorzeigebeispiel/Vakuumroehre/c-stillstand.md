---
title: c) Stillstand
---

# c) Stillstand: Die Pumpe ist aus <small>(optional)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** den selektiven Absorber aus a) ohne Wasserstrom rechnen: Wie heiß wird er?
</div>

Im Sommer ist der Speicher oft schon voll, die Solarpumpe schaltet ab. Die
Sonne scheint trotzdem weiter. Ohne Wasserstrom kann der Absorber seine Wärme
nur noch durch Strahlung loswerden.

Gerechnet wird mit dem **selektiven Absorber aus a)**: Randbedingungen und
Ergebnisse werden aus a) kopiert, nicht aus b).

??? tip "Kurzanleitung: Wasser abschalten"
    1. Wie in Fall b) eine dritte Analyse **c) Stillstand** an die Zelle **Model** hängen, die Randbedingungen und die beiden Temperaturen aus Fall a) übernehmen, nicht aus b) (Reaction Probes braucht c) nicht)
    2. Unter **Steady-State Thermal 3 (C5)**: `Rechtsklick Wasser → Suppress`. Die Randbedingung bleibt im Baum, wirkt aber nicht mehr: Die Rohrinnenseite ist jetzt isoliert

<tutorial slug="p2-stillstand"></tutorial>

Dann `Rechtsklick Solution (C6) → Solve`. Den Vergleich mit schwarzem Absorber
(**Emissivity** 0,9 bei **Absorber zum Glas**) nicht selbst rechnen: Die Werte
stehen im Checkpoint, warum, steht in der Warnung darunter.

??? warning "Abbruch oder Temperaturen von Tausenden Grad?"
    Beim schwarzen Absorber bricht ANSYS ab („Temperatur zu hoch“) oder
    liefert Unsinn, z. B. 800 000 °C am Glas. Grund ist die
    Bilanzlücke des 20 mm langen Stücks (siehe
    [Wärmestrahlung: Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect)): Der
    Strahlungsraum erzeugt etwas Energie, und zwar umso mehr, je heißer es
    ist ($\sim T^4$ mit der absoluten Temperatur $T$). Dadurch gibt es neben der echten Lösung eine zweite bei
    absurd hohen Temperaturen. Ohne Wasser hält nichts den Absorber fest, und
    mit dem Emissionsgrad $\varepsilon = 0{,}9$ ist die Kopplung so stark, dass der Löser dorthin
    springen kann.

    Die Werte im Checkpoint lassen sich nur mit vielen kleinen Schritten
    erzwingen: **Initial Temperature** 50 °C und unter
    `Analysis Settings → Step Controls` 100 bis 1000 **Substeps**. Dann bringt
    ANSYS die Sonnenleistung stufenweise auf und bleibt bei der echten Lösung,
    rechnet aber sehr lange. Nachrechnen lohnt sich nicht, zum Vergleich reicht
    der Checkpoint.

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

<figure style="text-align:center;">
  <img src="../../../images/p2_energiefluss.excalidraw.png" alt="Aufteilung der Sonnenleistung auf Wasser und Strahlung zum Glas für a), b) und c)" class="no-lightbox">
</figure>

- Die selektive Beschichtung, die im Betrieb so gut ist, wird im Stillstand
  zum Problem: Der Absorber wird **fast 300 °C** heiß, bevor er so viel
  abstrahlt, wie er von der Sonne aufnimmt. Der schwarze Absorber strahlt so
  gut ab, dass ihm schon **72 °C** reichen.
- Das Glas ist in beiden Fällen gleich warm: Es muss die ganze Sonnenleistung an
  Luft und Himmel abgeben, egal wie heiß der Absorber dafür wird. Dass Luft und
  Himmel zusammen etwa −0,79 W statt −0,672 W zeigen, ist die Bilanzlücke des
  kurzen Stücks (siehe [Auswertung](03-auswertung.md)).
- Die Grafik oben zeigt alle drei Fälle: Im Stillstand geht die ganze
  Sonnenleistung als Strahlung zum Glas.
- In der Praxis verdampft dabei das Wasser in der Röhre. Solaranlagen brauchen
  deshalb ein Ausdehnungsgefäß und hitzefeste Bauteile.

!!! question "Kurz nachdenken"
    In c) wird die Konvektion zum Wasser nur unterdrückt. Man könnte das
    stehende Wasser im Rohr auch als eigenen Körper mit dem Material Wasser
    modellieren. Was ändert sich dadurch an der Lösung? Und wann würde es einen
    Unterschied machen?

    ??? success "Auflösung"
        **Stationär ändert sich nichts:** Der Absorber hat weiter rund 287 °C.
        Das stehende Wasser hat keinen anderen Weg für Wärme als über die
        Rohrwand. Im Gleichgewicht fließt also nichts hinein oder hinaus, das
        Wasser nimmt nur die Temperatur des Rohrs an.

        **Einen Unterschied macht es instationär**, also beim Aufheizen nach dem
        Abschalten der Pumpe: Das Wasser speichert Wärme und bremst das
        Aufheizen. Grob für das 20 mm lange Stück:

        - Wärmekapazität des Wassers: 1,6 g · 4,18 J/(g·K) ≈ 6,6 J/K
        - Wärmekapazität von Rohr und Blech aus Kupfer: 10,5 g · 0,385 J/(g·K) ≈ 4 J/K
        - Anfangs heizt der Absorber mit Wasser um etwa 3,8 K pro Minute auf, ohne Wasser um etwa 10 K pro Minute

        Was das Modell nicht kann: Ab etwa 100 bis 140 °C, je nach Druck in der
        Anlage, verdampft das Wasser. Einen Phasenwechsel kennt das Modell nicht.
