import io
import json
import subprocess
import sys

import pytest

from translation_engine.errors import EngineError
from translation_engine.protocol import LIMITS, encode
from translation_engine.service import Service
from translation_engine.worker import run


class FakeBackend:
    def __init__(self, failure=None):
        self.initializations = 0
        self.closed = False
        self.failure = failure

    def initialize(self):
        self.initializations += 1
        if self.failure:
            raise self.failure

    def translate(self, text):
        return text

    def close(self):
        self.closed = True


def request(command="health", identifier="r1", **fields):
    return {"protocol_version": 1, "id": identifier, "command": command, **fields}


def line(value):
    return json.dumps(value, ensure_ascii=False).encode() + b"\n"


def exchange(data, backend=None):
    backend = backend or FakeBackend()
    output = io.BytesIO()
    assert run(io.BytesIO(data), output, Service(backend)) == 0
    return [json.loads(frame) for frame in output.getvalue().splitlines()], backend


def test_sequential_unicode_readiness_and_shutdown():
    text = "你好 café 😊\nsecond paragraph"
    frames = [request("info"), request("health", "h"), request("translate", "t", source="zh", target="en", text=text),
              request("health", "again"), request("shutdown", "s"), request("health", "ignored")]
    result, backend = exchange(b"".join(map(line, frames)))
    assert [item["id"] for item in result] == ["r1", "h", "t", "again", "s"]
    assert result[0]["result"]["ready_pairs"] == []
    assert result[1]["result"]["ready"]
    assert result[2]["result"]["text"] == text
    assert backend.initializations == 1 and backend.closed


@pytest.mark.parametrize("bad,code", [
    (b"{broken\n", "INVALID_JSON"), (b"\xff\n", "INVALID_UTF8"),
    (b"[]\n", "INVALID_REQUEST"), (b"\n", "INVALID_JSON"),
    (b'{"id":"x","id":"y"}\n', "INVALID_JSON"),
    (b'{"value":NaN}\n', "INVALID_JSON"),
    (line(request(protocol_version=True)), "INVALID_REQUEST"),
    (line(request(protocol_version=2)), "UNSUPPORTED_PROTOCOL"),
    (line(request(extra=True)), "INVALID_REQUEST"),
    (line(request(command="unknown")), "UNKNOWN_COMMAND"),
    (line(request(identifier="")), "INVALID_REQUEST"),
    (line(request("translate", source="zh", target="en", text=10)), "INVALID_REQUEST"),
    (b'{"protocol_version":1,"id":"x","command":"translate","source":"zh","target":"en","text":"\\ud800"}\n', "INVALID_REQUEST"),
])
def test_invalid_request_recovers(bad, code):
    result, _ = exchange(bad + line(request(identifier="next")))
    assert result[0]["error"]["code"] == code
    assert result[1]["id"] == "next" and result[1]["ok"]


def test_valid_id_is_preserved_on_field_failure():
    result, _ = exchange(line(request(protocol_version=9)))
    assert result[0]["id"] == "r1"


def test_oversized_line_drains_and_recovers():
    result, _ = exchange(b"x" * (LIMITS["request_bytes"] + 100000) + b"\n" + line(request()))
    assert result[0]["error"]["code"] == "REQUEST_TOO_LARGE"
    assert result[0]["id"] is None and result[1]["ok"]


def test_text_utf8_limit_and_response_limit():
    data = line(request("translate", source="zh", target="en", text="你" * 22000))
    result, _ = exchange(data)
    assert result[0]["error"]["code"] == "TEXT_TOO_LARGE"
    response = json.loads(encode("id", result={"text": "x" * LIMITS["response_bytes"]}))
    assert response["error"]["code"] == "RESPONSE_TOO_LARGE" and response["id"] == "id"


def test_eof_and_crlf():
    assert exchange(b"")[0] == []
    assert exchange(line(request()).replace(b"\n", b"\r\n"))[0][0]["ok"]
    assert exchange(line(request())[:-1])[0][0]["error"]["code"] == "INVALID_REQUEST"


def test_missing_model_health_info_and_shutdown():
    backend = FakeBackend(EngineError("MODEL_MISSING", "Provision local assets."))
    result, _ = exchange(line(request()) + line(request("info")) + line(request("translate", source="zh", target="en", text="你好")) + line(request("shutdown")), backend)
    assert result[0]["result"]["alive"] and not result[0]["result"]["ready"]
    assert result[1]["ok"] and result[2]["error"]["code"] == "MODEL_MISSING"
    assert backend.initializations == 1 and result[3]["result"]["shutdown"]


def test_unsupported_pair_does_not_initialize():
    result, backend = exchange(line(request("translate", source="fr", target="en", text="Bonjour")))
    assert result[0]["error"]["code"] == "UNSUPPORTED_LANGUAGE"
    assert backend.initializations == 0


def test_flush_each_response():
    class Output(io.BytesIO):
        flushed = 0
        def flush(self):
            self.flushed += 1
    output = Output()
    run(io.BytesIO(line(request()) + line(request("shutdown"))), output, Service(FakeBackend()))
    assert output.flushed == 2


def test_real_subprocess_missing_model_stdout_is_json(tmp_path):
    result = subprocess.run([sys.executable, "-m", "translation_engine", "--models-dir", str(tmp_path / "models"),
                             "--state-dir", str(tmp_path / "state")],
                            input=line(request()) + line(request("shutdown")), capture_output=True, timeout=15)
    assert result.returncode == 0
    responses = [json.loads(frame) for frame in result.stdout.splitlines()]
    assert responses[0]["result"]["error"]["code"] == "MODEL_MISSING"
    assert responses[1]["result"]["shutdown"]
