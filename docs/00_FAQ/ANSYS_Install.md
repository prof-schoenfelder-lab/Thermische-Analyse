---
title: ANSYS Installation
icon: material/download-box
hide:
  - toc
---


!!! warning "Studentenversion"

    Es gibt neben der Version die im PC Pool installiert ist auch eine kostenlose Studentenversion. Die ist zum einen immer die aktuellste Version, hat aber den Nachteil, dass die Anzahl an Knoten limitiert ist. Dadurch sind manche Praktika eventuell nicht möglich. Die Empfehlung für das Praktikum ist deshalb die Nicht-Studenten Version zu installieren (Anleitung unten)



# ANSYS Installations Anleitung für Version im PC Pool ANSYS2025R2

Für das Praktikum brauchen Sie nur **Mechanical** und **SpaceClaim**. In OPAL liegen dafür drei Pakete:

| Paket | Datei in OPAL | Größe |
|---|---|---|
| Grundinstallation | `ANSYS2025R2_WINX64_DISK1.iso` bis `…_DISK8.iso` | je 6,2 bis 7,3 GB, zusammen ca. 56 GB |
| SpaceClaim | `SPACECLAIM_2025R2_WINX64.zip` | 3,9 GB |
| Service Pack 05 | `ANSYS_2025R2.05_WINX64.zip` | 31,1 GB |

Alle zehn Dateien zusammen sind 91,3 GB groß.

!!! tip "Wenig Speicherplatz? Paket für Paket"

    Laden Sie nicht alles auf einmal herunter, sondern ein Paket nach dem anderen: herunterladen, installieren, Dateien wieder löschen, dann das nächste Paket. Am meisten Platz brauchen die Grundinstallation (ca. 56 GB für die ISO-Dateien) und das Entpacken des Service Packs (kurz etwa 60 GB, weil ZIP und entpackter Ordner gleichzeitig da sind), jeweils plus Platz für die Installation selbst. Löschen Sie jedes ZIP gleich nach dem Entpacken.

<div class="steps" markdown="1" data-kategorie="Setup">

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">VPN-Client installieren und aktivieren</p>
    <p>Auf dem nachfolgenden Link mit dem HTWK Login anmelden um Download Link zu sehen: <a href="https://itsz.htwk-leipzig.de/dienste/vpn-zugriff-auf-das-hochschulnetz" target="_blank">HTWK-ITSZ-VPN</a></p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Grundinstallation: alle 8 ISO-Dateien herunterladen</p>
    <p>ANSYS Downloadlink im OPAL: <a href="https://bildungsportal.sachsen.de/opal/auth/RepositoryEntry/18448121873/CourseNode/102618893872254" target="_blank">HTWK OPAL LINK</a>. Für die Grundinstallation werden alle acht ISO-Dateien (DISK1 bis DISK8) gebraucht, SpaceClaim und Service Pack laden Sie erst später herunter.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Alle ISO-Dateien mounten und die setup.exe von DISK1 ausführen</p>
    <p>ISO-Dateien müssen nicht entpackt werden: Doppelklick auf jede ISO-Datei bindet sie in Windows als Laufwerk ein. Danach im Laufwerk von DISK1 die <code>setup.exe</code> starten.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Lizenzserver angeben</p>
    <p>Server: ansys.htwk-leipzig.de</p>
    <p>Port: 1055</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Nur diese Installationspakete auswählen</p>
    <p> Design / SpaceClaim </p>
    <p> Structures / Mechanical Products </p>
    <p>Alles andere abwählen, das spart Speicherplatz.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Nach der Installation die ISO-Dateien entfernen</p>
    <p>Erst wenn die Installation fertig ist: die eingebundenen Laufwerke auswerfen (Rechtsklick auf das Laufwerk, <code>Auswerfen</code>) und die ISO-Dateien löschen.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">SpaceClaim-Paket installieren</p>
    <p>Das SpaceClaim-ZIP aus OPAL herunterladen, entpacken und das ZIP löschen. Im entpackten Ordner <code>SPACECLAIM_2025R2_WINX64</code> die <code>setup.exe</code> ausführen. Als Lizenzserver wieder <code>ansys.htwk-leipzig.de</code> mit Port <code>1055</code> angeben. Danach den entpackten Ordner löschen.</p>
  </div>

  <div class="step">
    <p class="step-title" role="heading" aria-level="2">Service Pack 05 installieren (immer als Letztes)</p>
    <p>Das Service-Pack-ZIP aus OPAL herunterladen, entpacken und das ZIP löschen. Im Ordner <code>ANSYS_2025R2.05_WINX64</code> die <code>setup.exe</code> ausführen. Das Service Pack bringt alle installierten Teile, auch SpaceClaim, auf den aktuellen Stand. Deshalb erst nach dem SpaceClaim-Paket installieren. Danach den entpackten Ordner löschen.</p>
  </div>

</div>

!!! info "Später etwas nachinstallieren?"

    Die gelöschten Dateien werden für ANSYS selbst nicht mehr gebraucht. Wollen Sie später ein Paket ergänzen oder die Installation reparieren, laden Sie die Dateien einfach erneut aus OPAL herunter.

!!! warning "Discovery nicht zusätzlich installieren"

    Liegt im Download auch ein Einzelpaket für Discovery, dieses nicht installieren: Discovery ist in der Grundinstallation schon enthalten, und das zusätzliche Paket bricht bei einer bestehenden Installation mit einem Fehler ab.



