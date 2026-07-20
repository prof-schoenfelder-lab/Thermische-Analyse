---
title: "Praktikum 4: Transiente Temperaturfeldberechnung"
icon: material/clock-fast
---

# Praktikum 4: Transiente Temperaturfeldberechnung

## Lernziele

!!! abstract "Lernziele"
    - Einführung in die Analyse **transienter Temperaturfeldberechnungen**
    - Einstellung des **Zeitschritts** in **Abhängigkeit** der
      **Vernetzungsgröße**

## Inhalte

Als Vorzeigebeispiel wurde eine **ebene Wand** gewählt:

- [Einleitung](Einleitung.md)
- [Beispielaufgabe: Ebene Wand](Beispiel-Ebene-Wand.md)
- [Zusatzaufgabe: Abkühlung Teewasser](Zusatz-Teewasser.md)

![Ebene Wand](images/p4_Untitled_1.png)

## Zusammenfassung des Praktikums

In diesem Praktikum wird die **transiente Temperaturfeldberechnung**
eingeführt. Dabei geht es vor allem um die Unterschiede zur bisherigen
stationären Berechnung:

!!! success "Das Wichtigste in Kürze"
    1. Die **initialen Temperaturbedingungen** sind für die **transiente
       Berechnung — anders als im stationären Fall — von Bedeutung** und
       können über zwei Wege festgelegt werden:

        a) als **konstant** über das gesamte Bauteil (weniger realistisch)

        b) aus dem **Ergebnis einer stationären Berechnung** (realistischer)

    2. Der **Zeitschritt darf nicht kleiner** als $\Delta t_{min}$ bzw. die
       **Elementgröße** (in Richtung des Wärmeflusses) **nicht größer** als
       $\Delta x_{max}$ gewählt werden.

    3. Auch die **Randbedingungen** sind oft **zeitlich veränderlich** und
       sollten dementsprechend berücksichtigt werden.

## Ausblick

Im folgenden Praktikum geht es um **Wärmestrahlung** — auch von
**Körper zu Körper**.
