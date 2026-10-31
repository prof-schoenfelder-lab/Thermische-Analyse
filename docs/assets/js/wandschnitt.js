// Wandschnitt 2D: Oberfläche der Seite werkzeuge/wandschnitt (Editor, Bild, Ergebnisse, Speichern).
// Einbinden: <div id="wandschnitt"></div>. Rechenkern in wandschnitt-loeser.js, Materialien und Vorlagen in wandschnitt-daten.js.
(function () {
  'use strict';

  // ANSYS-Legende: neun Bänder von Blau nach Rot (wie hero-anim.js)
  const BAENDER = [[0, 0, 255], [0, 178, 255], [0, 255, 255], [0, 255, 178], [0, 255, 0], [178, 255, 0], [255, 255, 0], [255, 178, 0], [255, 0, 0]];
  const SPEICHER = 'wandschnitt-modell';
  const ROLLEN = [['innen', 'innen'], ['aussen', 'außen'], ['sonstige', 'sonstige']];
  const TOENUNG = { innen: 'rgba(229, 48, 9, .10)', aussen: 'rgba(0, 158, 227, .13)', sonstige: 'rgba(135, 147, 154, .16)' };
  const de = (v, n) => (Number.isFinite(v) ? v.toFixed(n).replace('.', ',').replace('-', '−') : '');
  const zahl = s => parseFloat(String(s).replace(',', '.'));
  const ganz = v => Math.round(v * 1000) / 1000;

  function el(tag, attrs, ...kinder) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      const v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === 'text') e.textContent = v;
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kinder.flat()) if (c !== null && c !== undefined && c !== false) e.append(c);
    return e;
  }

  function starten(wurzel) {
    const L = window.WandschnittLoeser, D = window.WandschnittDaten;
    let modell = null, erg = null, iso = null, vorlageId = '', geaendert = false;
    const opt = { baender: true, isolinien: true, netz: false, mass: 'aussen' };
    const ansicht = { s: 1, ox: 0, oy: 0, w: 0, h: 0 };
    let markiert = -1, zug = null, kanteUnter = null, druck = null;

    const stoffe = () => {
      const m = new Map(D.BIBLIOTHEK.map(s => [s.id, s]));
      for (const s of modell.eigeneStoffe) m.set(s.id, Object.assign({ eigen: true, gruppe: 'Eigene Materialien', quelle: 'eigener Wert', farbe: '#eadff0' }, s));
      return m;
    };
    const bereichVon = id => modell.bereiche.find(b => b.id === id);

    // ---------- Gerüst ----------
    const ui = {};
    ui.vorlage = el('select', { 'aria-label': 'Vorlage', onchange: () => vorlageLaden(ui.vorlage.value) },
      el('option', { value: '', text: 'Vorlage wählen …' }), D.VORLAGEN.map(v => el('option', { value: v.id, text: v.titel })));
    ui.meldung = el('span', { class: 'ws-meldung', 'aria-live': 'polite' });
    ui.datei = el('input', { type: 'file', accept: '.json,application/json', onchange: jsonLaden });
    ui.vorlagetext = el('div', { class: 'ws-vorlagetext' });
    ui.legende = el('div', { class: 'ws-legende', 'aria-label': 'Farblegende Temperatur' });
    ui.bild = el('canvas', { class: 'ws-bild', role: 'img', 'aria-label': 'Wandschnitt mit Temperaturfeld' });
    ui.status = el('div', { class: 'ws-status', 'aria-live': 'off' });
    ui.netz = el('input', { type: 'range', min: 5, max: 50, step: 5, 'aria-label': 'Netzweite', oninput: () => aendern(() => { modell.netz = +ui.netz.value; }) });
    ui.netzWert = el('output');
    ui.grenze = el('input', { type: 'number', step: 'any', 'aria-label': 'Grenzlinie in °C', onchange: () => aendern(() => { const v = zahl(ui.grenze.value); modell.grenze = Number.isFinite(v) ? v : null; }) });
    const schalter = (key, text) => el('label', {}, el('input', { type: 'checkbox', checked: opt[key], onchange: e => { opt[key] = e.target.checked; zeichnen(); } }), text);
    ui.ergebnisse = el('div', { class: 'ws-ergebnisse' });
    ui.rechtecke = el('tbody');
    ui.bereiche = el('tbody');
    ui.stoffe = el('tbody');

    wurzel.textContent = '';
    wurzel.append(
      el('div', { class: 'ws-leiste' },
        el('label', {}, 'Vorlage', ui.vorlage),
        el('button', { type: 'button', onclick: () => leerLaden() }, 'Leeres Modell'),
        el('button', { type: 'button', onclick: () => { einpassen(); zeichnen(); } }, 'Ansicht einpassen'),
        el('button', { type: 'button', onclick: linkKopieren }, 'Link kopieren'),
        el('button', { type: 'button', onclick: jsonSpeichern }, 'JSON speichern'),
        el('label', { class: 'ws-datei' }, 'JSON laden', ui.datei),
        ui.meldung),
      ui.vorlagetext,
      el('div', { class: 'ws-haupt' },
        el('div', { class: 'ws-bildspalte' },
          el('div', { class: 'ws-bildrahmen' }, ui.legende, ui.bild),
          ui.status,
          el('div', { class: 'ws-anzeige' },
            schalter('baender', 'Temperaturbänder'), schalter('isolinien', 'Isothermen'), schalter('netz', 'Netz'),
            el('label', {}, 'Grenzlinie', ui.grenze, '°C'),
            el('label', {}, 'Netzweite', ui.netz, ui.netzWert)),
          el('div', { class: 'ws-text',  class: 'ws-hinweis', text: 'Kanten im Bild ziehen: alle Kanten auf derselben Linie wandern mit, mit gedrückter Alt-Taste nur die Kante dieses Rechtecks, mit Umschalt in 10-mm-Schritten. Ein Klick ins Material setzt eine Sonde.' })),
        ui.ergebnisse),
      el('section', { class: 'ws-abschnitt' },
        el('div', { class: 'ws-abschnitt-titel', text: 'Rechtecke' }),
        el('div', { class: 'ws-tabelle' }, el('table', { class: 'ws-t' },
          el('thead', {}, el('tr', {}, ['Nr.', 'Art', 'Material oder Luftbereich', 'x von', 'x bis', 'y von', 'y bis', ''].map(t => el('th', { text: t })))),
          ui.rechtecke)),
        el('div', { class: 'ws-text',  class: 'ws-hinweis', text: 'Maße in mm. Spätere Rechtecke überdecken frühere. Materialkanten an einem Luftbereich bekommen dessen Konvektion, Kanten ins Leere sind adiabat (Schnittrand). Die Materialwerte sind vorläufig und werden noch gegen die Normen geprüft.' }),
        el('div', { class: 'ws-knoepfe' },
          el('button', { type: 'button', onclick: () => rechteckNeu('material') }, '+ Materialrechteck'),
          el('button', { type: 'button', onclick: () => rechteckNeu('luft') }, '+ Luftrechteck'))),
      el('section', { class: 'ws-abschnitt' },
        el('div', { class: 'ws-abschnitt-titel', text: 'Luftbereiche (Randbedingungen)' }),
        el('div', { class: 'ws-tabelle' }, el('table', { class: 'ws-t' },
          el('thead', {}, el('tr', {}, ['Name', 'Rolle', 'Lufttemperatur (Ambient Temperature) °C', 'Wärmeübergang', 'h (Film Coefficient) W/(m²·K)', 'R = 1/h m²·K/W', 'h → ∞', ''].map(t => el('th', { text: t })))),
          ui.bereiche)),
        el('div', { class: 'ws-text',  class: 'ws-hinweis', text: 'Rolle innen und außen braucht f_Rsi und ψ. h → ∞ heißt: die Oberfläche nimmt die Lufttemperatur an (feste Temperatur wie Fall a in P1).' }),
        el('div', { class: 'ws-knoepfe' }, el('button', { type: 'button', onclick: bereichNeu }, '+ Luftbereich'))),
      el('section', { class: 'ws-abschnitt' },
        el('div', { class: 'ws-abschnitt-titel', text: 'Eigene Materialien' }),
        el('div', { class: 'ws-tabelle' }, el('table', { class: 'ws-t' },
          el('thead', {}, el('tr', {}, ['Name', 'λ W/(m·K)', ''].map(t => el('th', { text: t })))),
          ui.stoffe)),
        el('div', { class: 'ws-knoepfe' }, el('button', { type: 'button', onclick: stoffNeu }, '+ Eigenes Material'))));

    // ---------- Modell ändern ----------
    function aendern(fn, tabellenNeu) {
      fn();
      geaendert = true;
      if (tabellenNeu) tabellen();
      rechnenSpaeter();
    }
    let geplant = false;
    function rechnenSpaeter() {
      if (geplant) return;
      geplant = true;
      requestAnimationFrame(() => { geplant = false; rechnenJetzt(); });
    }
    function rechnenJetzt() {
      erg = L.rechnen(modell, D.BIBLIOTHEK);
      iso = null;
      ui.netz.value = modell.netz;
      ui.netzWert.textContent = modell.netz + ' mm';
      if (document.activeElement !== ui.grenze) ui.grenze.value = modell.grenze === null ? '' : modell.grenze;
      zeichnen();
      ergebnisse();
      speichernSpaeter();
    }
    function setzen(m, id) {
      modell = D.normalisieren(m);
      vorlageId = id || '';
      geaendert = false;
      ui.vorlage.value = vorlageId;
      const v = D.VORLAGEN.find(x => x.id === vorlageId);
      ui.vorlagetext.textContent = v ? v.text : '';
      tabellen();
      einpassen();
      rechnenJetzt();
    }
    function vorlageLaden(id) {
      const v = D.VORLAGEN.find(x => x.id === id);
      if (!v) return;
      if (geaendert && !window.confirm('Das aktuelle Modell durch die Vorlage ersetzen? Ungespeicherte Änderungen gehen verloren.')) { ui.vorlage.value = vorlageId; return; }
      setzen(v.modell(), id);
    }
    function leerLaden() {
      if (geaendert && !window.confirm('Ein leeres Modell beginnen? Ungespeicherte Änderungen gehen verloren.')) return;
      setzen({ netz: 20, grenze: null, rechtecke: [], sonden: [], eigeneStoffe: [], bereiche: [
        { id: 'aussen', name: 'Außenluft', rolle: 'aussen', T: -5, h: 25, vorlage: 'rse004' },
        { id: 'raum', name: 'Raum', rolle: 'innen', T: 20, h: 1 / 0.13, vorlage: 'rsi013' }] }, '');
    }
    function rechteckNeu(art) {
      const b = huelle(), w = Math.max(50, Math.round((b.x1 - b.x0) / 5)), h = Math.max(50, Math.round((b.y1 - b.y0) / 5));
      const x0 = Math.round((b.x0 + b.x1) / 2 - w / 2), y0 = Math.round((b.y0 + b.y1) / 2 - h / 2);
      aendern(() => {
        modell.rechtecke.push(art === 'luft'
          ? { art, bereich: modell.bereiche[0] ? modell.bereiche[0].id : '', x0, x1: x0 + w, y0, y1: y0 + h }
          : { art: 'material', stoff: 'ks1800', x0, x1: x0 + w, y0, y1: y0 + h });
      }, true);
    }
    function bereichNeu() {
      let n = modell.bereiche.length + 1;
      while (bereichVon('b' + n)) n++;
      aendern(() => modell.bereiche.push({ id: 'b' + n, name: 'Bereich ' + n, rolle: 'sonstige', T: 20, h: 1 / 0.13, vorlage: 'rsi013', unendlich: false }), true);
    }
    function stoffNeu() {
      let n = modell.eigeneStoffe.length + 1;
      while (modell.eigeneStoffe.some(s => s.id === 'eigen' + n)) n++;
      aendern(() => modell.eigeneStoffe.push({ id: 'eigen' + n, name: 'Eigenes Material ' + n, lambda: 1 }), true);
    }

    // ---------- Tabellen ----------
    function tabellen() { tabelleRechtecke(); tabelleBereiche(); tabelleStoffe(); }

    function stoffAuswahl(r) {
      const gruppen = new Map();
      for (const s of stoffe().values()) {
        if (!gruppen.has(s.gruppe)) gruppen.set(s.gruppe, []);
        gruppen.get(s.gruppe).push(s);
      }
      const sel = el('select', { 'aria-label': 'Material' },
        Array.from(gruppen, ([g, liste]) => el('optgroup', { label: g }, liste.map(s => el('option', { value: s.id, text: `${s.name} (λ ${de(s.lambda, s.lambda < 0.1 ? 3 : 2)})` })))));
      sel.value = r.stoff;
      const s = stoffe().get(r.stoff);
      sel.title = s ? `λ = ${de(s.lambda, 3)} W/(m·K), Quelle: ${s.quelle}` : '';
      sel.addEventListener('change', () => aendern(() => { r.stoff = sel.value; }, true));
      return sel;
    }
    function bereichAuswahl(r) {
      const sel = el('select', { 'aria-label': 'Luftbereich' }, modell.bereiche.map(b => el('option', { value: b.id, text: b.name })));
      sel.value = r.bereich;
      sel.addEventListener('change', () => aendern(() => { r.bereich = sel.value; }));
      return sel;
    }
    function tabelleRechtecke() {
      ui.rechtecke.textContent = '';
      modell.rechtecke.forEach((r, k) => {
        const art = el('select', { 'aria-label': `Rechteck ${k + 1}: Art` },
          el('option', { value: 'material', text: 'Material' }), el('option', { value: 'luft', text: 'Luftbereich' }));
        art.value = r.art;
        art.addEventListener('change', () => aendern(() => {
          if (art.value === 'luft') { r.art = 'luft'; delete r.stoff; r.bereich = modell.bereiche[0] ? modell.bereiche[0].id : ''; }
          else { r.art = 'material'; delete r.bereich; r.stoff = 'ks1800'; }
        }, true));
        const koord = ['x0', 'x1', 'y0', 'y1'].map(f => {
          const inp = el('input', { type: 'number', step: 'any', value: ganz(r[f]), 'data-k': k, 'data-f': f, 'aria-label': `Rechteck ${k + 1}: ${f}` });
          inp.addEventListener('change', () => aendern(() => {
            const v = zahl(inp.value);
            if (Number.isFinite(v)) r[f] = v;
            if (r.x0 > r.x1) [r.x0, r.x1] = [r.x1, r.x0];
            if (r.y0 > r.y1) [r.y0, r.y1] = [r.y1, r.y0];
          }, true));
          return el('td', {}, inp);
        });
        const knopf = (text, titel, fn) => el('button', { type: 'button', class: 'ws-klein', title: titel, 'aria-label': titel, onclick: fn }, text);
        const tr = el('tr', { class: k === markiert ? 'ws-markiert' : null },
          el('td', { class: 'ws-nr', text: k + 1 }), el('td', {}, art),
          el('td', {}, r.art === 'luft' ? bereichAuswahl(r) : stoffAuswahl(r)),
          koord,
          el('td', {},
            knopf('↑', `Rechteck ${k + 1} nach vorn (wird früher gezeichnet)`, () => aendern(() => tauschen(k, k - 1), true)),
            knopf('↓', `Rechteck ${k + 1} nach hinten (überdeckt mehr)`, () => aendern(() => tauschen(k, k + 1), true)),
            knopf('✕', `Rechteck ${k + 1} löschen`, () => aendern(() => modell.rechtecke.splice(k, 1), true))));
        tr.addEventListener('mouseenter', () => { markiert = k; zeichnen(); });
        tr.addEventListener('mouseleave', () => { markiert = -1; zeichnen(); });
        ui.rechtecke.append(tr);
      });
    }
    function tauschen(a, b) {
      const r = modell.rechtecke;
      if (b < 0 || b >= r.length) return;
      [r[a], r[b]] = [r[b], r[a]];
    }
    function tabelleBereiche() {
      ui.bereiche.textContent = '';
      const benutzt = new Set(modell.rechtecke.filter(r => r.art === 'luft').map(r => r.bereich));
      for (const b of modell.bereiche) {
        const name = el('input', { type: 'text', value: b.name, 'aria-label': 'Name des Luftbereichs', size: 12 });
        name.addEventListener('change', () => aendern(() => { b.name = name.value.trim() || b.name; }, true));
        const rolle = el('select', { 'aria-label': 'Rolle' }, ROLLEN.map(([v, t]) => el('option', { value: v, text: t })));
        rolle.value = b.rolle;
        rolle.addEventListener('change', () => aendern(() => { b.rolle = rolle.value; }));
        const T = el('input', { type: 'number', step: 'any', value: b.T, 'aria-label': 'Lufttemperatur in °C' });
        T.addEventListener('change', () => aendern(() => { const v = zahl(T.value); if (Number.isFinite(v)) b.T = v; }));
        const vorlage = el('select', { 'aria-label': 'Wärmeübergang' },
          D.NORMWERTE.map(n => el('option', { value: n.id, text: n.name, title: n.quelle })), el('option', { value: 'frei', text: 'eigener Wert' }));
        vorlage.value = D.NORMWERTE.some(n => n.id === b.vorlage) ? b.vorlage : 'frei';
        vorlage.addEventListener('change', () => aendern(() => {
          b.vorlage = vorlage.value;
          const n = D.NORMWERTE.find(x => x.id === b.vorlage);
          if (n) b.h = 1 / n.R;
        }, true));
        const h = el('input', { type: 'number', step: 'any', min: 0, value: ganz(b.h), disabled: b.vorlage !== 'frei' || b.unendlich, 'aria-label': 'h in W/(m²·K)' });
        h.addEventListener('change', () => aendern(() => { const v = zahl(h.value); if (v > 0) b.h = v; }, true));
        const unendlich = el('input', { type: 'checkbox', checked: b.unendlich, 'aria-label': 'h unendlich' });
        unendlich.addEventListener('change', () => aendern(() => { b.unendlich = unendlich.checked; }, true));
        const loeschen = benutzt.has(b.id) ? el('small', { text: 'in Benutzung' })
          : el('button', { type: 'button', class: 'ws-klein', 'aria-label': `Luftbereich ${b.name} löschen`, onclick: () => aendern(() => modell.bereiche.splice(modell.bereiche.indexOf(b), 1), true) }, '✕');
        ui.bereiche.append(el('tr', {},
          el('td', {}, name), el('td', {}, rolle), el('td', {}, T), el('td', {}, vorlage), el('td', {}, h),
          el('td', { text: b.unendlich ? '0' : de(1 / b.h, 3) }), el('td', {}, unendlich), el('td', {}, loeschen)));
      }
    }
    function tabelleStoffe() {
      ui.stoffe.textContent = '';
      const benutzt = new Set(modell.rechtecke.filter(r => r.art !== 'luft').map(r => r.stoff));
      if (!modell.eigeneStoffe.length) ui.stoffe.append(el('tr', {}, el('td', { colspan: 3, text: 'Noch keine eigenen Materialien.' })));
      for (const s of modell.eigeneStoffe) {
        const name = el('input', { type: 'text', value: s.name, size: 24, 'aria-label': 'Name des Materials' });
        name.addEventListener('change', () => aendern(() => { s.name = name.value.trim() || s.name; }, true));
        const lam = el('input', { type: 'number', step: 'any', min: 0, value: s.lambda, 'aria-label': 'λ in W/(m·K)' });
        lam.addEventListener('change', () => aendern(() => { const v = zahl(lam.value); if (v > 0) s.lambda = v; }, true));
        const loeschen = benutzt.has(s.id) ? el('small', { text: 'in Benutzung' })
          : el('button', { type: 'button', class: 'ws-klein', 'aria-label': `${s.name} löschen`, onclick: () => aendern(() => modell.eigeneStoffe.splice(modell.eigeneStoffe.indexOf(s), 1), true) }, '✕');
        ui.stoffe.append(el('tr', {}, el('td', {}, name), el('td', {}, lam), el('td', {}, loeschen)));
      }
    }
    // Während des Ziehens nur die Zahlen in der Rechtecktabelle nachführen
    function koordinatenNachfuehren() {
      for (const inp of ui.rechtecke.querySelectorAll('input[data-f]')) {
        const r = modell.rechtecke[+inp.dataset.k];
        if (r) inp.value = ganz(r[inp.dataset.f]);
      }
    }

    // ---------- Ansicht ----------
    function huelle() {
      const r = modell.rechtecke;
      if (!r.length) return { x0: 0, x1: 1000, y0: 0, y1: 1000 };
      return { x0: Math.min(...r.map(q => q.x0)), x1: Math.max(...r.map(q => q.x1)), y0: Math.min(...r.map(q => q.y0)), y1: Math.max(...r.map(q => q.y1)) };
    }
    function einpassen() {
      const b = huelle(), bw = Math.max(1, b.x1 - b.x0), bh = Math.max(1, b.y1 - b.y0);
      const w = Math.max(240, ui.bild.clientWidth || 600);
      const hoechstens = Math.max(320, Math.min(760, (window.innerHeight || 900) * 0.78));
      const h = Math.round(Math.min(Math.max(w * bh / bw, 320), hoechstens));
      ui.bild.style.height = h + 'px';
      const rand = 22;
      ansicht.w = w; ansicht.h = h;
      ansicht.s = Math.min((w - 2 * rand) / bw, (h - 2 * rand) / bh);
      ansicht.ox = (w - ansicht.s * bw) / 2 - ansicht.s * b.x0;
      ansicht.oy = (h + ansicht.s * bh) / 2 + ansicht.s * b.y0;
    }
    const X = x => ansicht.ox + x * ansicht.s, Y = y => ansicht.oy - y * ansicht.s;
    const invX = px => (px - ansicht.ox) / ansicht.s, invY = py => (ansicht.oy - py) / ansicht.s;
    const farbeVar = (name, ersatz) => getComputedStyle(wurzel).getPropertyValue(name).trim() || ersatz;

    function bandVon(T) {
      if (!(erg.tMax > erg.tMin)) return 4;
      return Math.max(0, Math.min(8, Math.floor((T - erg.tMin) / (erg.tMax - erg.tMin) * 9)));
    }

    // Feld in Bildschirmauflösung: jede Pixelmitte bilinear aus den Knoten, Farbe nach Band oder Material
    function feldBild() {
      const w = Math.round(ansicht.w), h = Math.round(ansicht.h);
      const c = document.createElement('canvas');
      c.width = w; c.height = h;
      const g = c.getContext('2d'), img = g.createImageData(w, h), px = img.data;
      const { xs, ys, NX, EX, art, T, stoffDer, stoffListe } = erg;
      const ci = new Int32Array(w), cf = new Float64Array(w);
      for (let p = 0; p < w; p++) {
        const x = invX(p + 0.5), i = L.zelleBei(xs, x);
        ci[p] = i;
        cf[p] = i < 0 ? 0 : (x - xs[i]) / (xs[i + 1] - xs[i]);
      }
      const farben = stoffListe.map(s => {
        const f = (s.farbe || '#dddddd').replace('#', '');
        return [parseInt(f.slice(0, 2), 16), parseInt(f.slice(2, 4), 16), parseInt(f.slice(4, 6), 16)];
      });
      for (let q = 0; q < h; q++) {
        const y = invY(q + 0.5), j = L.zelleBei(ys, y);
        if (j < 0) continue;
        const fy = (y - ys[j]) / (ys[j + 1] - ys[j]);
        for (let p = 0; p < w; p++) {
          const i = ci[p];
          if (i < 0 || art[i + j * EX] !== 1) continue;
          let rgb;
          if (opt.baender) {
            const k = i + j * NX, fx = cf[p];
            const t = (1 - fy) * ((1 - fx) * T[k] + fx * T[k + 1]) + fy * ((1 - fx) * T[k + NX] + fx * T[k + NX + 1]);
            rgb = BAENDER[bandVon(t)];
          } else rgb = farben[stoffDer[i + j * EX]];
          const o = 4 * (q * w + p);
          px[o] = rgb[0]; px[o + 1] = rgb[1]; px[o + 2] = rgb[2]; px[o + 3] = 255;
        }
      }
      g.putImageData(img, 0, 0);
      return c;
    }

    function isolinienHolen() {
      if (iso) return iso;
      iso = { stufen: [], grenze: null };
      if (erg.tMax > erg.tMin) {
        for (let k = 1; k < 9; k++) {
          const w = erg.tMin + k * (erg.tMax - erg.tMin) / 9;
          iso.stufen.push({ w, seg: L.isolinie(erg, w) });
        }
      }
      if (modell.grenze !== null && modell.grenze > erg.tMin && modell.grenze < erg.tMax) iso.grenze = { w: modell.grenze, seg: L.isolinie(erg, modell.grenze) };
      return iso;
    }

    // Beschriftung einer Linie an der Strecke nahe ihrem Schwerpunkt, ohne andere Beschriftungen zu überdecken
    function beschriften(g, seg, text, belegt, farbe) {
      if (!seg.length) return;
      let sx = 0, sy = 0;
      for (const s of seg) { sx += s[0] + s[2]; sy += s[1] + s[3]; }
      sx /= 2 * seg.length; sy /= 2 * seg.length;
      const kandidaten = seg.map(s => [(s[0] + s[2]) / 2, (s[1] + s[3]) / 2]).sort((a, b) => Math.hypot(a[0] - sx, a[1] - sy) - Math.hypot(b[0] - sx, b[1] - sy));
      for (const [mx, my] of kandidaten.slice(0, 60)) {
        const px = X(mx), py = Y(my);
        if (px < 30 || py < 12 || px > ansicht.w - 30 || py > ansicht.h - 12) continue;
        if (belegt.some(([bx, by]) => Math.abs(bx - px) < 58 && Math.abs(by - py) < 16)) continue;
        belegt.push([px, py]);
        g.font = '600 11px "Source Sans Pro", Arial, sans-serif';
        g.textAlign = 'center'; g.textBaseline = 'middle';
        g.lineWidth = 3; g.strokeStyle = 'rgba(255, 255, 255, .9)'; g.strokeText(text, px, py);
        g.fillStyle = farbe; g.fillText(text, px, py);
        return;
      }
    }

    function zeichnen() {
      if (!modell) return;
      const dpr = Math.min(2, window.devicePixelRatio || 1), b = ui.bild;
      const w = Math.round(ansicht.w), h = Math.round(ansicht.h);
      if (b.width !== Math.round(w * dpr) || b.height !== Math.round(h * dpr)) { b.width = Math.round(w * dpr); b.height = Math.round(h * dpr); }
      const g = b.getContext('2d');
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, w, h);
      const text2 = farbeVar('--kurs-text-2', '#566166');
      const akzent = farbeVar('--kurs-accent', '#009ee3'), warn = farbeVar('--kurs-c-warn', '#e53009');

      // Luftbereiche in Listenreihenfolge, darüber das Feld (dort, wo Material ist)
      for (const r of modell.rechtecke) {
        if (r.art !== 'luft') continue;
        const z = bereichVon(r.bereich);
        g.fillStyle = TOENUNG[z ? z.rolle : 'sonstige'];
        g.fillRect(X(r.x0), Y(r.y1), (r.x1 - r.x0) * ansicht.s, (r.y1 - r.y0) * ansicht.s);
      }
      if (erg && erg.ok) {
        g.imageSmoothingEnabled = false;
        g.drawImage(feldBild(), 0, 0, w, h);
        materialgrenzen(g);
        if (opt.netz) netzZeichnen(g);
        if (opt.isolinien && opt.baender) {
          const I = isolinienHolen(), belegt = [];
          g.lineWidth = 1; g.strokeStyle = 'rgba(0, 0, 0, .55)';
          for (const st of I.stufen) strecken(g, st.seg);
          if (I.grenze) { g.lineWidth = 2.4; g.strokeStyle = warn; g.setLineDash([7, 4]); strecken(g, I.grenze.seg); g.setLineDash([]); }
          if (I.grenze) beschriften(g, I.grenze.seg, de(I.grenze.w, 1) + ' °C', belegt, warn);
          for (const st of I.stufen) beschriften(g, st.seg, de(st.w, Math.abs(erg.tMax - erg.tMin) < 10 ? 2 : 1), belegt, '#1b2327');
        }
        markenZeichnen(g);
      } else {
        // Ohne Rechnung (Fehler im Modell) wenigstens die Materialrechtecke zeigen
        const st = stoffe();
        for (const r of modell.rechtecke) {
          if (r.art === 'luft') continue;
          g.fillStyle = (st.get(r.stoff) || {}).farbe || '#dddddd';
          g.fillRect(X(r.x0), Y(r.y1), (r.x1 - r.x0) * ansicht.s, (r.y1 - r.y0) * ansicht.s);
          g.lineWidth = 1; g.strokeStyle = 'rgba(20, 28, 32, .8)';
          g.strokeRect(X(r.x0), Y(r.y1), (r.x1 - r.x0) * ansicht.s, (r.y1 - r.y0) * ansicht.s);
        }
      }
      bereichsnamen(g, text2);
      if (markiert >= 0 && modell.rechtecke[markiert]) {
        const r = modell.rechtecke[markiert];
        g.lineWidth = 2; g.strokeStyle = akzent; g.setLineDash([5, 3]);
        g.strokeRect(X(r.x0), Y(r.y1), (r.x1 - r.x0) * ansicht.s, (r.y1 - r.y0) * ansicht.s);
        g.setLineDash([]);
      }
      const kante = zug || kanteUnter;
      if (kante) kanteZeichnen(g, kante, akzent);
      legende();
    }
    function strecken(g, seg) {
      g.beginPath();
      for (const s of seg) { g.moveTo(X(s[0]), Y(s[1])); g.lineTo(X(s[2]), Y(s[3])); }
      g.stroke();
    }
    // Grenzen zwischen verschiedenen Materialien und zum Luftbereich, aus den Rasterzellen
    function materialgrenzen(g) {
      const { xs, ys, EX, EY, art, stoffDer, bereichDer } = erg;
      const sorte = (i, j) => (i < 0 || j < 0 || i >= EX || j >= EY ? -2 : art[i + j * EX] === 1 ? stoffDer[i + j * EX] : art[i + j * EX] === 2 ? -10 - bereichDer[i + j * EX] : -1);
      g.beginPath();
      for (let j = 0; j < EY; j++) for (let i = 0; i <= EX; i++) {
        const a = sorte(i - 1, j), c = sorte(i, j);
        if (a !== c && (a >= 0 || c >= 0)) { g.moveTo(X(xs[i]), Y(ys[j])); g.lineTo(X(xs[i]), Y(ys[j + 1])); }
      }
      for (let i = 0; i < EX; i++) for (let j = 0; j <= EY; j++) {
        const a = sorte(i, j - 1), c = sorte(i, j);
        if (a !== c && (a >= 0 || c >= 0)) { g.moveTo(X(xs[i]), Y(ys[j])); g.lineTo(X(xs[i + 1]), Y(ys[j])); }
      }
      g.lineWidth = 1.2; g.strokeStyle = 'rgba(20, 28, 32, .8)'; g.stroke();
    }
    function netzZeichnen(g) {
      const { xs, ys, EX, EY, art } = erg;
      g.beginPath();
      for (let j = 0; j < EY; j++) for (let i = 0; i < EX; i++) {
        if (art[i + j * EX] !== 1) continue;
        g.rect(X(xs[i]), Y(ys[j + 1]), (xs[i + 1] - xs[i]) * ansicht.s, (ys[j + 1] - ys[j]) * ansicht.s);
      }
      g.lineWidth = 0.5; g.strokeStyle = 'rgba(0, 0, 0, .35)'; g.stroke();
    }
    function marke(g, x, y, text, farbe, rechts) {
      const px = X(x), py = Y(y);
      g.beginPath(); g.arc(px, py, 4.5, 0, 2 * Math.PI);
      g.fillStyle = farbe; g.fill(); g.lineWidth = 2; g.strokeStyle = '#ffffff'; g.stroke();
      g.font = '600 12px "Source Sans Pro", Arial, sans-serif';
      g.textBaseline = 'middle';
      const tw = g.measureText(text).width, links = rechts === false || px + 10 + tw > ansicht.w - 4;
      g.textAlign = links ? 'right' : 'left';
      const tx = links ? px - 9 : px + 9, ty = py - 11;
      g.lineWidth = 3.5; g.strokeStyle = 'rgba(255, 255, 255, .92)'; g.strokeText(text, tx, ty);
      g.fillStyle = '#1b2327'; g.fillText(text, tx, ty);
    }
    function markenZeichnen(g) {
      for (const z of erg.auswertung) {
        if (z.rolle === 'innen' && z.ortMin) marke(g, z.ortMin[0], z.ortMin[1], `${z.name} min ${de(z.tMin, 2)} °C`, '#0b4f9c');
      }
      modell.sonden.forEach(s => {
        const p = L.sonde(erg, s.x, s.y);
        marke(g, s.x, s.y, p ? `${s.name}: ${de(p.T, 2)} °C` : `${s.name}: kein Material`, '#1b2327');
      });
    }
    function bereichsnamen(g, farbe) {
      const groesste = new Map();
      for (const r of modell.rechtecke) {
        if (r.art !== 'luft') continue;
        const f = (r.x1 - r.x0) * (r.y1 - r.y0);
        if (!groesste.has(r.bereich) || f > groesste.get(r.bereich).f) groesste.set(r.bereich, { r, f });
      }
      g.font = '600 12px "Source Sans Pro", Arial, sans-serif';
      g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = farbe;
      for (const [id, { r }] of groesste) {
        const z = bereichVon(id);
        if (!z) continue;
        const pw = (r.x1 - r.x0) * ansicht.s, ph = (r.y1 - r.y0) * ansicht.s;
        if (pw < 70 || ph < 18) continue;
        g.fillText(`${z.name} ${de(z.T, 1)} °C`, X((r.x0 + r.x1) / 2), Y((r.y0 + r.y1) / 2));
      }
    }
    function kanteZeichnen(g, k, farbe) {
      g.lineWidth = 3; g.strokeStyle = farbe;
      g.beginPath();
      for (const { r, key } of k.ziele) {
        if (k.achse === 'x') { g.moveTo(X(r[key]), Y(r.y0)); g.lineTo(X(r[key]), Y(r.y1)); }
        else { g.moveTo(X(r.x0), Y(r[key])); g.lineTo(X(r.x1), Y(r[key])); }
      }
      g.stroke();
      if (zug) {
        const r = k.ziele[0].r, wert = r[k.ziele[0].key];
        const px = k.achse === 'x' ? X(wert) + 6 : X((r.x0 + r.x1) / 2), py = k.achse === 'x' ? Y((r.y0 + r.y1) / 2) : Y(wert) - 10;
        g.font = '700 12px "Source Sans Pro", Arial, sans-serif'; g.textAlign = 'left'; g.textBaseline = 'middle';
        const t = `${k.achse} = ${de(wert, 0)} mm`;
        g.lineWidth = 3.5; g.strokeStyle = 'rgba(255, 255, 255, .92)'; g.strokeText(t, px, py);
        g.fillStyle = farbe; g.fillText(t, px, py);
      }
    }
    function legende() {
      ui.legende.textContent = '';
      if (!erg || !erg.ok || !opt.baender) return;
      const n = Math.abs(erg.tMax - erg.tMin) < 10 ? 2 : 1;
      ui.legende.append(el('b', { text: '°C' }));
      for (let k = 8; k >= 0; k--) {
        const oben = erg.tMin + (k + 1) * (erg.tMax - erg.tMin) / 9;
        ui.legende.append(el('div', {},
          el('span', { style: `background: rgb(${BAENDER[k].join(',')})` }),
          el('span', { text: k === 8 ? `${de(oben, n)} Max` : de(oben, n) })));
      }
      ui.legende.append(el('div', {}, el('span', {}), el('span', { text: `${de(erg.tMin, n)} Min` })));
    }

    // ---------- Ergebnisse ----------
    function ergebnisse() {
      const E = ui.ergebnisse;
      E.textContent = '';
      if (!erg.ok) { E.append(el('div', { class: 'ws-fehler' }, erg.fehler.map(f => el('div', { text: f })))); ui.status.textContent = ''; return; }
      const karte = (titel, ...inhalt) => el('div', { class: 'ws-karte' }, el('div', { class: 'ws-kartentitel', text: titel }), inhalt);
      const frsiVon = id => erg.frsi.find(f => f.id === id);

      E.append(karte('Oberflächentemperaturen',
        el('table', { class: 'ws-t' }, el('tr', {}, ['Luftbereich', 'min °C', 'max °C', 'f_Rsi'].map(t => el('th', { text: t }))),
          erg.auswertung.map(z => {
            const f = frsiVon(z.id);
            return el('tr', {}, el('td', { text: `${z.name} (${ROLLEN.find(r => r[0] === z.rolle)[1]})` }), el('td', { text: de(z.tMin, 2) }), el('td', { text: de(z.tMax, 2) }),
              el('td', {}, f ? el('span', { class: f.wert >= 0.7 ? 'ws-ok' : 'ws-warn', title: f.wert >= 0.7 ? 'Mindestwert 0,70 eingehalten' : 'unter 0,70: Schimmelgefahr' }, de(f.wert, 3)) : ''));
          })),
        el('div', { class: 'ws-text',  text: 'f_Rsi = (θsi,min − θe)/(θi − θe), Mindestwert 0,70 nach DIN 4108-2 mit R_si 0,25.' })));

      E.append(karte('Wärmeströme je Meter Bauteiltiefe',
        el('table', { class: 'ws-t' }, el('tr', {}, el('th', { text: 'Luftbereich' }), el('th', { text: 'W/m' })),
          erg.auswertung.map(z => el('tr', {}, el('td', { text: z.name }), el('td', { text: de(z.strom, 3) }))),
          el('tr', {}, el('td', { text: 'Bilanz' }), el('td', { text: de(Math.abs(erg.bilanz) < 1e-9 ? 0 : erg.bilanz, 3) }))),
        el('div', { class: 'ws-text',  text: 'Positiv: Wärme strömt aus dem Luftbereich in das Bauteil (wie Reaction Probe in ANSYS).' })));

      const p = erg.psi;
      if (p.fehler) E.append(karte('ψ-Wert nach DIN EN ISO 10211', el('div', { class: 'ws-text',  text: p.fehler })));
      else {
        const key = opt.mass === 'aussen' ? 'lAussen' : 'lInnen';
        const summe = p.elemente.reduce((s, e) => s + e.U * e[key] / 1000, 0), psi = p.L2D - summe;
        const umschalter = el('div', { class: 'ws-umschalter', role: 'group', 'aria-label': 'Maßbezug' },
          [['aussen', 'Außenmaß'], ['innen', 'Innenmaß']].map(([v, t]) => el('button', { type: 'button', class: 'ws-klein', 'aria-pressed': String(opt.mass === v), onclick: () => { opt.mass = v; ergebnisse(); } }, t)));
        const kurz = s => s.name.replace(/,? (WLS|\d).*$/, '').replace(/ \(.*\)$/, '');
        const innenNicht013 = modell.bereiche.some(b => b.rolle === 'innen' && b.vorlage !== 'rsi013');
        E.append(karte('ψ-Wert nach DIN EN ISO 10211', umschalter,
          el('div', { class: 'ws-text',  text: `L2D = Φ/(θi − θe) = ${de(p.phi, 3)} W/m / ${de(p.Ti - p.Te, 1)} K = ${de(p.L2D, 4)} W/(m·K)` }),
          el('table', { class: 'ws-t' }, el('tr', {}, ['Schnitt', 'U W/(m²·K)', 'l mm', 'U·l W/(m·K)'].map(t => el('th', { text: t }))),
            p.elemente.map(e => el('tr', { title: 'Aufbau von außen: ' + e.schichten.map(s => `${kurz(s)} ${de(s.d, 0)} mm`).join(', ') },
              el('td', { text: e.lage }), el('td', { text: de(e.U, 4) }), el('td', { text: de(e[key], 0) }), el('td', { text: de(e.U * e[key] / 1000, 4) })))),
          el('div', { class: 'ws-text', }, 'ψ = L2D − Σ U·l = ', el('span', { class: 'ws-gross', text: `${de(psi, 3)} W/(m·K)` })),
          el('div', { class: 'ws-text',  text: 'Aufbau je Schnitt: Maus über die Zeile halten.' + (innenNicht013 ? ' Hinweis: Für ψ nach Norm innen R_si 0,13 wählen, die eingestellten Werte gelten für L2D und U.' : '') })));
      }

      if (modell.sonden.length) {
        E.append(karte('Sonden', el('table', { class: 'ws-t' },
          el('tr', {}, ['Name', 'T °C', 'q W/m²', ''].map(t => el('th', { text: t }))),
          modell.sonden.map((s, k) => {
            const w = L.sonde(erg, s.x, s.y);
            const name = el('input', { type: 'text', value: s.name, size: 14, 'aria-label': 'Name der Sonde' });
            name.addEventListener('change', () => aendern(() => { s.name = name.value.trim() || s.name; }));
            return el('tr', { title: `x = ${de(s.x, 0)} mm, y = ${de(s.y, 0)} mm` }, el('td', {}, name), el('td', { text: w ? de(w.T, 3) : '' }), el('td', { text: w ? de(w.q, 2) : '' }),
              el('td', {}, el('button', { type: 'button', class: 'ws-klein', 'aria-label': `Sonde ${s.name} löschen`, onclick: () => aendern(() => modell.sonden.splice(k, 1)) }, '✕')));
          }))));
      }
      ui.status.dataset.rechnung = `${erg.knoten.toLocaleString('de-DE')} Knoten, ${de(erg.ms.gesamt, 0)} ms`;
      if (!ui.status.dataset.zeiger) ui.status.textContent = ui.status.dataset.rechnung;
    }

    // ---------- Ziehen, Sonden, Anzeige unter dem Zeiger ----------
    function kanteBei(px, py) {
      let best = null, bd = 7;
      modell.rechtecke.forEach((r, k) => {
        for (const key of ['x0', 'x1']) {
          const d = Math.abs(px - X(r[key]));
          if (d < bd && py >= Y(r.y1) - 6 && py <= Y(r.y0) + 6) { bd = d; best = { k, key, achse: 'x' }; }
        }
        for (const key of ['y0', 'y1']) {
          const d = Math.abs(py - Y(r[key]));
          if (d < bd && px >= X(r.x0) - 6 && px <= X(r.x1) + 6) { bd = d; best = { k, key, achse: 'y' }; }
        }
      });
      return best;
    }
    function zieleVon(treffer, nurDieses) {
      const r0 = modell.rechtecke[treffer.k], wert = r0[treffer.key];
      const keys = treffer.achse === 'x' ? ['x0', 'x1'] : ['y0', 'y1'];
      const ziele = nurDieses ? [{ r: r0, key: treffer.key }]
        : modell.rechtecke.flatMap(r => keys.filter(key => Math.abs(r[key] - wert) < 1e-6).map(key => ({ r, key })));
      let lo = -Infinity, hi = Infinity;
      for (const { r, key } of ziele) {
        if (key === 'x0') hi = Math.min(hi, r.x1 - 1);
        if (key === 'x1') lo = Math.max(lo, r.x0 + 1);
        if (key === 'y0') hi = Math.min(hi, r.y1 - 1);
        if (key === 'y1') lo = Math.max(lo, r.y0 + 1);
      }
      return { achse: treffer.achse, ziele, lo, hi };
    }
    const zeiger = ev => { const r = ui.bild.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top]; };

    ui.bild.addEventListener('pointerdown', ev => {
      if (!modell) return;
      const [px, py] = zeiger(ev);
      druck = { px, py, bewegt: false };
      const t = kanteBei(px, py);
      if (t) {
        zug = zieleVon(t, ev.altKey);
        ui.bild.setPointerCapture(ev.pointerId);
        ev.preventDefault();
      }
    });
    ui.bild.addEventListener('pointermove', ev => {
      if (!modell) return;
      const [px, py] = zeiger(ev);
      if (druck && Math.hypot(px - druck.px, py - druck.py) > 4) druck.bewegt = true;
      if (zug) {
        const roh = zug.achse === 'x' ? invX(px) : invY(py), raster = ev.shiftKey ? 10 : 1;
        const v = Math.min(zug.hi, Math.max(zug.lo, Math.round(roh / raster) * raster));
        if (zug.ziele.some(({ r, key }) => r[key] !== v)) {
          for (const z of zug.ziele) z.r[z.key] = v;
          geaendert = true;
          koordinatenNachfuehren();
          rechnenSpaeter();
        }
        return;
      }
      const t = kanteBei(px, py);
      const neu = t ? zieleVon(t, ev.altKey) : null;
      if (JSON.stringify(neu && neu.ziele.map(z => [modell.rechtecke.indexOf(z.r), z.key])) !== JSON.stringify(kanteUnter && kanteUnter.ziele.map(z => [modell.rechtecke.indexOf(z.r), z.key]))) {
        kanteUnter = neu;
        zeichnen();
      }
      ui.bild.style.cursor = t ? (t.achse === 'x' ? 'ew-resize' : 'ns-resize') : 'crosshair';
      zeigerStatus(invX(px), invY(py));
    });
    const loslassen = ev => {
      if (zug) {
        zug = null;
        tabellen();
        rechnenSpaeter();
      } else if (druck && !druck.bewegt && erg && erg.ok && ev.type === 'pointerup') {
        const x = Math.round(invX(druck.px)), y = Math.round(invY(druck.py));
        if (L.sonde(erg, x, y)) aendern(() => modell.sonden.push({ name: 'S' + (modell.sonden.length + 1), x, y }));
      }
      druck = null;
    };
    ui.bild.addEventListener('pointerup', loslassen);
    ui.bild.addEventListener('pointercancel', loslassen);
    ui.bild.addEventListener('pointerleave', () => {
      if (!zug && kanteUnter) { kanteUnter = null; zeichnen(); }
      delete ui.status.dataset.zeiger;
      ui.status.textContent = ui.status.dataset.rechnung || '';
    });
    function zeigerStatus(x, y) {
      if (!erg || !erg.ok) return;
      const teile = [`x ${de(x, 0)} mm, y ${de(y, 0)} mm`];
      const s = L.sonde(erg, x, y);
      if (s) teile.push(`${de(s.T, 2)} °C`, `q ${de(s.q, 1)} W/m²`, s.stoff.name);
      else {
        const i = L.zelleBei(erg.xs, x), j = L.zelleBei(erg.ys, y);
        if (i >= 0 && j >= 0 && erg.art[i + j * erg.EX] === 2) {
          const z = erg.bereiche[erg.bereichDer[i + j * erg.EX]];
          teile.push(`${z.name}, Luft ${de(z.T, 1)} °C`);
        }
      }
      ui.status.dataset.zeiger = '1';
      ui.status.textContent = teile.join(' · ') + ' · ' + (ui.status.dataset.rechnung || '');
    }

    // ---------- Speichern und Laden ----------
    let speichernZeit = 0;
    function speichernSpaeter() {
      clearTimeout(speichernZeit);
      speichernZeit = setTimeout(() => {
        try { localStorage.setItem(SPEICHER, JSON.stringify({ modell, vorlageId })); } catch (e) { /* Speicher gesperrt: dann eben nicht */ }
      }, 400);
    }
    function melden(text) {
      ui.meldung.textContent = text;
      clearTimeout(melden.zeit);
      melden.zeit = setTimeout(() => { ui.meldung.textContent = ''; }, 4000);
    }
    async function linkKopieren() {
      const code = await D.kodieren(modell);
      const url = location.origin + location.pathname + '#modell=' + code;
      history.replaceState(null, '', url);
      try { await navigator.clipboard.writeText(url); melden('Link kopiert'); }
      catch (e) { window.prompt('Link zum Modell (kopieren mit Strg+C bzw. Cmd+C):', url); }
    }
    function jsonSpeichern() {
      const blob = new Blob([JSON.stringify(modell, null, 2)], { type: 'application/json' });
      const a = el('a', { href: URL.createObjectURL(blob), download: 'wandschnitt.json' });
      document.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    }
    function jsonLaden() {
      const f = ui.datei.files && ui.datei.files[0];
      if (!f) return;
      f.text().then(t => { setzen(JSON.parse(t), ''); geaendert = true; melden('Modell geladen'); })
        .catch(() => melden('Die Datei ist kein gültiges Modell.'))
        .finally(() => { ui.datei.value = ''; });
    }
    async function ausAdresse() {
      const h = location.hash;
      if (h.startsWith('#modell=')) {
        try { setzen(await D.dekodieren(h.slice(8)), ''); geaendert = true; return true; } catch (e) { melden('Der Link enthält kein gültiges Modell.'); }
      }
      if (h.startsWith('#vorlage=')) {
        const v = D.VORLAGEN.find(x => x.id === h.slice(9));
        if (v) { setzen(v.modell(), v.id); return true; }
      }
      return false;
    }

    // ---------- Start ----------
    (async () => {
      if (await ausAdresse()) return;
      try {
        const g = JSON.parse(localStorage.getItem(SPEICHER) || 'null');
        if (g && g.modell) { setzen(g.modell, g.vorlageId); return; }
      } catch (e) { /* kein gespeichertes Modell */ }
      setzen(D.VORLAGEN.find(v => v.id === 'aussenecke').modell(), 'aussenecke');
    })();
    window.addEventListener('hashchange', () => { ausAdresse(); });
    let breite = 0;
    new ResizeObserver(() => {
      const w = ui.bild.clientWidth;
      if (!modell || Math.abs(w - breite) < 2) return;
      breite = w;
      einpassen();
      zeichnen();
    }).observe(ui.bild);
  }

  function init() {
    const wurzel = document.getElementById('wandschnitt');
    if (wurzel && window.WandschnittLoeser && window.WandschnittDaten) starten(wurzel);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
