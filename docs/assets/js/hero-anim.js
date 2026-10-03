/* Startseiten-Animation im Kopfbereich: die Vorzeigeaufgabe Rohr aus
   Praktikum 2 im Zeitraffer. Rohr aus Baustahl mit stationärer
   Wärmeleitung (innen 100 °C, außen 20 °C), durch die sieben Schritte des
   Simulations-Workflows aus dem Kurs bis zum Temperaturfeld. Läuft von
   selbst in Schleife, pausiert außerhalb des Sichtbereichs; bei reduzierter
   Bewegung steht das Endbild. Die Schritt-Leiste darunter ist anklickbar. */
(function () {
  'use strict';

  var STEPS = [
    { key: 'Material',   text: 'Baustahl mit λ = 60,5 W/(m·K)',                     t0: 0.0,  t1: 1.8 },
    { key: 'Geometrie',  text: 'Rohr: Länge 20 mm, Innen-Ø 10 mm, Außen-Ø 30 mm',     t0: 1.8,  t1: 4.2 },
    { key: 'Zuweisung',  text: 'Das Rohr bekommt den Werkstoff Baustahl',             t0: 4.2,  t1: 5.6 },
    { key: 'Netz',       text: 'Vernetzung mit Hexaeder-Elementen',                   t0: 5.6,  t1: 7.8 },
    { key: 'Randbed.',   text: 'Innenfläche 100 °C, Außenfläche 20 °C',               t0: 7.8,  t1: 10.4 },
    { key: 'Lösen',      text: 'Das Gleichungssystem wird gelöst',                    t0: 10.4, t1: 12.0 },
    { key: 'Auswertung', text: 'Die Temperatur fällt von innen 100 °C auf außen 20 °C', t0: 12.0, t1: 18.0 }
  ];
  var LOOP = 18.8;
  var STILL = 15.6; // Endbild bei reduzierter Bewegung

  // ANSYS-Legende: neun Bänder von Blau nach Rot
  var BANDS = [[0, 0, 255], [0, 178, 255], [0, 255, 255], [0, 255, 178], [0, 255, 0],
               [178, 255, 0], [255, 255, 0], [255, 178, 0], [255, 0, 0]];
  var LABELS = ['100 Max', '91,1', '82,2', '73,3', '64,4', '55,6', '46,7', '37,8', '28,9', '20 Min'];
  var STEEL = [139, 156, 171];
  // Texel der Farbtabelle: 0 bis 8 Legende, 12 Stahl, 15 CAD-Körper
  var U_STEEL = 12.5 / 16, U_CAD = 15.5 / 16;

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function span(t, a, b) { return clamp01((t - a) / (b - a)); }
  function smooth(v) { v = clamp01(v); return v * v * (3 - 2 * v); }
  function backOut(v) { v = clamp01(v); var c = 1.70158; return 1 + (c + 1) * Math.pow(v - 1, 3) + c * Math.pow(v - 1, 2); }

  function init() {
    var host = document.querySelector('.kurs-anim');
    if (!host || !window.THREE || host.getAttribute('data-ready')) return;
    var renderer;
    try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { return; }
    host.setAttribute('data-ready', '1');
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;

    // ---------- DOM: Bühne, Einblendungen, Schritt-Leiste ----------
    var stage = document.createElement('div');
    stage.className = 'kurs-anim-stage';
    host.appendChild(stage);
    var canvas = renderer.domElement;
    canvas.className = 'kurs-anim-canvas';
    stage.appendChild(canvas);

    function overlay(cls, html) {
      var d = document.createElement('div');
      d.className = 'kurs-anim-ov ' + cls;
      d.innerHTML = '<div class="kurs-ov-in">' + html + '</div>';
      stage.appendChild(d);
      return d;
    }
    var ovMat = overlay('kurs-anim-tag', '<b>Baustahl</b><span>λ = 60,5 W/(m·K)</span>');
    var ovDim = overlay('kurs-anim-dimlabel', 'Ø 30 mm');
    var ovHot = overlay('kurs-anim-bclabel kurs-anim-bclabel--hot', 'innen 100 °C');
    var ovCold = overlay('kurs-anim-bclabel kurs-anim-bclabel--cold', 'außen 20 °C');
    var ovMax = overlay('kurs-anim-flag', '<i></i><span><b>Max</b> 100 °C</span>');
    var ovMin = overlay('kurs-anim-flag kurs-anim-flag--min', '<i></i><span><b>Min</b> 20 °C</span>');
    var bands = '', labs = '';
    for (var b = BANDS.length - 1; b >= 0; b--) bands += '<i style="background:rgb(' + BANDS[b].join(',') + ')"></i>';
    for (var l = 0; l < LABELS.length; l++) labs += '<span>' + LABELS[l] + '</span>';
    var legend = overlay('kurs-anim-legend',
      '<b>Temperatur</b><em>Einheit: °C</em>' +
      '<div class="kurs-leg"><div class="kurs-leg-bar">' + bands + '</div><div class="kurs-leg-lab">' + labs + '</div></div>');

    var track = document.createElement('div');
    track.className = 'kurs-anim-track';
    track.innerHTML = STEPS.map(function (s, i) {
      return '<button type="button" data-i="' + i + '" title="' + (i + 1) + ' · ' + s.key + '"><i></i><span>' + s.key + '</span></button>';
    }).join('');
    host.appendChild(track);
    var trackBtns = track.querySelectorAll('button');
    var cap = document.createElement('div');
    cap.className = 'kurs-anim-cap';
    cap.setAttribute('aria-live', 'off');
    host.appendChild(cap);

    // ---------- Szene: Rohrachse entlang x, 1 Einheit = 5 mm ----------
    var L = 4, RI = 1, RA = 3;           // Länge 20 mm, Innen-Ø 10 mm, Außen-Ø 30 mm
    var NX = 8, NR = 4, NT = 32;          // Elemente axial, radial, am Umfang
    var Y0 = -RA - 0.55;                  // Boden für den Schatten
    var LNRATIO = Math.log(RA / RI);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(30, 1.6, 0.1, 120);
    var hemi = new THREE.HemisphereLight(0xffffff, 0x7d8a94, 0.9);
    scene.add(hemi);
    var sun = new THREE.DirectionalLight(0xffffff, 0.9);
    sun.position.set(6, 10, 7);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -8; sun.shadow.camera.right = 8;
    sun.shadow.camera.top = 8; sun.shadow.camera.bottom = -8;
    scene.add(sun);
    var ground = new THREE.Mesh(new THREE.PlaneGeometry(40, 24), new THREE.ShadowMaterial({ opacity: 0.13 }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = Y0;
    ground.receiveShadow = true;
    scene.add(ground);

    // 1 Material: Werkstoffprobe als Kugel
    var sphere = new THREE.Mesh(
      new THREE.SphereGeometry(0.55, 48, 32),
      new THREE.MeshStandardMaterial({ color: 0xa3b1bc, metalness: 0.55, roughness: 0.26 })
    );
    scene.add(sphere);
    var SPH0 = new THREE.Vector3(-3.4, 2.9, 1.4);
    var SPH1 = new THREE.Vector3(0, (RI + RA) / 2, 0); // Ziel: Mitte der Rohrwand oben

    // 2 Geometrie: Kreisring-Profil (Skizze) und Endkreise der Extrusion
    var edgeMat = new THREE.LineBasicMaterial({ color: 0x0070a6, transparent: true, opacity: 0 });
    function ring(r) {
      var pts = [];
      for (var a = 0; a <= 64; a++) pts.push(new THREE.Vector3(0, r * Math.cos(a / 64 * 2 * Math.PI), r * Math.sin(a / 64 * 2 * Math.PI)));
      return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), edgeMat);
    }
    var sketch = new THREE.Group(), endRing = new THREE.Group();
    sketch.add(ring(RI)); sketch.add(ring(RA));
    endRing.add(ring(RI)); endRing.add(ring(RA));
    sketch.position.x = -L / 2;
    scene.add(sketch); scene.add(endRing);

    // Maßlinie: Außendurchmesser in der Ebene der Stirnfläche, seitlich daneben
    var dimMat = new THREE.LineBasicMaterial({ color: 0x0070a6, transparent: true, opacity: 0 });
    var dimConeMat = new THREE.MeshBasicMaterial({ color: 0x0070a6, transparent: true, opacity: 0 });
    var dimZ = -(RA + 0.75);
    var dim = new THREE.Group();
    dim.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, -RA, dimZ), new THREE.Vector3(0, RA, dimZ),
      new THREE.Vector3(0, RA, -0.3), new THREE.Vector3(0, RA, dimZ - 0.25),
      new THREE.Vector3(0, -RA, -0.3), new THREE.Vector3(0, -RA, dimZ - 0.25)
    ]), dimMat));
    [-1, 1].forEach(function (sgn) {
      var c = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.32, 12), dimConeMat);
      if (sgn < 0) c.rotation.z = Math.PI;
      c.position.set(0, sgn * (RA - 0.16), dimZ);
      dim.add(c);
    });
    dim.position.x = L / 2;
    scene.add(dim);

    // 3 bis 7: ein Netz aus Hexaeder-Elementen für alle Phasen
    // (CAD-Körper, Stahl, Netz, Ergebnis unterscheiden sich nur in der Farbe)
    var count = NX * NR * NT;
    var CORNERS = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]];
    // lokale Achsen: 0 = axial, 1 = radial, 2 = Umfang
    var FACES = [[1, 2, 6, 5], [0, 4, 7, 3], [3, 7, 6, 2], [0, 1, 5, 4], [4, 5, 6, 7], [0, 3, 2, 1]];
    var VPE = 36;
    var positions = new Float32Array(count * VPE * 3);
    var normals = new Float32Array(count * VPE * 3);
    var uvs = new Float32Array(count * VPE * 2);
    var vcols = new Float32Array(count * VPE * 3);
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('normal', new THREE.BufferAttribute(normals, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('color', new THREE.BufferAttribute(vcols, 3).setUsage(THREE.DynamicDrawUsage));

    var tdata = new Uint8Array(16 * 4);
    function fillTexture(cadRGB) {
      for (var ti = 0; ti < 16; ti++) {
        var c = ti < 9 ? BANDS[ti] : ti < 14 ? STEEL : cadRGB;
        tdata[ti * 4] = c[0]; tdata[ti * 4 + 1] = c[1]; tdata[ti * 4 + 2] = c[2]; tdata[ti * 4 + 3] = 255;
      }
    }
    fillTexture([169, 217, 241]);
    var tex = new THREE.DataTexture(tdata, 16, 1, THREE.RGBAFormat);
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
    tex.encoding = THREE.sRGBEncoding;
    tex.needsUpdate = true;
    var elemMat = new THREE.MeshStandardMaterial({
      map: tex, vertexColors: true, roughness: 0.5, metalness: 0.05,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1
    });
    var mesh = new THREE.Mesh(geo, elemMat);
    mesh.castShadow = true;
    mesh.frustumCulled = false;
    scene.add(mesh);

    var COS = [], SIN = [];
    for (var a = 0; a <= NT; a++) { COS.push(Math.cos(a / NT * 2 * Math.PI)); SIN.push(Math.sin(a / NT * 2 * Math.PI)); }
    var items = [];
    for (var k = 0; k < NX; k++) for (var i = 0; i < NR; i++) for (var j = 0; j < NT; j++) {
      items.push({
        k: k, i: i, j: j,
        xc: -L / 2 + (k + 0.5) * L / NX,
        rc: RI + (i + 0.5) * (RA - RI) / NR,
        order: (k + 0.6 * j / NT) / (NX + 0.6)
      });
    }
    var totalEdges = 0;
    items.forEach(function (it) {
      it.bFaces = [];
      if (it.k === NX - 1) it.bFaces.push(0);
      if (it.k === 0) it.bFaces.push(1);
      if (it.i === NR - 1) it.bFaces.push(2);
      if (it.i === 0) it.bFaces.push(3);
      totalEdges += it.bFaces.length * 4;
    });
    var edgePos = new Float32Array(totalEdges * 6);
    var lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.BufferAttribute(edgePos, 3).setUsage(THREE.DynamicDrawUsage));
    var lineMat = new THREE.LineBasicMaterial({ color: 0x24323b, transparent: true, opacity: 0.5 });
    var lines = new THREE.LineSegments(lineGeo, lineMat);
    lines.frustumCulled = false;
    scene.add(lines);

    // 5 Randbedingungen: Innenfläche heiß (rot), Außenfläche kalt (blau)
    function shell(r, color) {
      var m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, L * 1.002, 64, 1, true),
        new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
      m.rotation.z = Math.PI / 2;
      scene.add(m);
      return m;
    }
    var hot = shell(RI * 0.985, 0xe53009);
    var cold = shell(RA * 1.012, 0x009ee3);

    // 7 Auswertung: Wärmestrom von innen nach außen (Pfeile auf der Stirnfläche)
    var fluxMat = new THREE.MeshBasicMaterial({ color: 0x022541, transparent: true, opacity: 0 });
    var flux = new THREE.Group();
    for (var fa = 0; fa < 8; fa++) {
      var ang = fa / 8 * 2 * Math.PI + Math.PI / 8;
      var g = new THREE.Group();
      var sh = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.25, 8), fluxMat);
      sh.position.y = RI + 0.2 + 0.625;
      var tp = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.3, 12), fluxMat);
      tp.position.y = RI + 0.2 + 1.25 + 0.15;
      g.add(sh); g.add(tp);
      g.rotation.x = ang;
      flux.add(g);
    }
    flux.position.x = L / 2 + 0.03;
    scene.add(flux);

    // ---------- Farben je Hell/Dunkel ----------
    var lastDark = null;
    function applyTheme() {
      var dark = document.body.getAttribute('data-md-color-scheme') === 'slate';
      if (dark === lastDark) return;
      lastDark = dark;
      var ink = dark ? 0x62c9f5 : 0x0070a6;
      edgeMat.color.setHex(ink); dimMat.color.setHex(ink); dimConeMat.color.setHex(ink);
      lineMat.color.setHex(dark ? 0xd5e6f2 : 0x24323b);
      hot.material.color.setHex(dark ? 0xff5a36 : 0xe53009).convertSRGBToLinear();
      cold.material.color.setHex(dark ? 0x18aeef : 0x009ee3).convertSRGBToLinear();
      fluxMat.color.setHex(dark ? 0xffffff : 0x022541).convertSRGBToLinear();
      fillTexture(dark ? [47, 88, 115] : [169, 217, 241]);
      tex.needsUpdate = true;
      ground.material.opacity = dark ? 0.32 : 0.13;
      hemi.groundColor.setHex(dark ? 0x3a4752 : 0x7d8a94);
    }

    // ---------- Größe ----------
    var cw = 0, ch = 0;
    function resize() {
      var w = Math.round(stage.clientWidth) || 560;
      var h = Math.max(250, Math.min(420, Math.round(w * 0.6)));
      if (w === cw && h === ch) return;
      cw = w; ch = h;
      renderer.setSize(w, h, true);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    if (window.ResizeObserver) new ResizeObserver(function () { resize(); draw(curT); }).observe(stage);

    var v3 = new THREE.Vector3();
    function place(el, x, y, z, op) {
      el.style.opacity = op;
      if (op <= 0.001) return;
      v3.set(x, y, z).project(camera);
      var px = (v3.x * 0.5 + 0.5) * cw, py = (-v3.y * 0.5 + 0.5) * ch;
      el.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)';
    }

    // ---------- Ein Bild zum Zeitpunkt t ----------
    var corner = [];
    for (var cc = 0; cc < 8; cc++) corner.push([0, 0, 0, 0]);
    var lastStep = -1;

    function draw(t) {
      applyTheme();
      resize();

      // Ein- und Ausblenden der Schleife
      stage.style.opacity = Math.min(smooth(span(t, 0, 0.45)), 1 - smooth(span(t, 18.0, 18.8))).toFixed(3);

      // 1 Material und 3 Zuweisung: Kugel erscheint und fliegt in die Rohrwand
      var sphIn = backOut(span(t, 0.15, 0.95));
      var fly = smooth(span(t, 4.25, 4.95));
      sphere.visible = t < 4.95 && sphIn > 0.001;
      sphere.position.lerpVectors(SPH0, SPH1, fly);
      sphere.position.y += Math.sin(fly * Math.PI) * 0.9;
      var ss = Math.max(0.001, sphIn * (1 - 0.8 * fly));
      sphere.scale.set(ss, ss, ss);
      sphere.rotation.y = t * 0.9;

      // 2 Geometrie: Kreisring skizzieren, dann entlang der Achse extrudieren
      var prof = smooth(span(t, 1.85, 2.35));
      var ext = smooth(span(t, 2.35, 3.7));
      var e = 0.012 + 0.988 * ext;
      edgeMat.opacity = prof * (1 - smooth(span(t, 5.1, 5.6)));
      sketch.visible = endRing.visible = edgeMat.opacity > 0.003;
      endRing.position.x = -L / 2 + L * e;
      var dimOp = smooth(span(t, 3.55, 3.95)) * (1 - smooth(span(t, 5.6, 6.0)));
      dimMat.opacity = dimOp; dimConeMat.opacity = dimOp;
      dim.visible = dimOp > 0.003;

      // 3 bis 7: Zustand je Element (CAD, Stahl, vernetzt, Ergebnis)
      var showMesh = t >= 2.3;
      mesh.visible = showMesh;
      var fill = (L / 2 + 0.3) * smooth(span(t, 4.85, 5.45));
      var net = span(t, 5.6, 7.5);
      var sol = span(t, 10.45, 11.75);
      var waveR = RI - 0.4 + (RA - RI + 0.8) * sol;
      var waveOn = sol > 0 && sol < 1;
      var wipe = RI + (RA - RI + 0.2) * smooth(span(t, 12.05, 12.9));
      var meshedAny = false;
      if (showMesh) {
        var p = 0, q = 0, pe = 0;
        for (var n = 0; n < count; n++) {
          var it = items[n];
          var appear = clamp01((net * 1.12 - it.order) / 0.12);
          if (appear > 0) meshedAny = true;
          var u = t < 12.05 || it.rc > wipe ? (Math.abs(it.xc) <= fill ? U_STEEL : U_CAD) : -1;
          var glow = waveOn ? Math.exp(-Math.pow((it.rc - waveR) / 0.35, 2)) : 0;
          var cx = 0, cy = 0, cz = 0;
          for (var c8 = 0; c8 < 8; c8++) {
            var C = CORNERS[c8];
            var x = -L / 2 + (it.k + C[0]) * L / NX;
            x = -L / 2 + (x + L / 2) * e;
            var r = RI + (it.i + C[1]) * (RA - RI) / NR;
            var jj = it.j + C[2];
            corner[c8][0] = x; corner[c8][1] = r * COS[jj]; corner[c8][2] = r * SIN[jj]; corner[c8][3] = r;
            cx += corner[c8][0]; cy += corner[c8][1]; cz += corner[c8][2];
          }
          cx /= 8; cy /= 8; cz /= 8;
          // vernetzte Elemente bekommen eine feine Fuge, die das Netz sichtbar macht
          var shrink = 1 - 0.014 * appear;
          for (var c9 = 0; c9 < 8; c9++) {
            corner[c9][0] = cx + (corner[c9][0] - cx) * shrink;
            corner[c9][1] = cy + (corner[c9][1] - cy) * shrink;
            corner[c9][2] = cz + (corner[c9][2] - cz) * shrink;
          }
          var gr = 1 + glow * 0.8, gg = 1 + glow * 0.45, gb = 1 + glow * 0.15;
          for (var f = 0; f < 6; f++) {
            var fq = FACES[f];
            var A = corner[fq[0]], B = corner[fq[1]], Cc = corner[fq[2]], D = corner[fq[3]];
            var ux = B[0] - A[0], uy = B[1] - A[1], uz = B[2] - A[2];
            var vx = D[0] - A[0], vy = D[1] - A[1], vz = D[2] - A[2];
            var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            var fx = (A[0] + B[0] + Cc[0] + D[0]) / 4 - cx, fy = (A[1] + B[1] + Cc[1] + D[1]) / 4 - cy, fz = (A[2] + B[2] + Cc[2] + D[2]) / 4 - cz;
            if (nx * fx + ny * fy + nz * fz < 0) { nx = -nx; ny = -ny; nz = -nz; }
            var nl = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
            nx /= nl; ny /= nl; nz /= nl;
            var tri = [A, B, Cc, A, Cc, D];
            for (var tv = 0; tv < 6; tv++) {
              var P = tri[tv];
              positions[p] = P[0]; normals[p] = nx; vcols[p] = gr; p++;
              positions[p] = P[1]; normals[p] = ny; vcols[p] = gg; p++;
              positions[p] = P[2]; normals[p] = nz; vcols[p] = gb; p++;
              // Temperatur T(r) im Rohr: von innen (Wert 1) logarithmisch nach außen (0)
              uvs[q++] = u >= 0 ? u : Math.min(0.9999, 1 - Math.log(P[3] / RI) / LNRATIO) * 9 / 16;
              uvs[q++] = 0.5;
            }
          }
          for (var bf = 0; bf < it.bFaces.length; bf++) {
            var qe = FACES[it.bFaces[bf]];
            for (var e4 = 0; e4 < 4; e4++) {
              var P1 = corner[qe[e4]], P2 = appear > 0 ? corner[qe[(e4 + 1) % 4]] : P1;
              edgePos[pe++] = P1[0]; edgePos[pe++] = P1[1]; edgePos[pe++] = P1[2];
              edgePos[pe++] = P2[0]; edgePos[pe++] = P2[1]; edgePos[pe++] = P2[2];
            }
          }
        }
        geo.attributes.position.needsUpdate = true;
        geo.attributes.normal.needsUpdate = true;
        geo.attributes.uv.needsUpdate = true;
        geo.attributes.color.needsUpdate = true;
        lineGeo.attributes.position.needsUpdate = true;
        lineMat.opacity = (lastDark ? 0.3 : 0.45) - (lastDark ? 0.14 : 0.22) * smooth(span(t, 12.1, 12.8));
      }
      lines.visible = showMesh && meshedAny;

      // 5 Randbedingungen: erst die heiße Innenfläche, dann die kalte Außenfläche
      var bcFade = 1 - smooth(span(t, 12.0, 12.5));
      hot.material.opacity = 0.62 * smooth(span(t, 7.9, 8.5)) * bcFade;
      cold.material.opacity = 0.38 * smooth(span(t, 8.9, 9.5)) * bcFade;
      hot.visible = hot.material.opacity > 0.003;
      cold.visible = cold.material.opacity > 0.003;

      // 7 Auswertung: Wärmestrom-Pfeile nach außen
      var fluxIn = smooth(span(t, 14.6, 15.2)) * (1 - smooth(span(t, 18.0, 18.6)));
      fluxMat.opacity = 0.85 * fluxIn;
      flux.visible = fluxIn > 0.003;
      flux.scale.set(1, 0.6 + 0.4 * fluxIn, 0.6 + 0.4 * fluxIn);

      // Kamera: schräg auf die Stirnfläche, langsame Umrundung
      var res = smooth(span(t, 12.3, 14.3));
      var az = 0.62 + 0.3 * (t / LOOP);
      var elv = 0.36 - 0.06 * res;
      // schmale Bühne (Handy): weiter weg, damit das ganze Rohr ins Bild passt,
      // und zur Auswertung tiefer, damit die Legende frei bleibt
      var narrow = Math.max(1, 1.62 / camera.aspect);
      var rad = 17.5 * narrow;
      var ty = 0.35 * res * narrow * narrow;
      camera.position.set(rad * Math.sin(az) * Math.cos(elv), ty + rad * Math.sin(elv), rad * Math.cos(az) * Math.cos(elv));
      camera.lookAt(0, ty, 0);
      camera.updateMatrixWorld();

      renderer.render(scene, camera);

      // Einblendungen
      place(ovMat, sphere.position.x, sphere.position.y + 0.95, sphere.position.z,
        smooth(span(t, 0.6, 1.0)) * (1 - smooth(span(t, 4.2, 4.5))));
      place(ovDim, L / 2, 0, dimZ, dimOp);
      place(ovHot, L / 2, 0, 0, smooth(span(t, 8.1, 8.6)) * bcFade);
      place(ovCold, -L / 4, RA + 0.15, 0, smooth(span(t, 9.1, 9.6)) * bcFade);
      var flagOp = smooth(span(t, 13.6, 14.1)) * (1 - smooth(span(t, 18.0, 18.6)));
      place(ovMax, L / 2, RI * Math.cos(2.4), RI * Math.sin(2.4), flagOp);
      place(ovMin, L / 2, RA * Math.cos(-0.9), RA * Math.sin(-0.9), flagOp);
      legend.style.opacity = (smooth(span(t, 12.4, 13.0)) * (1 - smooth(span(t, 18.0, 18.6)))).toFixed(3);

      // Schritt-Leiste und Beschriftung
      var cur = 0;
      for (var si = 0; si < STEPS.length; si++) if (t >= STEPS[si].t0) cur = si;
      for (var bi = 0; bi < trackBtns.length; bi++) {
        var st = STEPS[bi];
        trackBtns[bi].style.setProperty('--p', span(t, st.t0, st.t1).toFixed(3));
        trackBtns[bi].classList.toggle('on', bi === cur);
        trackBtns[bi].classList.toggle('done', bi < cur);
      }
      if (cur !== lastStep) {
        lastStep = cur;
        cap.innerHTML = '<b>' + (cur + 1) + ' · ' + STEPS[cur].key.replace('Randbed.', 'Randbedingungen') + '</b><span>' + STEPS[cur].text + '</span>';
      }
    }

    // ---------- Ablauf ----------
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var curT = reduced ? STILL : 0, running = false, last = 0, visible = true;
    function tick(now) {
      if (!running) return;
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0;
      last = now;
      curT = (curT + dt) % LOOP;
      draw(curT);
      requestAnimationFrame(tick);
    }
    function start() { if (running || reduced || !visible) return; running = true; last = 0; requestAnimationFrame(tick); }
    function stop() { running = false; }

    track.addEventListener('click', function (ev) {
      var btn = ev.target.closest('button');
      if (!btn) return;
      var st = STEPS[+btn.getAttribute('data-i')];
      curT = st.key === 'Auswertung' ? STILL : st.t0 + 0.02;
      draw(curT);
    });
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (en) {
        visible = en[0].isIntersecting;
        if (visible) start(); else stop();
      }).observe(host);
    }
    new MutationObserver(function () { if (!running) draw(curT); })
      .observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });

    // Für Tests: Zeitpunkt setzen und anhalten (window.__heroAnim.seek(12.5))
    window.__heroAnim = {
      seek: function (t) { stop(); reduced = true; curT = t; draw(t); },
      play: function () { reduced = false; start(); }
    };

    draw(curT);
    start();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { setTimeout(init, 0); });
  else setTimeout(init, 0);
})();
