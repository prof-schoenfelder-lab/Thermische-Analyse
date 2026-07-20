// Bootstrap loader for inline tutorial embeds
document.addEventListener('DOMContentLoaded', () => {
  // wait until TutorialPlayer is available
  function tryInit(){
    if(!window.TutorialPlayer || typeof window.TutorialPlayer.init !== 'function'){
      // try again shortly
      setTimeout(tryInit, 120);
      return;
    }

    document.querySelectorAll('.tutorial-embed').forEach((el)=>{
      let src = el.dataset.tutorial;
      if(!src) return;

      // normalize src: strip leading/trailing slashes
      src = String(src).replace(/^\/+|\/+$/g, '');
      if(!src) return;
      const parts = src.split('/').filter(Boolean);

      // if an explicit JSON path is provided, use it directly
      let jsonUrl = null;
      if(src.endsWith('.json')){
        // accept both folder/imported.json and direct json file names
        jsonUrl = src.startsWith('/') ? src : ('/' + src);
      } else {
        // assume the last path part is the examples folder name
        const folder = parts.length ? parts[parts.length-1] : '';
        if(!folder) return;
        // prefer to resolve the tutorial JSON relative to this bootstrap script's location
        // this avoids leading-root paths ("/assets/...") breaking on project pages hosted under a subpath
        try{
          // Find the script tag robustly: prefer document.currentScript, otherwise search for a
          // script element whose src contains 'player-bootstrap.js' (take the last occurrence).
          let scriptTag = document.currentScript;
          if(!scriptTag){
            const scripts = Array.from(document.getElementsByTagName('script'));
            for(let i=scripts.length-1;i>=0;i--){ const s = scripts[i]; if(s && s.src && s.src.indexOf('player-bootstrap.js')!==-1){ scriptTag = s; break; } }
          }
          const scriptSrc = (scriptTag && scriptTag.src) ? scriptTag.src : '';
          if(scriptSrc){
            // derive the base folder where this script lives, typically .../assets/tutorials/
            const base = scriptSrc.replace(/\/player-bootstrap\.js(\?.*)?$/, '/') ;
            jsonUrl = new URL(folder + '/imported.json', base).href;
          } else {
            // fallback to relative assets path (avoid leading-root when possible)
            jsonUrl = 'assets/tutorials/' + folder + '/imported.json';
          }
        }catch(e){
          jsonUrl = 'assets/tutorials/' + folder + '/imported.json';
        }
      }

      // apply per-embed CSS overrides if provided
      if(el.dataset.height) el.style.setProperty('--tp-fixed-height', el.dataset.height);
      if(el.dataset.pillMinHeight) el.style.setProperty('--tp-pill-min-height', el.dataset.pillMinHeight);

      try{
        // pass a concrete jsonUrl so the player can load the JSON directly
        window.TutorialPlayer.init(el, { jsonUrl: jsonUrl });
      }catch(err){
        console.error('TutorialPlayer init failed for', src, err);
      }
    });
  }

  tryInit();
});
