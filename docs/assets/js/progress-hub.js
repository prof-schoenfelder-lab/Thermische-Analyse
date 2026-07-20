// "Mein Fortschritt": Fortschrittsringe pro Praktikum + Gesamtpunkte.
// Fragenkatalog kommt vom Backend (/api/questions, ohne Antworten);
// der eigene Stand aus dem localStorage (nach OPAL-Login serverseitig gemerged).
(function () {
  'use strict';

  var PRAKTIKA = [
    { prefix: '/P1_Einfuehrung/', name: 'Praktikum 1 · Einführung', href: 'P1_Einfuehrung/' },
    { prefix: '/P2_Modellierung_Vernetzung/', name: 'Praktikum 2 · Modellierung & Vernetzung', href: 'P2_Modellierung_Vernetzung/' },
    { prefix: '/P3_Randbedingungen_Postprocessing/', name: 'Praktikum 3 · Randbedingungen & Postprocessing', href: 'P3_Randbedingungen_Postprocessing/' },
    { prefix: '/P4_Transient/', name: 'Praktikum 4 · Transiente Berechnung', href: 'P4_Transient/' },
    { prefix: '/P5_Strahlung/', name: 'Praktikum 5 · Strahlung', href: 'P5_Strahlung/' }
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
      '<div class="ph-medals">' + badgeHtml + '</div>';
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
