import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from translation_engine.assets import PACKAGE_NAME
from translation_engine.config import Config
from translation_engine.errors import EngineError
from translation_engine.provision import provision, sha256

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "downloads" / "translate-zh_en-1_9.argosmodel"
SBD = ROOT / "downloads" / "zh-hans.onnx"
pytestmark = [pytest.mark.integration, pytest.mark.skipif(
    os.environ.get("ENGINE_INTEGRATION") != "1" or not MODEL.exists() or not SBD.exists(),
    reason="Set ENGINE_INTEGRATION=1 and explicitly acquire the pinned local assets",
)]

AUDITED_WORKER = '''
import runpy, sys, os, importlib.metadata
attempts = []
def audit(event, args):
    if os.environ.get("ENGINE_TEST_EXCLUDE_SPACY") == "1" and event == "import" and args[0].split(".")[0] == "spacy":
        raise ModuleNotFoundError("Simulated frozen spacy exclusion", name="spacy")
    if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.sendto", "socket.sendmsg", "subprocess.Popen", "os.system"}:
        attempts.append(event)
        raise RuntimeError("Forbidden network/process attempt: " + event)
sys.addaudithook(audit)
try:
    runpy.run_module("translation_engine", run_name="__main__")
except SystemExit as result:
    code = result.code
else:
    code = 0
if attempts:
    print("AUDIT_FAILURE: " + repr(attempts), file=sys.stderr)
    code = 99
for prefix in ("stanza", "torch") + (("spacy", "thinc") if os.environ.get("ENGINE_TEST_EXCLUDE_SPACY") == "1" else ()):
    if any(name == prefix or name.startswith(prefix + ".") for name in sys.modules):
        print("UNEXPECTED_LOADED_MODULE: " + prefix, file=sys.stderr)
        code = 98
for name in ("stanza", "torch"):
    try:
        importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        print("UNEXPECTED_INSTALLED_DEPENDENCY: " + name, file=sys.stderr)
        code = 97
raise SystemExit(code)
'''


def call_worker(models, state, requests):
    # sys.argv[0] supplied to -c is accepted by argparse; no shell quoting.
    return subprocess.run(
        [sys.executable, "-c", AUDITED_WORKER, "--models-dir", str(models), "--state-dir", str(state)],
        input=b"".join(json.dumps(request, ensure_ascii=False).encode() + b"\n" for request in requests),
        capture_output=True, timeout=90,
    )


def req(command, identifier, **fields):
    return {"protocol_version": 1, "id": identifier, "command": command, **fields}


@pytest.mark.parametrize("exclude_spacy", [False, True])
def test_real_worker_offline_unicode_repeated_and_no_text_logs(tmp_path, monkeypatch, exclude_spacy):
    if exclude_spacy:
        monkeypatch.setenv("ENGINE_TEST_EXCLUDE_SPACY", "1")
    models, state = tmp_path / "models", tmp_path / "state"
    cli = subprocess.run([
        sys.executable, "-c", AUDITED_WORKER, "provision-model", "--file", str(MODEL),
        "--sbd-file", str(SBD), "--models-dir", str(models), "--state-dir", str(state),
    ], capture_output=True, timeout=90)
    assert cli.returncode == 0, cli.stderr.decode(errors="replace")
    assert not cli.stdout
    assert b"tokenized" not in cli.stderr and b"paragraphs:" not in cli.stderr
    # This actual segmentation check uses the production backend, not a fake.
    from translation_engine.backends.argos import ArgosBackend
    backend = ArgosBackend(Config.resolve(str(models), str(state)))
    backend.initialize()
    text = "这是一个测试。今天的天气很好。"
    assert backend.engine.sentencizer.split_sentences(text) == ["这是一个测试。", "今天的天气很好。"]
    native, detector = backend.engine.translator, backend.engine.sentencizer.detector
    assert backend.translate("你好，世界！") == "Hello, world!"
    assert backend.engine.translator is native and backend.engine.sentencizer.detector is detector
    backend.close()
    product = "不锈钢保温杯，容量500毫升。轻便耐用，适合旅行和日常使用。"
    requests = [req("health", "h"), req("translate", "p", source="zh", target="en", text=product),
                req("translate", "u", source="zh", target="en", text="你好，Alice！ café 😊。"),
                req("translate", "r", source="zh", target="en", text="你好，世界！"),
                req("translate", "r2", source="zh", target="en", text="你好，世界！"),
                req("translate", "paragraph", source="zh", target="en", text="这是第一段。\n这是第二段。"),
                req("translate", "long", source="zh", target="en", text="这是一个测试。" * 40),
                req("translate", "empty", source="zh", target="en", text=""), req("shutdown", "s")]
    result = call_worker(models, tmp_path / "empty-worker-state", requests)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    responses = [json.loads(frame) for frame in result.stdout.splitlines()]
    assert [response["id"] for response in responses] == [request["id"] for request in requests]
    assert all(response["ok"] for response in responses)
    assert responses[0]["result"]["ready"]
    assert "500" in responses[1]["result"]["text"] and "steel" in responses[1]["result"]["text"].lower()
    assert responses[3]["result"]["text"] == responses[4]["result"]["text"] == "Hello, world!"
    assert "\n" in responses[5]["result"]["text"]
    assert responses[6]["result"]["text"].count("test") >= 30
    assert responses[7]["result"]["text"] == ""
    assert not result.stderr, result.stderr.decode(errors="replace")


