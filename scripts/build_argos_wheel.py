"""Build/verify the unmodified approved Argos source wheel; never select a branch."""
import argparse
from datetime import datetime
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'packaging/argos-upstream.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild', action='store_true')
    parser.add_argument('--establish-hash', action='store_true', help='Initial approved maintainer operation only')
    args = parser.parse_args()
    spec = json.loads(MANIFEST.read_text())
    output = ROOT / 'downloads/wheels' / spec['wheel_filename']
    if output.exists() and not args.rebuild:
        if not spec['wheel_sha256'] or digest(output) != spec['wheel_sha256']:
            raise SystemExit('Cached Argos wheel differs from reviewed identity')
        print('Verified ' + str(output))
        return
    if args.establish_hash and spec['wheel_sha256']:
        raise SystemExit('Wheel hash already established; do not silently replace it')
    for name, version in spec['build_tools'].items():
        if metadata.version(name) != version:
            raise SystemExit(f'Build requires {name}=={version}')
    archive = ROOT / 'downloads' / ('argos-' + spec['commit'] + '.zip')
    archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        captured = ROOT / 'runtime/optional-stanza-investigation/upstream.zip'
        if captured.exists() and digest(captured) == spec['source_sha256']:
            shutil.copyfile(captured, archive)
        else:
            with urllib.request.urlopen(spec['source_url'], timeout=60) as response:
                with tempfile.NamedTemporaryFile(dir=archive.parent, delete=False) as stream:
                    temporary_download = Path(stream.name)
                    try:
                        shutil.copyfileobj(response, stream)
                    except BaseException:
                        temporary_download.unlink(missing_ok=True)
                        raise
            if digest(temporary_download) != spec['source_sha256']:
                temporary_download.unlink()
                raise SystemExit('Argos source digest mismatch')
            temporary_download.replace(archive)
    if digest(archive) != spec['source_sha256']:
        raise SystemExit('Argos source digest mismatch')
    runtime = ROOT / 'runtime'
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='argos-wheel-', dir=runtime) as temporary:
        work = Path(temporary).resolve()
        if not work.is_relative_to(runtime.resolve()):
            raise SystemExit('Temporary source workspace escaped runtime root')
        with zipfile.ZipFile(archive) as source:
            entries = source.infolist()
            if len(entries) > 10000 or sum(e.file_size for e in entries) > 64 * 1024**2:
                raise SystemExit('Source archive exceeds bounds')
            for entry in entries:
                path = PurePosixPath(entry.filename)
                if path.is_absolute() or '..' in path.parts or ':' in entry.filename or '\\' in entry.filename:
                    raise SystemExit('Unsafe source archive path')
            source.extractall(work)
        source_root = work / ('argos-translate-' + spec['commit'])
        env = dict(os.environ, SOURCE_DATE_EPOCH=str(int(datetime.fromisoformat(spec['source_date']).timestamp())),
                   PYTHONHASHSEED='0')
        subprocess.run([sys.executable, '-m', 'pip', 'wheel', '--no-index', '--no-deps',
                        '--no-build-isolation', '--wheel-dir', str(work / 'wheels'), str(source_root)],
                       check=True, env=env)
        wheel = work / 'wheels' / spec['wheel_filename']
        observed = digest(wheel)
        if args.establish_hash:
            spec['wheel_sha256'] = observed
            MANIFEST.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
        elif observed != spec['wheel_sha256']:
            raise SystemExit('Rebuilt wheel differs from reviewed hash; refusing promotion')
        output.parent.mkdir(exist_ok=True)
        shutil.copyfile(wheel, output)
        print(json.dumps({'wheel': str(output), 'sha256': observed, 'source_modified': False}))


if __name__ == '__main__':
    main()
