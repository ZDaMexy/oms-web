"""Deterministic signed-APK runtime export, without build tools or application data."""
import gzip
from pathlib import Path
import sys
import tarfile

root, target = map(Path, sys.argv[1:])
assert root.resolve() == root and root.name == 'r2-root'
assert target.parent.is_dir() and not target.exists()

def normalized(entry):
    if not (entry.isfile() or entry.isdir() or entry.issym()):
        raise ValueError('No device or other special file belongs in the PHP runtime')
    entry.uid = entry.gid = entry.mtime = 0
    entry.uname = entry.gname = ''
    return entry

with target.open('xb') as output, gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as compressed:
    with tarfile.open(fileobj=compressed, mode='w|') as archive:
        for path in sorted(root.rglob('*')):
            archive.add(path, arcname=str(path.relative_to(root)), recursive=False, filter=normalized)
