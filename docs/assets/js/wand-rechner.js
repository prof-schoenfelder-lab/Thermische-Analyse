// Wand-Rechner: Temperaturverlauf durch die Außenwand (Kalksandstein + EPS) mit Konvektion.
// Einbinden: <div class="wand-rechner"></div>. Regler für h innen, h außen und λ der Dämmung;
// großes h zeigt, dass die Oberfläche die Lufttemperatur annimmt (Fall a).
(function () {
  'use strict';

  var TI = 20, TE = -10, D_KS = 0.175, L_KS = 0.99, D_EPS = 0.14;
  var NORM = { hi: 7.7, he: 25, leps: 0.035 };
  var NS = 'http://www.w3.org/2000/svg';

  function de(x, n) { return x.toFixed(n).replace('.', ',').replace('-', '−'); }

  function rechnen(hi, he, leps) {
    var R = 1 / hi + D_KS / L_KS + D_EPS / leps + 1 / he;
    var q = (TI - TE) / R;
    var tsi = TI - q / hi, tf = tsi - q * D_KS / L_KS, tse = tf - q * D_EPS / leps;
    return { q: q, U: 1 / R, tsi: tsi, tf: tf, tse: tse };
  }

  // Logarithmischer Regler 0..1000 -> [min, max]
  function ausRegler(v, min, max) { return min * Math.pow(max / min, v / 1000); }
  function inRegler(x, min, max) { return Math.round(1000 * Math.log(x / min) / Math.log(max / min)); }

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function aufbauen(box) {
    var regler = [
      { key: 'hi', label: 'h innen', unit: 'W/(m²·K)', min: 1, max: 1000, dez: 1 },
      { key: 'he', label: 'h außen', unit: 'W/(m²·K)', min: 1, max: 1000, dez: 1 },
      { key: 'leps', label: 'λ Dämmung', unit: 'W/(m·K)', min: 0.02, max: 2, dez: 3 }
    ];
    var wert = { hi: NORM.hi, he: NORM.he, leps: NORM.leps };
    var id = 'wr' + Math.random().toString(36).slice(2, 7);

    box.innerHTML = '';
    var ctrl = document.createElement('div');
    ctrl.className = 'wr-ctrl';
    regler.forEach(function (r) {
      var z = document.createElement('div');
      z.className = 'wr-row';
      z.innerHTML = '<label for="' + id + r.key + '">' + r.label + '</label>' +
        '<input type="range" id="' + id + r.key + '" min="0" max="1000" step="1">' +
        '<output for="' + id + r.key + '"></output>';
      ctrl.appendChild(z);
      r.input = z.querySelector('input');
      r.out = z.querySelector('output');
      r.input.addEventListener('input', function () {
        wert[r.key] = ausRegler(+r.input.value, r.min, r.max);
        zeichnen();
      });
    });
    var knoepfe = document.createElement('div');
    knoepfe.className = 'wr-btns';
    knoepfe.innerHTML = '<button type="button" data-a="norm">Werte der Aufgabe</button>' +
      '<button type="button" data-a="gross">h sehr groß (wie Fall a)</button>' +
      '<button type="button" data-a="klein">h innen sehr klein</button>';
    knoepfe.addEventListener('click', function (ev) {
      var a = ev.target.getAttribute('data-a');
      if (!a) return;
      if (a === 'norm') { wert.hi = NORM.hi; wert.he = NORM.he; wert.leps = NORM.leps; }
      if (a === 'gross') { wert.hi = 1000; wert.he = 1000; }
      if (a === 'klein') { wert.hi = 1; }
      zeichnen();
    });
    ctrl.appendChild(knoepfe);

    // Diagramm: x in px, Wand 175 + 140 mm, links und rechts je eine Luftzone
    var W = 900, H = 340, X0 = 70, LUFT = 120, WAND = 520, Y_OB = 24, Y_UN = 296, TMIN = -12, TMAX = 22;
    var xKS = X0 + LUFT, xF = xKS + WAND * D_KS / (D_KS + D_EPS), xE = xKS + WAND, xR = xE + LUFT;
    var y = function (t) { return Y_UN - (t - TMIN) / (TMAX - TMIN) * (Y_UN - Y_OB); };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'wr-svg', role: 'img',
      'aria-label': 'Temperaturverlauf durch die Wand' });
    el('rect', { x: X0, y: Y_OB, width: LUFT, height: Y_UN - Y_OB, class: 'wr-luft' }, svg);
    el('rect', { x: xE, y: Y_OB, width: LUFT, height: Y_UN - Y_OB, class: 'wr-luft' }, svg);
    el('rect', { x: xKS, y: Y_OB, width: xF - xKS, height: Y_UN - Y_OB, class: 'wr-ks' }, svg);
    el('rect', { x: xF, y: Y_OB, width: xE - xF, height: Y_UN - Y_OB, class: 'wr-eps' }, svg);
    for (var t = -10; t <= 20; t += 5) {
      el('line', { x1: X0, x2: xR, y1: y(t), y2: y(t), class: 'wr-grid' }, svg);
      el('text', { x: X0 - 10, y: y(t) + 5, class: 'wr-axis', 'text-anchor': 'end' }, svg).textContent = de(t, 0) + ' °C';
    }
    [['Raumluft', X0 + LUFT / 2], ['Kalksandstein', (xKS + xF) / 2], ['EPS', (xF + xE) / 2], ['Außenluft', xE + LUFT / 2]]
      .forEach(function (b) { el('text', { x: b[1], y: H - 14, class: 'wr-axis', 'text-anchor': 'middle' }, svg).textContent = b[0]; });
    var fallA = el('polyline', { class: 'wr-fall-a' }, svg);
    var linie = el('polyline', { class: 'wr-linie' }, svg);
    var punkte = [0, 1, 2].map(function () {
      return { c: el('circle', { r: 6, class: 'wr-punkt' }, svg), t: el('text', { class: 'wr-label' }, svg) };
    });
    var legende = el('text', { x: xR, y: 16, class: 'wr-axis', 'text-anchor': 'end' }, svg);
    legende.textContent = 'gestrichelt: Fall a) mit fester Oberflächentemperatur';

    var werte = document.createElement('div');
    werte.className = 'wr-werte';
    werte.setAttribute('aria-live', 'polite');

    box.appendChild(ctrl);
    box.appendChild(svg);
    box.appendChild(werte);

    var grenz = 26; // Breite der Luftschicht, in der die Temperatur zur Wand hin abfällt
    function zeichnen() {
      regler.forEach(function (r) {
        r.input.value = inRegler(wert[r.key], r.min, r.max);
        r.out.textContent = de(wert[r.key], wert[r.key] >= 100 ? 0 : r.dez) + ' ' + r.unit;
      });
      var e = rechnen(wert.hi, wert.he, wert.leps);
      var a = rechnen(1e9, 1e9, wert.leps);
      linie.setAttribute('points', [[X0, TI], [xKS - grenz, TI], [xKS, e.tsi], [xF, e.tf], [xE, e.tse],
        [xE + grenz, TE], [xR, TE]].map(function (p) { return p[0] + ',' + y(p[1]); }).join(' '));
      fallA.setAttribute('points', [[xKS, a.tsi], [xF, a.tf], [xE, a.tse]]
        .map(function (p) { return p[0] + ',' + y(p[1]); }).join(' '));
      [[xKS, e.tsi, 'start', 10], [xF, e.tf, 'start', 10], [xE, e.tse, 'start', 12]].forEach(function (p, i) {
        punkte[i].c.setAttribute('cx', p[0]);
        punkte[i].c.setAttribute('cy', y(p[1]));
        punkte[i].t.setAttribute('x', p[0] + p[3]);
        punkte[i].t.setAttribute('y', y(p[1]) - 10);
        punkte[i].t.setAttribute('text-anchor', p[2]);
        punkte[i].t.textContent = de(p[1], 2) + ' °C';
      });
      werte.innerHTML =
        '<div><span>Oberfläche innen</span><b>' + de(e.tsi, 2) + ' °C</b></div>' +
        '<div><span>Trennfuge</span><b>' + de(e.tf, 2) + ' °C</b></div>' +
        '<div><span>Oberfläche außen</span><b>' + de(e.tse, 2) + ' °C</b></div>' +
        '<div><span>Wärmestromdichte</span><b>' + de(e.q, 2) + ' W/m²</b></div>' +
        '<div><span>U-Wert</span><b>' + de(e.U, 3) + ' W/(m²·K)</b></div>';
    }
    zeichnen();
  }

  function init() {
    var boxen = document.querySelectorAll('.wand-rechner');
    for (var i = 0; i < boxen.length; i++) aufbauen(boxen[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
