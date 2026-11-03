---
title: 2 · Randbedingungen
---

# 2 · Randbedingungen <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** Flächen benennen, dann Sonne, Wasser, Luft, Himmel und die Strahlung zwischen Absorber und Glas anbringen
</div>

## Aufgabenstellung

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Randbedingungen"

## Flächen benennen: Named Selections

Statt die Flächen bei jeder Randbedingung im Grafikfenster anzuklicken, legen
wir sie einmal als **Named Selection** an. Das Worksheet findet sie über eine
Regel, zum Beispiel „alle Flächen mit Radius 5 mm“. Bei den Randbedingungen
wählt man danach nur noch den Namen aus einer Liste.

??? tip "Kurzanleitung: Named Selection über das Worksheet"
    1. `Rechtsklick Strukturbaum Model (A4) → Insert → Named Selection`
    2. Im `Detailfenster` bei **Scoping Method** `Worksheet` wählen
    3. Unten im Worksheet `Rechtsklick → Add Row`, in der Zeile **Entity Type**, **Criterion** und **Value** wie in der Tabelle eintragen
    4. `Generate`, dann im Strukturbaum mit `F2` umbenennen

<tutorial slug="p2-named-selection"></tutorial>

!!! tip "Tipp: ab der zweiten Named Selection duplizieren"
    - Rechtsklick im Strukturbaum auf eine fertige Named Selection → `Duplicate`
    - In der Kopie im Worksheet nur **Criterion** und **Value** ändern, `Generate`, mit `F2` umbenennen
    - Beispiel: „Glas aussen“ duplizieren und den Value auf 0,0325 m (32,5 mm) setzen, das ergibt „Glas innen“
    - Beispiel: „Oberseiten Blech“ duplizieren und im Worksheet mit `Rechtsklick → Add Row` die Zeilen 2 und 3 aus der Tabelle unten ergänzen, das ergibt „Absorber aussen“

Diese fünf Named Selections braucht die Röhre. Die Zeilen mit **Location**
hängen davon ab, welche Achse in Ihrem Modell **senkrecht zum Blech** steht
(im Bild unten senkrecht), je nachdem, wie das Rechteck in der Skizze liegt.
Am Achsenkreuz unten links im Grafikfenster ablesen und hier wählen, die
Tabelle passt sich an (die Klickanleitung zeigt X):

<div class="achsenwahl"></div>

| Name | Entity Type | Criterion | Value | für |
|---|---|---|---|---|
| Oberseiten Blech | Face | Location <span class="aw-achse">X</span> | 0,00025 m (0,25 mm) | Sonne |
| Rohr innen | Face | Radius | 0,005 m (5 mm) | Wasser |
| Glas aussen | Face | Radius | 0,035 m (35 mm) | Luft und Himmel |
| Glas innen | Face | Radius | 0,0325 m (32,5 mm) | Glas zum Absorber |
| Absorber aussen, Zeile 1 | Face | Location <span class="aw-achse">X</span> | 0,00025 m (0,25 mm) | Absorber zum Glas |
| Absorber aussen, Zeile 2 | Face | Location <span class="aw-achse">X</span> | −0,00025 m (−0,25 mm) | Absorber zum Glas |
| Absorber aussen, Zeile 3 | Face | Radius | 0,006 m (6 mm) | Absorber zum Glas |

<figure style="text-align:center;">
  <img src="../../../images/p2_named_selections.excalidraw.png" alt="Die fünf Named Selections im Querschnitt, die Flächen jeweils rot: Oberseiten Blech, Rohr innen, Glas aussen, Glas innen, Absorber aussen" class="no-lightbox">
  <figcaption>Querschnitt, nicht maßstäblich (Rohr und Blech vergrößert): rot die Flächen der Named Selection, jede rote Linie ist eine Fläche über die ganze Länge</figcaption>
</figure>

Die Zeilen mit **Radius** gelten unabhängig von der Achse.

!!! check "Checkpoint"
    Nach `Generate` steht im `Detailfenster` unter **Total Selection**:
    Oberseiten Blech **2 Faces**, Absorber aussen **6 Faces**, die übrigen
    je **1 Face**.

## Sonne: Wärmestromdichte

??? tip "Kurzanleitung: Heat Flux"
    1. `Rechtsklick Strukturbaum Steady-State Thermal (A5) → Insert → Heat Flux`
    2. **Scoping Method** `Named Selection`, **Named Selection** `Oberseiten Blech`
    3. **Magnitude** **700** W/m², umbenennen in **Sonne**

<tutorial slug="p2-sonne"></tutorial>

