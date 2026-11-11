// Strahlenzähler: Vakuumröhre (P2 Wärmestrahlung) im Querschnitt (lange Röhre) oder in der Seitenansicht (Stück mit
// offenen Enden, 20 oder 200 mm). Strahlen verlassen Absorber oder Glas an zufälligen Stellen in zufälliger Richtung
// (im Raum kosinusverteilt); gezählt wird, was sie zuerst treffen. Die Anteile nähern sich den Sichtfaktoren
// (Balkengrafik der Seite, tools/sollwerte/p2_sichtfaktoren.py).
// Einbinden: <div class="strahlenzaehler"></div> (Querschnitt) oder <div class="strahlenzaehler" data-ansicht="laengs"></div>.
// Startet erst, wenn man wählt, was strahlt; jede Wahl beginnt neu. Läuft nur im Sichtbereich.
(function () {
  'use strict';

  var RG = 32.5, RA = 35, RT = 6, B = 30, XA = 6;   // Glas innen/außen, Rohr außen, halbe Blechbreite, Blechansatz (mm)
  var TEMPI = [{ name: 'langsam', rate: 3, v: 45 }, { name: 'mittel', rate: 15, v: 90 }, { name: 'schnell', rate: 90, v: 260 }];
  var SOLL = {   // p2_sichtfaktoren.py: lange Röhre (Querschnitt) und Stücke mit offenen Enden
    quer: { A: { G: 0.920, A: 0.079 }, G: { A: 0.602, G: 0.398 } },
    20: { A: { G: 0.397, A: 0.065, E: 0.538 }, G: { A: 0.263, G: 0.132, E: 0.605 } },
    200: { A: { G: 0.841, A: 0.077, E: 0.082 }, G: { A: 0.552, G: 0.346, E: 0.102 } }
  };
  var ZEILEN = {
    A: [['G', 'trifft das Glas'], ['A', 'trifft den Absorber (Rohr oder Blech)'], ['E', 'geht vorn oder hinten hinaus']],
    G: [['A', 'trifft den Absorber'], ['G', 'trifft das Glas gegenüber'], ['E', 'geht vorn oder hinten hinaus']]
  };

  // Richtung um die Normale (nx, ny, 0), kosinusverteilt; im Querschnitt reicht die Projektion: sin θ gleichverteilt
  function richtung(nx, ny, eben) {
    if (eben) {
      var s = 2 * Math.random() - 1, c = Math.sqrt(1 - s * s);
      return { x: nx * c - ny * s, y: nx * s + ny * c, z: 0 };
    }
    var u = Math.random(), r = Math.sqrt(u), phi = 2 * Math.PI * Math.random(), a = r * Math.cos(phi), n = Math.sqrt(1 - u);
    return { x: -a * ny + n * nx, y: a * nx + n * ny, z: r * Math.sin(phi) };
  }

  function start(quelle, L) {
    var z = L * Math.random();
    if (quelle === 'G') {
      var a = 2 * Math.PI * Math.random(), c = Math.cos(a), s = Math.sin(a);
      return { x: RG * c, y: RG * s, z: z, nx: -c, ny: -s, teil: 'glas' };
    }
    var lb = 4 * (B - XA), lr = 2 * Math.PI * RT;   // Blech oben und unten, Rohr außen
    if (Math.random() * (lb + lr) < lb) {
      var x = (Math.random() < 0.5 ? -1 : 1) * (XA + (B - XA) * Math.random());
      return { x: x, y: 0, z: z, nx: 0, ny: Math.random() < 0.5 ? 1 : -1, teil: 'blech' };
    }
    var w;
    do { w = 2 * Math.PI * Math.random(); } while (Math.abs(Math.sin(w)) < 0.05);   // nicht am Blechansatz
    return { x: RT * Math.cos(w), y: RT * Math.sin(w), z: z, nx: Math.cos(w), ny: Math.sin(w), teil: 'rohr' };
  }

  // Erste getroffene Fläche: 'G' Glas innen, 'A' Absorber (Rohr oder Blech, das Blech ohne Dicke),
  // 'E' offenes Ende bei z = 0 oder z = L (L = Infinity: lange Röhre)
  function treffer(p, d, L) {
    var t = d.z > 0 ? (L - p.z) / d.z : (d.z < 0 ? -p.z / d.z : Infinity), ziel = 'E';
    var a = d.x * d.x + d.y * d.y, b = p.x * d.x + p.y * d.y;
    if (a > 1e-12) {
      var tg = (-b + Math.sqrt(Math.max(0, b * b - a * (p.x * p.x + p.y * p.y - RG * RG)))) / a;
      if (tg < t) { t = tg; ziel = 'G'; }
      if (p.teil !== 'rohr') {
        var q = b * b - a * (p.x * p.x + p.y * p.y - RT * RT);
        if (q > 0) { var tr = (-b - Math.sqrt(q)) / a; if (tr > 1e-9 && tr < t) { t = tr; ziel = 'A'; } }
      }
    }
    if (p.teil !== 'blech' && Math.abs(d.y) > 1e-12) {
      var tb = -p.y / d.y;
      if (tb > 1e-9 && tb < t) { var x = Math.abs(p.x + tb * d.x); if (x >= XA && x <= B) { t = tb; ziel = 'A'; } }
    }
    return { t: t, ziel: ziel };
  }

  function zeile(i) {
    return '<div><div class="stz-text"><span class="stz-l' + i + '"></span><b class="stz-p' + i + '"></b></div>' +
      '<div class="stz-balken"><span class="stz-fuell stz-f' + i + '"></span><span class="stz-soll stz-t' + i + '"></span></div></div>';
  }

  function aufbauen(box) {
    var laengs = box.getAttribute('data-ansicht') === 'laengs';
    var W = laengs ? 640 : 340, H = laengs ? 280 : 340;
    box.innerHTML =
      '<div class="stz-knoepfe">' +
      '<button type="button" class="stz-quelle" data-q="A" aria-pressed="false">Absorber strahlt</button>' +
      '<button type="button" class="stz-quelle" data-q="G" aria-pressed="false">Glas strahlt</button>' +
      (laengs ? '<button type="button" class="stz-laenge">Länge: 20 mm</button>' : '') +
      '<button type="button" class="stz-pause"></button>' +
      '<button type="button" class="stz-tempo">Tempo: mittel</button></div>' +
      '<div class="stz-inhalt"><canvas role="img" aria-label="' +
      (laengs ? 'Seitenansicht eines Röhrenstücks mit offenen Enden' : 'Querschnitt der Vakuumröhre') + ' und Strahlen"></canvas>' +
      '<div class="stz-zahlen"><p class="stz-hinweis">Wählen Sie oben, was strahlt.</p>' +
      '<div class="stz-zeilen">' + zeile(1) + zeile(2) + (laengs ? zeile(3) : '') +
      '<p class="stz-fuss">Strahlen: <span class="stz-n">0</span><br>' +
      (laengs ? 'Strich: Ergebnis der Strahlverfolgung für diese Länge' : 'Strich: Sichtfaktor der langen Röhre (Balkengrafik unten)') +
      '</p></div></div></div>';

    var cv = box.querySelector('canvas'), g = cv.getContext('2d'), cs = getComputedStyle(box);
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = H * dpr;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    function f(name) { return cs.getPropertyValue(name).trim(); }
    function q(sel) { return box.querySelector(sel); }

    var quelle = null, L = laengs ? 20 : Infinity, pause = false, tempo = 1;
    var strahlen = [], marken = [], n = 0, z = { G: 0, A: 0, E: 0 };
    var uhr = 0, rest = 0, letzt = 0, sichtbar = false, laeuft = false;

    // Bildpunkt: Querschnitt (x, y) mit 4,3 px/mm, Seitenansicht (z, y) mit 3 px/mm
    function punkt(x, y, zz) {
      return laengs ? [(W - L * 3) / 2 + zz * 3, H / 2 - y * 3] : [W / 2 + x * 4.3, H / 2 - y * 4.3];
    }
    function ort(r, s) { return punkt(r.p.x + s * r.d.x, r.p.y + s * r.d.y, r.p.z + s * r.d.z); }

    function querschnitt(glas, abs, rot) {
      var S = 4.3, M = W / 2;
      function X(x) { return M + x * S; }
      function Y(y) { return M - y * S; }
      g.globalAlpha = abs ? 0.55 : 1;
      g.beginPath(); g.arc(M, M, RA * S, 0, 2 * Math.PI); g.arc(M, M, RG * S, 0, 2 * Math.PI, true);
      g.fillStyle = f('--stz-glas'); g.fill('evenodd');
      g.strokeStyle = f('--stz-kante'); g.lineWidth = 1;
      g.beginPath(); g.arc(M, M, RA * S, 0, 2 * Math.PI); g.stroke();
      g.beginPath(); g.arc(M, M, RG * S, 0, 2 * Math.PI); g.stroke();
      g.globalAlpha = glas ? 0.55 : 1;
      g.fillStyle = f('--stz-kupfer');
      g.fillRect(X(-B), Y(0.35), (B - XA) * S, 0.7 * S); g.fillRect(X(XA), Y(0.35), (B - XA) * S, 0.7 * S);
      g.beginPath(); g.arc(M, M, RT * S, 0, 2 * Math.PI); g.fill();
      g.fillStyle = f('--stz-wasser'); g.beginPath(); g.arc(M, M, (RT - 1) * S, 0, 2 * Math.PI); g.fill();
      g.globalAlpha = 1; g.strokeStyle = rot; g.lineWidth = 2;   // was strahlt, ist rot umrandet
      if (glas) { g.beginPath(); g.arc(M, M, RG * S, 0, 2 * Math.PI); g.stroke(); }
      if (abs) {
        g.strokeRect(X(-B), Y(0.35), (B - XA) * S, 0.7 * S); g.strokeRect(X(XA), Y(0.35), (B - XA) * S, 0.7 * S);
        g.beginPath(); g.arc(M, M, RT * S, 0, 2 * Math.PI); g.stroke();
      }
    }

    function seite(glas, abs, rot) {
      var s = 3, M = H / 2, z0 = (W - L * s) / 2, lang = L * s, wand = (RA - RG) * s;
      function Z(zz) { return z0 + zz * s; }
      function Y(y) { return M - y * s; }
      g.strokeStyle = f('--stz-kante'); g.lineWidth = 1; g.globalAlpha = 0.5; g.setLineDash([4, 4]);   // Nachbarstücke
      [RA, RG, RT, -RT, -RG, -RA].forEach(function (y) {
        g.beginPath(); g.moveTo(0, Y(y)); g.lineTo(Z(0), Y(y)); g.moveTo(Z(L), Y(y)); g.lineTo(W, Y(y)); g.stroke();
      });
      g.setLineDash([]);
      g.globalAlpha = abs ? 0.55 : 1; g.fillStyle = f('--stz-glas');
      g.fillRect(Z(0), Y(RA), lang, wand); g.fillRect(Z(0), Y(-RG), lang, wand);
      g.globalAlpha = abs ? 0.25 : 0.45; g.fillRect(Z(0), Y(RG), lang, 2 * RG * s);   // vordere und hintere Glaswand
      g.globalAlpha = abs ? 0.55 : 1; g.strokeStyle = f('--stz-kante');
      g.strokeRect(Z(0), Y(RA), lang, wand); g.strokeRect(Z(0), Y(-RG), lang, wand);
      g.globalAlpha = glas ? 0.55 : 1; g.fillStyle = f('--stz-kupfer');
      g.fillRect(Z(0), Y(RT), lang, 2 * RT * s);
      g.globalAlpha = 1; g.strokeStyle = rot; g.lineWidth = 2;
      if (glas) { g.strokeRect(Z(0), Y(RA), lang, wand); g.strokeRect(Z(0), Y(-RG), lang, wand); }
      if (abs) g.strokeRect(Z(0), Y(RT), lang, 2 * RT * s);
      g.strokeStyle = f('--stz-kante'); g.fillStyle = f('--stz-kante'); g.lineWidth = 1.5; g.setLineDash([6, 4]);
      g.font = '600 13px ' + cs.fontFamily; g.textAlign = 'center';
      [0, L].forEach(function (zz) {                                   // offene Enden
        g.beginPath(); g.moveTo(Z(zz), Y(RA) - 4); g.lineTo(Z(zz), Y(-RA) + 4); g.stroke();
        g.fillText('offen', Z(zz), Y(RA) - 10);
      });
      g.setLineDash([]);
    }

    function etikett() {
      if (!quelle) return;
      var text = quelle === 'G' ? 'Glas strahlt' : 'Absorber strahlt', y;
      if (laengs) y = H / 2 + (quelle === 'G' ? RA : RT) * 3 + 22;
      else y = H / 2 + (quelle === 'G' ? 28 : 12) * 4.3;
      g.font = '700 15px ' + cs.fontFamily; g.textAlign = 'center';
      g.lineJoin = 'round'; g.lineWidth = 5; g.strokeStyle = f('--stz-grund'); g.strokeText(text, W / 2, y);
      g.fillStyle = f('--stz-strahl'); g.fillText(text, W / 2, y);
    }

    function bild() {
      var rot = f('--stz-strahl'), grau = f('--stz-kante');
      var farbe = { G: f('--stz-glas-treffer'), A: f('--stz-abs-treffer'), E: grau };
      g.clearRect(0, 0, W, H);
      (laengs ? seite : querschnitt)(quelle === 'G', quelle === 'A', rot);
      marken.forEach(function (m) {
        var p = punkt(m.x, m.y, m.z);
        g.globalAlpha = Math.max(0, 1 - (uhr - m.zeit) / 5000); g.fillStyle = farbe[m.ziel];
        g.beginPath(); g.arc(p[0], p[1], 2, 0, 2 * Math.PI); g.fill();
      });
      g.lineWidth = 1.2;
      strahlen.forEach(function (r) {
        var p0 = punkt(r.p.x, r.p.y, r.p.z), p1 = ort(r, Math.min(r.s, r.t)), kopf = p1;
        g.globalAlpha = r.fertig < 0 ? 0.6 : Math.max(0, 0.6 * (1 - (uhr - r.fertig) / 600));
        g.strokeStyle = rot; g.fillStyle = rot;
        g.beginPath(); g.moveTo(p0[0], p0[1]); g.lineTo(p1[0], p1[1]); g.stroke();
        g.beginPath(); g.arc(p0[0], p0[1], 2.2, 0, 2 * Math.PI); g.fill();   // Startpunkt
        if (r.s > r.t) {                                                     // hinaus: draußen grau weiter
          kopf = ort(r, r.s); g.strokeStyle = grau; g.fillStyle = grau;
          g.beginPath(); g.moveTo(p1[0], p1[1]); g.lineTo(kopf[0], kopf[1]); g.stroke();
        }
        if (r.fertig < 0) { g.globalAlpha = 1; g.beginPath(); g.arc(kopf[0], kopf[1], 2.4, 0, 2 * Math.PI); g.fill(); }
      });
      g.globalAlpha = 1;
      etikett();
    }

    function anzeigen() {
      q('.stz-hinweis').style.display = quelle ? 'none' : '';
      q('.stz-zeilen').style.display = quelle ? '' : 'none';
      q('.stz-pause').style.display = quelle ? '' : 'none';
      if (!quelle) return;
      var soll = (laengs ? SOLL[L] : SOLL.quer)[quelle];
      ZEILEN[quelle].slice(0, laengs ? 3 : 2).forEach(function (zl, i) {
        var a = n ? z[zl[0]] / n : 0, k = i + 1;
        q('.stz-l' + k).textContent = zl[1];
        q('.stz-p' + k).textContent = Math.round(a * 100) + ' %';
        q('.stz-f' + k).className = 'stz-fuell stz-f' + k + ' stz-' + zl[0];
        q('.stz-f' + k).style.width = (a * 100) + '%';
        q('.stz-t' + k).style.left = (soll[zl[0]] * 100) + '%';
      });
      q('.stz-n').textContent = n.toLocaleString('de-DE');
      q('.stz-pause').textContent = pause ? 'Weiter' : 'Pause';
    }

    function schritt(jetzt) {
      if (!sichtbar || pause || !quelle) { laeuft = false; return; }
      var dt = Math.min(0.05, (jetzt - letzt) / 1000), T = TEMPI[tempo];
      letzt = jetzt; uhr += dt * 1000;
      for (rest += T.rate * dt; rest >= 1; rest -= 1) {
        var p = start(quelle, laengs ? L : 0), d = richtung(p.nx, p.ny, !laengs), h = treffer(p, d, L);
        strahlen.push({ p: p, d: d, t: h.t, ziel: h.ziel, ende: h.ziel === 'E' ? h.t + 40 : h.t, s: 0, gezaehlt: false, fertig: -1 });
      }
      strahlen.forEach(function (r) {
        if (r.fertig >= 0) return;
        r.s = Math.min(r.ende, r.s + T.v * dt);
        if (!r.gezaehlt && r.s >= r.t) {
          r.gezaehlt = true; n++; z[r.ziel]++;
          marken.push({ x: r.p.x + r.t * r.d.x, y: r.p.y + r.t * r.d.y, z: r.p.z + r.t * r.d.z, ziel: r.ziel, zeit: uhr });
        }
        if (r.s >= r.ende) r.fertig = uhr;
      });
      strahlen = strahlen.filter(function (r) { return r.fertig < 0 || uhr - r.fertig < 600; });
      marken = marken.filter(function (m) { return uhr - m.zeit < 5000; });
      anzeigen(); bild();
      requestAnimationFrame(schritt);
    }

    function los() {
      if (laeuft || !sichtbar || pause || !quelle) return;
      laeuft = true; letzt = performance.now(); requestAnimationFrame(schritt);
    }

    function neu() {
      strahlen = []; marken = []; n = 0; z = { G: 0, A: 0, E: 0 }; rest = 0; pause = false;
      anzeigen(); bild(); los();
    }

    box.querySelectorAll('.stz-quelle').forEach(function (k) {
      k.addEventListener('click', function () {
        box.querySelectorAll('.stz-quelle').forEach(function (x) { x.setAttribute('aria-pressed', x === k ? 'true' : 'false'); });
        quelle = k.getAttribute('data-q'); neu();
      });
    });
    if (laengs) q('.stz-laenge').addEventListener('click', function () {
      L = L === 20 ? 200 : 20; this.textContent = 'Länge: ' + L + ' mm';
      if (quelle) neu(); else bild();
    });
    q('.stz-pause').addEventListener('click', function () { pause = !pause; anzeigen(); los(); });
    q('.stz-tempo').addEventListener('click', function () {
      tempo = (tempo + 1) % TEMPI.length; this.textContent = 'Tempo: ' + TEMPI[tempo].name;
    });

    anzeigen(); bild();
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; los(); }).observe(box);
    } else { sichtbar = true; los(); }
  }

  function init() {
    var boxen = document.querySelectorAll('.strahlenzaehler');
    for (var i = 0; i < boxen.length; i++) aufbauen(boxen[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
