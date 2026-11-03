// Achsenwahl (P2 Vakuumröhre, Named Selections): Die Studierenden wählen, welche Achse in ihrem Modell senkrecht zum
// Blech steht; alle Stellen <span class="aw-achse">X</span> auf der Seite zeigen danach diese Achse.
// Einbinden: <div class="achsenwahl"></div>. Die Wahl bleibt im Browser gespeichert.
(function () {
  'use strict';

  var SCHLUESSEL = 'thermo-achse-blech';

  function lesen() { try { return localStorage.getItem(SCHLUESSEL) || 'X'; } catch (e) { return 'X'; } }
  function merken(a) { try { localStorage.setItem(SCHLUESSEL, a); } catch (e) { /* ohne Speicher gilt die Wahl nur hier */ } }

  function setzen(a) {
    var stellen = document.querySelectorAll('.aw-achse');
    for (var i = 0; i < stellen.length; i++) stellen[i].textContent = a;
    var knoepfe = document.querySelectorAll('.achsenwahl button');
    for (var j = 0; j < knoepfe.length; j++) knoepfe[j].setAttribute('aria-pressed', knoepfe[j].textContent === a ? 'true' : 'false');
  }

  function init() {
    var boxen = document.querySelectorAll('.achsenwahl');
    if (!boxen.length) return;
    for (var i = 0; i < boxen.length; i++) {
      boxen[i].innerHTML = '<span>Achse senkrecht zum Blech in Ihrem Modell:</span>' +
        '<button type="button">X</button><button type="button">Y</button><button type="button">Z</button>';
      boxen[i].addEventListener('click', function (e) {
        if (e.target.tagName !== 'BUTTON') return;
        merken(e.target.textContent); setzen(e.target.textContent);
      });
    }
    setzen(lesen());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
