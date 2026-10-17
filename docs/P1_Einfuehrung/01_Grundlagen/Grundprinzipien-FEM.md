---
title: Grundprinzip der FEM
icon: material/atom
hide:
  - toc
---

# Grundprinzip der Finite-Elemente-Methode

Die Finite-Elemente-Methode (FEM) zerlegt ein Bauteil in viele kleine, einfache
Teile (Elemente). Für jedes Element lässt sich die Wärmeleitung mit wenigen
Gleichungen beschreiben. Zusammengesetzt ergibt sich ein großes, aber lösbares
Gleichungssystem für die Temperaturen im ganzen Bauteil.

In ANSYS Workbench arbeiten Sie dafür immer dieselben **7 Schritte** ab: Material,
Geometrie, Zuweisung, Netz, Randbedingungen, Lösen, Auswertung. Was hinter den
wichtigsten Schritten steckt:

<div class="steps">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Material</p>
    <p>Für eine <strong>stationäre</strong> (zeitlich unveränderliche) Wärmeleitung genügt eine Materialgröße: die <strong>Wärmeleitfähigkeit λ</strong> in W/(m·K). Dichte und Wärmekapazität werden erst bei <strong>instationären</strong> (zeitabhängigen) Rechnungen gebraucht, in ANSYS heißen sie <em>transient</em>.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Geometrie</p>
    <p>Zunächst wird ein <strong>Bauteil erstellt</strong> (in ANSYS mit SpaceClaim) oder ein vorhandenes Bauteil <strong>eingeladen</strong> (z. B. aus einem CAD-Programm).</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Elemente (Vernetzung)</p>
    <figure style="text-align:center;">
      <img src="../../images/p1_fem_1d.svg" alt="Wand in vier Elemente zerlegt" class="no-lightbox">
    </figure>
    <p>Das Bauteil wird mit Elementen vernetzt, die Elemente sind über <strong>Knoten</strong> verbunden. Jeder Knoten hat in der thermischen Analyse genau <strong>einen Freiheitsgrad: die Temperatur T</strong> (in der Strukturmechanik sind es drei Verschiebungen).</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Randbedingungen</p>
    <p>Ohne Randbedingungen ist die Temperatur nicht bestimmt. Vorgegeben werden z. B. <strong>Temperaturen</strong> auf Flächen, <strong>Konvektion</strong> (Wärmeübergang an Luft oder Wasser), <strong>Strahlung</strong> oder ein <strong>Wärmestrom</strong>. Flächen ohne Randbedingung sind automatisch <strong>adiabat</strong> (kein Wärmestrom).</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Gleichungssystem lösen</p>
    <p>Für jedes Element gilt das <strong>Fouriersche Gesetz</strong>: Wärme fließt vom Warmen zum Kalten, und zwar umso mehr, je steiler das Temperaturgefälle ist, \(\dot q = -\lambda\,\mathrm{d}T/\mathrm{d}x\). Zusammengesetzt entsteht das Gleichungssystem</p>
    <p>$$\mathbf{K}\,\mathbf{T} = \dot{\mathbf{Q}}$$</p>
    <p>mit der Wärmeleitmatrix <strong>K</strong>, den unbekannten Knotentemperaturen <strong>T</strong> und den Knotenwärmeströmen \(\dot{\mathbf{Q}}\). Für ein Element der Länge L und Fläche A sieht das so aus:</p>
    <p>$$\frac{\lambda A}{L}\begin{bmatrix}1 & -1\\ -1 & 1\end{bmatrix}\begin{Bmatrix}T_1\\ T_2\end{Bmatrix}=\begin{Bmatrix}\dot Q_1\\ \dot Q_2\end{Bmatrix}$$</p>
    <p>Das ist das <strong>Ohmsche Gesetz für Wärme</strong>: Der <strong>Wärmeleitwert λA/L</strong> (Kehrwert des Wärmewiderstands) entspricht dem elektrischen Leitwert, die Temperaturdifferenz der Spannung, der Wärmestrom dem Strom. In der Strukturmechanik hat eine Feder dieselbe Form (Steifigkeit, Verschiebung, Kraft).</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Auswertung</p>
    <p>Aus den Knotentemperaturen werden die weiteren Größen berechnet, vor allem die <strong>Wärmestromdichte</strong></p>
    <p>$$\dot{\vec q} = -\lambda\,\operatorname{grad} T \quad \text{in W/m}^2$$</p>
    <p>Das Ergebnis muss immer auf <strong>Plausibilität</strong> geprüft werden, z. B. mit einer Handrechnung.</p>
  </div>

</div>
