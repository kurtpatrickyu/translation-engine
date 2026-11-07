"""Bounded strict UTF-8 NDJSON framing and v1 envelopes."""

import json

from .errors import EngineError

LIMITS = {"request_bytes": 1048576, "text_bytes": 65536, "response_bytes": 1048576, "id_characters": 128}
COMMANDS = ("translate", "health", "info", "shutdown")


def valid_id(value):
    if not isinstance(value, str) or not 1 <= len(value) <= LIMITS["id_characters"]:
        return False
    try:
        value.encode("utf-8")
        return True
    except UnicodeError:
        return False


def frames(stream):
    limit = LIMITS["request_bytes"]
    while True:
        line = stream.readline(limit + 3)
        if not line:
            return
        terminated = line.endswith(b"\n")
        data = line[:-1].removesuffix(b"\r") if terminated else line
        if len(data) > limit:
            while line and not line.endswith(b"\n"):
                line = stream.readline(65536)
            yield EngineError("REQUEST_TOO_LARGE", "Request exceeds the advertised byte limit.")
        elif not terminated:
            yield EngineError("INVALID_REQUEST", "Final request must end with a newline.")
        else:
            yield data


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def parse(data):
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise EngineError("INVALID_UTF8", "Input must be UTF-8.") from error
    try:
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonstandard number")))
    except (ValueError, RecursionError) as error:
        raise EngineError("INVALID_JSON", "Input must be a strict JSON object without duplicate keys.") from error


def validate(request):
    if not isinstance(request, dict) or not valid_id(request.get("id")):
        raise EngineError("INVALID_REQUEST", "Supply an object with a valid nonempty string id.")
    if type(request.get("protocol_version")) is not int:
        raise EngineError("INVALID_REQUEST", "protocol_version must be an integer.")
    if request["protocol_version"] != 1:
        raise EngineError("UNSUPPORTED_PROTOCOL", "Supported protocol_version is 1.")
    command = request.get("command")
    if not isinstance(command, str):
        raise EngineError("INVALID_REQUEST", "command must be a string.")
    if command not in COMMANDS:
        raise EngineError("UNKNOWN_COMMAND", "Use an advertised command.")
    required = {"protocol_version", "id", "command"}
    if command == "translate":
        required |= {"source", "target", "text"}
    if set(request) != required:
        raise EngineError("INVALID_REQUEST", "Unexpected or missing request fields.")
    if command == "translate":
        if any(not isinstance(request[key], str) for key in ("source", "target", "text")):
            raise EngineError("INVALID_REQUEST", "source, target, and text must be strings.")
        try:
            sizes = {key: len(request[key].encode("utf-8")) for key in ("source", "target", "text")}
        except UnicodeError as error:
            raise EngineError("INVALID_REQUEST", "Strings must contain valid Unicode scalar values.") from error
        if sizes["text"] > LIMITS["text_bytes"]:
            raise EngineError("TEXT_TOO_LARGE", "Text exceeds the advertised UTF-8 byte limit.")
    return request


def encode(identifier, *, result=None, error=None):
    envelope = {"protocol_version": 1, "id": identifier, "ok": error is None}
    envelope["error" if error else "result"] = error.payload() if error else result
    data = json.dumps(envelope, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(data) > LIMITS["response_bytes"]:
        return encode(identifier, error=EngineError("RESPONSE_TOO_LARGE", "Result exceeds the response limit."))
    return data + b"\n"
