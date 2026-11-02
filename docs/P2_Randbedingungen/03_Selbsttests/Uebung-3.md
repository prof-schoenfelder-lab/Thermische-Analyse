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

- Leiter Aluminium: Wärmeleitfähigkeit $\lambda = 230\ \mathrm{W/(m\,K)}$, spezifischer Widerstand $\rho = 0{,}0282\ \Omega\,\mathrm{mm^2/m}$
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

- Leiter: Strom $I = 550\ \mathrm{A}$, als Wärmeerzeugung
- Erdoberfläche: Luft $T = 20\ \mathrm{°C}$, Wärmeübergangskoeffizient $\alpha = 10\ \mathrm{W/(m^2\,K)}$
- Unterseite in 3 m Tiefe: feste Temperatur $T = 10\ \mathrm{°C}$
- Seiten, Vorder- und Rückseite: isoliert

## Hinweise

<div class="steps" markdown="1" data-anleitung="nein">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <ul>
      <li>Kabel in den Ursprung: zwei Kreise Ø <strong>40</strong> und <strong>17,5</strong> mm</li>
      <li>Mit <code>Line</code> vom Ursprung <strong>500 mm</strong> nach unten</li>
      <li>Am Endpunkt <code>Rectangle</code> mit <strong>Define rectangle from center</strong>: <strong>4000 × 3000</strong> mm. Dann liegt das Kabel 1000 mm unter der Oberkante</li>
      <li>Die Hilfslinie vor dem Beenden der Skizze löschen, sonst teilt sie die Kreisflächen</li>
      <li>Zuerst das Erdreich <strong>100 mm</strong> ziehen</li>
      <li>Dann Isolierung und Leiter je mit <strong>No merge</strong> ziehen</li>
      <li>Share Topology: <strong>Share</strong></li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Netz mit zwei Größen</p>
    <ul>
      <li>Global <strong>100 mm</strong> (in Mechanical <strong>0,1</strong> m eintragen)</li>
      <li>Oben <code>Body</code> wählen und Leiter und Isolierung markieren</li>
      <li><code>Rechtsklick Mesh → Insert → Sizing</code></li>
      <li><strong>Element Size 2 mm</strong> (in Mechanical <strong>0,002</strong> m eintragen)</li>
      <li>Warum das nötig ist, behandelt Praktikum 3</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Wärmeerzeugung</p>
    <ul>
      <li>Die Stromwärme je Volumen ist \(\dot q''' = I^2 \rho / A^2\) mit dem Strom \(I\) in A, dem spezifischen Widerstand \(\rho\) in Ω·m und dem Leiterquerschnitt \(A\) in m²</li>
      <li>Körper Leiter anklicken</li>
      <li><code>Insert → Internal Heat Generation</code> und den Wert in W/m³ eintragen</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Temperatur und Konvektion</p>
    <ul>
      <li>Unterseite: <code>Temperature</code> 10 °C</li>
      <li>Oberseite: <code>Convection</code> mit 10 W/m²·°C und 20 °C</li>
      <li>Alle übrigen Flächen bleiben frei</li>
      <li>Auswerten: <code>Temperature</code> auf den Körper Leiter setzen und das Maximum ablesen</li>
      <li>Für b) im Strukturbaum dem Erdreich das Material trockener Sand zuweisen und neu lösen</li>
    </ul>
  </div>

</div>

## Gesucht

### Wärmeerzeugung im Leiter in W/m³

<div class="numeric-question" data-answer="148099" data-tolerance="1500" data-points="5" data-attempts="5" data-hints="ρ = 0,0282 Ω·mm²/m = 2,82·10⁻⁸ Ω·m; A = 240 mm² = 2,4·10⁻⁴ m²; Formel I²·ρ/A²">
</div>

### a) Höchste Leitertemperatur im feuchten Boden in °C

<div class="numeric-question" data-answer="57.72" data-tolerance="0.8" data-points="5" data-attempts="5" data-hints="Wärmeerzeugung auf dem Körper Leiter (nicht auf einer Fläche)?; Netzgröße 2 mm an Leiter und Isolierung?; Unterseite 10 °C?; Oberseite Konvektion 10 bei 20 °C?; Boden λ = 1,0?">
</div>

### b) Höchste Leitertemperatur im trockenen Sand in °C

<div class="numeric-question" data-answer="95.67" data-tolerance="1.2" data-points="5" data-attempts="5" data-hints="Nur das Material des Erdreichs ändert sich: λ = 0,4; Alles andere wie in a)">
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

- Wärmeerzeugung $\dot q''' = 550^2 \cdot 2{,}82\cdot10^{-8} / (2{,}4\cdot10^{-4})^2 \approx 148\,100\ \mathrm{W/m^3}$, das sind 35,5 W je Meter Kabel
- a) feuchter Boden: Leiter **57,7 °C**, deutlich unter 90 °C
- b) trockener Sand: Leiter **95,7 °C**, über der Grenze. Der Boden leitet die Wärme schlechter ab, das Kabel staut die Wärme
- Deshalb werden Erdkabel in speziellem Sand mit bekannter Wärmeleitfähigkeit verlegt, und die zulässige Stromstärke hängt vom Boden ab
- Die Isolierung allein verursacht rund 16 K: Kunststoff leitet schlecht, aber ohne sie geht es nicht
- Die feste Temperatur in 3 m Tiefe ist hier berechtigt: Dort ändert sich die Bodentemperatur über das Jahr kaum

</div>
