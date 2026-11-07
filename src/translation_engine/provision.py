"""Explicit local-only, staged installation of the unchanged Argos archive and SBD asset."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

from .assets import MODEL_SHA256, PACKAGE_NAME, SBD_SHA256
from .errors import EngineError


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_install(path: Path):
    if not path.is_dir():
        raise EngineError("MODEL_MISSING", "Provision the pinned model and zh-hans MiniSBD resource, then restart.")
    try:
        root = path.resolve()
        if path.is_symlink():
            raise ValueError("Package links are not an isolated installation")
        for name in ("metadata.json", "installation.json", "minisbd", "minisbd/zh-hans.onnx"):
            if not (path / name).resolve().is_relative_to(root):
                raise ValueError("Installed resource escapes package directory")
        metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
        if (metadata["from_code"], metadata["to_code"], metadata["package_version"], metadata["argos_version"]) != ("zh", "en", "1.9", "1.9.0"):
            raise ValueError("Unexpected package identity")
        sbd = list((path / "minisbd").glob("*.onnx"))
        if len(sbd) != 1 or sbd[0].name != "zh-hans.onnx" or sha256(sbd[0]) != SBD_SHA256:
            raise ValueError("Missing or changed MiniSBD resource")
        receipt = json.loads((path / "installation.json").read_text(encoding="utf-8"))
        if receipt["model_sha256"] != MODEL_SHA256 or receipt["sbd_sha256"] != SBD_SHA256:
            raise ValueError("Unexpected installation identity")
        expected_files = receipt["files"]
        if not {"metadata.json", "model/model.bin", "sentencepiece.model", "minisbd/zh-hans.onnx"} <= expected_files.keys():
            raise ValueError("Incomplete receipt")
        for name, digest in expected_files.items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts or ":" in name or "\\" in name:
                raise ValueError("Invalid receipt path")
            if not (path / name).resolve().is_relative_to(root):
                raise ValueError("Installed file escapes package directory")
            if sha256(path / name) != digest:
                raise ValueError("Installed files changed")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise EngineError("MODEL_INCOMPATIBLE", "Installed model/SBD is incomplete or changed; reprovision into a new directory.") from error


def provision(model: Path, sbd: Path, destination: Path, validate_runtime=None) -> Path:
    if sha256(model) != MODEL_SHA256 or sha256(sbd) != SBD_SHA256:
        raise EngineError("MODEL_INCOMPATIBLE", "Asset checksum mismatch; obtain the exact pinned files.")
    destination.mkdir(parents=True, exist_ok=True)
    final = destination / PACKAGE_NAME
    # Published installations are immutable: never replace an active worker's files.
    if final.exists():
        validate_install(final)
        if validate_runtime:
            validate_runtime(destination)
        return final
    with tempfile.TemporaryDirectory(prefix=".provision-", dir=destination) as temporary:
        stage = Path(temporary)
        with zipfile.ZipFile(model) as archive:
            entries = archive.infolist()
            if len(entries) > 10000 or sum(entry.file_size for entry in entries) > 2 * 1024**3:
                raise EngineError("MODEL_INCOMPATIBLE", "Archive exceeds extraction limits.")
            seen = set()
            for entry in entries:
                name = entry.filename
                path = PurePosixPath(name)
                key = path.as_posix().casefold()
                if (path.is_absolute() or ".." in path.parts or ":" in name or "\\" in name
                        or not path.parts or path.parts[0] != PACKAGE_NAME
                        or stat.S_ISLNK(entry.external_attr >> 16) or key in seen):
                    raise EngineError("MODEL_INCOMPATIBLE", "Unsafe or duplicate archive path.")
                seen.add(key)
            archive.extractall(stage)
        package = stage / PACKAGE_NAME
        (package / "minisbd").mkdir()
        shutil.copyfile(sbd, package / "minisbd" / "zh-hans.onnx")
        receipt = {
            "model_sha256": MODEL_SHA256, "sbd_sha256": SBD_SHA256,
            "files": {file.relative_to(package).as_posix(): sha256(file)
                      for file in package.rglob("*") if file.is_file()},
        }
        (package / "installation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        validate_install(package)
        if validate_runtime:
            validate_runtime(stage)
        # This code never removes or overwrites an existing installation.
        package.rename(final)
    return final
