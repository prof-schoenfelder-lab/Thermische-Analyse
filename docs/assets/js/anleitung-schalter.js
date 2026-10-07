// Anleitung "mit Bildern" / "ohne Bilder": ein Schalter, der auf allen Seiten gilt (localStorage).
// Mit Bildern: Klick-Anleitungen (details.tut-embed) und Elemente mit class="anl-bild" (z.B. GIF).
// Ohne Bilder: Kurzanleitungen (Admonition, deren Titel mit "Kurzanleitung" beginnt).
// Ausgeblendet wird nur, wenn eine Seite beides hat; einzelne Anleitungen bleiben immer sichtbar.
// Muss nach tutorials.js geladen werden (das ersetzt <tutorial> durch details.tut-embed).
(function () {
  'use strict';
  var KEY = 'kurs-anleitung';
  var MODI = [['bilder', 'mit Bildern'], ['ohne', 'ohne Bilder']];

  function lesen() { try { return localStorage.getItem(KEY) || 'bilder'; } catch (e) { return 'bilder'; } }
  function merken(m) { try { localStorage.setItem(KEY, m); } catch (e) { /* nur diese Seite */ } }

  function init() {
    var inhalt = document.querySelector('.md-content article') || document.body;
    var text = Array.prototype.filter.call(inhalt.querySelectorAll('details, .admonition'), function (d) {
      var t = d.querySelector('summary, .admonition-title');
      return t && /^\s*Kurzanleitung/.test(t.textContent);
    });
    var bild = Array.prototype.slice.call(inhalt.querySelectorAll('details.tut-embed, .anl-bild'));
    if (!text.length || !bild.length) return;
    text.forEach(function (d) { d.classList.add('anl-text'); });
    bild.forEach(function (d) { d.classList.add('anl-bild'); });

    var leiste = document.createElement('div');
    leiste.className = 'anl-schalter';
    leiste.setAttribute('role', 'group');
    leiste.setAttribute('aria-label', 'Anleitung anzeigen');
    leiste.innerHTML = '<span class="anl-label">Anleitung</span>' + MODI.map(function (m) {
      return '<button type="button" data-modus="' + m[0] + '">' + m[1] + '</button>';
    }).join('');
    var erstes = [].concat(text, bild).sort(function (a, b) {
      return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    })[0];
    erstes.parentNode.insertBefore(leiste, erstes);

    function setzen(modus) {
      document.body.setAttribute('data-anleitung', modus);
      Array.prototype.forEach.call(leiste.querySelectorAll('button'), function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-modus') === modus ? 'true' : 'false');
      });
      (modus === 'bilder' ? bild : text).forEach(function (d) { if (d.tagName === 'DETAILS') d.open = true; });
    }
    leiste.addEventListener('click', function (ev) {
      var m = ev.target.getAttribute && ev.target.getAttribute('data-modus');
      if (m) { merken(m); setzen(m); }
    });
    setzen(lesen());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
