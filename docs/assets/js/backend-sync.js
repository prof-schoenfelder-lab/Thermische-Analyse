// Optional backend sync for the answer checker.
// Disabled unless window.AC_BACKEND_URL is set (see backend-config.js) AND a
// login token is present (delivered by the LTI launch via #ac_token=... in the
// URL). Without both, the site keeps working purely on localStorage as before.
(function () {
  'use strict';

  var BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
  var TOKEN_KEY = 'ac_backend_token';

  // Capture a token delivered via URL fragment after an LTI launch.
  try {
    var m = (window.location.hash || '').match(/[#&]ac_token=([^&]+)/);
    if (m) {
      localStorage.setItem(TOKEN_KEY, m[1]);
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  } catch (e) { }

  var token = null;
  try { token = localStorage.getItem(TOKEN_KEY); } catch (e) { }
  if (!BACKEND || !token) return;

  // Collect the full local answer state: { qid: { best, attempts, max } }
  function collectResults() {
    var out = {};
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        var qid, rec;
        if (k && k.indexOf('answer_best_') === 0) {
          qid = k.slice('answer_best_'.length);
          try { rec = JSON.parse(localStorage.getItem(k)); } catch (e) { rec = null; }
          out[qid] = out[qid] || {};
          out[qid].best = (rec && typeof rec.points === 'number') ? rec.points : 0;
        } else if (k && k.indexOf('answer_attempts_') === 0) {
          qid = k.slice('answer_attempts_'.length);
          out[qid] = out[qid] || {};
          out[qid].attempts = parseInt(localStorage.getItem(k) || '0', 10) || 0;
        } else if (k && k.indexOf('answer_max_') === 0) {
          qid = k.slice('answer_max_'.length);
          out[qid] = out[qid] || {};
          out[qid].max = parseFloat(localStorage.getItem(k) || '0') || 0;
        }
      }
    } catch (e) { }
    return out;
  }

  // Small "logged in" chip in the Material header, fed by /api/me
  function showBadge(me) {
    try {
      var el = document.getElementById('ac-sync-badge');
      if (!el) {
        var host = document.querySelector('.md-header__inner');
        if (!host) return;
        el = document.createElement('span');
        el.id = 'ac-sync-badge';
        el.style.cssText = 'display:inline-flex;align-items:center;white-space:nowrap;' +
          'margin:0 .4rem;padding:.15rem .6rem;border-radius:1rem;font-size:.65rem;' +
          'background:rgba(255,255,255,.15);color:var(--md-primary-bg-color,#fff);cursor:default;';
        host.appendChild(el);
      }
      el.textContent = '✓ OPAL · ' + (me.total_points || 0) + ' P.';
      el.title = 'Über OPAL angemeldet — Punkte werden gespeichert (' +
        (me.total_points || 0) + ' von ' + (me.max_points || 0) + ' bisher erreichbaren Punkten)';
    } catch (e) { }
  }

  function refreshBadge() {
    fetch(BACKEND + '/api/me', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (me) { if (me) showBadge(me); })
      .catch(function () { });
  }

  // Der lokale Punktestand gehört genau einem OPAL-Account. Meldet sich in
  // diesem Browser jemand anderes an, wird der lokale Stand geleert, damit
  // keine fremden Punkte auf den neuen Account hochgeladen werden.
  function wipeLocalState() {
    try {
      var prefixes = ['answer_', 'page_claimed', 'player_level'];
      var doomed = [];
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k) continue;
        for (var p = 0; p < prefixes.length; p++) {
          if (k.indexOf(prefixes[p]) === 0) { doomed.push(k); break; }
        }
      }
      doomed.forEach(function (k) { localStorage.removeItem(k); });
      sessionStorage.removeItem('ac_merged_reload');
    } catch (e) { }
  }

  function checkOwnerThenSync() {
    fetch(BACKEND + '/api/me', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) {
        if (r.status === 401) {
          try { localStorage.removeItem(TOKEN_KEY); } catch (e) { }
          return null;
        }
        return r.ok ? r.json() : null;
      })
      .then(function (me) {
        if (!me) return;
        // Semester-Reset erkannt? Dann lokalen Altbestand räumen statt ihn
        // wieder auf den Server zu laden.
        try {
          var gen = localStorage.getItem('ac_generation');
          if (me.generation && gen && gen !== me.generation) {
            wipeLocalState();
            localStorage.setItem('ac_generation', me.generation);
            localStorage.setItem('ac_owner', me.pseudonym);
            location.reload();
            return;
          }
          if (me.generation) localStorage.setItem('ac_generation', me.generation);
        } catch (e) { }
        var owner = null;
        try { owner = localStorage.getItem('ac_owner'); } catch (e) { }
        if (owner && owner !== me.pseudonym) {
          wipeLocalState();
          try { localStorage.setItem('ac_owner', me.pseudonym); } catch (e) { }
          location.reload();
          return;
        }
        try { localStorage.setItem('ac_owner', me.pseudonym); } catch (e) { }
        showBadge(me);
        pullAndMerge();
        setTimeout(push, 800);
      })
      .catch(function () { });
  }

  function push() {
    var results = collectResults();
    if (Object.keys(results).length === 0) return;
    fetch(BACKEND + '/api/results', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ results: results })
    }).then(function (r) {
      if (r.status === 401) {
        // token expired/invalid — drop it, site falls back to local-only mode
        try { localStorage.removeItem(TOKEN_KEY); } catch (e) { }
        var el = document.getElementById('ac-sync-badge');
        if (el && el.parentNode) el.parentNode.removeChild(el);
      } else if (r.ok) {
        refreshBadge();
      }
    }).catch(function () { /* offline etc. — retry on next change */ });
  }

  var timer = null;
  document.addEventListener('answer-checker:changed', function () {
    if (timer) clearTimeout(timer);
    timer = setTimeout(push, 1500);
  });

  // Pull server state and merge into localStorage (server best wins if higher),
  // so points follow the login onto any device/browser. Reloads once if the
  // merge changed anything, so the question UI reflects the server state.
  function pullAndMerge() {
    fetch(BACKEND + '/api/results', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.results) return;
        var changed = false;
        Object.keys(data.results).forEach(function (qid) {
          var srv = data.results[qid] || {};
          try {
            var localBest = 0;
            try { localBest = (JSON.parse(localStorage.getItem('answer_best_' + qid)) || {}).points || 0; } catch (e) { }
            if ((srv.best || 0) > localBest) {
              localStorage.setItem('answer_best_' + qid,
                JSON.stringify({ points: srv.best, updated: new Date().toISOString() }));
              changed = true;
            }
            var localAtt = parseInt(localStorage.getItem('answer_attempts_' + qid) || '0', 10) || 0;
            if ((srv.attempts || 0) > localAtt) {
              localStorage.setItem('answer_attempts_' + qid, String(srv.attempts));
              changed = true;
            }
            if (srv.max && !localStorage.getItem('answer_max_' + qid)) {
              localStorage.setItem('answer_max_' + qid, String(srv.max));
              changed = true;
            }
          } catch (e) { }
        });
        if (changed && !sessionStorage.getItem('ac_merged_reload')) {
          sessionStorage.setItem('ac_merged_reload', '1');
          location.reload();
        }
      })
      .catch(function () { });
  }

  // initial sync (covers results collected while logged out or offline) + badge.
  // Erst der Besitzer-Check, dann mergen/pushen — nie fremde Punkte hochladen.
  function init() { checkOwnerThenSync(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
