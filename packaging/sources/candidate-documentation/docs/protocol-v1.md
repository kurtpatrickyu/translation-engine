# Worker protocol v1

This is the authoritative application-neutral consumer contract, implemented by
`python -m translation_engine --models-dir <packages> --state-dir <state>` and
the equivalent executable. Consumers integrate through this versioned contract
in their own repositories. No consumer-specific commands or paths exist.

Use binary pipes carrying strict UTF-8 newline-delimited JSON. Each request
occupies one LF-terminated line (CRLF accepted); escape newlines inside strings.
There is no greeting. The worker returns one correlated response per processed
request in order, flushed immediately. Drain stderr independently to avoid pipe
deadlocks. Stdout contains responses only; diagnostics never belong on stdout.

Every request requires integer `protocol_version: 1`, nonempty string `id`
(maximum 128 Unicode scalar values), and a `command`. Extra fields, duplicate
keys, nonstandard JSON numbers, wrong types, and lone surrogate strings fail.
Callers choose unique outstanding IDs; the worker does not retain ID history.
Unparseable/invalid IDs return `null`; valid IDs are preserved on other errors.

```json
{"protocol_version":1,"id":"1","command":"health"}
{"protocol_version":1,"id":"2","command":"info"}
{"protocol_version":1,"id":"3","command":"translate","source":"zh","target":"en","text":"你好，世界！"}
{"protocol_version":1,"id":"3","ok":true,"result":{"source":"zh","target":"en","text":"Hello, world!"}}
{"protocol_version":1,"id":"4","command":"shutdown"}
{"protocol_version":1,"id":"4","ok":true,"result":{"shutdown":true}}
```

Each response contains `protocol_version`, `id`, boolean `ok`, and exactly one
of `result` or `error`. Errors have `code`, actionable `message`, and boolean
`retryable`; no dependency traceback appears in the envelope.

`health` returns `alive`, `ready`, `ready_pairs`, and `error` (null or the same
public error structure). `ok: true` means inspection succeeded even if readiness
is false. First health/translation initializes and warms the backend; later
requests reuse it. Missing/incompatible resources are cached as not ready until
restart. Fix/provision resources outside the worker and restart it.

`info` reports engine/protocol/Argos versions, backend, commands, configured pairs
(including translation/SBD versions), currently ready pairs, and limits. It
does not initialize the model. Only the configured direct `zh` to `en` pair is
implemented. `translate` requires string `source`, `target`, and `text`. Empty
text returns empty output only after readiness succeeds. Unicode and paragraph
newlines are supported, but translation-model quality is not lossless text
preservation; see the recorded [quality limits](compatibility-spike.md).

| Limit | Value |
|---|---|
| Request frame | 1,048,576 bytes excluding LF and optional preceding CR |
| Translation text | 65,536 UTF-8 bytes |
| Serialized response | 1,048,576 bytes excluding LF |
| ID | 128 Unicode scalar values |

Oversized frames are drained in bounded chunks through the next LF before
continuing. Malformed requests do not end a healthy worker. Blank lines fail as
invalid JSON. A partial frame at EOF receives an error; clean EOF exits zero.
`shutdown` flushes its acknowledgement and exits zero without processing later
frames. Broken pipes and fatal startup/config errors exit nonzero. Processing is
sequential; health/shutdown cannot interrupt a long inference. Hosts must impose
timeouts and terminate/restart hung processes, deciding whether retries are safe.

Codes: `INVALID_UTF8`, `INVALID_JSON`, `INVALID_REQUEST`, `REQUEST_TOO_LARGE`,
`TEXT_TOO_LARGE`, `RESPONSE_TOO_LARGE`, `UNSUPPORTED_PROTOCOL`, `UNKNOWN_COMMAND`,
`UNSUPPORTED_LANGUAGE`, `MODEL_MISSING`, `MODEL_INCOMPATIBLE`,
`BACKEND_UNAVAILABLE`, `TRANSLATION_FAILED`, `INTERNAL_ERROR`.

```json
{"protocol_version":1,"id":"5","ok":false,"error":{"code":"UNSUPPORTED_LANGUAGE","message":"Only configured zh to en translation is supported.","retryable":false}}
```

Model installation is an explicit CLI operation, not a protocol request. Version
and compatibility changes must update this reference and conformance tests.
Future language support can extend advertised configured pairs without changing
the envelope; unsupported languages never trigger pivots, downloads, or cloud use.
