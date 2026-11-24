// Tests für den α-Rechner (docs/assets/js/alpha-rechner.js) gegen die Rechenbeispiele aus Çengel 2002 und gegen
// tools/sollwerte/p2_konvektion.py. Aufruf: node tools/sollwerte/test_alpha_rechner.mjs (Exit 1 bei Fehler)
import fs from 'node:fs';
import vm from 'node:vm';

const code = fs.readFileSync(new URL('../../docs/assets/js/alpha-rechner.js', import.meta.url), 'utf8');
const ctx = { module: { exports: {} } };
vm.runInNewContext(code, ctx);
const { NU, FAELLE, zahl, zehner } = ctx.module.exports;

let fehler = 0;
function pruefe(name, ist, soll, toleranz = 0.01) {
  const abw = ist / soll - 1, ok = Math.abs(abw) <= toleranz;
  if (!ok) fehler++;
  console.log(`${ok ? 'ok    ' : 'FEHLER'} ${name}: ${ist.toPrecision(5)} gegen ${soll} (${(abw * 100).toFixed(2)} %)`);
}
const alpha = (fall, w) => FAELLE[fall].rechnen(w).alpha;

console.log('Formeln mit den Kennzahlen aus dem Buch (Nu):');
pruefe('Bsp. 7-2a Platte längs, vorn laminar, hinten turbulent', NU.platteLaengs(1.884e6, 0.7154), 2687);
pruefe('Bsp. 7-2b Platte längs, laminar', NU.platteLaengs(4.71e5, 0.7154), 408);
pruefe('Bsp. 7-5 Rohr quer angeströmt', NU.rohrQuer(4.219e4, 0.7202), 124);
pruefe('Bsp. 8-5 Wasser im Rohr, Dittus-Boelter erwärmt', NU.dittusBoelter(10760, 4.34, 0.4), 69.5);
pruefe('Bsp. 9-1 Rohr in ruhender Luft', NU.rohrFrei(1.869e6, 0.7241), 17.40);
pruefe('Bsp. 9-2a senkrechte Platte', NU.wand(7.656e8, 0.7202), 113.4);
pruefe('Bsp. 9-2c waagerechte Platte, warme Seite unten', NU.platteUnten(1.196e7), 15.86);
const b92b = NU.platteOben(1.196e7);
console.log(`info   Bsp. 9-2b warme Seite oben: Das Buch nimmt 0,54·Ra^¼ = 31,76 knapp über Ra 10⁷, der Rechner dort ` +
  `0,15·Ra^⅓ = ${b92b.toFixed(2)} (${((b92b / 31.76 - 1) * 100).toFixed(1)} %); bei 0,54·Ra^¼ ` +
  `${(0.54 * Math.pow(1.196e7, 0.25)).toFixed(2)}`);

console.log('\nGanze Rechnung mit Eingaben wie im Buch (Stofftabelle bei 1 atm):');
pruefe('Bsp. 7-5 Dampfrohr Ø 100 mm im Wind 8 m/s, 110 und 10 °C', alpha('rohr_quer', { D: 0.1, v: 8, TO: 110, TL: 10 }), 34.8);
pruefe('Bsp. 9-1 Rohr Ø 80 mm, 70 und 20 °C', alpha('rohr_frei', { D: 0.08, TO: 70, TL: 20 }), 5.869);
pruefe('Bsp. 9-2a Platte 0,6 m senkrecht, 90 und 30 °C', alpha('wand', { L: 0.6, TO: 90, TL: 30 }), 5.306);
pruefe('Bsp. 9-2c Platte 0,6 × 0,6 m, warme Seite unten', alpha('platte_unten', { a: 0.6, b: 0.6, TO: 90, TL: 30 }), 2.973);
pruefe('Bsp. 8-5 Wasser 40 °C, Ø 30 mm, 0,236 m/s, Dittus-Boelter',
  FAELLE.rohr_innen.rechnen({ D: 0.03, v: 0.236, TW: 40 }).zahlen.alphaDB.erwaermt, 1462);

