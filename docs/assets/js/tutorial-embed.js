// Tutorial embed image loader
(function(){
  'use strict';
  function onReady(fn){ if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  onReady(function(){
    try{
      var nodes = document.querySelectorAll('.tutorial-embed[data-tutorial]');
      nodes.forEach(function(n){
        try{
          var base = n.getAttribute('data-tutorial');
          if (!base) return;
          // normalize base to avoid double slashes
          base = base.replace(/\/+$/,'');
          var jpg = base + '.jpg';
          var png = base + '.png';
          var img = document.createElement('img');
          img.src = jpg;
          img.alt = n.getAttribute('data-alt') || 'Tutorial preview';
          img.style.width = '100%'; img.style.height = 'auto'; img.style.display = 'block';
          img.onerror = function(){ if (img.src.indexOf('.jpg') !== -1) img.src = png; else img.style.display = 'none'; };
          n.appendChild(img);
        }catch(e){}
      });
    }catch(e){}
  });
})();
