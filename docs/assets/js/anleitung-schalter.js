// Anleitung "mit Bildern" / "ohne Bilder": ein Schalter, der auf allen Seiten gilt (localStorage).
// Beide Stellungen zeigen dieselbe Klick-Anleitung (details.tut-embed, von tutorials.js aus
// <tutorial slug> erzeugt). Ohne Bilder sind die Bilder eingeklappt; jeder Schritt hat einen Knopf
// "Bild", der genau sein Bild zeigt. Elemente mit class="anl-bild" (z.B. GIF) gibt es nur mit Bildern.
// Kurzanleitungen (Titel beginnt mit "Kurzanleitung") entfallen auf Seiten mit Klick-Anleitung,
// sie bleiben als Rückfall stehen, falls JavaScript fehlt.
// Muss nach tutorials.js geladen werden.
(function () {
  'use strict';
  var KEY = 'kurs-anleitung';
  var MODI = [['bilder', 'mit Bildern'], ['ohne', 'ohne Bilder']];

  function lesen() { try { return localStorage.getItem(KEY) || 'bilder'; } catch (e) { return 'bilder'; } }
  function merken(m) { try { localStorage.setItem(KEY, m); } catch (e) { /* nur diese Seite */ } }

  // Je Schritt einen Knopf "Bild" einsetzen, sobald tutorials.js die Schritte geladen hat
  function knoepfe(det) {
    Array.prototype.forEach.call(det.querySelectorAll('.tut-steps > li'), function (li) {
      if (li.querySelector('.anl-bildknopf') || !li.querySelector('img.tut-img')) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'anl-bildknopf';
      b.setAttribute('aria-expanded', 'false');
      b.textContent = 'Bild';
      b.addEventListener('click', function () {
        var offen = li.classList.toggle('bild-offen');
        b.setAttribute('aria-expanded', offen ? 'true' : 'false');
        b.textContent = offen ? 'Bild ausblenden' : 'Bild';
      });
      var cap = li.querySelector('.tut-cap');
      cap.parentNode.insertBefore(b, cap.nextSibling);
    });
  }

  function init() {
    var inhalt = document.querySelector('.md-content article') || document.body;
    var tuts = Array.prototype.slice.call(inhalt.querySelectorAll('details.tut-embed'));
    if (!tuts.length) return;
    Array.prototype.forEach.call(inhalt.querySelectorAll('details, .admonition'), function (d) {
      var t = d.querySelector('summary, .admonition-title');
      if (t && /^\s*Kurzanleitung/.test(t.textContent)) d.classList.add('anl-doppelt');
    });
    tuts.forEach(function (det) {
      det.open = true;
      knoepfe(det);
      new MutationObserver(function () { knoepfe(det); }).observe(det, { childList: true, subtree: true });
    });

    var leiste = document.createElement('div');
    leiste.className = 'anl-schalter';
    leiste.setAttribute('role', 'group');
    leiste.setAttribute('aria-label', 'Anleitung anzeigen');
    leiste.innerHTML = '<span class="anl-label">Anleitung</span>' + MODI.map(function (m) {
      return '<button type="button" data-modus="' + m[0] + '">' + m[1] + '</button>';
    }).join('');
    var erstes = [].concat(tuts, Array.prototype.slice.call(inhalt.querySelectorAll('.anl-bild')))
      .sort(function (a, b) { return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1; })[0];
    erstes.parentNode.insertBefore(leiste, erstes);

    function setzen(modus) {
      document.body.setAttribute('data-anleitung', modus);
      Array.prototype.forEach.call(leiste.querySelectorAll('button'), function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-modus') === modus ? 'true' : 'false');
      });
    }
    leiste.addEventListener('click', function (ev) {
      var m = ev.target.getAttribute && ev.target.getAttribute('data-modus');
      if (m) { merken(m); setzen(m); }
    });
    setzen(lesen());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
