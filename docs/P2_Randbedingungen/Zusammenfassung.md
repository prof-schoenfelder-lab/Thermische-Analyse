---
title: Zusammenfassung
icon: material/head-snowflake
hide:
  - toc
---

# :material-head-snowflake: Zusammenfassung

In diesem Praktikum ging es um die Randbedingungen der Wärmeleitung, am
Vorzeigebeispiel der Vakuumröhre eines Solarkollektors: Sonne, Wasser, Luft
und Wärmestrahlung zum Himmel und zwischen Absorber und Glas.

<figure style="text-align:center;">
  <img src="../images/p2_rb_gruppen.excalidraw.png" alt="Drei Gruppen von Randbedingungen: an der Systemgrenze, im ganzen Körper, überall" class="no-lightbox">
</figure>

Die wichtigsten Kernaussagen:

<div class="steps" markdown="1" data-spickzettel="ja">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingungen wirken an der Systemgrenze, im ganzen Körper oder überall</p>
    <ul>
      <li>An der Systemgrenze: Konvektion, Strahlung, Wärmestromdichte, Wärmestrom</li>
      <li>Im ganzen Körper: Wärmeerzeugung</li>
      <li>Überall: feste Temperatur auf Fläche, Kante, Punkt oder Körper</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Jede Randbedingung legt eine Größe fest, die andere rechnet ANSYS aus</p>
    <ul>
      <li>Feste Temperatur: Der Wärmestrom ist Ergebnis</li>
      <li>Wärmestrom, Wärmestromdichte: Die Temperatur ist Ergebnis</li>
      <li>Konvektion und Strahlung: Ein Gesetz verknüpft beide</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Konvektion und Strahlung wirken gleichzeitig</p>
    <ul>
      <li>Beide auf dieselbe Fläche setzen: Ihre Wärmeströme addieren sich</li>
      <li>Schon bei Raumtemperatur ist die Strahlung etwa so groß wie freie Konvektion</li>
      <li>Am Heizungsrohr (Übung 1) ist sie knapp die Hälfte des Wärmeverlusts</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Strahlung geht zur Umgebung oder zu anderen Flächen</p>
    <ul>
      <li><code>To Ambient</code>: Die Gegenseite hat eine vorgegebene Temperatur (unter freiem Himmel kälter als die Luft)</li>
      <li><code>Surface to Surface</code>: Flächen mit derselben Enclosure-Nummer strahlen sich gegenseitig an (die Sichtfaktoren rechnet ANSYS)</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Die Sonne ist eine Wärmestromdichte</p>
    <p>Vorgegeben wird nur, was die Fläche wirklich aufnimmt: Einstrahlung mal Durchlässigkeit des Glases mal Absorptionsgrad</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Die Oberfläche entscheidet über die Strahlung</p>
    <ul>
      <li>Der Emissionsgrad ist eine Eigenschaft der Oberfläche, nicht des Materials</li>
      <li>Die selektive Schicht ist im Sonnenlicht schwarz und im Infrarot wie blankes Metall</li>
      <li>Im Vorzeigebeispiel kommen so 95 % der Sonne im Wasser an, mit schwarzem Lack nur 43 %</li>
    </ul>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Die Energiebilanz ist die schnellste Kontrolle</p>
    <ul>
      <li>Im stationären Zustand ergeben vorgegebene Wärmeströme und alle Reaktionen zusammen null</li>
      <li>Reaktionen liest die Reaction Probe ab: die Randbedingung auf <strong>Solution</strong> ziehen</li>
    </ul>
  </div>

</div>

Im nächsten Praktikum geht es um **Abstraktionen und Vernetzung**: 2D-Modelle,
Symmetrie und ein passendes Netz, am Beispiel eines Fernwärmerohrs.
