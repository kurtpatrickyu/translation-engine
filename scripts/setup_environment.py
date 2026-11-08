"""Hash-verified installation from a controlled local wheelhouse."""
import importlib.metadata as metadata
import re
from pathlib import Path
import subprocess
import sys
import tempfile
from verify_dependency_locks import verify

ROOT = Path(__file__).resolve().parents[1]


def main():
    if Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        raise SystemExit('Use the project .venv interpreter')
    verify(ROOT)
    (ROOT / 'runtime').mkdir(exist_ok=True)
    for name in ('stanza', 'torch'):
        try:
            metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
        raise SystemExit('Old dependency graph detected; preserve it and create a fresh .venv before setup')
    def pip(*args):
        subprocess.run([sys.executable, '-m', 'pip', '--disable-pip-version-check', *args], check=True)
    pip('install', '--require-hashes', '--only-binary=:all:', '-r', str(ROOT / 'packaging/argos-build.lock'))
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_argos_wheel.py')], check=True)
    wheelhouse = ROOT / 'downloads/wheels'
    # Do not let an index's same-version Argos artifact compete with our reviewed wheel.
    # Acquire all other pinned wheels, then install the complete graph without an index.
    lock = (ROOT / 'requirements-dev.lock').read_text()
    other = re.sub(r'(?m)^argostranslate==[^\n]+(?:\n[ \t]+[^\n]*)*', '', lock)
    if other == lock:
        raise SystemExit('Expected the reviewed version/hash Argos lock entry')
    with tempfile.TemporaryDirectory(dir=ROOT / 'runtime', prefix='setup-') as directory:
        requirements = Path(directory) / 'other.lock'
        requirements.write_text(other, encoding='utf-8')
        pip('download', '--require-hashes', '--only-binary=:all:', '--dest', str(wheelhouse), '-r', str(requirements))
    pip('install', '--no-index', '--find-links', str(wheelhouse), '--require-hashes', '--only-binary=:all:',
        '-r', str(ROOT / 'requirements-dev.lock'))
    pip('install', '--no-deps', '--no-build-isolation', '-e', str(ROOT))
    pip('check')
    for name in ('stanza', 'torch'):
        try:
            metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        raise SystemExit('Unexpected dependency: ' + name)


if __name__ == '__main__':
    main()
