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

    function pos() { var p = parseInt(lies(KEY_POS, '0'), 10); return isNaN(p) ? 0 : Math.max(0, Math.min(p, tut.steps.length - 1)); }
    function setzePos(p) { schreib(KEY_POS, String(Math.max(0, Math.min(p, tut.steps.length - 1)))); zeichnen(); }
    this.weiter = function (d) { if (tut) setzePos(pos() + d); };

    function bildUrl(st) { return st.media && st.media.length ? BASE + 'tutorials/' + slug + '/' + st.media[0] : ''; }
    function veredeln(el) { if (window.KursUI) window.KursUI.enhance(el); }

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
      var i = pos(), st = tut.steps[i], n = tut.steps.length, box = h('div', 'kb-schritt');
      var fort = h('div', 'kb-fort');
      for (var j = 0; j < n; j++) {
        (function (j) {
          var seg = h('button', 'kb-seg' + (j < i ? ' fertig' : j === i ? ' jetzt' : ''));
          seg.type = 'button';
          seg.setAttribute('aria-label', 'Schritt ' + (j + 1));
          seg.addEventListener('click', function () { setzePos(j); });
          fort.appendChild(seg);
        })(j);
      }
      box.appendChild(fort);
      box.appendChild(h('div', 'kb-zaehler', 'Schritt <b>' + (i + 1) + '</b> von ' + n));
      var text = h('div', 'kb-text tut-cap', md(st.caption));
      box.appendChild(text);
      var url = bildUrl(st);
      if (url) {
        var fig = h('button', 'kb-bild');
        fig.type = 'button';
        fig.setAttribute('aria-label', 'Bild im Vollbild zeigen');
        fig.innerHTML = '<img alt="" src="' + url + '">';
        fig.addEventListener('click', function () { vollbild(); });
        wischen(fig);
        box.appendChild(fig);
      }
      var nav = h('div', 'kb-nav');
      var zur = h('button', 'kb-zurueck', '← Zurück'), vor = h('button', 'kb-weiter', i === n - 1 ? 'Fertig ✓' : 'Weiter →');
      zur.type = vor.type = 'button';
      zur.disabled = i === 0;
      zur.addEventListener('click', function () { self.weiter(-1); });
      vor.addEventListener('click', function () {
        if (i < n - 1) { self.weiter(1); return; }
        var nach = wurzel.nextElementSibling;  // fertig: zum Inhalt nach der Anleitung
        if (nach) nach.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      nav.appendChild(zur);
      nav.appendChild(vor);
      box.appendChild(nav);
      if (bilder[i + 1]) { var vorab = new Image(); vorab.src = bilder[i + 1]; }
      veredeln(text);
      return box;
    }

    function liste() {
      var i = pos(), ol = h('ol', 'kb-liste');
      tut.steps.forEach(function (st, j) {
        var li = h('li', j < i ? 'fertig' : j === i ? 'jetzt' : '');
        var nr = h('button', 'kb-nr', String(j + 1));
        nr.type = 'button';
        nr.title = 'Hier bin ich';
        nr.addEventListener('click', function () { setzePos(j); });
        li.appendChild(nr);
        var text = h('div', 'kb-ltext tut-cap', md(st.caption));
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
        veredeln(text);
      });
      return ol;
    }

    // Vollbild: Bild so groß wie möglich, Text und Blättern bleiben
    function vollbild() {
      var ov = h('div', 'kb-vollbild');
      ov.setAttribute('role', 'dialog');
      ov.setAttribute('aria-modal', 'true');
      function fuellen() {
        var i = pos(), st = tut.steps[i];
        ov.innerHTML = '';
        var oben = h('div', 'kb-vb-oben');
        oben.appendChild(h('div', 'kb-zaehler', 'Schritt <b>' + (i + 1) + '</b> von ' + tut.steps.length));
        var zu = h('button', 'kb-vb-zu', 'Schließen ✕'); zu.type = 'button';
        zu.addEventListener('click', schliessen);
        oben.appendChild(zu);
        ov.appendChild(oben);
        var t = h('div', 'kb-text tut-cap', md(st.caption));
        ov.appendChild(t);
        var b = h('div', 'kb-vb-bild', bildUrl(st) ? '<img alt="" src="' + bildUrl(st) + '">' : '');
        wischen(b, fuellen);
        ov.appendChild(b);
        var nav = h('div', 'kb-nav');
        var z = h('button', 'kb-zurueck', '← Zurück'), w = h('button', 'kb-weiter', 'Weiter →');
        z.type = w.type = 'button';
        z.disabled = i === 0;
        w.disabled = i === tut.steps.length - 1;
        z.addEventListener('click', function () { self.weiter(-1); fuellen(); });
        w.addEventListener('click', function () { self.weiter(1); fuellen(); });
        nav.appendChild(z); nav.appendChild(w);
        ov.appendChild(nav);
        veredeln(t);
      }
      function taste(ev) {
        if (ev.key === 'Escape') schliessen();
        else if (ev.key === 'ArrowRight') { self.weiter(1); fuellen(); }
        else if (ev.key === 'ArrowLeft') { self.weiter(-1); fuellen(); }
        else return;
        ev.preventDefault(); ev.stopPropagation();
      }
      function schliessen() { document.removeEventListener('keydown', taste, true); ov.remove(); document.body.classList.remove('kb-offen'); }
      document.addEventListener('keydown', taste, true);
      document.body.classList.add('kb-offen');
      document.body.appendChild(ov);
      fuellen();
    }

    function wischen(el, danach) {
      var x0 = null;
      el.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      el.addEventListener('touchend', function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0; x0 = null;
        if (Math.abs(dx) > 50) { self.weiter(dx < 0 ? 1 : -1); if (danach) danach(); }
      });
    }

    function zeichnen() {
      if (!tut) return;
      var a = ansicht();
      wurzel.className = 'kb kb-modus-' + a;
      wurzel.innerHTML = '';
      wurzel.appendChild(kopf());
      wurzel.appendChild(a === 'schritt' ? schritt() : liste());
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
