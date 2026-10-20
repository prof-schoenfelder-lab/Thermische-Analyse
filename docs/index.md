---
icon: material/home
title: Angewandte FEM in der Thermodynamik
hide:
  - title
  - navigation
  - toc
  - footer
---

<div class="page--home" hidden></div>

<script>
  // Über OPAL angemeldet (Token gespeichert oder gerade von OPAL zurück): Knopf und Band umschalten
  try { if (localStorage.getItem('ac_backend_token') || /[#&]ac_token=/.test(location.hash)) document.documentElement.classList.add('opal-in'); } catch (e) { }
</script>

<section class="kurs-hero">
  <div class="kurs-hero-text">
    <p class="kurs-kicker">HTWK Leipzig · Fakultät Ingenieurwissenschaften</p>
    <h1 class="kurs-hero-title">Angewandte FEM in der <span>Thermodynamik</span></h1>
    <p class="kurs-hero-lead">Temperaturfelder mit der Finite-Elemente-Methode berechnen: von der stationären Wärmeleitung bis zur instationären (transienten) Analyse und Strahlung, Schritt für Schritt in ANSYS Workbench.</p>
    <div class="kurs-hero-actions">
      <a class="kurs-btn kurs-btn--primary" href="P1_Einfuehrung/">Mit Praktikum 1 starten <span aria-hidden="true">→</span></a>
      <a class="kurs-btn kurs-btn--opal kurs-btn--out" href="https://bildungsportal.sachsen.de/opal/auth/RepositoryEntry/18416861197/CourseNode/1792463951835633004"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17l5-5-5-5v3H3v4h7v3zm9 2h-6v2h6c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-6v2h6v14z"/></svg> Über OPAL anmelden</a>
      <a class="kurs-btn kurs-btn--in" href="Fortschritt/">Mein Fortschritt</a>
    </div>
    <div class="kurs-opal">
      <div class="kurs-opal-out">
        <p class="kurs-opal-title">Mit OPAL-Anmeldung:</p>
        <ul class="kurs-opal-list">
          <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15,9H5V5H15M12,19A3,3 0 0,1 9,16A3,3 0 0,1 12,13A3,3 0 0,1 15,16A3,3 0 0,1 12,19M17,3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V7L17,3Z"/></svg><span>Punkte gespeichert und auf jedem Gerät verfügbar</span></li>
          <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13,2.05V5.08C16.39,5.57 19,8.47 19,12C19,12.9 18.82,13.75 18.5,14.54L21.12,16.07C21.68,14.83 22,13.45 22,12C22,6.82 18.05,2.55 13,2.05M12,19A7,7 0 0,1 5,12C5,8.47 7.61,5.57 11,5.08V2.05C5.94,2.55 2,6.81 2,12A10,10 0 0,0 12,22C15.3,22 18.23,20.39 20.05,17.91L17.45,16.38C16.17,18 14.21,19 12,19Z"/></svg><span>Kursfortschritt mit Abzeichen unter Mein Fortschritt</span></li>
          <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h4v-1.9l2-2V20h-.1L10 22H6V4h7v5h5v1.1l2-2V8l-6-6m6.1 11c-.1 0-.3.1-.4.2l-1 1 2.1 2.1 1-1c.2-.2.2-.6 0-.8l-1.3-1.3c-.1-.1-.2-.2-.4-.2m-2 1.8L12 20.9V23h2.1l6.1-6.1-2.1-2.1Z"/></svg><span>Eigener Spickzettel für die Prüfung, an jedem Rechner verfügbar</span></li>
        </ul>
        <p class="kurs-opal-foot">Außerhalb des HTWK-Netzes nur mit VPN: <a href="https://itsz.htwk-leipzig.de/dienste/vpn-zugriff-auf-das-hochschulnetz/" target="_blank" rel="noopener">Anleitung des ITSZ</a> (mit HTWK-Login).</p>
      </div>
      <div class="kurs-opal-in">
        <p class="kurs-opal-ok"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg><span><b>Über OPAL angemeldet:</b> Ihre Punkte, Eingaben und Ihr Spickzettel werden gespeichert, den Stand sehen Sie unter Mein Fortschritt.</span></p>
        <p class="kurs-opal-foot">Außerhalb des HTWK-Netzes braucht der Abgleich das VPN: <a href="https://itsz.htwk-leipzig.de/dienste/vpn-zugriff-auf-das-hochschulnetz/" target="_blank" rel="noopener">Anleitung des ITSZ</a> (mit HTWK-Login).</p>
      </div>
    </div>
  </div>
  <div class="kurs-hero-media"><div class="kurs-anim" role="img" aria-label="Animation: ein Rohr durch alle sieben Schritte des Simulations-Workflows"></div></div>
</section>

## Die Praktika

<!-- Daten der Praktika: extra.praktika in mkdocs.yml (auch für die Abschluss-Karte am Ende jedes Praktikums) -->
<div class="prakt-list">
{%- for p in praktika %}
  <a class="prakt-row" href="{{ p.link }}">
    <span class="prakt-body">
      <span class="prakt-label">Praktikum {{ p.nr }}</span>
      <span class="prakt-title">{{ p.titel }}</span>
      <span class="prakt-desc">{{ p.text }}</span>
    </span>
    <img class="prakt-thumb no-lightbox" src="{{ p.bild or 'assets/images/card_folgt.svg' }}" alt="">
  </a>
{%- endfor %}
</div>

<a class="home-faq" href="00_FAQ/">Fragen? Antworten auf die häufigsten gibt es im <strong>FAQ</strong> →</a>

## Dozenten

<div class="doz-list">
  <a class="doz-item" href="mailto:felix.kaule@htwk-leipzig.de">
    <img src="assets/people/Felix_Kaule.jpg" alt="Felix Kaule" class="no-lightbox">
    <span class="doz-body">
      <span class="doz-name">M.Eng. Felix Kaule</span>
      <span class="doz-mail">Felix(dot)Kaule(at)htwk-leipzig.de</span>
    </span>
  </a>
  <a class="doz-item" href="mailto:stephan.schoenfelder@htwk-leipzig.de">
    <img src="assets/people/Stephan_Schoenfelder.png" alt="Prof. Dr.-Ing. Stephan Schönfelder" class="no-lightbox">
    <span class="doz-body">
      <span class="doz-name">Prof. Dr.-Ing. Stephan Schönfelder</span>
      <span class="doz-mail">Stephan(dot)Schoenfelder(at)htwk-leipzig.de</span>
    </span>
  </a>
</div>
