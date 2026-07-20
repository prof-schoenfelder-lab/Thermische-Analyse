// Anonyme Kurs-Statistik unter jeder Übungsfrage:
// "73 % des Kurses haben diese Aufgabe gelöst · ø 2,1 Versuche".
// Nutzt den öffentlichen /api/stats-Endpunkt — funktioniert auch ohne Login.
// Wird erst ab MIN_N Teilnehmenden angezeigt (Rausch-/Datenschutz-Schwelle).
(function () {
  'use strict';

  var BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
  if (!BACKEND) return;
  var MIN_N = 5;

  function annotate(stats) {
    var byQid = {};
    stats.forEach(function (row) { byQid[row.qid] = row; });
    var questions = document.querySelectorAll('.numeric-question, .multiple-choice-question');
    questions.forEach(function (q) {
      var row = byQid[q.dataset.qid];
      if (!row || !row.participants || row.participants < MIN_N) return;
      if (q.querySelector('.course-stat')) return;
      var pct = Math.round(100 * (row.solved || 0) / row.participants);
      var tries = row.avg_attempts ? (Math.round(row.avg_attempts * 10) / 10).toLocaleString('de-DE') : null;
      var el = document.createElement('div');
      el.className = 'course-stat';
      el.textContent = pct + ' % des Kurses haben diese Aufgabe gelöst' +
        (tries ? ' · ø ' + tries + ' Versuche' : '');
      q.appendChild(el);
    });
  }

  function init() {
    if (!document.querySelector('.numeric-question, .multiple-choice-question')) return;
    fetch(BACKEND + '/api/stats')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (stats) { if (Array.isArray(stats)) annotate(stats); })
      .catch(function () { });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
