---
title: Konvektion
---

# Konvektion

Konvektion ist der Wärmeübergang zwischen einer Oberfläche und einem
strömenden Fluid, also Luft oder Wasser. In ANSYS ist das die Randbedingung
`Convection`. Sie braucht zwei Zahlen: die Temperatur des Fluids und den
**Wärmeübergangskoeffizienten α**. Die Temperatur ist meist bekannt, α nicht.
Diese Seite erklärt, woher α kommt, und dient als Nachschlagewerk, um α
abzuschätzen. Jede Zahl hat eine Quelle (unten auf der Seite).

## Newtonsches Abkühlungsgesetz

$$
\dot q = \alpha \, (T_O - T_F)
$$

mit

- $\dot q$: Wärmestromdichte von der Oberfläche ins Fluid in W/m²
- $\alpha$: Wärmeübergangskoeffizient in W/(m²·K)
- $T_O$: Temperatur der Oberfläche
- $T_F$: Temperatur des Fluids weit weg von der Oberfläche

Die Formel sieht einfach aus, weil die ganze Physik in α steckt.

## Woher α kommt: die Grenzschicht

<div class="grenzschicht"></div>

- Direkt an der Oberfläche haftet das Fluid, seine Geschwindigkeit ist dort null. Durch diese Schicht kommt die Wärme nur durch Leitung
- Die Temperatur ändert sich nur in einer dünnen Schicht nahe der Oberfläche, der **Grenzschicht**. Sie ist oft nur wenige Millimeter dick
- Grob gilt $\alpha \approx \lambda_F / \delta$ mit der Wärmeleitfähigkeit $\lambda_F$ des Fluids in W/(m·K) und der Dicke $\delta$ der Grenzschicht in m
- Schnellere Strömung macht die Grenzschicht dünner, α wird größer
- Wasser leitet Wärme rund 25-mal besser als Luft (0,6 gegen 0,025 W/(m·K)). Bei ähnlicher Strömung ist α für Wasser deshalb viel größer
- α ist **keine Stoffeigenschaft**: Es hängt vom Fluid, von der Geschwindigkeit, von Form und Lage der Oberfläche und bei freier Konvektion auch vom Temperaturunterschied ab

## Freie und erzwungene Konvektion

- **Erzwungen:** Eine Pumpe, ein Lüfter oder der Wind bewegt das Fluid. α hängt vor allem von der Geschwindigkeit ab
- **Frei:** Das Fluid an einer warmen Oberfläche wird leichter und steigt auf, an einer kalten sinkt es ab. Die Strömung entsteht erst durch den Temperaturunterschied. Deshalb wächst α mit dem Temperaturunterschied, in ruhender Luft bei kleinen Bauteilen etwa mit $\Delta T^{1/4}$
- Ist der Temperaturunterschied zu klein, um das Fluid in Bewegung zu bringen, bleibt nur Wärmeleitung im Fluid, zum Beispiel in schmalen Luftspalten

## Typische Werte

<figure style="text-align:center;">
  <img src="../../images/p2_alpha_bereiche.excalidraw.png" alt="Typische Bereiche des Wärmeübergangskoeffizienten auf logarithmischer Achse: freie Konvektion Gase 2 bis 25, erzwungene Konvektion Gase 25 bis 250, freie Konvektion Flüssigkeiten 10 bis 1000, erzwungene Konvektion Flüssigkeiten 50 bis 20 000, Sieden und Kondensieren 2500 bis 100 000 W/(m²·K)" class="no-lightbox">
  <figcaption>Typische Bereiche nach Çengel 2002, Tab. 1-5</figcaption>
</figure>

| Art der Konvektion | α in W/(m²·K) |
|---|---|
| freie Konvektion, Gase | 2 bis 25 |
| erzwungene Konvektion, Gase | 25 bis 250 |
| freie Konvektion, Flüssigkeiten | 10 bis 1000 |
| erzwungene Konvektion, Flüssigkeiten | 50 bis 20 000 |
| Sieden und Kondensieren | 2500 bis 100 000 |

