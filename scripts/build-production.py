"""Export committed native OMS sources, locked dependencies and unchanged adapters."""
import argparse
import ast
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

WEB = Path(__file__).resolve().parent.parent
BACKEND = WEB.parent.parent / 'oms-server/oms-backend'
CLIENT = Path('/mnt/f/oms')
LEGACY = Path('/mnt/f/oms/artifacts/oms-deai-20261007/oms-ir-d1f052b93a81-e6fdf914cb04.tar.gz')
LEGACY_SHA = 'b2bc5c490b5f2e6bddb72bb4cdb35ab0b7412507d4ae8b9ac8bc3cd59b78e62b'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def archive_files(repo, *paths):
    with tarfile.open(fileobj=io.BytesIO(git(repo, 'archive', '--format=tar', 'HEAD', '--', *paths))) as archive:
        result = {}
        for entry in archive:
            if entry.isdir():
                continue
            if not entry.isfile() or PurePosixPath(entry.name).is_absolute() or '..' in PurePosixPath(entry.name).parts:
                raise ValueError('Committed source export accepts regular files only')
            result[entry.name] = archive.extractfile(entry).read()
        return result

def tar_bytes(files):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|') as archive:
            for name, data in sorted(files.items()):
                entry = tarfile.TarInfo(name)
                entry.size, entry.mode = len(data), 0o644
                archive.addfile(entry, io.BytesIO(data))
    return out.getvalue()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    heads = {name: git(repo, 'rev-parse', 'HEAD').decode().strip() for name, repo in [('backend', BACKEND), ('website', WEB), ('client', CLIENT)]}
    web_paths = ('app', 'config', 'routes', 'bootstrap', 'resources/views', 'resources/lang', 'resources/oms', 'public', 'deploy', 'scripts', 'artisan', 'composer.json', 'composer.lock', 'LICENCE')
    build_paths = ('resources/js', 'resources/css', 'resources/fonts', 'package.json', 'package-lock.json', 'webpack.config.js', 'tsconfig.json', '.node-version')
    if git(WEB, 'status', '--porcelain', '--untracked-files=no', '--', *web_paths) or git(WEB, 'status', '--porcelain', '--', *build_paths):
        raise ValueError('Commit the reviewed native runtime and publisher before exporting')
    build_receipt = json.loads((WEB / 'artifacts/production/compiled-inputs.json').read_text())
    assert set(build_receipt['inputs']) == set(git(WEB, 'ls-files', '--', *build_paths).decode().splitlines())
    assert set(build_receipt['assets']) == {path.relative_to(WEB).as_posix() for path in (WEB / 'public/assets').rglob('*') if path.is_file()}
    for name, checksum in build_receipt['inputs'].items():
        assert hashlib.sha256(git(WEB, 'show', 'HEAD:' + name)).hexdigest() == checksum, name
    for name, checksum in build_receipt['assets'].items():
        assert hashlib.sha256((WEB / name).read_bytes()).hexdigest() == checksum, name
    tree = ast.parse(git(BACKEND, 'show', 'HEAD:scripts/build_release.py'))
    backend_paths = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BACKEND_FILES' for t in node.targets))
    if git(BACKEND, 'status', '--porcelain', '--', *backend_paths):
        raise ValueError('Uncommitted backend runtime changes cannot be published')
    files = {'backend/' + name: data for name, data in archive_files(BACKEND, *backend_paths).items()}
    files.update({'web/' + name: data for name, data in archive_files(WEB, *web_paths).items() if not name.startswith(('bootstrap/cache/', 'public/assets/'))})
    for prefix in ('vendor', 'public/assets'):
        root = WEB / prefix
        for path in sorted(root.rglob('*')):
            if path.is_symlink():
                # Composer executable proxies are build-time tools, not runtime.
                if prefix == 'vendor' and path.relative_to(root).parts[0] == 'bin':
                    continue
                raise ValueError('Unexpected dependency link')
            if path.is_file():
                name = path.relative_to(WEB).as_posix()
                if name.startswith('vendor/bin/'):
                    continue
                files['web/' + name] = path.read_bytes()
    assert hashlib.file_digest(LEGACY.open('rb'), 'sha256').hexdigest() == LEGACY_SHA
    with tarfile.open(LEGACY) as old:
        old_manifest = json.load(old.extractfile('release.json'))
        for name, checksum in old_manifest['files'].items():
            if name.startswith('web/ir/adapters/'):
                data = old.extractfile(name).read()
                assert hashlib.sha256(data).hexdigest() == checksum
                files[name] = data
    versions = json.loads(files['web/ir/adapters/versions.json'])
    assert all(row['backend_commit'] == old_manifest['backend_commit'] for row in versions['items'])
    # Corresponding source has all committed web inputs, locks, licences and
    # exact backend inputs. Never include developer caches, env files or data.
    sources = {'web/' + name: data for name, data in archive_files(WEB).items()}
    sources.update({name: data for name, data in files.items() if name.startswith('backend/')})
    sources['source-manifest.json'] = json.dumps({'backend_commit': heads['backend'], 'website_commit': heads['website'], 'adapter_backend_commit': old_manifest['backend_commit'], 'files': {name: hashlib.sha256(data).hexdigest() for name, data in sources.items()}}, indent=2).encode()
    files['web/public/oms-web-source.tar.gz'] = tar_bytes(sources)
    runtime = WEB / 'artifacts/production/php85-alpine3242.tar.gz'
    file_map = json.dumps({'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}, 'file_bytes': {name: len(data) for name, data in sorted(files.items())}}, separators=(',', ':')).encode()
    manifest = {
        'format': 3, 'runtime_kind': 'native-osu-web-1', 'database_schema_version': 3,
        'release_id': heads['backend'][:12] + '-' + heads['website'][:12],
        **{name + '_commit': commit for name, commit in heads.items()},
        'public_archive': old_manifest['public_archive'],
        'adapter_source': {'backend_commit': old_manifest['backend_commit'], 'original_release': old_manifest['release_id'], 'original_package_sha256': LEGACY_SHA, 'artifacts_rebuilt': False},
        'php_runtime': {'sha256': hashlib.file_digest(runtime.open('rb'), 'sha256').hexdigest(), 'bytes': runtime.stat().st_size, 'php': '8.5.11', 'alpine_base': '3.24.2', 'apk_packages': (WEB / 'artifacts/production/php-packages.txt').read_text().splitlines()},
        'compiled_input_sha256': hashlib.sha256((WEB / 'artifacts/production/compiled-inputs.json').read_bytes()).hexdigest(),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'files_manifest': {'path': 'runtime-files.json', 'sha256': hashlib.sha256(file_map).hexdigest(), 'bytes': len(file_map), 'count': len(files)},
    }
    files['runtime-files.json'] = file_map
    files['release.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode()
    assert len(files['release.json']) < 1024 * 1024, 'The fixed maintenance helper caps release metadata at 1 MiB'
    args.output.mkdir(parents=True, exist_ok=False)
    package = args.output / ('oms-native-' + manifest['release_id'] + '.tar.gz')
    package.write_bytes(tar_bytes(files))
    (args.output / 'release.json').write_bytes(files['release.json'])
    receipt = {'release_id': manifest['release_id'], 'package': package.name, 'bytes': package.stat().st_size, 'sha256': hashlib.file_digest(package.open('rb'), 'sha256').hexdigest(), 'runtime_file_count': len(files) - 1, 'adapter_source': manifest['adapter_source']}
    (args.output / 'package-receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
