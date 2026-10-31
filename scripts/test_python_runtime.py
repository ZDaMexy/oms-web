"""Exercise the real installer guard and its subprocess contract offline."""

import ast
import builtins
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from php_runtime import REQUIRED_PACKAGES, inspect_runtime


SCRIPT = Path(__file__).with_name("install-production.py")
SOURCE = SCRIPT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE, filename=str(SCRIPT))
CONSTANTS = {"Path": Path}
for statement in TREE.body:
    if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id.startswith("PYTHON_") for target in statement.targets):
        exec(compile(ast.Module(body=[statement], type_ignores=[]), str(SCRIPT), "exec"), CONSTANTS)
PUBLIC_ROOT = CONSTANTS["PYTHON_RUNTIME"]
GUARD = CONSTANTS["PYTHON_RUNTIME_GUARD"]


def run_guard(code=GUARD, *, version=(3, 12, 16), base=None,
              openssl=(3, 5, 0, 9, 0), openssl_text=None, sqlite=(3, 51, 3), certifi="2026.10.19"):
    modules = {
        "sys": SimpleNamespace(version_info=version, base_prefix=str(PUBLIC_ROOT) if base is None else base,
                               argv=["python", str(PUBLIC_ROOT)]),
        "ssl": SimpleNamespace(OPENSSL_VERSION_INFO=openssl, OPENSSL_VERSION=openssl_text or f"OpenSSL {openssl[0]}.{openssl[1]}.{openssl[3]} 29 Sep 2026"),
        "sqlite3": SimpleNamespace(sqlite_version_info=sqlite),
        "importlib.metadata": SimpleNamespace(metadata=SimpleNamespace(version=lambda name: certifi)),
    }

    def importer(name, *args, **kwargs):
        return modules[name] if name in modules else builtins.__import__(name, *args, **kwargs)

    exec(compile(code, str(SCRIPT), "exec", optimize=2), {"__builtins__": {**vars(builtins), "__import__": importer}})


