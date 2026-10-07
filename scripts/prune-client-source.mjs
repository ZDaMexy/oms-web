// Remove unreachable upstream code, keeping the actual TypeScript/Coffee and
// original BEM dependency graph. Review the manifest and run build + browser gates.
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const root = path.resolve(import.meta.dirname, '..');
if (!/^F:\\/i.test(root) && !root.startsWith('/mnt/f/')) throw new Error('F checkout required');
const js = path.join(root, 'resources/js');
const css = path.join(root, 'resources/css');
const walk = directory => fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? walk(path.join(directory, entry.name)) : [path.join(directory, entry.name)]);
const read = file => fs.readFileSync(file, 'utf8');
const globals = path.join(js, 'globals.d.ts');
fs.writeFileSync(globals, read(globals).replace(/declare module 'mod-names\.json' \{[\s\S]*?\n\}\r?\n\r?\n/, ''));
const config = ts.readConfigFile(path.join(root, 'tsconfig.json'), ts.sys.readFile);
if (config.error) throw new Error('Invalid tsconfig');
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, root);
const program = ts.createProgram(parsed.fileNames, parsed.options);
const kept = new Set(program.getSourceFiles().map(file => path.resolve(file.fileName)).filter(file => file.startsWith(js + path.sep)));
const resolveLocal = (specifier, owner) => {
  const base = specifier.startsWith('.') ? path.resolve(path.dirname(owner), specifier) : path.join(js, specifier);
  if (!base.startsWith(js + path.sep)) return null;
  const found = [base, ...['.ts', '.tsx', '.coffee', '.json', '/index.ts', '/index.tsx'].map(ext => base + ext)].find(file => fs.existsSync(file) && fs.statSync(file).isFile());
  return found == null ? null : path.resolve(found);
};
let changed = true;
while (changed) {
  changed = false;
  for (const file of [...kept]) {
    for (const match of read(file).matchAll(/(?:from\s*|import\s*|require\s*\(?)['"]([^'"]+)['"]/g)) {
      const dependency = resolveLocal(match[1], file);
      if (dependency != null && !kept.has(dependency)) { kept.add(dependency); changed = true; }
    }
  }
}
const removedJs = walk(js).filter(file => !kept.has(file));
for (const file of removedJs) fs.unlinkSync(file);

const activeText = [...kept, ...walk(path.join(root, 'resources/views'))].map(read).join('\n');
const bemFiles = walk(path.join(css, 'bem')).filter(file => file.endsWith('.less'));
const mentions = (name, text) => new RegExp(`(^|[^a-zA-Z0-9-])${name.replaceAll('-', '\\-')}(?=__|--|[^a-zA-Z0-9-]|$)`).test(text);
const keptBem = new Set(bemFiles.filter(file => mentions(path.basename(file, '.less'), activeText)));
// Shared Less mixins and :extend references can require otherwise unused BEM.
const shared = new Set();
const visitStyle = file => {
  if (shared.has(file) || file.endsWith('bem-index.less')) return;
  shared.add(file);
  for (const match of read(file).matchAll(/@import\s+(?:\([^)]*\)\s*)?["']([^"']+)["']/g)) {
    if (match[1].startsWith('~')) continue;
    const base = path.resolve(path.dirname(file), match[1]);
    const dependency = [base, base + '.less'].find(item => fs.existsSync(item) && fs.statSync(item).isFile());
    if (dependency != null) visitStyle(dependency);
  }
};
visitStyle(path.join(css, 'entrypoints/app.less'));
const sharedText = [...shared].map(read).join('\n');
changed = true;
while (changed) {
  changed = false;
  const styles = sharedText + [...keptBem].map(read).join('\n');
  for (const file of bemFiles) {
    if (!keptBem.has(file) && mentions(path.basename(file, '.less'), styles)) { keptBem.add(file); changed = true; }
  }
}
const index = path.join(css, 'bem-index.less');
fs.writeFileSync(index, read(index).split(/\r?\n/).filter(line => {
  const match = line.match(/^@import "bem\/(.+)";/);
  return match == null || keptBem.has(path.join(css, 'bem', match[1] + '.less'));
}).join('\n'));
const removedBem = bemFiles.filter(file => !keptBem.has(file));
for (const file of removedBem) fs.unlinkSync(file);
const relative = files => files.map(file => path.relative(root, file).replaceAll('\\', '/')).sort();
fs.mkdirSync(path.join(root, 'artifacts'), { recursive: true });
fs.writeFileSync(path.join(root, 'artifacts/pruned-client.json'), JSON.stringify({ keptJs: relative([...kept]), removedJs: relative(removedJs), keptBem: relative([...keptBem]), removedBem: relative(removedBem) }, null, 2));
console.log(JSON.stringify({ js: kept.size, removedJs: removedJs.length, bem: keptBem.size, removedBem: removedBem.length }));
