/* Mini-Selbsttest des Inhalts-Generators: node tools/studio/test-gen-content.js */
const C = require('./gen-content.js');
const u = { typ:'uebung', titel:'T', gegeben:[{art:'text',md:'x'}],
  fragen:[ {typ:'numerisch',frage:'a',antwort:7.378,toleranz:0.1,punkte:5,versuche:5,hinweise:'h'},
           {typ:'mc',frage:'b',optionen:['x','y','z'],richtig:[1],punkte:3,versuche:3} ] };
const md = C.generateUebung(u,{rel:'P/uebung.json'});
function assert(c,m){ if(!c){ console.error('FEHLGESCHLAGEN:',m); process.exit(1);} }
assert(/data-answer="7.378"/.test(md),'numeric data-answer');
assert(/data-tolerance="0.1"/.test(md),'numeric tolerance');
assert(/data-attempts="5"/.test(md),'numeric attempts');
assert(/data-correct="B"/.test(md),'mc data-correct=B (richtig[1])');
assert(/id="q2b" name="q2"/.test(md),'mc option ids');
assert(/inhalt-hash:[a-z0-9]+/.test(md),'marker mit hash');
assert(!C.handEdited(md),'frisch generiert = nicht handEdited');
assert(C.handEdited(md.replace('# T','# GEÄNDERT')),'manipulierte Datei = handEdited');
console.log('✓ gen-content Selbsttest bestanden');