Die Werte in diesem Kurs ordnen sich so ein:

- Ruhende Luft an Rohren und Bauteilen, freie Konvektion: Heizungsrohr 7, Kühlkörper 6 W/(m²·K)
- Luft außen mit leichtem Wind: Vakuumröhre und Erdoberfläche 10 W/(m²·K)
- Wasser im Rohr, erzwungen: Heizungsrohr und Vakuumröhre 1000 W/(m²·K)

## Normwerte der Bauphysik enthalten Strahlung

In der Bauphysik rechnet man mit festen Wärmeübergangswiderständen nach
DIN EN ISO 6946. Sie enthalten **Konvektion und Strahlung zusammen**:

| Stelle | Wärmeübergangswiderstand | entspricht α (Konvektion und Strahlung) |
|---|---|---|
| innen, Wärmestrom waagerecht (Wand) | $R_{si} = 0{,}13\ \mathrm{m^2\,K/W}$ | 7,7 W/(m²·K) |
| innen, Wärmestrom nach oben (Decke) | $R_{si} = 0{,}10\ \mathrm{m^2\,K/W}$ | 10 W/(m²·K) |
| innen, Wärmestrom nach unten (Fußboden) | $R_{si} = 0{,}17\ \mathrm{m^2\,K/W}$ | 5,9 W/(m²·K) |
| außen | $R_{se} = 0{,}04\ \mathrm{m^2\,K/W}$ | 25 W/(m²·K) |

- $R_{si}$, $R_{se}$: Wärmeübergangswiderstand innen und außen, der Kehrwert des Wärmeübergangskoeffizienten
- Innen an einer Wand stecken in den 7,7 W/(m²·K) nur etwa 2,5 W/(m²·K) Konvektion. Die übrigen gut 5 W/(m²·K) sind Strahlung zu den anderen Wänden (bei ε = 0,9 und 20 °C)
- Außen setzt die Norm für die Konvektion $\alpha_K = 4 + 4\,v$ an, mit dem konvektiven Anteil $\alpha_K$ in W/(m²·K) und der Windgeschwindigkeit $v$ in m/s. Die 25 W/(m²·K) gelten für 4 m/s Wind plus Strahlung

!!! warning "Strahlung nicht doppelt zählen"
    - P1 rechnet mit diesen Normwerten als Konvektion, die Strahlung steckt darin
    - Wer die Strahlung wie in P2 als eigene Randbedingung setzt, nimmt für die Konvektion nur den konvektiven Anteil, innen an einer Wand etwa 2,5 statt 7,7 W/(m²·K)
    - Sonst zählt die Strahlung doppelt

## Überschlägig rechnen

### Schnellformeln für ruhende Luft

Für freie Konvektion in Luft bei Normaldruck gibt Çengel einfache Formeln
(Tab. 15-1). Sie gelten für **laminare** Strömung:

| Form | α in W/(m²·K) | Länge |
|---|---|---|
| senkrechte Wand oder senkrechter Zylinder | $1{,}42\,(\Delta T / L)^{0{,}25}$ | Höhe $L$ |
| waagerechter Zylinder (Rohr) | $1{,}32\,(\Delta T / D)^{0{,}25}$ | Durchmesser $D$ |
| waagerechte Platte, warme Seite oben | $1{,}32\,(\Delta T / L)^{0{,}25}$ | $L = 4A/p$ |
| waagerechte Platte, warme Seite unten | $0{,}59\,(\Delta T / L)^{0{,}25}$ | $L = 4A/p$ |
| Kugel | $1{,}92\,(\Delta T / D)^{0{,}25}$ | Durchmesser $D$ |

