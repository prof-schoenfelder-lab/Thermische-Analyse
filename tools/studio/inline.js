/* Kurs-Studio — Inline-Renderer für Vorschauen (Chips, Klick-Pillen,
 * Tastenkappen). Spiegelt die Kurs-Logik aus modern-ui.js; für Studios,
 * die eine Live-Vorschau von Beschreibungen zeigen. Browser: window.KursInline.
 * (CSS dazu: die .pv-…-Regeln im jeweiligen Studio.)
 */
(function (root) {
  'use strict';
  var MP_ICONS = {
    reiter:'<svg viewBox="0 0 24 24"><path d="M3 7h6l2-2.5h10V19H3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    baum:'<svg viewBox="0 0 24 24"><path d="M6 4v13a2 2 0 0 0 2 2h4M6 9h6M10 14h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="6" cy="4" r="2" fill="currentColor"/></svg>',
    detail:'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 4v16" stroke="currentColor" stroke-width="2"/><path d="M12 9h6M12 13h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    maus:'<svg viewBox="0 0 24 24"><rect x="6.5" y="2.5" width="11" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 3v6.3" stroke="currentColor" stroke-width="1.4"/><path d="M12 3.4h4.1a4.7 4.7 0 0 1 1.4 5.9H12z" fill="currentColor"/></svg>',
    mausL:'<svg viewBox="0 0 24 24"><rect x="6.5" y="2.5" width="11" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 3v6.3" stroke="currentColor" stroke-width="1.4"/><path d="M12 3.4H7.9a4.7 4.7 0 0 0-1.4 5.9H12z" fill="currentColor"/></svg>',
    mausD:'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="10" height="16.5" rx="5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M8 5.5v5.6" stroke="currentColor" stroke-width="1.4"/><path d="M8 5.9H4.6a4.3 4.3 0 0 0-1.3 5.2H8z" fill="currentColor"/><circle cx="18" cy="6" r="5.4" fill="currentColor"/><text x="18" y="9.15" text-anchor="middle" font-family="sans-serif" font-size="8.4" font-weight="700" fill="#fff">2</text></svg>',
    grafik:'<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 21h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M5 14l4-4 3 3 4-5 3 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'
  };
  function mpKind(text){var t=text.toLowerCase();
    if(t.indexOf("rechtsklick")===0)return"maus";
    if(t.indexOf("doppelklick")===0)return"mausD";
    if(t.indexOf("linksklick")===0)return"mausL";
    if(t.indexOf("reiter")===0||t.indexOf("tab ")===0)return"reiter";
    if(t.indexOf("strukturbaum")!==-1)return"baum";
    if(t.indexOf("detailfenster")!==-1)return"detail";
    if(t.indexOf("grafikfenster")!==-1)return"grafik";return null;}
  var MP_PREFIX=[
    {kw:"Rechtsklick",icon:"maus",cls:"act"},{kw:"Doppelklick",icon:"mausD",cls:"act"},{kw:"Linksklick",icon:"mausL",cls:"act"},
    {kw:"Reiter",icon:"reiter",cls:"loc",merge:true},{kw:"Strukturbaum",icon:"baum",cls:"loc",merge:true},
    {kw:"Detailfenster",icon:"detail",cls:"loc",merge:true},{kw:"Grafikfenster",icon:"grafik",cls:"loc",merge:true}];
  function prefixFor(label){for(var k=0;k<MP_PREFIX.length;k++){var kw=MP_PREFIX[k].kw;
    if(label===kw)return{def:MP_PREFIX[k],rest:""};
    if(label.indexOf(kw+" ")===0)return{def:MP_PREFIX[k],rest:label.slice(kw.length+1).trim()};}return null;}
  var MP_SOLO=/^(Reiter |Rechtsklick|Doppelklick|Linksklick|Strukturbaum|Detailfenster|Grafikfenster)/;
  function mpPlain(label){var seg=document.createElement("span");seg.className="mp-seg";var kind=mpKind(label);
    if(kind){seg.classList.add("mp-"+kind);seg.innerHTML='<i class="mp-ic">'+MP_ICONS[kind]+"</i>";seg.appendChild(document.createTextNode(label));}
    else{seg.textContent=label;}return seg;}
  function splitPrefixes(label){var comps=[];while(true){var pf=prefixFor(label);if(!pf)break;comps.push({kw:pf.def.kw,icon:pf.def.icon,cls:pf.def.cls});label=pf.rest;if(!label)break;}return{comps:comps,tail:label};}
  function buildPill(comps,tail){var g=document.createElement("span");g.className="mp-click mp-click--"+comps[0].cls;
    for(var i=0;i<comps.length;i++){var seg=document.createElement("span");
      seg.className="mp-seg mp-"+(comps[i].cls==="act"?"action":"loc");
      seg.innerHTML='<i class="mp-ic">'+MP_ICONS[comps[i].icon]+"</i>";seg.appendChild(document.createTextNode(comps[i].kw));g.appendChild(seg);}
    if(tail)g.appendChild(mpPlain(tail));return g;}
  function chipify(root){var codes=root.querySelectorAll("code");
    for(var i=0;i<codes.length;i++){var c=codes[i],t=c.textContent;
      if(t.indexOf("→")===-1&&t.indexOf(">")===-1&&!MP_SOLO.test(t))continue;
      var parts=t.split(/\s*(?:→|->|>)\s*/).filter(function(s){return s.trim()!=="";}),span=document.createElement("span");span.className="menu-path";var first=true;
      for(var p=0;p<parts.length;p++){var label=parts[p].trim();
        var pf0=prefixFor(label);
        if(pf0&&!pf0.rest&&pf0.def.merge&&p+1<parts.length){label=label+" "+parts[p+1].trim();p++;}
        var sp=splitPrefixes(label),node;
        if(sp.comps.length===0)node=mpPlain(sp.tail);
        else if(sp.comps.length===1&&!sp.tail)node=mpPlain(sp.comps[0].kw);
        else node=buildPill(sp.comps,sp.tail);
        if(!first){var ar=document.createElement("span");ar.className="mp-arrow";ar.textContent="→";span.appendChild(ar);}
        first=false;span.appendChild(node);}
      c.parentNode.replaceChild(span,c);}}
  var KEY_LABELS={enter:"⏎ Enter","return":"⏎ Enter",esc:"Esc",escape:"Esc",tab:"↹ Tab",strg:"Strg",ctrl:"Strg",control:"Strg",shift:"⇧ Shift",umschalt:"⇧ Umschalt",alt:"Alt",entf:"Entf",del:"Entf","delete":"Entf",backspace:"⌫","rücktaste":"⌫ Rücktaste",leertaste:"Leertaste",space:"Leertaste"};
  function keyLabel(tok){var t=tok.toLowerCase();if(KEY_LABELS.hasOwnProperty(t))return KEY_LABELS[t];if(/^f([1-9]|1[0-2])$/.test(t))return tok.toUpperCase();return null;}
  function isKeyTok(tok){return keyLabel(tok)!==null||/^[A-Za-z0-9]$/.test(tok);}
  function keyCaps(root){var codes=root.querySelectorAll("code");
    for(var i=0;i<codes.length;i++){var c=codes[i],txt=c.textContent.trim();
      var toks=txt.split("+").map(function(s){return s.trim();}).filter(function(s){return s.length;});
      if(!toks.length)continue;var hasReal=false,allOk=true;
      for(var k=0;k<toks.length;k++){if(keyLabel(toks[k]))hasReal=true;if(!isKeyTok(toks[k]))allOk=false;}
      if(!hasReal||!allOk)continue;if(toks.length===1&&!keyLabel(toks[0]))continue;
      var span=document.createElement("span");span.className="keys";
      for(var m=0;m<toks.length;m++){if(m>0){var pl=document.createElement("span");pl.className="keys-plus";pl.textContent="+";span.appendChild(pl);}
        var kbd=document.createElement("kbd");kbd.className="kc";kbd.textContent=keyLabel(toks[m])||toks[m].toUpperCase();span.appendChild(kbd);}
      c.parentNode.replaceChild(span,c);}}
  function mdInline(s){var out=(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    out=out.replace(/`([^`]+)`/g,function(_,c){return "<code>"+c+"</code>";});
    out=out.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>");
    out=out.replace(/\*([^*]+)\*/g,"<em>$1</em>");return out;}
  function renderInline(text){var d=document.createElement("span");d.innerHTML=mdInline(text);chipify(d);keyCaps(d);return d;}
  if(root) root.KursInline={renderInline:renderInline, chipify:chipify, keyCaps:keyCaps};
})(typeof window!=="undefined"?window:null);
