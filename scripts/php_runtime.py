"""Read the shipped APK metadata; never label an older archive as a patched PHP."""
import hashlib
from pathlib import Path
import re
import tarfile

RUNTIME_ARCHIVE = 'php85-8.5.12-alpine3242.tar.gz'
REQUIRED_PACKAGES = {
    'php85', 'php85-common', 'php85-fpm', 'php85-intl', 'php85-mbstring',
    'php85-ctype', 'php85-dom', 'php85-fileinfo', 'php85-iconv', 'php85-openssl',
    'php85-session', 'php85-tokenizer', 'php85-curl', 'php85-pdo', 'php85-phar',
    'php85-xml', 'php85-xmlwriter', 'php85-xmlreader', 'php85-simplexml',
}


def package_metadata(installed, alpine):
    packages = {}
    for block in installed.strip().split('\n\n'):
        fields = dict(line.split(':', 1) for line in block.splitlines() if line.startswith(('P:', 'V:')))
        name, version = fields['P'], fields['V']
        if name in packages:
            raise ValueError('Duplicate installed APK package: ' + name)
        packages[name] = version
    if not REQUIRED_PACKAGES <= packages.keys():
        raise ValueError('PHP runtime is missing required CLI, FPM or extensions')
    versions = {version for name, version in packages.items() if name.startswith('php85')}
    if len(versions) != 1:
        raise ValueError('PHP CLI, FPM and extensions must have the same package version')
    version = versions.pop()
    match = re.fullmatch(r'8\.5\.(\d+)-r\d+', version)
    if match is None or int(match[1]) < 12:
        raise ValueError('PHP 8.5.12 or newer is required by the October 2026 security fixes')
    if not alpine.startswith('3.24.'):
        raise ValueError('This publisher requires the reviewed Alpine 3.24 runtime')
    return {'php': version.split('-r')[0], 'alpine_base': alpine,
            'apk_packages': sorted(f'{name}-{version}' for name, version in packages.items())}


def inspect_installed_runtime(root):
    root = Path(root)
    return package_metadata((root / 'lib/apk/db/installed').read_text(encoding='utf-8'),
                            (root / 'etc/alpine-release').read_text(encoding='utf-8').strip())


def inspect_runtime(path, declared=None):
    path = Path(path)
    with tarfile.open(path) as archive:
        def text(name, limit):
            matches = [entry for entry in archive.getmembers() if entry.name == name]
            if len(matches) != 1 or not matches[0].isfile() or matches[0].size > limit:
                raise ValueError('Missing, duplicate or invalid PHP runtime metadata: ' + name)
            return archive.extractfile(matches[0]).read().decode('utf-8')

        metadata = package_metadata(text('lib/apk/db/installed', 2 * 1024 * 1024), text('etc/alpine-release', 64).strip())
    with path.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    actual = {'sha256': checksum, 'bytes': path.stat().st_size, **metadata}
    if declared is not None and declared != actual:
        raise ValueError('The release PHP metadata does not match the actual runtime archive')
    return actual
