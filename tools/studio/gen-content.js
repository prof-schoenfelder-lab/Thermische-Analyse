/* Kurs-Studio — Block-Renderer & Inhalts-Generatoren (Browser UND Node).
 *
 * Wandelt das Block-Modell (content/SCHEMA.md) in Kurs-Markdown:
 *  - renderBlocks(blocks) -> Zeilen[]
 *  - generateUebung(uebung, opts) -> vollständige .md (Frontmatter + Marker + Body)
 *  - contentHash(str) -> kurze Prüfsumme (Hand-Edit-Warnung)
 *
 * Node:    const C = require('./gen-content.js');
 * Browser: <script src="studio/gen-content.js"> -> window.KursContent
 */
(function (root) {
  'use strict';

  function esc(s) { return String(s == null ? '' : s); }
  function attr(s) { return String(s == null ? '' : s).replace(/"/g, '&quot;'); }

  // ---- Block-Modell -> Markdown-Zeilen ------------------------------------
  function renderBlock(b) {
    switch (b.art) {
      case 'text':
        return String(b.md || '').split('\n');
      case 'trenner':
        return ['---'];
      case 'bild':
        return [
          '<figure style="text-align:center;">',
          '  <img src="' + attr(b.datei) + '" alt="' + attr(b.alt || '') + '"' +
            (b.breite ? ' width="' + attr(b.breite) + '"' : '') + '>',
          '</figure>'
        ];
      case 'tutorial':
        return ['<tutorial slug="' + attr(b.slug) + '"' + (b.offen ? ' open' : '') + '></tutorial>'];
      case 'tabelle': {
        var kopf = b.kopf || [];
        var out = ['| ' + kopf.map(esc).join(' | ') + ' |',
                   '| ' + kopf.map(function () { return '---'; }).join(' | ') + ' |'];
        (b.zeilen || []).forEach(function (z) { out.push('| ' + z.map(esc).join(' | ') + ' |'); });
        return out;
      }
      case 'box': {
        var head = '!!! ' + (b.typ || 'info') + (b.titel ? ' "' + b.titel + '"' : '');
        var inner = renderBlocks(b.blocks || []);
        return [head, ''].concat(inner.map(function (l) { return l ? '    ' + l : ''; }));
      }
      default:
        return [];
    }
  }

  // Blockliste rendern, Blöcke durch Leerzeile getrennt
  function renderBlocks(blocks) {
    var out = [];
    (blocks || []).forEach(function (b, i) {
      if (i > 0) out.push('');
      out = out.concat(renderBlock(b));
    });
    return out;
  }

  // ---- Fragen-Markup (answer-checker) -------------------------------------
  var LETTERS = 'ABCDEFGHIJ';
  function questionMarkup(frage, qNum) {
    if (frage.typ === 'mc') {
      var correct = (frage.richtig || []).map(function (i) { return LETTERS[i]; }).join(',');
      var lines = [
        '<div class="multiple-choice-question" data-correct="' + correct +
          '" data-points="' + (frage.punkte || 0) + '" data-attempts="' + (frage.versuche || 3) + '">',
        '  <div class="mc-options">'
      ];
      (frage.optionen || []).forEach(function (opt, i) {
        var L = LETTERS[i], id = 'q' + qNum + L.toLowerCase();
        lines.push('    <div class="mc-option" data-value="' + L + '">');
        lines.push('      <input type="checkbox" id="' + id + '" name="q' + qNum + '">');
        lines.push('      <label for="' + id + '">' + esc(opt) + '</label>');
        lines.push('    </div>');
      });
      lines.push('  </div>');
      lines.push('</div>');
      return lines;
    }
    // numerisch
    return ['<div class="numeric-question" data-answer="' + attr(frage.antwort) +
      '" data-tolerance="' + attr(frage.toleranz != null ? frage.toleranz : 0) +
      '" data-points="' + (frage.punkte || 0) + '" data-attempts="' + (frage.versuche || 5) +
      '" data-hints="' + attr(frage.hinweise || '') + '"></div>'];
  }

  // ---- Prüfsumme (nicht kryptografisch; nur Änderungserkennung) -----------
  function contentHash(s) {
    var h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
    return h.toString(36);
  }
  var MARKER_RE = /^<!-- GENERIERT .*-->$/m;
  function withMarker(front, rel, body) {
    var hash = contentHash(body);
    var marker = '<!-- GENERIERT aus content/' + rel + ' · inhalt-hash:' + hash +
      ' · Kurs-Studio — nicht von Hand ändern -->';
    return front.concat([marker, '']).concat(body.split('\n')).join('\n') + '\n';
  }
  // true, wenn die Datei seit der Generierung von Hand verändert wurde
  function handEdited(fileText) {
    var m = fileText.match(/inhalt-hash:([a-z0-9]+)/);
    if (!m) return false; // keine generierte Datei
    var body = fileText.split(/\n/).slice(fileText.split('\n').findIndex(function (l) { return MARKER_RE.test(l); }) + 1).join('\n');
    body = body.replace(/^\n/, '');
    return contentHash(body.replace(/\n$/, '')) !== m[1];
  }

  // ---- Übung -> vollständige Markdown-Seite --------------------------------
  function generateUebung(u, opts) {
    opts = opts || {};
    var front = ['---', 'title: ' + (u.titel || 'Übung'), '---'];
    var body = [];
    function section(title, blocks) {
      if (!blocks || !blocks.length) return;
      body.push('## ' + title, '');
      body = body.concat(renderBlocks(blocks));
      body.push('');
    }
    body.push('# ' + (u.titel || 'Übung'), '');
    if (u.intro && u.intro.length) { body = body.concat(renderBlocks(u.intro)); body.push(''); }
    section('Gegeben', u.gegeben);
    // Gesucht: einleitende Blöcke + je Frage Überschrift + Markup
    if ((u.gesucht && u.gesucht.length) || (u.fragen && u.fragen.length)) {
      body.push('## Gesucht', '');
      if (u.gesucht && u.gesucht.length) { body = body.concat(renderBlocks(u.gesucht)); body.push(''); }
      (u.fragen || []).forEach(function (f, i) {
        body.push('### ' + esc(f.frage), '');
        body = body.concat(questionMarkup(f, i + 1));
        body.push('');
      });
    }
    section('Hinweise', u.hinweise);
    if (u.loesung && u.loesung.length) {
      body.push('<!-- Lösung — wird angezeigt, wenn alle Fragen beantwortet sind -->');
      body.push('<div class="solution-images" markdown="1">', '');
      body.push('### 🎯 Lösung', '');
      body = body.concat(renderBlocks(u.loesung));
      body.push('', '</div>');
    }
    // trailing Leerzeilen trimmen
    while (body.length && body[body.length - 1] === '') body.pop();
    return withMarker(front, (opts.rel || 'uebung.json'), body.join('\n'));
  }

  var API = {
    renderBlocks: renderBlocks,
    renderBlock: renderBlock,
    questionMarkup: questionMarkup,
    generateUebung: generateUebung,
    contentHash: contentHash,
    handEdited: handEdited
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  if (root) root.KursContent = API;
})(typeof window !== 'undefined' ? window : null);
