---
title: "Übung 2: Kühlkörper eines Wechselrichters"
---

# Übung 2: Kühlkörper eines Wechselrichters

Der Wechselrichter einer Photovoltaikanlage wandelt Gleichstrom in Wechselstrom.
Seine Leistungshalbleiter sitzen in einem Modul, das laut Datenblatt **40 W**
Verlustleistung abgibt. Ein Aluminium-Kühlkörper führt die Wärme an die Luft im
Gehäuse ab. Gerechnet wird ein heißer Sommertag: Die Luft im Gehäuse hat dann
40 °C, die Gehäusewände ebenso. Unter dem Modul darf der Kühlkörper höchstens
**100 °C** warm werden. Reicht dafür blankes Aluminium, oder muss er schwarz
eloxiert sein?

<figure style="text-align:center;">
  <img src="../../images/p2_kuehlkoerper.excalidraw.png" alt="Kühlkörper mit Rippen" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Aluminium: Wärmeleitfähigkeit $\lambda = 200\ \mathrm{W/(m\,K)}$

**Geometrie**

- Grundplatte 100 mm × 100 mm, 8 mm dick
- 8 Rippen, je 2 mm dick, 40 mm hoch, 100 mm lang; die äußeren Rippen schließen bündig mit der Platte ab, Abstand von Rippe zu Rippe 14 mm (Mitte zu Mitte)
- Modul 50 mm × 50 mm mittig auf der Rückseite

**Netz**

- Netzgröße global **2,5 mm**

**Randbedingungen**

- Fläche unter dem Modul: Wärmestrom $\dot Q = 40\ \mathrm{W}$
- alle Flächen außer der Rückseite, auch die Stirnflächen vorn und hinten (im Bild cyan):
    - Konvektion: Luft im Gehäuse $T = 40\ \mathrm{°C}$, Wärmeübergangskoeffizient $\alpha = 6\ \mathrm{W/(m^2\,K)}$
    - Strahlung zu den Gehäusewänden mit $T = 40\ \mathrm{°C}$ (in ANSYS die `Ambient Temperature`)
- Emissionsgrad: a) schwarz eloxiert $\varepsilon = 0{,}85$, b) blank $\varepsilon = 0{,}05$
- Rückseite neben dem Modul: liegt am Gehäuse, isoliert

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <ul>
      <li>Querschnitt skizzieren: Rechteck <strong>100 × 8</strong> mm ab dem Ursprung</li>
      <li>Darauf am linken Rand ein Rechteck <strong>2 × 40</strong> mm (erste Rippe)</li>
      <li>Alles <strong>100 mm</strong> ziehen</li>
      <li>Die Rippe mit <code>Move</code> und der Option <strong>Create Patterns</strong> in 14 mm Abstand auf insgesamt 8 Rippen vervielfachen, sodass ein einziger Körper entsteht</li>
      <li>Alternativ alle 8 Rippen gleich in der Skizze zeichnen (Rechtecke 2 × 40 mm bei x = 0, 14, 28 … 98 mm) und zusammen mit der Platte ziehen</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Fläche für das Modul</p>
    <ul>
      <li>Auf der Rückseite skizzieren: <code>Rectangle</code> mit <strong>Define rectangle from center</strong> im Mittelpunkt der Fläche, <strong>50 × 50</strong> mm</li>
      <li>Skizze beenden: Die Rückseite ist jetzt in zwei Flächen geteilt</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wärmestrom und viele Flächen auf einmal</p>
    <ul>
      <li>Fläche unter dem Modul: <code>Heat Flow</code> 40 W</li>
      <li>Für Luft und Strahlung: oben <code>Face</code> wählen und mit <code>Strg + A</code> alle Flächen auswählen</li>
      <li>Mit <code>Strg</code>-Klick die beiden Flächen der Rückseite wieder abwählen</li>
      <li>Darauf <code>Convection</code> und <code>Radiation</code> (To Ambient)</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswerten</p>
    <ul>
      <li><code>Temperature</code> im ganzen Modell einfügen und das Maximum ablesen</li>
      <li>Für b) nur die <strong>Emissivity</strong> der Strahlung auf 0,05 ändern und neu lösen</li>
    </ul>
  </div>

