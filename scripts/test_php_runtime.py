import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

from php_runtime import REQUIRED_PACKAGES, inspect_installed_runtime, inspect_runtime


class PhpRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, version='8.5.12-r0', overrides=None):
        packages = dict.fromkeys(REQUIRED_PACKAGES, version)
        packages.update({'libcurl': '8.23.0-r0', 'libssl3': '3.5.9-r0',
                         'libcrypto3': '3.5.9-r0', 'c-ares': '1.34.9-r0',
                         'ca-certificates-bundle': '20261020-r0'})
        packages.update(overrides or {})
        installed = '\n\n'.join(f'P:{name}\nV:{version}' for name, version in sorted(packages.items()) if version)
        path = self.root / 'runtime.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, value in {'lib/apk/db/installed': installed, 'etc/alpine-release': '3.24.3\n'}.items():
                data = value.encode()
                entry = tarfile.TarInfo(name)
                entry.size = len(data)
                archive.addfile(entry, io.BytesIO(data))
        return path

    def test_fixed_archive_and_declared_metadata_agree(self):
        path = self.archive()
        actual = inspect_runtime(path)
        self.assertEqual(actual['php'], '8.5.12')
        self.assertEqual(inspect_runtime(path, actual), actual)

    def test_vulnerable_archive_rejected(self):
        with self.assertRaisesRegex(ValueError, '8.5.12 or newer'):
            inspect_runtime(self.archive('8.5.11-r0'))

    def test_only_common_package_updated_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'same package version'):
            inspect_runtime(self.archive('8.5.11-r0', {'php85-common': '8.5.12-r0'}))

    def test_missing_fpm_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing required'):
            inspect_runtime(self.archive(overrides={'php85-fpm': None}))

    def test_fixed_php_with_old_curl_rejected(self):
        with self.assertRaisesRegex(ValueError, 'libcurl 8.23.0'):
            inspect_runtime(self.archive(overrides={'libcurl': '8.22.0-r0'}))

    def test_old_or_mismatched_openssl_rejected(self):
        with self.assertRaisesRegex(ValueError, 'libssl3 3.5.9'):
            inspect_runtime(self.archive(overrides={'libssl3': '3.5.8-r0'}))

    def test_missing_dns_fix_rejected(self):
        with self.assertRaisesRegex(ValueError, 'c-ares 1.34.9'):
            inspect_runtime(self.archive(overrides={'c-ares': None}))

    def test_old_ca_bundle_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CA bundle'):
            inspect_runtime(self.archive(overrides={'ca-certificates-bundle': '20260319-r0'}))

    def test_incorrect_declared_version_rejected(self):
        path = self.archive()
        actual = inspect_runtime(path)
        actual['php'] = '8.5.11'
        with self.assertRaisesRegex(ValueError, 'does not match'):
            inspect_runtime(path, actual)

    def test_existing_vulnerable_directory_rejected(self):
        root = self.root / 'installed'
        (root / 'lib/apk/db').mkdir(parents=True)
        (root / 'etc').mkdir()
        (root / 'etc/alpine-release').write_text('3.24.2\n')
        (root / 'lib/apk/db/installed').write_text('\n\n'.join(f'P:{name}\nV:8.5.11-r0' for name in sorted(REQUIRED_PACKAGES)))
        with self.assertRaisesRegex(ValueError, '8.5.12 or newer'):
            inspect_installed_runtime(root)

    def test_installer_rejects_old_runtime_before_creating_directories(self):
        runtime = self.archive('8.5.11-r0')
        file_map = json.dumps({'files': {}, 'file_bytes': {}}).encode()
        import hashlib
        manifest = {'format': 3, 'runtime_kind': 'native-osu-web-1', 'database_schema_version': 3,
                    'files_manifest': {'path': 'runtime-files.json', 'bytes': len(file_map), 'count': 0,
                                       'sha256': hashlib.sha256(file_map).hexdigest()},
                    'php_runtime': {'php': '8.5.12'}}
        package = self.root / 'release.tar.gz'
        with tarfile.open(package, 'w:gz') as archive:
            for name, data in {'release.json': json.dumps(manifest).encode(), 'runtime-files.json': file_map}.items():
                entry = tarfile.TarInfo(name)
                entry.size = len(data)
                archive.addfile(entry, io.BytesIO(data))
        with package.open('rb') as stream:
            checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('install-production.py')),
                                 '--package', str(package), '--package-sha256', checksum,
                                 '--php-runtime', str(runtime)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PHP 8.5.12 or newer', result.stderr)
        self.assertNotIn('PermissionError', result.stderr)


if __name__ == '__main__':
    unittest.main()