- $\Delta T$: Temperaturunterschied zwischen Oberfläche und Luft in K
- $L$, $D$: Länge bzw. Durchmesser in m
- $A$, $p$: Fläche in m² und Umfang in m der Platte
- Laminar heißt: Rayleigh-Zahl unter $10^9$ (unten). Rohre und kleine Bauteile liegen fast immer darin, eine raumhohe Wand meist nicht

!!! example "Beispiel: Heizungsrohr aus Übung 1"
    - Rohr außen Ø 26,9 mm, Oberfläche etwa 59 °C, Kellerluft 15 °C, also $\Delta T \approx 44\ \mathrm{K}$
    - Schnellformel: $\alpha \approx 1{,}32 \cdot (44 / 0{,}0269)^{0{,}25} \approx 8{,}4\ \mathrm{W/(m^2\,K)}$
    - Genauer mit der Formel für das waagerechte Rohr (unten): $\alpha \approx 7{,}0\ \mathrm{W/(m^2\,K)}$, genau der Wert der Übung
    - Die Schnellformel liegt hier 20 % daneben. Für einen ersten Überschlag reicht das

### Genauer: mit Kennzahlen

Die Formeln der Lehrbücher sind in dimensionslosen Kennzahlen geschrieben.
Damit gelten sie für jedes Fluid und jede Größe:

- **Nusselt-Zahl** $Nu = \alpha \, L / \lambda_F$: Sie sagt, wie viel besser die Konvektion Wärme überträgt als reine Leitung durch eine ruhende Fluidschicht der Dicke $L$. Aus ihr folgt $\alpha = Nu \cdot \lambda_F / L$
- **Reynolds-Zahl** $Re = v\,L / \nu$ für erzwungene Konvektion: klein heißt laminar, groß heißt turbulent
- **Rayleigh-Zahl** $Ra = g\,\beta\,\Delta T\,L^3 / \nu^2 \cdot Pr$ für freie Konvektion: Sie sagt, wie stark der Auftrieb treibt
- **Prandtl-Zahl** $Pr$: ein Stoffwert, Luft etwa 0,7, Wasser 2 bis 7

mit

- $L$: charakteristische Länge in m, je nach Form (in den Tabellen angegeben)
- $\lambda_F$: Wärmeleitfähigkeit des Fluids in W/(m·K)
- $v$: Strömungsgeschwindigkeit in m/s
- $\nu$: kinematische Viskosität des Fluids in m²/s
- $g = 9{,}81\ \mathrm{m/s^2}$: Erdbeschleunigung
- $\beta$: Wärmeausdehnungskoeffizient in 1/K, für Gase $\beta = 1/T_f$ mit $T_f$ in Kelvin
- $\Delta T$: Temperaturunterschied zwischen Oberfläche und Fluid in K

Die Stoffwerte nimmt man bei der **Filmtemperatur** $T_f = (T_O + T_F)/2$,
bei der Strömung im Rohr bei der mittleren Temperatur des Fluids.

**Freie Konvektion** (Çengel Tab. 9-1)

- Senkrechte Wand, $L$ = Höhe, für alle $Ra$ (Gl. 9-21):

    $$
    Nu = \left[0{,}825 + \frac{0{,}387\,Ra^{1/6}}{\left[1 + (0{,}492/Pr)^{9/16}\right]^{8/27}}\right]^2
    $$

- Waagerechtes Rohr, $L = D$, für $Ra \le 10^{12}$ (Gl. 9-25):

    $$
    Nu = \left[0{,}6 + \frac{0{,}387\,Ra^{1/6}}{\left[1 + (0{,}559/Pr)^{9/16}\right]^{8/27}}\right]^2
    $$

- Waagerechte Platte, $L = A/p$ (hier ohne Faktor 4):
    - warme Seite oben oder kalte Seite unten: $Nu = 0{,}54\,Ra^{1/4}$ für $Ra = 10^4$ bis $10^7$, $Nu = 0{,}15\,Ra^{1/3}$ für $Ra = 10^7$ bis $10^{11}$ (Gl. 9-22, 9-23)
    - warme Seite unten oder kalte Seite oben: $Nu = 0{,}27\,Ra^{1/4}$ für $Ra = 10^5$ bis $10^{11}$ (Gl. 9-24)

