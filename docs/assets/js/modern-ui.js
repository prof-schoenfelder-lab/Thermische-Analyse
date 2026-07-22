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
    // Rechtsklick: Maus mit voll gefüllter rechter Taste
    maus: '<svg viewBox="0 0 24 24"><rect x="6.5" y="2.5" width="11" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 3v6.3" stroke="currentColor" stroke-width="1.4"/><path d="M12 3.4h4.1a4.7 4.7 0 0 1 1.4 5.9H12z" fill="currentColor"/></svg>',
    // Linksklick: Maus mit voll gefüllter linker Taste
    mausL: '<svg viewBox="0 0 24 24"><rect x="6.5" y="2.5" width="11" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 3v6.3" stroke="currentColor" stroke-width="1.4"/><path d="M12 3.4H7.9a4.7 4.7 0 0 0-1.4 5.9H12z" fill="currentColor"/></svg>',
    // Doppelklick: linke Taste gefüllt + „2"-Badge — unmissverständlich
    mausD: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="10" height="16.5" rx="5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M8 5.5v5.6" stroke="currentColor" stroke-width="1.4"/><path d="M8 5.9H4.6a4.3 4.3 0 0 0-1.3 5.2H8z" fill="currentColor"/><circle cx="18" cy="6" r="5.4" fill="currentColor"/><text x="18" y="9.15" text-anchor="middle" font-family="Inter, system-ui, sans-serif" font-size="8.4" font-weight="700" fill="var(--kurs-card)">2</text></svg>',
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

  // Vorsatz-Wörter, die sich mit dem folgenden Ziel zu EINER Pille verbinden:
  // Klick-Aktionen (orange) und Orte (blau). cls='act'|'loc' steuert die Optik,
  // merge=true zieht bei alleinstehendem Ort das nächste Pfad-Segment als Ziel
  // heran (z.B. `Strukturbaum → Mesh` → [Strukturbaum | Mesh]).
  var MP_PREFIX = [
    { kw: 'Rechtsklick',  icon: 'maus',   cls: 'act', merge: false },
    { kw: 'Doppelklick',  icon: 'mausD',  cls: 'act', merge: false },
    { kw: 'Linksklick',   icon: 'mausL',  cls: 'act', merge: false },
    { kw: 'Reiter',       icon: 'reiter', cls: 'loc', merge: true },
    { kw: 'Strukturbaum', icon: 'baum',   cls: 'loc', merge: true },
    { kw: 'Detailfenster',icon: 'detail', cls: 'loc', merge: true },
    { kw: 'Grafikfenster',icon: 'grafik', cls: 'loc', merge: true }
  ];

  // Liefert {def, rest} wenn label mit einem Vorsatz-Wort beginnt; rest ist das
  // Ziel im selben Segment (Leerzeichen-Form) bzw. '' wenn nur das Wort dasteht.
  function prefixFor(label) {
    for (var k = 0; k < MP_PREFIX.length; k++) {
      var kw = MP_PREFIX[k].kw;
      if (label === kw) return { def: MP_PREFIX[k], rest: '' };
      if (label.indexOf(kw + ' ') === 0)
        return { def: MP_PREFIX[k], rest: label.slice(kw.length + 1).trim() };
    }
    return null;
  }

  // Einzelbegriffe ohne Pfeil, die trotzdem als Ort-Chip erscheinen sollen
  var MP_SOLO = /^(Reiter |Rechtsklick|Doppelklick|Linksklick|Strukturbaum|Detailfenster|Grafikfenster)/;

  // Ein einfaches Ziel-Chip rendern (mit Ort-Icon, falls es selbst ein Ort ist)
  function renderPlain(label) {
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
    return seg;
  }

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
      var first = true;
      for (var p = 0; p < parts.length; p++) {
        var label = parts[p].trim();
        var pf = prefixFor(label);
        var node;
        if (pf) {
          var rest = pf.rest;
          // alleinstehender Ort (Pfeil-Form): nächstes Segment als Ziel ziehen
          if (!rest && pf.def.merge && p + 1 < parts.length) {
            rest = parts[p + 1].trim();
            p++;
          }
          if (rest) {
            // zusammengesetzte Pille: [Icon Wort | Ziel]
            node = document.createElement('span');
            node.className = 'mp-click mp-click--' + pf.def.cls;
            var pre = document.createElement('span');
            pre.className = 'mp-seg mp-' + (pf.def.cls === 'act' ? 'action' : 'loc');
            pre.innerHTML = '<i class="mp-ic">' + MP_ICONS[pf.def.icon] + '</i>';
            pre.appendChild(document.createTextNode(pf.def.kw));
            node.appendChild(pre);
            node.appendChild(renderPlain(rest));
          } else {
            // nur das Wort (z.B. `Detailfenster` allein) → Ort-Chip mit Icon
            node = renderPlain(pf.def.kw);
          }
        } else {
          node = renderPlain(label);
        }
        if (!first) {
          var ar = document.createElement('span');
          ar.className = 'mp-arrow';
          ar.textContent = '→';
          span.appendChild(ar);
        }
        first = false;
        span.appendChild(node);
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
  // Aufgaben, die pro Workflow-Schritt eine eigene Seite haben, bekommen
  // unter der Überschrift eine Stepper-Navigation zum Springen zwischen den
  // Schritten. Jede Schritt-Gruppe beschreibt ihre Slugs (Geschwister-Seiten
  // im selben Ordner), Kurz-Labels und optional eine Tabs-Zeile darüber.
  var WF_SLUGS = ['01-material', '02-geometrie', '03-zuweisung', '04-netz',
                  '05-randbedingungen', '06-loesen', '07-auswertung'];
  var WF_GROUPS = [
    { // Konvention nummerierter Schritt-Slugs (wie Thermo-Kurs, Rohr-Muster)
      slugs: WF_SLUGS,
      labels: ['Material', 'Geometrie', 'Zuweisung', 'Netz', 'Randbed.', 'Lösen', 'Auswertung'],
      base: null,
      tabs: null
    },
    { // P1 Vorzeigebeispiel: zweiseitig gelagerter Balken (Lösung mit ANSYS)
      // '' = die Übersichtsseite (README, Workbench öffnen) als Schritt 1
      slugs: ['', 'material', 'geometrie', 'materialzuordnung', 'vernetzung',
              'navigation', 'lagerung', 'belastung', 'gleichungssystem-losen',
              'gesuchte-werte-bestimmen'],
      labels: ['Start', 'Material', 'Geometrie', 'Zuweisung', 'Netz', 'Navigation',
               'Lagerung', 'Belastung', 'Lösen', 'Auswertung'],
      base: 'losung-mit-ansys',
      tabs: 'Aufgabe=../../Aufgabenstellung/|Lösung mit ANSYS=../|Analytische Lösung=../../analytische-loesung/',
      tabsIndex: 'Aufgabe=../Aufgabenstellung/|Lösung mit ANSYS=./|Analytische Lösung=../analytische-loesung/'
    }
  ];

  // Liefert {grp, idx, isIndex} wenn der Pfad eine Schrittseite einer Gruppe
  // ist. isIndex: die Seite ist die Basis-Übersicht (Slug '') selbst.
  function wfGroupFor(path) {
    var parts = path.split('/');
    var seg = parts.pop();
    var parent = parts[parts.length - 1];
    for (var g = 0; g < WF_GROUPS.length; g++) {
      var grp = WF_GROUPS[g];
      var idx = grp.slugs.indexOf(seg);
      if (idx !== -1 && seg !== '' && (!grp.base || parent === grp.base)) {
        return { grp: grp, idx: idx, isIndex: false };
      }
      // Basis-Übersicht als eigener Schritt (Slug '')
      if (grp.base && seg === grp.base && grp.slugs[0] === '') {
        return { grp: grp, idx: 0, isIndex: true };
      }
    }
    return null;
  }

  function wfPageNav(root) {
    var path = window.location.pathname.replace(/\/+$/, '');
    var hit = wfGroupFor(path);
    if (!hit) return;
    var grp = hit.grp, idx = hit.idx;
    var h1 = root.querySelector('article h1, .md-content__inner h1');
    if (!h1) return;
    var nav = document.createElement('nav');
    nav.className = 'wf-pagenav';
    var html = '';
    // Links relativ zur Basis: von der Übersicht aus 'slug/', von einer
    // Schrittseite aus '../slug/'; die Übersicht selbst ist './' bzw. '../'
    var up = hit.isIndex ? '' : '../';
    for (var i = 0; i < grp.slugs.length; i++) {
      var cls = i < idx ? 'done' : i === idx ? 'active' : '';
      var href = grp.slugs[i] === '' ? (hit.isIndex ? './' : '../')
                                     : up + grp.slugs[i] + '/';
      html += '<a class="wf-pstep ' + cls + '" href="' + href + '">' +
        '<span class="wf-pnum">' + (i < idx ? '✓' : (i + 1)) + '</span>' +
        '<span class="wf-plabel">' + grp.labels[i] + '</span></a>';
      if (i < grp.slugs.length - 1) html += '<span class="wf-pline' + (i < idx ? ' done' : '') + '"></span>';
    }
    nav.innerHTML = html;
    h1.parentNode.insertBefore(nav, h1.nextSibling);
    // Schmales Fenster (neben ANSYS): aktiven Schritt in die Mitte rücken —
    // aber nur bei deutlichem Überlauf, sonst schneidet es links an
    var act = nav.querySelector('.wf-pstep.active');
    if (act && nav.scrollWidth > nav.clientWidth + 40) {
      nav.scrollLeft = act.offsetLeft - nav.clientWidth / 2 + act.clientWidth / 2;
    }
  }

  // --- 4b) Varianten-Tabs über dem Stepper ---------------------------------
  // Aufgaben mit mehreren Lösungswegen (a/b/c …) deklarieren die Tabs am
  // task-banner: data-tabs="Aufgabe=../|a) Vollmodell=../01-material/|…"
  function taskTabs() {
    // data-tabs am task-banner ODER als unsichtbare Konfiguration
    // (<div class="task-tabs-src" data-tabs="…" hidden>) z.B. auf der
    // Aufgabenstellungs-Seite selbst — ODER automatisch aus der
    // Schritt-Gruppe (WF_GROUPS mit tabs-Eintrag)
    var cur = window.location.pathname.replace(/\/+$/, '');
    var hit = wfGroupFor(cur);
    var banner = document.querySelector('.task-banner[data-tabs], .task-tabs-src[data-tabs]');
    var tabsStr = banner ? banner.getAttribute('data-tabs')
                         : (hit ? (hit.isIndex ? hit.grp.tabsIndex : hit.grp.tabs) : null);
    if (!tabsStr) return;
    var h1 = document.querySelector('.md-content article h1, .md-content__inner h1');
    if (!h1) return;
    var parentDir = cur.slice(0, cur.lastIndexOf('/'));
    var wrap = document.createElement('div');
    wrap.className = 'task-tabs';
    tabsStr.split('|').forEach(function (part) {
      var i = part.indexOf('=');
      if (i === -1) return;
      var a = document.createElement('a');
      a.className = 'task-tab';
      a.href = part.slice(i + 1);
      a.textContent = part.slice(0, i);
      var target = new URL(a.href, window.location.href).pathname.replace(/\/+$/, '');
      // aktiv: Ziel = aktuelle Seite, Ziel = Schritt-Ordner der aktuellen
      // Schrittseite, oder (alte Konvention) beide sind Schritt-Slugs
      // derselben Gruppe
      var tHit = wfGroupFor(target);
      var active = target === cur ||
        (hit && target === parentDir) ||
        (hit && tHit && tHit.grp === hit.grp);
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
    // Mitmach-Overlay abgeschaltet: die Anleitungen bleiben als scrollbare
    // Ausklapp-Blöcke auf der Seite (Entscheidung 07/2026).
    // try { followAlong(root); } catch (e) { }
    try { collapseBreadcrumbs(); } catch (e) { }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
