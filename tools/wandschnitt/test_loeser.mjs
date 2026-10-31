// Tests für den Rechenkern von Wandschnitt 2D (docs/assets/js/wandschnitt-loeser.js), ohne Abhängigkeiten.
//
// Aufruf:  node tools/wandschnitt/test_loeser.mjs
//
// Sollwerte: Außenecke aus tools/sollwerte/p1_uebungen.py (scikit-fem, P2-Dreiecke) und ANSYS (Felix, 20.10.2026),
// Wärmestrom innen mit scikit-fem auf demselben Netz nachgerechnet (9,6775 W/m bei 4 und 6 mm Netzweite),
// 1D-Wand gegen die Handrechnung mit Widerständen in Reihe.
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const L = require('../../docs/assets/js/wandschnitt-loeser.js');
const D = require('../../docs/assets/js/wandschnitt-daten.js');

let fehlerZahl = 0;
const pruefe = (name, ok, info = '') => {
  console.log(`${ok ? 'ok    ' : 'FEHLER'} ${name}${info ? ': ' + info : ''}`);
  if (!ok) fehlerZahl++;
};
const nahe = (a, b, tol) => Math.abs(a - b) <= tol;
const vorlage = id => D.VORLAGEN.find(v => v.id === id).modell();
const rechne = m => L.rechnen(m, D.BIBLIOTHEK);

// Außenecke (P1 Übung 2)
{
  const m = vorlage('aussenecke'), e = rechne(m);
  pruefe('Außenecke rechnet', e.ok, e.ok ? `${e.knoten} Knoten, ${e.ms.gesamt.toFixed(1)} ms` : e.fehler.join(' '));
  const ecke = L.sonde(e, 315, 315), wand = L.sonde(e, 1000, 315);
  pruefe('Ecke innen 17,385 °C (scikit-fem), ANSYS 17,384 °C', nahe(ecke.T, 17.385, 0.01), ecke.T.toFixed(4));
  pruefe('Wand ungestört 18,497 °C (scikit-fem)', nahe(wand.T, 18.497, 0.01), wand.T.toFixed(4));
  const f = e.frsi.find(z => z.id === 'raum');
  pruefe('f_Rsi 0,8954', nahe(f.wert, 0.8954, 0.0005), f.wert.toFixed(5));
  pruefe('kleinste Oberflächentemperatur liegt in der Ecke', nahe(f.ort[0], 315, 1e-6) && nahe(f.ort[1], 315, 1e-6), f.ort.join(', '));
  const innen = e.auswertung.find(z => z.id === 'raum');
  pruefe('Wärmestrom innen 9,6775 W/m (scikit-fem)', nahe(innen.strom, 9.6775, 0.02), innen.strom.toFixed(4));
  pruefe('Energiebilanz', Math.abs(e.bilanz) < 1e-6 * innen.strom, e.bilanz.toExponential(1) + ' W/m');

  // ψ: zwei flankierende Wände, Außenmaß 1000 mm, Innenmaß 685 mm
  const p = e.psi, U = 1 / (0.25 + 0.175 / 0.99 + 0.14 / 0.035 + 0.04);
  pruefe('ψ: zwei flankierende Bauteile', p.elemente && p.elemente.length === 2, p.fehler || p.elemente.map(x => x.lage).join(', '));
  pruefe('ψ: U der Wand wie 1D', p.elemente.every(x => nahe(x.U, U, 1e-9)), p.elemente.map(x => x.U.toFixed(5)).join(', '));
  pruefe('ψ: Außenmaß 1000 mm, Innenmaß 685 mm', p.elemente.every(x => nahe(x.lAussen, 1000, 1e-6) && nahe(x.lInnen, 685, 1e-6)),
    p.elemente.map(x => `${x.lAussen}/${x.lInnen}`).join(', '));
  pruefe('ψ: L2D = Φ/(θi − θe)', nahe(p.L2D, innen.strom / 25, 1e-12), p.L2D.toFixed(5));
  pruefe('ψ außen negativ, innen positiv (Außenecke)', p.psiAussen < 0 && p.psiInnen > 0, `ψe ${p.psiAussen.toFixed(4)}, ψi ${p.psiInnen.toFixed(4)} W/(m·K)`);

  // Netzkonvergenz an der Ecke
  const werte = [40, 20, 10].map(h => L.sonde(rechne(Object.assign(vorlage('aussenecke'), { netz: h })), 315, 315).T);
  pruefe('Netzkonvergenz Ecke (40, 20, 10 mm)', werte.every(t => nahe(t, 17.385, 0.02)), werte.map(t => t.toFixed(4)).join(', '));
}