**Erzwungene Konvektion außen**

- Platte, längs angeströmt, $L$ = Länge in Strömungsrichtung, $0{,}6 \le Pr \le 60$ (Gl. 7-21, 7-22, 7-24):
    - laminar, $Re < 5 \cdot 10^5$: $Nu = 0{,}664\,Re^{0{,}5}\,Pr^{1/3}$
    - turbulent ab der Vorderkante, $5 \cdot 10^5 \le Re \le 10^7$: $Nu = 0{,}037\,Re^{0{,}8}\,Pr^{1/3}$
    - vorn laminar, hinten turbulent: $Nu = (0{,}037\,Re^{0{,}8} - 871)\,Pr^{1/3}$
- Rohr, quer angeströmt (zum Beispiel im Wind), $L = D$, für $Re \cdot Pr > 0{,}2$ (Gl. 7-35):

    $$
    Nu = 0{,}3 + \frac{0{,}62\,Re^{1/2}\,Pr^{1/3}}{\left[1 + (0{,}4/Pr)^{2/3}\right]^{1/4}} \left[1 + \left(\frac{Re}{282\,000}\right)^{5/8}\right]^{4/5}
    $$

**Strömung im Rohr** ($L$ = Innendurchmesser $D$)

- Laminar, $Re < 2300$, voll ausgebildet: $Nu = 3{,}66$ bei fester Wandtemperatur, $Nu = 4{,}36$ bei festem Wärmestrom (Gl. 8-61, 8-59)
- Turbulent nach Gnielinski, $3000 < Re < 5 \cdot 10^6$ und $0{,}5 \le Pr \le 2000$ (Gl. 8-70, Reibungszahl nach Gl. 8-65):

    $$
    Nu = \frac{(f/8)\,(Re - 1000)\,Pr}{1 + 12{,}7\,(f/8)^{0{,}5}\,(Pr^{2/3} - 1)} \qquad f = (0{,}790 \ln Re - 1{,}64)^{-2}
    $$

    mit der Reibungszahl $f$ des glatten Rohrs

- Einfacher, aber ungenauer, nach Dittus und Boelter, $Re > 10\,000$, $0{,}7 \le Pr \le 160$: $Nu = 0{,}023\,Re^{0{,}8}\,Pr^n$ mit $n = 0{,}4$, wenn das Fluid erwärmt wird, und $n = 0{,}3$, wenn es abkühlt (Gl. 8-68)

!!! example "Beispiel: Wasser im Heizungsrohr"
    - Innen Ø 21,7 mm, Wasser 60 °C, angenommen 0,5 m/s: $Re \approx 22\,900$, also turbulent
    - Gnielinski: $\alpha \approx 3500\ \mathrm{W/(m^2\,K)}$, Dittus und Boelter: $\alpha \approx 2900\ \mathrm{W/(m^2\,K)}$
    - Die Übung rechnet vorsichtig mit 1000 W/(m²·K). Am Ergebnis ändert das kaum etwas: Den Wärmestrom begrenzt die Luft außen, nicht das Wasser innen

!!! info "Wie genau sind solche Formeln?"
    - Die einfachen Formeln wie Dittus und Boelter können bis zu 25 % danebenliegen, genauere wie Gnielinski unter 10 % (Çengel S. 441)
    - Ein so bestimmtes α ist also eine gute Abschätzung, kein exakter Wert
    - Hängt viel an α, lohnt eine Rechnung mit kleinerem und größerem α: Ändert sich das Ergebnis kaum, reicht die Abschätzung

### Stoffwerte von Luft und Wasser

Zwischenwerte linear interpolieren.

