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

!!! abstract "Was bedeutet die Randbedingung Temperatur?"
    Gerechnet werden Temperaturen, und hier geben wir selbst eine Temperatur
    vor. Auf der Fläche steht damit von vornherein fest, was herauskommt: genau
    20 °C innen und −10 °C außen. ANSYS bestimmt nur noch die Temperaturen
    **im Inneren** der Wand und den Wärmestrom, der dafür durch die Wand fließen
    muss. Die Oberflächentemperatur ist hier also **Eingabe**, nicht Ergebnis.

    In Wirklichkeit kennt man die Oberflächentemperatur meist nicht, sondern die
    Temperatur der Luft davor. Dafür gibt es die Konvektion in
    [Fall b)](b-konvektion.md).

!!! info "Und die anderen vier Seitenflächen?"
    Flächen ohne Randbedingung sind in ANSYS **adiabat**: Über sie fließt keine
    Wärme. Das passt hier, denn wir schneiden ein Stück aus einer langen Wand
    heraus, und die Wärme fließt nur von innen nach außen.

!!! check "Checkpoint"
    `Strukturbaum Steady-State Thermal` anklicken: Im Grafikfenster sind beide
    Randbedingungen mit **A** und **B** markiert. Liegen sie auf den richtigen
    Flächen?
