// Compact inline tutorial player for MkDocs

// Resolve image paths to site paths (global helper)
function resolveImageUrlGlobal(imgPath){
  if(!imgPath) return '';
  if(/^https?:\/\//.test(imgPath) || imgPath.startsWith('/')) return imgPath;
  const m = imgPath.match(/^examples\/([^\/]+)\/(.*)$/);
  if(m) return '/tutorials/examples/' + m[1] + '/' + m[2];
  const m2 = imgPath.match(/^([^\/]+)\/img\/(.*)$/);
  if(m2){
    try{
      const parts = location.pathname.split('/').filter(Boolean);
      const idx = parts.indexOf('examples');
      if(idx>=0 && parts.length>idx+1){
        const folder = parts[idx+1];
        return '/tutorials/examples/' + folder + '/img/' + m2[2];
      }
      // fallback: assume the folder is under /tutorials/<folder>/img/
      return '/tutorials/' + m2[1] + '/img/' + m2[2];
    }catch(e){}
  }
  try{ return new URL(imgPath, location.href).toString(); }catch(e){ return imgPath; }
}

(function(window){
  function el(html){ const d=document.createElement('div'); d.innerHTML = html.trim(); return d.firstElementChild; }

  function createPlayerRoot(){
    return el('\n      <div class="player">\n        <div class="player__header">\n          <div class="player__title"><h1 id="playerTitle">Tutorial</h1></div>\n        </div>\n        <section class="player__stage">\n          <div class="player__canvas">\n            <div id="canvasRoot">\n              <div class="canvas-frame" id="canvasFrame">\n                <img id="stepImage" draggable="false"/>\n                <div id="highlightLayer" class="layer"></div>\n              </div>\n              <!-- UI overlays outside the transformed frame so they remain fixed -->\n              <div id="stepPill" class="step-pill"></div>\n              <div class="zoom-floating" id="zoomFloating">\n                <button id="btnZoomIn" title="Vergrößern">+</button>\n                <button id="btnZoomOut" title="Verkleinern">−</button>\n              </div>\n            </div>\n          </div>\n          <div class="player__controls-bottom">\n            <div class="progress-row">\n              <div class="nav-buttons">\n                <button id="btnPrev" class="nav-prev" title="Zurück">◀</button>\n                <button id="btnNext" class="nav-next" title="Weiter">▶</button>\n              </div>\n              <div id="progress" class="progress"><div id="progressBar"></div></div>\n              <div id="stepCounter" class="step-counter"></div>\n            </div>\n          </div>\n        </section>\n      </div>\n    ');
  }

  async function tryFetch(variants){
    for(const p of variants){
      try{
        const r = await fetch(p);
        if(!r.ok) continue;
        const json = await r.json();
        return { json, path: p };
      }catch(e){/* ignore */}
    }
    throw new Error('all fetch attempts failed');
  }

  function normalize(v){
    if(v && v.guide && Array.isArray(v.steps)){
      return {
        title: v.guide.title || 'Tutorial',
        default_duration_ms: 1800,
        // Prefer explicit filename when available, fall back to relative path if present
        steps: v.steps.map(s=>({ label: s.title||'', text: s.description||'', image: (s.screenshotFilename || s.screenshotRelativePath || '') , highlights: s.highlights || [] }))
      };
    }
    return v;
  }

  function init(container, opts={}){
    if(!container) throw new Error('container required');
  // normalize options and defaults (default to 'cover' so screenshots fill the player)
    const cfg = Object.assign({ fit: 'contain' }, opts || {});
    const root = createPlayerRoot(); container.innerHTML = ''; container.appendChild(root);

    const imgEl = root.querySelector('#stepImage');
    const hlLayer = root.querySelector('#highlightLayer');
    const bar = root.querySelector('#progressBar');
    const btnPrev = root.querySelector('#btnPrev');
    const btnNext = root.querySelector('#btnNext');
      // click capture removed: clicking no longer advances
      // const clickCap = root.querySelector('#clickCapture');
    const canvasFrame = root.querySelector('#canvasFrame');
    const canvasRoot = root.querySelector('#canvasRoot');
    const titleEl = root.querySelector('#playerTitle');
      const btnZoomIn = root.querySelector('#btnZoomIn');
      const btnZoomOut = root.querySelector('#btnZoomOut');

  let data=null, i=0, playing=false, timer=null;
  let jsonBase = null; // base URL of loaded imported.json (used to resolve relative image paths)
    let scale=1, originX=0, originY=0, baseScale=1, isPanning=false, panStart={x:0,y:0};

    function applyTransform(){ canvasFrame.style.transform = 'translate(' + originX + 'px, ' + originY + 'px) scale(' + scale + ')'; }
    function renderHighlights(step){ hlLayer.innerHTML=''; (step.highlights||[]).forEach(h=>{ const d=document.createElement('div'); d.className='highlight'; d.style.left=(h.x||0)+'%'; d.style.top=(h.y||0)+'%'; d.style.width=(h.w||0)+'%'; d.style.height=(h.h||0)+'%'; hlLayer.appendChild(d); }); }
    function computeBaseScaleAndFit(img){
      // Let CSS scale the image to the container using object-fit (contain|cover).
      // Ensure the canvas frame occupies the full container and the image is 100% of that.
      canvasFrame.style.width = '100%';
      canvasFrame.style.height = '100%';
      imgEl.style.width = '100%';
      imgEl.style.height = '100%';
      imgEl.style.objectFit = (cfg && cfg.fit === 'cover') ? 'cover' : 'contain';
      // reset transform state: start without extra zoom and centered
      baseScale = 1;
      scale = 1;
      originX = 0;
      originY = 0;
      applyTransform();
    }

    // Restore zoom behaviour for buttons (wheel remains disabled).
    // scale is relative where baseScale == 1 represents the CSS/object-fit 'contain' state.
    function setZoom(z, center){
      const minScale = baseScale;
      const maxScale = baseScale * 4;
      const newScale = Math.max(minScale, Math.min(maxScale, z));
      if(center){
        const rect = canvasFrame.getBoundingClientRect();
        const cx = (center.x - rect.left - originX) / scale;
        const cy = (center.y - rect.top - originY) / scale;
        originX -= (newScale/scale - 1) * cx;
        originY -= (newScale/scale - 1) * cy;
      }
      scale = newScale;
      // if we've zoomed back to base, reset origin to center
      if(Math.abs(scale - baseScale) < 1e-6){ originX = 0; originY = 0; }
      applyTransform();
    }

    function highlightActionWords(text){
      // Only highlight segments wrapped in backticks `...`.
      // e.g. "Schritt `Klick`" -> the Klickeintrag gets an action-pill.
      const frag = document.createDocumentFragment();
      const re = /`([^`]+)`/g;
      let lastIndex = 0;
      let m;
      while((m = re.exec(String(text))) !== null){
        const idx = m.index;
        if(idx > lastIndex){
          frag.appendChild(document.createTextNode(text.slice(lastIndex, idx)));
        }
        const token = m[1];
        // Only use generic action-pill class now; no keyword matching.
        const span = document.createElement('span');
        span.className = 'action-pill action-generic';
        span.textContent = token;
        frag.appendChild(span);
        lastIndex = re.lastIndex;
      }
      if(lastIndex < text.length){
        frag.appendChild(document.createTextNode(text.slice(lastIndex)));
      }
      return frag;
    }

    function render(){
      if(!data) return;
      const step = data.steps[i];
      const pill = root.querySelector('#stepPill');
      if(pill){
        pill.innerHTML = '';
        const lbl = step.label || ('Schritt '+(i+1));
        pill.appendChild(highlightActionWords(lbl));
      }
      const counter = root.querySelector('#stepCounter'); if(counter) counter.textContent = 'Schritt ' + (i+1) + ' von ' + data.steps.length;

      const tmp = new Image();
      tmp.onload = ()=>{ imgEl.src = tmp.src; computeBaseScaleAndFit(tmp); renderHighlights(step); };
      // Resolve image paths relative to the discovered jsonBase if possible
      let candidateImage = step.image || '';
      try{
        // normalize Windows-style backslashes and remove leading slashes so
        // paths like "\\img\\step-0.png" become "img/step-0.png" and
        // will be resolved relative to the imported.json base path.
        if(typeof candidateImage === 'string'){
          candidateImage = candidateImage.replace(/\\\\/g,'/').replace(/\\/g,'/');
          candidateImage = candidateImage.replace(/^\/+/, '');
        }
      }catch(e){}
      if(candidateImage && jsonBase && !/^https?:\/\//.test(candidateImage) && !candidateImage.startsWith('/')){
        // if it's only a filename (like 'step-0.png'), prefix with img/
        try{
          if(typeof candidateImage === 'string' && candidateImage.indexOf('/') === -1){ candidateImage = 'img/' + candidateImage; }
        }catch(e){}
        // join relative to jsonBase
        try{ candidateImage = new URL(candidateImage, location.origin + jsonBase).pathname; }catch(e){}
      }
      // Compute final src using resolver and log it for debugging
        try{
          const finalSrc = (typeof resolveImageUrl === 'function' ? resolveImageUrl(candidateImage) : resolveImageUrlGlobal(candidateImage));
          tmp.src = finalSrc;
        }catch(e){ tmp.src = (typeof resolveImageUrl === 'function' ? resolveImageUrl(candidateImage) : resolveImageUrlGlobal(candidateImage)); }
      bar.style.width = ((i+1)/data.steps.length*100).toFixed(2) + '%';
      clearTimeout(timer);
      if(playing){ const dur = step.duration_ms ?? data.default_duration_ms ?? 1800; timer = setTimeout(next, dur); }
    }

    function prev(){ i=Math.max(0,i-1); render(); }
    function next(){ i=Math.min(data.steps.length-1,i+1); render(); }

    // events
    btnPrev.addEventListener('click', prev); btnNext.addEventListener('click', next);
  root.addEventListener('keydown',(e)=>{ if(e.key==='ArrowLeft') prev(); if(e.key==='ArrowRight') next(); });
  // clicking the image no longer advances; panning is activated by pointerdown + move
  canvasFrame.addEventListener('pointerdown',(ev)=>{
    // don't start panning when interacting with UI controls (buttons or overlays)
    if(ev.target && ev.target.closest && (ev.target.closest('button') || ev.target.closest('.zoom-floating') || ev.target.closest('#stepPill') || ev.target.closest('.nav-buttons'))) return;
    isPanning=true; panStart={x:ev.clientX-originX,y:ev.clientY-originY};
    try{ canvasFrame.setPointerCapture(ev.pointerId); }catch(e){}
  });
    window.addEventListener('pointermove',(ev)=>{ if(!isPanning) return; originX = ev.clientX - panStart.x; originY = ev.clientY - panStart.y; applyTransform(); });
    window.addEventListener('pointerup',(ev)=>{ isPanning=false; try{ canvasFrame.releasePointerCapture(ev.pointerId);}catch(e){} });
  // Mouse wheel zoom disabled to ensure the image remains fully visible.
  // canvasFrame.addEventListener('wheel',(ev)=>{ ev.preventDefault(); const delta=-ev.deltaY; const factor = delta>0?1.1:0.9; setZoom(scale*factor, {x:ev.clientX,y:ev.clientY}); }, {passive:false});

    // Zoom buttons
    if(btnZoomIn) btnZoomIn.addEventListener('click', (e)=>{ e.stopPropagation(); setZoom(scale*1.2); });
    if(btnZoomOut) btnZoomOut.addEventListener('click', (e)=>{ e.stopPropagation(); setZoom(scale/1.2); });

    // fetch candidates
    const candidates = [];
    if(opts.jsonUrl){ candidates.push(opts.jsonUrl); if(opts.jsonUrl.startsWith('/')) candidates.push(opts.jsonUrl.slice(1)); }
    if(opts.t){ const folder = String(opts.t).split('/')[0];
      // prefer the shorter /tutorials/<folder>/ path but keep legacy examples/ variants as fallback
      candidates.push('/tutorials/' + folder + '/imported.json');
      candidates.push('/tutorials/' + folder + '.json');
      candidates.push('/tutorials/examples/' + folder + '/imported.json');
      candidates.push('/tutorials/examples/' + folder + '.json');
      candidates.push('tutorials/' + folder + '/imported.json');
      candidates.push('tutorials/examples/' + folder + '/imported.json');
      candidates.push('examples/' + folder + '/imported.json');
      candidates.push('./examples/' + folder + '/imported.json'); }
    candidates.push('./imported.json'); candidates.push('imported.json');

    tryFetch(candidates).then(({json,path})=>{
      data = normalize(json);
      // compute base dir for images relative to the json path (keep trailing slash)
      try{
        let p = String(path || '');
        // if we were given an absolute URL (http(s)), derive the pathname from it
        if(/^https?:\/\//.test(p)){
          try{ jsonBase = new URL(p).pathname.replace(/\/[^\/]*$/, '/'); }
          catch(e){ jsonBase = null; }
        } else {
          if(!p.startsWith('/')) p = '/' + p;
          jsonBase = p.replace(/\/[^\/]*$/, '/');
        }
      }catch(e){ jsonBase = null; }
      // Debug: report where the JSON was loaded from and the derived base path for images
      
      i=0; playing=false; if(titleEl && data && data.title) titleEl.textContent = data.title; render(); if(cfg.zoom) setZoom(parseFloat(cfg.zoom));
    }).catch(err=>{ console.error('player load error',err); const dbg = document.createElement('div'); dbg.style.marginTop='8px'; dbg.style.fontSize='0.85em'; dbg.style.color='#a00'; dbg.textContent = 'Getestete Pfade: ' + candidates.join(' | '); try{ root.appendChild(dbg); }catch(e){} });

    root.tabIndex = 0; return { root, destroy: ()=>{ container.removeChild(root); } };
  }

  window.TutorialPlayer = { init };

})(window);

