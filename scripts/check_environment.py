"""Verify locked imports without loading a model or touching global Argos state."""

import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import tempfile


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        print("Use scripts\\python.cmd scripts\\check_environment.py", file=sys.stderr)
        return 2
    if sys.version_info[:3] != (3, 12, 10) or platform.machine() != "AMD64":
        print("Requires the selected CPython 3.12.10 x64 baseline.", file=sys.stderr)
        return 2
    state_root = root / "runtime"
    state_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="environment-", dir=state_root) as state:
        for variable, directory in {
            "XDG_DATA_HOME": "data",
            "XDG_CONFIG_HOME": "config",
            "XDG_CACHE_HOME": "cache",
            "ARGOS_PACKAGES_DIR": "packages",
        }.items():
            os.environ[variable] = str(Path(state) / directory)
        os.environ.update(
            ARGOS_DEVICE_TYPE="cpu",
            ARGOS_MODEL_PROVIDER="OPENNMT",
            ARGOS_CHUNK_TYPE="MINISBD",
            ARGOS_DEBUG="0",
            ARGOS_DEV_MODE="0",
        )
        modules = (
            "ctranslate2", "sentencepiece", "spacy",
            "minisbd", "onnxruntime", "argostranslate.package",
            "argostranslate.sbd", "argostranslate.translate", "PyInstaller",
        )
        for module in modules:
            try:
                importlib.import_module(module)
            except Exception as error:
                print(f"Import failed: {module}: {type(error).__name__}: {error}", file=sys.stderr)
                return 1
        distributions = (
            "argostranslate", "ctranslate2", "sentencepiece", "spacy",
            "minisbd", "onnxruntime", "pyinstaller", "pip", "pip-tools",
            "setuptools", "wheel", "build",
        )
        for forbidden in ("stanza", "torch"):
            try:
                importlib.metadata.version(forbidden)
            except importlib.metadata.PackageNotFoundError:
                pass
            else:
                raise SystemExit(f"Unexpected {forbidden}; recreate the reduced environment")
            if any(name == forbidden or name.startswith(forbidden + ".") for name in sys.modules):
                raise SystemExit(f"Unexpected loaded {forbidden}")
        print(json.dumps({
            "python": sys.version,
            "os": platform.platform(),
            "machine": platform.machine(),
            "versions": {name: importlib.metadata.version(name) for name in distributions},
            "lock_sha256": {
                name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                for name in ("requirements.lock", "requirements-dev.lock")
            },
            "imports": list(modules),
            "model_loaded": False,
            "translation_verified": False,
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
