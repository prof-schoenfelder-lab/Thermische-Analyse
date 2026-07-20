---
title: "Beispiel: Cerankochfeld"
---

# Beispiel: Cerankochfeld

Ein Cerankochfeld ist ein ideales Beispiel, um zwei Effekte zu kombinieren,
die bisher im Kurs nicht behandelt wurden:

1. **Strahlung von Körper zu Körper** (Surface to Surface): Das
   Heizelement überträgt seine Wärme zum großen Teil durch **Strahlung**
   auf die Unterseite der Glaskeramikplatte — nicht durch Kontakt.
2. **Anisotrope Wärmeleitung**: Die Glaskeramik leitet Wärme senkrecht zur
   Platte (zum Topf hin) anders als in der Plattenebene — genau das ist der
   Trick, damit die Kochzone heiß wird, die Fläche daneben aber
   berührbar bleibt.

<!-- TODO(NEU): Ausarbeiten —
     - Geometrie: Heizwendel/Strahlungsheizkörper unter Glaskeramikplatte
       (ggf. 2D-rotationssymmetrisch), Luftspalt dazwischen
     - Material Glaskeramik mit Orthotropic Thermal Conductivity
       (λ_eben klein, λ_senkrecht größer — Werte aus Datenblatt ergänzen)
     - Randbedingungen: Wärmeerzeugung/Temperatur am Heizelement,
       Radiation Surface-to-Surface (Enclosure) zwischen Heizelement und
       Plattenunterseite, Konvektion + Strahlung an der Oberseite
     - Auswertung: Temperaturverteilung auf der Kochfläche,
       Vergleich isotrope vs. anisotrope Wärmeleitung
     - ANSYS-Projekt + Screenshots + Klick-Tutorials erstellen
     - Übungsfragen (numeric-question) ergänzen -->

!!! warning "Im Aufbau"
    Dieses Beispiel wird gerade erstellt. Geplante Schritte:

    1. Geometrie: Heizelement unter Glaskeramikplatte (mit Luftspalt)
    2. Material: Glaskeramik mit **orthotroper Wärmeleitfähigkeit**
       (*Orthotropic Thermal Conductivity* in Engineering Data)
    3. Randbedingung **Radiation** mit Correlation = **Surface to
       Surface**: Heizelement und Plattenunterseite in ein gemeinsames
       **Enclosure**
    4. Konvektion und Strahlung an der Oberseite
    5. Auswertung: Temperaturverteilung der Kochfläche — Vergleich
       isotrope vs. anisotrope Wärmeleitung
