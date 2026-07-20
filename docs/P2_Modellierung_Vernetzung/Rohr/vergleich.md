---
title: Vergleich
---

# Vergleich der Abstraktionen

<div class="task-banner" data-tabs="Aufgabe=../|a) Vollmodell=../01-material/|b) Viertelmodell=../b-viertelmodell/|c) Rotationssym.=../c-rotationssymmetrie/|Vergleich=../vergleich/" markdown>
🎯 **Jetzt:** Ergebnis-Check: Was haben die Abstraktionen gebracht?
</div>

Im **Ergebnis** zeigt sich zwischen den drei Modellen kein Unterschied:

![Vergleich Temperatur](../images/rohr_Ergebnis_T.png)

![Vergleich Wärmestromdichte](../images/rohr_Ergebnis_W.png)

In der **Berechnungszeit** dagegen deutlich:

| Modell | Rechenzeit |
|---|---|
| a) 3D-Vollmodell | **3,8 s** |
| b) 3D-Viertelmodell | **0,9 s** |
| c) 2D-Rotationssymmetrie | **0,4 s** |

??? note "Für Neugierige: Wo steht die Berechnungszeit?"
    `Solution Information → Solver Output`

    ![Solver Output](../images/rohr_Untitled_24.png)

    ![Solver Output Zeit](../images/rohr_Untitled_25.png)

!!! success "Merke"
    **Abstraktionen** erreichen die **gleiche Genauigkeit** bei **stark
    reduzierter Rechenzeit** — sie sollten, wann immer möglich, angewendet
    werden. Bei diesem Mini-Beispiel wirkt eine Sekunde egal; bei
    transienten Analysen mit tausenden Zeitschritten entscheidet genau das
    über Minuten oder Tage.
