// Licensed under AGPL-3.0-or-later; see LICENCE.
// Usage (same Alpine WSL, Node 24):
// node scripts/restore-local.mjs BACKUP_ROOT NEW_ROOT_1 [NEW_ROOT_2]
// BACKUP_ROOT contains source-manifest.json and local-runtime.tar.
// This restores files and checks a task-owned SQLite snapshot; it never starts HTTP.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createReadStream, existsSync } from 'node:fs';
import { lstat, readFile, readdir, readlink, realpath, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const [backupArg, ...targetArgs] = process.argv.slice(2);
if (!backupArg || targetArgs.length < 1 || targetArgs.length > 2) {
  throw new Error('Usage: node scripts/restore-local.mjs BACKUP_ROOT NEW_ROOT_1 [NEW_ROOT_2]');
}
if (process.platform !== 'linux' || Number(process.versions.node.split('.')[0]) !== 24) {
  throw new Error('Run recovery with Node 24 inside the existing Alpine WSL.');
}
const designatedBackup = '/mnt/f/zdamexy-workspace/websites/oms-web/artifacts/local-recovery';
const publicArchive = '/mnt/f/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db';
const backupRoot = path.resolve(backupArg);
const targets = targetArgs.map((target) => path.resolve(target));
const webPrefix = 'websites/oms-web/';
const backendPrefix = 'oms-server/oms-backend/';
const databasePath = webPrefix + '.dev-cache/local-runtime/live.db';
const runtimePrefixes = [
  webPrefix + 'vendor/',
  webPrefix + 'public/assets/',
  webPrefix + '.dev-cache/backend-venv/',
  webPrefix + '.dev-cache/local-runtime/legacy-ir/',
];
const generatedFiles = new Set([
  webPrefix + 'bootstrap/cache/packages.php',
  webPrefix + 'bootstrap/cache/services.php',
]);
const freshDirectories = [
  [webPrefix + '.dev-cache/temp', 0o755],
  [webPrefix + '.dev-cache/local-runtime', 0o755],
  [webPrefix + '.dev-cache/local-runtime/nginx-tmp', 0o777],
  [webPrefix + 'artifacts', 0o777],
  [webPrefix + 'bootstrap/cache', 0o777],
  [webPrefix + 'storage/framework/cache', 0o777],
  [webPrefix + 'storage/framework/cache/data', 0o777],
  [webPrefix + 'storage/framework/views', 0o777],
  [webPrefix + 'storage/logs', 0o777],
];
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const digestPattern = /^[a-f0-9]{64}$/;
const ancestorOf = (parent, child) => child === parent || child.startsWith(parent + '/');

function requireFPath(value) {
  if (!value.startsWith('/mnt/f/') || /(^|\/)private-data(\/|$)/i.test(value)) {
    throw new Error('Recovery paths must stay on F and outside private-data.');
  }
}

function requireRelative(value) {
  if (typeof value !== 'string' || !value || value.startsWith('/') || /[\\:\x00-\x1f\x7f]/.test(value)
    || value.split('/').some((part) => !part || part === '.' || part === '..')) {
    throw new Error('A recovery manifest path is not a safe relative path.');
  }
  const parts = value.split('/');
  if (parts.some((part) => ['.git', '.ssh', 'node_modules', 'private-data'].includes(part)
    || /^\.env(?:\.|$)/.test(part) && part !== '.env.example')) {
    throw new Error('Git, node_modules, credentials and private directories are excluded.');
  }
  if (/\.(db|sqlite|sqlite3)(-(wal|shm))?$/.test(value) && value !== databasePath) {
    throw new Error('Only the task-owned standalone SQLite snapshot may be restored.');
  }
}

async function fileHash(filename) {
  const digest = createHash('sha256');
  for await (const chunk of createReadStream(filename)) digest.update(chunk);
  return digest.digest('hex');
}

function version(command, args, pattern) {
  const result = spawnSync(command, args, { encoding: 'utf8' });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error('Required local OS command failed: ' + command);
  const found = (result.stdout + '\n' + result.stderr).match(pattern);
  if (!found) throw new Error('Cannot identify local OS command version: ' + command);
  return found[1];
}

async function runtimeVersions() {
  return {
    alpine: (await readFile('/etc/alpine-release', 'utf8')).trim(),
    php: version('php85', ['--version'], /PHP (\d+\.\d+\.\d+)/),
    python: version('python3', ['--version'], /Python (\d+\.\d+\.\d+)/),
    node: process.versions.node,
    nginx: version('nginx', ['-v'], /nginx\/(\d+\.\d+\.\d+)/),
    wslDistro: process.env.WSL_DISTRO_NAME ?? null,
  };
}

function validateManifest(manifest) {
  if (manifest.schemaVersion !== 1 || manifest.kind !== 'oms-web-local-runtime-recovery'
    || !Array.isArray(manifest.files) || !manifest.files.length || !Array.isArray(manifest.sourceAllowlist)) {
    throw new Error('Unsupported local recovery manifest.');
  }
  if (manifest.archive?.file !== 'local-runtime.tar' || !digestPattern.test(manifest.archive.sha256)
    || !Number.isSafeInteger(manifest.archive.bytes) || manifest.archive.bytes <= 0) {
    throw new Error('The immutable runtime archive identity is missing.');
  }
  if (manifest.database?.path !== databasePath || manifest.database.captureMethod !== 'sqlite-backup-api'
    || manifest.database.taskOwnedTestData !== true || manifest.runtime?.publicArchive !== publicArchive) {
    throw new Error('Recovery requires the task-owned consistent SQLite backup and approved external projection.');
  }
  const sources = new Set();
  for (const source of manifest.sourceAllowlist) {
    requireRelative(source);
    if (sources.has(source) || !(source.startsWith(webPrefix) || source.startsWith(backendPrefix))) {
      throw new Error('The source allowlist has an unexpected or duplicate entry.');
    }
    if (source.startsWith(backendPrefix) && /^(\.dev-cache|\.venv|artifacts)\//.test(source.slice(backendPrefix.length))
      || source.startsWith(webPrefix) && /^(\.dev-cache|artifacts|vendor|public\/assets)\//.test(source.slice(webPrefix.length))) {
      throw new Error('Runtime files must use the explicitly permitted recovery prefixes.');
    }
    sources.add(source);
  }
  const records = new Map();
  const directories = new Set(['', 'websites', 'websites/oms-web', 'oms-server', 'oms-server/oms-backend']);
  for (const record of manifest.files) {
    requireRelative(record.path);
    if (records.has(record.path) || !['file', 'symlink'].includes(record.type) || !digestPattern.test(record.sha256)) {
      throw new Error('A runtime recovery file has an invalid or duplicate identity.');
    }
    if (!sources.has(record.path) && !runtimePrefixes.some((prefix) => record.path.startsWith(prefix))
      && !generatedFiles.has(record.path) && record.path !== databasePath) {
      throw new Error('A file is outside the explicitly permitted recovery scope.');
    }
    if (record.type === 'file') {
      if (!Number.isSafeInteger(record.bytes) || record.bytes < 0
        || record.mode !== undefined && (!Number.isInteger(record.mode) || record.mode < 0 || record.mode > 0o777)) {
        throw new Error('A regular file has an invalid size or mode.');
      }
    } else {
      if (typeof record.target !== 'string' || !record.target || /[\\\x00-\x1f\x7f]/.test(record.target)
        || sha256(Buffer.from(record.target)) !== record.sha256) {
        throw new Error('A symbolic link has an invalid identity.');
      }
      if (record.target.startsWith('/')) {
        if (!/^websites\/oms-web\/\.dev-cache\/backend-venv\/bin\/python(?:3(?:\.\d+)?)?$/.test(record.path)
          || !/^\/usr\/bin\/python3(?:\.\d+)?$/.test(record.target)) {
          throw new Error('Only the existing OS Python interpreter may be referenced by an absolute link.');
        }
      } else {
        const destination = path.posix.resolve('/recovery', path.posix.dirname(record.path), record.target);
        if (!destination.startsWith('/recovery/')) throw new Error('A symbolic link escapes its recovery root.');
      }
    }
    for (let parent = path.posix.dirname(record.path); parent !== '.'; parent = path.posix.dirname(parent)) directories.add(parent);
    records.set(record.path, record);
  }
  for (const [directory] of freshDirectories) {
    directories.add(directory);
    for (let parent = path.posix.dirname(directory); parent !== '.'; parent = path.posix.dirname(parent)) directories.add(parent);
  }
  for (const directory of directories) {
    if (records.has(directory)) throw new Error('A file or link is also used as a directory.');
  }
  for (const source of sources) {
    if (!records.has(source)) throw new Error('A declared source file is absent from the archive manifest.');
  }
  const required = [
    'artisan', 'bootstrap/app.php', 'app/helpers.php', 'public/index.php', 'public/assets/manifest.json',
    'vendor/autoload.php', 'composer.json', 'composer.lock', 'scripts/local-runtime.sh',
    '.dev-cache/backend-venv/pyvenv.cfg', '.dev-cache/backend-venv/bin/python',
    '.dev-cache/local-runtime/legacy-ir/adapters/versions.json',
  ].map((relative) => webPrefix + relative).concat([
    backendPrefix + 'oms_ir/__init__.py', backendPrefix + 'oms_ir/__main__.py',
    backendPrefix + 'oms_ir/app.py', backendPrefix + 'oms_ir/catalog_worker.py',
    backendPrefix + 'pyproject.toml', backendPrefix + 'uv.lock', databasePath,
  ]);
  for (const relative of required) if (!records.has(relative)) throw new Error('A necessary local runtime file is absent: ' + relative);
  if (records.get(databasePath).type !== 'file') throw new Error('The consistent database snapshot must be a regular file.');
  return { records, directories };
}

const restoreProgram = String.raw`
import json, os, pathlib, shutil, sqlite3, sys, tarfile

archive_path, target_root = sys.argv[1:3]
spec = json.load(sys.stdin)
expected = {entry["path"]: entry for entry in spec["files"]}
directories = set(spec["directories"])
runtime_prefixes = spec["runtimePrefixes"]

def name_for(member):
    value = member.name
    while value.startswith("./"):
        value = value[2:]
    if member.isdir():
        value = value.rstrip("/")
    if value in ("", ".") and member.isdir():
        return ""
    if value.startswith("/") or "\\" in value or ":" in value or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise RuntimeError("Unsafe archive member name")
    parts = value.split("/")
    if any(part in ("", ".", "..", ".git", ".ssh", "node_modules", "private-data") for part in parts):
        raise RuntimeError("Unsafe archive member scope")
    if any((part == ".env" or part.startswith(".env.")) and part != ".env.example" for part in parts):
        raise RuntimeError("Credentials are excluded from recovery")
    return value

with tarfile.open(archive_path, mode="r:") as archive:
    members = archive.getmembers()
    seen = set()
    bound = []
    for member in members:
        name = name_for(member)
        if name in seen:
            raise RuntimeError("Duplicate archive member")
        seen.add(name)
        if member.isdir():
            permitted = name in directories or any(name == prefix.rstrip("/") or name.startswith(prefix) for prefix in runtime_prefixes)
            if not permitted or member.size:
                raise RuntimeError("Unexpected archive directory")
            continue
        record = expected.get(name)
        if record is None:
            raise RuntimeError("Archive member is outside the manifest")
        if record["type"] == "file":
            if not member.isfile() or member.size != record["bytes"]:
                raise RuntimeError("Regular archive file identity differs")
        elif not member.issym() or member.linkname != record["target"]:
            raise RuntimeError("Symbolic link identity differs")
        if "mode" in record and member.mode & 0o777 != record["mode"]:
            raise RuntimeError("Archive member permissions differ")
        bound.append((member, record))
    if set(expected) != {record["path"] for _, record in bound}:
        raise RuntimeError("Archive is missing declared files")
    # No output is created until every member has been bound to the allowlist.
    os.mkdir(target_root, 0o755)
    for directory in sorted(directories, key=lambda name: (name.count("/"), name)):
        if directory:
            os.makedirs(os.path.join(target_root, directory), mode=0o755, exist_ok=True)
    for member, record in bound:
        if record["type"] != "file":
            continue
        destination = os.path.join(target_root, record["path"])
        os.makedirs(os.path.dirname(destination), mode=0o755, exist_ok=True)
        with archive.extractfile(member) as source, open(destination, "xb") as output:
            shutil.copyfileobj(source, output, length=64 * 1024)
        os.chmod(destination, record.get("mode", member.mode & 0o777))
    # Links are never dereferenced while copying; no archive file has a link parent.
    for member, record in bound:
        if record["type"] == "symlink":
            os.symlink(record["target"], os.path.join(target_root, record["path"]))

for relative, permissions in spec["freshDirectories"]:
    destination = os.path.join(target_root, relative)
    os.makedirs(destination, mode=permissions, exist_ok=True)
    os.chmod(destination, permissions)
database = os.path.join(target_root, spec["databasePath"])
os.chmod(database, 0o600)
connection = sqlite3.connect(pathlib.Path(database).as_uri() + "?mode=ro&immutable=1", uri=True)
try:
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise RuntimeError("Restored SQLite integrity_check failed")
finally:
    connection.close()
print(json.dumps({"restoredFiles": len(bound), "sqliteIntegrityCheck": "ok", "databaseMode": "0600"}))
`;

async function collectRestored(root, relative = '') {
  const result = [];
  for (const entry of await readdir(path.join(root, relative), { withFileTypes: true })) {
    const current = path.posix.join(relative, entry.name);
    if (entry.isDirectory()) result.push(...await collectRestored(root, current));
    else if (entry.isFile() || entry.isSymbolicLink()) result.push(current);
    else throw new Error('An unexpected filesystem object was restored.');
  }
  return result.sort();
}

async function main() {
  requireFPath(backupRoot);
  if (backupRoot !== designatedBackup || await realpath(backupRoot) !== backupRoot) throw new Error('Only the designated immutable local backup directory is accepted.');
  if (new Set(targets).size !== targets.length) throw new Error('Recovery roots must be distinct.');
  for (const target of targets) {
    requireFPath(target);
    if (existsSync(target) || ancestorOf(backupRoot, target) || ancestorOf(target, backupRoot)
      || targets.some((other) => other !== target && (ancestorOf(target, other) || ancestorOf(other, target)))) {
      throw new Error('Recovery requires new nonoverlapping directories outside the backup.');
    }
    const parent = path.dirname(target);
    if (await realpath(parent) !== parent) throw new Error('Create the target parent directly on F first; symbolic parent paths are rejected.');
  }
  const manifestPath = path.join(backupRoot, 'source-manifest.json');
  const archivePath = path.join(backupRoot, 'local-runtime.tar');
  for (const filename of [manifestPath, archivePath]) if (!(await lstat(filename)).isFile()) throw new Error('Backup inputs must be regular files.');
  const manifestBytes = await readFile(manifestPath);
  const manifest = JSON.parse(manifestBytes);
  const { records, directories } = validateManifest(manifest);
  if ((await lstat(archivePath)).size !== manifest.archive.bytes || await fileHash(archivePath) !== manifest.archive.sha256) {
    throw new Error('The readonly runtime archive differs from its manifest.');
  }
  const observed = await runtimeVersions();
  for (const key of ['alpine', 'php', 'python', 'node']) {
    if (manifest.runtime[key] !== observed[key]) throw new Error('This is a same-WSL recovery; an OS runtime version differs: ' + key);
  }
  if (manifest.runtime.nginx !== undefined && manifest.runtime.nginx !== observed.nginx) throw new Error('The existing Nginx version differs.');
  if (!(await lstat(publicArchive)).isFile()) throw new Error('The explicitly authorized external public projection is unavailable.');
  const scriptSha256 = await fileHash(fileURLToPath(import.meta.url));
  const specification = JSON.stringify({
    files: manifest.files, directories: [...directories], runtimePrefixes,
    freshDirectories, databasePath,
  });
  for (const target of targets) {
    const startedAt = new Date().toISOString();
    const restored = spawnSync('python3', ['-c', restoreProgram, archivePath, target], {
      input: specification,
      encoding: 'utf8',
      maxBuffer: 1024 * 1024,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    });
    if (restored.error) throw restored.error;
    if (restored.status !== 0) throw new Error('Recovery failed; keep its incomplete target for evidence.\n' + restored.stderr);
    const databaseResult = JSON.parse(restored.stdout);
    const found = await collectRestored(target);
    if (JSON.stringify(found) !== JSON.stringify([...records.keys()].sort())) throw new Error('Recovered file set differs from the manifest.');
    for (const relative of found) {
      const record = records.get(relative);
      const filename = path.join(target, relative);
      const info = await lstat(filename);
      const digest = record.type === 'symlink'
        ? sha256(Buffer.from(await readlink(filename)))
        : await fileHash(filename);
      if (record.type === 'file' && (!info.isFile() || info.size !== record.bytes)
        || record.type === 'symlink' && !info.isSymbolicLink() || digest !== record.sha256) {
        throw new Error('Restored file bytes or link identity differ: ' + relative);
      }
    }
    const assets = JSON.parse(await readFile(path.join(target, webPrefix, 'public/assets/manifest.json'), 'utf8'));
    for (const value of Object.values(assets)) {
      if (typeof value !== 'string' || !value.startsWith('/assets/') || !records.has(webPrefix + 'public' + value)) {
        throw new Error('A generated asset manifest entry does not resolve in this recovery.');
      }
    }
    if (sha256(await readFile(manifestPath)) !== sha256(manifestBytes) || await fileHash(archivePath) !== manifest.archive.sha256) {
      throw new Error('The readonly backup changed during recovery.');
    }
    const report = {
      scope: 'same-existing-Alpine-WSL-file-and-SQLite-recovery',
      startedAt, completedAt: new Date().toISOString(), target,
      backupManifestSha256: sha256(manifestBytes), archiveSha256: manifest.archive.sha256,
      scriptSha256, filesRestoredAndShaVerified: found.length,
      symlinksVerifiedWithoutDereferencing: manifest.files.filter((file) => file.type === 'symlink').length,
      sqliteIntegrityCheck: databaseResult.sqliteIntegrityCheck,
      databaseSnapshotCaptureMethod: manifest.database.captureMethod,
      databaseTaskOwnedTestData: true, databaseModeRequested: databaseResult.databaseMode,
      backupUnchanged: true, runtimeVersions: observed,
      externalPublicArchive: publicArchive, publicProjectionCopied: false,
      originalMotherArchiveAccessed: false, credentialsEnvCopied: false,
      osReinstalled: false, servicesStarted: false, httpVerified: false,
      acceptanceBoundary: 'File and SQLite recovery passed; actual HTTP startup and player paths still need separate evidence.',
      startScript: path.join(target, webPrefix, 'scripts/local-runtime.sh'),
    };
    await writeFile(path.join(target, 'restoration-report.json'), JSON.stringify(report, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ target, filesVerified: found.length, sqliteIntegrityCheck: 'ok', httpVerified: false, osReinstalled: false }) + '\n');
  }
}

try {
  await main();
} catch (error) {
  process.stderr.write('Local recovery failed: ' + error.message + '\n');
  process.exitCode = 1;
}
