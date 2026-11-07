import os

import pytest

from translation_engine.backends.argos import ArgosBackend
from translation_engine.config import Config
from translation_engine.errors import EngineError
from translation_engine.provision import provision


@pytest.fixture
def local_assets(tmp_path, monkeypatch):
    """Small synthetic package: exercise installation safety without ML imports."""
    import json
    import zipfile
    import translation_engine.provision as provisioning
    model, sbd = tmp_path / "fixture.argosmodel", tmp_path / "fixture.onnx"
    metadata = {"from_code": "zh", "to_code": "en", "package_version": "1.9", "argos_version": "1.9.0"}
    with zipfile.ZipFile(model, "w") as archive:
        for name, data in {"metadata.json": json.dumps(metadata), "model/model.bin": "fixture",
                           "sentencepiece.model": "fixture"}.items():
            archive.writestr(f"{provisioning.PACKAGE_NAME}/{name}", data)
    sbd.write_bytes(b"synthetic local SBD")
    monkeypatch.setattr(provisioning, "MODEL_SHA256", provisioning.sha256(model))
    monkeypatch.setattr(provisioning, "SBD_SHA256", provisioning.sha256(sbd))
    return model, sbd


def test_corrupt_archive_does_not_leave_staging(tmp_path, monkeypatch):
    import zipfile
    import translation_engine.provision as provisioning
    model, sbd = tmp_path / "corrupt", tmp_path / "sbd"
    model.write_bytes(b"not a ZIP")
    sbd.write_bytes(b"fixture")
    monkeypatch.setattr(provisioning, "MODEL_SHA256", provisioning.sha256(model))
    monkeypatch.setattr(provisioning, "SBD_SHA256", provisioning.sha256(sbd))
    target = tmp_path / "models"
    with pytest.raises(zipfile.BadZipFile):
        provision(model, sbd, target)
    assert list(target.iterdir()) == []


@pytest.mark.parametrize("field,value", [("from_code", "fr"), ("package_version", "2.0"), ("argos_version", "9.0")])
def test_changed_install_identity_is_rejected(local_assets, tmp_path, field, value):
    import json
    from translation_engine.provision import validate_install
    installed = provision(*local_assets, tmp_path / "models")
    metadata = installed / "metadata.json"
    data = json.loads(metadata.read_text())
    data[field] = value
    metadata.write_text(json.dumps(data))
    with pytest.raises(EngineError) as error:
        validate_install(installed)
    assert error.value.code == "MODEL_INCOMPATIBLE"


def test_interrupted_validation_preserves_previous_and_unrelated_files(local_assets, tmp_path):
    models = tmp_path / "models"
    models.mkdir()
    marker = models / "unrelated.txt"
    marker.write_bytes(b"preserve")
    previous = provision(*local_assets, tmp_path / "previous")
    before = {file.relative_to(previous): file.read_bytes() for file in previous.rglob("*") if file.is_file()}
    def interrupted(_):
        raise KeyboardInterrupt("Simulated interruption before promotion")
    with pytest.raises(KeyboardInterrupt):
        provision(*local_assets, models, validate_runtime=interrupted)
    assert list(models.iterdir()) == [marker]
    assert marker.read_bytes() == b"preserve"
    assert {file.relative_to(previous): file.read_bytes() for file in previous.rglob("*") if file.is_file()} == before


def test_existing_install_revalidation_failure_never_replaces_it(local_assets, tmp_path):
    models = tmp_path / "models"
    installed = provision(*local_assets, models)
    receipt = installed / "installation.json"
    before = receipt.read_bytes(), receipt.stat().st_mtime_ns
    def fail(_):
        raise EngineError("BACKEND_UNAVAILABLE", "Synthetic runtime failure")
    with pytest.raises(EngineError):
        provision(*local_assets, models, validate_runtime=fail)
    assert (receipt.read_bytes(), receipt.stat().st_mtime_ns) == before
    assert list(models.iterdir()) == [installed]


