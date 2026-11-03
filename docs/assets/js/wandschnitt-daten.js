// Wandschnitt 2D, Daten: Materialauswahl mit Fundstelle, Normwerte der Wärmeübergänge, Vorlagen und
// Modell im Link (komprimiertes JSON). Ohne DOM, läuft im Browser und in Node.
(function (root) {
  'use strict';

  // Startauswahl (Stufe 1). Alle Werte sind von Felix gegen die Normen zu prüfen (Aufgabe TD-22).
  // Keine vollständigen Normtabellen: die Seite ist öffentlich, daher nur einzelne Werte mit Fundstelle.
  const BIBLIOTHEK = [
    { id: 'ks1800', name: 'Kalksandstein 1800 kg/m³', gruppe: 'Mauerwerk', lambda: 0.99, quelle: 'DIN 4108-4, Tab. 1', farbe: '#d9dcde' },
    { id: 'vz1600', name: 'Vollziegel 1600 kg/m³', gruppe: 'Mauerwerk', lambda: 0.68, quelle: 'DIN 4108-4, Tab. 1', farbe: '#e8c9b8' },
    { id: 'stb1', name: 'Stahlbeton, 1 % Bewehrung', gruppe: 'Beton', lambda: 2.3, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#c4c9ce' },
    { id: 'stb2', name: 'Stahlbeton, 2 % Bewehrung', gruppe: 'Beton', lambda: 2.5, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#b9bfc5' },
    { id: 'zementestrich', name: 'Zementestrich 2000 kg/m³', gruppe: 'Estrich und Putz', lambda: 1.4, quelle: 'DIN 4108-4, Tab. 1', farbe: '#e4e0d8' },
    { id: 'kalkzementputz', name: 'Kalkzementputz 1800 kg/m³', gruppe: 'Estrich und Putz', lambda: 1.0, quelle: 'DIN 4108-4, Tab. 1', farbe: '#ece8e1' },
    { id: 'gipsplatte', name: 'Gipsplatte 900 kg/m³', gruppe: 'Estrich und Putz', lambda: 0.25, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#f1efea' },
    { id: 'eps035', name: 'EPS, WLS 035', gruppe: 'Dämmstoffe', lambda: 0.035, quelle: 'Produktwert (Wärmeleitfähigkeitsstufe 035)', farbe: '#e6f5fc' },
    { id: 'mw035', name: 'Mineralwolle, WLS 035', gruppe: 'Dämmstoffe', lambda: 0.035, quelle: 'Produktwert (Wärmeleitfähigkeitsstufe 035)', farbe: '#eef6e4' },
    { id: 'xps035', name: 'XPS, WLS 035', gruppe: 'Dämmstoffe', lambda: 0.035, quelle: 'Produktwert (Wärmeleitfähigkeitsstufe 035)', farbe: '#e3eefb' },
    { id: 'pur025', name: 'PUR/PIR, WLS 025', gruppe: 'Dämmstoffe', lambda: 0.025, quelle: 'Produktwert (Wärmeleitfähigkeitsstufe 025)', farbe: '#f3ecf8' },
    { id: 'holzfaser040', name: 'Holzfaserdämmplatte, WLS 040', gruppe: 'Dämmstoffe', lambda: 0.04, quelle: 'Produktwert (Wärmeleitfähigkeitsstufe 040)', farbe: '#efe6d6' },
    { id: 'kragplatte80', name: 'Kragplattenanschluss, Dämmkörper 80 mm (λ_eq)', gruppe: 'Dämmstoffe', lambda: 0.15, quelle: 'Vorschlag, Produktwert beim Hersteller nachsehen', farbe: '#d8eedf' },
    { id: 'nadelholz', name: 'Nadelholz 500 kg/m³', gruppe: 'Holz', lambda: 0.13, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#ead9b5' },
    { id: 'osb', name: 'OSB-Platte 650 kg/m³', gruppe: 'Holz', lambda: 0.13, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#e3cfa3' },
    { id: 'stahl', name: 'Baustahl', gruppe: 'Metalle', lambda: 50, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#a9b4bd' },
    { id: 'edelstahl', name: 'Nichtrostender Stahl', gruppe: 'Metalle', lambda: 17, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#bcc5cc' },
    { id: 'aluminium', name: 'Aluminiumlegierung', gruppe: 'Metalle', lambda: 160, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#c9d0d6' },
    { id: 'glas', name: 'Natronkalkglas', gruppe: 'Glas und Kunststoffe', lambda: 1.0, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#d4ecf4' },
    { id: 'pehd', name: 'Polyethylen, hohe Dichte', gruppe: 'Glas und Kunststoffe', lambda: 0.5, quelle: 'DIN EN ISO 10456, Tab. 3', farbe: '#e0e4ea' },
    { id: 'ton', name: 'Erdreich: Ton oder Schluff', gruppe: 'Erdreich', lambda: 1.5, quelle: 'DIN EN ISO 13370', farbe: '#d8cdb8' },
    { id: 'sand', name: 'Erdreich: Sand oder Kies', gruppe: 'Erdreich', lambda: 2.0, quelle: 'DIN EN ISO 13370', farbe: '#e2d6bd' },
  ].map(s => Object.assign({ pruefen: true }, s));

  // Wärmeübergangswiderstände als Vorlagen für Luftbereiche (h = 1/R)
  const NORMWERTE = [
    { id: 'rsi013', name: 'innen, R_si 0,13 (U-Wert, ψ)', R: 0.13, quelle: 'DIN EN ISO 6946, Wärmestrom horizontal' },
    { id: 'rsi025', name: 'innen, R_si 0,25 (Schimmel, f_Rsi)', R: 0.25, quelle: 'DIN 4108-2, Mindestwärmeschutz an Wärmebrücken' },
    { id: 'rse004', name: 'außen, R_se 0,04', R: 0.04, quelle: 'DIN EN ISO 6946' },
  ];

  const luft = (bereich, x0, x1, y0, y1) => ({ art: 'luft', bereich, x0, x1, y0, y1 });
  const mat = (stoff, x0, x1, y0, y1) => ({ art: 'material', stoff, x0, x1, y0, y1 });
  const aussenLuft = () => ({ id: 'aussen', name: 'Außenluft', rolle: 'aussen', T: -5, h: 25, vorlage: 'rse004', unendlich: false });

  const balkon = trennung => ({
    version: 1, netz: 25, grenze: 12.6,
    bereiche: [
      aussenLuft(),
      { id: 'oben', name: 'Raum oben', rolle: 'innen', T: 20, h: 1 / 0.13, vorlage: 'rsi013', unendlich: false },
      { id: 'unten', name: 'Raum unten', rolle: 'innen', T: 20, h: 1 / 0.13, vorlage: 'rsi013', unendlich: false },
    ],
    rechtecke: [
      luft('aussen', -1700, 0, 0, 2200), luft('unten', 315, 1315, 0, 1000), luft('oben', 315, 1315, 1200, 2200),
      mat('eps035', 0, 140, 0, 2200), mat('ks1800', 140, 315, 0, 2200), mat('stb1', -1500, 1315, 1000, 1200),
    ].concat(trennung ? [mat('kragplatte80', 60, 140, 1000, 1200)] : []),
    sonden: [{ name: 'Ecke Decke oben', x: 315, y: 1200 }, { name: 'Ecke Decke unten', x: 315, y: 1000 }],
    eigeneStoffe: [],
  });

  const VORLAGEN = [
    {
      id: 'aussenwand', titel: 'Außenwand (P1 Vorzeigebeispiel)',
      text: 'Kalksandstein 175 mm mit 140 mm EPS als Streifen von 1 m Höhe, oben und unten adiabat. Innen h = 7,7 W/(m²·K) bei 20 °C, außen h = 25 W/(m²·K) bei −10 °C wie in P1 Fall b. Das Feld ist eindimensional: q = 6,90 W/m², ψ = 0.',
      modell: () => ({
        version: 1, netz: 20, grenze: null,
        bereiche: [
          { id: 'aussen', name: 'Außenluft', rolle: 'aussen', T: -10, h: 25, vorlage: 'rse004', unendlich: false },
          { id: 'raum', name: 'Raum', rolle: 'innen', T: 20, h: 7.7, vorlage: 'frei', unendlich: false },
        ],
        rechtecke: [luft('aussen', -200, 0, 0, 1000), luft('raum', 315, 515, 0, 1000), mat('eps035', 0, 140, 0, 1000), mat('ks1800', 140, 315, 0, 1000)],
        sonden: [{ name: 'Oberfläche innen', x: 315, y: 500 }, { name: 'Trennfuge', x: 140, y: 500 }],
        eigeneStoffe: [],
      }),
    },
    {
      id: 'aussenecke', titel: 'Außenecke (P1 Übung 2)',
      text: 'Geometrische Wärmebrücke: Kalksandstein 175 mm mit 140 mm EPS, Schenkel 1 m. Mindestwärmeschutz nach DIN 4108-2: innen R_si 0,25 bei 20 °C, außen R_se 0,04 bei −5 °C.',
      modell: () => ({
        version: 1, netz: 20, grenze: 12.6,
        bereiche: [aussenLuft(), { id: 'raum', name: 'Raum', rolle: 'innen', T: 20, h: 4, vorlage: 'rsi025', unendlich: false }],
        rechtecke: [
          luft('aussen', -150, 1000, -150, 0), luft('aussen', -150, 0, 0, 1000), luft('raum', 315, 1000, 315, 1000),
          mat('eps035', 0, 1000, 0, 140), mat('eps035', 0, 140, 140, 1000), mat('ks1800', 140, 1000, 140, 315), mat('ks1800', 140, 315, 315, 1000),
        ],
        sonden: [{ name: 'Ecke innen', x: 315, y: 315 }, { name: 'Wand ungestört', x: 1000, y: 315 }],
        eigeneStoffe: [],
      }),
    },
    {
      id: 'balkonplatte', titel: 'Balkonplatte ohne Trennung (P3, Vorschlag)',
      text: 'Stahlbetondecke 200 mm läuft durch die Außenwand (Kalksandstein 175 mm, EPS 140 mm) und kragt 1,50 m aus. Schnitte 1 m über und unter der Decke und 1 m im Raum. Innen R_si 0,13 bei 20 °C, außen R_se 0,04 bei −5 °C. Maße und Werte sind ein Vorschlag.',
      modell: () => balkon(false),
    },
    {
      id: 'balkonplatte-trennung', titel: 'Balkonplatte mit thermischer Trennung (P3, Vorschlag)',
      text: 'Wie die Balkonplatte, aber mit Kragplattenanschluss: Dämmkörper 80 mm in der Dämmebene mit äquivalentem λ (Vorschlag 0,15 W/(m·K), Produktwert beim Hersteller nachsehen).',
      modell: () => balkon(true),
    },
  ];

  // Modell aus Link, JSON oder Browserspeicher prüfen und in eine saubere Form bringen
  function normalisieren(m) {
    if (!m || typeof m !== 'object' || !Array.isArray(m.rechtecke) || !Array.isArray(m.bereiche)) throw new Error('Kein gültiges Modell.');
    const zahl = (v, d) => (Number.isFinite(+v) ? +v : d);
    const text = (v, d) => (typeof v === 'string' && v ? v.slice(0, 120) : d);
    return {
      version: 1,
      netz: Math.min(100, Math.max(5, zahl(m.netz, 20))),
      grenze: m.grenze === null || m.grenze === undefined || m.grenze === '' ? null : zahl(m.grenze, null),
      bereiche: m.bereiche.map((b, i) => ({
        id: text(b.id, 'b' + i), name: text(b.name, 'Bereich ' + (i + 1)),
        rolle: ['innen', 'aussen', 'sonstige'].includes(b.rolle) ? b.rolle : 'sonstige',
        T: zahl(b.T, 20), h: zahl(b.h, 7.7), vorlage: text(b.vorlage, 'frei'), unendlich: !!b.unendlich,
      })),
      rechtecke: m.rechtecke.map(r => {
        const x0 = zahl(r.x0, 0), x1 = zahl(r.x1, 0), y0 = zahl(r.y0, 0), y1 = zahl(r.y1, 0);
        const box = { x0: Math.min(x0, x1), x1: Math.max(x0, x1), y0: Math.min(y0, y1), y1: Math.max(y0, y1) };
        return r.art === 'luft' ? Object.assign({ art: 'luft', bereich: text(r.bereich, '') }, box) : Object.assign({ art: 'material', stoff: text(r.stoff, '') }, box);
      }),
      sonden: (Array.isArray(m.sonden) ? m.sonden : []).map((s, i) => ({ name: text(s.name, 'S' + (i + 1)), x: zahl(s.x, 0), y: zahl(s.y, 0) })),
      eigeneStoffe: (Array.isArray(m.eigeneStoffe) ? m.eigeneStoffe : []).map((s, i) => ({ id: text(s.id, 'eigen' + i), name: text(s.name, 'Eigenes Material'), lambda: zahl(s.lambda, 1) })),
    };
  }

  // Modell im Link: JSON, mit deflate komprimiert (wo der Browser das kann), als base64url
  const zuB64 = bytes => {
    let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  };
  const ausB64 = t => {
    const s = atob(t.replace(/-/g, '+').replace(/_/g, '/'));
    return Uint8Array.from(s, c => c.charCodeAt(0));
  };
  async function kodieren(modell) {
    const roh = new TextEncoder().encode(JSON.stringify(modell));
    if (typeof CompressionStream === 'undefined') return 'j' + zuB64(roh);
    const strom = new Blob([roh]).stream().pipeThrough(new CompressionStream('deflate-raw'));
    return 'z' + zuB64(new Uint8Array(await new Response(strom).arrayBuffer()));
  }
  async function dekodieren(t) {
    let bytes = ausB64(t.slice(1));
    if (t[0] === 'z') {
      const strom = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
      bytes = new Uint8Array(await new Response(strom).arrayBuffer());
    } else if (t[0] !== 'j') throw new Error('Unbekanntes Linkformat.');
    return normalisieren(JSON.parse(new TextDecoder().decode(bytes)));
  }

  const api = { BIBLIOTHEK, NORMWERTE, VORLAGEN, normalisieren, kodieren, dekodieren };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.WandschnittDaten = api;
})(typeof window !== 'undefined' ? window : this);
