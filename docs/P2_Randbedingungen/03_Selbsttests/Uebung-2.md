---
title: "Übung 2: Kühlkörper eines Wechselrichters"
---

# Übung 2: Kühlkörper eines Wechselrichters

Der Wechselrichter einer Photovoltaikanlage wandelt Gleichstrom in Wechselstrom.
Seine Leistungshalbleiter sitzen in einem Modul, das laut Datenblatt **40 W**
Verlustleistung abgibt. Ein Aluminium-Kühlkörper im Gehäuse des Wechselrichters
führt die Wärme ab. Das Gehäuse ist dicht gegen Staub und Feuchte: Die
Verlustwärme heizt die Luft darin auf und kommt nur durch die Gehäusewände nach
draußen, innen ist es deshalb wärmer als draußen. Gerechnet wird ein heißer
Sommertag. Unter dem Modul darf der Kühlkörper höchstens **100 °C** warm werden.
Reicht dafür blankes Aluminium, oder muss er schwarz eloxiert sein?

<figure style="text-align:center;">
  <img src="../../images/p2_kuehlkoerper.excalidraw.png" alt="Kühlkörper mit 8 Rippen, Maße, Modul 50 × 50 mm mit 40 W unter der Grundplatte, Rückseite daneben isoliert" class="no-lightbox">
</figure>

<figure style="text-align:center;">
  <img src="../../images/p2_gehaeuse.excalidraw.png" alt="Der Kühlkörper sitzt im dichten Gehäuse des Wechselrichters: draußen 30 °C, Luft im Gehäuse 40 °C, Gehäusewände innen 40 °C, das Modul mit 40 W unter der Grundplatte" class="no-lightbox" style="width:100%;max-width:640px">
  <figcaption>Die Situation an einem heißen Sommertag</figcaption>
</figure>

!!! tip "Nur den Kühlkörper modellieren"
    - Modellieren Sie nur den Kühlkörper, nicht das Gehäuse
    - Welche Randbedingungen aus der Situation folgen, entscheiden Sie selbst: Das ist Teil der Aufgabe

## Gegeben

**Material**

- Aluminium: Wärmeleitfähigkeit $\lambda = 200\ \mathrm{W/(m\,K)}$

**Geometrie**

- Grundplatte 100 mm × 100 mm, 8 mm dick
- 8 Rippen, je 2 mm dick, 40 mm hoch, 100 mm lang; die äußeren Rippen schließen bündig mit der Platte ab, Abstand von Rippe zu Rippe 14 mm (Mitte zu Mitte)
- Modul 50 mm × 50 mm mittig auf der Rückseite

**Netz**

- Netzgröße global **2,5 mm**

**Wärme und Oberflächen**

- Das Modul gibt seine 40 W über die Fläche unter dem Modul in den Kühlkörper ab
- Die Rückseite neben dem Modul liegt isoliert am Gehäuse
- Freie Konvektion an die Luft im Gehäuse: Wärmeübergangskoeffizient $\alpha = 6\ \mathrm{W/(m^2\,K)}$
- Emissionsgrad: a) schwarz eloxiert $\varepsilon = 0{,}85$, b) blank $\varepsilon = 0{,}05$
- Temperaturen: im Bild der Situation

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <ul>
      <li>Rippen als Muster: eine Rippe zeichnen und mit <code>Move</code> und der Option <strong>Create Patterns</strong> in 14 mm Abstand auf 8 Rippen vervielfachen, sodass ein einziger Körper entsteht</li>
      <li>Fläche für das Modul: auf der Rückseite ein Rechteck <strong>50 × 50</strong> mm aus der Mitte skizzieren (<code>Rectangle</code> mit <strong>Define rectangle from center</strong>), die Skizze teilt die Rückseite in zwei Flächen</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Viele Flächen auf einmal</p>
    <ul>
      <li>Oben <code>Face</code> wählen, mit <code>Strg + A</code> alle Flächen auswählen und einzelne Flächen mit <code>Strg</code>-Klick wieder abwählen</li>
    </ul>
  </div>

</div>

## Gesucht

### Welche Strahlungsrandbedingung bildet den Kühlkörper richtig ab?

<div class="multiple-choice-question" data-correct="C" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2a" name="u2">
      <label for="u2a">To Ambient</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2b" name="u2">
      <label for="u2b">Surface to Surface mit Enclosure Type Perfect</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2c" name="u2">
      <label for="u2c">Surface to Surface mit Enclosure Type Open</label>
    </div>
  </div>
