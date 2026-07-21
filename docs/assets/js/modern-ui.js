// Moderne Lehr-UI, rein progressiv über dem bestehenden Markdown:
// 1) Menüpfad-Chips:  `Environment → Temperature` (Inline-Code mit Pfeilen)
//    wird zu klickpfad-artigen Chips.
// 2) Workflow-Stepper: Absätze wie **4. Vernetzung (Mechanical)** werden zum
//    7-Schritte-Stepper (der rote Faden jeder FEM-Simulation).
// 3) Mitmach-Modus: Kurzanleitungen (Details-Blöcke mit nummerierten
//    Schritten) bekommen einen "Schritt für Schritt"-Modus im Overlay —
//    ein Schritt pro Ansicht, Pfeiltasten, Fortschrittsbalken.
(function () {
  'use strict';

  var WF_STEPS = [
    ['materialdefinition', 'Material'],
    ['geometrieerstellung', 'Geometrie'],
    ['materialzuweisung', 'Zuweisung'],
    ['vernetzung', 'Netz'],
    ['randbedingungen', 'Randbed.'],
    ['lösungseinstellungen', 'Lösen'],
    ['lösungsdarstellung', 'Auswertung']
  ];

  // --- 1) Menüpfad-Chips ----------------------------------------------------
  // Wiederkehrende ANSYS-Orte bekommen ein Erkennungs-Icon im Chip:
  // Reiter, Strukturbaum, Detailfenster, Rechtsklick, Grafikfenster.
  var MP_ICONS = {
    reiter: '<svg viewBox="0 0 24 24"><path d="M3 7h6l2-2.5h10V19H3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    baum: '<svg viewBox="0 0 24 24"><path d="M6 4v13a2 2 0 0 0 2 2h4M6 9h6M10 14h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="6" cy="4" r="2" fill="currentColor"/></svg>',
    detail: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 4v16" stroke="currentColor" stroke-width="2"/><path d="M12 9h6M12 13h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    maus: '<svg viewBox="0 0 24 24"><rect x="7" y="3" width="10" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3v6" stroke="currentColor" stroke-width="2"/><path d="M12 3h5a5 5 0 0 1 0 6h-5z" fill="currentColor"/></svg>',
    mausL: '<svg viewBox="0 0 24 24"><rect x="7" y="3" width="10" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3v6" stroke="currentColor" stroke-width="2"/><path d="M12 3H7a5 5 0 0 0 0 6h5z" fill="currentColor"/></svg>',
    mausD: '<svg viewBox="0 0 24 24"><rect x="8" y="4" width="10" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M13 4v6" stroke="currentColor" stroke-width="2"/><path d="M13 4H8a5 5 0 0 0 0 6h5z" fill="currentColor"/><path d="M5.2 5.8A5.5 5.5 0 0 1 6.9 2.9M2.5 4.6A8.6 8.6 0 0 1 5 1.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    grafik: '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 21h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M5 14l4-4 3 3 4-5 3 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'
  };

  function mpKind(text) {
    var t = text.toLowerCase();
    if (t.indexOf('rechtsklick') === 0) return 'maus';
    if (t.indexOf('doppelklick') === 0) return 'mausD';
    if (t.indexOf('linksklick') === 0) return 'mausL';
    if (t.indexOf('reiter') === 0 || t.indexOf('tab ') === 0) return 'reiter';
    if (t.indexOf('strukturbaum') !== -1) return 'baum';
    if (t.indexOf('detailfenster') !== -1) return 'detail';
    if (t.indexOf('grafikfenster') !== -1) return 'grafik';
    return null;
  }

  // Einzelbegriffe ohne Pfeil, die trotzdem als Ort-Chip erscheinen sollen
  var MP_SOLO = /^(Reiter |Rechtsklick|Doppelklick|Linksklick|Strukturbaum|Detailfenster|Grafikfenster)/;

  function menuPathChips(root) {
    var codes = root.querySelectorAll('p > code, li > code, td > code, summary > code');
    for (var i = 0; i < codes.length; i++) {
      var c = codes[i];
      var t = c.textContent;
      if (c.closest('pre')) continue;
      if (t.indexOf('→') === -1 && !MP_SOLO.test(t)) continue;
      var parts = t.split('→');
      var span = document.createElement('span');
      span.className = 'menu-path';
      for (var p = 0; p < parts.length; p++) {
        if (p > 0) {
          var ar = document.createElement('span');
          ar.className = 'mp-arrow';
          ar.textContent = '→';
          span.appendChild(ar);
        }
        var label = parts[p].trim();
        // "Rechtsklick X": Aktion und Ziel als getrennte Chips —
        // [🖱 Rechtsklick] [X]; eigenes Icon je Klick-Art
        var m = label.match(/^(Rechtsklick|Doppelklick|Linksklick)\s+(.+)$/);
        if (m) {
          var actIcon = m[1] === 'Rechtsklick' ? 'maus' :
                        m[1] === 'Doppelklick' ? 'mausD' : 'mausL';
          var act = document.createElement('span');
          act.className = 'mp-seg mp-action';
          act.innerHTML = '<i class="mp-ic">' + MP_ICONS[actIcon] + '</i>';
          act.appendChild(document.createTextNode(m[1]));
          span.appendChild(act);
          label = m[2];
        }
        var seg = document.createElement('span');
        seg.className = 'mp-seg';
        var kind = mpKind(label);
        if (kind) {
          seg.classList.add('mp-' + kind);
          seg.innerHTML = '<i class="mp-ic">' + MP_ICONS[kind] + '</i>';
          seg.appendChild(document.createTextNode(label));
        } else {
          seg.textContent = label;
        }
        span.appendChild(seg);
      }
      c.parentNode.replaceChild(span, c);
    }
  }

  // --- 2) Workflow-Stepper --------------------------------------------------
  function stepIndexFor(title) {
    var t = title.toLowerCase();
    for (var i = 0; i < WF_STEPS.length; i++) {
      if (t.indexOf(WF_STEPS[i][0]) !== -1) return i;
    }
    return -1;
  }

  function workflowStepper(root) {
    var strongs = root.querySelectorAll('p > strong');
    for (var i = 0; i < strongs.length; i++) {
      var st = strongs[i];
      var p = st.parentNode;
      if (p.textContent.trim() !== st.textContent.trim()) continue;
      // "4. Vernetzung (Mechanical)" — auch Varianten wie 4'. / 6''. / 5*.
      var m = st.textContent.trim().match(/^(\d)[.'*′]*\.?\s+(.+?)(?:\s*\(([^)]+)\))?$/);
      if (!m) continue;
      var idx = stepIndexFor(m[2]);
      if (idx === -1) continue;

      var head = document.createElement('div');
      head.className = 'wf-head';
      var track = '<div class="wf-track">';
      for (var d = 0; d < WF_STEPS.length; d++) {
        track += '<span class="wf-dot' + (d < idx ? ' done' : d === idx ? ' active' : '') +
          '" title="' + (d + 1) + ' · ' + WF_STEPS[d][1] + '"></span>';
      }
      track += '</div>';
      head.innerHTML = track +
        '<div class="wf-title"><span class="wf-num">' + (idx + 1) + '</span>' +
        '<span>' + st.textContent.trim().replace(/^\d[.'*′]*\.?\s+/, '') + '</span>' +
        '</div>' +
        '<div class="wf-label">Schritt ' + (idx + 1) + ' von 7 im Simulations-Workflow</div>';
      p.parentNode.replaceChild(head, p);
    }
  }

  // --- 3) Mitmach-Modus -----------------------------------------------------
  var faState = { steps: [], i: 0, title: '' };
  var overlay = null;

  function faRender() {
    var body = document.getElementById('fa-body');
    var count = document.getElementById('fa-count');
    var bar = document.getElementById('fa-progress').firstChild;
    var prev = document.getElementById('fa-prev');
    var next = document.getElementById('fa-next');
    body.innerHTML = faState.steps[faState.i];
    body.scrollTop = 0;
    count.textContent = 'Schritt ' + (faState.i + 1) + ' / ' + faState.steps.length;
    bar.style.width = (100 * (faState.i + 1) / faState.steps.length) + '%';
    prev.disabled = faState.i === 0;
    next.textContent = faState.i === faState.steps.length - 1 ? '✓ Fertig' : 'Weiter →';
  }

  function faClose() {
    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
    overlay = null;
    document.removeEventListener('keydown', faKeys);
  }

  function faKeys(ev) {
    if (ev.key === 'Escape') { faClose(); }
    else if (ev.key === 'ArrowRight' || ev.key === 'ArrowDown') { ev.preventDefault(); faNext(); }
    else if (ev.key === 'ArrowLeft' || ev.key === 'ArrowUp') { ev.preventDefault(); faPrev(); }
  }

  function faNext() {
    if (faState.i < faState.steps.length - 1) { faState.i++; faRender(); }
    else faClose();
  }
  function faPrev() { if (faState.i > 0) { faState.i--; faRender(); } }

  function faOpen(title, steps) {
    faState = { steps: steps, i: 0, title: title };
    overlay = document.createElement('div');
    overlay.id = 'fa-overlay';
    overlay.innerHTML =
      '<div id="fa-card">' +
      '<div id="fa-top"><h4></h4><span id="fa-count"></span>' +
      '<button id="fa-close" title="Schließen (Esc)">✕</button></div>' +
      '<div id="fa-progress"><span></span></div>' +
      '<div id="fa-body"></div>' +
      '<div id="fa-nav">' +
      '<span class="fa-hint">Klick aufs Bild oder → = weiter · linker Rand oder ← = zurück · Esc schließt</span>' +
      '<button id="fa-prev" class="fa-nav-btn prev">← Zurück</button>' +
      '<button id="fa-next" class="fa-nav-btn next">Weiter →</button>' +
      '</div></div>';
    document.body.appendChild(overlay);
    overlay.querySelector('h4').textContent = title;
    overlay.addEventListener('click', function (ev) { if (ev.target === overlay) faClose(); });
    document.getElementById('fa-close').addEventListener('click', faClose);
    document.getElementById('fa-prev').addEventListener('click', faPrev);
    document.getElementById('fa-next').addEventListener('click', faNext);
    // Neben ANSYS zählt jeder Klick: Schrittfläche klicken blättert weiter
    // (linkes Randviertel zurück) — der Klick holt zugleich den Fokus in den
    // Browser, danach funktionieren auch die Pfeiltasten sofort.
    var body = document.getElementById('fa-body');
    body.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) return;
      var r = body.getBoundingClientRect();
      if (ev.clientX - r.left < r.width * 0.22) faPrev();
      else faNext();
    });
    document.addEventListener('keydown', faKeys);
    faRender();
  }

  function followAlong(root) {
    var blocks = root.querySelectorAll('details');
    for (var i = 0; i < blocks.length; i++) {
      (function (det) {
        var summary = det.querySelector('summary');
        var ol = det.querySelector('ol');
        if (!summary || !ol) return;
        var label = summary.textContent || '';
        if (!/kurzanleitung|schritt für schritt|klick für klick/i.test(label)) return;
        var lis = ol.children;
        if (lis.length < 2) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'fa-btn';
        btn.innerHTML = '▶ Schritt für Schritt';
        btn.addEventListener('click', function (ev) {
          ev.preventDefault();
          var steps = [];
          for (var s = 0; s < lis.length; s++) steps.push(lis[s].innerHTML);
          faOpen(label.replace(/^\s*[▶▼]?\s*/, '').trim(), steps);
        });
        det.insertBefore(btn, summary.nextSibling);
        det.addEventListener('toggle', function () { });
      })(blocks[i]);
    }
  }

  // --- 4) Klickbarer Workflow-Stepper auf geteilten Schritt-Seiten ---------
  // Aufgaben, die pro Workflow-Schritt eine eigene Seite haben (01-material/
  // … 07-auswertung/), bekommen unter der Überschrift eine Stepper-Navigation
  // zum Springen zwischen den Schritten.
  var WF_SLUGS = ['01-material', '02-geometrie', '03-zuweisung', '04-netz',
                  '05-randbedingungen', '06-loesen', '07-auswertung'];

  function wfPageNav(root) {
    var path = window.location.pathname.replace(/\/+$/, '');
    var seg = path.split('/').pop();
    var idx = WF_SLUGS.indexOf(seg);
    if (idx === -1) return;
    var h1 = root.querySelector('article h1, .md-content__inner h1');
    if (!h1) return;
    var nav = document.createElement('nav');
    nav.className = 'wf-pagenav';
    var html = '';
    for (var i = 0; i < WF_SLUGS.length; i++) {
      var cls = i < idx ? 'done' : i === idx ? 'active' : '';
      html += '<a class="wf-pstep ' + cls + '" href="../' + WF_SLUGS[i] + '/">' +
        '<span class="wf-pnum">' + (i < idx ? '✓' : (i + 1)) + '</span>' +
        '<span class="wf-plabel">' + WF_STEPS[i][1] + '</span></a>';
      if (i < WF_SLUGS.length - 1) html += '<span class="wf-pline' + (i < idx ? ' done' : '') + '"></span>';
    }
    nav.innerHTML = html;
    h1.parentNode.insertBefore(nav, h1.nextSibling);
    // Schmales Fenster (neben ANSYS): aktiven Schritt in die Mitte rücken
    var act = nav.querySelector('.wf-pstep.active');
    if (act && nav.scrollWidth > nav.clientWidth) {
      nav.scrollLeft = act.offsetLeft - nav.clientWidth / 2 + act.clientWidth / 2;
    }
  }

  // --- 4b) Varianten-Tabs über dem Stepper ---------------------------------
  // Aufgaben mit mehreren Lösungswegen (a/b/c …) deklarieren die Tabs am
  // task-banner: data-tabs="Aufgabe=../|a) Vollmodell=../01-material/|…"
  function taskTabs() {
    // data-tabs am task-banner ODER als unsichtbare Konfiguration
    // (<div class="task-tabs-src" data-tabs="…" hidden>) z.B. auf der
    // Aufgabenstellungs-Seite selbst
    var banner = document.querySelector('.task-banner[data-tabs], .task-tabs-src[data-tabs]');
    if (!banner) return;
    var h1 = document.querySelector('.md-content article h1, .md-content__inner h1');
    if (!h1) return;
    var cur = window.location.pathname.replace(/\/+$/, '');
    var curSlug = cur.split('/').pop();
    var wrap = document.createElement('div');
    wrap.className = 'task-tabs';
    banner.getAttribute('data-tabs').split('|').forEach(function (part) {
      var i = part.indexOf('=');
      if (i === -1) return;
      var a = document.createElement('a');
      a.className = 'task-tab';
      a.href = part.slice(i + 1);
      a.textContent = part.slice(0, i);
      var target = new URL(a.href, window.location.href).pathname.replace(/\/+$/, '');
      var active = target === cur ||
        (WF_SLUGS.indexOf(curSlug) !== -1 && WF_SLUGS.indexOf(target.split('/').pop()) !== -1);
      if (active) a.classList.add('active');
      wrap.appendChild(a);
    });
    h1.parentNode.insertBefore(wrap, h1.nextSibling);
  }

  // --- 5) Breadcrumbs eindampfen -------------------------------------------
  // Lange Pfade scrollen sonst horizontal. Wir zeigen Home · … · die letzten
  // beiden Stationen; Klick auf „…" klappt den vollen Pfad aus.
  function collapseBreadcrumbs() {
    // Breadcrumbs raus aus der weißen Karte, auf den Canvas darüber
    var path = document.querySelector('.md-content__inner > .md-path');
    if (path) {
      var inner = path.parentNode;
      inner.parentNode.insertBefore(path, inner);
    }
    var list = document.querySelector('.md-path__list');
    if (!list) return;
    // Nur der Pfad INNERHALB des Praktikums interessiert: Home und die
    // Praktikums-Station selbst fliegen raus (stehen eh in Tabs/Sidebar).
    var items = Array.prototype.slice.call(list.children);
    var cut = 0; // Home (erste Station) immer weg
    items.forEach(function (li, i) {
      var a = li.querySelector('a');
      if (a && /\/P\d+_[^\/]+\/?$/.test(new URL(a.href, window.location.href).pathname)) {
        cut = Math.max(cut, i);
      }
    });
    items.slice(0, cut + 1).forEach(function (li) { li.parentNode.removeChild(li); });
    items = Array.prototype.slice.call(list.children);
    if (items.length < 2) {
      var nav = list.closest('.md-path');
      if (nav && nav.parentNode) nav.parentNode.removeChild(nav);
      return;
    }
    if (items.length <= 4) return;
    var hidden = items.slice(1, items.length - 2);
    hidden.forEach(function (li) { li.classList.add('md-path__item--collapsed'); });
    var dots = document.createElement('li');
    dots.className = 'md-path__item md-path__item--dots';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '…';
    btn.title = 'Ganzen Pfad anzeigen';
    btn.addEventListener('click', function () {
      hidden.forEach(function (li) { li.classList.remove('md-path__item--collapsed'); });
      dots.parentNode.removeChild(dots);
    });
    dots.appendChild(btn);
    list.insertBefore(dots, items[1]);
  }

  function init() {
    var root = document.querySelector('.md-content');
    if (!root) return;
    try { menuPathChips(root); } catch (e) { }
    try { workflowStepper(root); } catch (e) { }
    try { wfPageNav(root); } catch (e) { }
    try { taskTabs(); } catch (e) { }
    try { followAlong(root); } catch (e) { }
    try { collapseBreadcrumbs(); } catch (e) { }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
