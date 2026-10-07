"""Install a verified immutable native release; never activate it or touch live data."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('--package', type=Path, required=True)
parser.add_argument('--package-sha256', required=True)
parser.add_argument('--php-runtime', type=Path, required=True)
args = parser.parse_args()
assert hashlib.file_digest(args.package.open('rb'), 'sha256').hexdigest() == args.package_sha256
with tarfile.open(args.package) as archive:
    entries = archive.getmembers()
    if len({e.name for e in entries}) != len(entries):
        raise ValueError('Duplicate package path')
    for entry in entries:
        path = PurePosixPath(entry.name)
        if not entry.isfile() or path.is_absolute() or '..' in path.parts or entry.size > 64 * 1024 * 1024:
            raise ValueError('No links, special files or unbounded files in a release')
    manifest = json.load(archive.extractfile('release.json'))
    assert manifest['format'] == 3 and manifest['runtime_kind'] == 'native-osu-web-1' and manifest['database_schema_version'] == 3
    rid = manifest['release_id']
    assert re.fullmatch(r'[0-9a-f]{12}-[0-9a-f]{12}', rid)
    for key in ('backend_commit', 'website_commit', 'client_commit'):
        assert re.fullmatch(r'[0-9a-f]{40}', manifest[key])
    assert rid == manifest['backend_commit'][:12] + '-' + manifest['website_commit'][:12]
    assert {e.name for e in entries} == {'release.json', *manifest['files']}
    for name, checksum in manifest['files'].items():
        allowed = name.startswith(('backend/oms_ir/', 'backend/deploy/', 'backend/scripts/', 'web/app/', 'web/config/', 'web/routes/', 'web/bootstrap/', 'web/resources/views/', 'web/resources/lang/', 'web/resources/oms/', 'web/deploy/', 'web/scripts/', 'web/vendor/', 'web/public/assets/', 'web/public/images/', 'web/ir/adapters/')) or name in {
            'backend/pyproject.toml', 'backend/uv.lock', 'backend/adapters/sdk-manifest.json',
            'web/artisan', 'web/composer.json', 'web/composer.lock', 'web/LICENCE', 'web/THIRD_PARTY_NOTICES.md',
            'web/public/index.php', 'web/public/favicon.ico', 'web/public/site.webmanifest', 'web/public/oms-web-source.tar.gz',
        }
        assert allowed and '/.env' not in name and '/node_modules/' not in name and '/.dev-cache/' not in name and not name.startswith('web/bootstrap/cache/')
        data = archive.extractfile(name).read()
        assert len(data) == manifest['file_bytes'][name] and hashlib.sha256(data).hexdigest() == checksum
    versions = json.load(archive.extractfile('web/ir/adapters/versions.json'))
    assert not manifest['adapter_source']['artifacts_rebuilt']
    assert all(item['backend_commit'] == manifest['adapter_source']['backend_commit'] for item in versions['items'])
    public = manifest['public_archive']
    projection = Path('/opt/oms-ir/archives') / (public['projection_version'] + '.db')
    assert not projection.is_symlink() and projection.stat().st_size == public['bytes']
    assert hashlib.file_digest(projection.open('rb'), 'sha256').hexdigest() == public['sha256']
    php = manifest['php_runtime']
    assert args.php_runtime.stat().st_size == php['bytes']
    assert hashlib.file_digest(args.php_runtime.open('rb'), 'sha256').hexdigest() == php['sha256']
    runtime = Path('/opt/oms-web/runtime') / ('php85-' + php['sha256'][:12])
    if not runtime.exists():
        runtime.mkdir(parents=True)
        with tarfile.open(args.php_runtime) as php_archive:
            # APK base contains only regular files, directories and symlinks.
            # Absolute OS symlinks belong inside this dedicated chroot. No
            # extraction follows a previously-created symlink.
            members = php_archive.getmembers()
            for entry in members:
                p = PurePosixPath(entry.name)
                assert not p.is_absolute() and '..' not in p.parts and (entry.isfile() or entry.isdir() or entry.issym())
                assert not entry.islnk()
                if entry.issym():
                    continue
                target = runtime / entry.name
                assert not any(parent.is_symlink() for parent in target.parents if parent != runtime.parent)
            for entry in members:
                if entry.isdir():
                    (runtime / entry.name).mkdir(parents=True, exist_ok=True)
                elif entry.isfile():
                    target = runtime / entry.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(php_archive.extractfile(entry).read())
                    target.chmod(entry.mode & 0o755)
            for entry in members:
                if entry.issym():
                    target = runtime / entry.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(entry.linkname)
        (runtime / '.package-sha256').write_text(php['sha256'] + '\n')
    else:
        assert (runtime / '.package-sha256').read_text().strip() == php['sha256']
    destination = Path('/opt/oms-ir/releases') / rid
    destination.mkdir()
    for entry in entries:
        target = destination / entry.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(entry).read())
        target.chmod(0o644)
    (destination / 'archive.db').symlink_to(projection)
    for path in ('bootstrap/cache', 'storage/framework/views', 'storage/framework/cache', 'storage/logs'):
        (destination / 'web' / path).mkdir(parents=True, exist_ok=True)
subprocess.run(['/opt/oms-ir/tools/uv-0.12.11/uv', 'sync', '--project', str(destination / 'backend'), '--offline', '--frozen', '--no-dev', '--no-editable', '--managed-python', '--python', '3.12.14'], check=True,
    env={**__import__('os').environ, 'UV_CACHE_DIR': '/opt/oms-ir/cache', 'UV_PYTHON_INSTALL_DIR': '/opt/oms-ir/python'})
subprocess.run([str(destination / 'backend/.venv/bin/python'), '-c', 'import sqlite3; assert sqlite3.sqlite_version_info>=(3,51,3),sqlite3.sqlite_version'], check=True)
(destination / '.ready').touch()
print(json.dumps({'release': str(destination), 'runtime': str(runtime), 'production_activated': False}))
