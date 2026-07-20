// Scrollytelling-Hero der Startseite: ein Stab wird beim Scrollen modelliert,
// vernetzt, mit thermischen Randbedingungen versehen (Wärmezufuhr links,
// Konvektion an der Oberfläche) und gelöst — das Temperaturfeld färbt das Netz.
// Bevorzugt echtes 3D (three.js/WebGL, lokal gevendort); ohne WebGL fällt es
// auf die 2D-SVG-Variante zurück. Läuft nur, wenn #fem-scrolly existiert.
(function () {
  'use strict';

  var SCROLL_SCREENS = 2.6; // Scroll-Strecke in Viewport-Höhen

  var phases = [
    { until: 0.15, title: '1 · Geometrie', text: 'Das Bauteil wird als CAD-Geometrie beschrieben.' },
    { until: 0.40, title: '2 · Vernetzung', text: 'Die Geometrie wird in finite Elemente zerlegt.' },
    { until: 0.52, title: '3 · Randbedingungen', text: 'Links wird Wärme zugeführt, die Oberfläche kühlt durch Konvektion.' },
    { until: 0.80, title: '4 · Lösung', text: 'Der Solver berechnet das Temperaturfeld und die Wärmeströme.' },
    { until: 1.01, title: 'Genau darum geht es in diesem Kurs', text: 'Von der Geometrie bis zum Temperaturfeld — Schritt für Schritt in ANSYS, ab Praktikum 1.' }
  ];

  // Temperaturprofil eines gekühlten Stabes (Fin): heiß am linken Ende,
  // exponentiell abklingend zur Spitze; normiert auf [0,1]
  var DECAY = 2.6;
  function tempProfile(s) {
    var e0 = Math.exp(-DECAY), v = (Math.exp(-DECAY * s) - e0) / (1 - e0);
    return Math.max(0, Math.min(1, v));
  }

  // Weiche Regenbogen-Skala wie in FEM-Postprozessoren
  var STOPS = [[13, 71, 161], [2, 136, 209], [0, 188, 170], [76, 175, 80], [205, 220, 57], [255, 179, 0], [230, 57, 44]];
  function colormapRGB(v) {
    v = Math.max(0, Math.min(1, v));
    var f = v * (STOPS.length - 1);
    var k = Math.min(STOPS.length - 2, Math.floor(f));
    var r = f - k, A = STOPS[k], B = STOPS[k + 1];
    return [A[0] + (B[0] - A[0]) * r, A[1] + (B[1] - A[1]) * r, A[2] + (B[2] - A[2]) * r];
  }
  function colormapCSS(v) {
    var c = colormapRGB(v);
    return 'rgb(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ')';
  }

  function makeCaptionUpdater(scrolly, captionEl) {
    var currentPhase = -1;
    return function (t) {
      var p = 0;
      while (phases[p].until < t) p++;
      if (p === currentPhase) return;
      currentPhase = p;
      var dots = '';
      for (var d = 0; d < phases.length - 1; d++) {
        dots += '<i class="' + (d <= Math.min(p, 3) ? 'on' : '') + '"></i>';
      }
      captionEl.innerHTML = '<span class="fem-dots">' + dots + '</span>' +
        '<strong>' + phases[p].title + '</strong><span>' + phases[p].text + '</span>';
      scrolly.setAttribute('data-phase', p);
    };
  }

  function phaseTimes(t) {
    var solveT = Math.max(0, Math.min(1, (t - 0.52) / 0.22));
    return {
      // Geometrie von Anfang an sichtbar — so ist die Animation schon beim
      // Laden präsent, die "Action" beginnt mit der Vernetzung
      geom: 1,
      mesh: Math.max(0, Math.min(1, (t - 0.15) / 0.22)),
      bc: Math.max(0, Math.min(1, (t - 0.40) / 0.10)),
      ease: solveT * solveT * (3 - 2 * solveT)
    };
  }

  function viewportH() {
    return window.innerHeight || document.documentElement.clientHeight ||
      (window.visualViewport && window.visualViewport.height) || 720;
  }

  // ===========================================================================
  // 3D-Variante (three.js)
  // ===========================================================================
  function initThree(scrolly, sticky, captionEl) {
    if (!window.THREE) return null;
    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch (e) { return null; }

    var LEN = 6, H = 0.78, W = 1.2;
    var NX = 30, NY = 5, NZ = 5;

    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    var canvas = renderer.domElement;
    canvas.className = 'fem-canvas';
    sticky.insertBefore(canvas, sticky.firstChild);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(36, 16 / 9, 0.1, 60);

    scene.add(new THREE.HemisphereLight(0xffffff, 0x77828c, 0.8));
    var sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(4.5, 7, 5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -5; sun.shadow.camera.right = 5;
    sun.shadow.camera.top = 4; sun.shadow.camera.bottom = -3;
    scene.add(sun);

    var groundY = -H / 2 - 0.62;
    var ground = new THREE.Mesh(
      new THREE.PlaneGeometry(24, 12),
      new THREE.ShadowMaterial({ opacity: 0.16 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = groundY;
    ground.receiveShadow = true;
    scene.add(ground);

    var BASE = new THREE.Color(0x93a8b6);

    // Phase 1: massiver CAD-Körper
    var solid = new THREE.Mesh(
      new THREE.BoxGeometry(LEN, H, W),
      new THREE.MeshStandardMaterial({ color: BASE, roughness: 0.45, metalness: 0.08, transparent: true })
    );
    solid.castShadow = true;
    scene.add(solid);

    // Phase 2+: Elemente als gemeinsame Geometrie mit gemeinsamen Knoten.
    var ex = LEN / NX, ey = H / NY, ez = W / NZ;
    var INSET = 0.012; // minimale Fuge gegen Z-Fighting; Netz zeigen die Kantenlinien
    var count = NX * NY * NZ;

    // Hexaeder-Ecken lokal (dx,dy,dz in {0,1}) und die 6 Quad-Flächen
    var CORNERS = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]];
    var FACES = [[1, 2, 6, 5], [0, 4, 7, 3], [3, 7, 6, 2], [0, 1, 5, 4], [4, 5, 6, 7], [0, 3, 2, 1]];

    var vertsPerElem = 36; // 6 Flächen * 2 Dreiecke * 3
    var positions = new Float32Array(count * vertsPerElem * 3);
    var normals = new Float32Array(count * vertsPerElem * 3);
    var colors = new Float32Array(count * vertsPerElem * 3);
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('normal', new THREE.BufferAttribute(normals, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3).setUsage(THREE.DynamicDrawUsage));
    var elemMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.5, metalness: 0.05, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1, side: THREE.DoubleSide });
    var mesh = new THREE.Mesh(geo, elemMat);
    mesh.castShadow = true;
    mesh.frustumCulled = false;
    scene.add(mesh);

    var items = [];
    for (var i = 0; i < NX; i++) {
      for (var j = 0; j < NY; j++) {
        for (var k = 0; k < NZ; k++) {
          items.push({
            i: i, j: j, k: k,
            temp: tempProfile((i + 0.5) / NX),
            order: (i + j * 0.5 + k * 0.25) / (NX + NY * 0.5 + NZ * 0.25)
          });
        }
      }
    }

    // Oberflächen-Netzlinien (klassischer FEM-Look): pro Element die Kanten
    // der außenliegenden Flächen.
    var FACE_BOUNDARY = function (it, f) {
      return (f === 0 && it.i === NX - 1) || (f === 1 && it.i === 0) ||
             (f === 2 && it.j === NY - 1) || (f === 3 && it.j === 0) ||
             (f === 4 && it.k === NZ - 1) || (f === 5 && it.k === 0);
    };
    // Staffelung normieren: auch das letzte Element erreicht appear=1,
    // bevor die Vernetzungs-Phase endet
    var maxOrder = 0;
    items.forEach(function (it) { if (it.order > maxOrder) maxOrder = it.order; });
    items.forEach(function (it) { it.order = it.order / maxOrder; });

    var totalEdges = 0;
    items.forEach(function (it) {
      it.bFaces = [];
      for (var f = 0; f < 6; f++) if (FACE_BOUNDARY(it, f)) it.bFaces.push(f);
      totalEdges += it.bFaces.length * 4;
    });
    var edgePositions = new Float32Array(totalEdges * 2 * 3);
    var edgeGeo = new THREE.BufferGeometry();
    edgeGeo.setAttribute('position', new THREE.BufferAttribute(edgePositions, 3).setUsage(THREE.DynamicDrawUsage));
    var edgeMat = new THREE.LineBasicMaterial({ color: 0x2d3a42, transparent: true, opacity: 0.55 });
    var edgeLines = new THREE.LineSegments(edgeGeo, edgeMat);
    edgeLines.frustumCulled = false;
    scene.add(edgeLines);

    // Phase 3: thermische Randbedingungen
    var bcGroup = new THREE.Group();
    // Wärmezufuhr: rote Pfeile, die von links in die Stirnfläche zeigen
    var heatMat = new THREE.MeshStandardMaterial({ color: 0xe53935, roughness: 0.4, transparent: true });
    var heatArrows = [];
    var NHEAT = 3;
    for (var hy = 0; hy < NHEAT; hy++) {
      for (var hz = 0; hz < NHEAT; hz++) {
        var gArr = new THREE.Group();
        var shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.55, 10), heatMat);
        shaft.rotation.z = Math.PI / 2;
        shaft.position.x = -0.47;
        var tip = new THREE.Mesh(new THREE.ConeGeometry(0.085, 0.2, 12), heatMat);
        tip.rotation.z = -Math.PI / 2;
        tip.position.x = -0.1;
        gArr.add(shaft); gArr.add(tip);
        gArr.position.set(-LEN / 2, ((hy + 0.5) / NHEAT - 0.5) * H * 0.9, ((hz + 0.5) / NHEAT - 0.5) * W * 0.9);
        gArr.userData.ord = (hy * NHEAT + hz) / (NHEAT * NHEAT);
        heatArrows.push(gArr);
        bcGroup.add(gArr);
      }
    }
    // Konvektion: blaue Pfeile, die von der Oberseite nach oben abziehen
    var convMat = new THREE.MeshStandardMaterial({ color: 0x1e88e5, roughness: 0.4, transparent: true });
    var convArrows = [];
    var NCONV = 8;
    for (var cv = 0; cv < NCONV; cv++) {
      var gC = new THREE.Group();
      var shaftC = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.34, 10), convMat);
      shaftC.position.y = 0.27;
      var tipC = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.15, 12), convMat);
      tipC.position.y = 0.5;
      gC.add(shaftC); gC.add(tipC);
      var sC = (cv + 0.5) / NCONV;
      gC.position.set(-LEN / 2 + sC * LEN, H / 2 + 0.05, 0);
      gC.userData.ord = sC;
      convArrows.push(gC);
      bcGroup.add(gC);
    }
    scene.add(bcGroup);

    // Farblegende als HTML-Overlay
    var cbar = document.createElement('div');
    cbar.className = 'fem-cbar';
    var stopsCSS = [];
    for (var sc = 0; sc <= 10; sc++) stopsCSS.push(colormapCSS(1 - sc / 10) + ' ' + (sc * 10) + '%');
    cbar.innerHTML = '<em>Temperatur<br>T</em><span style="background:linear-gradient(' + stopsCSS.join(',') + ')"></span>';
    sticky.appendChild(cbar);

    function resize() {
      var w = Math.min(sticky.clientWidth * 0.97, 960) || 900;
      var h = Math.min(Math.round(viewportH() * 0.62), 520);
      renderer.setSize(w, h, true);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    resize();

    function render(t) {
      var ph = phaseTimes(t);

      // CAD-Körper: erscheint in Phase 1, weicht dem Netz in Phase 2
      var solidOp = ph.geom * Math.max(0, 1 - ph.mesh * 1.8);
      solid.material.opacity = solidOp;
      solid.visible = solidOp > 0.01;
      solid.scale.set(Math.max(0.001, 0.25 + 0.75 * ph.geom), 1, 1);

      // Elemente: gestaffelt erscheinen, beim Lösen mit Temperatur einfärben
      mesh.visible = ph.mesh > 0;
      if (mesh.visible) {
        var corner = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]];
        var col = new THREE.Color();
        var ptr = 0, ptrE = 0;
        for (var n = 0; n < count; n++) {
          var it = items[n];
          var appear = Math.max(0, Math.min(1, (ph.mesh * 1.15 - it.order) / 0.15));

          // 8 Element-Ecken (mit Nachbarn geteilte Knotenlagen)
          var cx = 0, cy = 0, cz = 0;
          for (var c8 = 0; c8 < 8; c8++) {
            var px = -LEN / 2 + (it.i + CORNERS[c8][0]) * ex;
            var py = -H / 2 + (it.j + CORNERS[c8][1]) * ey;
            var pz = -W / 2 + (it.k + CORNERS[c8][2]) * ez;
            corner[c8][0] = px; corner[c8][1] = py; corner[c8][2] = pz;
            cx += px; cy += py; cz += pz;
          }
          cx /= 8; cy /= 8; cz /= 8;
          // Fugen + Erscheinen: Ecken zum Elementzentrum ziehen
          var shrink = 1 - (INSET + (1 - appear));
          if (shrink < 0.001) shrink = 0.001;
          for (var c9 = 0; c9 < 8; c9++) {
            corner[c9][0] = cx + (corner[c9][0] - cx) * shrink;
            corner[c9][1] = cy + (corner[c9][1] - cy) * shrink;
            corner[c9][2] = cz + (corner[c9][2] - cz) * shrink;
          }

          // Farbe des Elements: Temperaturfeld blendet mit der Lösung ein
          if (ph.ease > 0) {
            var cRGB = colormapRGB(it.temp * ph.ease + (1 - ph.ease) * 0.0);
            col.setRGB(cRGB[0] / 255, cRGB[1] / 255, cRGB[2] / 255);
            col.lerpColors(BASE, col, Math.min(1, ph.ease * 1.4));
            col.offsetHSL(0, 0.18, -0.02);
          } else {
            col.copy(BASE);
          }

          // 6 Flächen -> 2 Dreiecke, Normale je Fläche nach außen
          for (var f = 0; f < 6; f++) {
            var q = FACES[f];
            var A = corner[q[0]], B = corner[q[1]], C = corner[q[2]], D = corner[q[3]];
            var ux = B[0] - A[0], uy = B[1] - A[1], uz = B[2] - A[2];
            var vx = D[0] - A[0], vy = D[1] - A[1], vz = D[2] - A[2];
            var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            var fcx = (A[0] + B[0] + C[0] + D[0]) / 4 - cx;
            var fcy = (A[1] + B[1] + C[1] + D[1]) / 4 - cy;
            var fcz = (A[2] + B[2] + C[2] + D[2]) / 4 - cz;
            if (nx * fcx + ny * fcy + nz * fcz < 0) { nx = -nx; ny = -ny; nz = -nz; }
            var nl = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
            nx /= nl; ny /= nl; nz /= nl;
            var tri = [A, B, C, A, C, D];
            for (var tv = 0; tv < 6; tv++) {
              positions[ptr] = tri[tv][0]; normals[ptr] = nx; colors[ptr] = col.r; ptr++;
              positions[ptr] = tri[tv][1]; normals[ptr] = ny; colors[ptr] = col.g; ptr++;
              positions[ptr] = tri[tv][2]; normals[ptr] = nz; colors[ptr] = col.b; ptr++;
            }
          }

          // Netzlinien der außenliegenden Flächen dieses Elements
          for (var bf = 0; bf < it.bFaces.length; bf++) {
            var qe = FACES[it.bFaces[bf]];
            for (var e4 = 0; e4 < 4; e4++) {
              var P1 = corner[qe[e4]], P2 = corner[qe[(e4 + 1) % 4]];
              edgePositions[ptrE++] = P1[0]; edgePositions[ptrE++] = P1[1]; edgePositions[ptrE++] = P1[2];
              edgePositions[ptrE++] = P2[0]; edgePositions[ptrE++] = P2[1]; edgePositions[ptrE++] = P2[2];
            }
          }
        }
        geo.attributes.position.needsUpdate = true;
        geo.attributes.normal.needsUpdate = true;
        geo.attributes.color.needsUpdate = true;
        edgeGeo.attributes.position.needsUpdate = true;
      }
      edgeLines.visible = mesh.visible;

      // Randbedingungen gestaffelt einblenden
      bcGroup.visible = ph.bc > 0;
      heatMat.opacity = ph.bc;
      convMat.opacity = ph.bc * 0.9;
      heatArrows.forEach(function (g) { g.visible = ph.bc > g.userData.ord * 0.6; });
      convArrows.forEach(function (g) { g.visible = ph.bc > g.userData.ord; });

      cbar.style.opacity = ph.ease;

      // Kamerafahrt: leichte Umrundung, beim Lösen näher ran
      var az = -0.78 + t * 0.55;
      var elv = 0.46 - 0.08 * ph.ease;
      var r = 8.8 - 0.9 * ph.ease;
      var ty = -0.1 * ph.ease;
      camera.position.set(r * Math.sin(az) * Math.cos(elv), ty + r * Math.sin(elv), r * Math.cos(az) * Math.cos(elv));
      camera.lookAt(0, ty, 0);

      renderer.render(scene, camera);
    }

    return { render: render, resize: resize };
  }

  // ===========================================================================
  // 2D-SVG-Fallback (ohne WebGL)
  // ===========================================================================
  function initSVG(scrolly, svg) {
    var NS = 'http://www.w3.org/2000/svg';
    var X0 = 90, Y0 = 100, L = 620, H = 72;
    var NX = 30, NY = 5;

    function el(name, attrs, parent) {
      var e = document.createElementNS(NS, name);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(e);
      return e;
    }
    svg.setAttribute('viewBox', '0 0 800 300');

    var outline = el('path', {
      d: 'M ' + X0 + ' ' + Y0 + ' h ' + L + ' v ' + H + ' h ' + (-L) + ' Z',
      fill: 'none', 'stroke-width': 2.5, 'class': 'fem-outline'
    });
    var outlineLen = outline.getTotalLength();
    outline.style.strokeDasharray = outlineLen;

    var meshG = el('g', { 'class': 'fem-mesh' });
    var elems = [];
    for (var j = 0; j < NY; j++) {
      for (var i = 0; i < NX; i++) {
        elems.push({ i: i, j: j, poly: el('polygon', { 'class': 'fem-elem' }, meshG) });
      }
    }
    elems.forEach(function (q) { q.order = (q.i + q.j * 0.5) / (NX + NY * 0.5); });

    var bcG = el('g', { 'class': 'fem-bc' });
    // Wärmezufuhr: rote Pfeile von links in die Stirnfläche
    var heatArrows = [];
    for (var hA = 0; hA < 3; hA++) {
      var hy = Y0 + H * (hA + 0.5) / 3;
      var g1 = el('g', { 'class': 'fem-arrow' }, bcG);
      el('line', { x1: X0 - 46, y1: hy, x2: X0 - 12, y2: hy, stroke: '#e53935' }, g1);
      el('polygon', { points: (X0 - 5) + ',' + hy + ' ' + (X0 - 14) + ',' + (hy - 4.5) + ' ' + (X0 - 14) + ',' + (hy + 4.5), fill: '#e53935' }, g1);
      heatArrows.push(g1);
    }
    // Konvektion: blaue Pfeile von der Oberseite nach oben
    var convArrows = [];
    for (var a = 0; a <= 10; a++) {
      var ax = X0 + (L / 10) * a;
      var g2 = el('g', { 'class': 'fem-arrow' }, bcG);
      el('line', { x1: ax, y1: Y0 - 12, x2: ax, y2: Y0 - 34, stroke: '#1e88e5' }, g2);
      el('polygon', { points: ax + ',' + (Y0 - 41) + ' ' + (ax - 4.5) + ',' + (Y0 - 32) + ' ' + (ax + 4.5) + ',' + (Y0 - 32), fill: '#1e88e5' }, g2);
      convArrows.push(g2);
    }

    function nodePos(i, j) {
      return (X0 + (i / NX) * L) + ',' + (Y0 + (j / NY) * H);
    }

    function render(t) {
      var ph = phaseTimes(t);
      outline.style.strokeDashoffset = outlineLen * (1 - ph.geom);
      outline.style.opacity = ph.mesh >= 1 ? 0.2 : 1;
      elems.forEach(function (q) {
        var visible = ph.mesh > 0 && q.order <= ph.mesh;
        q.poly.style.opacity = visible ? 1 : 0;
        if (!visible) return;
        q.poly.setAttribute('points',
          nodePos(q.i, q.j) + ' ' + nodePos(q.i + 1, q.j) + ' ' +
          nodePos(q.i + 1, q.j + 1) + ' ' + nodePos(q.i, q.j + 1));
        if (ph.ease > 0) {
          var c = colormapCSS(tempProfile((q.i + 0.5) / NX) * ph.ease);
          q.poly.style.fill = c;
          q.poly.style.stroke = ph.ease > 0.6 ? c : '';
        } else {
          q.poly.style.fill = 'var(--fem-elem-fill)';
          q.poly.style.stroke = '';
        }
      });
      bcG.style.opacity = ph.bc;
      heatArrows.forEach(function (g, idx) { g.style.opacity = ph.bc > idx / 4 ? 1 : 0; });
      convArrows.forEach(function (g, idx) { g.style.opacity = ph.bc > idx / convArrows.length ? 1 : 0; });
    }
    return { render: render, resize: function () { } };
  }

  // ===========================================================================
  var SEEN_KEY = 'fem_scrolly_seen';

  // Wer die Animation schon einmal komplett gesehen hat, bekommt sie beim
  // nächsten Besuch hinter der Praktika-Übersicht einsortiert — so steht die
  // Übersicht sofort oben, die Animation bleibt aber erreichbar.
  function moveAfterOverview(scrolly) {
    try {
      if (!localStorage.getItem(SEEN_KEY)) return;
      var grid = document.querySelector('.md-content .grid.cards');
      if (!grid || !grid.parentNode) return;
      grid.parentNode.insertBefore(scrolly, grid.nextSibling);
      var hint = document.getElementById('fem-scroll-hint');
      if (hint && hint.parentNode) hint.parentNode.removeChild(hint);
    } catch (e) { }
  }

  function init() {
    var scrolly = document.getElementById('fem-scrolly');
    if (!scrolly) return;
    var sticky = scrolly.querySelector('.fem-sticky');
    var svg = document.getElementById('fem-svg');
    var captionEl = document.getElementById('fem-caption');
    if (!sticky || !svg || !captionEl) return;
    moveAfterOverview(scrolly);

    var impl = initThree(scrolly, sticky, captionEl);
    if (impl) { svg.style.display = 'none'; }
    else { impl = initSVG(scrolly, svg); }

    var updateCaption = makeCaptionUpdater(scrolly, captionEl);
    var seenSaved = false;
    function render(t) {
      updateCaption(t);
      impl.render(t);
      if (!seenSaved && t >= 0.95) {
        seenSaved = true;
        try { localStorage.setItem(SEEN_KEY, '1'); } catch (e) { }
      }
    }
    window.__femRender = render; // für Tests/Debugging von außen aufrufbar

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) { render(0.999); return; }

    // Höhen in px setzen statt sich auf CSS-vh zu verlassen (robust gegen
    // Viewport-Eigenheiten mobiler Browser / eingebetteter Webviews)
    function layout() {
      var vh = viewportH();
      scrolly.style.height = Math.round(vh * SCROLL_SCREENS) + 'px';
      sticky.style.height = Math.round(vh - 56) + 'px';
      impl.resize();
    }
    layout();

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        var r = scrolly.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        var total = r.height - vh;
        if (total <= 0) { render(1); return; }
        render(Math.max(0, Math.min(1, -r.top / total)));
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () { layout(); onScroll(); });
    onScroll();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
