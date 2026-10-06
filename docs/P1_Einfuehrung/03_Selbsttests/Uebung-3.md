---
title: "Übung 3: Sanierung nach GEG"
---

# Übung 3: Sanierung nach GEG

Der Altbau aus Übung 2 soll außen gedämmt werden. Nach dem Gebäudeenergiegesetz
(GEG) darf die sanierte Außenwand höchstens $U = 0{,}24\ \mathrm{W/(m^2K)}$
haben. Wie dick muss die Dämmung mindestens sein?

<figure style="text-align:center;">
  <img src="../../images/p1_uebung3.svg" alt="Vollziegelwand mit Dämmung der Dicke d" width="560" class="no-lightbox">
</figure>

## Gegeben

- Vollziegel 365 mm wie in Übung 2, außen **EPS** mit $\lambda = 0{,}035\ \mathrm{W/(m\,K)}$, Dicke $d$ gesucht
- Randbedingungen wie im Vorzeigebeispiel **Fall b) Konvektion**

## Hinweise

- Erst von Hand abschätzen: Welcher Gesamtwiderstand $R_T$ gehört zu $U = 0{,}24$? Wie viel davon fehlt noch?
- Dann das Modell aufbauen (Dämmung wie im Vorzeigebeispiel als zweiter Körper, Share Topology) und prüfen, ob die FEM den Zielwert trifft
- Wer möchte: Dicke in SpaceClaim ein paar Mal ändern und den U-Wert über der Dicke auftragen

## Gesucht

### Mindestdicke der Dämmung in mm

<div class="numeric-question" data-answer="121.1" data-tolerance="1.5" data-points="5" data-attempts="5" data-hints="R_T = 1/U = 4,167 m²K/W. Davon Übergänge (0,130 + 0,040) und Vollziegel (0,537) abziehen, Rest mal λ der Dämmung.">
</div>

### Wärmestromdichte bei dieser Dicke in W/m²

<div class="numeric-question" data-answer="7.20" data-tolerance="0.05" data-points="5" data-attempts="5" data-hints="Bei U = 0,24 W/(m²K) und 30 K Temperaturunterschied.">
</div>

<div class="solution-images" markdown="1">

### Lösung

- $R_T = 1/0{,}24 = 4{,}167\ \mathrm{m^2K/W}$
- fehlender Widerstand: $4{,}167 - 0{,}130 - 0{,}537 - 0{,}040 = 3{,}460\ \mathrm{m^2K/W}$
- $d = 3{,}460 \cdot 0{,}035 = 0{,}121\ \mathrm{m} = 121\ \mathrm{mm}$, in der Praxis also **12 cm** Dämmung oder mehr
- $\dot q = 0{,}24 \cdot 30 = 7{,}20\ \mathrm{W/m^2}$, etwa ein **Sechstel** des Altbau-Werts

</div>
