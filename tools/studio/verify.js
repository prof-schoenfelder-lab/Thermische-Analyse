/* No-Op-Beweis: content/ -> Nav-Block generieren, gegen den aktuellen
 * AUTO-NAV-Block in mkdocs.yml SEMANTISCH vergleichen (Baum-Gleichheit;
 * Kommentare/Whitespace egal — die gebaute Site muss identisch sein).
 *
 *   node tools/studio/verify.js
 * Exit 0 = identisch, Exit 1 = Abweichung (mit Diff-Hinweis).
 */
const fs = require('fs');
const path = require('path');
const G = require('./generator.js');

const REPO = process.cwd();
const MK = path.join(REPO, 'mkdocs.yml');
const CONTENT = path.join(REPO, 'content');

function navBlockLines(mk) {
  const lines = mk.split('\n');
  const a = lines.findIndex(l => l.includes('# >>> AUTO-NAV'));
  const b = lines.findIndex(l => l.includes('# <<< AUTO-NAV'));
  return lines.slice(a + 1, b);
}

function loadCourse() {
  const course = JSON.parse(fs.readFileSync(path.join(CONTENT, 'course.json'), 'utf8'));
  const praktika = {};
  for (const slug of course.praktika) {
    praktika[slug] = JSON.parse(
      fs.readFileSync(path.join(CONTENT, slug, 'praktikum.json'), 'utf8'));
  }
  return { course, praktika };
}

function main() {
  const mk = fs.readFileSync(MK, 'utf8');
  const currentTree = G.parseNavBlock(navBlockLines(mk));

  const { course, praktika } = loadCourse();
  const generated = G.generateNav(course, praktika);
  const generatedTree = G.parseNavBlock(generated.split('\n'));

  const equal = G.treeEqual(currentTree, generatedTree);
  const countNodes = t => JSON.stringify(t.map(G.normNode)).match(/"e":/g);
  console.log('Praktika:', currentTree.length, '| Blattseiten:',
    (countNodes(currentTree) || []).length);

  if (equal) {
    console.log('✓ No-Op-Beweis bestanden: generierte Nav === aktuelle Nav (semantisch).');
    process.exit(0);
  }
  // Diff: erste abweichende Praktikums-Zeile grob anzeigen
  const A = JSON.stringify(currentTree.map(G.normNode), null, 1).split('\n');
  const B = JSON.stringify(generatedTree.map(G.normNode), null, 1).split('\n');
  for (let i = 0; i < Math.max(A.length, B.length); i++) {
    if (A[i] !== B[i]) {
      console.error('✗ Abweichung ab Zeile ' + i + ':');
      console.error('  IST:  ' + (A[i] || '—'));
      console.error('  NEU:  ' + (B[i] || '—'));
      break;
    }
  }
  process.exit(1);
}
main();
