// Schwebender "Hilfe"-Button: meldet Hilfebedarf ans Backend (Mini-Ticket).
// Reihenfolge der Meldungen sieht die Praktikumsleitung im Dashboard.
// Funktioniert eingeloggt (Pseudonym) und als Gast (per Pool-IP = Sitzplatz);
// ohne konfiguriertes Backend erscheint der Button gar nicht.
(function () {
  'use strict';

  var BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
  if (!BACKEND || !window.fetch) return;

  var css = document.createElement('style');
  css.textContent =
    '#help-fab{position:fixed;right:1rem;bottom:1rem;z-index:60;border:0;cursor:pointer;' +
    'border-radius:2rem;padding:.55rem .95rem;font-size:.8rem;font-weight:600;' +
    'background:#3f51b5;color:#fff;box-shadow:0 2px 10px rgba(0,0,0,.25)}' +
    '#help-fab.active{background:#e65100}' +
    '#help-fab:disabled{opacity:.6;cursor:wait}' +
    '#help-toast{position:fixed;right:1rem;bottom:3.6rem;z-index:60;background:#2e7d32;' +
    'color:#fff;border-radius:.5rem;padding:.5rem .8rem;font-size:.8rem;' +
    'box-shadow:0 2px 10px rgba(0,0,0,.25);opacity:0;transition:opacity .3s}' +
    '#help-toast.show{opacity:1}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'help-fab';
  btn.type = 'button';
  btn.textContent = '🙋 Hilfe';
  btn.title = 'Der Praktikumsleitung Bescheid geben, dass hier Hilfe gebraucht wird';

  var toastEl = document.createElement('div');
  toastEl.id = 'help-toast';

  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    setTimeout(function () { toastEl.classList.remove('show'); }, 5000);
  }

  var state = { open: false, position: null };

  function headers() {
    var h = { 'Content-Type': 'application/json' };
    try {
      var t = localStorage.getItem('ac_backend_token');
      if (t) h['Authorization'] = 'Bearer ' + t;
    } catch (e) { }
    return h;
  }

  function render() {
    if (state.open) {
      btn.classList.add('active');
      btn.textContent = '🙋 Nr. ' + state.position + ' in der Warteschlange — Klick zieht zurück';
    } else {
      btn.classList.remove('active');
      btn.textContent = '🙋 Hilfe';
    }
  }

  function apply(st, fromPoll) {
    if (!st) return;
    var wasOpen = state.open;
    state.open = !!st.open;
    state.position = st.position;
    if (fromPoll && wasOpen && !state.open) {
      toast('Als erledigt markiert — Hilfe ist da oder unterwegs!');
    }
    render();
  }

  function refresh() {
    fetch(BACKEND + '/api/help', { headers: headers() })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (st) { apply(st, true); })
      .catch(function () { });
  }

  btn.addEventListener('click', function () {
    btn.disabled = true;
    var body = state.open ? { cancel: true } : { page: window.location.pathname };
    fetch(BACKEND + '/api/help', { method: 'POST', headers: headers(), body: JSON.stringify(body) })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (st) {
        btn.disabled = false;
        if (!st) { toast('Nicht erreichbar — dafür ist das HTWK-Netz/VPN nötig.'); return; }
        var opened = !state.open && st.open;
        apply(st, false);
        if (opened) toast('Gemeldet! Du bist Nr. ' + st.position + ' — wir kommen der Reihe nach.');
      })
      .catch(function () {
        btn.disabled = false;
        toast('Nicht erreichbar — dafür ist das HTWK-Netz/VPN nötig.');
      });
  });

  function init() {
    document.body.appendChild(btn);
    document.body.appendChild(toastEl);
    refresh();
    setInterval(refresh, 20000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