// 1D-Wand: Streifen 200 mm hoch, oben und unten adiabat
const wand1d = (hi, he, unendlich) => ({
  version: 1, netz: 10, grenze: null,
  bereiche: [
    { id: 'a', name: 'außen', rolle: 'aussen', T: -5, h: he, unendlich },
    { id: 'i', name: 'innen', rolle: 'innen', T: 20, h: hi, unendlich },
  ],
  rechtecke: [
    { art: 'luft', bereich: 'a', x0: -50, x1: 0, y0: 0, y1: 200 }, { art: 'luft', bereich: 'i', x0: 315, x1: 365, y0: 0, y1: 200 },
    { art: 'material', stoff: 'eps035', x0: 0, x1: 140, y0: 0, y1: 200 }, { art: 'material', stoff: 'ks1800', x0: 140, x1: 315, y0: 0, y1: 200 },
  ],
  sonden: [], eigeneStoffe: [],
});
{
  const e = rechne(wand1d(4, 25, false));
  const R = 0.25 + 0.14 / 0.035 + 0.175 / 0.99 + 0.04, q = 25 / R;
  const tsi = L.sonde(e, 315, 100).T, tf = L.sonde(e, 140, 100).T;
  pruefe('1D-Wand: Oberfläche innen', nahe(tsi, 20 - q * 0.25, 1e-9), `${tsi.toFixed(6)} gegen ${(20 - q * 0.25).toFixed(6)}`);
  pruefe('1D-Wand: Trennfuge', nahe(tf, 20 - q * (0.25 + 0.175 / 0.99), 1e-9), tf.toFixed(6));
  pruefe('1D-Wand: Wärmestrom = q · 0,2 m', nahe(e.auswertung.find(z => z.id === 'i').strom, q * 0.2, 1e-9), (q * 0.2).toFixed(6) + ' W/m');
  const iso = L.isolinie(e, 10);
  pruefe('1D-Wand: Isotherme 10 °C senkrecht', iso.length > 0 && iso.every(s => nahe(s[0], s[2], 1e-9)), iso.length + ' Strecken');
  const tx = (20 - q * (0.25 + 0.175 / 0.99) - 10) / q * 0.035 * 1000;   // 10 °C liegt im EPS: Abstand von der Trennfuge nach außen
  pruefe('1D-Wand: Lage der Isotherme 10 °C', iso.every(s => nahe(s[0], 140 - tx, 1e-6)), `${iso[0][0].toFixed(3)} gegen ${(140 - tx).toFixed(3)} mm`);
}
{
  const e = rechne(wand1d(4, 25, true));
  const tsi = L.sonde(e, 315, 100).T, tse = L.sonde(e, 0, 100).T;
  pruefe('h → ∞: Oberflächen nehmen die Lufttemperatur an', nahe(tsi, 20, 1e-4) && nahe(tse, -5, 1e-4), `${tsi.toFixed(6)} / ${tse.toFixed(6)}`);
  const q = 25 / (0.14 / 0.035 + 0.175 / 0.99);
  pruefe('h → ∞: Wärmestrom ohne Übergangswiderstände', nahe(e.auswertung.find(z => z.id === 'i').strom, q * 0.2, 1e-4), (q * 0.2).toFixed(5) + ' W/m');
}

// Außenwand (P1 Vorzeigebeispiel, Fall b): eindimensional, ψ = 0
{
  const e = rechne(vorlage('aussenwand'));
  const q = 30 / (1 / 7.7 + 0.175 / 0.99 + 0.14 / 0.035 + 1 / 25);
  pruefe('Außenwand: q = 6,9019 W/m² wie P1 Fall b', nahe(e.auswertung.find(z => z.id === 'raum').strom, q * 1.0, 1e-9), `${q.toFixed(4)} W/m²`);
  pruefe('Außenwand: ψ = 0 (gerade Wand, oben und unten geschnitten)', e.psi.elemente && nahe(e.psi.psiAussen, 0, 1e-9) && nahe(e.psi.psiInnen, 0, 1e-9),
    e.psi.fehler || `${e.psi.psiAussen.toExponential(1)} / ${e.psi.psiInnen.toExponential(1)}`);
}

// Balkonplatte: Außenmaß über die Decke durchgehend, Innenmaß bis zur Decke
{
  const ohne = rechne(vorlage('balkonplatte')), mit = rechne(vorlage('balkonplatte-trennung'));
  pruefe('Balkonplatte rechnet', ohne.ok && mit.ok, `${ohne.knoten} und ${mit.knoten} Knoten, ${ohne.ms.gesamt.toFixed(1)} und ${mit.ms.gesamt.toFixed(1)} ms`);
  const p = ohne.psi;
  pruefe('Balkonplatte: Wand oben und unten flankierend', p.elemente && p.elemente.length === 2, p.fehler || p.elemente.map(x => x.lage).join(', '));
  pruefe('Balkonplatte: Außenmaß 1100 mm, Innenmaß 1000 mm', p.elemente.every(x => nahe(x.lAussen, 1100, 1e-6) && nahe(x.lInnen, 1000, 1e-6)),
    p.elemente.map(x => `${x.lAussen}/${x.lInnen}`).join(', '));
  pruefe('Balkonplatte: Trennung senkt ψ', mit.psi.psiAussen < p.psiAussen && mit.psi.psiAussen > 0,
    `ψe ohne ${p.psiAussen.toFixed(3)}, mit ${mit.psi.psiAussen.toFixed(3)} W/(m·K)`);
  pruefe('Balkonplatte: Energiebilanz', Math.abs(ohne.bilanz) < 1e-6 && Math.abs(mit.bilanz) < 1e-6, ohne.bilanz.toExponential(1));
}

// Fehlerfälle
{
  const m = vorlage('aussenecke');
  m.rechtecke.push({ art: 'material', stoff: 'ks1800', x0: 2000, x1: 2100, y0: 2000, y1: 2100 });
  const e = rechne(m);
  pruefe('Material ohne Luftbereich wird gemeldet', !e.ok && /keinen Luftbereich/.test(e.fehler[0]), e.ok ? 'kein Fehler' : e.fehler[0]);
  const e2 = rechne(Object.assign(vorlage('aussenecke'), { rechtecke: [] }));
  pruefe('Modell ohne Material wird gemeldet', !e2.ok, e2.ok ? 'kein Fehler' : e2.fehler[0]);
}

// Modell im Link: hin und zurück
{
  const m = D.normalisieren(vorlage('balkonplatte-trennung'));
  const text = await D.kodieren(m), zurueck = await D.dekodieren(text);
  pruefe('Link hin und zurück', JSON.stringify(zurueck) === JSON.stringify(m), `${text.length} Zeichen`);
}

console.log(fehlerZahl ? `\n${fehlerZahl} Test(s) fehlgeschlagen` : '\nAlle Tests bestanden');
process.exit(fehlerZahl ? 1 : 0);
