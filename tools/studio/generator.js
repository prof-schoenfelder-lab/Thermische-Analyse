/* Kurs-Studio — Generator & Nav-Parser (kanonisch, für Browser UND Node).
 *
 * Eine Richtung produktiv: content/ (Baum) -> mkdocs-Nav-Block (Text).
 * Der Parser (mkdocs-Nav -> Baum) wird nur für Bootstrap/Verify gebraucht.
 *
 * Node:    const G = require('./generator.js');
 * Browser: <script src="studio/generator.js"> -> window.KursGen
 *
 * Knoten-Modell (praktikum.kinder, rekursiv):
 *   { gruppe: "GRUNDLAGEN", kinder: [ … ] }        // Nav-Gruppe
 *   { titel: "…", extern: "pfad.md" }               // benannte Bestandsseite
 *   { extern: "pfad.md" }                            // Index/„bare" Seite ohne Titel
 * Praktikum: { slug, nav: "EINFÜHRUNG", kinder: [ … ] }
 * course:    { praktika: ["P1_Einfuehrung", …] }
 */
(function (root) {
  'use strict';

  var NAV_BASE_INDENT = 6;   // Einrückung der Praktikums-Zeile in mkdocs.yml
  var NAV_STEP = 8;          // Einrückung pro Verschachtelungsebene

  function pad(n) { return new Array(n + 1).join(' '); }

  // Label nur quoten, wenn nötig (Doppelpunkt/Raute → YAML-kritisch)
  function q(label) {
    return /[:#]/.test(label) ? '"' + label + '"' : label;
  }

  // ---- Generieren: Baum -> Nav-Block (Textzeilen) -------------------------
  // Pfad eines Blatt-Knotens: extern-Referenz ODER generierte Seite (pfad)
  function leafPath(node) { return node.extern !== undefined ? node.extern : node.pfad; }

  function genNode(node, indent, out) {
    if (node.gruppe !== undefined) {
      out.push(pad(indent) + '- ' + q(node.gruppe) + ':');
      (node.kinder || []).forEach(function (c) { genNode(c, indent + NAV_STEP, out); });
    } else if (node.titel !== undefined && node.titel !== null && node.titel !== '') {
      out.push(pad(indent) + '- ' + q(node.titel) + ': ' + leafPath(node));
    } else {
      out.push(pad(indent) + '- ' + leafPath(node));
    }
  }

  function generateNav(course, praktika) {
    var out = [];
    (course.praktika || []).forEach(function (slug) {
      var p = praktika[slug];
      if (!p) return;
      out.push(pad(NAV_BASE_INDENT) + '- ' + q(p.nav) + ':');
      (p.kinder || []).forEach(function (c) { genNode(c, NAV_BASE_INDENT + NAV_STEP, out); });
    });
    return out.join('\n');
  }

  // ---- Parsen: Nav-Block (Textzeilen) -> Praktika-Baum --------------------
  function stripComment(c) { return c.replace(/\s+#.*$/, ''); }

  function parseEntry(c) {
    if (c.charAt(0) === '"') {
      var end = c.indexOf('"', 1);
      var label = c.slice(1, end);
      var rest = c.slice(end + 1).trim();
      if (rest === ':') return { gruppe: label };
      if (rest.charAt(0) === ':') return { titel: label, extern: rest.slice(1).trim() };
    }
    if (c.charAt(c.length - 1) === ':') return { gruppe: c.slice(0, -1).trim() };
    var i = c.indexOf(': ');
    if (i !== -1) return { titel: c.slice(0, i).trim(), extern: c.slice(i + 2).trim() };
    return { extern: c.trim() };
  }

  // lines: Roh-Zeilen des AUTO-NAV-Blocks (ohne Marker). Liefert Praktika-Liste.
  function parseNavBlock(lines) {
    var roots = [];
    var stack = [{ indent: -1, children: roots }];
    lines.forEach(function (raw) {
      if (!raw.trim() || raw.trim().charAt(0) === '#') return;
      var indent = raw.length - raw.replace(/^ +/, '').length;
      var content = stripComment(raw.trim().replace(/^-\s*/, ''));
      var node = parseEntry(content);
      while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
      stack[stack.length - 1].children.push(node);
      if (node.gruppe !== undefined) {
        node.kinder = [];
        stack.push({ indent: indent, children: node.kinder });
      }
    });
    // roots = Praktika (jeweils gruppe mit Label = nav). In {slug,nav,kinder} wandeln.
    return roots.map(function (r) {
      return { nav: r.gruppe, slug: deriveSlug(r.kinder), kinder: r.kinder };
    });
  }

  // Slug = erstes Pfad-Segment eines beliebigen extern-Kindes im Teilbaum
  function deriveSlug(kinder) {
    var found = null;
    (function walk(list) {
      (list || []).forEach(function (n) {
        if (found) return;
        if (n.extern) { found = n.extern.split('/')[0]; }
        else if (n.kinder) walk(n.kinder);
      });
    })(kinder);
    return found;
  }

  // ---- Baum-Vergleich (semantisch, für Verify) ----------------------------
  function normNode(n) {
    // Gruppe ODER Praktikum (beide haben kinder; Label aus gruppe bzw. nav)
    if (n.kinder !== undefined) {
      var label = (n.gruppe !== undefined) ? n.gruppe : n.nav;
      return { g: label, k: n.kinder.map(normNode) };
    }
    return { t: (n.titel || null), e: (n.extern !== undefined ? n.extern : n.pfad) };
  }
  function treeEqual(a, b) {
    return JSON.stringify(a.map(normNode)) === JSON.stringify(b.map(normNode));
  }

  var API = {
    generateNav: generateNav,
    parseNavBlock: parseNavBlock,
    treeEqual: treeEqual,
    normNode: normNode,
    NAV_BASE_INDENT: NAV_BASE_INDENT,
    NAV_STEP: NAV_STEP
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  if (root) root.KursGen = API;
})(typeof window !== 'undefined' ? window : null);
