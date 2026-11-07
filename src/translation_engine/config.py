"""Resolve explicit external paths before importing any backend dependency."""

from dataclasses import dataclass
import os
from pathlib import Path
import sys


@dataclass(frozen=True)
class Config:
    models: Path
    state: Path

    @classmethod
    def resolve(cls, models: str | None, state: str | None):
        models = models or os.environ.get("ARGOS_PACKAGES_DIR")
        if not models or not state:
            raise ValueError("Supply --models-dir (or ARGOS_PACKAGES_DIR) and --state-dir.")
        package_root, state_root = Path(models).resolve(), Path(state).resolve()
        if package_root == state_root or package_root in state_root.parents or state_root in package_root.parents:
            raise ValueError("Model and state directories must not overlap.")
        executable_root = Path(sys.executable).resolve().parent
        if getattr(sys, "frozen", False) and (state_root == executable_root or executable_root in state_root.parents):
            raise ValueError("State must be outside the executable directory.")
        state_root.mkdir(parents=True, exist_ok=True)
        # Verify actual access rather than relying on permission bits on Windows.
        import tempfile
        with tempfile.TemporaryFile(dir=state_root):
            pass
        return cls(package_root, state_root)

    def configure_argos(self):
        for key, suffix in {
            "XDG_DATA_HOME": "data", "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
            "STANZA_RESOURCES_DIR": "stanza", "HF_HOME": "hf", "TORCH_HOME": "torch",
        }.items():
            os.environ[key] = str(self.state / suffix)
        os.environ.update(
            ARGOS_PACKAGES_DIR=str(self.models), ARGOS_CHUNK_TYPE="MINISBD",
            ARGOS_DEVICE_TYPE="cpu", ARGOS_MODEL_PROVIDER="OPENNMT",
            ARGOS_DEBUG="0", ARGOS_DEV_MODE="0", ARGOS_INTER_THREADS="1",
            ARGOS_INTRA_THREADS="2", ARGOS_COMPUTE_TYPE="auto",
            HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
        )
        os.environ.pop("SNAP", None)
        os.environ.pop("ARGOS_TRANSLATE_PACKAGE_DIR", None)
