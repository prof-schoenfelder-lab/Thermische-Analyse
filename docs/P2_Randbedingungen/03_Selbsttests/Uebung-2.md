---
title: "Übung 2: Kühlkörper eines Wechselrichters"
---

# Übung 2: Kühlkörper eines Wechselrichters

Der Wechselrichter einer Photovoltaikanlage wandelt Gleichstrom in Wechselstrom.
Seine Leistungshalbleiter sitzen in einem Modul, das laut Datenblatt **40 W**
Verlustleistung abgibt. Ein Aluminium-Kühlkörper führt die Wärme an die Luft im
Gehäuse ab. Unter dem Modul darf der Kühlkörper höchstens **100 °C** warm
werden. Reicht dafür blankes Aluminium, oder muss er schwarz eloxiert sein?

<figure style="text-align:center;">
  <img src="../../images/p2_kuehlkoerper.excalidraw.png" alt="Kühlkörper mit Rippen" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Aluminium: $\lambda = 200\ \mathrm{W/(m\,K)}$

**Geometrie**

- Grundplatte 100 mm × 100 mm, 8 mm dick
- 8 Rippen, je 2 mm dick, 40 mm hoch, 100 mm lang; die äußeren Rippen schließen bündig mit der Platte ab, Abstand von Rippe zu Rippe 14 mm (Mitte zu Mitte)
- Modul 50 mm × 50 mm mittig auf der Rückseite

**Netz**

- Netzgröße global **2,5 mm**

**Randbedingungen**

- Fläche unter dem Modul: Wärmestrom $\dot Q = 40\ \mathrm{W}$
- alle Flächen außer der Rückseite: Luft $T = 40\ \mathrm{°C}$, $\alpha = 6\ \mathrm{W/(m^2\,K)}$, und Strahlung zur Umgebung (40 °C)
- a) schwarz eloxiert $\varepsilon = 0{,}85$, b) blank $\varepsilon = 0{,}05$
- Rückseite neben dem Modul: liegt am Gehäuse, isoliert

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <p>Querschnitt skizzieren: Rechteck <strong>100 × 8</strong> mm ab dem Ursprung, darauf am linken Rand ein Rechteck <strong>2 × 40</strong> mm (erste Rippe). Alles <strong>100 mm</strong> ziehen. Die Rippe mit <code>Move</code> und der Option <strong>Create Patterns</strong> in 14 mm Abstand auf insgesamt 8 Rippen vervielfachen, sodass ein einziger Körper entsteht. Alternativ alle 8 Rippen gleich in der Skizze zeichnen (Rechtecke 2 × 40 mm bei x = 0, 14, 28 … 98 mm) und zusammen mit der Platte ziehen</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Fläche für das Modul</p>
    <p>Auf der Rückseite skizzieren: <code>Rectangle</code> mit <strong>Define rectangle from center</strong> im Mittelpunkt der Fläche, <strong>50 × 50</strong> mm. Skizze beenden: Die Rückseite ist jetzt in zwei Flächen geteilt</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wärmestrom und viele Flächen auf einmal</p>
    <p>Fläche unter dem Modul: <code>Heat Flow</code> 40 W. Für Luft und Strahlung: oben <code>Face</code>, mit <code>Strg + A</code> alle Flächen auswählen und mit <code>Strg</code>-Klick die beiden Flächen der Rückseite wieder abwählen. Darauf <code>Convection</code> und <code>Radiation</code> (To Ambient)</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswerten</p>
    <p><code>Temperature</code> im ganzen Modell, Maximum ablesen. Für b) nur die <strong>Emissivity</strong> der Strahlung auf 0,05 ändern und neu lösen</p>
  </div>

</div>

## Gesucht

### a) Höchste Temperatur, schwarz eloxiert, in °C

<div class="numeric-question" data-answer="82.53" data-tolerance="1" data-points="5" data-attempts="5" data-hints="Heat Flow 40 W nur auf der Fläche unter dem Modul? Konvektion 6 bei 40 °C und Strahlung 0,85 bei 40 °C auf allen Flächen außer der Rückseite?">
</div>

### b) Höchste Temperatur, blank, in °C

<div class="numeric-question" data-answer="122.08" data-tolerance="1.5" data-points="5" data-attempts="5" data-hints="Nur die Emissivity ändert sich auf 0,05. Die Konvektion bleibt.">
</div>

### Welche Ausführung hält die Grenze von 100 °C ein?

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

### Ist das Ergebnis mit Strahlung To Ambient auf allen Rippenflächen eher zu günstig oder zu ungünstig?

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u2e" name="u2b">
      <label for="u2e">Zu günstig: Die Rippen sehen sich gegenseitig, ein großer Teil ihrer Strahlung landet auf der Nachbarrippe statt in der Umgebung</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u2f" name="u2b">
      <label for="u2f">Zu ungünstig: Die Rippen strahlen sich gegenseitig zusätzlich Wärme ab</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u2g" name="u2b">
      <label for="u2g">Passt genau, Strahlung hängt nur von der eigenen Temperatur ab</label>
    </div>
  </div>
</div>

!!! tip "Zusatz für Schnelle: Surface to Surface"
    Ersetzen Sie in Fall a) die Strahlung durch `Surface To Surface` mit
    `Enclosure Type` **Open** und `Ambient Temperature` 40 °C. Dann rechnet
    ANSYS aus, welchen Teil der Strahlung die Nachbarrippen auffangen. Wie stark
    ändert sich die höchste Temperatur?

<div class="solution-images" markdown="1">

### Lösung

- a) schwarz eloxiert: **82,5 °C**, Grenze eingehalten. Von den 40 W gehen 18,3 W über Konvektion und 21,7 W über Strahlung
- b) blank: **122,1 °C**, zu heiß. Ohne Strahlung muss die Konvektion fast alles allein schaffen (36,9 W)
- Unter dem Modul ist es nur rund 5 K wärmer als an den Rippenspitzen: Aluminium verteilt die Wärme gut
- Wärmestrom statt Wärmestromdichte: Bekannt ist die Gesamtleistung von 40 W. Als Wärmestromdichte müsste man erst durch die Fläche teilen: 40 W / 0,0025 m² = 16 000 W/m²
- To Ambient auf allen Flächen ist zu günstig: Zwischen den Rippen strahlen gleich warme Flächen gegeneinander, dabei wird kaum Wärme abgegeben. Mit Surface to Surface wird das Ergebnis ungünstiger, und der Vorteil des Eloxierens kleiner

</div>