| Luft (1 bar), T in °C | 7 | 25 | 45 | 60 | 80 |
|---|---|---|---|---|---|
| $\lambda_F$ in W/(m·K) | 0,0242 | 0,0255 | 0,0270 | 0,0281 | 0,0295 |
| $\nu$ in $10^{-5}$ m²/s | 1,399 | 1,562 | 1,749 | 1,896 | 2,097 |
| $Pr$ | 0,734 | 0,730 | 0,724 | 0,720 | 0,715 |

| Wasser, T in °C | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 |
|---|---|---|---|---|---|---|---|---|
| $\lambda_F$ in W/(m·K) | 0,579 | 0,598 | 0,614 | 0,628 | 0,641 | 0,651 | 0,660 | 0,667 |
| $\nu$ in $10^{-6}$ m²/s | 1,306 | 1,003 | 0,801 | 0,658 | 0,553 | 0,474 | 0,413 | 0,364 |
| $Pr$ | 9,47 | 7,01 | 5,42 | 4,34 | 3,57 | 3,00 | 2,56 | 2,23 |

## Wie man es in der Praxis macht

| Fall | üblicher Weg | im Kurs |
|---|---|---|
| Wände, Fenster, Decken im Gebäude | Normwerte nach DIN EN ISO 6946, sie enthalten die Strahlung | P1 Außenwand |
| Rohre und Bauteile in ruhender Luft | freie Konvektion: Schnellformel oder Tab. 9-1 | Heizungsrohr, Kühlkörper |
| Außenflächen im Wind | erzwungene Konvektion: Platte oder quer angeströmtes Rohr, in der Bauphysik $\alpha_K = 4 + 4\,v$ | Vakuumröhre |
| Wasser in Rohren | Strömung im Rohr: laminar 3,66, turbulent Gnielinski | Heizungsrohr, Vakuumröhre |
| Elektronik mit Lüfter | erzwungene Konvektion, oft Angaben des Herstellers | Kühlkörper |
| Sieden und Kondensieren | eigene Formeln (Çengel Kap. 10), α sehr groß | |
| Wenn es genau sein muss | Strömungssimulation (CFD) oder Messung | |

## In ANSYS

- `Convection`: **Film Coefficient** in W/(m²·°C), das ist dasselbe wie W/(m²·K), und **Ambient Temperature** in °C
- Meist reicht ein fester Wert für α
- Hängt α stark von der Temperatur ab (freie Konvektion), lässt sich der **Film Coefficient** auch als Tabelle über der Temperatur eingeben
- Unter **Film Coefficient** bietet ANSYS mit `Import Temperature Dependent` fertige Ansätze an, zum Beispiel für ruhende Luft am waagerechten Zylinder. Vorher prüfen, ob der Ansatz passt: Der Ansatz für den Zylinder ist die Formel für turbulente Strömung, kleine Rohre sind meist laminar

## Quellen

- Y. A. Çengel: *Heat Transfer. A Practical Approach.* 2. Auflage, McGraw-Hill 2002: Tab. 1-5 (S. 26), Gl. 7-21 bis 7-24 (S. 374), Gl. 7-35 (S. 385), Gl. 8-59 und 8-61 (S. 436), Gl. 8-65, 8-68 und 8-70 (S. 441), Tab. 9-1 (S. 468), Tab. 15-1 (S. 815). Stoffwerte von Luft aus Tab. A-15, wie in den Rechenbeispielen zitiert (S. 377, 387, 388, 470, 482)
- Stoffwerte von Wasser: NIST Chemistry WebBook, Thermophysical Properties of Fluid Systems, Wasser im Sättigungszustand
- DIN EN ISO 6946: Bauteile, Wärmedurchlasswiderstand und Wärmedurchgangskoeffizient (Wärmeübergangswiderstände)
- Ansatz in ANSYS: ANSYS Learning Forum, Antwort eines ANSYS-Mitarbeiters zu `Import Temperature Dependent`
- Nachrechnung der Beispiele: `tools/sollwerte/p2_konvektion.py` im Kurs-Repository
