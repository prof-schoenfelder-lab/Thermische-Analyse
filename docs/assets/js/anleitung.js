// Klick-Anleitungen als "Schritt für Schritt" (ein Schritt, großes Bild, Zurück/Weiter, Pfeiltasten,
// Wischen, Vollbild) oder als kompakte "Liste" (eine Zeile je Schritt, Bild auf Tipp).
// Beide Ansichten teilen die Position je Anleitung (localStorage), die Ansicht gilt auf allen Seiten.
// Übernimmt <tutorial slug="…"> vor tutorials.js (deshalb vorher laden); die Übersichtsseite bleibt bei tutorials.js.
// Kurzanleitungen entfallen auf Seiten mit Klick-Anleitung (Rückfall ohne JavaScript),
// Elemente mit class="anl-bild" (z. B. GIF) werden zu "Ganzer Ablauf als Film".
(function () {
  'use strict';

  var KEY_ANSICHT = 'kurs-anleitung';
  var s = document.currentScript || document.querySelector('script[src*="anleitung.js"]');
  var BASE = new URL((s && s.getAttribute('src')) || '.', document.baseURI).href.replace(/assets\/js\/anleitung\.js.*$/, '');
  var alle = [];

  function lies(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function schreib(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* nur diese Sitzung */ } }
  function ansicht() { var v = lies(KEY_ANSICHT, 'schritt'); return v === 'liste' || v === 'ohne' ? 'liste' : 'schritt'; }

  function esc(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function md(t) {
    return esc(t || '').replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>');
  }
  function h(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  var ICON_BILD = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="10" r="1.8" fill="currentColor"/><path d="M5 17l5-5 3 3 2-2 4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>';

  function Anleitung(wurzel, slug) {
    var self = this, tut = null, bilder = [];
    var KEY_POS = 'kurs-anleitung-pos:' + slug;
    this.wurzel = wurzel;

    var ui = null;  // Elemente der aktuellen Ansicht, damit Blättern nichts neu aufbaut
    function pos() { var p = parseInt(lies(KEY_POS, '0'), 10); return isNaN(p) ? 0 : Math.max(0, Math.min(p, tut.steps.length - 1)); }
    function setzePos(p) { schreib(KEY_POS, String(Math.max(0, Math.min(p, tut.steps.length - 1)))); aktualisieren(); }
    this.weiter = function (d) { if (tut) setzePos(pos() + d); };

    function bildUrl(st) { return st.media && st.media.length ? BASE + 'tutorials/' + slug + '/' + st.media[0] : ''; }
    function veredeln(el) { if (window.KursUI) window.KursUI.enhance(el); }
    function textSetzen(el, st) { el.innerHTML = md(st.caption); veredeln(el); }

    // Neues Bild erst zeigen, wenn es geladen ist: das alte bleibt so lange stehen, nichts springt
    function bildTauschen(img, url) {
      img.dataset.ziel = url;
      if (!url) { img.removeAttribute('src'); return; }
      if (img.getAttribute('src') === url) return;
      var neu = new Image();
      neu.src = url;
      var fertig = function () { if (img.dataset.ziel === url) img.src = url; };
      if (neu.decode) neu.decode().then(fertig, fertig); else neu.onload = neu.onerror = fertig;
    }
    function vorladen(i) { if (bilder[i]) { var v = new Image(); v.src = bilder[i]; } }

    function kopf() {
      var k = h('div', 'kb-kopf');
      k.appendChild(h('div', 'kb-titel', '<span class="kb-kicker">Klick-Anleitung</span><span class="kb-name">' + esc(tut.title) + '</span>'));
      var sw = h('div', 'kb-ansicht');
      sw.setAttribute('role', 'group');
      sw.setAttribute('aria-label', 'Ansicht der Anleitung');
      [['schritt', 'Schritt für Schritt'], ['liste', 'Liste']].forEach(function (a) {
        var b = h('button', '', a[1]);
        b.type = 'button';
        b.setAttribute('aria-pressed', ansicht() === a[0] ? 'true' : 'false');
        b.addEventListener('click', function () { schreib(KEY_ANSICHT, a[0]); alle.forEach(function (x) { x.zeichnen(); }); });
        sw.appendChild(b);
      });
      k.appendChild(sw);
      return k;
    }

    function schritt() {
      var n = tut.steps.length, box = h('div', 'kb-schritt'), segs = [];
      var fort = h('div', 'kb-fort');
      tut.steps.forEach(function (st, j) {
        var seg = h('button', 'kb-seg');
        seg.type = 'button';
        seg.setAttribute('aria-label', 'Schritt ' + (j + 1));
        seg.addEventListener('click', function () { setzePos(j); });
        fort.appendChild(seg);
        segs.push(seg);
      });
      box.appendChild(fort);
      var zaehler = h('div', 'kb-zaehler');
      var text = h('div', 'kb-text tut-cap');
      var fig = h('button', 'kb-bild', '<img alt="">');
      fig.type = 'button';
      fig.setAttribute('aria-label', 'Bild im Vollbild zeigen');
      fig.addEventListener('click', function () { vollbild(); });
      wischen(fig);
      var nav = h('div', 'kb-nav');
      var zur = h('button', 'kb-zurueck', '← Zurück'), vor = h('button', 'kb-weiter');
      zur.type = vor.type = 'button';
      zur.addEventListener('click', function () { self.weiter(-1); });
      vor.addEventListener('click', function () {
        if (pos() < n - 1) { self.weiter(1); return; }
        var nach = wurzel.nextElementSibling;  // fertig: zum Inhalt nach der Anleitung
        if (nach) nach.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      nav.appendChild(zur);
      nav.appendChild(vor);
      [zaehler, text, fig, nav].forEach(function (e) { box.appendChild(e); });
      ui = { typ: 'schritt', segs: segs, zaehler: zaehler, text: text, img: fig.querySelector('img'), fig: fig, zur: zur, vor: vor };
      return box;
    }

    function liste() {
      var lis = [], ol = h('ol', 'kb-liste');
      tut.steps.forEach(function (st, j) {
        var li = h('li');
        var nr = h('button', 'kb-nr', String(j + 1));
        nr.type = 'button';
        nr.title = 'Hier bin ich';
        nr.addEventListener('click', function () { setzePos(j); });
        li.appendChild(nr);
        var text = h('div', 'kb-ltext tut-cap');
        textSetzen(text, st);
        li.appendChild(text);
        var url = bildUrl(st);
        if (url) {
          var b = h('button', 'kb-bildknopf', ICON_BILD);
          b.type = 'button';
          b.setAttribute('aria-label', 'Bild zu Schritt ' + (j + 1));
          b.setAttribute('aria-expanded', 'false');
          b.addEventListener('click', function () {
            var img = li.querySelector('.kb-limg');
            if (img) { img.remove(); b.setAttribute('aria-expanded', 'false'); return; }
            img = h('button', 'kb-limg', '<img alt="" src="' + url + '">');
            img.type = 'button';
            img.addEventListener('click', function () { setzePos(j); vollbild(); });
            li.appendChild(img);
            b.setAttribute('aria-expanded', 'true');
          });
          li.appendChild(b);
        }
        ol.appendChild(li);
        lis.push(li);
      });
      ui = { typ: 'liste', lis: lis };
      return ol;
    }

    // Nach jedem Blättern nur Inhalte austauschen, nicht neu aufbauen
    function aktualisieren() {
      if (!ui) return;
      var i = pos(), n = tut.steps.length, st = tut.steps[i];
      if (ui.typ === 'liste') {
        ui.lis.forEach(function (li, j) { li.className = j < i ? 'fertig' : j === i ? 'jetzt' : ''; });
      } else {
        ui.segs.forEach(function (seg, j) { seg.className = 'kb-seg' + (j < i ? ' fertig' : j === i ? ' jetzt' : ''); });
        ui.zaehler.innerHTML = 'Schritt <b>' + (i + 1) + '</b> von ' + n;
        textSetzen(ui.text, st);
        bildTauschen(ui.img, bildUrl(st));
        ui.fig.style.visibility = bildUrl(st) ? '' : 'hidden';
        ui.zur.disabled = i === 0;
        ui.vor.textContent = i === n - 1 ? 'Fertig ✓' : 'Weiter →';
        vorladen(i + 1);
      }
      if (vb) vb();
    }

    // Vollbild: Bild so groß wie möglich, Text und Blättern bleiben
    var vb = null;  // Aktualisierung des offenen Vollbilds
    function vollbild() {
      var ov = h('div', 'kb-vollbild');
      ov.setAttribute('role', 'dialog');
      ov.setAttribute('aria-modal', 'true');
      var oben = h('div', 'kb-vb-oben'), zaehler = h('div', 'kb-zaehler');
      var zu = h('button', 'kb-vb-zu', 'Schließen ✕'); zu.type = 'button';
      oben.appendChild(zaehler); oben.appendChild(zu);
      var t = h('div', 'kb-text tut-cap');
      var b = h('div', 'kb-vb-bild', '<img alt="">'), img = b.querySelector('img');
      wischen(b);
      var nav = h('div', 'kb-nav');
      var z = h('button', 'kb-zurueck', '← Zurück'), w = h('button', 'kb-weiter', 'Weiter →');
      z.type = w.type = 'button';
      z.addEventListener('click', function () { self.weiter(-1); });
      w.addEventListener('click', function () { self.weiter(1); });
      nav.appendChild(z); nav.appendChild(w);
      [oben, t, b, nav].forEach(function (e) { ov.appendChild(e); });
      vb = function () {
        var i = pos(), st = tut.steps[i];
        zaehler.innerHTML = 'Schritt <b>' + (i + 1) + '</b> von ' + tut.steps.length;
        textSetzen(t, st);
        bildTauschen(img, bildUrl(st));
        z.disabled = i === 0;
        w.disabled = i === tut.steps.length - 1;
      };
      function taste(ev) {
        if (ev.key === 'Escape') schliessen();
        else if (ev.key === 'ArrowRight') self.weiter(1);
        else if (ev.key === 'ArrowLeft') self.weiter(-1);
        else return;
        ev.preventDefault(); ev.stopPropagation();
      }
      function schliessen() { vb = null; document.removeEventListener('keydown', taste, true); ov.remove(); document.body.classList.remove('kb-offen'); }
      zu.addEventListener('click', schliessen);
      document.addEventListener('keydown', taste, true);
      document.body.classList.add('kb-offen');
      document.body.appendChild(ov);
      vb();
    }

    function wischen(el) {
      var x0 = null;
      el.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      el.addEventListener('touchend', function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0; x0 = null;
        if (Math.abs(dx) > 50) self.weiter(dx < 0 ? 1 : -1);
      });
    }

    function zeichnen() {
      if (!tut) return;
      var a = ansicht();
      wurzel.className = 'kb kb-modus-' + a;
      wurzel.innerHTML = '';
      wurzel.appendChild(kopf());
      wurzel.appendChild(a === 'schritt' ? schritt() : liste());
      aktualisieren();
    }
    this.zeichnen = zeichnen;

    wurzel.className = 'kb';
    wurzel.innerHTML = '<div class="kb-kopf"><div class="kb-titel"><span class="kb-kicker">Klick-Anleitung</span><span class="kb-name">wird geladen …</span></div></div>';
    fetch(BASE + 'tutorials/' + slug + '/tutorial.json').then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (j) {
      tut = j;
      bilder = tut.steps.map(bildUrl);
      zeichnen();
    }).catch(function () {
      wurzel.querySelector('.kb-name').textContent = 'Anleitung „' + slug + '“ nicht gefunden';
    });
  }

  // Pfeiltasten blättern in der Anleitung, die gerade am meisten im Bild ist
  function sichtbarste() {
    var best = null, beste = 0;
    alle.forEach(function (a) {
      if (!a.wurzel.classList.contains('kb-modus-schritt')) return;
      var r = a.wurzel.getBoundingClientRect();
      var sicht = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
      if (sicht > beste) { beste = sicht; best = a; }
    });
    return beste > 120 ? best : null;
  }
  document.addEventListener('keydown', function (ev) {
    if (document.body.classList.contains('kb-offen') || ev.altKey || ev.ctrlKey || ev.metaKey) return;
    if (/^(INPUT|TEXTAREA|SELECT)$/.test((ev.target && ev.target.tagName) || '')) return;
    var a = (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft') && sichtbarste();
    if (a) { a.weiter(ev.key === 'ArrowRight' ? 1 : -1); ev.preventDefault(); }
  });

  function init() {
    var inhalt = document.querySelector('.md-content article') || document.body;
    var tags = inhalt.querySelectorAll('tutorial[slug]');
    if (!tags.length) return;
    Array.prototype.forEach.call(tags, function (t) {
      var div = document.createElement('div');
      t.replaceWith(div);
      alle.push(new Anleitung(div, t.getAttribute('slug')));
    });
    Array.prototype.forEach.call(inhalt.querySelectorAll('details, .admonition'), function (d) {
      var t = d.querySelector('summary, .admonition-title');
      if (t && /^\s*Kurzanleitung/.test(t.textContent)) d.classList.add('kb-doppelt');
    });
    Array.prototype.forEach.call(inhalt.querySelectorAll('.anl-bild'), function (f) {
      var d = document.createElement('details');
      d.className = 'kb-film';
      d.innerHTML = '<summary>Ganzer Ablauf als Film</summary>';
      f.replaceWith(d);
      d.appendChild(f);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
