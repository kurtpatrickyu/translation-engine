"""One monitored onedir diagnostic; preserve outputs and stop on host pressure."""

import json
import argparse
import hashlib
from pathlib import Path
import platform
import subprocess
import sys
import time
import importlib.metadata as metadata
from windows_resources import Job, process_memory, process_tree, system_memory


def verify_package(root):
    """Compare native payload to the preserved successful diagnostic inventory."""
    baseline = Path(__file__).resolve().parents[1] / 'build/diagnostic-20261107-133601/native-static-audit-complete.json'
    from audit_windows_package import EXTERNAL_VC_DLLS, digest
    inventory = json.loads(baseline.read_text(encoding='utf-8'))
    files = {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file()}
    forbidden = [name for name, path in files.items() if path.name.casefold() in EXTERNAL_VC_DLLS
                 or path.name.casefold().startswith(('vc_redist', 'vcredist'))
                 or path.suffix.casefold() in {'.argosmodel', '.onnx'}]
    expected = {name: sha for name, sha in inventory['all_file_sha256'].items()
                if Path(name).suffix.casefold() in {'.dll', '.pyd'}
                and Path(name).name.casefold() not in EXTERNAL_VC_DLLS}
    actual = {name for name, path in files.items() if path.suffix.casefold() in {'.dll', '.pyd'}}
    errors = ['Forbidden payload: ' + name for name in forbidden]
    if actual != set(expected):
        errors.append('Native file-set mismatch: ' + repr(sorted(actual ^ set(expected))))
    errors += ['Changed native bytes: ' + name for name, sha in expected.items()
               if name in files and digest(files[name]) != sha]
    return dict(passed=not errors, errors=errors, file_count=len(files),
                retained_native_files=len(expected), baseline=str(baseline), baseline_sha256=digest(baseline),
                external_vc_dlls=sorted(EXTERNAL_VC_DLLS))


def main():
    root = Path(__file__).resolve().parents[1]
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise SystemExit("Use the project .venv interpreter; run scripts\\setup.cmd first.")
    if sys.platform != "win32" or platform.machine() != "AMD64":
        raise SystemExit("Build on Windows x64; cross-compilation is not supported.")
    for name in ('torch', 'stanza'):
        try:
            metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        raise SystemExit('Unexpected dependency before build: ' + name)
    initial = system_memory()
    # Host protection thresholds, not artifact performance acceptance budgets.
    if initial['physical_available'] < 2 * 1024**3 or initial['commit_available'] < 3 * 1024**3:
        raise SystemExit('Insufficient headroom; no build started')
    run_name = time.strftime('diagnostic-%Y%m%d-%H%M%S')
    build = root / 'build' / run_name
    build.mkdir(parents=True, exist_ok=False)
    destination = root / 'dist' / run_name
    started = time.perf_counter()
    def identities():
        files = list((root / "src").rglob("*.py")) + list((root / 'packaging').glob('*')) + [
            root / "requirements.lock", root / "requirements-dev.lock", root / 'pyproject.toml',
            Path(__file__), root / 'scripts/windows_resources.py', root / 'scripts/audit_windows_package.py']
        return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files if path.is_file()}
    source_hashes = identities()
    command = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--distpath', str(destination),
               '--workpath', str(build / 'work'), 'packaging/worker.spec']
    report = {'python': sys.version, 'os': platform.platform(), 'machine': platform.machine(),
              'command': command, 'source_sha256': source_hashes, 'samples': [], 'sampling_seconds': 0.25,
              'initial_system_memory': initial, 'resource_abort': None, 'distribution_clearance': 'pending',
              'clean_windows_acceptance': 'pending',
              'executable': str(destination / 'translation-engine-worker/translation-engine-worker.exe')}
    process = job = None
    try:
        with (build / 'pyinstaller.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
            job = Job(process)
            pressure = 0
            while process.poll() is None:
                system = system_memory()
                processes = {str(pid): data for pid in process_tree(process.pid) if (data := process_memory(pid))}
                report['samples'].append({'seconds': time.perf_counter()-started, 'system': system, 'processes': processes,
                    'tree_working_set': sum(p['working_set'] for p in processes.values()),
                    'tree_private_bytes': sum(p['private_bytes'] for p in processes.values())})
                pressure = pressure + 1 if (system['physical_available'] < 768 * 1024**2 or system['commit_available'] < 1024**3) else 0
                if pressure >= 3 or time.perf_counter()-started > 1200:
                    report['resource_abort'] = 'Sustained RAM/commit pressure or 20-minute diagnostic limit'
                    job.close()
                    break
                time.sleep(0.25)
            report['returncode'] = process.wait(timeout=30)
    except BaseException as error:
        report['error'] = repr(error)
    finally:
        if job:
            job.close()
        if process and process.poll() is None:
            process.kill()
        report['seconds'] = time.perf_counter()-started
        report['source_unchanged_during_build'] = identities() == source_hashes
        if report['samples']:
            for key in ('tree_working_set', 'tree_private_bytes'):
                report['peak_' + key] = max(s[key] for s in report['samples'])
            report['minimum_available_ram'] = min(s['system']['physical_available'] for s in report['samples'])
            report['minimum_commit_headroom'] = min(s['system']['commit_available'] for s in report['samples'])
        report['passed'] = report.get('returncode') == 0 and not report.get('error') and not report['resource_abort'] and report['source_unchanged_during_build']
        if report['passed']:
            try:
                report['packaging_policy'] = verify_package(Path(report['executable']).parent)
                report['passed'] = report['packaging_policy']['passed']
            except Exception as error:
                report['passed'] = False
                report['error'] = repr(error)
        (build / 'build-result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({k: report.get(k) for k in ('passed','returncode','error','resource_abort','seconds','peak_tree_working_set','peak_tree_private_bytes','executable')}, indent=2))
        print('Evidence: ' + str(build))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == "__main__":
    main()
