# Licensed under AGPL-3.0-or-later; see LICENCE.
"""Capture this task's local runtime for same-Alpine recovery; never production data."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import sqlite3
import stat
import subprocess
import sys
import tarfile


WEB = Path('/mnt/f/zdamexy-workspace/websites/oms-web')
BACKEND = Path('/mnt/f/zdamexy-workspace/oms-server/oms-backend')
BACKUP = WEB / 'artifacts/local-recovery'
PUBLIC = Path('/mnt/f/oms/artifacts/oms-ir-multisource-20261004/archive/lr2ir-public-v1.db')
LIVE = WEB / '.dev-cache/local-runtime/live.db'
WEB_PREFIX = 'websites/oms-web/'
BACKEND_PREFIX = 'oms-server/oms-backend/'
DB_PATH = WEB_PREFIX + '.dev-cache/local-runtime/live.db'
RUNTIME_DIRECTORIES = (
    'vendor', 'public/assets', '.dev-cache/backend-venv', '.dev-cache/local-runtime/legacy-ir',
)
GENERATED = ('bootstrap/cache/packages.php', 'bootstrap/cache/services.php')


def digest_file(filename):
    result = hashlib.sha256()
    with filename.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def safe_relative(relative):
    if not isinstance(relative, str) or not relative or relative.startswith('/') or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe source path')
    parts = relative.split('/')
    if any(not part or part in ('.', '..', '.git', '.ssh', 'node_modules', 'private-data') for part in parts):
        raise ValueError('A source path is outside the recovery scope')
    if any(ord(char) < 32 or ord(char) == 127 for char in relative):
        raise ValueError('Control characters are excluded from recovery paths')
    if any((part == '.env' or part.startswith('.env.')) and part != '.env.example' for part in parts):
        raise ValueError('Credential environment files are excluded')
    if re.search(r'\.(db|sqlite|sqlite3)(-(wal|shm))?$', relative, re.I) and relative != DB_PATH:
        raise ValueError('Only the task-owned consistent SQLite snapshot may be archived')


def excluded(relative):
    parts = PurePosixPath(relative).parts
    return any(part in ('.git', '.ssh', 'node_modules', 'private-data', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache')
               or (part == '.env' or part.startswith('.env.')) and part != '.env.example' for part in parts) \
        or relative.endswith(('.pyc', '.pyo')) \
        or re.search(r'\.(db|sqlite|sqlite3)(-(wal|shm))?$', relative, re.I) is not None


def git_output(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE).stdout


def sources(root, prefix, pathspec=()):
    # Git enumerates only this repository's visible source names. No private tree is scanned.
    candidates = git_output(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', *pathspec).split(b'\0')
    result = {}
    for raw in candidates:
        if not raw:
            continue
        relative = raw.decode('utf-8')
        if excluded(relative):
            continue
        if root == WEB and (relative.startswith(('.dev-cache/', 'artifacts/', 'vendor/', 'public/assets/', 'bootstrap/cache/'))
                            or relative.startswith('storage/') and not relative.endswith('/.gitignore')):
            continue
        if root == BACKEND and not (relative.startswith('oms_ir/') and relative.endswith(('.py', '.sql'))
                                    or relative in ('pyproject.toml', 'uv.lock')):
            continue
        safe_relative(prefix + relative)
        filename = root / relative
        if not os.path.lexists(filename):
            continue  # A tracked deletion is intentionally absent in the current worktree.
        if filename.parent.resolve() != filename.parent:
            raise ValueError('A selected source parent is symbolic')
        # A repository directory/submodule entry cannot be silently flattened into source.
        if not (filename.is_symlink() or filename.is_file()):
            raise ValueError('A selected source entry is not a regular file or symlink')
        result[prefix + relative] = filename
    return result


def runtime_files(root, relative):
    result = {}
    directory = root / relative
    if not directory.is_dir() or directory.is_symlink() or directory.resolve() != directory:
        raise ValueError('An explicitly required runtime directory is absent or symbolic')

    def visit(current):
        with os.scandir(current) as entries:
            for entry in entries:
                filename = Path(entry.path)
                name = filename.relative_to(root).as_posix()
                if excluded(name):
                    continue
                if entry.is_symlink():
                    result[WEB_PREFIX + name] = filename
                elif entry.is_dir(follow_symlinks=False):
                    visit(filename)
                elif entry.is_file(follow_symlinks=False):
                    result[WEB_PREFIX + name] = filename
                else:
                    raise ValueError('A runtime tree contains an unsupported filesystem object')
    visit(directory)
    return result


def runtime_versions():
    def command(program, arguments, pattern):
        value = subprocess.run([program, *arguments], check=True, capture_output=True, text=True)
        match = re.search(pattern, value.stdout + '\n' + value.stderr)
        if not match:
            raise ValueError('An installed OS runtime version could not be identified')
        return match.group(1)
    return {
        'alpine': Path('/etc/alpine-release').read_text().strip(),
        'php': command('php85', ['--version'], r'PHP (\d+\.\d+\.\d+)'),
        'python': command('python3', ['--version'], r'Python (\d+\.\d+\.\d+)'),
        'node': command('node', ['--version'], r'v(\d+\.\d+\.\d+)'),
        'nginx': command('nginx', ['-v'], r'nginx/(\d+\.\d+\.\d+)'),
        'sqlite': sqlite3.sqlite_version,
        'wslDistro': os.environ.get('WSL_DISTRO_NAME'),
        'publicArchive': str(PUBLIC),
    }


def state_file(filename):
    filename = Path(filename).absolute()
    if not str(filename).startswith('/mnt/f/') or 'private-data' in filename.parts or filename.resolve() != filename:
        raise ValueError('Acceptance state must be an explicit regular F-drive task file')
    if not filename.is_file() or filename.is_symlink():
        raise ValueError('The explicit acceptance state file is unavailable')
    return json.loads(filename.read_text())


def policy_values(connection, state):
    key_id = state['revoked_key']['id']
    post_id = state['hidden_post_id']
    if type(key_id) is not int or key_id <= 0 or type(post_id) is not int or post_id <= 0:
        raise ValueError('WAL witness IDs must identify actual test key/post rows')
    key = connection.execute('SELECT revoked FROM integration_keys WHERE id=?', (key_id,)).fetchone()
    post = connection.execute('SELECT hidden FROM community_posts WHERE id=?', (post_id,)).fetchone()
    return {'revoked_key_id': key_id, 'key_revoked': key[0] if key else None,
            'hidden_post_id': post_id, 'post_hidden': post[0] if post else None}


def consistent_database(destination, acceptance_state, require_wal):
    if LIVE.resolve() != LIVE or not LIVE.is_file() or LIVE.is_symlink():
        raise ValueError('Only the fixed task-owned local test database may be captured')
    destination.parent.mkdir(mode=0o700)
    before = digest_file(LIVE)
    source = sqlite3.connect(LIVE.as_uri() + '?mode=ro', uri=True, timeout=10, isolation_level=None)
    target = sqlite3.connect(destination)
    witness = None
    try:
        source.execute('PRAGMA query_only=ON')
        source.execute('BEGIN')
        version = source.execute('PRAGMA user_version').fetchone()[0]
        if version != 3:
            raise ValueError('Only the current local OMS schema 3 test database is accepted')
        if source.execute('SELECT COUNT(*) FROM users').fetchone()[0] < 2:
            raise ValueError('The local player-path acceptance accounts are absent')
        if acceptance_state is not None:
            for user in acceptance_state['users']:
                actual = source.execute('SELECT username FROM users WHERE id=?', (user['id'],)).fetchone()
                if actual is None or actual[0] != user['username']:
                    raise ValueError('Acceptance account ownership differs from this test database')
        if require_wal:
            if acceptance_state is None:
                raise ValueError('--require-wal-policy-delta needs explicit acceptance state')
            wal = Path(str(LIVE) + '-wal')
            if not wal.is_file() or wal.is_symlink() or wal.stat().st_size <= 32:
                raise ValueError('The required committed WAL evidence is absent')
            live_policy = policy_values(source, acceptance_state)
            main = sqlite3.connect(LIVE.as_uri() + '?mode=ro&immutable=1', uri=True)
            try:
                main_policy = policy_values(main, acceptance_state)
            finally:
                main.close()
            if live_policy['key_revoked'] != 1 or live_policy['post_hidden'] != 1 \
                    or main_policy['key_revoked'] == 1 or main_policy['post_hidden'] == 1:
                raise ValueError('The selected new revocation/hide are not both committed only in WAL')
            witness = {'liveWalView': live_policy, 'mainFileViewIgnoringWal': main_policy,
                       'walBytesObserved': wal.stat().st_size,
                       'sourceCheckpointRequested': False}
        source.backup(target)
        target.execute('PRAGMA journal_mode=DELETE')
        if target.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError('SQLite backup API did not produce an intact standalone snapshot')
        if require_wal and policy_values(target, acceptance_state) != witness['liveWalView']:
            raise ValueError('The SQLite backup did not retain the committed WAL policy values')
    finally:
        target.close()
        source.close()
    destination.chmod(0o600)
    if any(os.path.lexists(str(destination) + suffix) for suffix in ('-wal', '-shm', '-journal')):
        raise ValueError('The backup is not a standalone SQLite file')
    after = digest_file(LIVE)
    if before != after:
        raise ValueError('The live main database changed while capturing; pause the actual writer/checkpointer and retry a fresh round')
    return {'path': DB_PATH, 'captureMethod': 'sqlite-backup-api', 'taskOwnedTestData': True,
            'schemaVersion': version, 'integrityCheck': 'ok', 'sourceMainUnchanged': True,
            'sourceMainSha256': before, 'walPolicyWitness': witness}


def symlink_target(relative, filename):
    target = os.readlink(filename)
    if not target or '\\' in target or any(ord(char) < 32 or ord(char) == 127 for char in target):
        raise ValueError('Invalid symbolic link target')
    if target.startswith('/'):
        if not re.fullmatch(r'websites/oms-web/\.dev-cache/backend-venv/bin/python(?:3(?:\.\d+)?)?', relative) \
                or not re.fullmatch(r'/usr/bin/python3(?:\.\d+)?', target):
            raise ValueError('An absolute link is outside the permitted installed Python runtime')
    else:
        resolved = posixpath.normpath(posixpath.join('/recovery', posixpath.dirname(relative), target))
        if not resolved.startswith('/recovery/'):
            raise ValueError('A symbolic link escapes the recovery root')
    return target


class HashingReader:
    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        value = self.source.read(size)
        self.digest.update(value)
        return value


def create_archive(filename, selected):
    records = []
    with tarfile.open(filename, mode='x:', format=tarfile.PAX_FORMAT, dereference=False) as archive:
        for relative, source in sorted(selected.items()):
            safe_relative(relative)
            info = source.lstat()
            member = tarfile.TarInfo(relative)
            member.mtime = int(info.st_mtime)
            member.mode = stat.S_IMODE(info.st_mode) & 0o777
            member.uid = member.gid = 0
            member.uname = member.gname = ''
            if stat.S_ISLNK(info.st_mode):
                target = symlink_target(relative, source)
                member.type = tarfile.SYMTYPE
                member.linkname = target
                archive.addfile(member)
                records.append({'path': relative, 'type': 'symlink', 'target': target,
                                'sha256': hashlib.sha256(target.encode()).hexdigest(), 'mode': member.mode})
            elif stat.S_ISREG(info.st_mode):
                # Every regular input gets a regular member, including hard-linked source files.
                member.type = tarfile.REGTYPE
                member.size = info.st_size
                with source.open('rb') as stream:
                    hashing = HashingReader(stream)
                    archive.addfile(member, hashing)
                records.append({'path': relative, 'type': 'file', 'bytes': member.size,
                                'sha256': hashing.digest.hexdigest(), 'mode': member.mode})
            else:
                raise ValueError('Unsupported selected source object')
    # A freeze is required; the captured current-WT bytes must still be the exact sources.
    for record in records:
        source = selected[record['path']]
        if record['type'] == 'symlink':
            actual = hashlib.sha256(symlink_target(record['path'], source).encode()).hexdigest()
        else:
            if not source.is_file() or source.is_symlink() or source.stat().st_size != record['bytes']:
                raise ValueError('A source identity changed while capturing')
            actual = digest_file(source)
        if actual != record['sha256']:
            raise ValueError('A source changed while capturing; freeze source writes and use a fresh round')
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', choices=('r1', 'r2'), required=True)
    parser.add_argument('--task-owned-test-data', action='store_true', required=True)
    parser.add_argument('--acceptance-state')
    parser.add_argument('--require-wal-policy-delta', action='store_true')
    args = parser.parse_args()
    if sys.platform != 'linux' or not args.task_owned_test_data:
        raise ValueError('Capture only this task-owned local runtime inside the existing Alpine WSL')
    for directory in (WEB, BACKEND):
        if directory.resolve() != directory or not directory.is_dir():
            raise ValueError('A designated source checkout is unavailable or symbolic')
    if not PUBLIC.is_file() or PUBLIC.is_symlink() or PUBLIC.resolve() != PUBLIC:
        raise ValueError('The approved external public projection is unavailable')
    versions = runtime_versions()
    if versions['node'].split('.')[0] != '24':
        raise ValueError('Node 24 is required by the same-WSL restore helper')
    if sqlite3.sqlite_version_info < (3, 51, 3):
        raise ValueError('SQLite >=3.51.3 is required for the actual OMS WAL fix')
    source_files = sources(WEB, WEB_PREFIX)
    source_files.update(sources(BACKEND, BACKEND_PREFIX, ('oms_ir', 'pyproject.toml', 'uv.lock')))
    allowlist = sorted(source_files)
    selected = dict(source_files)
    for relative in RUNTIME_DIRECTORIES:
        selected.update(runtime_files(WEB, relative))
    for relative in GENERATED:
        source = WEB / relative
        if not source.is_file() or source.is_symlink() or source.resolve() != source:
            raise ValueError('A required generated PHP dependency manifest is missing')
        selected[WEB_PREFIX + relative] = source
    config = dict(line.split(' = ', 1) for line in (WEB / '.dev-cache/backend-venv/pyvenv.cfg').read_text().splitlines()
                  if ' = ' in line)
    if config.get('home') != '/usr/bin' or config.get('include-system-site-packages') != 'false' \
            or config.get('version') != versions['python']:
        raise ValueError('The captured venv is not compatible with the recorded existing OS Python')
    # Absolute activation/pip launcher paths are not used; local-runtime launches the relocated bin/python directly.
    for relative in selected:
        if '/.dev-cache/backend-venv/' in relative and relative.endswith('.pth'):
            for line in selected[relative].read_text().splitlines():
                if '/mnt/' in line:
                    raise ValueError('A venv path file binds this runtime to the original checkout')
    if args.acceptance_state and Path(args.acceptance_state).absolute() in selected.values():
        raise ValueError('Keep acceptance state outside the archived source allowlist')
    if BACKUP.parent.resolve() != BACKUP.parent or not BACKUP.parent.is_dir():
        raise ValueError('The designated artifacts parent must exist directly on F')
    BACKUP.mkdir(mode=0o700, exist_ok=True)
    if BACKUP.resolve() != BACKUP or BACKUP.is_symlink():
        raise ValueError('The fixed recovery directory must not be symbolic')
    BACKUP.chmod(0o700)
    round_root = BACKUP / args.round
    round_root.mkdir(mode=0o700)  # Never replace a previous or incomplete round.
    acceptance_state = state_file(args.acceptance_state) if args.acceptance_state else None
    database = consistent_database(round_root / 'database-backup/live.db', acceptance_state, args.require_wal_policy_delta)
    selected[DB_PATH] = round_root / 'database-backup/live.db'
    archive_path = round_root / 'local-runtime.tar'
    files = create_archive(archive_path, selected)
    manifest = {
        'schemaVersion': 1, 'kind': 'oms-web-local-runtime-recovery',
        'capturedAt': datetime.now(timezone.utc).isoformat(), 'round': args.round,
        'source': {'webHead': git_output(WEB, 'rev-parse', 'HEAD').decode().strip(),
                   'backendHead': git_output(BACKEND, 'rev-parse', 'HEAD').decode().strip(),
                   'currentWorktreeBytes': True, 'sourceNames': 'explicit Git tracked and visible pending source allowlist'},
        'archive': {'file': 'local-runtime.tar', 'bytes': archive_path.stat().st_size, 'sha256': digest_file(archive_path)},
        'sourceAllowlist': allowlist, 'runtime': versions, 'database': database, 'files': files,
        'excluded': ['Git metadata', 'credential env', 'node_modules', 'cache/pyc', 'runtime logs/PIDs/config',
                     'acceptance state/passwords/secrets', 'other databases', 'public projection bytes', 'mother/private data'],
        'sameExistingOSOnly': True,
    }
    manifest_path = round_root / 'source-manifest.json'
    with manifest_path.open('x', encoding='utf-8') as output:
        json.dump(manifest, output, ensure_ascii=False, indent=2)
        output.write('\n')
    for filename in (archive_path, manifest_path):
        filename.chmod(0o400)
    # Publish the latest pair without changing the retained r1/r2 archive bytes.
    # Same-volume hard links are regular input files for restore-local; archive members stay independent files.
    for filename in (archive_path, manifest_path):
        pending = BACKUP / ('.' + filename.name + '.' + args.round + '.pending')
        os.link(filename, pending)
        os.replace(pending, BACKUP / filename.name)
    print(json.dumps({'round': args.round, 'archiveBytes': manifest['archive']['bytes'], 'files': len(files),
                      'sha256': manifest['archive']['sha256'], 'sqliteIntegrityCheck': 'ok',
                      'walPolicyDeltaCaptured': args.require_wal_policy_delta,
                      'publicProjectionCopied': False, 'httpVerified': False}))


if __name__ == '__main__':
    main()
