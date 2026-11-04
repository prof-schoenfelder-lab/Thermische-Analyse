// Freie und erzwungene Konvektion (P2 Grundlagen Konvektion): warmes Rohr im Querschnitt. Links treibt ein Lüfter die Luft
// vorbei, rechts steigt die erwärmte Luft auf und kalte strömt von den Seiten nach. Schematisch, keine Strömungsrechnung:
// Stromfunktion ψ = (1 - R²/r²)·ψ0 läuft um das Rohr herum, ψ0 ist eine Parallelströmung oder eine aufsteigende Fahne.
// Teilchen erwärmen sich nah am Rohr, die Farbe zeigt ihre Temperatur.
// Einbinden: <div class="konvektionsarten"></div>. Läuft nur im Sichtbereich.
(function () {
  'use strict';

  var W = 332, H = 236, R = 34, N = 75;   // Bild in px, Rohrradius, Teilchen je Bild
  var U = 72, FAHNE = 2070, BREITE = 46;  // Geschwindigkeit links in px/s, Stärke und halbe Breite der Fahne rechts
  var FAELLE = [
    { frei: false, cy: H / 2, ymin: -H / 2, ymax: H / 2, dth: 10, k: 7, titel: 'Erzwungen', text: 'Ein Lüfter treibt die Luft am Rohr vorbei',
      alt: 'Erzwungene Konvektion: Ein Lüfter treibt Luft am warmen Rohr vorbei, sie erwärmt sich nur nah am Rohr' },
    { frei: true, cy: 163, ymin: -73, ymax: 163, dth: 20, k: 3, titel: 'Frei', text: 'Warme Luft steigt auf, kalte strömt nach',
      alt: 'Freie Konvektion: Luft erwärmt sich am Rohr und steigt auf, von den Seiten strömt kalte Luft nach' }
  ];

  function tanh(x) { var e = Math.exp(2 * x); return (e - 1) / (e + 1); }
  function rgb(s) { return [1, 3, 5].map(function (i) { return parseInt(s.substr(i, 2), 16); }); }

  function psi(fall, x, y) {
    var um = 1 - R * R / (x * x + y * y);
    return fall.frei ? -um * FAHNE * 0.5 * (1 + tanh((y + 10) / 60)) * tanh(x / BREITE) : um * U * y;
  }

  // Geschwindigkeit aus der Stromfunktion; nah am Rohr langsamer, an der Wand ruht das Fluid
  function geschw(fall, x, y) {
    var u = (psi(fall, x, y + 1) - psi(fall, x, y - 1)) / 2, v = (psi(fall, x - 1, y) - psi(fall, x + 1, y)) / 2;
    var s = 0.15 + 0.85 * Math.min(1, Math.max(Math.sqrt(x * x + y * y) - R, 0) / 16);
    return [u * s, v * s];
  }

  // Neues Teilchen: links am Rand, in der freien Konvektion dort, wo die Luft von der Seite nachströmt
  function setzen(fall, t) {
    t.T = 0;
    if (!fall.frei) { t.x = -W / 2; t.y = fall.ymin + Math.random() * (fall.ymax - fall.ymin); return; }
    t.x = (Math.random() < 0.5 ? -1 : 1) * (W / 2 - 1); t.y = -10;
    for (var i = 0; i < 40; i++) {
      var y = fall.ymin + Math.random() * (fall.ymax - fall.ymin);
      if (Math.random() < Math.abs(geschw(fall, t.x, y)[0]) / 18) { t.y = y; return; }
    }
  }

  function rechnen(fall, teile, dt) {
    teile.forEach(function (t) {
      var v = geschw(fall, t.x, t.y), r, d;
      t.x += v[0] * dt; t.y += v[1] * dt;
      r = Math.sqrt(t.x * t.x + t.y * t.y); d = r - R;
      if (d < 1) { t.x *= (R + 1) / r; t.y *= (R + 1) / r; d = 1; }
      t.T += d < fall.dth ? (1 - t.T) * fall.k * dt : -t.T * 0.12 * dt;
      if (Math.abs(t.x) > W / 2 + 4 || t.y > fall.ymax + 6 || t.y < fall.ymin - 6) setzen(fall, t);
    });
  }

  function aufbauen(box) {
    box.innerHTML = '<div class="kva-felder">' + FAELLE.map(function (fall) {
      return '<div class="kva-feld"><div class="kva-kopf"><strong>' + fall.titel + '</strong>' + fall.text + '</div>' +
        '<canvas role="img" aria-label="' + fall.alt + '"></canvas></div>';
    }).join('') + '</div><p class="kva-fuss">Schematisch, keine Strömungsrechnung. Idee nach Çengel 2002, Abb. 1-32</p>';

    var cs = getComputedStyle(box), dpr = window.devicePixelRatio || 1, schrift = cs.fontFamily;
    var felder = FAELLE.map(function (fall, i) {
      var cv = box.querySelectorAll('canvas')[i], g = cv.getContext('2d');
      cv.width = W * dpr; cv.height = H * dpr;
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { fall: fall, g: g, teile: [] };
    });
    var winkel = 0, letzt = 0, sichtbar = false, laeuft = false, vorgelaufen = false;
    function f(name) { return cs.getPropertyValue(name).trim(); }

    function vorlauf() {   // Das erste Bild zeigt die Strömung schon ausgebildet
      felder.forEach(function (feld) {
        var fall = feld.fall;
        for (var i = 0; i < N; i++) {
          var t = { T: 0 };
          do {
            t.x = W * (Math.random() - 0.5); t.y = fall.ymin + Math.random() * (fall.ymax - fall.ymin);
          } while (t.x * t.x + t.y * t.y < (R + 3) * (R + 3));
          feld.teile.push(t);
        }
        for (i = 0; i < 500; i++) rechnen(fall, feld.teile, 0.03);
      });
    }

    function bild() {
      var kalt = rgb(f('--kva-kalt')), warm = rgb(f('--kva-warm'));
      function farbe(T) {
        return 'rgb(' + kalt.map(function (k, i) { return Math.round(k + (warm[i] - k) * Math.min(1, T)); }).join(',') + ')';
      }
      felder.forEach(function (feld) {
        var g = feld.g, fall = feld.fall, cx = W / 2;
        g.fillStyle = farbe(0); g.fillRect(0, 0, W, H);
        feld.teile.forEach(function (t) {
          g.beginPath(); g.arc(cx + t.x, fall.cy - t.y, 3.2, 0, 2 * Math.PI);
          g.fillStyle = farbe(t.T); g.fill();
          g.strokeStyle = f('--kva-punkt'); g.lineWidth = 0.7; g.stroke();
        });
        g.beginPath(); g.arc(cx, fall.cy, R, 0, 2 * Math.PI);
        g.fillStyle = f('--kva-rohr'); g.fill();
        g.strokeStyle = f('--kva-kante'); g.lineWidth = 2.5; g.stroke();
        g.fillStyle = '#fff'; g.font = '600 13px ' + schrift; g.textAlign = 'center';
        g.fillText('warm', cx, fall.cy + 4);
        if (!fall.frei) {   // Lüfter von der Seite: Nabe und rotierendes Blatt
          g.fillStyle = f('--kva-nabe'); g.fillRect(11, fall.cy - 5, 11, 10);
          g.fillStyle = f('--kva-blatt'); g.beginPath();
          g.ellipse(24, fall.cy, 5, Math.max(46 * Math.abs(Math.cos(winkel)), 3), 0, 0, 2 * Math.PI); g.fill();
        }
      });
    }

    function schritt(jetzt) {
      if (!sichtbar) { laeuft = false; return; }
      var dt = Math.min(0.05, (jetzt - letzt) / 1000);
      letzt = jetzt; winkel += dt * 14;
      felder.forEach(function (feld) { rechnen(feld.fall, feld.teile, dt); });
      bild();
      requestAnimationFrame(schritt);
    }

    function los() {
      if (laeuft || !sichtbar) return;
      if (!vorgelaufen) { vorgelaufen = true; vorlauf(); bild(); }
      laeuft = true; letzt = performance.now(); requestAnimationFrame(schritt);
    }

    if (window.IntersectionObserver) {
      new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; los(); }).observe(box);
    } else { sichtbar = true; los(); }
  }

  function init() {
    var boxen = document.querySelectorAll('.konvektionsarten');
    for (var i = 0; i < boxen.length; i++) aufbauen(boxen[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