console.log('\nGegen tools/sollwerte/p2_konvektion.py (gleiche Formeln und Stoffwerte):');
pruefe('Heizungsrohr Ø 26,9 mm, 59,3 und 15 °C', alpha('rohr_frei', { D: 0.0269, TO: 59.3, TL: 15 }), 6.99, 0.002);
pruefe('Raumwand 2,5 m, 17 und 20 °C', alpha('wand', { L: 2.5, TO: 17, TL: 20 }), 2.05, 0.003);
const wasser = FAELLE.rohr_innen.rechnen({ D: 0.0217, v: 0.5, TW: 60 });
pruefe('Wasser im Heizungsrohr, Gnielinski', wasser.alpha, 3513, 0.001);
pruefe('Wasser im Heizungsrohr, Dittus-Boelter abgekühlt', wasser.zahlen.alphaDB.abgekuehlt, 2949, 0.001);
pruefe('Platte 1 m im Wind 3 m/s, Film 25 °C', alpha('platte_laengs', { L: 1, v: 3, TO: 30, TL: 20 }), 6.68, 0.002);
pruefe('Rohr Ø 50 mm im Wind 3 m/s, Film 25 °C', alpha('rohr_quer', { D: 0.05, v: 3, TO: 30, TL: 20 }), 27.05, 0.002);
pruefe('Vakuumröhre Ø 70 mm im Wind 1 m/s, Film 25 °C', alpha('rohr_quer', { D: 0.07, v: 1, TO: 30, TL: 20 }), 12.80, 0.002);
pruefe('Platte warm oben A/p 0,1 m, ΔT 20 K, Film 25 °C', alpha('platte_oben', { a: 0.4, b: 0.4, TO: 35, TL: 15 }), 5.16, 0.002);
pruefe('Platte warm unten A/p 0,25 m, ΔT 20 K, Film 25 °C', alpha('platte_unten', { a: 1, b: 1, TO: 35, TL: 15 }), 2.05, 0.003);

console.log('\nEingaben, Grenzen und Hinweise:');
const fall = (name, ok) => { if (!ok) fehler++; console.log(`${ok ? 'ok    ' : 'FEHLER'} ${name}`); };
fall('„2,5“ wird 2,5', zahl('2,5') === 2.5);
fall('„−5“ wird −5', zahl('−5') === -5);
fall('„abc“ ist keine Zahl', Number.isNaN(zahl('abc')));
fall('Ra 4,69·10⁹ wird geschrieben als 4,69·10⁹', zehner(4.69e9) === '4,69·10⁹');
fall('Raumwand: Überschlag gilt nicht (turbulent)', FAELLE.wand.rechnen({ L: 2.5, TO: 17, TL: 20 }).neben[3] === false);
fall('Heizungsrohr: Überschlag gilt', FAELLE.rohr_frei.rechnen({ D: 0.0269, TO: 59.3, TL: 15 }).neben[3] === true);
fall('gleiche Temperaturen: Fehlermeldung', !!FAELLE.wand.rechnen({ L: 1, TO: 20, TL: 20 }).fehler);
fall('Film 130 °C: Fehlermeldung', !!FAELLE.wand.rechnen({ L: 1, TO: 200, TL: 60 }).fehler);
fall('Film 0 °C: Hinweis „linear verlängert“',
  FAELLE.rohr_quer.rechnen({ D: 0.05, v: 3, TO: 5, TL: -5 }).hinweise.some((t) => t.includes('verlängert')));
fall('Wasser 90 °C: Fehlermeldung', !!FAELLE.rohr_innen.rechnen({ D: 0.02, v: 0.5, TW: 90 }).fehler);
fall('Wasser langsam: laminar 3,66 λ/D', Math.abs(FAELLE.rohr_innen.rechnen({ D: 0.02, v: 0.01, TW: 60 }).alpha - 3.66 * 0.651 / 0.02) < 0.01);
fall('Re im Übergang: Hinweis statt α',
  FAELLE.rohr_innen.rechnen({ D: 0.02, v: 0.06, TW: 60 }).hinweise.some((t) => t.includes('Übergang')));
fall('kalte Platte oben: Hinweis auf die andere Karte',
  FAELLE.platte_oben.rechnen({ a: 0.5, b: 0.5, TO: 10, TL: 20 }).hinweise.some((t) => t.includes('warme Seite unten')));
fall('Platte 6 m im Wind 8 m/s: nicht mehr laminar, Überschlag gilt nicht',
  FAELLE.platte_laengs.rechnen({ L: 6, v: 8, TO: 30, TL: 20 }).neben[3] === false);

console.log(fehler ? `\n${fehler} Prüfung(en) fehlgeschlagen` : '\nAlle Prüfungen bestanden');
process.exit(fehler ? 1 : 0);
