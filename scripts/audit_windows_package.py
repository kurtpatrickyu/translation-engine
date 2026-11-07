"""Static native/import and ZIP integrity audit of an existing Windows onedir."""

import argparse
import ast
import ctypes
from ctypes import wintypes
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import zipfile

import pefile


# Reviewed desktop OS import names, not a blanket System32 or *.dll exemption.
# Presence/export compatibility on each target OS remains a clean-machine gate.
WINDOWS_DLLS = set('user32 kernel32 advapi32 ws2_32 bcrypt version ole32 oleaut32 '
                   'iphlpapi rpcrt4 crypt32 propsys wintrust imagehlp dbghelp setupapi dxgi shell32'.split())
EXCLUDED = {'torch', 'stanza', 'spacy', 'thinc'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def windows_contract(name):
    return name.lower().startswith(('api-ms-win-', 'ext-ms-win-'))


def dependency_kind(name, bundled_names):
    name = name.lower()
    if name in bundled_names:
        return 'bundled'
    if windows_contract(name):
        return 'windows_api_contract'
    if name.removesuffix('.dll') in WINDOWS_DLLS:
        return 'windows_desktop_dll'
    return 'unresolved'


def module_scope(path, bundle, windows):
    path, bundle, windows = path.resolve(), bundle.resolve(), windows.resolve()
    if path.is_relative_to(bundle):
        return 'bundle'
    if path.is_relative_to(windows / 'System32'):
        return 'windows_system32'
    components = {'gdiplus.dll': 'amd64_microsoft.windows.gdiplus_6595b64144ccf1df_',
                  'comctl32.dll': 'amd64_microsoft.windows.common-controls_6595b64144ccf1df_'}
    if (path.parent.parent == windows / 'WinSxS' and path.name.lower() in components
            and path.parent.name.lower().startswith(components[path.name.lower()])):
        return 'windows_side_by_side_component'
    return 'external_host'


def loaded_modules(pid, bundle):
    """Snapshot one live x64 child; never load its DLLs into the auditor."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi.EnumProcessModulesEx.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.HMODULE),
                                         wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.DWORD]
    psapi.GetModuleFileNameExW.argtypes = [wintypes.HANDLE, wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        modules = (wintypes.HMODULE * 2048)()
        needed = wintypes.DWORD()
        if not psapi.EnumProcessModulesEx(handle, modules, ctypes.sizeof(modules), ctypes.byref(needed), 3):
            raise ctypes.WinError(ctypes.get_last_error())
        if needed.value > ctypes.sizeof(modules):
            raise RuntimeError('Module snapshot exceeds audit bound')
        result = []
        for module in modules[:needed.value // ctypes.sizeof(wintypes.HMODULE)]:
            buffer = ctypes.create_unicode_buffer(32768)
            if not psapi.GetModuleFileNameExW(handle, module, buffer, len(buffer)):
                raise ctypes.WinError(ctypes.get_last_error())
            path = Path(buffer.value).resolve()
            scope = module_scope(path, bundle, Path(os.environ['SystemRoot']))
            result.append(dict(path=str(path), scope=scope, sha256=digest(path)))
        return result
    finally:
        kernel.CloseHandle(handle)


def source_records(value):
    if isinstance(value, (tuple, list)):
        if len(value) == 3 and all(isinstance(item, str) for item in value) and value[2] in ('BINARY', 'EXTENSION'):
            yield value
        else:
            for item in value:
                yield from source_records(item)


def symbol_name(pe, offset):
    # pefile defaults truncate decorated C++ names at 512 bytes. Compare the
    # full names (bounded to 4096) rather than accepting matching prefixes.
    name = pe.get_data(pe.get_rva_from_offset(offset), 4097).split(b'\0', 1)[0]
    if len(name) > 4096:
        raise ValueError('Native symbol name exceeds audit bound')
    return name


def audit(build):
    result = json.loads((build / 'build-result.json').read_text(encoding='utf-8'))
    if not result['passed']:
        raise ValueError('Select a successful diagnostic build')
    executable = Path(result['executable']).resolve()
    root = executable.parent
    validation = json.loads((build / 'frozen-unicode-all.json').read_text(encoding='utf-8'))
    archive = build / 'frozen-unicode-all.worker.zip'
    errors = []
    files = {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file()}
    hashes = {name: digest(path) for name, path in files.items()}
    if not validation['passed'] or hashes[executable.name] != validation['worker_exe_sha256']:
        errors.append('Executable identity differs from successful validation')
    if digest(archive) != validation['worker_zip_sha256']:
        errors.append('ZIP identity differs from successful validation')
    with zipfile.ZipFile(archive) as zipped:
        entries = [entry for entry in zipped.infolist() if not entry.is_dir()]
        expected = {'translation-engine-worker/' + name for name in files}
        if len(entries) != len(expected) or {e.filename for e in entries} != expected:
            errors.append('ZIP/file inventory mismatch or duplicate entries')
        else:
            for entry in entries:
                name = entry.filename.removeprefix('translation-engine-worker/')
                with zipped.open(entry) as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != hashes[name]:
                        errors.append('ZIP/extracted file mismatch: ' + name)
    sources = {dest.lower(): src for dest, src, _ in source_records(ast.literal_eval(
        (build / 'work/worker/Analysis-00.toc').read_text(encoding='utf-8')))}
    binaries, exports = [], {}
    for name, path in files.items():
        if path.suffix.lower() not in ('.exe', '.dll', '.pyd'):
            continue
        # CTranslate2 has 13,884 named exports; pefile's default 8192 cap
        # truncates legitimate exports and produces false missing-symbol errors.
        with pefile.PE(str(path), fast_load=True, max_symbol_exports=65536) as pe:
            pe.parse_data_directories(directories=[0, 1, 13, 2])
            version = pe.VS_FIXEDFILEINFO[0] if getattr(pe, 'VS_FIXEDFILEINFO', None) else None
            symbols = getattr(getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None), 'symbols', [])
            exports[path.name.lower()] = ({symbol.ordinal for symbol in symbols}
                | {symbol_name(pe, symbol.name_offset) for symbol in symbols if symbol.name})
            imports = []
            for field, delayed in [('DIRECTORY_ENTRY_IMPORT', False), ('DIRECTORY_ENTRY_DELAY_IMPORT', True)]:
                for entry in getattr(pe, field, []):
                    imports.append(dict(dll=entry.dll.decode('ascii'), delay=delayed,
                                        symbols=[symbol_name(pe, i.name_offset).decode('ascii') if not i.import_by_ordinal else i.ordinal
                                                 for i in entry.imports]))
            original = sources.get(name.removeprefix('_internal/').replace('/', '\\').lower())
            binaries.append(dict(path=name, sha256=hashes[name], bytes=path.stat().st_size,
                                 machine=hex(pe.FILE_HEADER.Machine), imports=imports,
                                 file_version=('.'.join(map(str, [version.FileVersionMS >> 16, version.FileVersionMS & 65535,
                                                                  version.FileVersionLS >> 16, version.FileVersionLS & 65535]))
                                               if version else None),
                                 collected_from=original,
                                 parser_warnings=pe.get_warnings(),
                                 collection_source_still_matches=(digest(Path(original)) == hashes[name]
                                                                  if original and Path(original).is_file() else None)))
    names = {Path(b['path']).name.lower() for b in binaries}
    if len(names) != len(binaries):
        errors.append('Duplicate PE basenames require manual loader review')
    external = set()
    for binary in binaries:
        if binary['machine'] != '0x8664':
            errors.append('Non-AMD64 PE: ' + binary['path'])
        for entry in binary['imports']:
            entry['resolution'] = dependency_kind(entry['dll'], names)
            if entry['resolution'] == 'unresolved':
                errors.append('Unresolved import: ' + binary['path'] + ': ' + entry['dll'])
            if entry['resolution'] != 'bundled':
                external.add(entry['dll'].lower())
            else:
                available = exports[entry['dll'].lower()]
                missing = [s for s in entry['symbols'] if (s.encode('ascii') if isinstance(s, str) else s) not in available]
                if missing:
                    errors.append('Missing bundled exports: ' + repr((binary['path'], entry['dll'], missing)))
    metadata = {}
    for package, version in {'argostranslate': '1.11.1', 'ctranslate2': '4.8.5', 'sentencepiece': '0.2.1',
                             'minisbd': '0.9.5', 'numpy': '2.5.4'}.items():
        path = root / '_internal' / f'{package}-{version}.dist-info/METADATA'
        parsed = BytesParser().parsebytes(path.read_bytes())
        metadata[package] = dict(name=parsed['Name'], version=parsed['Version'], sha256=digest(path))
        if parsed['Name'].lower() != package or parsed['Version'] != version:
            errors.append('Incorrect metadata: ' + package)
    from PyInstaller.archive.readers import CArchiveReader
    pyz = CArchiveReader(str(executable)).open_embedded_archive('PYZ.pyz')
    excluded = [name for name in pyz.toc if name.split('.')[0] in EXCLUDED]
    excluded += [name for name in files if any(part.lower().split('.')[0] in EXCLUDED for part in Path(name).parts)]
    if excluded:
        errors.append('Excluded framework collected: ' + repr(excluded))
    # Verify the wheel, locks and production files used by this artifact have
    # not drifted since the build; extra audit scripts are not build inputs.
    project = Path(__file__).resolve().parents[1]
    drift = [name for name, expected in result['source_sha256'].items() if digest(project / name) != expected]
    if drift:
        errors.append('Build input identity drift: ' + repr(drift))
    return dict(passed=not errors, errors=errors, os=platform.platform(), build=str(build),
                executable=str(executable), exe_sha256=hashes[executable.name], zip_sha256=digest(archive),
                file_count=len(files), extracted_bytes=sum(p.stat().st_size for p in files.values()),
                all_file_sha256=hashes, pe_count=len(binaries), pe_inventory=binaries,
                windows_dependencies=sorted(external), metadata=metadata, excluded_modules=excluded,
                build_inputs_unchanged=not drift, clean_windows_acceptance=False,
                limitations=['API-set names are OS contracts, not missing physical files',
                             'Static imports do not enumerate dynamic LoadLibrary calls or prove loader search order',
                             'Bundled export presence does not prove all forwarders resolve on target OS',
                             'OS API/export availability and runtime paths require separate target validation',
                             'Collection hashes are technical provenance, not redistribution clearance'])


def main():
    root = Path(__file__).resolve().parents[1]
    if sys.platform != 'win32' or Path(sys.prefix).resolve() != (root / '.venv').resolve():
        raise SystemExit('Use the project Windows .venv interpreter')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise SystemExit('Refusing to overwrite evidence')
    report = audit(args.build_dir.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['passed', 'errors', 'file_count', 'pe_count', 'extracted_bytes']}, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
