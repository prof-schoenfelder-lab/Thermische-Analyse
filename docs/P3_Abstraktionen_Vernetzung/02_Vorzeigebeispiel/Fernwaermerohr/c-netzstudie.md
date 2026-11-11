---
title: c) Netzstudie
---

# c) Netzstudie: Wann ist das Netz fein genug?

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** die Elementgröße halbieren, bis sich das Ergebnis um weniger als 1 % ändert, erst überall, dann nur im Dämmring
</div>

Wie fein das Netz sein muss, hängt davon ab, **welche Größe** man auswertet.
Wir verfolgen zwei Größen im Modell aus a):

- den **Wärmeverlust** je Meter, die Reaktion am Vorlauf
- die **größte Wärmestromdichte** an der Innenkante der Dämmung

Das Vorgehen kommt aus der [Vernetzung](../../01_Grundlagen/Vernetzung.md):

<figure style="text-align:center;">
  <img src="../../../images/p3_netzstudie_ablauf.excalidraw.png" alt="Schleife: Modell mit Startnetz rechnen, Elementgröße halbieren und rechnen, bis sich das Ergebnis um weniger als 1 % ändert, erst überall, dann im Dämmring" class="no-lightbox">
</figure>

<!-- Klickanleitung nach dem Klicktest einfügen: <tutorial slug="p3-netzstudie"></tutorial> -->

## Die zweite Größe anlegen

??? tip "Kurzanleitung: Wärmestromdichte an der Innenkante"
    1. In Analyse a): `Rechtsklick Solution (A6) → Insert → Thermal → Total Heat Flux`
    2. **Scoping Method** `Named Selection`, **Named Selection** `Rohr innen`, umbenennen in **Waermestromdichte innen**
    3. Nach dem Lösen steht der größte Wert als **Maximum** im Detailfenster

Ausgewertet wird an der Kante selbst, nicht über einen Pfad.

!!! info "Kontrolle von Hand"
    Verteilt man den Wärmeverlust gleichmäßig auf den Umfang der Innenkante,
    ergibt das

    $$
    \dot q = \frac{\dot Q'}{2\pi\,r_i} = \frac{19{,}5\ \mathrm{W/m}}{2\pi \cdot 0{,}05715\ \mathrm{m}} \approx 54\ \mathrm{W/m^2}
    $$

    - $\dot q$: Wärmestromdichte an der Innenkante, im Mittel über den Umfang
    - $\dot Q'$: Wärmeverlust je Meter Rohr aus a)
    - $r_i$: Innenradius der Dämmung, 57,15 mm

    Oben, wo der Weg zur Oberfläche kürzer ist, liegt der Höchstwert etwas darüber.

## Schritt 1: überall halbieren

Für jede Elementgröße das Netz neu erzeugen, lösen und beide Größen notieren.

??? tip "Kurzanleitung: globale Elementgröße"
    1. `Strukturbaum Mesh`, im `Detailfenster` bei **Element Size** den Wert eintragen
    2. `Rechtsklick Solution (A6) → Solve`, dann die Reaktion Vorlauf und das Maximum der Wärmestromdichte ablesen
    3. Unter `Mesh → Statistics` steht die Zahl der **Elements**

| Elementgröße global | Elemente | Wärmeverlust in W/m | Wärmestromdichte innen max. in W/m² | Änderung |
|---|---|---|---|---|
| 200 mm | | | | |
| 100 mm | | | | |
| 50 mm | | | | |
| 25 mm | | | | |

## Schritt 2: nur im Dämmring verfeinern

Die Temperatur fällt fast ganz im 40 mm dicken Dämmring ab. Dort braucht das Netz
kleine Elemente, im Erdreich nicht. Also das Erdreich grob lassen und nur den
Ring verfeinern.

??? tip "Kurzanleitung: Elementgröße nur im Dämmring"
    1. Globale **Element Size** wieder auf **0,2** m (200 mm)
    2. Oben in der Symbolleiste den Auswahlfilter auf `Body` stellen, die Fläche **Daemmung** anklicken
    3. `Rechtsklick Mesh → Insert → Sizing`, im `Detailfenster` bei **Element Size** den Wert eintragen
    4. Lösen und ablesen wie in Schritt 1

| Elementgröße im Dämmring | Elemente | Wärmeverlust in W/m | Wärmestromdichte innen max. in W/m² | Änderung |
|---|---|---|---|---|
| 40 mm | | | | |
| 20 mm | | | | |
| 10 mm | | | | |
| 5 mm | | | | |

<!-- Tabellen nach dem Klicktest mit den ANSYS-Werten als Lösung füllen; eigener Löser (tools/sollwerte/p3_netzstudie.py): Wärmeverlust überall innerhalb 0,2 %, Wärmestromdichte grob 8 % zu hoch, im Dämmring unter 1 % zwischen 20 und 10 mm (rund 2 400 Elemente), global erst zwischen 25 und 12,5 mm (266 000) -->

### Zum Nachdenken: Welche Größe braucht das feinere Netz?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="p3nsa" name="p3ns">
      <label for="p3nsa">Der Wärmeverlust je Meter</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="p3nsb" name="p3ns">
      <label for="p3nsb">Die größte Wärmestromdichte an der Innenkante</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="p3nsc" name="p3ns">
      <label for="p3nsc">Beide brauchen dasselbe Netz</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Der **Wärmeverlust** ändert sich schon im groben Netz kaum. Er ist eine Summe über die ganze Innenkante
- Die **Wärmestromdichte** ist ein Wert an einer Stelle und kommt aus der Steigung der Temperatur. Sie ändert sich erst in einem feinen Netz kaum noch
- Wenn das Netz nur im Dämmring verfeinert wird, erreicht die Wärmestromdichte dieselbe Genauigkeit mit einem Bruchteil der Elemente

</div>

Weiter mit [d) Pufferspeicher](d-pufferspeicher.md).
