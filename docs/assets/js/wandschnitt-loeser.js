// Wandschnitt 2D, Rechenkern: stationäre Wärmeleitung in 2D auf einem Rechteckraster, ohne DOM
// (läuft im Browser und in Node für die Tests in tools/wandschnitt/).
// Bilineare Vierecke, Konvektion als Robin-Rand, h → ∞ als Strafterm, Knoten nach Reverse Cuthill-McKee
// nummeriert, Hüllen-Cholesky. Maße im Modell in mm, gerechnet wird in m; Wärmeströme in W/m Bauteiltiefe.
(function (root) {
  'use strict';

  // Elementmatrix Q4 für ein Rechteck a x b: K = λ (b/(6a) KA + a/(6b) KB), Knoten ab unten links gegen den Uhrzeigersinn
  const KA = [2, -2, -1, 1, -2, 2, 1, -1, -1, 1, 2, -2, 1, -1, -2, 2];
  const KB = [2, 1, -1, -2, 1, 2, -2, -1, -1, -2, 2, 1, -2, -1, 1, 2];
  const H_UNENDLICH = 1e8;   // W/(m²·K): Oberfläche nimmt praktisch die Lufttemperatur an
  const jetzt = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
  const rund = v => Math.round(v * 1000) / 1000;

  // Zellweiten eines Intervalls: an beiden Enden hMin, zur Mitte hin um den Faktor q gröber, höchstens hMax
  function teile(L, hMax, hMin, q) {
    if (L <= 2 * hMin) return [L];
    const halb = [];
    let s = 0, d = hMin;
    while (s + d <= L / 2) { halb.push(d); s += d; d = Math.min(hMax, d * q); }
    const rest = L - 2 * s, n = Math.ceil(rest / hMax);
    const mitte = rest > 0.5 * d ? new Array(n).fill(rest / n) : [];
    const g = halb.concat(mitte, halb.slice().reverse());
    const summe = g.reduce((a, b) => a + b, 0);
    return g.map(v => v * L / summe);
  }

  // Rasterlinien: alle Rechteckkanten liegen auf Linien, dazwischen gestuft
  function linien(knicke, hMax) {
    const k = Array.from(new Set(knicke.map(rund))).sort((a, b) => a - b);
    const hMin = Math.max(0.5, hMax / 4), xs = [k[0]];
    for (let i = 1; i < k.length; i++) {
      const g = teile(k[i] - k[i - 1], hMax, hMin, 1.4);
      let x = k[i - 1];
      for (let j = 0; j < g.length - 1; j++) { x += g[j]; xs.push(x); }
      xs.push(k[i]);
    }
    return xs;
  }

  // Index der Zelle, in der v liegt (xs aufsteigend), -1 außerhalb
  function zelleBei(xs, v) {
    if (!(v >= xs[0] && v <= xs[xs.length - 1])) return -1;
    let lo = 0, hi = xs.length - 2;
    while (lo < hi) { const m = (lo + hi + 1) >> 1; if (xs[m] <= v) lo = m; else hi = m - 1; }
    return lo;
  }

  function stoffTabelle(modell, bibliothek) {
    const stoffe = new Map();
    for (const s of bibliothek || []) stoffe.set(s.id, s);
    for (const s of modell.eigeneStoffe || []) stoffe.set(s.id, Object.assign({ eigen: true }, s));
    return stoffe;
  }

  // Effektives h eines Luftbereichs in W/(m²·K)
  const hVon = b => (b.unendlich ? H_UNENDLICH : b.h);

  function rechnen(modell, bibliothek) {
    const t0 = jetzt();
    const stoffe = stoffTabelle(modell, bibliothek);
    const bereiche = (modell.bereiche || []).map(b => Object.assign({}, b));
    const bIndex = new Map(bereiche.map((b, i) => [b.id, i]));
    const fehler = [];
    const rechtecke = (modell.rechtecke || []).filter(r => r.x1 - r.x0 > 1e-6 && r.y1 - r.y0 > 1e-6);
    rechtecke.forEach((r, k) => {
      if (r.art === 'luft' && !bIndex.has(r.bereich)) fehler.push(`Rechteck ${k + 1}: Luftbereich „${r.bereich}“ fehlt.`);
      if (r.art !== 'luft' && !(stoffe.get(r.stoff) && stoffe.get(r.stoff).lambda > 0)) fehler.push(`Rechteck ${k + 1}: Material fehlt oder λ ist nicht größer als null.`);
    });
    for (const b of bereiche) {
      if (!b.unendlich && !(b.h > 0)) fehler.push(`Luftbereich „${b.name}“: h muss größer als null sein.`);
      if (!Number.isFinite(b.T)) fehler.push(`Luftbereich „${b.name}“: Temperatur fehlt.`);
    }
    if (!rechtecke.some(r => r.art !== 'luft')) fehler.push('Es gibt noch kein Materialrechteck.');
    if (fehler.length) return { ok: false, fehler };

    const hMax = Math.min(200, Math.max(2, modell.netz || 20));
    const xs = linien(rechtecke.flatMap(r => [r.x0, r.x1]), hMax);
    const ys = linien(rechtecke.flatMap(r => [r.y0, r.y1]), hMax);
    const NX = xs.length, NY = ys.length, EX = NX - 1, EY = NY - 1;
    const ix = new Map(xs.map((v, i) => [rund(v), i])), iy = new Map(ys.map((v, i) => [rund(v), i]));

    // Zellen einordnen: spätere Rechtecke überdecken frühere. art 0 leer, 1 Material, 2 Luft
    const art = new Uint8Array(EX * EY), stoffDer = new Int32Array(EX * EY).fill(-1), bereichDer = new Int32Array(EX * EY).fill(-1);
    const stoffListe = [], stoffNr = new Map();
    for (const r of rechtecke) {
      const i0 = ix.get(rund(r.x0)), i1 = ix.get(rund(r.x1)), j0 = iy.get(rund(r.y0)), j1 = iy.get(rund(r.y1));
      let wert = -1;
      if (r.art === 'luft') wert = bIndex.get(r.bereich);
      else {
        if (!stoffNr.has(r.stoff)) { stoffNr.set(r.stoff, stoffListe.length); stoffListe.push(stoffe.get(r.stoff)); }
        wert = stoffNr.get(r.stoff);
      }
      for (let j = j0; j < j1; j++) for (let i = i0; i < i1; i++) {
        const c = i + j * EX;
        if (r.art === 'luft') { art[c] = 2; bereichDer[c] = wert; stoffDer[c] = -1; }
        else { art[c] = 1; stoffDer[c] = wert; bereichDer[c] = -1; }
      }
    }
    const istMaterial = (i, j) => i >= 0 && j >= 0 && i < EX && j < EY && art[i + j * EX] === 1;

    // Knoten der Materialzellen und Randkanten an Luftbereichen
    const id = new Int32Array(NX * NY).fill(-1), el = [], raender = [];
    let n = 0;
    for (let j = 0; j < EY; j++) for (let i = 0; i < EX; i++) {
      const c = i + j * EX;
      if (art[c] !== 1) continue;
      const g = [i + j * NX, i + 1 + j * NX, i + 1 + (j + 1) * NX, i + (j + 1) * NX];
      for (const k of g) if (id[k] < 0) id[k] = n++;
      const e = { n: g.map(k => id[k]), a: (xs[i + 1] - xs[i]) / 1000, b: (ys[j + 1] - ys[j]) / 1000, l: stoffListe[stoffDer[c]].lambda };
      el.push(e);
      for (const [p, q, ni, nj] of [[0, 1, i, j - 1], [1, 2, i + 1, j], [2, 3, i, j + 1], [3, 0, i - 1, j]]) {
        if (ni < 0 || nj < 0 || ni >= EX || nj >= EY) continue;
        const cn = ni + nj * EX;
        if (art[cn] !== 2) continue;
        const L = (p % 2 === 0 ? xs[i + 1] - xs[i] : ys[j + 1] - ys[j]) / 1000;
        raender.push({ a: e.n[p], b: e.n[q], ga: g[p], gb: g[q], L, z: bereichDer[cn] });
      }
    }

    // Reverse Cuthill-McKee je zusammenhängendem Teil; jeder Teil braucht einen Rand an einem Luftbereich
    const nb = Array.from({ length: n }, () => new Set());
    for (const e of el) for (const a of e.n) for (const b of e.n) if (a !== b) nb[a].add(b);
    const adj = nb.map(s => Array.from(s));
    const amRand = new Uint8Array(n);
    for (const r of raender) { amRand[r.a] = 1; amRand[r.b] = 1; }
    const besucht = new Uint8Array(n), order = [];
    const bfs = s => {
      const seen = new Uint8Array(n), q = [s];
      seen[s] = 1;
      for (let k = 0; k < q.length; k++) for (const w of adj[q[k]]) if (!seen[w]) { seen[w] = 1; q.push(w); }
      return q;
    };
    for (let s0 = 0; s0 < n; s0++) {
      if (besucht[s0]) continue;
      const teil = bfs(s0);
      if (!teil.some(k => amRand[k])) {
        return { ok: false, fehler: ['Ein Materialbereich berührt keinen Luftbereich und hat damit keine Randbedingung. Legen Sie einen Luftbereich an oder verbinden Sie das Material.'] };
      }
      const start = bfs(teil[teil.length - 1]).pop();
      const teilOrder = [start];
      besucht[start] = 1;
      for (let k = 0; k < teilOrder.length; k++) {
        const frei = adj[teilOrder[k]].filter(w => !besucht[w]).sort((a, b) => adj[a].length - adj[b].length);
        for (const w of frei) { besucht[w] = 1; teilOrder.push(w); }
      }
      for (const k of teilOrder) order.push(k);
    }
    const perm = new Int32Array(n);
    for (let k = 0; k < n; k++) perm[order[n - 1 - k]] = k;

    // Hülle: Zeile i speichert L[i][fst[i]..i]
    const fst = Int32Array.from({ length: n }, (_, i) => i);
    for (const e of el) {
      const q = e.n.map(k => perm[k]), lo = Math.min(q[0], q[1], q[2], q[3]);
      for (const r of q) if (lo < fst[r]) fst[r] = lo;
    }
    const off = new Int32Array(n + 1);
    for (let i = 0; i < n; i++) off[i + 1] = off[i] + i - fst[i] + 1;
    const E = new Float64Array(off[n]), x = new Float64Array(n);
    const add = (a, b, v) => { if (a >= b) E[off[a] + b - fst[a]] += v; };
    for (const e of el) {
      const c1 = e.l * e.b / (6 * e.a), c2 = e.l * e.a / (6 * e.b);
      for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) add(perm[e.n[r]], perm[e.n[c]], c1 * KA[4 * r + c] + c2 * KB[4 * r + c]);
    }
    for (const r of raender) {
      const b = bereiche[r.z], h = hVon(b), a = perm[r.a], c = perm[r.b];
      add(a, a, h * r.L / 3); add(c, c, h * r.L / 3); add(Math.max(a, c), Math.min(a, c), h * r.L / 6);
      x[a] += h * b.T * r.L / 2; x[c] += h * b.T * r.L / 2;
    }
    const t1 = jetzt();

    // Cholesky K = L L^T zeilenweise in der Hülle, dann Vorwärts- und Rückwärtseinsetzen
    for (let i = 0; i < n; i++) {
      const oi = off[i] - fst[i];
      for (let j = fst[i]; j < i; j++) {
        const oj = off[j] - fst[j];
        let s = E[oi + j];
        for (let k = Math.max(fst[i], fst[j]); k < j; k++) s -= E[oi + k] * E[oj + k];
        E[oi + j] = s / E[oj + j];
      }
      let s = E[oi + i];
      for (let k = fst[i]; k < i; k++) s -= E[oi + k] * E[oi + k];
      if (!(s > 0)) return { ok: false, fehler: ['Das Gleichungssystem ist nicht lösbar. Prüfen Sie Materialwerte und Randbedingungen.'] };
      E[oi + i] = Math.sqrt(s);
    }
    for (let i = 0; i < n; i++) { const oi = off[i] - fst[i]; let s = x[i]; for (let k = fst[i]; k < i; k++) s -= E[oi + k] * x[k]; x[i] = s / E[oi + i]; }
    for (let i = n - 1; i >= 0; i--) { const oi = off[i] - fst[i], xi = (x[i] /= E[oi + i]); for (let k = fst[i]; k < i; k++) x[k] -= E[oi + k] * xi; }
    const t2 = jetzt();

    // Temperaturen auf dem Raster (NaN, wo kein Material ist)
    const T = new Float64Array(NX * NY).fill(NaN);
    let tMin = Infinity, tMax = -Infinity;
    for (let k = 0; k < NX * NY; k++) if (id[k] >= 0) {
      const v = x[perm[id[k]]];
      T[k] = v;
      if (v < tMin) tMin = v;
      if (v > tMax) tMax = v;
    }

    // Je Luftbereich: Wärmestrom in das Bauteil (W/m), kleinste und größte Oberflächentemperatur mit Ort
    const ort = k => [xs[k % NX], ys[(k / NX) | 0]];
    const auswertung = bereiche.map(b => ({ id: b.id, name: b.name, rolle: b.rolle, T: b.T, strom: 0, laenge: 0, tMin: null, tMax: null, ortMin: null, ortMax: null }));
    for (const r of raender) {
      const b = bereiche[r.z], z = auswertung[r.z], ta = T[r.ga], tb = T[r.gb];
      z.strom += (b.unendlich ? H_UNENDLICH : b.h) * r.L * (b.T - (ta + tb) / 2);
      z.laenge += r.L * 1000;
      for (const [k, t] of [[r.ga, ta], [r.gb, tb]]) {
        if (z.tMin === null || t < z.tMin) { z.tMin = t; z.ortMin = ort(k); }
        if (z.tMax === null || t > z.tMax) { z.tMax = t; z.ortMax = ort(k); }
      }
    }
    const beteiligt = auswertung.filter(z => z.laenge > 0);
    const bilanz = beteiligt.reduce((s, z) => s + z.strom, 0);

    const erg = {
      ok: true, xs, ys, NX, NY, EX, EY, art, stoffDer, bereichDer, stoffListe, bereiche, T, tMin, tMax,
      knoten: n, elemente: el.length, ms: { aufbau: t1 - t0, loesen: t2 - t1, gesamt: jetzt() - t0 },
      auswertung: beteiligt, bilanz,
    };

    // f_Rsi je Innenbereich, wenn alle Außenbereiche dieselbe Temperatur haben
    const aussenT = Array.from(new Set(beteiligt.filter(z => z.rolle === 'aussen').map(z => z.T)));
    erg.frsi = [];
    if (aussenT.length === 1) {
      for (const z of beteiligt) if (z.rolle === 'innen' && z.T !== aussenT[0]) {
        erg.frsi.push({ id: z.id, name: z.name, wert: (z.tMin - aussenT[0]) / (z.T - aussenT[0]), tMin: z.tMin, ort: z.ortMin, Ti: z.T, Te: aussenT[0] });
      }
    }
    erg.psi = psiWert(erg);
    erg.ms.gesamt = jetzt() - t0;
    return erg;
  }

  // ψ nach DIN EN ISO 10211 für zwei Umgebungen: ψ = L2D − Σ U·l.
  // Flankierende Bauteile sind Schnittränder am Rand des Rechenbereichs, die durch Material von einem Innen- zu einem
  // Außenbereich laufen. U aus dem Schichtaufbau am Schnitt, l durch Abschreiten der Oberfläche vom Schnitt aus.
  function psiWert(erg) {
    const { xs, ys, EX, EY, art, stoffDer, bereichDer, stoffListe, bereiche, auswertung } = erg;
    const rollen = r => auswertung.filter(z => z.rolle === r);
    const innen = rollen('innen'), aussen = rollen('aussen'), sonst = rollen('sonstige');
    const Ti = Array.from(new Set(innen.map(z => z.T))), Te = Array.from(new Set(aussen.map(z => z.T)));
    if (!innen.length || !aussen.length) return { fehler: 'ψ braucht mindestens einen Innen- und einen Außenbereich am Bauteil.' };
    if (Ti.length > 1 || Te.length > 1 || sonst.length) {
      return { fehler: 'ψ braucht genau zwei Umgebungen: alle Innenbereiche mit gleicher Temperatur, alle Außenbereiche mit gleicher Temperatur und keine sonstigen Bereiche am Bauteil.' };
    }
    if (Ti[0] === Te[0]) return { fehler: 'Innen- und Außentemperatur sind gleich, ψ ist dann nicht bestimmt.' };
    const phi = innen.reduce((s, z) => s + z.strom, 0), L2D = phi / (Ti[0] - Te[0]);

    // Zugriff je Rand: t läuft entlang des Rands (Schichten), s vom Rand ins Innere (Bauteilachse)
    const raender = [
      { lage: 'rechts', nT: EY, nS: EX, zelle: (t, s) => [EX - 1 - s, t], dS: s => xs[EX - s] - xs[EX - 1 - s], dT: t => ys[t + 1] - ys[t], linie: t => ys[t], quer: 'x' },
      { lage: 'links', nT: EY, nS: EX, zelle: (t, s) => [s, t], dS: s => xs[s + 1] - xs[s], dT: t => ys[t + 1] - ys[t], linie: t => ys[t], quer: 'x' },
      { lage: 'oben', nT: EX, nS: EY, zelle: (t, s) => [t, EY - 1 - s], dS: s => ys[EY - s] - ys[EY - 1 - s], dT: t => xs[t + 1] - xs[t], linie: t => xs[t], quer: 'y' },
      { lage: 'unten', nT: EX, nS: EY, zelle: (t, s) => [t, s], dS: s => ys[s + 1] - ys[s], dT: t => xs[t + 1] - xs[t], linie: t => xs[t], quer: 'y' },
    ];
    const zelle = (R, t, s) => { const [i, j] = R.zelle(t, s); return i + j * EX; };
    const rolleDer = c => (art[c] === 2 ? bereiche[bereichDer[c]].rolle : null);
    // Länge der Oberfläche zwischen Materialzeile tm und Luftzeile tl mit der Rolle rolle, vom Rand aus abgeschritten (mm)
    const abschreiten = (R, tm, tl, rolle) => {
      let l = 0;
      for (let s = 0; s < R.nS; s++) {
        if (art[zelle(R, tm, s)] !== 1 || rolleDer(zelle(R, tl, s)) !== rolle) break;
        l += R.dS(s);
      }
      return l;
    };

    const elemente = [];
    for (const R of raender) {
      for (let t = 0; t < R.nT; t++) {
        if (art[zelle(R, t, 0)] !== 1) continue;
        let tb = t;
        while (tb + 1 < R.nT && art[zelle(R, tb + 1, 0)] === 1) tb++;
        const ta = t;
        t = tb;
        if (ta === 0 || tb === R.nT - 1) continue;
        const rA = rolleDer(zelle(R, ta - 1, 0)), rB = rolleDer(zelle(R, tb + 1, 0));
        if (!((rA === 'aussen' && rB === 'innen') || (rA === 'innen' && rB === 'aussen'))) continue;
        const aussenUnten = rA === 'aussen';
        const zA = bereiche[bereichDer[zelle(R, ta - 1, 0)]], zB = bereiche[bereichDer[zelle(R, tb + 1, 0)]];
        const zAussen = aussenUnten ? zA : zB, zInnen = aussenUnten ? zB : zA;
        // Schichten von außen nach innen, gleiche Nachbarn zusammengefasst
        const folge = [];
        for (let k = ta; k <= tb; k++) folge.push(k);
        if (!aussenUnten) folge.reverse();
        const schichten = [];
        let Rw = 0;
        for (const k of folge) {
          const st = stoffListe[stoffDer[zelle(R, k, 0)]], d = R.dT(k);
          Rw += d / 1000 / st.lambda;
          const letzte = schichten[schichten.length - 1];
          if (letzte && letzte.stoff === st) letzte.d += d;
          else schichten.push({ stoff: st, name: st.name, lambda: st.lambda, d });
        }
        const Rsi = zInnen.unendlich ? 0 : 1 / zInnen.h, Rse = zAussen.unendlich ? 0 : 1 / zAussen.h;
        const U = 1 / (Rsi + Rw + Rse);
        const tInnen = aussenUnten ? tb : ta, tAussen = aussenUnten ? ta : tb;
        const lAussen = abschreiten(R, tAussen, aussenUnten ? ta - 1 : tb + 1, 'aussen');
        const lInnen = abschreiten(R, tInnen, aussenUnten ? tb + 1 : ta - 1, 'innen');
        elemente.push({
          lage: R.lage, quer: R.quer, schichten: schichten.map(({ name, lambda, d }) => ({ name, lambda, d })),
          Rsi, Rse, R: Rw, U, lAussen, lInnen, wegAussen: lAussen, wegInnen: lInnen,
          linieAussen: aussenUnten ? R.linie(ta) : R.linie(tb + 1), linieInnen: aussenUnten ? R.linie(tb + 1) : R.linie(ta),
          aussenSeite: aussenUnten ? -1 : 1, gesamt: R.quer === 'x' ? xs[xs.length - 1] - xs[0] : ys[ys.length - 1] - ys[0],
        });
      }
    }
    // Zwei flankierende Bauteile auf derselben Linie von gegenüberliegenden Rändern:
    // - Lücke dazwischen (z. B. Wand über und unter einer Balkonplatte): beim Außenmaß läuft die Außenfläche
    //   über den Anschluss durch, die Lücke wird hälftig aufgeteilt; das Innenmaß endet am Anschluss
    // - Überlappung (gerade Wand ohne Anschluss, oben und unten geschnitten): dieselbe Wand, die Länge wird geteilt
    for (let a = 0; a < elemente.length; a++) for (let b = a + 1; b < elemente.length; b++) {
      const A = elemente[a], B = elemente[b];
      if (A.quer !== B.quer || A.lage === B.lage || A.aussenSeite !== B.aussenSeite) continue;
      if (Math.abs(A.linieAussen - B.linieAussen) < 1e-6) {
        const luecke = A.gesamt - A.wegAussen - B.wegAussen;
        if (luecke > 0) { A.lAussen = A.wegAussen + luecke / 2; B.lAussen = B.wegAussen + luecke / 2; }
        else if (luecke < 0) { const f = A.gesamt / (A.wegAussen + B.wegAussen); A.lAussen = A.wegAussen * f; B.lAussen = B.wegAussen * f; }
      }
      if (Math.abs(A.linieInnen - B.linieInnen) < 1e-6 && A.wegInnen + B.wegInnen > A.gesamt) {
        const f = A.gesamt / (A.wegInnen + B.wegInnen);
        A.lInnen = A.wegInnen * f; B.lInnen = B.wegInnen * f;
      }
    }
    if (!elemente.length) return { fehler: 'Kein flankierendes Bauteil gefunden: Ein Schnittrand am Rand des Modells muss durch Material von einem Innen- zu einem Außenbereich laufen.' };
    const summe = key => elemente.reduce((s, e) => s + e.U * e[key] / 1000, 0);
    return {
      L2D, phi, Ti: Ti[0], Te: Te[0],
      elemente: elemente.map(({ lage, schichten, Rsi, Rse, R, U, lAussen, lInnen }) => ({ lage, schichten, Rsi, Rse, R, U, lAussen, lInnen })),
      psiAussen: L2D - summe('lAussen'), psiInnen: L2D - summe('lInnen'),
    };
  }

  // Temperatur und Wärmestromdichte q = −λ grad T an einer Stelle (mm); null außerhalb des Materials
  function sonde(erg, px, py) {
    const { xs, ys, NX, EX, art, T } = erg;
    const i0 = zelleBei(xs, px), j0 = zelleBei(ys, py);
    if (i0 < 0 || j0 < 0) return null;
    // Liegt die Stelle auf einer Rasterlinie (z. B. eine Ecke an der Oberfläche), zählt auch die Nachbarzelle
    const is = Math.abs(px - xs[i0]) < 1e-6 && i0 > 0 ? [i0, i0 - 1] : [i0];
    const js = Math.abs(py - ys[j0]) < 1e-6 && j0 > 0 ? [j0, j0 - 1] : [j0];
    let i = -1, j = -1;
    for (const a of is) for (const b of js) if (i < 0 && art[a + b * EX] === 1) { i = a; j = b; }
    if (i < 0) return null;
    const k = i + j * NX;
    const a = xs[i + 1] - xs[i], b = ys[j + 1] - ys[j], fx = (px - xs[i]) / a, fy = (py - ys[j]) / b;
    const t00 = T[k], t10 = T[k + 1], t01 = T[k + NX], t11 = T[k + NX + 1];
    const t = (1 - fy) * ((1 - fx) * t00 + fx * t10) + fy * ((1 - fx) * t01 + fx * t11);
    const gx = ((1 - fy) * (t10 - t00) + fy * (t11 - t01)) / (a / 1000);
    const gy = ((1 - fx) * (t01 - t00) + fx * (t11 - t10)) / (b / 1000);
    const lam = erg.stoffListe[erg.stoffDer[i + j * erg.EX]].lambda;
    return { T: t, qx: -lam * gx, qy: -lam * gy, q: lam * Math.hypot(gx, gy), stoff: erg.stoffListe[erg.stoffDer[i + j * erg.EX]] };
  }

  // Isotherme zum Wert w als Liste von Strecken [x1, y1, x2, y2] in mm (Marching Squares je Materialzelle)
  function isolinie(erg, w) {
    const { xs, ys, NX, EX, EY, art, T } = erg, seg = [];
    for (let j = 0; j < EY; j++) for (let i = 0; i < EX; i++) {
      if (art[i + j * EX] !== 1) continue;
      const k = i + j * NX, v = [T[k], T[k + 1], T[k + NX + 1], T[k + NX]];
      const code = (v[0] > w) | ((v[1] > w) << 1) | ((v[2] > w) << 2) | ((v[3] > w) << 3);
      if (code === 0 || code === 15) continue;
      const X = [xs[i], xs[i + 1], xs[i + 1], xs[i]], Y = [ys[j], ys[j], ys[j + 1], ys[j + 1]];
      const p = (a, b) => { const f = (w - v[a]) / (v[b] - v[a]); return [X[a] + f * (X[b] - X[a]), Y[a] + f * (Y[b] - Y[a])]; };
      const kante = [[0, 1], [1, 2], [3, 2], [0, 3]].map(([a, b]) => ((v[a] > w) !== (v[b] > w) ? p(a, b) : null));
      let paare;
      if (code === 5 || code === 10) {
        const mitteHoch = (v[0] + v[1] + v[2] + v[3]) / 4 > w;
        paare = (code === 5) === mitteHoch ? [[0, 1], [2, 3]] : [[3, 0], [1, 2]];
      } else {
        const k2 = [0, 1, 2, 3].filter(e => kante[e]);
        paare = [k2];
      }
      for (const [e1, e2] of paare) seg.push([kante[e1][0], kante[e1][1], kante[e2][0], kante[e2][1]]);
    }
    return seg;
  }

  const api = { rechnen, sonde, isolinie, zelleBei, linien, H_UNENDLICH };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.WandschnittLoeser = api;
})(typeof window !== 'undefined' ? window : this);
