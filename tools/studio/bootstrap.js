/* Einmaliger Bootstrap: aktuellen AUTO-NAV-Block aus mkdocs.yml nach
 * content/ überführen (course.json + je Praktikum praktikum.json, alles als
 * extern-Referenzen). Danach beweist verify.js, dass die Regenerierung ein
 * No-Op gegen den Ist-Stand ist.
 *
 *   node tools/studio/bootstrap.js        (aus dem Repo-Wurzelverzeichnis)
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
  if (a < 0 || b < 0) throw new Error('AUTO-NAV-Marker nicht gefunden');
  return lines.slice(a + 1, b);
}

function main() {
  const mk = fs.readFileSync(MK, 'utf8');
  const praktika = G.parseNavBlock(navBlockLines(mk));

  fs.mkdirSync(CONTENT, { recursive: true });
  const order = [];
  for (const p of praktika) {
    if (!p.slug) throw new Error('Kein Slug für Praktikum "' + p.nav + '"');
    order.push(p.slug);
    const dir = path.join(CONTENT, p.slug);
    fs.mkdirSync(dir, { recursive: true });
    const doc = { slug: p.slug, nav: p.nav, kinder: p.kinder };
    fs.writeFileSync(path.join(dir, 'praktikum.json'),
      JSON.stringify(doc, null, 2) + '\n', 'utf8');
    console.log('  praktikum.json ->', p.slug, '(' + p.kinder.length + ' Knoten)');
  }
  fs.writeFileSync(path.join(CONTENT, 'course.json'),
    JSON.stringify({ praktika: order }, null, 2) + '\n', 'utf8');
  console.log('course.json ->', order.join(', '));
}
main();
