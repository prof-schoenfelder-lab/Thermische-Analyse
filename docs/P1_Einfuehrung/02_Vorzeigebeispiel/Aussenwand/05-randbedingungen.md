---
title: 5 · Randbedingungen
---

# 5 · Randbedingungen <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=../analytische-loesung/" markdown>
🎯 **Jetzt:** Temperaturen anbringen: **innen 20 °C, außen −10 °C**
</div>

## Aufgabenstellung

--8<-- "P1_Einfuehrung/02_Vorzeigebeispiel/Aussenwand/index.md:Randbedingungen_a"

## Umsetzung

??? tip "Kurzanleitung: Temperatur auf eine Fläche"
    1. Mit dem **Flächenauswahltool** die Innenfläche anklicken: die freie große Fläche des Kalksandsteins (nicht die Trennfuge)
        - Drehen: **mittlere Maustaste** · Verschieben: **mittlere Maustaste + Strg**
    2. `Strukturbaum Steady-State Thermal` anklicken
    3. `Reiter Environment → Temperature`
    4. Im `Detailfenster` bei **Magnitude** **20** °C eintragen
    5. `Rechtsklick Temperature → Rename` (oder `F2`): **Innenseite 20 °C**
    6. Genauso die Außenfläche (freie große Fläche der Dämmung) mit **−10 °C**, Name **Außenseite −10 °C**

<!-- TUTORIAL: p1-temperatur-anbringen (Aufnahme Kapitel 6) -->

!!! info "Und die anderen vier Seitenflächen?"
    Flächen ohne Randbedingung sind in ANSYS **adiabat**: Über sie fließt keine
    Wärme. Das passt hier, denn wir schneiden ein Stück aus einer langen Wand
    heraus, und die Wärme fließt nur von innen nach außen.

!!! check "Checkpoint"
    `Strukturbaum Steady-State Thermal` anklicken: Im Grafikfenster sind beide
    Randbedingungen mit **A** und **B** markiert. Liegen sie auf den richtigen
    Flächen?

[Weiter zu Schritt 6: Lösen →](06-loesen.md){ .md-button .md-button--primary }
