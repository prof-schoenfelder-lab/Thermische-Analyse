// α-Rechner der Seite P2 „Konvektion“: In jeder Fallkarte Werte eingeben, heraus kommen Re oder Ra, Pr und α.
// Einbinden: <div class="ar-rechner" data-fall="wand"></div> oder in Markdown, auch in Kästen, als Absatz mit
// „{: .ar-rechner data-fall="wand" }“ darunter (ein rohes <div> beendet dort den Kasten). Fälle unten in FAELLE. Präfix ar-.
// Formeln wie auf der Seite (Çengel 2002), Stoffwerte wie tools/sollwerte/p2_konvektion.py.
// Der Rechenkern läuft ohne Seite auch in Node (module.exports), Tests: node tools/sollwerte/test_alpha_rechner.mjs
(function (root) {
  'use strict';

  var G = 9.81;
  // Stoffwerte: T in °C, λ in W/(m·K), ν in m²/s, Pr. Luft Çengel Tab. A-15, Wasser NIST (siedend), wie p2_konvektion.py
  var LUFT = [[7, 0.02416, 1.399e-5, 0.7344], [25, 0.02551, 1.562e-5, 0.7296], [45, 0.02699, 1.749e-5, 0.7241],
              [60, 0.02808, 1.896e-5, 0.7202], [80, 0.02953, 2.097e-5, 0.7154]];
  var WASSER = [[10, 0.5787, 1.3061e-6, 9.465], [20, 0.5980, 1.0032e-6, 7.007], [30, 0.6143, 0.8006e-6, 5.423],
                [40, 0.6284, 0.6577e-6, 4.340], [50, 0.6406, 0.5531e-6, 3.567], [60, 0.6510, 0.4739e-6, 2.996],
                [70, 0.6597, 0.4127e-6, 2.563], [80, 0.6670, 0.3643e-6, 2.227]];
  // Luft außerhalb der Tabelle linear verlängert, erlaubt von -20 bis 120 °C Filmtemperatur (dort unter 1,5 % neben Tab. A-15)
  var LUFT_MIN = -20, LUFT_MAX = 120;

  function stoffwerte(tab, T) {
    var i = 0;
    while (i < tab.length - 2 && T > tab[i + 1][0]) i++;
    var a = tab[i], b = tab[i + 1], s = (T - a[0]) / (b[0] - a[0]);
    return { lam: a[1] + s * (b[1] - a[1]), nu: a[2] + s * (b[2] - a[2]), Pr: a[3] + s * (b[3] - a[3]),
             ausserhalb: T < tab[0][0] || T > tab[tab.length - 1][0] };
  }

  // Nusselt-Zahlen wie auf der Seite (Çengel 2002: Tab. 9-1, Gl. 7-21, 7-24, 7-35, 8-68, 8-70)
  var NU = {
    wand: function (Ra, Pr) {
      return Math.pow(0.825 + 0.387 * Math.pow(Ra, 1 / 6) / Math.pow(1 + Math.pow(0.492 / Pr, 9 / 16), 8 / 27), 2);
    },
    rohrFrei: function (Ra, Pr) {
      return Math.pow(0.6 + 0.387 * Math.pow(Ra, 1 / 6) / Math.pow(1 + Math.pow(0.559 / Pr, 9 / 16), 8 / 27), 2);
    },
    platteOben: function (Ra) { return Ra < 1e7 ? 0.54 * Math.pow(Ra, 0.25) : 0.15 * Math.pow(Ra, 1 / 3); },
    platteUnten: function (Ra) { return 0.27 * Math.pow(Ra, 0.25); },
    platteLaengs: function (Re, Pr) {
      return Re < 5e5 ? 0.664 * Math.sqrt(Re) * Math.pow(Pr, 1 / 3) : (0.037 * Math.pow(Re, 0.8) - 871) * Math.pow(Pr, 1 / 3);
    },
    rohrQuer: function (Re, Pr) {
      return 0.3 + 0.62 * Math.sqrt(Re) * Math.pow(Pr, 1 / 3) / Math.pow(1 + Math.pow(0.4 / Pr, 2 / 3), 0.25) *
        Math.pow(1 + Math.pow(Re / 282000, 5 / 8), 0.8);
    },
    gnielinski: function (Re, Pr) {
      var f = Math.pow(0.790 * Math.log(Re) - 1.64, -2);
      return (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * Math.sqrt(f / 8) * (Math.pow(Pr, 2 / 3) - 1));
    },
    dittusBoelter: function (Re, Pr, n) { return 0.023 * Math.pow(Re, 0.8) * Math.pow(Pr, n); }
  };

  // ---- Zahlen deutsch schreiben ----------------------------------------------------------------------------------
  function de(x, n) { return x.toFixed(n).replace('.', ',').replace('-', '−'); }
  function gruppiert(x) { return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  var HOCH = '⁰¹²³⁴⁵⁶⁷⁸⁹';
  function zehner(x) {                               // 4,69·10⁹; unter 100 000 als ganze Zahl
    if (x < 1e5) return x < 100 ? de(x, x < 10 ? 2 : 1) : gruppiert(x);
    var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e);
    if (m >= 9.995) { m /= 10; e += 1; }
    return de(m, 2) + '·10' + String(e).split('').map(function (c) { return HOCH[+c]; }).join('');
  }
  function alpha(x) { return (x < 10 ? de(x, 2) : x < 100 ? de(x, 1) : gruppiert(x)) + ' W/(m²·K)'; }
  function zahl(s) {
    var t = String(s).trim().replace(',', '.').replace('−', '-');
    return /^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(t) ? parseFloat(t) : NaN;
  }

  // ---- Rechnungen je Art ------------------------------------------------------------------------------------------
  function luft(Tf) {
    if (Tf < LUFT_MIN || Tf > LUFT_MAX) return null;
    return stoffwerte(LUFT, Tf);
  }
  function frei(L, TO, TL, fkt) {
    var dT = Math.abs(TO - TL), Tf = (TO + TL) / 2, s = luft(Tf);
    if (!s) return { fehler: 'Filmtemperatur ' + de(Tf, 0) + ' °C: Die Stoffwerte reichen nur von −20 bis 120 °C.' };
    if (dT === 0) return { fehler: 'Oberfläche und Luft sind gleich warm: Dann strömt nichts, es gibt keine freie Konvektion.' };
    var Ra = G / (Tf + 273.15) * dT * Math.pow(L, 3) / (s.nu * s.nu) * s.Pr;
    return { Tf: Tf, s: s, dT: dT, Ra: Ra, alpha: fkt(Ra, s.Pr) * s.lam / L };
  }
  function wind(L, v, TO, TL, fkt) {
    var Tf = (TO + TL) / 2, s = luft(Tf);
    if (!s) return { fehler: 'Filmtemperatur ' + de(Tf, 0) + ' °C: Die Stoffwerte reichen nur von −20 bis 120 °C.' };
    var Re = v * L / s.nu;
    return { Tf: Tf, s: s, Re: Re, alpha: fkt(Re, s.Pr) * s.lam / L };
  }
  function stoffKacheln(r, fluid) {
    var k = [['Filmtemperatur', de(r.Tf, 1) + ' °C']];
    if (r.Ra !== undefined) k.push(['Rayleigh-Zahl Ra', zehner(r.Ra)]);
    if (r.Re !== undefined) k.push(['Reynolds-Zahl Re', zehner(r.Re)]);
    k.push(['Prandtl-Zahl Pr', de(r.s.Pr, 3)], ['λ ' + fluid, de(r.s.lam, 4) + ' W/(m·K)']);
    return k;
  }
  function tabellenHinweis(r, h) {
    if (r.s && r.s.ausserhalb) h.push('Filmtemperatur außerhalb der Stofftabelle (7 bis 80 °C): Stoffwerte linear verlängert.');
    return h;
  }
  function ergebnis(r, kacheln, haupt, neben, hinweise) {
    return { fehler: null, kacheln: kacheln, haupt: haupt, neben: neben || null, hinweise: tabellenHinweis(r, hinweise || []),
             alpha: haupt[1], zahlen: r };
  }
  function ueberschlag(wert, gilt, grund) {
    return ['α Überschlag', alpha(wert) + (gilt ? '' : ', gilt hier nicht: ' + grund), wert, gilt];
  }

  function E(k, name, einheit, start, art) { return { k: k, name: name, einheit: einheit, start: start, art: art || 'pos' }; }
  var T_O = E('TO', 'Oberfläche', '°C', '', 'temp'), T_L = E('TL', 'Luft', '°C', '', 'temp');
  function mit(e, start) { var c = {}; for (var k in e) c[k] = e[k]; c.start = start; return c; }

  function platte(w, fkt, bereich, oben) {
    var A = w.a * w.b, p = 2 * (w.a + w.b), L = A / p, L4 = 4 * A / p;
    var r = frei(L, w.TO, w.TL, fkt);
    if (r.fehler) return r;
    var h = [];
    if (r.Ra < bereich[0] || r.Ra > bereich[1]) h.push('Ra liegt außerhalb ' + zehner(bereich[0]) + ' bis ' + zehner(bereich[1]) + ': Die genaue Formel gilt hier nicht.');
    if (oben && r.Ra > 5e6 && r.Ra < 2e7) h.push('Ra nahe 10⁷: Dort wechselt die Formel, α springt um rund 6 %.');
    var kalt = w.TO < w.TL;
    if (oben && kalt) h.push('Oberfläche kälter als die Luft: Das ist „kalte Seite oben“ und gehört zur Karte „warme Seite unten“.');
    if (!oben && kalt) h.push('Oberfläche kälter als die Luft: Das ist „kalte Seite unten“ und gehört zur Karte „warme Seite oben“.');
    var ra4 = r.Ra * 64;                                   // Ra mit L = 4A/p für den Überschlag
    var u = (oben ? 1.32 : 0.59) * Math.pow(r.dT / L4, 0.25);
    var k = [['Länge L = A/p', de(L, 3) + ' m']].concat(stoffKacheln(r, 'Luft'));
    return ergebnis(r, k, ['α genau', r.alpha], ueberschlag(u, ra4 < 1e9, 'turbulent'), h);
  }

  var FAELLE = {
    wand: {
      ein: [E('L', 'Höhe L', 'm', '2,5'), mit(T_O, '17'), mit(T_L, '20')],
      rechnen: function (w) {
        var r = frei(w.L, w.TO, w.TL, NU.wand);
        if (r.fehler) return r;
        var u = 1.42 * Math.pow(r.dT / w.L, 0.25);
        return ergebnis(r, stoffKacheln(r, 'Luft'), ['α genau', r.alpha], ueberschlag(u, r.Ra < 1e9, 'Ra über 10⁹, turbulent'));
      }
    },
    rohr_frei: {
      ein: [E('D', 'Außendurchmesser D', 'mm', '26,9'), mit(T_O, '59,3'), mit(T_L, '15')],
      mm: ['D'],
      rechnen: function (w) {
        var r = frei(w.D, w.TO, w.TL, NU.rohrFrei);
        if (r.fehler) return r;
        var u = 1.32 * Math.pow(r.dT / w.D, 0.25), h = [];
        if (r.Ra > 1e12) h.push('Ra über 10¹²: Die genaue Formel gilt hier nicht.');
        return ergebnis(r, stoffKacheln(r, 'Luft'), ['α genau', r.alpha], ueberschlag(u, r.Ra < 1e9, 'Ra über 10⁹, turbulent'), h);
      }
    },
    platte_oben: {
      ein: [E('a', 'Länge a', 'm', '0,5'), E('b', 'Breite b', 'm', '0,5'), mit(T_O, '50'), mit(T_L, '20')],
      rechnen: function (w) { return platte(w, NU.platteOben, [1e4, 1e11], true); }
    },
    platte_unten: {
      ein: [E('a', 'Länge a', 'm', '0,5'), E('b', 'Breite b', 'm', '0,5'), mit(T_O, '50'), mit(T_L, '20')],
      rechnen: function (w) { return platte(w, NU.platteUnten, [1e5, 1e11], false); }
    },
    platte_laengs: {
      ein: [E('L', 'Länge L in Windrichtung', 'm', '1'), E('v', 'Wind v', 'm/s', '3'), mit(T_O, '30'), mit(T_L, '20')],
      rechnen: function (w) {
        var r = wind(w.L, w.v, w.TO, w.TL, NU.platteLaengs);
        if (r.fehler) return r;
        var lam = r.Re < 5e5, h = [];
        if (r.Re > 1e7) h.push('Re über 10⁷: Die genaue Formel gilt hier nicht.');
        var k = stoffKacheln(r, 'Luft');
        k.splice(2, 0, ['Strömung', lam ? 'laminar' : 'vorn laminar, hinten turbulent']);
        return ergebnis(r, k, ['α genau', r.alpha], ueberschlag(3.9 * Math.sqrt(w.v / w.L), lam, 'nicht mehr laminar'), h);
      }
    },
    rohr_quer: {
      ein: [E('D', 'Außendurchmesser D', 'mm', '70'), E('v', 'Wind v', 'm/s', '1'), mit(T_O, '25'), mit(T_L, '20')],
      mm: ['D'],
      rechnen: function (w) {
        var r = wind(w.D, w.v, w.TO, w.TL, NU.rohrQuer);
        if (r.fehler) return r;
        var h = r.Re * r.s.Pr > 0.2 ? [] : ['Re · Pr unter 0,2: Die Formel gilt hier nicht.'];
        return ergebnis(r, stoffKacheln(r, 'Luft'), ['α genau', r.alpha], null, h);
      }
    },
    rohr_innen: {
      ein: [E('D', 'Innendurchmesser D', 'mm', '21,7'), E('v', 'Geschwindigkeit v', 'm/s', '0,5'), E('TW', 'Wasser', '°C', '60', 'temp')],
      mm: ['D'],
      rechnen: function (w) {
        if (w.TW < 10 || w.TW > 80) return { fehler: 'Die Stoffwerte für Wasser reichen von 10 bis 80 °C.' };
        var s = stoffwerte(WASSER, w.TW), Re = w.v * w.D / s.nu, r = { Tf: w.TW, s: s, Re: Re };
        var k = [['Wassertemperatur', de(w.TW, 1) + ' °C'], ['Reynolds-Zahl Re', zehner(Re)], ['Strömung', ''],
                 ['Prandtl-Zahl Pr', de(s.Pr, 2)], ['λ Wasser', de(s.lam, 3) + ' W/(m·K)']];
        var h = [];
        if (Re < 2300) {
          k[2][1] = 'laminar';
          r.alpha = 3.66 * s.lam / w.D;
          return ergebnis(r, k, ['α bei fester Wandtemperatur', r.alpha],
            ['α bei festem Wärmestrom', alpha(4.36 * s.lam / w.D), 4.36 * s.lam / w.D, true], h);
        }
        if (Re < 3000) {
          k[2][1] = 'Übergang';
          r.alpha = NaN;
          return { fehler: null, kacheln: k, haupt: null, neben: null, alpha: NaN, zahlen: r,
                   hinweise: ['Re zwischen 2300 und 3000: Übergang, dafür gibt es keine verlässliche Formel.'] };
        }
        k[2][1] = 'turbulent';
        if (Re > 5e6) h.push('Re über 5·10⁶: Gnielinski gilt hier nicht.');
        r.alpha = NU.gnielinski(Re, s.Pr) * s.lam / w.D;
        var neben = null;
        if (Re > 1e4) {
          var er = NU.dittusBoelter(Re, s.Pr, 0.4) * s.lam / w.D, ab = NU.dittusBoelter(Re, s.Pr, 0.3) * s.lam / w.D;
          neben = ['α nach Dittus und Boelter', alpha(er) + ' (Wasser wird erwärmt), ' + alpha(ab) + ' (abgekühlt)', er, true];
          r.alphaDB = { erwaermt: er, abgekuehlt: ab };
        } else {
          h.push('Dittus und Boelter erst ab Re 10 000.');
        }
        return ergebnis(r, k, ['α nach Gnielinski', r.alpha], neben, h);
      }
    }
  };

  // ---- Darstellung ------------------------------------------------------------------------------------------------
  function div(klasse, text) { var d = document.createElement('div'); d.className = klasse; if (text) d.textContent = text; return d; }

  function aufbauen(box) {
    var fall = FAELLE[box.getAttribute('data-fall')];
    if (!fall) { box.textContent = 'Rechner: unbekannter Fall „' + box.getAttribute('data-fall') + '“'; return; }
    var id = 'ar' + Math.random().toString(36).slice(2, 7), mm = fall.mm || [];
    box.innerHTML = '';
    box.appendChild(div('ar-kopf', 'Rechner: Werte eingeben, α wird sofort berechnet'));
    var form = div('ar-ein'), aus = div('ar-aus');
    aus.setAttribute('aria-live', 'polite');
    var felder = fall.ein.map(function (e) {
      var z = div('ar-feld');
      z.innerHTML = '<label for="' + id + e.k + '">' + e.name + '</label>' +
        '<span class="ar-eingabe"><input id="' + id + e.k + '" type="text" inputmode="decimal" autocomplete="off" spellcheck="false">' +
        '<span class="ar-einheit">' + e.einheit + '</span></span><small class="ar-fehler"></small>';
      var input = z.querySelector('input');
      input.value = e.start;
      form.appendChild(z);
      return { e: e, input: input, fehler: z.querySelector('.ar-fehler') };
    });
    box.appendChild(form);
    box.appendChild(aus);

    function kachel(t, w, klasse) {
      var d = div('ar-kachel' + (klasse ? ' ' + klasse : ''));
      d.appendChild(Object.assign(document.createElement('span'), { textContent: t }));
      d.appendChild(Object.assign(document.createElement('b'), { textContent: w }));
      return d;
    }

    function rechnen() {
      var w = {}, ok = true;
      felder.forEach(function (f) {
        var x = zahl(f.input.value), text = '';
        if (isNaN(x)) text = 'Zahl eingeben, Komma oder Punkt';
        else if (f.e.art === 'pos' && x <= 0) text = 'größer als 0';
        f.fehler.textContent = text;
        f.input.setAttribute('aria-invalid', text ? 'true' : 'false');
        if (text) ok = false;
        w[f.e.k] = mm.indexOf(f.e.k) >= 0 ? x / 1000 : x;
      });
      aus.innerHTML = '';
      if (!ok) { aus.appendChild(div('ar-hinweis', 'Bitte alle Felder richtig ausfüllen.')); return; }
      var r = fall.rechnen(w);
      if (r.fehler) { aus.appendChild(div('ar-hinweis', r.fehler)); return; }
      var raster = div('ar-kacheln');
      r.kacheln.forEach(function (k) { raster.appendChild(kachel(k[0], k[1])); });
      aus.appendChild(raster);
      if (r.haupt) aus.appendChild(kachel(r.haupt[0], alpha(r.haupt[1]), 'ar-haupt'));
      if (r.neben) aus.appendChild(kachel(r.neben[0], r.neben[1], r.neben[3] ? 'ar-neben' : 'ar-neben ar-ungueltig'));
      r.hinweise.forEach(function (t) { aus.appendChild(div('ar-hinweis', t)); });
    }
    form.addEventListener('input', rechnen);
    rechnen();
  }

  function init() {
    var boxen = document.querySelectorAll('.ar-rechner');
    for (var i = 0; i < boxen.length; i++) {
      var box = boxen[i];
      if (box.getAttribute('data-ar-fertig')) continue;
      if (box.tagName !== 'DIV') {                     // Platzhalter-Absatz aus Markdown ({: .ar-rechner data-fall="…" })
        var d = document.createElement('div');
        d.className = box.className;
        d.setAttribute('data-fall', box.getAttribute('data-fall'));
        box.parentNode.replaceChild(d, box);
        box = d;
      }
      box.setAttribute('data-ar-fertig', '1');
      aufbauen(box);
    }
  }

  var KERN = { G: G, LUFT: LUFT, WASSER: WASSER, stoffwerte: stoffwerte, NU: NU, FAELLE: FAELLE, zahl: zahl, zehner: zehner };
  if (typeof module === 'object' && module.exports) module.exports = KERN;
  else root.AlphaRechner = KERN;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
    if (root.document$ && root.document$.subscribe) root.document$.subscribe(init);
  }
})(typeof window !== 'undefined' ? window : this);
