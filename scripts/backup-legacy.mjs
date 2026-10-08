import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const [sourceArg, destinationArg] = process.argv.slice(2);
if (!sourceArg || !destinationArg) throw new Error('Usage: node scripts/backup-legacy.mjs SOURCE DESTINATION');
const source = path.resolve(sourceArg);
const destination = path.resolve(destinationArg);
if (!source.toLowerCase().endsWith(`${path.sep}websites${path.sep}oms-website`)) throw new Error('Only the designated old website is accepted.');
if (path.parse(destination).root.toLowerCase() !== 'f:\\') throw new Error('Legacy design backups must stay on F.');
if (existsSync(path.join(destination, 'legacy.bundle'))) throw new Error('Backup already exists; do not overwrite recovery evidence.');
mkdirSync(destination, { recursive: true });
const git = (args, cwd = source) => execFileSync('git', ['-C', cwd, ...args], { maxBuffer: 32 * 1024 * 1024 });
const hash = (data) => createHash('sha256').update(data).digest('hex');
const head = git(['rev-parse', 'HEAD']).toString().trim();
const status = git(['status', '--porcelain=v1', '-z']);
const files = git(['ls-files', '-z']).toString().split('\0').filter(Boolean);
const snapshot = () => files.map((relative) => {
  const filename = path.join(source, relative);
  return existsSync(filename)
    ? { path: relative, bytes: statSync(filename).size, sha256: hash(readFileSync(filename)) }
    : { path: relative, deleted: true };
});
const before = snapshot();
if (git(['ls-files', '--others', '--exclude-standard', '-z']).length) throw new Error('Untracked source files need an explicit archive review.');
const rawWorkingTree = path.join(destination, 'working-tree');
for (const entry of before) {
  if (!entry.deleted) {
    const copyTarget = path.join(rawWorkingTree, entry.path);
    mkdirSync(path.dirname(copyTarget), { recursive: true });
    copyFileSync(path.join(source, entry.path), copyTarget);
  }
}
execFileSync('tar', ['-czf', path.join(destination, 'working-tree.tar.gz'), '-C', rawWorkingTree, '.']);
const patch = git(['diff', '--binary', 'HEAD', '--']);
writeFileSync(path.join(destination, 'working-tree.patch'), patch);
writeFileSync(path.join(destination, 'working-tree-status.bin'), status);
git(['bundle', 'create', path.join(destination, 'legacy.bundle'), '--all']);
git(['bundle', 'verify', path.join(destination, 'legacy.bundle')]);
const revisions = {
  original: 'e8b764bcbbc9a7c25c330f5a6b144692bb374dd5',
  published: 'e6fdf914cb04b89c73b29d5703d0f21fccb28696',
  head,
};
for (const [name, revision] of Object.entries(revisions)) {
  git(['-c', 'core.autocrlf=false', '-c', 'core.eol=lf', 'archive', '--format=tar.gz', `--output=${path.join(destination, `${name}.tar.gz`)}`, revision]);
}
const restore = path.join(destination, 'restore-current');
if (existsSync(restore)) throw new Error('Recovery directory must be new.');
execFileSync('git', ['clone', '--quiet', '--branch', 'main', path.join(destination, 'legacy.bundle'), restore]);
if (patch.length) git(['apply', '--binary', path.join(destination, 'working-tree.patch')], restore);
// Git checkout normalizes text according to autocrlf. Restore exact original bytes too.
for (const entry of before) {
  if (!entry.deleted) {
    const copyTarget = path.join(restore, entry.path);
    mkdirSync(path.dirname(copyTarget), { recursive: true });
    copyFileSync(path.join(rawWorkingTree, entry.path), copyTarget);
  }
}
for (const entry of before) {
  const filename = path.join(restore, entry.path);
  if (entry.deleted) {
    if (existsSync(filename)) throw new Error(`Deleted file reappeared: ${entry.path}`);
  } else if (!existsSync(filename) || hash(readFileSync(filename)) !== entry.sha256) {
    throw new Error(`Recovered working tree differs: ${entry.path}`);
  }
}
const originalRestore = path.join(destination, 'restore-original');
mkdirSync(originalRestore);
execFileSync('tar', ['-xzf', path.join(destination, 'original.tar.gz'), '-C', originalRestore]);
for (const relative of ['index.html', 'assets/styles/site.css', 'assets/scripts/site.js', 'assets/scripts/i18n.js', 'assets/scripts/chart-lost.js']) {
  const original = git(['show', `${revisions.original}:${relative}`]);
  if (hash(readFileSync(path.join(originalRestore, relative))) !== hash(original)) throw new Error(`Original recovery differs: ${relative}`);
}
const production = 'F:/zdamexy-workspace/oms/artifacts/oms-deai-20261007/oms-ir-d1f052b93a81-e6fdf914cb04.tar.gz';
copyFileSync(production, path.join(destination, 'published-runtime.tar.gz'));
if (hash(readFileSync(production)) !== 'b2bc5c490b5f2e6bddb72bb4cdb35ab0b7412507d4ae8b9ac8bc3cd59b78e62b') throw new Error('Published runtime hash differs.');
if (hash(git(['status', '--porcelain=v1', '-z'])) !== hash(status) || JSON.stringify(snapshot()) !== JSON.stringify(before)) throw new Error('Original work changed during capture.');
const archiveFiles = ['legacy.bundle', 'working-tree.patch', 'working-tree-status.bin', 'working-tree.tar.gz', 'original.tar.gz', 'published.tar.gz', 'head.tar.gz', 'published-runtime.tar.gz'];
const report = {
  capturedAt: new Date().toISOString(), source, head, revisions,
  workingTree: before, workingTreeRestored: true, originalFiveFilesRestored: true,
  untrackedCount: 0, sourceUnchanged: true,
  offlineOriginalFontsComplete: false,
  fontBoundary: 'Original Google Fonts are external; archive is unchanged. Separate local fonts and licensed offline overlay remain required.',
  files: archiveFiles.map((relative) => ({ path: relative, bytes: statSync(path.join(destination, relative)).size, sha256: hash(readFileSync(path.join(destination, relative))) })),
};
writeFileSync(path.join(destination, 'recovery-report.json'), `${JSON.stringify(report, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({ destination, workingTreeRestored: true, originalFiveFilesRestored: true, sourceUnchanged: true, offlineFontsPending: true, trackedFiles: files.length })}\n`);
