"""Relocated local executable smoke/measurement harness; not clean-VM acceptance."""

import argparse
import base64
import ctypes
from contextlib import contextmanager
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from windows_resources import process_tree, process_memory


def main():
    root = Path(__file__).resolve().parents[1]
    if Path(sys.prefix).resolve() != (root / ".venv").resolve() or sys.platform != "win32":
        raise SystemExit("Run with the project's Windows .venv interpreter.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=root / "dist/translation-engine-worker/translation-engine-worker.exe")
    parser.add_argument("--report", type=Path, default=root / "build/packaged-validation.json")
    parser.add_argument('--source', action='store_true', help='Measure actual source worker with the same corpus; no ZIP')
    parser.add_argument('--ascii-paths', action='store_true', help='Isolate non-Unicode operation; not Unicode acceptance')
    args = parser.parse_args()
    report = {"passed": False, "clean_machine": False, "os_firewall_isolation": False,
              "os": platform.platform(), "cpu": platform.processor(), "machine": platform.machine(),
              "cache_conditions": "Fresh worker process; filesystem/DLL caches may be warm from provisioning/copying",
              "memory_sampling_seconds": 0.05, "performance_thresholds": None}
    report.update(corpus_version="local-smoke-v1", repetitions=5,
                  thread_settings={"argos_inter_threads": 1, "argos_intra_threads": 2, "compute_type": "auto"},
                  environment_limitations=["Development host, not a clean VM", "Storage hardware and power mode not captured",
                                            "Worker process tree sampled; short-lived processes between samples may be missed"])
    report['memory_scope'] = 'Sum of worker and descendant counters; per-process OS peak sums are not simultaneous peaks'
    runtime = root / "runtime"
    runtime.mkdir(exist_ok=True)
    process = None
    handle = None
    monitor_thread = None
    stop = threading.Event()
    @contextmanager
    def workspace():
        temporary = tempfile.TemporaryDirectory(prefix="packaged-ascii " if args.ascii_paths else "packaged Caf\u00e9 ", dir=runtime)
        if not Path(temporary.name).resolve().is_relative_to(runtime.resolve()):
            raise ValueError("Temporary workspace escaped the intended root")
        try:
            yield temporary.name
        finally:
            stop.set()
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()
            temporary.cleanup()
    try:
        with workspace() as temporary:
            base = Path(temporary).resolve()
            if not base.is_relative_to(runtime.resolve()):
                raise ValueError("Temporary validation path escaped the workspace")
            relocated = base / "worker folder"
            if args.source:
                executable = Path(sys.executable)
                worker_command = [str(executable), '-m', 'translation_engine']
            else:
                shutil.copytree(args.exe.resolve().parent, relocated)
                executable = relocated / args.exe.name
                worker_command = [str(executable)]
            report['worker_mode'] = 'source' if args.source else 'frozen'
            report['path_mode'] = 'ascii-with-spaces' if args.ascii_paths else 'unicode-with-spaces'
            report['argos_provenance'] = json.loads((root / 'packaging/argos-upstream.json').read_text())
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("PYTHON", "ARGOS_", "VIRTUAL_ENV", "CONDA_"))}
            env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
            models, state = base / "external-models", base / "worker-state"
            provision = subprocess.run(worker_command + [
                "provision-model", "--file", str(root / "downloads/translate-zh_en-1_9.argosmodel"),
                "--sbd-file", str(root / "downloads/zh-hans.onnx"), "--models-dir", str(models),
                "--state-dir", str(base / "provision-state"),
            ], capture_output=True, env=env, timeout=120)
            report['provisioning_stdout'] = provision.stdout.decode('utf-8', errors='replace')
            report['provisioning_stderr'] = provision.stderr.decode('utf-8', errors='replace')
            report['provisioning_stderr_base64'] = base64.b64encode(provision.stderr).decode('ascii')
            if provision.returncode or provision.stdout:
                raise RuntimeError("Frozen provisioning failed: " + provision.stderr.decode(errors="replace"))
            pending, stderr = queue.Queue(), []
            launch = time.perf_counter()
            process = subprocess.Popen(worker_command + ["--models-dir", str(models), "--state-dir", str(state)],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            def read_stdout():
                for frame in iter(process.stdout.readline, b""):
                    pending.put(frame)
                pending.put(None)
            def read_stderr():
                stderr.append(process.stderr.read())
            threading.Thread(target=read_stdout, daemon=True).start()
            errors_thread = threading.Thread(target=read_stderr, daemon=True)
            errors_thread.start()

            class Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
                    (name, ctypes.c_size_t) for name in ("peak_working_set", "working_set", "peak_paged", "paged",
                                                       "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile", "private")]
            kernel, psapi = ctypes.WinDLL("kernel32", use_last_error=True), ctypes.WinDLL("psapi", use_last_error=True)
            kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            handle = kernel.OpenProcess(0x410, False, process.pid)
            memory = []
            def sample():
                counters = [data for pid in process_tree(process.pid) if (data := process_memory(pid))]
                if counters:
                    value = {key: sum(item[key] for item in counters) for key in
                             ('working_set', 'private_bytes', 'peak_working_set')}
                    value['process_count'] = len(counters)
                    memory.append(value)
                    return value
                return None
            def monitor():
                while not stop.wait(0.05):
                    sample()
            monitor_thread = threading.Thread(target=monitor, daemon=True)
            monitor_thread.start()
            number = 0
            def send(command, **fields):
                nonlocal number
                number += 1
                request = {"protocol_version": 1, "id": str(number), "command": command, **fields}
                before = time.perf_counter()
                process.stdin.write(json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n")
                process.stdin.flush()
                response = pending.get(timeout=120)
                if response is None:
                    raise RuntimeError("Frozen worker exited before responding")
                response = json.loads(response)
                if response.get("id") != str(number) or not response.get("ok"):
                    raise RuntimeError("Frozen protocol failure: " + repr(response))
                return response["result"], time.perf_counter() - before
            info, _ = send("info")
            report["cold_process_start_seconds"] = time.perf_counter() - launch
            report["idle_memory"] = sample()
            health, elapsed = send("health")
            report["model_initialization_seconds"] = elapsed
            if not health["ready"]:
                raise RuntimeError("Frozen readiness failed: " + repr(health))
            report["ready_memory"] = sample()
            corpus = ["你好，世界！", "不锈钢保温杯，容量500毫升。轻便耐用。", "这是第一段。\n这是第二段。"]
            observations = []
            for _ in range(5):
                for text in corpus:
                    translated, seconds = send("translate", source="zh", target="en", text=text)
                    if not translated["text"].strip():
                        raise RuntimeError("Empty frozen translation")
                    observations.append({"input_utf8_bytes": len(text.encode()), "seconds": seconds,
                                         "text": text, "output": translated["text"]})
            send("shutdown")
            if process.wait(timeout=30):
                raise RuntimeError("Frozen worker did not exit cleanly")
            errors_thread.join(timeout=5)
            if b"".join(stderr):
                raise RuntimeError("Unexpected frozen stderr: " + b"".join(stderr).decode(errors="replace"))
            stop.set()
            monitor_thread.join(timeout=5)
            report["memory_peak_observed"] = {key: max(item[key] for item in memory) for key in memory[0]} if memory else None
            ordered = sorted(item["seconds"] for item in observations)
            report["translation_latency"] = {"samples": observations, "median_seconds": ordered[len(ordered)//2],
                                              "p95_seconds": ordered[min(len(ordered)-1, int(len(ordered)*0.95))]}
            report["info"] = info
            missing = subprocess.run(worker_command + ['--models-dir', str(base / 'missing-models'),
                '--state-dir', str(base / 'missing-state')], input=b'{"protocol_version":1,"id":"h","command":"health"}\n{"protocol_version":1,"id":"s","command":"shutdown"}\n',
                capture_output=True, env=env, timeout=30)
            missing_responses = [json.loads(frame) for frame in missing.stdout.splitlines()]
            if (missing.returncode or missing.stderr or len(missing_responses) != 2
                    or missing_responses[0]['result']['error']['code'] != 'MODEL_MISSING'):
                raise RuntimeError('Missing-model frozen/source smoke failed: ' + repr(missing.stderr))
            report['missing_model_error'] = 'MODEL_MISSING'
            for key, filename in [('model_sha256', 'translate-zh_en-1_9.argosmodel'), ('sbd_sha256', 'zh-hans.onnx')]:
                with (root / 'downloads' / filename).open('rb') as stream:
                    report[key] = hashlib.file_digest(stream, 'sha256').hexdigest()
            if args.source:
                report['passed'] = True
                return finish(args.report, report)
            report["worker_extracted_bytes"] = sum(file.stat().st_size for file in relocated.rglob("*") if file.is_file())
            archive = args.report.with_suffix('.worker.zip')
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
                for file in relocated.rglob("*"):
                    if file.is_file():
                        if file.suffix == ".argosmodel" or file.name == "zh-hans.onnx":
                            raise RuntimeError("External model asset was bundled unexpectedly")
                        bundle.write(file, Path("translation-engine-worker") / file.relative_to(relocated))
            report["worker_zip_bytes"] = archive.stat().st_size
            with archive.open("rb") as stream:
                report["worker_zip_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
            report["worker_exe_sha256"] = hashlib.sha256(executable.read_bytes()).hexdigest()
            report["asset_sizes"] = {name: (root / "downloads" / name).stat().st_size
                                     for name in ("translate-zh_en-1_9.argosmodel", "zh-hans.onnx")}
            report["passed"] = True
    except Exception as error:
        report['passed'] = False
        report["error"] = str(error)
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
    finally:
        stop.set()
        if monitor_thread:
            monitor_thread.join(timeout=5)
        if handle:
            kernel.CloseHandle(handle)
    return finish(args.report, report)


def finish(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report.get(key) for key in ("passed", "error", "worker_zip_bytes", "worker_extracted_bytes",
                                                        "cold_process_start_seconds", "model_initialization_seconds")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
