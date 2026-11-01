---
title: 2 · Randbedingungen
---

# 2 · Randbedingungen <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Selektiv=../01-modell/|b) Schwarz=../b-schwarz/|c) Stillstand=../c-stillstand/" markdown>
🎯 **Jetzt:** Sonne, Wasser, Luft, Himmel und die Strahlung zwischen Absorber und Glas anbringen
</div>

## Aufgabenstellung

--8<-- "P2_Randbedingungen/02_Vorzeigebeispiel/Vakuumroehre/index.md:Randbedingungen"

Alle Randbedingungen kommen über `Rechtsklick Strukturbaum Steady-State Thermal → Insert → …`
(oder `Reiter Environment`). Jede Randbedingung gleich mit `F2` sinnvoll benennen,
z. B. **Sonne**, **Wasser**: Das hilft später bei der Auswertung.

## Sonne: Wärmestromdichte

??? tip "Kurzanleitung: Heat Flux"
    1. Oben `Face` anklicken, die **Oberseite** des linken Blechflügels anklicken, mit `Strg` die Oberseite des rechten dazunehmen (nicht das Rohr)
    2. `Insert → Heat Flux`, **Magnitude** **700** W/m²
    3. Umbenennen in **Sonne**

!!! info "Warum Heat Flux?"
    Die Sonne liefert eine bekannte Leistung **je Fläche**, unabhängig davon,
    wie warm der Absorber ist. Positiv heißt: Wärme geht in das Bauteil hinein.

## Wasser und Luft: Konvektion

??? tip "Kurzanleitung: zweimal Convection"
    1. Die **Innenfläche des Kupferrohrs** anklicken (Ansicht drehen, ins Rohr schauen), `Insert → Convection`, **Film Coefficient** **1000** W/m²·°C, **Ambient Temperature** **50** °C, umbenennen in **Wasser**
    2. Die **Außenfläche des Glases** anklicken, `Insert → Convection`, **10** W/m²·°C und **20** °C, umbenennen in **Luft**

## Glas zum Himmel: Strahlung To Ambient

??? tip "Kurzanleitung: Radiation To Ambient"
    1. Wieder die **Außenfläche des Glases** anklicken (sie hat schon die Konvektion, das ist gewollt)
    2. `Insert → Radiation`
    3. **Correlation** bleibt **To Ambient**, **Emissivity** **0,9**, **Ambient Temperature** **5** °C
    4. Umbenennen in **Himmel**

!!! abstract "Konvektion und Strahlung auf derselben Fläche"
    Die Glasfläche gibt Wärme an die Luft **und** an den Himmel ab. Beide
    Randbedingungen gelten gleichzeitig, ihre Wärmeströme addieren sich.
    **Ambient Temperature** ist bei der Strahlung die Temperatur des
    Himmels, nicht der Luft.

## Absorber zum Glas: Strahlung Surface to Surface

??? tip "Kurzanleitung: Radiation Surface to Surface"
    1. Alle Außenflächen des **Absorbers** mit `Strg` auswählen: Ober- und Unterseite beider Blechflügel und die Außenfläche des Kupferrohrs (oben und unten). Die beiden schmalen Stirnkanten der Bleche (0,5 mm) dürfen fehlen. Nicht dazu gehören die Rohrinnenseite und die beiden Schnittflächen vorn und hinten
    2. `Insert → Radiation`, **Correlation** **Surface To Surface**, **Emissivity** **0,05**, **Enclosure** **1**, **Enclosure Type** **Perfect**, umbenennen in **Absorber zum Glas**
    3. Die **Innenfläche des Glases** anklicken, `Insert → Radiation`, **Surface To Surface**, **Emissivity** **0,9**, **Enclosure** **1**, **Enclosure Type** **Perfect**, umbenennen in **Glas zum Absorber**

!!! abstract "Warum Enclosure 1 und Perfect?"
    - Gleiche **Enclosure**-Nummer heißt: Diese Flächen strahlen sich
      gegenseitig an. ANSYS berechnet selbst, wie viel jede Fläche von jeder
      anderen sieht (Sichtfaktor).
    - Unser 20 mm langes Stück ist vorn und hinten offen. In der echten,
      langen Röhre geht dort aber keine Strahlung verloren: Was hinausgeht,
      trifft das Nachbarstück, und genauso viel kommt von dort zurück.
      **Perfect** bildet das nach: Der Raum zwischen Absorber und Glas gilt
      als geschlossen.
    - Eine Umgebungstemperatur gibt es hier nicht: Die Temperatur der
      Gegenseite rechnet ANSYS selbst aus.
    - Ganz genau ist Perfect bei einem so kurzen Stück nicht, die Bilanz geht
      später um einige Prozent nicht auf. Warum, steht unter
      [Wärmestrahlung: Der Haken an Perfect](../../01_Grundlagen/Strahlung.md#haken-perfect).

## Was bleibt frei?

Die beiden Schnittflächen vorn und hinten bekommen **keine** Randbedingung:
Sie sind isoliert. Das passt, denn entlang der Röhre fließt keine Wärme.

!!! check "Checkpoint"
    `Strukturbaum Steady-State Thermal` aufklappen: Unter **Initial Temperature**
    und **Analysis Settings** stehen **sechs** Randbedingungen: Sonne, Wasser,
    Luft, Himmel, Absorber zum Glas, Glas zum Absorber.

Weiter mit [Lösen und Auswerten](03-auswertung.md).
