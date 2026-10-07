---
title: Analytische Lösung
icon: material/calculator-variant
---

# Analytische Lösung

<div class="task-tabs-src" data-tabs="Aufgabe=../|a) Temperaturen=../01-material/|b) Konvektion=../b-konvektion/|Analytische Lösung=./" hidden></div>

Für die ebene Wand gibt es eine exakte Lösung. Mit ihr lässt sich jedes
FEM-Ergebnis dieses Beispiels prüfen.

## Fouriersches Gesetz und Wärmewiderstand

Stationär und ohne Wärmequellen ist die Wärmestromdichte in allen Schichten
gleich. In jeder Schicht fällt die Temperatur **linear** ab:

$$\dot q = \frac{\lambda}{d}\,\Delta T \qquad\Longleftrightarrow\qquad \Delta T = \dot q\,\underbrace{\frac{d}{\lambda}}_{R}$$

Der **Wärmedurchlasswiderstand** $R = d/\lambda$ (in m²·K/W) verhält sich
wie ein elektrischer Widerstand: Schichten hintereinander werden **addiert**.

| Schicht | $d$ | $\lambda$ | $R = d/\lambda$ |
|---|---|---|---|
| Kalksandstein | 0,175 m | 0,99 W/(m·K) | 0,177 m²·K/W |
| EPS | 0,140 m | 0,035 W/(m·K) | 4,000 m²·K/W |
| **Summe** | | | **4,177 m²·K/W** |

Die Dämmung hat über **95 %** des Widerstands. Deshalb fällt dort fast die
ganze Temperatur ab.

## Fall a) Oberflächentemperaturen

$$\dot q = \frac{T_i - T_e}{R_{KS} + R_{EPS}} = \frac{30\ \mathrm{K}}{4{,}177\ \mathrm{m^2K/W}} = 7{,}18\ \mathrm{W/m^2}$$

$$T_{Fuge} = T_i - \dot q\,R_{KS} = 20\ \mathrm{°C} - 7{,}18 \cdot 0{,}177\ \mathrm{K} = 18{,}73\ \mathrm{°C}$$

## Fall b) Konvektion

Der Wärmeübergang an der Oberfläche ist ein zusätzlicher Widerstand
$R_s = 1/\alpha$. Mit $R_{si} = 1/7{,}7 = 0{,}130$ und $R_{se} = 1/25 = 0{,}040$
(das sind genau die Normwerte nach DIN EN ISO 6946):

$$R_T = R_{si} + R_{KS} + R_{EPS} + R_{se} = 0{,}130 + 0{,}177 + 4{,}000 + 0{,}040 = 4{,}347\ \mathrm{m^2K/W}$$

$$U = \frac{1}{R_T} = 0{,}230\ \mathrm{\frac{W}{m^2K}} \qquad \dot q = U\,(T_i - T_e) = 6{,}90\ \mathrm{W/m^2}$$

$$T_{si} = T_i - \dot q\,R_{si} = 20 - 6{,}90 \cdot 0{,}130 = 19{,}10\ \mathrm{°C}$$

## Vergleich

| Größe | FEM | Analytisch |
|---|---|---|
| $\dot q$ Fall a) | 7,18 W/m² | 7,18 W/m² |
| $T_{Fuge}$ Fall a) | 18,73 °C | 18,73 °C |
| $\dot q$ Fall b) | 6,90 W/m² | 6,90 W/m² |
| $T_{si}$ Fall b) | 19,10 °C | 19,10 °C |
| $U$ | 0,230 W/(m²·K) | 0,230 W/(m²·K) |

FEM und Handrechnung stimmen **exakt** überein, weil der Temperaturverlauf je
Schicht linear ist und die Elemente das genau abbilden können.

!!! tip "Merke: Plausibilität prüfen"
    In jedem Schritt bis zum Ergebnis können kleine Fehler passieren (Einheit,
    falsche Fläche, Material nicht zugewiesen). Deshalb das Ergebnis **immer**
    prüfen: mit einer Handrechnung, mit einer Abschätzung oder mit Messwerten.
