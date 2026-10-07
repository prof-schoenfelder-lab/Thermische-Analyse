---
title: 2 · Geometrie
---

# 2 · Geometrie <small>(SpaceClaim)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Wand aus **zwei Körpern** erstellen, **175 mm + 140 mm** dick, **100 × 100 mm**
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Geometrie"

## Umsetzung

SpaceClaim arbeitet anders als klassische CAD-Programme: Es gibt keinen
Skizzen-Verlauf, den man nachträglich ändert. Stattdessen fasst man die
Geometrie direkt an (Fläche ziehen, verschieben).

!!! info "Firewall-Abfrage beim ersten Start"
    Beim ersten Öffnen von `SpaceClaim` fragt Windows, ob die Firewall der App
    den Zugriff erlauben soll. Die Abfrage mit `Abbrechen` ablehnen, SpaceClaim
    funktioniert trotzdem.

??? tip "Kurzanleitung: Wand mit zwei Schichten"
    1. `Rechtsklick Geometry → New SpaceClaim Geometry...`
    2. Skizze: Rechteck **100 mm × 100 mm** zeichnen, das ist die Innenfläche der Wand (Werte mit `Tab` wechseln, mit `Enter` bestätigen)
    3. `Pull` (Taste `P`): die Fläche um **175 mm** ziehen, das ist der Kalksandstein
    4. Die gegenüberliegende große Fläche anklicken und mit `Pull` um weitere **140 mm** ziehen. Dabei im Optionsfenster **Kein Zusammenführen** (*No merge*) wählen, damit ein **zweiter Körper** entsteht. Die angeklickte Fläche wird zur Trennfuge
    5. Körper im Strukturbaum sinnvoll benennen: **Kalksandstein**, **EPS**
    6. `Reiter Workbench → Share`: Die beiden Körper teilen sich jetzt die Fläche in der Trennfuge
    7. SpaceClaim schließen

<!-- TUTORIAL: p1-geometrie-wand (Aufnahme Kapitel 3) -->
<!-- TODO: Kurzanleitung beim Aufnehmen mit SpaceClaim 2025 R2 abgleichen (Optionsname No merge, Share) -->

!!! info "Innen, außen, Trennfuge"
    Die Wand hat zwei große Flächen mit Randbedingung: **innen** die freie Fläche
    des Kalksandsteins (Raumseite), **außen** die freie Fläche der Dämmung
    (Wetterseite). Dazwischen liegt die **Trennfuge**. Die vier schmalen
    Seitenflächen bleiben ohne Randbedingung.

!!! warning "Warum Share Topology?"
    Ohne *Share* sind es zwei getrennte Körper, und ANSYS verbindet sie über
    einen **Kontakt**. Mit *Share* gehören die Knoten in der Trennfuge zu
    beiden Körpern: Die Wärme geht ohne Umweg über einen Kontakt hindurch.
    Kontakte schauen wir uns in diesem Kurs nicht an.

<!-- TODO: Datei P1_Aussenwand.scdoc als Download ablegen (files/) -->

[Weiter zu Schritt 3: Zuweisung →](03-zuweisung.md){ .md-button .md-button--primary }
