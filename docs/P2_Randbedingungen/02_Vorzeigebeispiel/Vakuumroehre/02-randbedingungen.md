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

Diese fünf Named Selections braucht die Röhre:

| Name | Entity Type | Criterion | Value | für |
|---|---|---|---|---|
| Oberseiten Blech | Face | Location X | 0,00025 m | Sonne |
| Rohr innen | Face | Radius | 0,005 m | Wasser |
| Glas aussen | Face | Radius | 0,035 m | Luft und Himmel |
| Glas innen | Face | Radius | 0,0325 m | Glas zum Absorber |
| Absorber aussen | Face | Location X, Location X, Radius (drei Zeilen) | 0,00025 m, −0,00025 m, 0,006 m | Absorber zum Glas |

**Location X** ist die Achse, in der das Blech 0,5 mm dick ist. Findet
`Generate` nicht die erwartete Zahl an Flächen, `Location Y` oder `Location Z`
probieren.

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
