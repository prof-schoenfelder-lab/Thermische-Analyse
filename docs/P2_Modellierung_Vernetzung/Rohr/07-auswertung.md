---
title: 7 · Auswertung
---

# 7 · Lösungsdarstellung <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Vollmodell=../01-material/|b) Viertelmodell=../b-viertelmodell/|c) Rotationssym.=../c-rotationssymmetrie/|Vergleich=../vergleich/" markdown>
🎯 **Aufgabe:** Temperaturverlauf und Wärmestromdichte von der Innen- zur Außenfläche bestimmen
</div>

**Temperatur** und **Wärmestromdichte (Total Heat Flux)** von der Innen- zur
Außenfläche als **Pfad** darstellen.

??? tip "Kurzanleitung: Auswertung als Pfad"
    1. **Kantenauswahltool** auswählen
        ![Kantenauswahltool](../images/rohr_Untitled_6.png)
    2. Eine Kante wählen, die von innen nach außen verläuft (grün markiert)
        ![Kante auswählen](../images/rohr_Untitled_7.png)
    3. `Rechtsklick Solution → Insert → Thermal → Temperature`
        ![Insert Temperature](../images/rohr_Untitled_8.png)
    4. `Rechtsklick Temperature → Convert to Path Result`
        ![Convert to Path Result](../images/rohr_Untitled_9.png)
    5. `Rechtsklick Solution → Evaluate All Results`
        ![Evaluate All Results](../images/rohr_Untitled_10.png)

!!! tip "Zweite Auswertung (Wärmestromdichte)"
    Für den zweiten Pfad **Total Heat Flux** einfügen und im Detailfenster
    `Scoping Method → Path` den vorhandenen Pfad wählen (nicht erneut
    „Convert to Path Result").

[KLICK-TUTORIAL: Lösungsdarstellung (aus Praktikum 1)](http://ior.ad/6XCx){target=_blank .md-button}

!!! check "Checkpoint: So sollte die Lösung aussehen"
    **Temperatur** von außen nach innen:

    ![Temperaturverlauf a](../images/rohr_Untitled_11.png)

    **Wärmestromdichte** von außen nach innen:

    ![Wärmestromdichte a](../images/rohr_Untitled_12.png)

**Fall a) geschafft!** Jetzt das gleiche Ergebnis mit einem Viertel des
Modells: [b) Viertelmodell →](b-viertelmodell.md){ .md-button .md-button--primary }