@pytest.mark.parametrize("broken", ["missing", "corrupt", "ambiguous"])
def test_missing_or_changed_sbd_fails_without_download(tmp_path, broken):
    models = tmp_path / "models"
    installed = provision(MODEL, SBD, models)
    target = installed / "minisbd" / "zh-hans.onnx"
    if broken == "missing":
        target.unlink()
    elif broken == "corrupt":
        target.write_bytes(b"changed")
    else:
        (target.parent / "other.onnx").write_bytes(b"ambiguous")
    result = call_worker(models, tmp_path / "state", [req("health", "h"), req("shutdown", "s")])
    assert result.returncode == 0 and not result.stderr
    health = json.loads(result.stdout.splitlines()[0])["result"]
    assert not health["ready"] and health["error"]["code"] == "MODEL_INCOMPATIBLE"


def test_failed_runtime_validation_never_promotes_and_original_is_unchanged(tmp_path):
    original = sha256(MODEL)
    def fail(_):
        raise EngineError("BACKEND_UNAVAILABLE", "Deliberate runtime rejection")
    with pytest.raises(EngineError):
        provision(MODEL, SBD, tmp_path / "models", fail)
    assert not (tmp_path / "models" / PACKAGE_NAME).exists()
    assert list((tmp_path / "models").iterdir()) == []
    assert sha256(MODEL) == original


def test_existing_install_is_immutable_and_concurrent_provision_does_not_replace(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    models = tmp_path / "models"
    installed = provision(MODEL, SBD, models)
    receipt = installed / "installation.json"
    before = receipt.read_bytes(), receipt.stat().st_mtime_ns
    process = subprocess.Popen([
        sys.executable, "-m", "translation_engine", "--models-dir", str(models),
        "--state-dir", str(tmp_path / "state"),
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        process.stdin.write(json.dumps(req("health", "h")).encode() + b"\n")
        process.stdin.flush()
        assert json.loads(process.stdout.readline())["result"]["ready"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: provision(MODEL, SBD, models), range(2)))
        assert results == [installed, installed]
        assert (receipt.read_bytes(), receipt.stat().st_mtime_ns) == before
        process.stdin.write(json.dumps(req("translate", "t", source="zh", target="en", text="你好，世界！")).encode() + b"\n")
        process.stdin.write(json.dumps(req("shutdown", "s")).encode() + b"\n")
        process.stdin.flush()
        assert json.loads(process.stdout.readline())["result"]["text"] == "Hello, world!"
        assert json.loads(process.stdout.readline())["result"]["shutdown"]
        assert process.wait(timeout=15) == 0
        assert process.stderr.read() == b""
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
