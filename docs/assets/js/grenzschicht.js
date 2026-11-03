// Grenzschicht (P2 Grundlagen Konvektion): Fluid strömt über eine warme Wand. Farbe = Temperatur T = erfc(y/δ) mit
// δ ~ √(x/v) (laminare Plattengrenzschicht). Die Teilchen folgen den Stromlinien des Profils u = v·s(2 - s), rote Pfeile
// zeigen den Wärmestrom aus der Wand (~ 1/δ). Der Regler ändert v, die Balken zeigen v, δ ~ 1/√v und α ~ √v gegenüber
// der Mitte des Reglers.
// Einbinden: <div class="grenzschicht"></div>. Läuft nur im Sichtbereich.
(function () {
  'use strict';

  var W = 680, H = 290, X0 = 30, X1 = 660, YW = 245, HT = 215, WD = 40, K = 0.2475, N = 90;

  function erfc(x) {   // x >= 0, Näherung aus Numerical Recipes (Fehler unter 1,2e-7)
    var t = 1 / (1 + 0.5 * x);
    return t * Math.exp(-x * x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 +
      t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  }
  function rgb(hex) { var n = parseInt(hex.replace('#', ''), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function zahl(f) { return '× ' + f.toLocaleString('de-DE', { maximumFractionDigits: 2 }); }
  function zeile(k, text) {
    return '<div class="gsa-zeile"><span>' + text + '</span><span class="gsa-balken"><span class="gsa-fuell gsa-' + k +
      '"></span></span><b class="gsa-wert"></b></div>';
  }

  function aufbauen(box) {
    box.innerHTML =
      '<canvas role="img" aria-label="Fluid strömt über eine warme Wand. In einer dünnen Schicht an der Wand, der ' +
      'Grenzschicht, ist das Fluid warm und langsam. Schnellere Strömung macht die Schicht dünner und den Wärmestrom ' +
      'größer."></canvas>' +
      '<div class="gsa-regler"><span>langsam</span><input type="range" min="-1" max="1" step="0.05" value="0" ' +
      'aria-label="Geschwindigkeit der Strömung"><span>schnell</span></div>' +
      '<div class="gsa-zeilen">' + zeile('v', 'Geschwindigkeit v') + zeile('d', 'Dicke δ der Grenzschicht') +
      zeile('a', 'Wärmeübergang α ≈ λ<sub>F</sub>/δ') + '</div>' +
      '<p class="gsa-fuss">Faktoren gegenüber der Mitte des Reglers. Laminar an einer Platte gilt: viermal so schnell ' +
      'ergibt eine halb so dicke Grenzschicht und ein doppelt so großes α.</p>';

    var cv = box.querySelector('canvas'), g = cv.getContext('2d'), cs = getComputedStyle(box);
    var regler = box.querySelector('input'), fuell = box.querySelectorAll('.gsa-fuell'), wert = box.querySelectorAll('.gsa-wert');
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = H * dpr;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    function f(name) { return cs.getPropertyValue(name).trim(); }

    var U = 1, feld = null, farben = '', kalt, warm, teile = [], letzt = 0, sichtbar = false, laeuft = false;
    function X(x) { return X0 + x * (X1 - X0); }
    function Y(y) { return YW - y * HT; }
    function delta(x) { return K * Math.sqrt((x + 0.02) / U); }
    function u(x, y) { var s = Math.min(y / (1.2 * delta(x)), 1); return U * s * (2 - s); }
    function psi(x, y) {   // Stromfunktion zum Profil u
      var h = 1.2 * delta(x), s = y / h;
      return U * h * (s < 1 ? s * s - s * s * s / 3 : s - 1 / 3);
    }
    function hoehe(x, p) {   // y auf der Stromlinie p an der Stelle x
      var h = 1.2 * delta(x), c = p / (U * h), a = 0, b = 1;
      if (c >= 2 / 3) return h * (c + 1 / 3);
      for (var i = 0; i < 30; i++) { var m = (a + b) / 2; if (m * m - m * m * m / 3 < c) a = m; else b = m; }
      return h * a;
    }
    function farbe(T) { return [0, 1, 2].map(function (i) { return Math.round(kalt[i] + (warm[i] - kalt[i]) * T); }); }
    function neu(t, x) { t.x = x; t.y = 0.01 + 0.99 * Math.random(); }

    function feldBauen() {
      var nx = 170, ny = 60, c = document.createElement('canvas'), cx, img;
      kalt = rgb(f('--gsa-kalt')); warm = rgb(f('--gsa-warm'));
      c.width = nx; c.height = ny; cx = c.getContext('2d'); img = cx.createImageData(nx, ny);
      for (var j = 0; j < ny; j++) {
        for (var i = 0; i < nx; i++) {
          var col = farbe(erfc((ny - 1 - j) / (ny - 1) / delta(i / (nx - 1)))), k = (j * nx + i) * 4;
          img.data[k] = col[0]; img.data[k + 1] = col[1]; img.data[k + 2] = col[2]; img.data[k + 3] = 255;
        }
      }
      cx.putImageData(img, 0, 0); feld = c;
    }

    function pfeil(x1, y1, x2, y2, c, w, rand) {
      var a = Math.atan2(y2 - y1, x2 - x1), s = 6;
      function weg() {
        g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2);
        g.moveTo(x2, y2); g.lineTo(x2 - s * Math.cos(a - 0.4), y2 - s * Math.sin(a - 0.4));
        g.lineTo(x2 - s * Math.cos(a + 0.4), y2 - s * Math.sin(a + 0.4)); g.closePath();
      }
      g.lineJoin = 'round';
      if (rand) { weg(); g.strokeStyle = rand; g.lineWidth = w + 3; g.stroke(); }
      weg(); g.strokeStyle = c; g.fillStyle = c; g.lineWidth = w; g.stroke(); g.fill();
    }
    function text(t, x, y, c, schrift, ausrichtung) {   // mit Rand in der Grundfarbe, lesbar auf dem Farbfeld
      g.font = schrift; g.textAlign = ausrichtung; g.lineJoin = 'round';
      g.strokeStyle = f('--gsa-grund'); g.lineWidth = 4; g.strokeText(t, x, y);
      g.fillStyle = c; g.fillText(t, x, y);
    }

    function bild() {
      var schrift = cs.fontFamily, rand = f('--gsa-grund'), i, x, y, L;
      if (f('--gsa-kalt') + f('--gsa-warm') !== farben) { farben = f('--gsa-kalt') + f('--gsa-warm'); feldBauen(); }
      g.clearRect(0, 0, W, H);
      g.imageSmoothingEnabled = true; g.drawImage(feld, X0, YW - HT, X1 - X0, HT);

      // Rand der Grenzschicht: dort sind noch 5 % des Temperaturunterschieds übrig
      g.setLineDash([5, 4]); g.strokeStyle = f('--gsa-rand'); g.lineWidth = 1.2; g.beginPath();
      for (i = 0; i <= 60; i++) {
        x = i / 60; y = Math.min(1.39 * delta(x), 1);
        if (i) g.lineTo(X(x), Y(y)); else g.moveTo(X(x), Y(y));
      }
      g.stroke(); g.setLineDash([]);

      // Geschwindigkeitsprofil
      var xv = 0.78, blau = f('--gsa-v');
      g.strokeStyle = blau; g.lineWidth = 1.2; g.beginPath(); g.moveTo(X(xv), YW); g.lineTo(X(xv), Y(0.95)); g.stroke();
      for (i = 1; i <= 9; i++) { L = u(xv, i / 10) * 32; if (L > 3) pfeil(X(xv), Y(i / 10), X(xv) + L, Y(i / 10), blau, 1.4); }

      teile.forEach(function (t) {
        var col = farbe(erfc(t.y / delta(t.x)));
        g.fillStyle = 'rgb(' + col.join(',') + ')'; g.strokeStyle = f('--gsa-punkt'); g.lineWidth = 0.8;
        g.beginPath(); g.arc(X(t.x), Y(t.y), 3.2, 0, 2 * Math.PI); g.fill(); g.stroke();
      });

      // Wand: fester Körper, schraffiert, mit klarer Kante zum Fluid
      g.fillStyle = f('--gsa-wand'); g.fillRect(X0, YW, X1 - X0, WD);
      g.save(); g.beginPath(); g.rect(X0, YW, X1 - X0, WD); g.clip();
      g.strokeStyle = 'rgba(255, 255, 255, .28)'; g.lineWidth = 1;
      for (x = X0 - WD; x < X1; x += 12) { g.beginPath(); g.moveTo(x, YW + WD); g.lineTo(x + WD, YW); g.stroke(); }
      g.restore();
      g.strokeStyle = f('--gsa-kante'); g.lineWidth = 2.5; g.beginPath(); g.moveTo(X0, YW); g.lineTo(X1, YW); g.stroke();
      g.font = '600 13px ' + schrift; g.textAlign = 'center'; g.fillStyle = '#fff';
      g.fillText('warme Wand (fester Körper)', (X0 + X1) / 2, YW + 25);

      // Wärmestrom aus der Wand, proportional zu 1/δ
      [0.04, 0.15, 0.28].forEach(function (x) { pfeil(X(x), YW - 2, X(x), YW - 2 - 2.4 / delta(x), f('--gsa-q'), 2.2, rand); });

      text('Strömung →', X0 + 6, 22, f('--gsa-text'), '13px ' + schrift, 'left');
      text('Geschwindigkeit', X(xv), 22, blau, '13px ' + schrift, 'left');
      text('warme Schicht (Grenzschicht)', X(0.5), Math.min(Y(1.39 * delta(0.5)) - 7, YW - 44), f('--gsa-rand'), '13px ' + schrift, 'center');
      g.font = '600 12.5px ' + schrift;   // Hintergrund, damit die gestrichelte Linie bei dünner Schicht nicht stört
      L = Math.max(g.measureText('an der Wand ruht das Fluid:').width, g.measureText('Wärme nur durch Leitung').width) / 2 + 6;
      g.globalAlpha = 0.75; g.fillStyle = rand; g.fillRect(X(0.53) - L, YW - 35, 2 * L, 33); g.globalAlpha = 1;
      text('an der Wand ruht das Fluid:', X(0.53), YW - 22, f('--gsa-hinweis'), '600 12.5px ' + schrift, 'center');
      text('Wärme nur durch Leitung', X(0.53), YW - 8, f('--gsa-hinweis'), '600 12.5px ' + schrift, 'center');
    }

    function anzeigen() {
      var fak = [U, 1 / Math.sqrt(U), Math.sqrt(U)], max = [4, 2, 2];
      for (var i = 0; i < 3; i++) { fuell[i].style.width = (fak[i] / max[i] * 100) + '%'; wert[i].textContent = zahl(fak[i]); }
    }

    function schritt(jetzt) {
      if (!sichtbar) { laeuft = false; return; }
      var dt = Math.min(0.05, (jetzt - letzt) / 1000);
      letzt = jetzt;
      teile.forEach(function (t) {
        var p = psi(t.x, t.y);
        t.x += u(t.x, t.y) * 0.22 * dt;
        if (t.x > 1) neu(t, 0);
        else { t.y = hoehe(t.x, p); if (t.y > 1) neu(t, 0); }
      });
      bild();
      requestAnimationFrame(schritt);
    }

    function los() {
      if (laeuft || !sichtbar) return;
      laeuft = true; letzt = performance.now(); requestAnimationFrame(schritt);
    }

    regler.addEventListener('input', function () {
      U = Math.pow(4, parseFloat(regler.value)); feldBauen(); anzeigen();
      if (!laeuft) bild();
    });

    for (var i = 0; i < N; i++) { var t = {}; neu(t, Math.random()); teile.push(t); }
    anzeigen(); bild();
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; los(); }).observe(box);
    } else { sichtbar = true; los(); }
  }

  function init() {
    var boxen = document.querySelectorAll('.grenzschicht');
    for (var i = 0; i < boxen.length; i++) aufbauen(boxen[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