</div>

## Gesucht

### a) Höchste Temperatur, schwarz eloxiert, in °C

<div class="numeric-question" data-answer="82.53" data-tolerance="1" data-points="5" data-attempts="5" data-hints="Wärmestrom (Heat Flow) 40 W nur auf der Fläche unter dem Modul?; Konvektion 6 bei 40 °C und Strahlung 0,85 bei 40 °C auf allen Flächen außer der Rückseite?">
</div>

### b) Höchste Temperatur, blank, in °C

<div class="numeric-question" data-answer="122.08" data-tolerance="1.5" data-points="5" data-attempts="5" data-hints="Nur die Emissivity ändert sich auf 0,05; Die Konvektion bleibt">
</div>

### Welche Ausführung hält nach Ihrer Rechnung die Grenze von 100 °C ein?

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2a" name="u2">
      <label for="u2a">Nur schwarz eloxiert</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2b" name="u2">
      <label for="u2b">Nur blank</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2c" name="u2">
      <label for="u2c">Beide</label>
    </div>
    <div class="mc-option" data-value="D">
      <input type="radio" id="u2d" name="u2">
      <label for="u2d">Keine</label>
    </div>
  </div>
</div>

### Wird der echte Kühlkörper wärmer oder kälter als berechnet?

Mit `To Ambient` rechnet ANSYS so, als käme die ganze Strahlung jeder Fläche an
den Gehäusewänden an. Zwischen den Rippen sieht eine Fläche aber vor allem die
Nachbarrippe.

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2e" name="u2b">
      <label for="u2e">Wärmer: Ein großer Teil der Strahlung einer Rippe trifft die Nachbarrippe statt die Gehäusewände und bleibt im Kühlkörper</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2f" name="u2b">
      <label for="u2f">Kälter: Die Nachbarrippen nehmen zusätzlich Wärme auf</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2g" name="u2b">
      <label for="u2g">Genauso warm: Jede Fläche strahlt nach ihrer eigenen Temperatur ab, egal was sie sieht</label>
    </div>
  </div>
</div>

!!! tip "Zusatz für Schnelle: Surface to Surface"
    - In a) und b) die Strahlung durch `Surface To Surface` ersetzen: `Enclosure Type` **Open** und `Ambient Temperature` 40 °C
    - Dann rechnet ANSYS aus, welchen Teil der Strahlung die Nachbarrippen auffangen
    - Wie stark ändert sich die höchste Temperatur? Hält die schwarze Ausführung die 100 °C dann noch ein?

<div class="solution-images" markdown="1">

### Lösung

- a) schwarz eloxiert: **82,5 °C**, Grenze nach dieser Rechnung eingehalten. Von den 40 W gehen 18,3 W über Konvektion und 21,7 W über Strahlung
- b) blank: **122,1 °C**, zu heiß. Ohne Strahlung muss die Konvektion fast alles allein schaffen (36,9 W)
- Unter dem Modul ist es nur rund 5 K wärmer als an den Rippenspitzen: Aluminium verteilt die Wärme gut
- Wärmestrom statt Wärmestromdichte: Bekannt ist die Gesamtleistung von 40 W. Als Wärmestromdichte müsste man erst durch die Fläche teilen: 40 W / 0,0025 m² = 16 000 W/m²
- Der echte Kühlkörper wird wärmer als berechnet: Zwischen den Rippen strahlen gleich warme Flächen gegeneinander, dabei wird kaum Wärme abgegeben. Aus den Rinnen zwischen den Rippen kommt nur heraus, was durch ihre offene Oberseite und die offenen Enden passt. Wirksam strahlt etwa nur die Hüllfläche, eine gedachte Haut über den Rippen: rund 0,03 m² statt 0,078 m²
- Mit `Surface to Surface` (Zusatz): schwarz eloxiert **101,5 °C** statt 82,5 °C, blank **123,0 °C** statt 122,1 °C. Damit hält auch die schwarze Ausführung die 100 °C knapp nicht ein: Mit `To Ambient` allein hätte man falsch entschieden
- Blankes Aluminium strahlt ohnehin wenig, deshalb ändert sich dort kaum etwas

</div>
