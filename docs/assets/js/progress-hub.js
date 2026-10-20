// "Mein Fortschritt": Fortschrittsringe pro Praktikum + Gesamtpunkte.
// Fragenkatalog kommt vom Backend (/api/questions, ohne Antworten);
// der eigene Stand aus dem localStorage (nach OPAL-Login serverseitig gemerged).
(function () {
  'use strict';

  var PRAKTIKA = [
    { prefix: '/P1_Einfuehrung/', name: 'Praktikum 1 · Einführung', href: 'P1_Einfuehrung/' },
    { prefix: '/P2_Randbedingungen/', name: 'Praktikum 2 · Randbedingungen', href: 'P2_Randbedingungen/' },
    { prefix: '/P3_Abstraktionen_Vernetzung/', name: 'Praktikum 3 · Abstraktionen & Vernetzung', href: 'P3_Abstraktionen_Vernetzung/' },
    { prefix: '/P4_Instationaer/', name: 'Praktikum 4 · Instationäre Berechnung', href: 'P4_Instationaer/' }
  ];

  function localBest(qid) {
    try {
      var rec = JSON.parse(localStorage.getItem('answer_best_' + qid));
      return rec && rec.points > 0 ? rec.points : 0;
    } catch (e) { return 0; }
  }

  function ring(pct, solved, total) {
    var r = 44, c = 2 * Math.PI * r;
    var off = c * (1 - pct);
    return '<svg viewBox="0 0 110 110" class="ph-ring">' +
      '<circle cx="55" cy="55" r="' + r + '" class="ph-ring-bg"/>' +
      '<circle cx="55" cy="55" r="' + r + '" class="ph-ring-fg" stroke-dasharray="' + c + '" stroke-dashoffset="' + off + '" transform="rotate(-90 55 55)"/>' +
      '<text x="55" y="52" class="ph-ring-num">' + solved + '/' + total + '</text>' +
      '<text x="55" y="70" class="ph-ring-sub">gelöst</text></svg>';
  }

  function localAttempts(qid) {
    try { return parseInt(localStorage.getItem('answer_attempts_' + qid), 10) || 0; } catch (e) { return 0; }
  }

  function render(hub, catalog) {
    var totalPoints = 0, totalSolved = 0, totalQ = 0;
    var firstTry = 0, comeback = false;
    var perP = {};
    var cards = PRAKTIKA.map(function (p) {
      var total = 0, solved = 0;
      Object.keys(catalog).forEach(function (qid) {
        if (qid.indexOf(p.prefix) === -1) return;
        total++;
        totalQ++;
        var best = localBest(qid);
        if (best > 0) {
          solved++; totalSolved++; totalPoints += best;
          if (best > (catalog[qid].points || 0)) firstTry++;      // Volltreffer-Bonus
          if (localAttempts(qid) >= 4) comeback = true;           // nach >=3 Fehlversuchen gelöst
        }
      });
      perP[p.prefix] = { solved: solved, total: total };
      var pct = total ? solved / total : 0;
      return '<a class="ph-card' + (pct >= 1 ? ' ph-done' : '') + '" href="../' + p.href + '">' +
        ring(pct, solved, total, p) +
        '<span class="ph-name">' + p.name + '</span>' +
        (pct >= 1 ? '<span class="ph-badge">✓ komplett</span>' : '') +
        '</a>';
    });

    var badges = (window.acEvaluateBadges && window.acEvaluateBadges(catalog)) || [];
    var earned = badges.filter(function (b) { return b.got; }).length;
    var badgeHtml = badges.map(function (b) {
      return '<div class="ph-medal' + (b.got ? ' ph-earned' : '') + '" title="' + b.desc + '">' +
        '<span class="ph-medal-icon">' + b.icon + '</span>' +
        '<span class="ph-medal-name">' + b.name + '</span>' +
        '<span class="ph-medal-desc">' + b.desc + '</span></div>';
    }).join('');

    var token = null;
    try { token = localStorage.getItem('ac_backend_token'); } catch (e) { }
    hub.innerHTML =
      '<div class="ph-summary"><strong>' + totalPoints + ' Punkte</strong> · ' +
      totalSolved + ' von ' + totalQ + ' Aufgaben gelöst' +
      (token ? ' · <span class="ph-sync">✓ über OPAL gespeichert</span>'
             : ' · <span class="ph-sync ph-sync-off">nur lokal in diesem Browser' +
               (window.AC_OPAL_URL ? ' — <a href="' + window.AC_OPAL_URL + '" target="_blank" rel="noopener">über OPAL anmelden</a>' : '') +
               '</span>') +
      '</div>' +
      '<div class="ph-grid">' + cards.join('') + '</div>' +
      '<h2>Abzeichen <small>(' + earned + '/' + badges.length + ')</small></h2>' +
      '<div class="ph-medals">' + badgeHtml + '</div>' +
      '<p class="ph-reset"><button type="button" class="md-button" id="ph-reset">Fortschritt zurücksetzen</button> ' +
      'Löscht Punkte und Abzeichen' + (token ? ', auch auf dem Server (dort samt Ihren Eingaben).' : ' in diesem Browser.') + '</p>';
    document.getElementById('ph-reset').onclick = zuruecksetzen;
  }

  // Fortschritt zurücksetzen: mit OPAL-Anmeldung erst auf dem Server (sonst holt der nächste Abgleich den
  // alten Stand zurück), dann im Browser wie beim Wechsel der Person (backend-sync.js), danach neu laden
  function zuruecksetzen() {
    if (!confirm('Ihren gesamten Fortschritt löschen? Punkte und Abzeichen gehen verloren. ' +
      'Das lässt sich nicht rückgängig machen.')) return;
    var token = null, BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
    try { token = localStorage.getItem('ac_backend_token'); } catch (e) { }
    var leeren = function () {
      try {
        Object.keys(localStorage).filter(function (k) { return /^(answer_|page_claimed|player_level)/.test(k); })
          .forEach(function (k) { localStorage.removeItem(k); });
      } catch (e) { }
      location.reload();
    };
    if (!token || !BACKEND) return leeren();
    fetch(BACKEND + '/api/reset', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
      .then(function (d) {
        // neue Generation gleich merken; andere Browser mit altem Stand leeren sich beim nächsten Abgleich selbst
        try { if (d && d.generation) localStorage.setItem('ac_generation', d.generation); } catch (e) { }
        leeren();
      })
      .catch(function () { alert('Zurücksetzen gerade nicht möglich: Dafür ist das HTWK-Netz oder VPN nötig.'); });
  }

  function init() {
    var hub = document.getElementById('progress-hub');
    if (!hub) return;
    var BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
    // Ohne Backend: statischer Fragenkatalog aus der Site (lokaler Modus)
    var url = BACKEND ? BACKEND + '/api/questions' : null;
    if (!url) {
      try {
        var s = document.querySelector('script[src*="assets/js/answer-checker.js"]');
        if (s) url = s.src.replace(/assets\/js\/answer-checker\.js.*$/, 'assets/qcatalog.json');
      } catch (e) { }
    }
    if (!url) {
      hub.innerHTML = '<p class="progress-hub-loading">Fortschrittsdaten sind gerade nicht verfügbar.</p>';
      return;
    }
    fetch(url)
      .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
      .then(function (catalog) { render(hub, catalog); })
      .catch(function () {
        hub.innerHTML = '<p class="progress-hub-loading">Fortschrittsdaten nicht erreichbar — dafür ist das HTWK-Netz oder VPN nötig.</p>';
      });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
