---
title: c) Rotationssymmetrie (2D)
---

# c) Rotationssymmetrie (2D)

<div class="task-banner" data-tabs="Aufgabe=../|a) Vollmodell=../01-material/|b) Viertelmodell=../b-viertelmodell/|c) Rotationssym.=../c-rotationssymmetrie/|Vergleich=../vergleich/" markdown>
🎯 **Aufgabe:** Temperaturverlauf und Wärmestromdichte von der Innen- zur Außenfläche bestimmen
</div>

Neue Steady-State-Thermal-Analyse anlegen („c) Rotationssymmetrie (2D)").
Material wie in a) (keine Aktion nötig). Die Besonderheiten stecken in
Geometrie und Randbedingungen:

## Geometrie (SpaceClaim)

!!! warning "Wichtige Änderung für 2D"
    **Workbench:** `Rechtsklick Geometry → Properties → Analysis Type → 2D`

    **SpaceClaim:** Skizze auf der **x-y-Ebene** erstellen — die **y-Achse
    ist die Rotationsachse**, gezeichnet wird in positiver x-Richtung.

[KLICK-TUTORIAL: Rohr als Rotationssymmetrie 2D](http://ior.ad/6Z4P){target=_blank .md-button}
[:material-download: Rohr_2D_RotSym.scdoc](../files/Rohr_2D_RotSym.scdoc)

Im Mechanical dann: `Geometry → Detailfenster → 2D Behavior → Axisymmetric`

![2D Behavior Axisymmetric](../images/rohr_Untitled_15.png)

## Netz (Mechanical)

Für den Vergleich mit a) die gleiche Elementgröße einstellen:
`Mesh → Detailfenster → Element Size: 1 mm` (**Einheiten beachten!**),
dann `Rechtsklick Mesh → Generate Mesh`.

!!! check "Checkpoint: So sollte das Netz aussehen"
    ![Netz 2D](../images/rohr_Untitled_17.png)

## Randbedingungen (Mechanical)

Innen 100 °C, außen 20 °C — **aber auf Kanten statt Flächen**: Durch die
Rotationssymmetrie sind aus den Flächen Kanten geworden
(**Kantenauswahltool** verwenden, sonst wie in
[Schritt 5 von Fall a](05-randbedingungen.md)).

!!! check "Checkpoint: So sollten die Randbedingungen aussehen"
    ![Randbedingungen 2D](../images/rohr_Untitled_20.png)

## Lösen & Auswertung

Lösen und als Pfad auswerten wie in [Schritt 7 von Fall a](07-auswertung.md)
(Pfadkante: eine Kante von innen nach außen).

!!! check "Checkpoint: So sollte die Lösung aussehen"
    ![Temperaturverlauf c](../images/rohr_Untitled_22.png)

    ![Wärmestromdichte c](../images/rohr_Untitled_23.png)

[Weiter zum Vergleich →](vergleich.md){ .md-button .md-button--primary }