!!! info "Warum eine Wärmestromdichte?"
    Die Sonne liefert eine bekannte Leistung **je Fläche**, unabhängig davon,
    wie warm der Absorber ist. Positiv heißt: Wärme geht in das Bauteil hinein.

## Wasser und Luft: Konvektion

??? tip "Kurzanleitung: zweimal Convection"
    1. `Insert → Convection`, **Named Selection** `Rohr innen`, **Film Coefficient** **1000** W/m²·°C, **Ambient Temperature** **50** °C, umbenennen in **Wasser**
    2. Zweite `Convection` auf `Glas aussen` mit **10** W/m²·°C und **20** °C, umbenennen in **Luft**

<tutorial slug="p2-konvektion"></tutorial>

## Glas zum Himmel: Strahlung To Ambient

??? tip "Kurzanleitung: Radiation To Ambient"
    1. `Insert → Radiation`, **Named Selection** `Glas aussen`: dieselbe Fläche wie die Luft
    2. **Correlation** bleibt **To Ambient**, **Emissivity** **0,9**, **Ambient Temperature** **5** °C
    3. Umbenennen in **Himmel**

<tutorial slug="p2-strahlung-himmel"></tutorial>

!!! abstract "Konvektion und Strahlung auf derselben Fläche"
    Die Glasfläche gibt Wärme an die Luft **und** an den Himmel ab. Beide
    Randbedingungen gelten gleichzeitig, ihre Wärmeströme addieren sich.
    **Ambient Temperature** ist bei der Strahlung die Temperatur des
    Himmels, nicht der Luft.

!!! question "Kurz nachdenken: Sieht das Glas nur den Himmel?"
    Hier strahlt die ganze Außenfläche des Glases zum Himmel mit 5 °C. Die
    untere Hälfte der Röhre sieht aber den Boden, und der ist etwa so warm wie
    die Luft (20 °C). Wird das Glas dadurch wärmer oder kälter? Und was
    passiert mit der Nutzwärme?

    ??? success "Auflösung"
        - Das Glas wird **wärmer**: Die untere Hälfte strahlt zu einem wärmeren Gegenüber und verliert weniger. Nach Handrechnung etwa 18,1 statt 15,7 °C
        - Die **Nutzwärme** ändert sich kaum (+0,3 %): Der selektive Absorber strahlt ohnehin nur wenig zum Glas, wie warm das Glas ist, spielt für ihn kaum eine Rolle
        - Genauer wären zwei Strahlungsrandbedingungen: obere Hälfte zum Himmel, untere zum Boden ([Wärmestrahlung](../../01_Grundlagen/Strahlung.md#welche-temperatur-ist-die-ambient-temperature))
        - Für dieses Beispiel reicht die Vereinfachung

## Absorber zum Glas: Strahlung Surface to Surface

??? tip "Kurzanleitung: Radiation Surface to Surface"
    1. `Insert → Radiation`, **Named Selection** `Absorber aussen`, **Correlation** **Surface To Surface**, **Emissivity** **0,05**, **Enclosure** **1**, **Enclosure Type** **Perfect**, umbenennen in **Absorber zum Glas**
    2. Genauso mit `Glas innen` und **Emissivity** **0,9**: **Glas zum Absorber**

<tutorial slug="p2-strahlung-s2s"></tutorial>

??? abstract "Warum Enclosure 1 und Perfect?"
    - Gleiche **Enclosure**-Nummer heißt: Diese Flächen strahlen sich
      gegenseitig an. Wie viel jede Fläche von jeder anderen sieht
      (Sichtfaktor), rechnet ANSYS selbst aus.
    - Unser Stück ist vorn und hinten offen. In der langen Röhre trifft, was
      dort hinausgeht, das Nachbarstück, und genauso viel kommt zurück.
      **Perfect** bildet das nach: Der Raum gilt als geschlossen, eine
      Umgebungstemperatur gibt es nicht.
    - Ganz genau ist das bei 20 mm nicht, die Bilanz geht später um einige
      Prozent nicht auf: [Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect).

## Was bleibt frei?

Die beiden Schnittflächen vorn und hinten bekommen **keine** Randbedingung:
Sie sind isoliert. Das passt, denn entlang der Röhre fließt keine Wärme.

!!! check "Checkpoint"
    `Strukturbaum Steady-State Thermal` aufklappen: Unter **Initial Temperature**
    und **Analysis Settings** stehen **sechs** Randbedingungen: Sonne, Wasser,
    Luft, Himmel, Absorber zum Glas, Glas zum Absorber.

Weiter mit [Lösen und Auswerten](03-auswertung.md).