class PythonRuntimeTests(unittest.TestCase):
    def test_actual_guard_accepts_patched_312_runtime(self):
        for version in ((3, 12, 16), (3, 12, 17)):
            with self.subTest(version=version):
                run_guard(version=version)

    def test_old_or_unreviewed_python_fails_even_with_optimization(self):
        for version in ((3, 12, 15), (3, 11, 16), (3, 13, 0)):
            with self.subTest(version=version), self.assertRaisesRegex(RuntimeError, "Python 3.12.16"):
                run_guard(version=version)

    def test_different_runtime_root_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "shared Python runtime"):
            run_guard(base="/opt/oms-ir/python/old")

    def test_openssl_and_sqlite_floors_are_preserved(self):
        for values, message in (({"openssl": (3, 5, 0, 8, 0)}, "OpenSSL 3.5.9"), ({"sqlite": (3, 51, 2)}, "SQLite 3.51.3")):
            with self.subTest(values=values), self.assertRaisesRegex(RuntimeError, message):
                run_guard(**values)

    def test_real_five_part_openssl_versions_accept_stable_359_and_360(self):
        for openssl in ((3, 5, 0, 9, 0), (3, 6, 0, 0, 0)):
            with self.subTest(openssl=openssl):
                run_guard(openssl=openssl)

    def test_openssl_previews_and_unknown_extra_strings_are_rejected(self):
        for text in ("OpenSSL 3.5.9-dev 29 Sep 2026", "LibreSSL 4.0.0", "OpenSSL 3.5.9 unexpected-vendor"):
            with self.subTest(text=text), self.assertRaisesRegex(RuntimeError, "OpenSSL 3.5.9"):
                run_guard(openssl_text=text)

    def test_venv_guard_checks_python_identity_and_trust_store(self):
        code = CONSTANTS["PYTHON_ENVIRONMENT_GUARD"]
        run_guard(code)
        with self.assertRaisesRegex(RuntimeError, "certifi trust store"):
            run_guard(code, certifi="2026.9.1")
        with self.assertRaisesRegex(RuntimeError, "Python 3.12.16"):
            run_guard(code, version=(3, 12, 15))

    def test_real_sync_call_is_frozen_offline_and_uses_the_public_interpreter(self):
        calls = []
        statements = [statement for statement in TREE.body if isinstance(statement, ast.Expr)
                      and isinstance(statement.value, ast.Call)
                      and isinstance(statement.value.func, ast.Attribute)
                      and isinstance(statement.value.func.value, ast.Name)
                      and statement.value.func.value.id == "subprocess" and statement.value.func.attr == "run"]
        namespace = {**CONSTANTS, "destination": Path("/test-release"), "os": SimpleNamespace(environ={"SYNTHETIC": "fixture"}),
                     "subprocess": SimpleNamespace(run=lambda command, **options: calls.append((command, options)))}
        exec(compile(ast.Module(body=statements, type_ignores=[]), str(SCRIPT), "exec"), namespace)
        self.assertEqual(len(calls), 2)
        command, options = calls[0]
        self.assertEqual(command[0:2], ["/opt/oms-ir/tools/uv-0.13.4/uv", "sync"])
        for flag in ("--offline", "--frozen", "--no-dev", "--no-editable", "--no-managed-python", "--no-python-downloads"):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--python") + 1], str(PUBLIC_ROOT / "bin/python3"))
        self.assertTrue(options["check"])
        self.assertEqual(options["env"], {"SYNTHETIC": "fixture", "UV_CACHE_DIR": "/opt/oms-ir/cache"})
        self.assertEqual(calls[1][0][2:], [CONSTANTS["PYTHON_ENVIRONMENT_GUARD"], str(PUBLIC_ROOT)])
        self.assertNotIn("3.12.15", SOURCE)

    def test_real_installer_rejects_old_python_before_creating_any_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            packages = dict.fromkeys(REQUIRED_PACKAGES, "8.5.12-r0")
            packages.update({"libcurl": "8.23.0-r0", "libssl3": "3.5.9-r0", "libcrypto3": "3.5.9-r0",
                             "c-ares": "1.34.9-r0", "ca-certificates-bundle": "20261020-r0"})
            php = directory / "php.tar.gz"
            with tarfile.open(php, "w:gz") as archive:
                content = {"lib/apk/db/installed": "\n\n".join(f"P:{name}\nV:{version}" for name, version in packages.items()),
                           "etc/alpine-release": "3.24.3\n"}
                for name, text in content.items():
                    entry = tarfile.TarInfo(name)
                    data = text.encode()
                    entry.size = len(data)
                    archive.addfile(entry, io.BytesIO(data))
            file_map = json.dumps({"files": {}, "file_bytes": {}}).encode()
            manifest = {"format": 3, "runtime_kind": "native-osu-web-1", "database_schema_version": 3,
                        "files_manifest": {"path": "runtime-files.json", "bytes": len(file_map), "count": 0,
                                           "sha256": hashlib.sha256(file_map).hexdigest()}, "php_runtime": inspect_runtime(php)}
            package = directory / "release.tar.gz"
            with tarfile.open(package, "w:gz") as archive:
                for name, data in {"release.json": json.dumps(manifest).encode(), "runtime-files.json": file_map}.items():
                    entry = tarfile.TarInfo(name)
                    entry.size = len(data)
                    archive.addfile(entry, io.BytesIO(data))

            def interpreter(command, **options):
                self.assertEqual(command, [str(PUBLIC_ROOT / "bin/python3"), "-c", GUARD, str(PUBLIC_ROOT)])
                run_guard(command[2], version=(3, 12, 15))

            arguments = [str(SCRIPT), "--package", str(package), "--package-sha256", hashlib.sha256(package.read_bytes()).hexdigest(), "--php-runtime", str(php)]
            old_umask = os.umask(0o022)
            try:
                with patch.object(sys, "argv", arguments), patch.object(subprocess, "run", side_effect=interpreter) as probe, patch.object(Path, "mkdir") as mkdir:
                    with self.assertRaisesRegex(RuntimeError, "Python 3.12.16"):
                        runpy.run_path(str(SCRIPT), run_name="__main__")
                    self.assertEqual(probe.call_count, 1)
                    mkdir.assert_not_called()
            finally:
                os.umask(old_umask)


if __name__ == "__main__":
    unittest.main()
