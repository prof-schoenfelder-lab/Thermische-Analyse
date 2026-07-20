// Local-only numeric answer checker (single clean IIFE)
(function () {
  'use strict';

  function safeJSONParse(s) { try { return JSON.parse(s); } catch (e) { return null; } }

  // notify optional listeners (e.g. backend-sync.js) that stored results changed
  function emitChanged() {
    try { document.dispatchEvent(new CustomEvent('answer-checker:changed')); } catch (e) { }
    try { updatePlayerBadge(); evaluateBadges(true); } catch (e) { }
  }

  // Server-side answer check (data-answer/-correct sind im Build entfernt).
  // Punkte gibt es nur mit OPAL-Login; Gäste bekommen richtig/falsch-Feedback.
  function serverCheck(payload) {
    var base = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
    if (!base) return Promise.reject(new Error('no-backend'));
    var headers = { 'Content-Type': 'application/json' };
    try { var t = localStorage.getItem('ac_backend_token'); if (t) headers['Authorization'] = 'Bearer ' + t; } catch (e) { }
    return fetch(base + '/api/check', { method: 'POST', headers: headers, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error('check-failed-' + r.status); return r.json(); });
  }
  function markDone(qid) { try { localStorage.setItem('answer_done_' + qid, '1'); } catch (e) { } }
  function cacheSolution(qid, sol) { try { localStorage.setItem('answer_solution_' + qid, JSON.stringify(sol)); } catch (e) { } }
  function cachedSolution(qid) { return safeJSONParse(localStorage.getItem('answer_solution_' + qid)); }
  var CHECK_OFFLINE_MSG = 'Antwortprüfung nicht erreichbar — dafür ist das HTWK-Netz oder VPN nötig.';
  function opalLoginLink() {
    var url = window.AC_OPAL_URL;
    if (!url) return 'OPAL-Login';
    return '<a href="' + url + '" target="_blank" rel="noopener">OPAL-Login</a>';
  }

  // Configuration: attempts allowed per question
  var ATTEMPTS_ALLOWED = 5;

  // Player/Per-page helpers
  // normalize path: remove trailing slash, convert /index.html -> /, always return encoded pathname
  function getPageId() {
    try {
      var p = window.location && window.location.pathname ? window.location.pathname : (window.location && window.location.href ? (new URL(window.location.href)).pathname : '/');
      try { if (p.indexOf('/index.html') !== -1) p = p.replace(/\/index\.html$/, '/'); } catch (e) { }
      if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
      return encodeURIComponent(p);
    } catch (e) { try { return encodeURIComponent(String(window.location.pathname || window.location.href)); } catch (ee) { return String(window.location.pathname || window.location.href); } }
  }
  // compare a link pathname (e.g. url.pathname) to a stored pid (encoded)
  function pagePathMatches(linkPath, pid) {
    try {
      if (!linkPath) return false;
      var enc = encodeURIComponent(linkPath);
      if (enc === pid) return true;
      // normalize linkPath (remove index.html and trailing slash)
      var lp = String(linkPath);
      if (lp.indexOf('/index.html') !== -1) lp = lp.replace(/\/index\.html$/, '/');
      if (lp.length > 1 && lp.endsWith('/')) lp = lp.slice(0, -1);
      if (encodeURIComponent(lp) === pid) return true;
      // try decoding pid and compare raw
      try { var dec = decodeURIComponent(pid); if (dec === linkPath || dec === lp) return true; } catch (e) { }
      return false;
    } catch (e) { return false; }
  }
  // canonicalize a path or pid for stable matching (remove index.html, trailing slash, decode)
  function canonicalizePath(p) {
    try {
      var s = String(p || '');
      // if looks encoded, try decode
      try { if (s.indexOf('%') !== -1) s = decodeURIComponent(s); } catch (e) { }
      if (!s.startsWith('/')) {
        try { s = new URL(s, location.href).pathname; } catch (e) { }
      }
      try { if (s.indexOf('/index.html') !== -1) s = s.replace(/\/index\.html$/, '/'); } catch (e) { }
      if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1);
      return s;
    } catch (e) { try { return String(p || ''); } catch (ee) { return ''; } }
  }
  function pageClaimKey(pid) { return 'page_claimed_' + pid; }
  function isPageClaimed(pid) { return localStorage.getItem(pageClaimKey(pid)) === '1'; }
  function setPageClaimed(pid) { try { localStorage.setItem(pageClaimKey(pid), '1'); } catch (e) { } }
  // Normalize a path or pid into a canonical encoded pid suitable for storage keys
  function pidForStorage(input) {
    try {
      var s = String(input || '');
      // if already encoded, try decode
      try { if (s.indexOf('%') !== -1) s = decodeURIComponent(s); } catch (e) { }
      var c = canonicalizePath(s);
      return encodeURIComponent(c);
    } catch (e) { try { return encodeURIComponent(String(input || '')); } catch (ee) { return String(input || ''); } }
  }
  function pageClaimKeyFor(input) { return 'page_claimed_' + pidForStorage(input); }
  function isPageClaimedFor(input) { try { return localStorage.getItem(pageClaimKeyFor(input)) === '1'; } catch (e) { return false; } }
  function setPageClaimedFor(input) { try { localStorage.setItem(pageClaimKeyFor(input), '1'); } catch (e) { } }
  // Find any existing page_claimed_<something> key that canonicalizes to the same page.
  function findExistingClaimKey(input) {
    try {
      var target = canonicalizePath(input && String(input) || window.location.pathname || '');
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k || k.indexOf('page_claimed_') !== 0) continue;
        try {
          var raw = k.replace('page_claimed_', '');
          var dec = raw;
          try { dec = decodeURIComponent(raw); } catch (e) { }
          var can = canonicalizePath(dec);
          if (can === target) return k; // return existing key name
        } catch (e) { }
      }
    } catch (e) { }
    return null;
  }
  // Level werden aus der Zahl gelöster Aufgaben berechnet (Meilensteine) —
  // deterministisch und dank Server-Sync auf jedem Gerät identisch.
  function countSolvedQuestions() {
    var n = 0;
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k || k.indexOf('answer_best_') !== 0) continue;
        var rec = safeJSONParse(localStorage.getItem(k));
        if (rec && rec.points > 0) n++;
      }
    } catch (e) { }
    return n;
  }
  // ensure styles for level-up notification/animation exist
  function ensureLevelUpStyles() {
    try {
      var css = '\n' +
        '.ac-level-overlay{position:fixed;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:9999;overflow:hidden}\n' +
        '.ac-piece{position:absolute;left:50%;top:40%;transform:translate(-50%,-50%);pointer-events:none;will-change:transform,opacity}\n' +
        '.ac-piece .dot{width:8px;height:8px;border-radius:50%;background:currentColor;box-shadow:0 1px 3px rgba(0,0,0,0.25)}\n' +
        '.ac-piece .confetti{width:10px;height:6px;background:currentColor;border-radius:2px;box-shadow:0 1px 2px rgba(0,0,0,0.18)}\n' +
        '.ac-piece.triangle .confetti{width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:10px solid currentColor;background:transparent;border-radius:0}\n' +
        '.ac-piece.ribbon{width:12px;height:80px;border-radius:6px;background:linear-gradient(90deg, rgba(255,255,255,0.12), rgba(255,255,255,0));transform-origin:center top;overflow:visible}\n' +
        '.ac-piece .tail{position:absolute;left:50%;top:50%;width:6px;height:40px;transform:translate(-50%,-10%);border-radius:3px;background:linear-gradient(180deg,currentColor,transparent);filter:blur(2px);opacity:0.9}\n' +
        '@keyframes ac-move-long{0%{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(0deg)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(0.7) rotate(var(--rot,0deg))}}\n' +
        '@keyframes ac-wiggle{0%{transform:translateX(0)}25%{transform:translateX(var(--wx,6px))}50%{transform:translateX(calc(var(--wx,6px) * -1))}75%{transform:translateX(var(--wx,4px))}100%{transform:translateX(0)}}\n' +
        '.ac-piece.move{animation:ac-move-long var(--dur,3200ms) cubic-bezier(.22,.9,.4,1) forwards}\n' +
        '.ac-piece .inner-wiggle{display:block;animation:ac-wiggle calc(var(--dur,3200ms) / 2) ease-in-out infinite}\n' +
        '.ac-ribbon-curve{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}\n' +
        '.ac-toast{position:fixed;right:20px;bottom:20px;background:linear-gradient(135deg,#111827,#1f2937);color:#fff;padding:12px 16px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.35);z-index:10001;pointer-events:auto;opacity:0;transform:translateY(10px);transition:opacity .24s,transform .24s;font-family:system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}\n' +
        '.ac-toast.show{opacity:1;transform:translateY(0)}\n' +
        '.ac-toast .title{font-weight:700;margin-bottom:6px;display:block;font-size:1.05rem}\n' +
        '.ac-toast .desc{font-size:0.95rem;opacity:0.95}\n';
      var sid = 'answer-checker-level-styles';
      var existing = document.getElementById(sid);
      if (existing) {
        try { existing.textContent = css; } catch (e) { /* ignore */ }
      } else {
        var s = document.createElement('style'); s.id = sid; s.appendChild(document.createTextNode(css)); document.head.appendChild(s);
      }
      // keep a flag for quick checks
      window.__answerCheckerLevelStyles = true;
    } catch (e) { }
  }

  // show a small firework-like particle burst and a toast notification for level up
  function showBadgeUp(badge) {
    showCelebration('Abzeichen verdient: ' + badge.icon + ' ' + badge.name, badge.desc, 4);
  }

  function showCelebration(titleHtml, descHtml, stars) {
    try {
      ensureLevelUpStyles();
      // try to use canvas-confetti for a nicer burst; load it dynamically if missing
      var colors = ['#ff4d6d', '#ffd14d', '#6ef27a', '#4fd3ff', '#c77bff', '#ffb86b'];
      function loadConfetti(cb) {
        if (window.confetti) return cb();
        try {
          var s = document.createElement('script');
          s.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js';
          s.async = true;
          s.onload = function () { setTimeout(cb, 10); };
          s.onerror = function () { cb(); };
          document.head.appendChild(s);
        } catch (e) { cb(); }
      }
      loadConfetti(function () {
        try {
          if (window.confetti && typeof window.confetti === 'function') {
            // create an instance that auto-resizes
            var conf = window.confetti;
            // determine particle counts based on stars (0..5)
            var starCount = (typeof stars === 'number' && isFinite(stars)) ? Math.max(0, Math.min(5, Math.round(stars))) : null;
            if (starCount === null) {
              // try to infer from current page percent
              try { var pid = getPageId(); var pct = computePagePercent(pid); starCount = Math.round(Math.max(0, Math.min(1, pct)) * 5); } catch (e) { starCount = 3; }
            }
            var mapping = [20, 40, 80, 140, 220, 320];
            var base = mapping[starCount] || 80;
            var secondary = Math.round(base * 1.4);
            try {
              conf({ particleCount: Math.max(6, Math.round(base * 0.6)), spread: 55, startVelocity: 40, ticks: 125, origin: { x: 0.5, y: 0.45 }, colors: colors });
              setTimeout(function () { try { conf({ particleCount: base, spread: 120 + starCount * 8, startVelocity: 30, ticks: 150, origin: { x: 0.5, y: 0.6 }, colors: colors }); } catch (e) { } }, 30);
              setTimeout(function () { try { conf({ particleCount: secondary, spread: 160 + starCount * 10, startVelocity: 20, ticks: 175, origin: { x: 0.5, y: 0.7 }, colors: colors }); } catch (e) { } }, 75);
            } catch (e) { /* fallback single call */
              try { conf({ particleCount: Math.max(40, base), spread: 100, origin: { y: 0.5 }, colors: colors }); } catch (e) { }
            }
          } else {
            // library not available: no-op (toast still shows)
          }
        } catch (e) { }
      });

      // toast
      var toast = document.createElement('div'); toast.className = 'ac-toast';
      toast.innerHTML = '<span class="title">' + titleHtml + '</span><span class="desc">' + descHtml + '</span>';
      document.body.appendChild(toast);
      // show
      setTimeout(function () { try { toast.classList.add('show'); } catch (e) { } }, 20);
      // hide and remove after longer display (9s)
      setTimeout(function () { try { toast.classList.remove('show'); setTimeout(function () { try { toast.parentNode && toast.parentNode.removeChild(toast); } catch (e) { } }, 300); } catch (e) { } }, 9000);
    } catch (e) { }
  }

  function updatePlayerBadge() {
    var header = document.querySelector('.md-header__inner');
    if (!header) return;
    var id = 'player-badge';
    var el = document.getElementById(id);
    if (!el) {
      // Link zur Fortschritt-Seite (statt Level-Zahl im Header)
      el = document.createElement('a');
      el.id = id;
      el.className = 'player-badge';
      var logo = document.querySelector('.md-header__button.md-logo');
      if (logo && logo.parentNode) logo.parentNode.insertBefore(el, logo.nextSibling);
      else header.insertBefore(el, header.firstChild);
    }
    try {
      var target = document.querySelector('.md-tabs__link[href*="Fortschritt"]') ||
        document.querySelector('.md-nav__link[href*="Fortschritt"]');
      if (target) el.href = target.getAttribute('href');
    } catch (e) { }
    try {
      // Mini-Fortschrittsring: füllt sich mit dem persönlichen Gesamtfortschritt
      var solved = countSolvedQuestions();
      var total = questionTotal();
      var pct = total ? Math.max(0, Math.min(1, solved / total)) : 0;
      var C = 56.55; // 2*pi*9
      el.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
        '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-opacity=".25" stroke-width="3"/>' +
        '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"' +
        ' stroke-dasharray="' + C + '" stroke-dashoffset="' + (C * (1 - pct)).toFixed(2) + '" transform="rotate(-90 12 12)"/></svg>';
      el.setAttribute('aria-label', 'Mein Fortschritt');
      el.title = 'Mein Fortschritt' + (total ? ' — ' + solved + ' von ' + total + ' Aufgaben gelöst' : '');
    } catch (e) { }
  }

  // Fragenkatalog (aus /api/questions, ohne Antworten), 6h im localStorage gecacht
  function cachedCatalog() {
    try {
      var rec = safeJSONParse(localStorage.getItem('ac_qcatalog'));
      if (rec && rec.data) return rec.data;
    } catch (e) { }
    return null;
  }
  function questionTotal() {
    var cat = cachedCatalog();
    return cat ? Object.keys(cat).length : null;
  }
  // Ohne Backend liegt der Katalog (ohne Antworten) als statische Datei in
  // der Site (assets/qcatalog.json, erzeugt vom Build-Hook).
  function localCatalogUrl() {
    try {
      var s = document.querySelector('script[src*="assets/js/answer-checker.js"]');
      if (!s) return null;
      return s.src.replace(/assets\/js\/answer-checker\.js.*$/, 'assets/qcatalog.json');
    } catch (e) { return null; }
  }
  function refreshQuestionTotal() {
    try {
      var base = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
      if (!window.fetch) return;
      var url = base ? base + '/api/questions' : localCatalogUrl();
      if (!url) return;
      var rec = safeJSONParse(localStorage.getItem('ac_qcatalog'));
      if (rec && rec.t && (Date.now() - rec.t) < 21600000) return;
      fetch(url)
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (cat) {
          if (!cat) return;
          localStorage.setItem('ac_qcatalog', JSON.stringify({ t: Date.now(), data: cat }));
          updatePlayerBadge();
          evaluateBadges(false); // Baseline ohne Feuerwerk
        })
        .catch(function () { });
    } catch (e) { }
  }

  // --- Abzeichen: zentral ausgewertet, gefeiert im Moment des Verdienens ----
  var BADGE_PRAKTIKA = [
    ['/P1_Einfuehrung/', 'Einführungs-Profi', '📥', 'Praktikum 1 komplett gelöst'],
    ['/P2_Modellierung_Vernetzung/', 'Netz-Meister', '🕸️', 'Praktikum 2 komplett gelöst'],
    ['/P3_Randbedingungen_Postprocessing/', 'Randbedingungs-Profi', '🌡️', 'Praktikum 3 komplett gelöst'],
    ['/P4_Transient/', 'Zeitschritt-Taktgeber', '⏱️', 'Praktikum 4 komplett gelöst']
  ];
  function evaluateBadges(celebrate, catOverride) {
    var cat = catOverride || cachedCatalog();
    if (!cat) return null;
    var totalQ = 0, totalSolved = 0, firstTry = 0, comeback = false;
    var per = {};
    BADGE_PRAKTIKA.forEach(function (p) { per[p[0]] = { s: 0, t: 0 }; });
    Object.keys(cat).forEach(function (qid) {
      totalQ++;
      var best = 0;
      var r = safeJSONParse(localStorage.getItem('answer_best_' + qid));
      if (r && r.points > 0) best = r.points;
      BADGE_PRAKTIKA.forEach(function (p) {
        if (qid.indexOf(p[0]) !== -1) { per[p[0]].t++; if (best > 0) per[p[0]].s++; }
      });
      if (best > 0) {
        totalSolved++;
        if (best > (cat[qid].points || 0)) firstTry++;
        if ((parseInt(localStorage.getItem('answer_attempts_' + qid), 10) || 0) >= 4) comeback = true;
      }
    });
    var defs = [
      { icon: '🚀', name: 'Erste Schritte', desc: 'Die erste Aufgabe gelöst', got: totalSolved >= 1 },
      { icon: '💪', name: 'Comeback', desc: 'Eine Aufgabe nach drei oder mehr Fehlversuchen doch noch geknackt', got: comeback },
      { icon: '🎯', name: 'Scharfschütze', desc: 'Fünf Aufgaben im ersten Versuch gelöst', got: firstTry >= 5 },
      { icon: '⏫', name: 'Halbzeit', desc: 'Die Hälfte aller Aufgaben gelöst', got: totalQ > 0 && totalSolved >= totalQ / 2 }
    ];
    BADGE_PRAKTIKA.forEach(function (p) {
      var x = per[p[0]];
      defs.push({ icon: p[2], name: p[1], desc: p[3], got: x.t > 0 && x.s >= x.t });
    });
    defs.push({ icon: '🏆', name: 'FEM-Vollprofi', desc: 'Alle Aufgaben des Kurses gelöst', got: totalQ > 0 && totalSolved >= totalQ });

    // Einmal verdient bleibt verdient; neue werden (gestaffelt) gefeiert
    var fresh = [];
    defs.forEach(function (b) {
      var key = 'answer_badge_' + b.name;
      var had = null;
      try { had = localStorage.getItem(key) === '1'; } catch (e) { }
      if (b.got && !had) {
        try { localStorage.setItem(key, '1'); } catch (e) { }
        fresh.push(b);
      }
      if (had) b.got = true;
    });
    if (celebrate) {
      fresh.forEach(function (b, idx) {
        setTimeout(function () { try { showBadgeUp(b); } catch (e) { } }, idx * 1500);
      });
    }
    return defs;
  }
  try { window.acEvaluateBadges = function (cat) { return evaluateBadges(false, cat); }; } catch (e) { }

  // --- Per-page reset button (hidden by default) ---
  function createPerPageResetIfAllowed() {
    try {
      var allow = (document.body && document.body.dataset && document.body.dataset.showReset === '1') || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
      if (!allow) return;
      var header = document.querySelector('.md-header__inner'); if (!header) return;
      var id = 'answer-reset-page-btn'; if (document.getElementById(id)) return;
      var btn = document.createElement('button'); btn.id = id; btn.className = 'answer-reset-page'; btn.type = 'button'; btn.textContent = 'Reset Ergebnisse (Seite)';
      btn.addEventListener('click', function () {
        if (!confirm('Alle lokalen Ergebnisse für diese Seite entfernen? Diese Aktion ist lokal und unwiderruflich.')) return;
        var path = location.pathname || location.href;
        var pathEnc = encodeURIComponent(path);
        var pathNoSlash = (path && path.length > 1 && path.endsWith('/')) ? path.slice(0, -1) : path;
        var removed = 0; var keys = Object.keys(localStorage);
        // prepare backup
        var backup = {};
        keys.forEach(function (k) {
          try {
            if (!k) return;
            // match keys that are answer_* and reference this page by either raw or encoded path
            if (k.indexOf('answer_') === 0 && (k.indexOf(path) !== -1 || k.indexOf(pathEnc) !== -1 || k.indexOf(pathNoSlash) !== -1)) {
              backup[k] = localStorage.getItem(k);
            }
          } catch (e) { }
        });
        // store backup (if any)
        try {
          var ts = Date.now();
          var bkey = 'answer_backup_' + encodeURIComponent(path) + '_' + ts;
          if (Object.keys(backup).length > 0) { try { localStorage.setItem(bkey, JSON.stringify(backup)); } catch (e) { } }
        } catch (e) { console.warn('Could not save backup', e); }
        // remove keys (same matching as backup)
        keys.forEach(function (k) {
          try {
            if (!k) return;
            if (k.indexOf('answer_') === 0 && (k.indexOf(path) !== -1 || k.indexOf(pathEnc) !== -1 || k.indexOf(pathNoSlash) !== -1)) {
              localStorage.removeItem(k); removed++;
            }
          } catch (e) { }
        });
        // also remove the page-claimed marker so the nav icon is unset
        try {
          var pid = pidForStorage(path);
          var claimKey = pageClaimKeyFor(path);
          if (localStorage.getItem(claimKey)) { try { localStorage.removeItem(claimKey); } catch (e) { } }
          try { var shownk2 = 'page_claimed_shown_' + pid; localStorage.removeItem(shownk2); } catch (e) { }
          // reset stars for this page (do not change nav icons)
          try { updateStarsForPage(pid); } catch (e) { }
        } catch (e) { }
        // also reset global player progress so the player level/rank returns to zero
        try {
          if (localStorage.getItem('player_level')) { try { localStorage.removeItem('player_level'); } catch (e) { } }
          if (localStorage.getItem('player_icon')) { try { localStorage.removeItem('player_icon'); } catch (e) { } }
        } catch (e) { }
        /* removed debug logs */
        location.reload();
      });
      // place to the right in header
      header.appendChild(btn);
    } catch (e) { }
  }

  // --- Debug panel for authors: show localStorage and per-question state ---
  // debug panel removed

  // --- Stars for Selbsttests (0..3) ---
  function computePagePercent(pid) {
    try {
      var pagePath = decodeURIComponent(pid);
      function normalizePath(p) { try { var s = String(p || ''); if (!s.startsWith('/')) { try { s = new URL(s, location.href).pathname; } catch (e) { } } s = decodeURIComponent(s); if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1); return s; } catch (e) { return String(p || ''); } }
      var normPage = normalizePath(pagePath);
      var sumBest = 0, sumMax = 0;
      var qidSet = Object.create(null);
      // collect qids from answer_max_
      for (var i = 0; i < localStorage.length; i++) {
        try {
          var k = localStorage.key(i);
          if (!k) continue;
          if (k.indexOf('answer_max_') === 0) {
            var qid = k.replace('answer_max_', '');
            // Split by :q or :mc to get the base path
            var base = String(qid).split(/:q|:mc/)[0] || qid;
            var normBase = normalizePath(base);
            if (normBase === normPage) qidSet[qid] = true;
          }
        } catch (e) { }
      }
      // also include qids that have best entries even if max missing
      for (var j = 0; j < localStorage.length; j++) {
        try {
          var kk = localStorage.key(j);
          if (!kk || kk.indexOf('answer_best_') !== 0) continue;
          var qid2 = kk.replace('answer_best_', '');
          // Split by :q or :mc to get the base path
          var base2 = String(qid2).split(/:q|:mc/)[0] || qid2;
          var normBase2 = normalizePath(base2);
          if (normBase2 === normPage) qidSet[qid2] = true;
        } catch (e) { }
      }
      // compute sums
      for (var qidKey in qidSet) {
        if (!Object.prototype.hasOwnProperty.call(qidSet, qidKey)) continue;
        try {
          var rec = safeJSONParse(localStorage.getItem('answer_best_' + qidKey));
          if (rec && typeof rec.points === 'number') sumBest += rec.points;
        } catch (e) { }
        try {
          var maxVal2 = parseFloat(localStorage.getItem('answer_max_' + qidKey));
          if (isFinite(maxVal2)) sumMax += maxVal2;
          else {
            // fallback: try to find question element on the current page and read dataset.points
            try {
              var sel = '[data-qid="' + qidKey.replace(/"/g, '\\"') + '"]';
              var el = document.querySelector(sel);
              if (el && el.dataset && el.dataset.points) {
                var p = parseFloat(el.dataset.points || 0);
                if (isFinite(p)) sumMax += p;
              } else {
                // as a last resort, if no max is known use recorded best as a conservative max
                if (rec && typeof rec.points === 'number') sumMax += rec.points;
              }
            } catch (e) { }
          }
        } catch (e) { }
      }
      if (sumMax <= 0) return 0;
      return Math.max(0, Math.min(1, sumBest / sumMax));
    } catch (e) { return 0; }
  }

  function computePageCounts(pid) {
    try {
      var pagePath = decodeURIComponent(pid);
      function normalizePath(p) { try { var s = String(p || ''); if (!s.startsWith('/')) { try { s = new URL(s, location.href).pathname; } catch (e) { } } s = decodeURIComponent(s); if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1); return s; } catch (e) { return String(p || ''); } }
      var normPage = normalizePath(pagePath);
      var qidSet = Object.create(null);
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k) continue;
        var m = null;
        if (k.indexOf('answer_max_') === 0) m = k.replace('answer_max_', '');
        else if (k.indexOf('answer_best_') === 0) m = k.replace('answer_best_', '');
        else if (k.indexOf('answer_done_') === 0) m = k.replace('answer_done_', '');
        if (!m) continue;
        var base = String(m).split(/:q|:mc/)[0] || m;
        if (normalizePath(base) === normPage) qidSet[m] = true;
      }
      var total = 0, solved = 0;
      for (var qid in qidSet) {
        if (!Object.prototype.hasOwnProperty.call(qidSet, qid)) continue;
        total++;
        // "gelöst" heißt: Punkte geholt. Das done-Flag (auch bei aufgebrauchten
        // Versuchen gesetzt) zählt hier bewusst NICHT — sonst gäbe es einen
        // grünen Haken für 0 Punkte.
        var rec = safeJSONParse(localStorage.getItem('answer_best_' + qid));
        if (rec && rec.points > 0) solved++;
      }
      return { solved: solved, total: total };
    } catch (e) { return { solved: 0, total: 0 }; }
  }

  // Mastery-Anzeige in der Navigation: Häkchen für komplett gelöste Seiten,
  // sonst "gelöst/gesamt" — ersetzt die frühere 5-Sterne-Skala.
  function renderProgressMark(counts) {
    if (!counts || counts.total <= 0) return '<span class="page-stars" aria-hidden="true"></span>';
    if (counts.solved >= counts.total) return '<span class="page-stars page-check" aria-hidden="true">✓</span>';
    return '<span class="page-stars page-count" aria-hidden="true">' + counts.solved + '/' + counts.total + '</span>';
  }

  function renderStarsForPercent(pct) {
    // map pct (0..1) to 0..5 stars using rounding
    var stars = Math.round(Math.max(0, Math.min(1, pct)) * 5);
    var out = '<span class="page-stars" aria-hidden="true">';
    for (var i = 0; i < 5; i++) {
      out += '<span class="star' + (i < stars ? ' filled' : '') + '">★</span>';
    }
    out += '</span>';
    return out;
  }

  function updateStarsForPage(pid) {
    try {
      // Only show stars for a page if the page has been attempted (any question had attempts or stored best)
      var attempted = pageIsAttempted(pid);
      var starsHtml = renderProgressMark(computePageCounts(pid));
      var links = document.querySelectorAll('.md-nav__link');
      links.forEach(function (link) {
        var href = link.getAttribute('href'); if (!href) return;
        // Skip links that are part of the page TOC / secondary nav (we don't want stars in the in-page TOC)
        try {
          // Only skip when the link is inside the secondary nav container (the in-page TOC),
          // not for all nav lists (primary left nav uses .md-nav__list as well).
          if (link.closest && link.closest('.md-nav--secondary')) return;
        } catch (e) { }
        try {
          var url = new URL(href, location.href);
          var linkPath = url.pathname || '';
          // Show stars for all pages with numeric questions (removed path restriction)
          if (pagePathMatches(linkPath, pid)) {
            var existing = link.querySelector('.page-stars');
            if (!attempted) {
              // remove any existing stars if page not yet attempted
              if (existing) { try { existing.parentNode && existing.parentNode.removeChild(existing); } catch (e) { } }
            } else {
              if (existing) {
                // only replace if different to avoid triggering mutation observers
                try { if ((existing.outerHTML || '').trim() !== (starsHtml || '').trim()) existing.outerHTML = starsHtml; } catch (e) { }
              } else {
                var span = link.querySelector('.md-ellipsis') || link;
                // avoid inserting duplicate if already present
                if (!span.querySelector || !span.querySelector('.page-stars')) {
                  var wrap = document.createElement('span'); wrap.innerHTML = starsHtml;
                  span.appendChild(wrap.firstChild);
                }
              }
            }
          }
        } catch (e) { }
      });
    } catch (e) { }
  }

  // Determine whether any question on the page has been attempted (attempts > 0) or has a stored best
  function pageIsAttempted(pid) {
    try {
      // normalize helper similar to computePagePercent
      function normalizePath(p) { try { var s = String(p || ''); if (!s.startsWith('/')) { try { s = new URL(s, location.href).pathname; } catch (e) { } } s = decodeURIComponent(s); if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1); return s; } catch (e) { return String(p || ''); } }
      var pagePath = decodeURIComponent(pid);
      var normPage = normalizePath(pagePath);
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k) continue;
        if (k.indexOf('answer_attempts_') === 0 || k.indexOf('answer_best_') === 0) {
          var qid = k.replace(/^answer_(?:attempts|best)_/, '');
          // Split by :q or :mc to get the base path
          var base = String(qid).split(/:q|:mc/)[0] || qid;
          var normBase = normalizePath(base);
          if (normBase === normPage) {
            // if attempts key, check value > 0; if best key, any stored record counts as attempt
            if (k.indexOf('answer_attempts_') === 0) { var val = parseInt(localStorage.getItem(k) || '0', 10) || 0; if (val > 0) return true; }
            else { var rec = safeJSONParse(localStorage.getItem(k)); if (rec) return true; }
          }
        }
      }
      return false;
    } catch (e) { return false; }
  }

  // Material-like SVGs for nav icon swapping
  var blankCircleOutlineSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8.009 8.009 0 0 1-8 8z"/></svg>';
  var markedCircleSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l6.59-6.59L19 9z"/></svg>';
  // icon to show when a test is claimed but yields 0 stars (checkbox-blank-circle)
  var zeroStarCircleSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>';

  function initializeNavIcons() {
    try {
      var links = document.querySelectorAll('.md-nav__link');
      var pid = getPageId();
      links.forEach(function (link) {
        var href = link.getAttribute('href'); if (!href) return;
        try {
          var url = new URL(href, location.href);
          var linkPath = url.pathname || '';
          // Initialize stars for all pages with numeric questions (removed path restriction)
          var linkPid = encodeURIComponent(url.pathname);
          try { updateStarsForPage(linkPid); } catch (e) { }
        } catch (e) { }
      });
    } catch (e) { }
  }

  function updateNavForPageClaim(pid) {
    try { updateStarsForPage(pid); } catch (e) { }
  }

  // Ensure we re-apply nav icons/stars if the theme re-renders the nav.
  // Uses MutationObserver when available and safe; falls back to short polling.
  function ensureNavObserver() {
    try {
      if (window.__answerCheckerNavObserverInstalled) return;
      var attempts = 0;
      var maxAttempts = 8;
      function tryAttach() {
        var nav = document.querySelector('.md-nav') || document.querySelector('nav') || document.querySelector('.md-sidebar');
        if (nav && nav.nodeType === 1) {
          try {
            if (typeof MutationObserver !== 'undefined') {
              var mo = new MutationObserver(function () {
                try {
                  // schedule a single debounced nav update to avoid feedback loops
                  scheduleNavUpdate();
                } catch (e) { }
              });
              try {
                // guard observe call - ensure nav is a Node
                if (nav && typeof nav.nodeType === 'number') mo.observe(nav, { childList: true, subtree: true });
                window.__answerCheckerNavObserver = mo;
                window.__answerCheckerNavObserverInstalled = true;
              } catch (e) {
                // if observe fails, fall back to polling
                console.warn('answer-checker: observer.observe failed, using polling fallback', e);
                var poll = setInterval(function () { try { initializeNavIcons(); } catch (e) { } }, 500);
                window.__answerCheckerNavPoll = poll; window.__answerCheckerNavObserverInstalled = true;
              }
            } else {
              var poll2 = setInterval(function () { try { initializeNavIcons(); } catch (e) { } }, 500);
              window.__answerCheckerNavPoll = poll2; window.__answerCheckerNavObserverInstalled = true;
            }
          } catch (e) { }
        } else {
          attempts++;
          if (attempts <= maxAttempts) setTimeout(tryAttach, 300);
        }
      }
      tryAttach();
    } catch (e) { console.warn('answer-checker: ensureNavObserver failed', e); }
  }

  // Debounced and rate-limited nav update scheduler to avoid infinite mutation feedback loops
  function scheduleNavUpdate() {
    try {
      if (!window.__answerCheckerNavUpdateCount) window.__answerCheckerNavUpdateCount = 0;
      // limit total updates per page session to avoid runaway loops
      if (window.__answerCheckerNavUpdateCount > 50) return;
      window.__answerCheckerNavUpdateCount += 1;
      if (window.__answerCheckerNavUpdateTimer) clearTimeout(window.__answerCheckerNavUpdateTimer);
      window.__answerCheckerNavUpdateTimer = setTimeout(function () {
        try { initializeNavIcons(); } catch (e) { }
        window.__answerCheckerNavUpdateTimer = null;
      }, 250);
    } catch (e) { }
  }

  // allow per-page nav icon override: data-page-icon on the page container
  // replace the nav link's inline SVG for a page identified by pid
  function replaceNavIcon(pid, svgHtml) {
    // Icon replacement disabled: do nothing. Kept for backward compatibility calls.
    return;
  }

  function checkPageCompletion() {
    var pid = getPageId();
    // Normalize and detect existing claims under different encodings.
    try {
      var existing = findExistingClaimKey(pid) || findExistingClaimKey(window.location.pathname) || findExistingClaimKey(decodeURIComponent(pid));
      if (existing) {
        // ensure canonical claim key exists and copy shown flag if present
        try {
          var raw = existing.replace('page_claimed_', '');
          var canPid = pidForStorage(raw);
          var canKey = 'page_claimed_' + canPid;
          if (!localStorage.getItem(canKey)) {
            try { localStorage.setItem(canKey, '1'); } catch (e) { }
          }
          // copy shown flag if present
          var shownOld = 'page_claimed_shown_' + raw;
          var shownNew = 'page_claimed_shown_' + canPid;
          if (localStorage.getItem(shownOld) && !localStorage.getItem(shownNew)) {
            try { localStorage.setItem(shownNew, localStorage.getItem(shownOld)); } catch (e) { }
          }
        } catch (e) { }
        updatePlayerBadge(); updateNavForPageClaim(pid); return;
      }
    } catch (e) { }

    // Check both numeric and multiple choice questions
    var qs = document.querySelectorAll('.numeric-question');
    var mcqs = document.querySelectorAll('.multiple-choice-question');
    var allQuestions = [];

    for (var i = 0; i < qs.length; i++) allQuestions.push(qs[i]);
    for (var j = 0; j < mcqs.length; j++) allQuestions.push(mcqs[j]);

    if (allQuestions.length === 0) return;

    // All questions must have a stored best > 0
    for (var k = 0; k < allQuestions.length; k++) {
      var q = allQuestions[k];
      var qid = q.dataset.qid || ((document.location.pathname || location.href) + ':q' + k);
      var rec = safeJSONParse(localStorage.getItem('answer_best_' + qid));
      if (!rec || !(rec.points > 0)) return; // not completed yet
    }

    // All completed → compute stars for this page and award level
    var pctNow = 0;
    try { pctNow = computePagePercent(pid); } catch (e) { }
    var starsNow = Math.round(Math.max(0, Math.min(1, pctNow)) * 5);
    setPageClaimedFor(pid);
    // Award level-up (incrementPlayerLevel handles idempotency and the shown-flag)
    try { incrementPlayerLevel(starsNow, pid); } catch (e) { try { incrementPlayerLevel(starsNow); } catch (e) { } }
    // Do NOT change nav icons anymore. Only stars (via updateStarsForPage) reflect progress.
  }

  // Check if all questions on the page are finished (either correct or attempts exhausted)
  function checkAllQuestionsFinished() {
    var qs = document.querySelectorAll('.numeric-question');
    var mcqs = document.querySelectorAll('.multiple-choice-question');
    var allQuestions = [];

    // Collect all questions
    for (var i = 0; i < qs.length; i++) allQuestions.push({ el: qs[i], type: 'numeric' });
    for (var j = 0; j < mcqs.length; j++) allQuestions.push({ el: mcqs[j], type: 'mc' });

    if (allQuestions.length === 0) return false;

    for (var k = 0; k < allQuestions.length; k++) {
      var q = allQuestions[k].el;
      var qid = q.dataset.qid || ((document.location.pathname || location.href) + ':q' + k);
      var attemptsAllowed = parseInt(q.dataset.attempts || q.dataset.attemptsAllowed || ATTEMPTS_ALLOWED, 10) || ATTEMPTS_ALLOWED;
      var attempts = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
      var bestRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };
      // Question is finished if: got points OR used all attempts OR was
      // answered correctly without points (Gast-Modus setzt answer_done_)
      var done = localStorage.getItem('answer_done_' + qid) === '1';
      if (!(bestRec.points > 0 || attempts >= attemptsAllowed || done)) {
        return false; // at least one question not finished yet
      }
    }
    return true; // all questions finished
  }

  // Show solution images when all questions are finished
  function showSolutionImages() {
    try {
      var container = document.querySelector('.solution-images');
      if (!container) return;
      // Check if already shown to avoid re-showing on every check
      if (container.classList.contains('solution-shown')) return;
      if (checkAllQuestionsFinished()) {
        container.classList.add('solution-shown');
        container.style.display = 'block';
        // Add a smooth fade-in effect
        container.style.opacity = '0';
        setTimeout(function () {
          container.style.transition = 'opacity 0.5s ease-in';
          container.style.opacity = '1';
        }, 10);
      }
    } catch (e) { }
  }

  function computeTotals() {
    var all = 0, today = 0, details = [];
    var todayKey = new Date().toISOString().slice(0, 10);
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (!k || k.indexOf('answer_best_') !== 0) continue;
      var rec = safeJSONParse(localStorage.getItem(k));
      if (!rec || typeof rec.points !== 'number') continue;
      all += rec.points;
      var d = rec.updated ? new Date(rec.updated).toISOString().slice(0, 10) : null;
      if (d === todayKey) today += rec.points;
      details.push({ qid: k.replace('answer_best_', ''), points: rec.points, updated: rec.updated });
    }
    details.sort(function (a, b) { return b.points - a.points; });
    return { allTime: all, today: today, details: details };
  }

  // Remove answer entries older than `maxAgeMs` (default 12h)
  function cleanupOldEntries(maxAgeMs) {
    maxAgeMs = typeof maxAgeMs === 'number' ? maxAgeMs : 12 * 60 * 60 * 1000; // 12h
    var now = Date.now();
    var toRemove = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (!k || k.indexOf('answer_best_') !== 0) continue;
      var rec = safeJSONParse(localStorage.getItem(k));
      if (!rec || !rec.updated) { continue; }
      var t = Date.parse(rec.updated);
      if (!isFinite(t)) continue;
      if ((now - t) > maxAgeMs) {
        toRemove.push(k);
      }
    }
    toRemove.forEach(function (k) {
      try { localStorage.removeItem(k); localStorage.removeItem('answer_attempts_' + k.replace('answer_best_', '')); } catch (e) { }
    });
    // After removing old answer entries, ensure page-claimed markers are still valid.
    // If a claimed page no longer has full points (percent < 1), remove the claim.
    try {
      var claimKeys = [];
      for (var j = 0; j < localStorage.length; j++) {
        var kk = localStorage.key(j);
        if (!kk) continue;
        if (kk.indexOf('page_claimed_') === 0) claimKeys.push(kk);
      }
      claimKeys.forEach(function (ck) {
        try {
          var pid = ck.replace('page_claimed_', '');
          var pct = 0;
          try { pct = computePagePercent(pid); } catch (e) { }
          // Only remove claim if there are no stored points for this page (pct === 0).
          // Previously we removed claims when pct < 1 which caused repeated award/animation
          // for partially-scored pages — keep the claim once any points exist.
          if (pct === 0) {
            try { localStorage.removeItem(ck); } catch (e) { }
            try { var shownk = 'page_claimed_shown_' + pid; localStorage.removeItem(shownk); } catch (e) { }
          }
        } catch (e) { }
      });
      // Recompute player level as number of remaining claimed pages
      var newLevel = 0;
      for (var k2 = 0; k2 < localStorage.length; k2++) {
        var key2 = localStorage.key(k2);
        if (!key2) continue;
        if (key2.indexOf('page_claimed_') === 0) newLevel++;
      }
      try { setPlayerLevel(newLevel); updatePlayerBadge(); initializeNavIcons(); } catch (e) { }
    } catch (e) { }
  }

  function renderSummary() {
    var el = document.getElementById('leaderboard-summary'); if (!el) return;
    // cleanup old entries first (default 24h)
    cleanupOldEntries();
    var t = computeTotals(); el.innerHTML = '';
    var max = 0;
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (!k) continue;
      if (k.indexOf('answer_max_') === 0) {
        var mp = parseFloat(localStorage.getItem(k));
        if (isFinite(mp)) max += mp;
      }
    }
    if (max === 0) {
      var questions = document.querySelectorAll('.numeric-question');
      for (var j = 0; j < questions.length; j++) {
        var p = parseFloat(questions[j].dataset.points || 0);
        if (isFinite(p)) max += p;
      }
    }
    // If no explicit max could be determined (e.g. leaderboard opened standalone), try to infer
    // from stored per-question bests or per-question max entries. This avoids showing 0% when
    // the user does have stored points but no answer_max_* keys.
    if (max === 0 && t.details && t.details.length > 0) {
      for (var d = 0; d < t.details.length; d++) {
        var qid = t.details[d].qid;
        var mp2 = parseFloat(localStorage.getItem('answer_max_' + qid));
        if (isFinite(mp2)) max += mp2; else max += (parseFloat(t.details[d].points) || 0);
      }
    }
    var pct = (max > 0) ? Math.round((t.allTime / max) * 100) : (t.allTime > 0 ? 100 : 0);

    // Fun rank system
    var rank = '';
    var rankDesc = '';
    if (pct < 25) { rank = 'Finites-Element'; rankDesc = 'Willkommen in der Welt der Elemente!'; }
    else if (pct < 50) { rank = 'Knotenknacker'; rankDesc = 'Du knackst Knoten wie Nüsse.'; }
    else if (pct < 75) { rank = 'Balkenbändiger'; rankDesc = 'Balken zähmst du mit Stil.'; }
    else { rank = 'Elemente‑Meister'; rankDesc = 'Du herrschst über die Elemente!'; }

    var stats = document.createElement('div'); stats.className = 'leaderboard-stats';
    stats.innerHTML = '<div><strong>Deine Punkte (aktuell)</strong>: ' + t.allTime + ' Punkte</div>' +
      '<div><strong>Max möglich</strong>: ' + max + ' Punkte</div>' +
      '<div><strong>Erreicht</strong>: ' + pct + '%</div>' +
      '<div class="leaderboard-badge">Rang: <strong>' + rank + '</strong> — ' + rankDesc + '</div>';
    el.appendChild(stats);

    // We intentionally do not show a per-question detail table here — only overall own score and max.
  }

  // Observe content changes and render summary when the leaderboard placeholder is inserted.
  function ensureContentObserver() {
    try {
      if (window.__answerCheckerContentObserverInstalled) return;
      var attempts = 0, maxAttempts = 8;
      function tryAttach() {
        var container = document.querySelector('main') || document.querySelector('.md-content') || document.body;
        if (container && container.nodeType === 1) {
          if (typeof MutationObserver !== 'undefined') {
            var mo = new MutationObserver(function (muts) {
              try {
                // if leaderboard placeholder is present, render summary
                if (document.getElementById('leaderboard-summary')) renderSummary();
              } catch (e) { }
            });
            try { mo.observe(container, { childList: true, subtree: true }); window.__answerCheckerContentObserver = mo; window.__answerCheckerContentObserverInstalled = true; }
            catch (e) { /* ignore */ window.__answerCheckerContentObserverInstalled = true; }
          } else {
            // fallback polling
            var poll = setInterval(function () { try { if (document.getElementById('leaderboard-summary')) renderSummary(); } catch (e) { } }, 500);
            window.__answerCheckerContentObserverInstalled = true; window.__answerCheckerContentPoll = poll;
          }
        } else {
          attempts++; if (attempts <= maxAttempts) setTimeout(tryAttach, 300);
        }
      }
      tryAttach();
    } catch (e) { }
  }

  function setupQuestion(q, index) {
    // use normalized page path for fallback qid to avoid collisions when pages were copied
    var normPath = (function () { try { var p = window.location && window.location.pathname ? window.location.pathname : (new URL(window.location.href)).pathname; if (p.indexOf('/index.html') !== -1) p = p.replace(/\/index\.html$/, '/'); if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1); return p; } catch (e) { return (document.location.pathname || document.location.href); } })();
    var fallbackQid = normPath + ':q' + index;
    var qid = q.dataset.qid || fallbackQid;
    q.dataset.qid = qid;

    var answer = parseFloat(q.dataset.answer);
    var tol = parseFloat(q.dataset.tolerance || 0);
    var points = parseFloat(q.dataset.points || 1) || 1;
    // persist question max so leaderboard can compute total even from the leaderboard page
    try { localStorage.setItem('answer_max_' + qid, String(points)); } catch (e) { }
    var hints = (q.dataset.hints || '').split('|').map(function (h) { return h.trim(); });

    var attempts = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
    // allow per-question override for number of attempts via data-attempts or data-attempts-allowed
    var attemptsAllowed = parseInt(q.dataset.attempts || q.dataset.attemptsAllowed || ATTEMPTS_ALLOWED, 10) || ATTEMPTS_ALLOWED;
    var bestRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };

    var input = q.querySelector('.numeric-answer-input');
    if (!input) { input = document.createElement('input'); input.type = 'text'; input.className = 'numeric-answer-input'; q.appendChild(input); }
    var btn = q.querySelector('.numeric-answer-submit');
    if (!btn) { btn = document.createElement('button'); btn.type = 'button'; btn.className = 'numeric-answer-submit'; btn.textContent = 'Antwort prüfen'; q.appendChild(btn); }
    var fb = q.querySelector('.numeric-answer-feedback'); if (!fb) { fb = document.createElement('div'); fb.className = 'numeric-answer-feedback'; q.appendChild(fb); }
    var scoreEl = q.querySelector('.numeric-answer-score'); if (!scoreEl) { scoreEl = document.createElement('div'); scoreEl.className = 'numeric-answer-score'; q.appendChild(scoreEl); }

    // Per-question local-delete button removed to avoid easy reset by students.

    function saveAttempts() { localStorage.setItem('answer_attempts_' + qid, String(attempts)); emitChanged(); }
    function saveBest(pointsVal) { localStorage.setItem('answer_best_' + qid, JSON.stringify({ points: pointsVal, updated: new Date().toISOString() })); bestRec = { points: pointsVal, updated: new Date().toISOString() }; emitChanged(); }

    function disableControls() { if (btn) btn.disabled = true; if (input) input.disabled = true; }
    function enableControls() { if (btn) btn.disabled = false; if (input) input.disabled = false; }

    function reveal(sol) {
      if (sol === undefined) sol = isFinite(answer) ? answer : cachedSolution(qid);
      fb.innerHTML += (sol === null || sol === undefined)
        ? '<div class="numeric-reveal">Keine weiteren Versuche.</div>'
        : '<div class="numeric-reveal">Beim nächsten Mal! Die Lösung: <strong>' + sol + '</strong></div>';
      disableControls();
    }

    function updateUI() {
      bestRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };
      attempts = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
      if (bestRec.points > 0) {
        scoreEl.textContent = 'Punkte: ' + bestRec.points + '/' + points;
        fb.innerHTML = '<span class="numeric-correct">Richtig — ' + bestRec.points + ' Punkte.</span>';
        disableControls();
      } else if (attempts >= attemptsAllowed) { scoreEl.textContent = 'Punkte: 0/' + points; reveal(); }
      else { scoreEl.textContent = 'Versuche: ' + attempts + '/' + attemptsAllowed; }
      // no per-question delete UI; we keep stored data immutable from the page
    }

    function submit() {
      if (attempts >= attemptsAllowed) { reveal(); return; }
      var raw = input && input.value;
      if (typeof raw === 'string') raw = raw.trim().replace(',', '.');
      // If nothing was entered (empty string or whitespace) or parsing yields NaN,
      // do NOT count this as an attempt. Prompt the user to enter a number.
      if (!raw) { fb.innerHTML = '<span class="numeric-wrong">Bitte eine Zahl eingeben.</span>'; updateUI(); return; }
      var val = parseFloat(raw);
      if (!isFinite(val)) { fb.innerHTML = '<span class="numeric-wrong">Bitte eine Zahl eingeben.</span>'; updateUI(); return; }

      // Server-Modus: data-answer ist im Build entfernt, der Server prüft.
      if (!isFinite(answer)) {
        if (btn) btn.disabled = true;
        serverCheck({ qid: qid, value: val, attemptsUsed: attempts }).then(function (res) {
          if (btn) btn.disabled = false;
          attempts = res.attempts || (attempts + 1);
          saveAttempts();
          if (res.solution !== undefined) cacheSolution(qid, res.solution);
          if (res.correct || attempts >= (res.attemptsAllowed || attemptsAllowed)) markDone(qid);
          if (res.correct) {
            if (res.authed) {
              var prev = (safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0 }).points || 0;
              if ((res.best || 0) > prev) saveBest(res.best);
              fb.innerHTML = '<span class="numeric-correct">' + ((res.earned || 0) > points ? 'Volltreffer im ersten Versuch — ' + points + ' Punkte + 1 Bonus!' : 'Richtig — ' + (res.earned || 0) + ' Punkte.') + '</span>';
              scoreEl.textContent = 'Punkte: ' + (res.best || 0) + '/' + points;
              try { checkPageCompletion(); } catch (e) { }
              try { updateStarsForPage(getPageId()); } catch (e) { }
            } else {
              fb.innerHTML = '<span class="numeric-correct">Richtig! <small>(Punkte gibt es nur mit ' + opalLoginLink() + '.)</small></span>';
              scoreEl.textContent = '';
            }
            disableControls();
            try { showSolutionImages(); } catch (e) { }
          } else {
            var aa = res.attemptsAllowed || attemptsAllowed;
            var s2 = '<span class="numeric-wrong">Noch nicht richtig (' + attempts + '/' + aa + ').</span>';
            if (hints[attempts - 1]) s2 += '<div class="numeric-hint">Hinweis: ' + hints[attempts - 1] + '</div>';
            fb.innerHTML = s2;
            if (attempts >= aa) {
              if (res.authed) scoreEl.textContent = 'Punkte: 0/' + points;
              reveal(res.solution);
              try { showSolutionImages(); } catch (e) { }
            } else updateUI();
          }
          renderSummary();
        }).catch(function () {
          if (btn) btn.disabled = false;
          fb.innerHTML = '<span class="numeric-wrong">' + CHECK_OFFLINE_MSG + '</span>';
        });
        return;
      }

      // Only now count the attempt because a valid number was supplied
      attempts += 1; saveAttempts();
      if (Math.abs(val - answer) <= tol) {
        // Linear scaling across allowed attempts (Option A):
        // earned = round(points * (attemptsAllowed - attemptNumber + 1) / attemptsAllowed)
        // `attempts` was incremented above and represents the current attempt number (1..attemptsAllowed)
        // Mastery-Prinzip: Lösen zählt voll — +1 Bonus für den ersten Versuch
        var earned = Math.round(points) + (attempts === 1 ? 1 : 0);
        if (!isFinite(earned) || earned < 0) earned = 0;
        markDone(qid);
        var prevRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };
        var prev = prevRec.points || 0;
        var didSave = false;
        if (earned > prev) { saveBest(earned); didSave = true; }
        // check if this completed the page (may set page claimed)
        try { checkPageCompletion(); } catch (e) { }
        // Immediately update stars/nav for this page so UI reflects new score without page switch
        try {
          var myPid = getPageId();
          // update visible stars when a submission occurs; do NOT mutate nav icons
          updateStarsForPage(myPid);
        } catch (e) { }
        // schedule a short retry to handle themes that re-render the nav after our change
        try { (function (pid) { setTimeout(function () { try { updateStarsForPage(pid); } catch (e) { } }, 250); })(getPageId()); } catch (e) { }
        fb.innerHTML = '<span class="numeric-correct">' + (earned > points ? 'Volltreffer im ersten Versuch — ' + points + ' Punkte + 1 Bonus!' : 'Richtig — ' + earned + ' Punkte.') + '</span>';
        scoreEl.textContent = 'Punkte: ' + (safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: earned }).points + '/' + points;
        disableControls();
        // Check if all questions are finished and show solution images if so
        try { showSolutionImages(); } catch (e) { }
      } else {
        var s = '<span class="numeric-wrong">Noch nicht richtig (' + attempts + '/' + attemptsAllowed + ').</span>';
        if (hints[attempts - 1]) s += '<div class="numeric-hint">Hinweis: ' + hints[attempts - 1] + '</div>';
        fb.innerHTML = s;
        if (attempts >= attemptsAllowed) {
          scoreEl.textContent = 'Punkte: 0/' + points;
          reveal();
          // Check if all questions are finished and show solution images if so
          try { showSolutionImages(); } catch (e) { }
        } else updateUI();
      }
      renderSummary();
    }

    // clear button removed; no event listener attached
    btn.addEventListener('click', submit);
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') submit(); });

    updateUI();
  }

  // Setup Multiple Choice Question
  function setupMultipleChoiceQuestion(q, index) {
    var normPath = (function () { try { var p = window.location && window.location.pathname ? window.location.pathname : (new URL(window.location.href)).pathname; if (p.indexOf('/index.html') !== -1) p = p.replace(/\/index\.html$/, '/'); if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1); return p; } catch (e) { return (document.location.pathname || document.location.href); } })();
    var fallbackQid = normPath + ':mc' + index;
    var qid = q.dataset.qid || fallbackQid;
    q.dataset.qid = qid;

    var correctAnswers = (q.dataset.correct || '').split(',').map(function (s) { return s.trim(); }).filter(function (s) { return s.length > 0; });
    var points = parseFloat(q.dataset.points || 1) || 1;
    try { localStorage.setItem('answer_max_' + qid, String(points)); } catch (e) { }
    var hints = (q.dataset.hints || '').split('|').map(function (h) { return h.trim(); });

    var attempts = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
    var attemptsAllowed = parseInt(q.dataset.attempts || q.dataset.attemptsAllowed || ATTEMPTS_ALLOWED, 10) || ATTEMPTS_ALLOWED;
    var bestRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };

    // Find or create options container
    var optionsContainer = q.querySelector('.mc-options');
    if (!optionsContainer) {
      optionsContainer = document.createElement('div');
      optionsContainer.className = 'mc-options';
      q.appendChild(optionsContainer);
    }

    // Get all option elements
    var options = optionsContainer.querySelectorAll('.mc-option');

    // Create submit button
    var btn = q.querySelector('.mc-submit');
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'mc-submit';
      btn.textContent = 'Antwort prüfen';
      q.appendChild(btn);
    }

    var fb = q.querySelector('.mc-feedback');
    if (!fb) {
      fb = document.createElement('div');
      fb.className = 'mc-feedback';
      q.appendChild(fb);
    }

    var scoreEl = q.querySelector('.mc-score');
    if (!scoreEl) {
      scoreEl = document.createElement('div');
      scoreEl.className = 'mc-score';
      q.appendChild(scoreEl);
    }

    function saveAttempts() { localStorage.setItem('answer_attempts_' + qid, String(attempts)); emitChanged(); }
    function saveBest(pointsVal) {
      localStorage.setItem('answer_best_' + qid, JSON.stringify({ points: pointsVal, updated: new Date().toISOString() }));
      bestRec = { points: pointsVal, updated: new Date().toISOString() };
      emitChanged();
    }

    function disableControls() {
      if (btn) btn.disabled = true;
      options.forEach(function (opt) {
        var checkbox = opt.querySelector('input[type="checkbox"]');
        if (checkbox) checkbox.disabled = true;
      });
    }

    function enableControls() {
      if (btn) btn.disabled = false;
      options.forEach(function (opt) {
        var checkbox = opt.querySelector('input[type="checkbox"]');
        if (checkbox) checkbox.disabled = false;
      });
    }

    function reveal(sol) {
      if (sol === undefined && correctAnswers.length === 0) sol = cachedSolution(qid);
      if (Array.isArray(sol)) correctAnswers = sol.map(String);
      if (correctAnswers.length === 0) {
        fb.innerHTML += '<div class="mc-reveal">Keine weiteren Versuche.</div>';
        disableControls();
        return;
      }
      fb.innerHTML += '<div class="mc-reveal">Beim nächsten Mal! Richtige Antworten: <strong>' + correctAnswers.join(', ') + '</strong></div>';
      disableControls();
      // Highlight correct answers
      options.forEach(function (opt) {
        var value = opt.dataset.value || '';
        if (correctAnswers.indexOf(value) !== -1) {
          opt.classList.add('mc-correct-answer');
        }
      });
    }

    function updateUI() {
      bestRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };
      attempts = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
      if (bestRec.points > 0) {
        scoreEl.textContent = 'Punkte: ' + bestRec.points + '/' + points;
        fb.innerHTML = '<span class="mc-correct">Richtig — ' + bestRec.points + ' Punkte.</span>';
        disableControls();
        // Highlight the selected answers
        var savedSelection = safeJSONParse(localStorage.getItem('answer_selection_' + qid)) || [];
        options.forEach(function (opt) {
          var checkbox = opt.querySelector('input[type="checkbox"]');
          var value = opt.dataset.value || '';
          if (checkbox && savedSelection.indexOf(value) !== -1) {
            checkbox.checked = true;
          }
        });
      } else if (attempts >= attemptsAllowed) {
        scoreEl.textContent = 'Punkte: 0/' + points;
        reveal();
      } else {
        scoreEl.textContent = 'Versuche: ' + attempts + '/' + attemptsAllowed;
      }
    }

    function submit() {
      if (attempts >= attemptsAllowed) { reveal(); return; }

      // Get selected options
      var selected = [];
      options.forEach(function (opt) {
        var checkbox = opt.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
          selected.push(opt.dataset.value || '');
        }
      });

      // Check if at least one option is selected
      if (selected.length === 0) {
        fb.innerHTML = '<span class="mc-wrong">Bitte mindestens eine Antwort auswählen.</span>';
        return;
      }

      // Server-Modus: data-correct ist im Build entfernt, der Server prüft.
      if (correctAnswers.length === 0) {
        if (btn) btn.disabled = true;
        serverCheck({ qid: qid, selected: selected, attemptsUsed: attempts }).then(function (res) {
          if (btn) btn.disabled = false;
          attempts = res.attempts || (attempts + 1);
          saveAttempts();
          if (res.solution !== undefined) cacheSolution(qid, res.solution);
          if (res.correct || attempts >= (res.attemptsAllowed || attemptsAllowed)) markDone(qid);
          if (res.correct) {
            if (res.authed) {
              var prev = (safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0 }).points || 0;
              if ((res.best || 0) > prev) {
                saveBest(res.best);
                try { localStorage.setItem('answer_selection_' + qid, JSON.stringify(selected)); } catch (e) { }
              }
              fb.innerHTML = '<span class="mc-correct">' + ((res.earned || 0) > points ? 'Volltreffer im ersten Versuch — ' + points + ' Punkte + 1 Bonus!' : 'Richtig — ' + (res.earned || 0) + ' Punkte.') + '</span>';
              scoreEl.textContent = 'Punkte: ' + (res.best || 0) + '/' + points;
              try { checkPageCompletion(); } catch (e) { }
              try { updateStarsForPage(getPageId()); } catch (e) { }
            } else {
              fb.innerHTML = '<span class="mc-correct">Richtig! <small>(Punkte gibt es nur mit ' + opalLoginLink() + '.)</small></span>';
              scoreEl.textContent = '';
            }
            disableControls();
            try { showSolutionImages(); } catch (e) { }
          } else {
            var aa = res.attemptsAllowed || attemptsAllowed;
            var s2 = '<span class="mc-wrong">Noch nicht richtig (' + attempts + '/' + aa + ').</span>';
            if (hints[attempts - 1]) s2 += '<div class="mc-hint">Hinweis: ' + hints[attempts - 1] + '</div>';
            fb.innerHTML = s2;
            if (attempts >= aa) {
              if (res.authed) scoreEl.textContent = 'Punkte: 0/' + points;
              reveal(res.solution);
              try { showSolutionImages(); } catch (e) { }
            } else updateUI();
          }
          renderSummary();
        }).catch(function () {
          if (btn) btn.disabled = false;
          fb.innerHTML = '<span class="mc-wrong">' + CHECK_OFFLINE_MSG + '</span>';
        });
        return;
      }

      // Check if answer is correct (all correct selected, no wrong selected)
      var isCorrect = true;

      // Check if all correct answers are selected
      for (var i = 0; i < correctAnswers.length; i++) {
        if (selected.indexOf(correctAnswers[i]) === -1) {
          isCorrect = false;
          break;
        }
      }

      // Check if any wrong answers are selected
      for (var j = 0; j < selected.length; j++) {
        if (correctAnswers.indexOf(selected[j]) === -1) {
          isCorrect = false;
          break;
        }
      }

      if (isCorrect) {
        // Mastery-Prinzip: Lösen zählt voll — +1 Bonus für den ersten Versuch
        var earned = Math.round(points) + (attempts === 1 ? 1 : 0);
        if (!isFinite(earned) || earned < 0) earned = 0;

        markDone(qid);
        var prevRec = safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: 0, updated: null };
        var prev = prevRec.points || 0;
        if (earned > prev) {
          saveBest(earned);
          // Save the selection for display later
          try { localStorage.setItem('answer_selection_' + qid, JSON.stringify(selected)); } catch (e) { }
        }

        try { checkPageCompletion(); } catch (e) { }
        try {
          var myPid = getPageId();
          updateStarsForPage(myPid);
        } catch (e) { }
        try { (function (pid) { setTimeout(function () { try { updateStarsForPage(pid); } catch (e) { } }, 250); })(getPageId()); } catch (e) { }

        fb.innerHTML = '<span class="mc-correct">' + (earned > points ? 'Volltreffer im ersten Versuch — ' + points + ' Punkte + 1 Bonus!' : 'Richtig — ' + earned + ' Punkte.') + '</span>';
        scoreEl.textContent = 'Punkte: ' + (safeJSONParse(localStorage.getItem('answer_best_' + qid)) || { points: earned }).points + '/' + points;
        disableControls();
        try { showSolutionImages(); } catch (e) { }
      } else {
        var s = '<span class="mc-wrong">Noch nicht richtig (' + attempts + '/' + attemptsAllowed + ').</span>';
        if (hints[attempts - 1]) s += '<div class="mc-hint">Hinweis: ' + hints[attempts - 1] + '</div>';
        fb.innerHTML = s;
        if (attempts >= attemptsAllowed) {
          scoreEl.textContent = 'Punkte: 0/' + points;
          reveal();
          try { showSolutionImages(); } catch (e) { }
        } else updateUI();
      }
      renderSummary();
    }

    btn.addEventListener('click', submit);
    updateUI();
  }

  function onReady(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }

  onReady(function () {
    try { localStorage.removeItem('player_level'); localStorage.removeItem('player_level_seen'); } catch (e) { }
    // remove old entries on load (24h default)
    cleanupOldEntries();
    try { refreshQuestionTotal(); } catch (e) { }
    try { evaluateBadges(false); } catch (e) { }
    // initialize nav icons according to localStorage (claimed vs not)
    try { initializeNavIcons(); } catch (e) { }

    // Setup numeric questions
    var questions = document.querySelectorAll('.numeric-question');
    for (var i = 0; i < questions.length; i++) setupQuestion(questions[i], i);

    // Setup multiple choice questions
    var mcQuestions = document.querySelectorAll('.multiple-choice-question');
    for (var j = 0; j < mcQuestions.length; j++) setupMultipleChoiceQuestion(mcQuestions[j], j);

    // update player badge and nav
    try { updatePlayerBadge(); checkPageCompletion(); } catch (e) { }

    // Check if solution images should be shown (on page load)
    try { showSolutionImages(); } catch (e) { }

    // create reset UI for authors/local testing if allowed
    try { createPerPageResetIfAllowed(); } catch (e) { }
    try { ensureNavObserver(); } catch (e) { }
    try { ensureLevelUpStyles(); } catch (e) { }

    // Global reset removed to prevent easy deletion of local results by students

    renderSummary();
  });

  // local debug tools removed

  // expose a tiny test helper so authors can trigger the level-up animation from the console
  try {
    if (typeof window !== 'undefined') {
      window.__ac_debug_state = function () {
        try {
          var out = { keys: [], pageClaims: [], answerBests: [], qidsOnPage: [] };
          for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); out.keys.push(k); if (k && k.indexOf('page_claimed_') === 0) out.pageClaims.push(k); if (k && k.indexOf('answer_best_') === 0) out.answerBests.push({ key: k, val: safeJSONParse(localStorage.getItem(k)) }); }
          var qs = document.querySelectorAll('.numeric-question'); for (var j = 0; j < qs.length; j++) { out.qidsOnPage.push(qs[j].dataset.qid || null); }
          console.info('answer-checker debug state', out); return out;
        } catch (e) { console.warn('debug state failed', e); return null; }
      };
    }
  } catch (e) { }

})();
