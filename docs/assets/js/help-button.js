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
    '#help-toast.show{opacity:1}' +
    '#help-text{position:fixed;right:1rem;bottom:3.6rem;z-index:61;width:min(22rem,calc(100vw - 2rem));background:#fff;color:#2e3639;' +
    'border:1px solid #e2e8ec;border-radius:.6rem;padding:.6rem .7rem;font-size:.8rem;box-shadow:0 2px 12px rgba(0,0,0,.2)}' +
    '#help-text textarea{width:100%;box-sizing:border-box;min-height:3.6rem;font:inherit;border:1px solid #bec3c6;border-radius:.4rem;padding:.35rem}' +
    '#help-text .ht-zeile{display:flex;justify-content:flex-end;gap:.5rem;margin-top:.4rem}' +
    '#help-text button{border:0;border-radius:1rem;padding:.3rem .8rem;font-weight:600;cursor:pointer;background:#e2e8ec;color:#2e3639}' +
    '#help-text button.ht-senden{background:#009ee3;color:#fff}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'help-fab';
  btn.type = 'button';
  btn.textContent = '🙋 Hand heben';
  btn.title = 'Der Praktikumsleitung Bescheid geben, dass hier Hilfe gebraucht wird';

  var toastEl = document.createElement('div');
  toastEl.id = 'help-toast';

  // Nach dem Melden: Problem kurz beschreiben (freiwillig), damit die Praktikumsleitung abschätzen kann, wie lange es dauert
  var textEl = document.createElement('div');
  textEl.id = 'help-text';
  textEl.hidden = true;
  textEl.innerHTML = '<label for="help-text-in"><strong>Worum geht es?</strong> Freiwillig, ein Satz genügt.</label>' +
    '<textarea id="help-text-in" maxlength="200" placeholder="z. B. ANSYS zeigt eine Fehlermeldung, Temperatur passt nicht, finde die Konvektion nicht"></textarea>' +
    '<div class="ht-zeile"><button type="button" class="ht-zu">Ohne Beschreibung</button><button type="button" class="ht-senden">Senden</button></div>';
  textEl.querySelector('.ht-zu').onclick = function () { textEl.hidden = true; };
  textEl.querySelector('.ht-senden').onclick = function () {
    var text = textEl.querySelector('textarea').value.trim();
    textEl.hidden = true;
    if (!text) return;
    fetch(BACKEND + '/api/help', { method: 'POST', headers: headers(), body: JSON.stringify({ page: window.location.pathname, text: text }) })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (st) { if (st) { apply(st, false); toast('Beschreibung ist angekommen.'); } })
      .catch(function () { });
  };

  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    setTimeout(function () { toastEl.classList.remove('show'); }, 5000);
  }

  var state = { open: false, position: null, enabled: false };
  btn.style.display = 'none'; // erscheint erst, wenn die Lehrveranstaltung ihn freischaltet

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
      btn.textContent = '🙋 Nr. ' + state.position + ' in der Warteschlange, Klick zieht zurück';
    } else {
      btn.classList.remove('active');
      btn.textContent = '🙋 Hand heben';
    }
  }

  function apply(st, fromPoll) {
    if (!st) return;
    var wasOpen = state.open;
    state.open = !!st.open;
    state.position = st.position;
    // Der Button existiert nur während der Lehrveranstaltung
    // (Schalter im Dashboard; ältere Backends ohne Feld gelten als "an")
    state.enabled = st.enabled !== false;
    btn.style.display = state.enabled ? '' : 'none';
    if (!state.open) textEl.hidden = true;
    if (fromPoll && wasOpen && !state.open && state.enabled) {
      toast('Als erledigt markiert: Hilfe ist da oder unterwegs.');
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
        if (!st) { toast('Nicht erreichbar: Dafür ist das HTWK-Netz oder VPN nötig.'); return; }
        var opened = !state.open && st.open;
        apply(st, false);
        if (opened) {
          textEl.querySelector('strong').textContent = 'Gemeldet, Sie sind Nr. ' + st.position + '. Worum geht es?';
          textEl.querySelector('textarea').value = '';
          textEl.hidden = false;
          textEl.querySelector('textarea').focus();
        }
      })
      .catch(function () {
        btn.disabled = false;
        toast('Nicht erreichbar: Dafür ist das HTWK-Netz oder VPN nötig.');
      });
  });

  function init() {
    document.body.appendChild(btn);
    document.body.appendChild(toastEl);
    document.body.appendChild(textEl);
    refresh();
    setInterval(refresh, 20000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
