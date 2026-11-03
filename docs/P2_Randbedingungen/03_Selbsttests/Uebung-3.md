---
title: "Übung 3: Erdkabel im Windpark"
---

# Übung 3: Erdkabel im Windpark

Die Windräder eines Windparks sind über Erdkabel verbunden. Durch den
Kupfer- oder Aluminiumleiter fließt Strom, und der elektrische Widerstand
erzeugt Wärme. Die Isolierung aus vernetztem Polyethylen (VPE) verträgt
dauerhaft höchstens **90 °C**. Ob das Kabel heiß wird, hängt stark vom Boden ab.

<figure style="text-align:center;">
  <img src="../../images/p2_erdkabel.excalidraw.png" alt="Erdkabel im Boden" class="no-lightbox">
</figure>

## Gegeben

**Material**

- Leiter Aluminium: Wärmeleitfähigkeit $\lambda = 230\ \mathrm{W/(m\,K)}$
- Isolierung VPE: $\lambda = 0{,}3\ \mathrm{W/(m\,K)}$
- Boden a) feucht: $\lambda = 1{,}0\ \mathrm{W/(m\,K)}$, b) trockener Sand: $\lambda = 0{,}4\ \mathrm{W/(m\,K)}$

**Geometrie** (Scheibe, 100 mm dick)

- Erdreich 4 m breit, 3 m tief
- Kabelmitte 1 m unter der Oberfläche, mittig
- Leiter Ø 17,5 mm (Querschnitt 240 mm²), Isolierung außen Ø 40 mm
- drei Körper mit Share Topology: Erdreich, Isolierung, Leiter

**Netz**

- Netzgröße global **100 mm**
- Leiter und Isolierung: eigene Netzgröße **2 mm** (sonst ist das Kabel nur ein Element)

**Randbedingungen**

- Leiter: Wärmeerzeugung durch den Strom $\dot q''' = 148\,100\ \mathrm{W/m^3}$ (bei 550 A)
- Erdoberfläche: Luft $T = 20\ \mathrm{°C}$, Wärmeübergangskoeffizient $\alpha = 10\ \mathrm{W/(m^2\,K)}$
- Unterseite in 3 m Tiefe: feste Temperatur $T = 10\ \mathrm{°C}$
- Seiten, Vorder- und Rückseite: isoliert

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Kabel 1000 mm tief</p>
    <ul>
      <li>Vom Ursprung mit <code>Line</code> eine Hilfslinie <strong>500 mm</strong> nach unten, an ihrem Ende <code>Rectangle</code> mit <strong>Define rectangle from center</strong>: <strong>4000 × 3000</strong> mm</li>
      <li>Die Hilfslinie vor dem Beenden der Skizze löschen, sonst teilt sie die Kreisflächen</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Netz mit zwei Größen</p>
    <ul>
      <li>Leiter und Isolierung feiner vernetzen: oben <code>Body</code> wählen, beide markieren, <code>Rechtsklick Mesh → Insert → Sizing</code>, <strong>Element Size 2 mm</strong> (in Mechanical <strong>0,002</strong> m). Warum das nötig ist, behandelt Praktikum 3</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wärmeerzeugung</p>
    <ul>
      <li>Körper Leiter anklicken, <code>Insert → Internal Heat Generation</code> und den Wert in W/m³ eintragen</li>
    </ul>
  </div>

</div>

## Gesucht

### a) Feuchter Boden: höchste Temperatur im Leiter in °C

<div class="numeric-question" data-answer="57.72" data-tolerance="0.8" data-points="5" data-attempts="5" data-hints="Temperatur im Leiter abgelesen, nicht im Erdreich? Die Isolierung allein macht rund 16 K aus; Wärmeerzeugung 148 100 W/m³ auf dem Körper Leiter, nicht auf einer Fläche?; Share Topology und Netzgröße 2 mm an Leiter und Isolierung?; Unterseite 10 °C, Oberseite Konvektion 10 bei 20 °C?; Boden λ = 1,0?">
</div>

### b) Trockener Sand: höchste Temperatur im Leiter in °C

<div class="numeric-question" data-answer="95.67" data-tolerance="1.2" data-points="5" data-attempts="5" data-hints="Temperatur im Leiter abgelesen, nicht im Erdreich?; Nur das Material des Erdreichs ändert sich: λ = 0,4; Alles andere wie in a)">
</div>

### Hält das Kabel die Grenze von 90 °C ein?

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="u3a" name="u3">
      <label for="u3a">In beiden Böden</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="u3b" name="u3">
      <label for="u3b">Nur im feuchten Boden</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="u3c" name="u3">
      <label for="u3c">Nur im trockenen Sand</label>
    </div>
    <div class="mc-option" data-value="D">
      <input type="radio" id="u3d" name="u3">
      <label for="u3d">In keinem</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Die 148 100 W/m³ im Leiter sind 35,5 W je Meter Kabel
- a) feuchter Boden: Leiter **57,7 °C**, deutlich unter 90 °C
- b) trockener Sand: Leiter **95,7 °C**, über der Grenze. Der Boden leitet die Wärme schlechter ab, das Kabel staut die Wärme
- Deshalb werden Erdkabel in speziellem Sand mit bekannter Wärmeleitfähigkeit verlegt, und die zulässige Stromstärke hängt vom Boden ab
- Die Isolierung allein verursacht rund 16 K: Kunststoff leitet schlecht, aber ohne sie geht es nicht. Im trockenen Sand hat das Erdreich direkt am Kabel rund 80 °C, der Leiter 95,7 °C
- Die feste Temperatur in 3 m Tiefe ist hier berechtigt: Dort ändert sich die Bodentemperatur über das Jahr kaum

</div>
