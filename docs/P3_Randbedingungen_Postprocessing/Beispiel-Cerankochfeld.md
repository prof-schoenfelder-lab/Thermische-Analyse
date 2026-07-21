---
title: "Strahlung: Cerankochfeld"
---

# Strahlung: Cerankochfeld

Aufbauend auf der Randbedingung
[Wärmestrahlung aus der Übersicht](Randbedingungen.md#warmestrahlung-radiation)
wird hier die **Strahlung von Körper zu Körper** (Surface to Surface)
vertieft. Ein Cerankochfeld ist dafür ein ideales Beispiel, weil es zwei
Effekte kombiniert, die bisher im Kurs nicht behandelt wurden:

1. **Strahlung von Körper zu Körper** (Surface to Surface): Das
   Heizelement überträgt seine Wärme zum großen Teil durch **Strahlung**
   auf die Unterseite der Glaskeramikplatte — nicht durch Kontakt.
2. **Anisotrope Wärmeleitung**: Die Glaskeramik leitet Wärme senkrecht zur
   Platte (zum Topf hin) anders als in der Plattenebene — genau das ist der
   Trick, damit die Kochzone heiß wird, die Fläche daneben aber
   berührbar bleibt.

!!! abstract "Lernziele"
    - Unterschied **Strahlung zur Umgebung** (To Ambient) und **Strahlung
      von Körper zu Körper** (Surface to Surface, Enclosure)
    - Emissionsgrad, Stefan-Boltzmann-Gesetz, Nichtlinearität
    - **Anisotrope Wärmeleitung** (richtungsabhängige Wärmeleitfähigkeit,
      *Orthotropic Thermal Conductivity*)

<!-- WICHTIG bei der Ausarbeitung: Die "Ambient Temperature" der
     Radiation-RB ist NICHT die Umgebungs-/Lufttemperatur (bisheriger
     Lehrfehler in den alten Unterlagen) — sondern die Temperatur der
     strahlenden Umgebung. Im Beispiel sauber abgrenzen! -->
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
