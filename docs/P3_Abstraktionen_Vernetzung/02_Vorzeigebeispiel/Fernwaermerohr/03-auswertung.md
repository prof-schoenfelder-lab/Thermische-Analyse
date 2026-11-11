---
title: 3 · Lösen und Auswerten
---

# 3 · Lösen und Auswerten <small>(Mechanical)</small>

<div class="task-banner" data-tabs="Aufgabe=../|a) Querschnitt=../01-modell/|b) Halbmodell=../b-halbmodell/|c) Netzstudie=../c-netzstudie/|d) Pufferspeicher=../d-pufferspeicher/" markdown>
🎯 **Jetzt:** lösen, das Temperaturfeld ansehen und den **Wärmeverlust je Meter** aus der Reaktion ablesen
</div>

## Aufgabenstellung

--8<-- "P3_Abstraktionen_Vernetzung/02_Vorzeigebeispiel/Fernwaermerohr/index.md:Gesucht"

## Lösen

??? tip "Lösen"
    1. `Rechtsklick Solution → Solve`
    2. `Rechtsklick Solution → Insert → Thermal → Temperature`, dann `Rechtsklick Solution → Evaluate All Results`

## Wärmeverlust aus der Reaktion

Wie viel Wärme über eine feste Temperatur fließt, zeigt die **Reaction Probe**
(Praktikum 2). Mit der Dicke 1000 mm ist der Wärmestrom in W gleich dem
Wärmeverlust in W je Meter Rohr.

??? tip "Kurzanleitung: Reaction Probe"
    1. Die Randbedingung **Vorlauf** mit gedrückter Maustaste auf **Solution** ziehen, umbenennen in **Reaktion Vorlauf**
    2. Genauso **Oberflaeche**: **Reaktion Oberflaeche**
    3. `Rechtsklick Solution → Evaluate All Results`, den Wärmestrom (**Heat**) im Detailfenster der Probe ablesen

- **Vorzeichen:** Am Vorlauf ist die Reaktion positiv, dort geht die Wärme in
  das Modell hinein. An der Oberfläche ist sie negativ, dort verlässt die
  Wärme das Modell.
- **Bilanz:** Beide Reaktionen zusammen ergeben null. Was das Rohr abgibt,
  kommt an der Oberfläche an.

<!-- Werte aus tools/sollwerte/p3_fernwaermerohr.py, im Klicktest durch die ANSYS-Werte ersetzen, dazu ein Bild des Temperaturfelds -->
!!! check "Checkpoint: Diese Werte sollten herauskommen"
    | Größe | Wert |
    |---|---|
    | Temperatur | 10 bis 80 °C |
    | Reaktion Vorlauf | +19,5 W |
    | Reaktion Oberflaeche | −19,5 W |

## Was die Zahlen zeigen

- **Wärmeverlust:** rund **19,5 W je Meter** Rohr. Auf 1 km Vorlauf sind das
  19,5 kW, Tag und Nacht.
- **Handrechnung:** 19,6 W/m, 0,7 % mehr. Sie nimmt das Erdreich unendlich
  ausgedehnt an, unser Block ist 6 m × 3 m groß.
- **Hersteller:** 19,0 W/m, unter etwas anderen Bedingungen (Überdeckung 0,6 m
  statt 0,8 m, Dämmung bei 50 °C gemessen).
- **Die Dämmung trägt fast alles:** Der Temperaturabfall liegt fast ganz im
  40 mm dicken PUR-Ring, das Erdreich trägt nur 13 % des Widerstands.

### Zum Nachdenken: Warum nicht einfach den PE-Mantel zur Dämmung zählen?

Im Modell fehlen Stahlrohr und PE-Mantel. Ein naheliegender Gedanke wäre, den
3,2 mm dicken PE-Mantel der Dämmung zuzuschlagen, also den Ring bis Ø 200 mm
zu zeichnen.

<div class="multiple-choice-question" data-correct="A" data-points="5" data-attempts="1">
  <div class="mc-options">
    <div class="mc-option" data-value="A">
      <input type="radio" id="p3pea" name="p3pe">
      <label for="p3pea">Dann wird die Dämmung 3,2 mm dicker, und der Wärmeverlust fällt rund 5 % zu klein aus</label>
    </div>
    <div class="mc-option" data-value="B">
      <input type="radio" id="p3peb" name="p3pe">
      <label for="p3peb">PE dämmt besser als PUR, der Wärmeverlust fällt zu groß aus</label>
    </div>
    <div class="mc-option" data-value="C">
      <input type="radio" id="p3pec" name="p3pe">
      <label for="p3pec">Das ändert nichts, der PE-Mantel trägt ja nur 0,4 % zum Widerstand bei</label>
    </div>
  </div>
</div>

<div class="solution-images" markdown="1">

### Lösung

- Der PE-Mantel ist dünn und leitet mit λ = 0,4 W/(m·K) fast 15-mal besser als PUR
- Rechnet man ihn als PUR, wird aus 3,2 mm gut leitendem Kunststoff 3,2 mm Dämmung: Der Wärmeverlust sinkt auf 18,5 W/m, rund 5 % zu wenig
- Weglassen heißt deshalb: Den Platz der Schicht übernimmt das Nachbarmaterial, das ihr in der Wärmeleitfähigkeit näher kommt, hier das Erdreich

</div>

Weiter mit [b) Halbmodell](b-halbmodell.md).
