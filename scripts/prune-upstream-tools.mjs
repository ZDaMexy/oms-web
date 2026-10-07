// Only unchanged, Git-tracked upstream tools are removed; no recursive delete.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
const root = path.resolve(import.meta.dirname, '..');
if (!/^F:\\/i.test(root)) throw new Error('Run source cleanup on F with UseDevelopmentStorage.ps1');
const scope = ['tests', 'database', 'docker', 'bin', 'yarn.lock', 'phpunit.xml', 'phpunit.dusk.xml', 'docker-compose.yml', 'docker-compose.override.yml', 'Dockerfile'];
const git = args => {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  if (result.status !== 0) throw new Error('Git source verification failed');
  return result.stdout;
};
if (git(['diff', '--name-only', '--diff-filter=ACMRTUXB', '--', ...scope]).trim() !== '') throw new Error('Source tools have local edits; preserve and review them');
const files = git(['ls-files', '-z', '--', ...scope]).split('\0').filter(Boolean);
for (const relative of files) {
  const file = path.resolve(root, relative);
  if (!file.startsWith(root + path.sep)) throw new Error('Source path outside checkout');
  if (!fs.existsSync(file)) continue;
  for (let ancestor = file; ancestor !== root; ancestor = path.dirname(ancestor)) {
    if (fs.lstatSync(ancestor).isSymbolicLink()) throw new Error('Source path redirected');
  }
  if (!fs.lstatSync(file).isFile()) throw new Error('Source entry is not a regular file');
}
fs.mkdirSync(path.join(root, 'artifacts'), { recursive: true });
fs.writeFileSync(path.join(root, 'artifacts/pruned-upstream-tools.json'), JSON.stringify({scope, files, provenance:'unchanged upstream files in current Git HEAD'}, null, 2));
for (const relative of files) if (fs.existsSync(path.join(root, relative))) fs.unlinkSync(path.join(root, relative));
console.log(JSON.stringify({removedFiles:files.length, directoriesRecursivelyRemoved:0}));
