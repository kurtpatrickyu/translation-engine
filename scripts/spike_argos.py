"""Local pinned-model experiment, not production provisioning or offline OS proof."""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import sys
import tempfile
import time
import traceback
import zipfile

from translation_engine.assets import MODEL_SHA256, SBD_SHA256


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--sbd", choices=("default", "stanza-offline", "stanza-local-tokenizer", "minisbd"), default="default")
    parser.add_argument("--sbd-model", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        parser.error("Run through scripts\\python.cmd or .venv\\Scripts\\python.exe")
    def version_or_none(name):
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            return None
    versions = {name: version_or_none(name) for name in (
        "argostranslate", "ctranslate2", "sentencepiece", "stanza", "torch",
        "spacy", "minisbd", "onnxruntime",
    )}
    if any(versions[name] != version for name, version in {
        "argostranslate": "1.11.1", "ctranslate2": "4.8.5",
        "sentencepiece": "0.2.1", "minisbd": "0.9.5",
    }.items()):
        parser.error("Pinned dependency mismatch; do not substitute versions")
    attempts = []
    report = {
        "purpose": "local compatibility experiment; redistribution unverified",
        "python": sys.version, "os": platform.platform(), "machine": platform.machine(),
        "versions": versions, "sbd_mode": args.sbd, "samples": [],
        "network_attempts": attempts, "network_control": "Python audit hook; no OS firewall proof",
        "clean_machine_verified": False, "passed": False,
    }
    runtime = root / "runtime"
    runtime.mkdir(exist_ok=True)
    try:
        digest = hashlib.sha256()
        with args.model.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        report["model_sha256"] = digest.hexdigest()
        if digest.hexdigest() != MODEL_SHA256:
            raise ValueError("Model bytes differ from the recorded evaluation pin")
        with tempfile.TemporaryDirectory(prefix="argos-spike-", dir=runtime) as temporary:
            state = Path(temporary)
            packages = state / "packages"
            packages.mkdir()
            with zipfile.ZipFile(args.model) as archive:
                entries = archive.infolist()
                if len(entries) > 10000 or sum(item.file_size for item in entries) > 2 * 1024**3:
                    raise ValueError("Evaluation archive exceeds bounded extraction limits")
                for item in entries:
                    path = PurePosixPath(item.filename)
                    if (path.is_absolute() or ".." in path.parts or ":" in item.filename
                            or "\\" in item.filename or stat.S_ISLNK(item.external_attr >> 16)):
                        raise ValueError(f"Unsafe archive member: {item.filename}")
                report["archive_files"] = [item.filename for item in entries]
                archive.extractall(packages)
            metadata_paths = list(packages.glob("*/metadata.json"))
            if len(metadata_paths) != 1:
                raise ValueError("Expected exactly one model package")
            package_path = metadata_paths[0].parent
            if args.sbd == "minisbd":
                if not args.sbd_model or hashlib.sha256(args.sbd_model.read_bytes()).hexdigest() != SBD_SHA256:
                    raise ValueError("Supply the explicitly provisioned, pinned zh-hans MiniSBD asset")
                (package_path / "minisbd").mkdir()
                shutil.copyfile(args.sbd_model, package_path / "minisbd" / "zh-hans.onnx")
                report["sbd_sha256"] = SBD_SHA256
            metadata = json.loads(metadata_paths[0].read_text(encoding="utf-8"))
            report["model_metadata"] = metadata
            if (metadata.get("from_code"), metadata.get("to_code"),
                    metadata.get("package_version")) != ("zh", "en", "1.9"):
                raise ValueError("Pinned model identity mismatch")
            for variable, directory in {
                "ARGOS_PACKAGES_DIR": "packages", "XDG_DATA_HOME": "data",
                "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
                "STANZA_RESOURCES_DIR": "stanza-cache", "HF_HOME": "hf-cache",
                "TORCH_HOME": "torch-cache",
            }.items():
                os.environ[variable] = str(state / directory)
            os.environ.update(
                ARGOS_DEVICE_TYPE="cpu", ARGOS_MODEL_PROVIDER="OPENNMT",
                ARGOS_CHUNK_TYPE="MINISBD" if args.sbd == "minisbd" else "DEFAULT" if args.sbd == "default" else "STANZA",
                ARGOS_DEBUG="0", ARGOS_DEV_MODE="0", ARGOS_INTER_THREADS="1",
                ARGOS_INTRA_THREADS="2", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
            )
            os.environ.pop("SNAP", None)

            def deny_network(event, arguments):
                if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo",
                             "socket.sendto", "socket.sendmsg", "subprocess.Popen", "os.system"}:
                    attempts.append({"event": event, "arguments": repr(arguments)[:1000]})
                    raise RuntimeError(f"Forbidden network/process attempt during spike: {event}")

            sys.addaudithook(deny_network)
            started = time.perf_counter()
            from argostranslate import package, translate

            model = package.Package(package_path)
            engine = translate.PackageTranslation(
                translate.Language("zh", "Chinese"), translate.Language("en", "English"), model,
            )
            report["selected_sentencizer"] = type(engine.sentencizer).__name__
            report["packaged_sbd"] = str(model.packaged_sbd_path.relative_to(package_path)) if model.packaged_sbd_path else None
            if args.sbd in {"stanza-offline", "stanza-local-tokenizer"}:
                if not (package_path / "stanza" / "resources.json").is_file():
                    raise ValueError("Candidate has no local Stanza resources.json")
                import stanza

                options = {"processors": "tokenize"}
                if args.sbd == "stanza-local-tokenizer":
                    # Explicitly select the bundled tokenizer. An empty MWT list
                    # prevents automatic optional-MWT discovery against legacy
                    # metadata; it does not pretokenize input or skip tokenization.
                    options = {"package": None, "processors": {"tokenize": "gsdsimp", "mwt": []}}
                report["stanza_options"] = options
                engine.sentencizer.stanza_pipeline = stanza.Pipeline(
                    lang="zh", dir=str(package_path / "stanza"), **options,
                    use_gpu=False, logging_level="WARNING", download_method=None,
                )
            corpus = ["你好，世界！", "这是一个测试。今天的天气很好。",
                      "不锈钢保温杯，容量500毫升。轻便耐用，适合旅行和日常使用。",
                      "你好！你好吗？我很好。", "这款 USB-C 充电器支持 fast charging，功率为65W。",
                      "你好，Alice！测试 Unicode： café 😊。", "这是第一段。\n这是第二段。",
                      "这是一个测试。" * 40, "你好，世界！"]
            native_identity = None
            splitter_identity = None
            detector_identity = None
            for text in corpus:
                before = time.perf_counter()
                segments = engine.sentencizer.split_sentences(text)
                output = engine.translate(text)
                elapsed = time.perf_counter() - before
                if not output.strip() or not re.search(r"[A-Za-z]", output):
                    raise ValueError("Translation lacks a nonempty English result")
                if native_identity is None:
                    native_identity = id(engine.translator)
                    splitter_identity = id(engine.sentencizer)
                    detector_identity = id(engine.sentencizer.detector) if args.sbd == "minisbd" else None
                if id(engine.translator) != native_identity or id(engine.sentencizer) != splitter_identity:
                    raise ValueError("Translation resources were reinitialized")
                if args.sbd == "minisbd" and id(engine.sentencizer.detector) != detector_identity:
                    raise ValueError("MiniSBD detector was reinitialized")
                report["samples"].append({"input": text, "segments": segments, "output": output, "seconds": elapsed})
            if report["samples"][0]["output"] != report["samples"][-1]["output"]:
                raise ValueError("Repeated input produced inconsistent output")
            if attempts:
                raise ValueError("Network/process attempts occurred even if caught by a dependency")
            report.update(passed=True, resource_reuse=True, seconds=time.perf_counter() - started)
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        traceback.print_exc(file=sys.stderr)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report.get(key) for key in (
        "passed", "sbd_mode", "model_sha256", "packaged_sbd", "selected_sentencizer", "error", "network_attempts",
    )}, ensure_ascii=True, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
