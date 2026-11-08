"""Compare preferred Python source with embedded worker code, without executing it.

Use the build's CPython 3.12 interpreter and installed PyInstaller reader.
Only co_filename is normalized, recursively; bytecode, constants, line tables,
names, flags and other code attributes must compare equal. This proves Python
code correspondence, not native/static-library source completeness.
"""
import argparse
import hashlib
import json
import marshal
from pathlib import Path
import sys
import types
import zipfile

from PyInstaller.archive.readers import CArchiveReader


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalized(code):
    return code.replace(co_filename='<source>', co_consts=tuple(
        normalized(c) if isinstance(c, types.CodeType) else c for c in code.co_consts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    assert sys.version_info[:3] == (3, 12, 10), 'Use candidate CPython 3.12.10'
    root = Path(__file__).resolve().parents[1]
    inv = json.loads((root / 'packaging/compliance-inventory.json').read_text(encoding='utf-8'))
    exe = root / inv['candidate']['worker'] / 'translation-engine-worker.exe'
    assert digest(exe.read_bytes()) == inv['candidate']['exe_sha256']
    pkg = CArchiveReader(str(exe))
    pyz = pkg.open_embedded_archive('PYZ.pyz')
    records = []

    def compare(component, name, source, origin, frozen):
        rebuilt = compile(source, frozen.co_filename, 'exec', dont_inherit=True, optimize=0)
        records.append(dict(component=component, module=name, source=origin,
                            source_sha256=digest(source),
                            frozen_code_sha256=digest(marshal.dumps(frozen)),
                            matches=normalized(rebuilt) == normalized(frozen)))

    for c in inv['components']:
        identity = c['source_identity']
        if not c.get('pyz_roots') or not identity.get('wheel'):
            continue
        wheel = root / identity['wheel']
        assert digest(wheel.read_bytes()) == identity['wheel_sha256']
        with zipfile.ZipFile(wheel) as archive:
            for name, entry in sorted(pyz.toc.items()):
                if name.split('.')[0] not in c['pyz_roots']:
                    continue
                member = name.replace('.', '/') + ('/__init__.py' if entry[0] == 1 else '.py')
                assert member in archive.namelist(), f'Missing preferred source: {name}'
                compare(c['id'], name, archive.read(member),
                        dict(path=identity['wheel'], archive_sha256=identity['wheel_sha256'], member=member),
                        pyz.extract(name))
    for name, entry in sorted(pyz.toc.items()):
        if name.split('.')[0] == 'translation_engine':
            file = 'src/' + name.replace('.', '/') + ('/__init__.py' if entry[0] == 1 else '.py')
            compare('translation-engine', name, (root / file).read_bytes(), dict(path=file), pyz.extract(name))
    for name in sorted(pkg.toc):
        if name.startswith(('pyimod', 'pyiboot', 'pyi_rth')):
            directory = 'hooks/rthooks' if name.startswith('pyi_rth') else 'loader'
            file = f'.venv/Lib/site-packages/PyInstaller/{directory}/{name}.py'
            compare('pyinstaller', name, (root / file).read_bytes(), dict(path=file), marshal.loads(pkg.extract(name)))
        elif name == 'worker_entry':
            file = 'packaging/worker_entry.py'
            compare('translation-engine', name, (root / file).read_bytes(), dict(path=file), marshal.loads(pkg.extract(name)))
    report = dict(schema_version=1, exe_sha256=digest(exe.read_bytes()), python=sys.version,
                  method='compile optimize=0; recursive co_filename normalization; code-object equality',
                  passed=all(r['matches'] for r in records), records=records,
                  limitations=['Native/static source correspondence is not established by Python code comparison.'])
    destination = Path(args.report)
    with destination.open('x', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], modules=len(records),
                          mismatches=[r['module'] for r in records if not r['matches']])))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
