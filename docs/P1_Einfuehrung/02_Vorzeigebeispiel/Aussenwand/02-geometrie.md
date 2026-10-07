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
    2. `Rectangle`, auf den Koordinatenursprung klicken, Maus in Richtung des Rechtecks bewegen (positive x und z), **nicht klicken**: mit `Tab` die Seitenlängen **100 mm** und **100 mm** eingeben, `Enter`. Das ist die Innenfläche der Wand
    3. `Pull` (Taste `P`): die Fläche anklicken und gedrückt halten, in Zugrichtung ziehen (nicht loslassen), `Leertaste` drücken, **175 mm** eingeben, `Enter`. Das ist der Kalksandstein
    4. Die gegenüberliegende Fläche anklicken (sie wird zur Trennfuge) und mit `Strg + C`, `Strg + V` kopieren: Im Strukturbaum erscheint **Surface**
    5. **Surface** anklicken, `Pull`, links unter `Options` **No merge** einschalten. Die Fläche anklicken und gedrückt halten, nach außen ziehen, `Leertaste`, **140 mm**, `Enter`. Das ist die Dämmung
    6. Körper im Strukturbaum umbenennen (`Rechtsklick → Rename`): **Kalksandstein**, **EPS**
    7. `Rechtsklick Design1 → Properties`, unter **Analysis** bei **Share Topology** den Wert **Share** wählen
    8. SpaceClaim schließen

<figure class="anl-bild" style="text-align:center;">
  <img src="../../../../tutorials/p1-geometrie-wand/ablauf.gif" alt="Ablauf der Geometrieerstellung" class="no-lightbox">
  <figcaption>Der ganze Ablauf als Film, die einzelnen Schritte in der Klick-Anleitung darunter</figcaption>
</figure>

<tutorial slug="p1-geometrie-wand"></tutorial>

!!! warning "Warum nicht direkt die Fläche des Kalksandsteins ziehen?"
    Zieht man eine Fläche eines vorhandenen Körpers, wird immer **dieser Körper**
    länger, auch mit *No merge*. Erst die kopierte Fläche (*Surface*) ist ein
    eigenes Objekt: Aus ihr entsteht mit *No merge* ein zweiter Körper.

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
