---
title: d) Pufferspeicher
---

# d) Pufferspeicher: ein Drehkörper als Halbschnitt

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** einen Pufferspeicher rotationssymmetrisch rechnen und seinen Wärmeverlust mit dem Herstellerwert und der Ökodesign-Grenze vergleichen
</div>

Ein Pufferspeicher hält heißes Wasser für die Heizung vor. Über die Dämmung
verliert er laufend Wärme an den Raum. Der Speicher ist ein Zylinder: Alles,
was ihn ausmacht, liegt im **Halbschnitt** von der Achse bis zum Rand (siehe
[Abstraktionen](../../01_Grundlagen/Abstraktionen.md#rotationssymmetrie)).

<figure style="text-align:center;">
  <img src="../../../images/p3_pufferspeicher.excalidraw.png" alt="Halbschnitt eines Pufferspeichers rechts der Drehachse: Wasser 65 °C, Dämmung an Deckel, Mantel und Boden, außen Raumluft" class="no-lightbox">
</figure>

## Gegeben

Vorbild ist ein Pufferspeicher mit 800 l aus dem Katalog eines Herstellers
(Wolf BSH-800):

- **Wasser:** 800 l, im Modell ein Zylinder mit ebenen Böden, Radius 395 mm, Höhe 1632 mm
- **Dämmung:** Polyestervlies, $\lambda = 0{,}038\ \mathrm{W/(m\,K)}$, am Mantel 120 mm, am Deckel 100 mm, am Boden 100 mm
- **Innen:** Temperatur 65 °C an der Behälterwand (wie bei der Prüfung des Herstellers)
- **Außen:** Raumluft 20 °C, Konvektion und Strahlung zusammen mit $\alpha = 8\ \mathrm{W/(m^2\,K)}$
- **Achse:** keine Randbedingung

!!! warning "Annahmen im Modell"
    - **Stahlwand weggelassen:** Sie leitet gut und ist dünn, wie das Stahlrohr in a)
    - **Ebene Böden:** Der echte Speicher hat gewölbte Böden. Das Modell hat dasselbe Volumen
    - **Ohne Anschlüsse und Füße:** Die sitzen an einzelnen Stellen des Umfangs und lassen sich rotationssymmetrisch nicht abbilden
    - **Dämmung am Boden 100 mm:** Der Hersteller nennt keine Dicke, angenommen

## Modell

<!-- Klickanleitung nach dem Klicktest einfügen: <tutorial slug="p3-pufferspeicher"></tutorial> -->

??? tip "Kurzanleitung: Material und Geometrie"
    1. Neue Analyse **d) Pufferspeicher** (`Doppelklick Steady-State Thermal`), in **Engineering Data** das Material **Vlies** mit **0,038** W m⁻¹ C⁻¹ anlegen
    2. `Rechtsklick Geometry → Properties`, **Analysis Type** `2D`
    3. In SpaceClaim zwei Rechtecke in der x-y-Ebene, beide mit der linken Kante auf der **y-Achse**: außen von (0, −100) bis (515, 1732) mm, innen von (0, 0) bis (395, 1632) mm
    4. Skizze beenden (`Pull`, Taste `P`), die innere Fläche (Wasser) anklicken und mit `Entf` löschen. Die äußere Fläche umbenennen in **Daemmung**

!!! danger "Die Drehachse ist immer die y-Achse"
    ANSYS dreht den Halbschnitt um die y-Achse. Der Querschnitt muss deshalb
    rechts von ihr liegen (x ≥ 0), x ist der Radius.

??? tip "Kurzanleitung: Mechanical"
    1. `Strukturbaum Geometry` anklicken, im `Detailfenster` bei **2D Behavior** `Axisymmetric` wählen. Eine Dicke gibt es dann nicht
    2. Fläche **Daemmung** mit **Vlies**, Netzgröße global **0,01** m (10 mm)
    3. Zwei Named Selections über das Worksheet, Entity Type `Edge`, je drei Zeilen:
        - **Wasser:** Location X 0,395 m (395 mm), Location Y 0 m, Location Y 1,632 m (1632 mm)
        - **Raumluft:** Location X 0,515 m (515 mm), Location Y −0,1 m (−100 mm), Location Y 1,732 m (1732 mm)
    4. `Insert → Temperature` auf **Wasser**, **65** °C; `Insert → Convection` auf **Raumluft**, **Film Coefficient** **8** W/(m²·°C), **Ambient Temperature** **20** °C
    5. Lösen, die Temperatur **Wasser** auf **Solution** ziehen: Die Reaktion ist der Wärmeverlust des **ganzen** Speichers (360°)

<!-- Wert aus tools/sollwerte/p3_pufferspeicher.py, im Klicktest durch den ANSYS-Wert ersetzen -->
!!! check "Checkpoint: Dieser Wert sollte herauskommen"
    | Größe | Wert |
    |---|---|
    | Reaktion Wasser (Wärmeverlust) | rund +85 W |

## Vergleich mit Hersteller und Ökodesign-Grenze

Der Hersteller gibt den **Bereitschaftswärmeaufwand** an: 2,32 kWh in 24 h,
also 97 W. Für Speicher bis 2000 l schreibt die Ökodesign-Verordnung der EU
(814/2013) eine Grenze vor:

$$
S < 16{,}66 + 8{,}33 \cdot V^{0{,}4} = 16{,}66 + 8{,}33 \cdot 800^{0{,}4} = 137\ \mathrm{W}
$$

- $S$: Warmhalteverlust des Speichers in W (gemessen bei 65 °C Wasser und 20 °C Raum)
- $V$: Speichervolumen in l

Im Vergleich:

- **Modell gegen Hersteller:** Das Modell liegt rund 12 % unter dem
  Herstellerwert. Die Anschlüsse und Füße fehlen im Modell, über sie geht
  zusätzlich Wärme verloren.
- **Gegen die Grenze:** Der Speicher liegt weit darunter.

### Darf der Speicher mit 60 mm Dämmung verkauft werden?

Die Dämmung kostet Geld und Platz. Rechnen Sie den Speicher mit **60 mm
Dämmung überall** (Mantel, Deckel und Boden): Außenrechteck dann von
(0, −60) bis (455, 1692) mm.

<div class="multiple-choice-question" data-correct="B" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="p3psa" name="p3ps">
      <label for="p3psa">Ja, der Wärmeverlust bleibt unter 137 W</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="p3psb" name="p3ps">
      <label for="p3psb">Nein, der Wärmeverlust liegt über 137 W</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Mit 60 mm Dämmung verliert der Speicher rund **146 W**, mehr als die erlaubten 137 W: Er dürfte so nicht verkauft werden
- Die Grenze erreicht der Speicher bei rund 65 mm Dämmung überall. Der Hersteller nutzt 120 mm am Mantel und liegt damit weit darunter

</div>
