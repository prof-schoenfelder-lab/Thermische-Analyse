// Tutorial-Datenbank: eine Quelle (docs/tutorials/), drei Oberflächen —
//  1) Einbetten:  <tutorial slug="festlager-anbringen"></tutorial>
//  2) Übersicht:  <div id="tut-overview"></div> (durchsuchbar, nach Kategorie)
//  3) Hilfe:      dieselbe Anleitung, überall referenzierbar
// Rein statisch: Daten liegen als JSON im Repo, hier nur gerendert.
(function () {
  'use strict';

  // Basis-URL der Site aus dem eigenen <script src> ableiten (funktioniert in
  // beiden Kursen, egal ob /Strukturmechanik/ oder /Thermische-Analyse/).
  function baseURL() {
    var s = document.currentScript ||
      document.querySelector('script[src*="tutorials.js"]');
    var src = s ? s.getAttribute('src') : '';
    var abs = new URL(src || '.', document.baseURI).href;
    return abs.replace(/assets\/js\/tutorials\.js.*$/, '');
  }
  var BASE = baseURL();
  var CACHE = {};

  function fetchJSON(url) {
    if (CACHE[url]) return CACHE[url];
    CACHE[url] = fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + ' → ' + r.status);
      return r.json();
    });
    return CACHE[url];
  }

  // Minimales Inline-Markdown für Beschreibungen: `code`, **fett**, *kursiv*.
  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function mdInline(s) {
    var out = esc(s || '');
    out = out.replace(/`([^`]+)`/g, function (_, c) { return '<code>' + c + '</code>'; });
    out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    return out;
  }

  // Medium eines Schritts (ein Bild = statisch, mehrere = bereits als .gif
  // vorbereitet; die Datenbank speichert dann eine einzelne .gif-Datei).
  function mediaNode(slug, media) {
    if (!media || !media.length) return null;
    var img = document.createElement('img');
    img.className = 'tut-img no-lightbox';
    img.loading = 'lazy';
    img.alt = '';
    img.src = BASE + 'tutorials/' + slug + '/' + media[0];
    return img;
  }

  // Eine Anleitung als Schritt-Block (gleiche Optik wie die Kurzanleitungen).
  function buildSteps(tut) {
    var wrap = document.createElement('div');
    wrap.className = 'tut-body';
    var ol = document.createElement('ol');
    ol.className = 'tut-steps';
    tut.steps.forEach(function (st) {
      var li = document.createElement('li');
      var cap = document.createElement('div');
      cap.className = 'tut-cap';
      cap.innerHTML = mdInline(st.caption);
      li.appendChild(cap);
      if (st.note) {
        var note = document.createElement('div');
        note.className = 'tut-note';
        note.innerHTML = mdInline(st.note);
        li.appendChild(note);
      }
      var m = mediaNode(tut.slug, st.media);
      if (m) li.appendChild(m);
      ol.appendChild(li);
    });
    wrap.appendChild(ol);
    if (window.KursUI) window.KursUI.enhance(wrap);
    return wrap;
  }

  function metaLine(tut) {
    var meta = document.createElement('div');
    meta.className = 'tut-meta';
    meta.innerHTML =
      '<span class="tut-cat">' + esc(tut.category || '') + '</span>' +
      (tut.software ? '<span class="tut-soft">' + esc(tut.software) + '</span>' : '') +
      '<span class="tut-count">' + tut.steps.length + ' Schritte</span>';
    return meta;
  }

  // --- 1) Embeds ------------------------------------------------------------
  function renderEmbeds(root) {
    var nodes = root.querySelectorAll('tutorial[slug], .tutorial[data-slug]');
    Array.prototype.forEach.call(nodes, function (el) {
      var slug = el.getAttribute('slug') || el.getAttribute('data-slug');
      var open = el.hasAttribute('open') || el.getAttribute('data-open') === 'true';
      var det = document.createElement('details');
      det.className = 'tut tut-embed admonition';
      if (open) det.open = true;
      var sum = document.createElement('summary');
      sum.innerHTML = '<span class="tut-kicker">Klick-Anleitung</span> ' +
        '<span class="tut-title-txt">…</span>';
      det.appendChild(sum);
      el.replaceWith(det);
      fetchJSON(BASE + 'tutorials/' + slug + '/tutorial.json').then(function (tut) {
        sum.querySelector('.tut-title-txt').textContent = tut.title;
        det.appendChild(metaLine(tut));
        det.appendChild(buildSteps(tut));
      }).catch(function () {
        sum.querySelector('.tut-title-txt').textContent = 'Anleitung „' + slug + '" nicht gefunden';
      });
    });
  }

  // --- 2) Übersichtsseite ---------------------------------------------------
  function renderOverview(host) {
    fetchJSON(BASE + 'tutorials/index.json').then(function (db) {
      var all = db.tutorials || [];
      var cats = [];
      all.forEach(function (t) { if (cats.indexOf(t.category) === -1) cats.push(t.category); });

      var bar = document.createElement('div');
      bar.className = 'tut-bar';
      var search = document.createElement('input');
      search.type = 'search';
      search.className = 'tut-search';
      search.placeholder = 'Anleitung suchen … (z.B. Festlager, Netz, Material)';
      bar.appendChild(search);
      var chips = document.createElement('div');
      chips.className = 'tut-cats';
      var active = '';
      function mkChip(label, val) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'tut-chip' + (val === active ? ' active' : '');
        b.textContent = label;
        b.addEventListener('click', function () {
          active = val; draw();
          chips.querySelectorAll('.tut-chip').forEach(function (c) { c.classList.remove('active'); });
          b.classList.add('active');
        });
        return b;
      }
      chips.appendChild(mkChip('Alle', ''));
      cats.forEach(function (c) { chips.appendChild(mkChip(c, c)); });
      bar.appendChild(chips);
      host.appendChild(bar);

      var grid = document.createElement('div');
      grid.className = 'tut-grid';
      host.appendChild(grid);

      var detail = document.createElement('div');
      detail.className = 'tut-detail';
      detail.hidden = true;
      host.appendChild(detail);

      function openDetail(slug) {
        fetchJSON(BASE + 'tutorials/' + slug + '/tutorial.json').then(function (tut) {
          detail.innerHTML = '';
          var back = document.createElement('button');
          back.type = 'button';
          back.className = 'tut-back';
          back.textContent = '← Alle Anleitungen';
          back.addEventListener('click', function () {
            detail.hidden = true; bar.hidden = false; grid.hidden = false;
            history.replaceState(null, '', location.pathname + location.search);
          });
          var h = document.createElement('h2');
          h.className = 'tut-detail-title';
          h.textContent = tut.title;
          detail.appendChild(back);
          detail.appendChild(h);
          detail.appendChild(metaLine(tut));
          detail.appendChild(buildSteps(tut));
          bar.hidden = true; grid.hidden = true; detail.hidden = false;
          window.scrollTo(0, 0);
        });
      }

      function draw() {
        var q = search.value.trim().toLowerCase();
        grid.innerHTML = '';
        var shown = 0;
        all.forEach(function (t) {
          if (active && t.category !== active) return;
          var hay = (t.title + ' ' + t.category + ' ' + (t.tags || []).join(' ')).toLowerCase();
          if (q && hay.indexOf(q) === -1) return;
          shown++;
          var card = document.createElement('a');
          card.className = 'tut-card';
          card.href = '#' + t.slug;
          card.addEventListener('click', function (e) { e.preventDefault(); openDetail(t.slug); });
          if (t.thumb) {
            var img = document.createElement('img');
            img.className = 'tut-thumb no-lightbox';
            img.loading = 'lazy'; img.alt = '';
            img.src = BASE + 'tutorials/' + t.slug + '/' + t.thumb;
            card.appendChild(img);
          }
          var b = document.createElement('span');
          b.className = 'tut-card-body';
          b.innerHTML = '<span class="tut-card-title">' + esc(t.title) + '</span>' +
            '<span class="tut-card-meta"><span class="tut-cat">' + esc(t.category) + '</span>' +
            '<span class="tut-count">' + t.steps + ' Schritte</span></span>';
          card.appendChild(b);
          grid.appendChild(card);
        });
        if (!shown) {
          var empty = document.createElement('p');
          empty.className = 'tut-empty';
          empty.textContent = 'Keine Anleitung gefunden.';
          grid.appendChild(empty);
        }
      }
      search.addEventListener('input', draw);
      draw();

      // Direktlink /tutorials/#slug öffnet gleich die Anleitung
      var hash = (location.hash || '').replace('#', '');
      if (hash) openDetail(hash);
    }).catch(function () {
      host.innerHTML = '<p class="tut-empty">Tutorial-Datenbank konnte nicht geladen werden.</p>';
    });
  }

  function init() {
    var root = document.querySelector('.md-content') || document.body;
    try { renderEmbeds(root); } catch (e) { }
    var host = document.getElementById('tut-overview');
    if (host) { try { renderOverview(host); } catch (e) { } }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