</div>

### Welche Ambient Temperature gehört zur Strahlung?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2e" name="u2b">
      <label for="u2e">30 °C, die Luft draußen</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2f" name="u2b">
      <label for="u2f">40 °C, die Gehäusewände innen</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2g" name="u2b">
      <label for="u2g">Keine, die Strahlung geht durch das Gehäuse nach draußen</label>
    </div>
  </div>
</div>

### a) Höchste Temperatur, schwarz eloxiert, in °C

<div class="numeric-question" data-answer="101.5" data-tolerance="1" data-points="5" data-attempts="5" data-hints="Strahlung als Surface to Surface mit Open? To Ambient übersieht, dass sich die Rippen gegenseitig sehen, Perfect schickt nichts an die Gehäusewände; Ambient Temperature 40 °C, die Gehäusewände, nicht die Luft draußen?; Wärmestrom (Heat Flow) 40 W nur auf der Fläche unter dem Modul?; Konvektion mit 6 W/(m²·K) und 40 °C auf allen Flächen außer der Rückseite?">
</div>

### b) Höchste Temperatur, blank, in °C

<div class="numeric-question" data-answer="123.02" data-tolerance="1.5" data-points="5" data-attempts="5" data-hints="Nur die Emissivity ändert sich auf 0,05; Strahlung weiter Surface to Surface mit Open, Konvektion bleibt">
</div>

### Welche Ausführung hält die Grenze von 100 °C ein?

<div class="multiple-choice-question" data-correct="D" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2h" name="u2c">
      <label for="u2h">Nur schwarz eloxiert</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2i" name="u2c">
      <label for="u2i">Nur blank</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2j" name="u2c">
      <label for="u2j">Beide</label>
    </div>
    <div class="mc-option" data-value="D">
      <input type="radio" id="u2k" name="u2c">
      <label for="u2k">Keine</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Strahlung: **Surface to Surface mit Open**. Zwischen den Rippen sieht eine Fläche vor allem die Nachbarrippe, To Ambient passt deshalb nicht. Der Kühlkörper umschließt aber keinen Raum: Was keine Fläche des Kühlkörpers trifft, geht an die Gehäusewände. Deshalb Open und nicht Perfect
- Ambient Temperature: **40 °C, die Gehäusewände**. Die Strahlung geht an die Flächen ringsum und nicht durch das Gehäuse nach draußen
- a) schwarz eloxiert: **101,5 °C**, b) blank: **123,0 °C**. Damit hält **keine** Ausführung die 100 °C ein

<figure style="text-align:center;">
  <img src="../../images/p2_kuehlkoerper_vergleich.excalidraw.png" alt="Höchste Temperatur schwarz eloxiert je nach Strahlung: To Ambient 82,5 °C, Surface to Surface mit Open 101,5 °C, Surface to Surface mit Perfect etwa 129 °C; Grenze 100 °C" class="no-lightbox">
</figure>

- Mit To Ambient wären es nur 82,5 °C: Man hätte schwarz eloxiert gewählt, und das Modul wäre zu heiß geworden. Aus den Rinnen zwischen den Rippen kommt nur heraus, was durch ihre offene Oberseite und die offenen Enden passt. Wirksam strahlt etwa nur die Hüllfläche, eine gedachte Haut über den Rippen: rund 0,03 m² statt 0,078 m²
- Mit Perfect wären es etwa 129 °C: Perfect schickt nichts an die Gehäusewände, das wirkt wie ganz ohne Strahlung
- Mit 30 °C draußen statt der Gehäusewände würde der Kühlkörper rund 2 K zu kalt gerechnet: Er sieht nur die Wände, nicht die Luft draußen
- Blankes Aluminium strahlt ohnehin wenig, dort ändert die Wahl der Strahlung kaum etwas (To Ambient 122,1 °C)
- Die Gehäusewände sind in Wirklichkeit etwas kühler als 40 °C, weil sie zwischen der warmen Luft innen und der kühleren Luft draußen liegen. Mit 40 °C liegt die Rechnung auf der sicheren Seite: Zu kühleren Wänden strahlt der Kühlkörper mehr ab
- Unter dem Modul ist es nur rund 5 K wärmer als an den Rippenspitzen: Aluminium verteilt die Wärme gut
- Wärmestrom statt Wärmestromdichte: Bekannt ist die Gesamtleistung von 40 W. Als Wärmestromdichte müsste man erst durch die Fläche teilen: 40 W / 0,0025 m² = 16 000 W/m²

</div>