def test_explicit_model_path_precedence_and_global_isolation(tmp_path, monkeypatch):
    global_path = tmp_path / "global"
    global_path.mkdir()
    marker = global_path / "marker"
    marker.write_text("unchanged")
    monkeypatch.setenv("ARGOS_PACKAGES_DIR", str(global_path))
    config = Config.resolve(str(tmp_path / "local"), str(tmp_path / "state"))
    with pytest.raises(EngineError, match="Provision"):
        ArgosBackend(config).initialize()
    assert marker.read_text() == "unchanged" and not list(config.state.iterdir())
    config.configure_argos()
    assert os.environ["ARGOS_PACKAGES_DIR"] == str(config.models)
    assert os.environ["ARGOS_CHUNK_TYPE"] == "MINISBD"
    assert global_path not in [config.models, config.state]


def test_overlapping_paths_rejected(tmp_path):
    with pytest.raises(ValueError, match="overlap"):
        Config.resolve(str(tmp_path), str(tmp_path / "state"))


def test_provision_rejects_wrong_bytes_before_touching_destination(tmp_path):
    model, sbd, target = tmp_path / "bad.argosmodel", tmp_path / "bad.onnx", tmp_path / "models"
    model.write_bytes(b"not the pinned archive")
    sbd.write_bytes(b"not the pinned ONNX")
    with pytest.raises(EngineError, match="checksum"):
        provision(model, sbd, target)
    assert not target.exists()


def test_dependency_mismatch_is_actionable_before_import(tmp_path, monkeypatch):
    import translation_engine.backends.argos as adapter
    monkeypatch.setattr(adapter, "validate_install", lambda _: None)
    monkeypatch.setattr(adapter.importlib.metadata, "version", lambda _: "unexpected")
    with pytest.raises(EngineError) as error:
        ArgosBackend(Config.resolve(str(tmp_path / "models"), str(tmp_path / "state"))).initialize()
    assert error.value.code == "BACKEND_UNAVAILABLE"


def test_duplicate_external_package_is_rejected(tmp_path):
    models = tmp_path / "models"
    extra = models / "other-package"
    extra.mkdir(parents=True)
    (extra / "metadata.json").write_text("{}")
    with pytest.raises(EngineError) as error:
        ArgosBackend(Config.resolve(str(models), str(tmp_path / "state"))).initialize()
    assert error.value.code == "MODEL_INCOMPATIBLE"


@pytest.mark.parametrize("members", [
    ["../escape"], ["/absolute"], ["translate-zh_en-1_9/C:escape"],
    ["translate-zh_en-1_9/File", "translate-zh_en-1_9/file"],
])
def test_archive_paths_fail_before_extraction(tmp_path, monkeypatch, members):
    import zipfile
    import translation_engine.provision as provisioning
    from translation_engine.provision import sha256
    model, sbd, target = tmp_path / "test.argosmodel", tmp_path / "test.onnx", tmp_path / "models"
    with zipfile.ZipFile(model, "w") as archive:
        for name in members:
            archive.writestr(name, b"test")
    sbd.write_bytes(b"test SBD")
    # Test-only pinning lets the archive validator see malicious fixture paths.
    monkeypatch.setattr(provisioning, "MODEL_SHA256", sha256(model))
    monkeypatch.setattr(provisioning, "SBD_SHA256", sha256(sbd))
    with pytest.raises(EngineError, match="Unsafe"):
        provision(model, sbd, target)
    assert not (tmp_path / "escape").exists()
    assert list(target.iterdir()) == []


def test_archive_expansion_limit_is_checked_before_extraction(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import translation_engine.provision as provisioning
    from translation_engine.provision import sha256
    model, sbd = tmp_path / "fixture", tmp_path / "fixture.onnx"
    model.write_bytes(b"fixture archive")
    sbd.write_bytes(b"fixture ONNX")
    monkeypatch.setattr(provisioning, "MODEL_SHA256", sha256(model))
    monkeypatch.setattr(provisioning, "SBD_SHA256", sha256(sbd))
    class LargeArchive:
        def __init__(self, _):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass
        def infolist(self):
            return [SimpleNamespace(file_size=3 * 1024**3)]
        def extractall(self, _):
            raise AssertionError("Oversized archive must never extract")
    monkeypatch.setattr(provisioning.zipfile, "ZipFile", LargeArchive)
    with pytest.raises(EngineError, match="limits"):
        provision(model, sbd, tmp_path / "models")
    assert list((tmp_path / "models").iterdir()) == []
