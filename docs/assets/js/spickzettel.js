// "Mein Spickzettel": der Zettel als fertige Ansicht (zwei Spalten wie im Druck), im Modus "Bearbeiten"
// Aussagen aus dem Kurs übernehmen (assets/spickzettel.json, scripts/spickzettel_hook.py), umformulieren,
// eigene Einträge ergänzen. Unveränderte Übernahmen zeigen immer die aktuelle Kursfassung, selbst
// bearbeitete Einträge behalten ihren Text. Füllstand für ein Blatt A4 vorne und hinten, Druck über ein
// unsichtbares iframe. Stand im localStorage ("spickzettel"), nach OPAL-Login zusätzlich auf dem Server
// (/api/spickzettel): der neuere Stand gewinnt. backend-sync.js meldet "kurs:angemeldet" nach der Besitzerprüfung.
(function () {
  'use strict';

  var KEY = 'spickzettel';
  var s = document.currentScript || document.querySelector('script[src*="spickzettel.js"]');
  var BASE = new URL((s && s.getAttribute('src')) || '.', document.baseURI).href.replace(/assets\/js\/spickzettel\.js.*$/, '');
  var BACKEND = (window.AC_BACKEND_URL || '').replace(/\/$/, '');
  // Abschnitte: Kennung, Marke vor der Überschrift, Überschrift
  var GRUPPEN = [
    ['P1', 'P1', 'Einführung'], ['P2', 'P2', 'Randbedingungen und Strahlung'],
    ['P3', 'P3', 'Abstraktionen und Vernetzung'], ['P4', 'P4', 'Instationär I'], ['P5', 'P5', 'Instationär II'],
    ['weitere', '✎', 'Weitere Notizen']
  ];
  // Blatt: A4 mit 10 mm Rand, zwei Spalten mit 5 mm Abstand, vorne und hinten
  var MM = 96 / 25.4, SPALTE = 92.5, HOEHE = 277, SPALTEN = 4;
  var DRUCK_CSS =
    '@page{size:A4;margin:10mm}' +
    'body{margin:0;font:8pt/1.25 "Source Sans Pro","Source Sans 3",Arial,sans-serif;color:#000}' +
    '.blatt{column-count:2;column-gap:5mm;column-fill:auto}' +
    'h2{display:inline-block;font-size:9pt;margin:0 0 1mm;padding:0 1mm;color:#022541;break-after:avoid;' +
    'background:linear-gradient(transparent 55%,#bfe6f8 55%);-webkit-print-color-adjust:exact;print-color-adjust:exact}' +
    'h2 span{color:#0070a6;margin-right:1.5mm}' +
    'section{margin:0 0 2.5mm}' +
    'p{margin:0 0 1mm;white-space:pre-wrap}strong{color:#022541}' +
    '.fehler p:before{content:"\\2610  "}';

  var stand = normal(lesen()), daten = null, token = null, angemeldet = false, sendeTimer = null, messFrame = null;
  var bearbeiten = false, offen = null;  // offen: id des Eintrags im Formular oder "neu:<gruppe>"
  var info = null;  // Erklärung aus Spickzettel.md (#sz-info), aufklappbar über den Knopf „i“
  var umschreiben = false;  // Formular eines Zitats gerade als freier Text

  function lesen() { try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; } }
  function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return '&#' + c.charCodeAt(0) + ';'; }); }
  function neueId() { return 'e' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }

  // Stand der ersten Fassung (Auswahl kurz/ausführlich, Häkchen, Notizfelder) in Einträge übernehmen
  function normal(d) {
    if (!d) return { version: 2, stand: 0, eintraege: [] };
    if (d.eintraege) return d;
    var e = [];
    Object.keys(d.kern || {}).forEach(function (id) {
      var p = (id.match(/^kern-(p\d+)-/) || [])[1];
      if (p) e.push({ id: neueId(), gruppe: p.toUpperCase(), quelle: id });
    });
    Object.keys(d.check || {}).forEach(function (id) { e.push({ id: neueId(), gruppe: 'fehler', quelle: id }); });
    Object.keys(d.notizen || {}).forEach(function (g) {
      var t = (d.notizen[g] || '').trim();
      if (t) e.push({ id: neueId(), gruppe: g, quelle: null, eigen: { titel: '', text: t } });
    });
    return { version: 2, stand: d.stand || 0, eintraege: e };
  }

  function quelle(id) {
    if (!id || !daten) return null;
    var alle = daten.kernaussagen.concat(daten.checkliste);
    for (var i = 0; i < alle.length; i++) if (alle[i].id === id) return alle[i];
    return null;
  }
  // angezeigter Inhalt: eigene Fassung, sonst die aktuelle Kursfassung, sonst die Kopie von damals
  // Selbst markierter Text (e.markiert) ist ein Zitat: Stichwort davor und Ergänzung dahinter sind änderbar,
  // umschreiben macht daraus normalen Text (e.umgeschrieben), „Zitat wiederherstellen“ holt den Wortlaut zurück
  function inhalt(e) {
    if (e.eigen) return { titel: e.eigen.titel, text: e.eigen.text, zusatz: e.eigen.zusatz, zitat: !!e.markiert && !e.umgeschrieben };
    var q = quelle(e.quelle);
    return q ? { titel: q.titel, text: q.text } : (e.kopie || { titel: '', text: '' });
  }
  function vorschlaege(g) {
    if (!daten || g === 'weitere') return [];
    var liste = g === 'fehler' ? daten.checkliste : daten.kernaussagen.filter(function (k) { return k.praktikum === g; });
    return liste.filter(function (q) { return !stand.eintraege.some(function (e) { return e.quelle === q.id; }); });
  }

  function speichern() {
    stand.stand = Date.now();
    try { localStorage.setItem(KEY, JSON.stringify(stand)); } catch (e) { }
    zeigen();
    if (angemeldet) {
      clearTimeout(sendeTimer);
      sendeTimer = setTimeout(senden, 1500);
    }
  }

  // ---- Zettel --------------------------------------------------------------------------------------------
  function zeile(i, inline) {
    var text = i.zitat ? '<em>' + esc(i.text) + '</em>' : esc(i.text || '');
    var t = (i.titel ? '<strong>' + esc(i.titel) + '</strong>' + (i.text ? ' ' : '') : '') + text +
      (i.zusatz ? ' ' + esc(i.zusatz) : '');
    return inline ? t : '<p>' + t + '</p>';
  }

  function eintragHtml(e) {
    if (offen === e.id) {
      var i = inhalt(e);
      if (umschreiben) i = { titel: i.titel, text: i.text + (i.zusatz ? ' ' + i.zusatz : '') };
      return formular(i, e.markiert ? (e.umgeschrieben || umschreiben) && 'Zitat wiederherstellen'
        : e.quelle && e.eigen && 'Kursfassung wiederherstellen');
    }
    var q = quelle(e.quelle), link = q ? q.url : e.link;  // link: Stelle eines auf der Kursseite markierten Texts
    return '<div class="sz-e" data-id="' + e.id + '"><span class="sz-e-text">' + zeile(inhalt(e), true) + '</span>' +
      (link ? ' <a class="sz-mehr" href="' + BASE + link + '">Mehr Info ›</a>' : '') +
      (bearbeiten ? '<span class="sz-knoepfe">' +
        '<button type="button" data-aktion="edit" data-id="' + e.id + '" aria-label="Bearbeiten" title="Bearbeiten">✎</button>' +
        '<button type="button" data-aktion="weg" data-id="' + e.id + '" aria-label="Entfernen" title="Entfernen">✕</button></span>' : '') +
      '</div>';
  }

  function formular(i, zurueck) {
    return '<div class="sz-form">' +
      '<input type="text" data-feld="titel" placeholder="Stichwort (fett)" value="' + esc(i.titel || '') + '">' +
      (i.zitat
        ? '<p class="sz-zitat">' + esc(i.text) + '</p>' +
          '<textarea data-feld="zusatz" rows="2" placeholder="Ergänzung in eigenen Worten">' + esc(i.zusatz || '') + '</textarea>' +
          '<button type="button" class="sz-link sz-umschreiben" data-aktion="umschreiben">In eigenen Worten umschreiben</button>'
        : '<textarea data-feld="text" rows="3" placeholder="In eigenen Worten">' + esc(i.text || '') + '</textarea>') +
      '<span class="sz-form-knoepfe"><button type="button" class="md-button md-button--primary" data-aktion="ok">Übernehmen</button>' +
      '<button type="button" class="md-button" data-aktion="abbrechen">Abbrechen</button>' +
      (zurueck ? '<button type="button" class="sz-link" data-aktion="original">' + zurueck + '</button>' : '') +
      '</span></div>';
  }

  function gruppeHtml(g) {
    var eintraege = stand.eintraege.filter(function (e) { return e.gruppe === g[0]; });
    if (!bearbeiten && !eintraege.length) return '';
    var html = '<section class="sz-abschnitt sz-g-' + g[0] + '">' + kopf(g) + eintraege.map(eintragHtml).join('');
    if (bearbeiten) {
      var vor = vorschlaege(g[0]);
      html += (offen === 'neu:' + g[0] ? formular({}, false) : '') +
        '<div class="sz-vorschlaege">' +
        (vor.length ? '<span class="sz-vor-titel">Aus dem Kurs übernehmen</span>' : '') +
        vor.map(function (q) {
          return '<button type="button" data-aktion="nimm" data-gruppe="' + g[0] + '" data-quelle="' + q.id + '">+ ' + esc(q.titel || q.text) + '</button>';
        }).join('') +
        '<button type="button" class="sz-eigen" data-aktion="neu" data-gruppe="' + g[0] + '">+ Eigener Eintrag</button>' +
        '</div>';
    }
    return html + '</section>';
  }

  function kopf(g) { return '<h2><span>' + g[1] + '</span>' + g[2] + '</h2>'; }

  function blattHtml() {
    return GRUPPEN.map(function (g) {
      var e = stand.eintraege.filter(function (x) { return x.gruppe === g[0]; });
      return e.length ? '<section' + (g[0] === 'fehler' ? ' class="fehler"' : '') + '>' + kopf(g) +
        e.map(function (x) { return zeile(inhalt(x), false); }).join('') + '</section>' : '';
    }).join('');
  }

  function dokument(inhalt, mess) {
    return '<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Spickzettel</title><style>' + DRUCK_CSS +
      (mess ? '.blatt{column-count:1;width:' + SPALTE + 'mm}' : '') + '</style></head><body><div class="blatt">' +
      inhalt + '</div></body></html>';
  }

  // Höhe in einer Spalte messen (gleiche Schrift wie im Druck), Anteil an 2 Seiten × 2 Spalten
  function fuellstand() {
    if (!messFrame) {
      messFrame = document.createElement('iframe');
      messFrame.setAttribute('aria-hidden', 'true');
      messFrame.tabIndex = -1;
      messFrame.style.cssText = 'position:absolute;left:-9999px;top:0;width:' + (SPALTE + 2) + 'mm;height:10px;border:0;visibility:hidden';
      document.body.appendChild(messFrame);
    }
    var d = messFrame.contentDocument;
    d.open(); d.write(dokument(blattHtml(), true)); d.close();
    return d.querySelector('.blatt').scrollHeight / (SPALTEN * HOEHE * MM);
  }

  function zeigen() {
    var box = document.getElementById('spickzettel');
    var leer = !stand.eintraege.length;
    var pct = Math.round(fuellstand() * 100);
    box.innerHTML =
      '<div class="sz-leiste">' +
      '<div class="sz-fuell' + (pct > 100 ? ' sz-voll' : '') + '"><div class="sz-fuell-balken"><div style="width:' + Math.min(pct, 100) + '%"></div></div>' +
      '<span>' + (pct > 100 ? pct + ' %: passt nicht mehr auf ein Blatt, bitte kürzen' : pct + ' % des Blatts (A4 vorne und hinten)') + '</span></div>' +
      '<button type="button" class="sz-info-knopf" data-aktion="info" aria-label="Erklärung" title="Erklärung"' +
      ' aria-expanded="' + (info && !info.hidden) + '">i</button>' +
      '<button type="button" class="md-button' + (bearbeiten ? ' md-button--primary' : '') + '" data-aktion="modus">' + (bearbeiten ? 'Fertig' : 'Bearbeiten') + '</button>' +
      '<button type="button" class="md-button" data-aktion="drucken"' + (leer ? ' disabled' : '') + '>Drucken</button></div>' +
      (leer && !bearbeiten
        ? '<div class="sz-leer"><p>Ihr Spickzettel ist noch leer.</p><p>Mit <strong>Bearbeiten</strong> übernehmen Sie Aussagen aus dem Kurs und formulieren sie in eigenen Worten um, oder Sie schreiben eigene Einträge.</p></div>'
        : '<div class="sz-blatt' + (bearbeiten ? ' sz-bearbeiten' : '') + '">' +
          '<header class="sz-kopf"><span>Mein Spickzettel</span>Angewandte FEM in der Thermodynamik</header>' +
          GRUPPEN.map(gruppeHtml).join('') + '</div>');
    if (info) box.querySelector('.sz-leiste').after(info);
    var feld = box.querySelector('.sz-form input');
    if (feld) feld.focus();
  }

  function drucken() {
    var f = document.createElement('iframe');
    f.setAttribute('aria-hidden', 'true');
    f.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0';
    document.body.appendChild(f);
    var d = f.contentDocument;
    d.open(); d.write(dokument(blattHtml(), false)); d.close();
    setTimeout(function () {
      f.contentWindow.focus();
      f.contentWindow.print();
      setTimeout(function () { f.remove(); }, 1000);
    }, 100);
  }

  // ---- Bedienung -----------------------------------------------------------------------------------------
  function eintrag(id) { return stand.eintraege.filter(function (e) { return e.id === id; })[0]; }

  function formularUebernehmen(box) {
    var titel = box.querySelector('.sz-form [data-feld="titel"]').value.trim();
    var feld = box.querySelector('.sz-form [data-feld="text"]'), text = feld ? feld.value.trim() : '';
    if (offen.indexOf('neu:') === 0) {
      if (titel || text) stand.eintraege.push({ id: neueId(), gruppe: offen.slice(4), quelle: null, eigen: { titel: titel, text: text } });
    } else {
      var e = eintrag(offen), q = quelle(e.quelle);
      var zusatz = box.querySelector('.sz-form [data-feld="zusatz"]');
      if (zusatz) e.eigen = { titel: titel, text: e.markiert, zusatz: zusatz.value.trim() };
      else if (!titel && !text) stand.eintraege.splice(stand.eintraege.indexOf(e), 1);
      else if (e.markiert) { e.eigen = { titel: titel, text: text }; e.umgeschrieben = true; }
      else if (q && q.titel === titel && q.text === text) delete e.eigen;  // unverändert: bleibt an der Kursfassung
      else e.eigen = { titel: titel, text: text };
    }
    offen = null;
    umschreiben = false;
    speichern();
  }

  function klick(ev) {
    var b = ev.target.closest('[data-aktion]');
    if (!b) return;
    var a = b.dataset.aktion, box = document.getElementById('spickzettel');
    if (a !== 'umschreiben' && a !== 'ok' && a !== 'original') umschreiben = false;
    if (a === 'modus') { bearbeiten = !bearbeiten; offen = null; zeigen(); }
    else if (a === 'info') { info.hidden = !info.hidden; b.setAttribute('aria-expanded', !info.hidden); }
    else if (a === 'drucken') drucken();
    else if (a === 'edit') { offen = b.dataset.id; zeigen(); }
    else if (a === 'neu') { offen = 'neu:' + b.dataset.gruppe; zeigen(); }
    else if (a === 'abbrechen') { offen = null; zeigen(); }
    else if (a === 'ok') formularUebernehmen(box);
    else if (a === 'umschreiben') { umschreiben = true; zeigen(); }
    else if (a === 'original') {
      var o = eintrag(offen);
      if (o.markiert) { o.eigen = { titel: (o.eigen && o.eigen.titel) || '', text: o.markiert }; delete o.umgeschrieben; }
      else delete o.eigen;
      offen = null; umschreiben = false; speichern();
    }
    else if (a === 'weg') {
      stand.eintraege.splice(stand.eintraege.indexOf(eintrag(b.dataset.id)), 1);
      speichern();
    } else if (a === 'nimm') {
      var q = quelle(b.dataset.quelle);
      stand.eintraege.push({ id: neueId(), gruppe: b.dataset.gruppe, quelle: q.id, kopie: { titel: q.titel, text: q.text } });
      speichern();
    }
  }

  // ---- Server ---------------------------------------------------------------------------------------------
  function senden() {
    fetch(BACKEND + '/api/spickzettel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ daten: stand })
    }).catch(function () { });
  }

  function abgleichen() {
    fetch(BACKEND + '/api/spickzettel', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (srv) {
        if (!srv) return;
        angemeldet = true;
        var server = srv.daten;
        if (server && (server.stand || 0) > (stand.stand || 0)) {
          stand = normal(server);
          try { localStorage.setItem(KEY, JSON.stringify(stand)); } catch (e) { }
          if (!offen) zeigen();
        } else if ((stand.stand || 0) > ((server && server.stand) || 0)) {
          senden();
        }
      })
      .catch(function () { });
  }

  // ---- Kursseiten: „+ Zum Spickzettel“ an Zusammenfassung, Merke-Kästen und Checkliste, markierter Text ---
  function hat(qid) { return stand.eintraege.some(function (e) { return e.quelle === qid; }); }

  // angemeldet: erst den neueren Stand vom Server holen, damit ein Eintrag hier keinen Stand von einem
  // anderen Rechner überschreibt; auch andere Tabs können den Stand im Browser inzwischen geändert haben
  function holen() {
    stand = normal(lesen());
    if (!BACKEND || !token || !window.AC_ANGEMELDET) return Promise.resolve();
    return fetch(BACKEND + '/api/spickzettel', { headers: { 'Authorization': 'Bearer ' + token } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (srv) {
        if (!srv) return;
        angemeldet = true;
        if (srv.daten && (srv.daten.stand || 0) > (stand.stand || 0)) {
          stand = normal(srv.daten);
          try { localStorage.setItem(KEY, JSON.stringify(stand)); } catch (e) { }
        }
      })
      .catch(function () { });
  }

  function hinzufuegen(e) {
    return holen().then(function () {
      stand.eintraege.push(e);
      stand.stand = Date.now();
      try { localStorage.setItem(KEY, JSON.stringify(stand)); } catch (x) { }
      if (angemeldet) senden();
      melden();
    });
  }

  function melden() {
    var t = document.getElementById('sz-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'sz-toast';
      t.setAttribute('role', 'status');
      document.body.appendChild(t);
    }
    t.innerHTML = '✓ Auf dem Spickzettel <a href="' + BASE + 'Spickzettel/">Ansehen</a>';
    t.classList.add('sz-zeigen');
    clearTimeout(t.timer);
    t.timer = setTimeout(function () { t.classList.remove('sz-zeigen'); }, 3500);
  }

  function knopfAn(el, aktualisieren) {
    var q = quelle(el.id);
    if (!q) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'sz-plus';
    function zeigeStand() {
      var drauf = hat(q.id);
      b.textContent = drauf ? '✓ Auf dem Spickzettel' : '+ Zum Spickzettel';
      b.classList.toggle('sz-drauf', drauf);
    }
    b.addEventListener('click', function () {
      if (hat(q.id)) { location.href = BASE + 'Spickzettel/'; return; }
      var gruppe = q.praktikum === undefined ? 'fehler' : (q.praktikum || 'weitere');
      hinzufuegen({ id: neueId(), gruppe: gruppe, quelle: q.id, kopie: { titel: q.titel, text: q.text } }).then(zeigeStand);
    });
    zeigeStand();
    aktualisieren.push(zeigeStand);
    el.appendChild(b);
  }

  function seite() { return location.href.split('#')[0].replace(BASE, ''); }

  // Selbst markierter und übernommener Text bleibt auf der Kursseite hinterlegt, solange der Eintrag besteht:
  // Text im Artikel suchen (Leerraum zusammengefasst) und je Textknoten in <mark class="sz-markiert"> legen
  function markieren() {
    var artikel = document.querySelector('article');
    if (!artikel) return;
    artikel.querySelectorAll('mark.sz-markiert').forEach(function (m) {
      var eltern = m.parentNode;
      while (m.firstChild) eltern.insertBefore(m.firstChild, m);
      eltern.removeChild(m);
      eltern.normalize();
    });
    var hier = stand.eintraege.filter(function (e) { return e.markiert && e.link && e.link.split('#')[0] === seite(); });
    if (!hier.length) return;
    var text = '', karte = [], walker = document.createTreeWalker(artikel, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        return n.parentNode.closest('script, style, button, input, textarea, pre, mjx-container, .arithmatex, .sz-plus')
          ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    for (var n = walker.nextNode(); n; n = walker.nextNode()) {
      for (var i = 0; i < n.data.length; i++) {
        var leer = /\s/.test(n.data[i]);
        if (leer && (!text.length || text[text.length - 1] === ' ')) continue;
        text += leer ? ' ' : n.data[i];
        karte.push([n, i]);
      }
    }
    hier.forEach(function (e) {
      var start = text.indexOf(e.markiert);
      if (start < 0) return;
      var stuecke = [];
      for (var k = start; k < start + e.markiert.length; k++) {
        var z = karte[k], letztes = stuecke[stuecke.length - 1];
        if (letztes && letztes[0] === z[0]) letztes[2] = z[1] + 1; else stuecke.push([z[0], z[1], z[1] + 1]);
      }
      stuecke.reverse().forEach(function (st) {
        var r = document.createRange(), m = document.createElement('mark');
        m.className = 'sz-markiert';
        m.dataset.id = e.id;
        m.title = 'Steht auf Ihrem Spickzettel: anklicken zum Ansehen oder Entfernen';
        r.setStart(st[0], st[1]);
        r.setEnd(st[0], st[2]);
        r.surroundContents(m);
      });
    });
  }

  // Seite plus nächste Überschrift über dem markierten Text
  function stelle(el) {
    var id = '';
    document.querySelectorAll('article h1[id], article h2[id], article h3[id], article h4[id]').forEach(function (h) {
      if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) id = h.id;
    });
    return seite() + (id ? '#' + id : '');
  }

  function auswahlKnopf() {
    var artikel = document.querySelector('article');
    if (!artikel) return;
    var knopf = document.createElement('button'), auswahl = null, timer = null;
    knopf.type = 'button';
    knopf.id = 'sz-auswahl';
    knopf.textContent = '+ Spickzettel';
    knopf.hidden = true;
    document.body.appendChild(knopf);
    knopf.addEventListener('mousedown', function (ev) { ev.preventDefault(); });  // Markierung bleibt stehen
    knopf.addEventListener('click', function () {
      var a = auswahl, m = /(?:^|\/)P(\d+)_/.exec(location.pathname);
      knopf.hidden = true;
      if (!a) return;
      window.getSelection().removeAllRanges();
      hinzufuegen({ id: neueId(), gruppe: m ? 'P' + m[1] : 'weitere', quelle: null, eigen: { titel: '', text: a.text },
        link: a.link, markiert: a.text }).then(markieren);
    });
    document.addEventListener('selectionchange', function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var sel = window.getSelection(), text = sel.toString().replace(/\s+/g, ' ').trim();
        var r = sel.rangeCount ? sel.getRangeAt(0) : null;
        var start = r && (r.startContainer.nodeType === 1 ? r.startContainer : r.startContainer.parentNode);
        if (!r || text.length < 3 || text.length > 600 || !artikel.contains(start) ||
            start.closest('input, textarea, button, pre, .sz-plus')) {
          knopf.hidden = true;
          auswahl = null;
          return;
        }
        auswahl = { text: text, link: stelle(start) };
        var box = r.getBoundingClientRect();
        knopf.style.left = Math.max(8, Math.min(document.documentElement.clientWidth - 130, box.left + box.width / 2 - 55)) + window.scrollX + 'px';
        knopf.style.top = box.top + window.scrollY - 34 + 'px';  // über der Markierung, verdeckt keinen Text darunter
        knopf.hidden = false;
      }, 250);
    });
  }

  // Klick auf eine Markierung: kleines Menü mit „Ansehen“ und „Entfernen“
  function markierungsMenue() {
    var menue = document.createElement('div');
    menue.id = 'sz-menue';
    menue.hidden = true;
    menue.innerHTML = '<span>Auf Ihrem Spickzettel</span><a href="' + BASE + 'Spickzettel/">Ansehen</a>' +
      '<button type="button">Entfernen</button>';
    document.body.appendChild(menue);
    document.addEventListener('click', function (ev) {
      var m = ev.target.closest('mark.sz-markiert');
      if (m && !window.getSelection().toString()) {
        var box = m.getBoundingClientRect();
        menue.dataset.id = m.dataset.id;
        menue.style.left = Math.max(8, Math.min(document.documentElement.clientWidth - 260, box.left)) + window.scrollX + 'px';
        menue.style.top = box.bottom + window.scrollY + 6 + 'px';
        menue.hidden = false;
      } else if (!menue.contains(ev.target)) {
        menue.hidden = true;
      }
    });
    menue.querySelector('button').addEventListener('click', function () {
      var id = menue.dataset.id;
      menue.hidden = true;
      holen().then(function () {
        stand.eintraege = stand.eintraege.filter(function (e) { return e.id !== id; });
        stand.stand = Date.now();
        try { localStorage.setItem(KEY, JSON.stringify(stand)); } catch (x) { }
        if (angemeldet) senden();
        markieren();
      });
    });
  }

  function kursseite() {
    var stellen = document.querySelectorAll('.step[id^="kern-"], .merke[id^="kern-"], li[id^="check-"]'), aktualisieren = [];
    if (stellen.length) {
      fetch(BASE + 'assets/spickzettel.json')
        .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
        .then(function (d) {
          daten = d;
          stellen.forEach(function (el) { knopfAn(el, aktualisieren); });
          // nach der Anmeldung den Stand vom Server holen, damit „Auf dem Spickzettel“ stimmt
          var nachAnmeldung = function () { holen().then(function () { aktualisieren.forEach(function (f) { f(); }); }); };
          if (window.AC_ANGEMELDET) nachAnmeldung(); else document.addEventListener('kurs:angemeldet', nachAnmeldung);
        })
        .catch(function () { });
    }
    auswahlKnopf();
    markierungsMenue();
    markieren();
    if (!window.AC_ANGEMELDET) document.addEventListener('kurs:angemeldet', function () { holen().then(markieren); });
    else holen().then(markieren);
  }

  // Symbol im Seitenkopf: von jeder Seite schnell zum Spickzettel
  function kopfSymbol() {
    var suche = document.querySelector('.md-header__inner .md-search');
    if (!suche) return;
    var a = document.createElement('a');
    a.className = 'md-header__button md-icon sz-kopf-link';
    a.href = BASE + 'Spickzettel/';
    a.title = 'Mein Spickzettel';
    a.setAttribute('aria-label', 'Mein Spickzettel');
    a.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h4v-1.9l2-2V20h-.1L10 22H6V4h7v5h5v1.1l2-2V8l-6-6m6.1 11c-.1 0-.3.1-.4.2l-1 1 2.1 2.1 1-1c.2-.2.2-.6 0-.8l-1.3-1.3c-.1-.1-.2-.2-.4-.2m-2 1.8L12 20.9V23h2.1l6.1-6.1-2.1-2.1Z"/></svg>';
    suche.parentNode.insertBefore(a, suche);
  }

  function init() {
    var box = document.getElementById('spickzettel');
    try { token = localStorage.getItem('ac_backend_token'); } catch (e) { }
    kopfSymbol();
    if (!box) { kursseite(); return; }
    info = document.getElementById('sz-info');
    box.addEventListener('click', klick);
    box.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && offen) { offen = null; umschreiben = false; zeigen(); }
      else if (ev.key === 'Enter' && ev.target.matches('.sz-form input')) formularUebernehmen(box);
    });
    fetch(BASE + 'assets/spickzettel.json')
      .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
      .then(function (d) {
        daten = d;
        zeigen();
        if (BACKEND && token) {
          if (window.AC_ANGEMELDET) abgleichen();
          else document.addEventListener('kurs:angemeldet', abgleichen);
        }
      })
      .catch(function () { box.innerHTML = '<p class="sz-laden">Spickzettel konnte nicht geladen werden.</p>'; });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
