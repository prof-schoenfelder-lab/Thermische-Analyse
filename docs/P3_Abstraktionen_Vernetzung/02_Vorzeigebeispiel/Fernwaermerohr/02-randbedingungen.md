---
title: 2 · Randbedingungen
---

# 2 · Randbedingungen <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** die beiden Kanten benennen und dort die Temperaturen anbringen
</div>

## Aufgabenstellung

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Randbedingungen"

## Kanten benennen: Named Selections

Im 2D-Modell sitzen Randbedingungen auf **Kanten** statt auf Flächen. Wie in
Praktikum 2 legen wir die beiden Kanten einmal als Named Selection an, mit
**Entity Type** `Edge`:

| Name | Entity Type | Criterion | Value | für |
|---|---|---|---|---|
| Rohr innen | Edge | Radius | 0,05715 m (57,15 mm) | Vorlauf 80 °C |
| Oberflaeche | Edge | Location Y | 0,9 m (900 mm) | Oberfläche 10 °C |

??? tip "Kurzanleitung: Named Selection über das Worksheet"
    1. `Rechtsklick Strukturbaum Model (A4) → Insert → Named Selection`
    2. Im `Detailfenster` bei **Scoping Method** `Worksheet` wählen
    3. Unten im Worksheet `Rechtsklick → Add Row`, in der Zeile **Entity Type**, **Criterion** und **Value** wie in der Tabelle eintragen
    4. `Generate`, dann im Strukturbaum mit `F2` umbenennen

!!! check "Checkpoint"
    **Rohr innen** ist ein Kreis, **Oberflaeche** die obere Kante des Blocks,
    6 m lang. Im Detailfenster der Named Selection steht unter **Statistics**
    bei beiden **1** Kante.

## Temperaturen anbringen

??? tip "Kurzanleitung: zwei Temperaturen"
    1. `Rechtsklick Steady-State Thermal (A5) → Insert → Temperature`, **Scoping Method** `Named Selection`, **Named Selection** `Rohr innen`, **Magnitude** **80** °C, im Strukturbaum mit `F2` umbenennen in **Vorlauf**
    2. Genauso mit `Oberflaeche` und **10** °C, umbenennen in **Oberflaeche**

Seiten und Unterkante bekommen **keine** Randbedingung: Ränder ohne
Randbedingung sind adiabat, über sie fließt keine Wärme (siehe
[Praktikum 2](../../../P2_Randbedingungen/01_Grundlagen/Randbedingungen.md)).

Weiter mit [Lösen und Auswerten](03-auswertung.md).
