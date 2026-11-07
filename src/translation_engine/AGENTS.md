# Runtime and provisioning

## Ownership and flow

- `__main__.py` resolves CLI paths before importing the backend, then constructs
  `ArgosBackend` -> `Service` -> `worker.run`. The separate `provision-model`
  branch validates local files and supplies a warm-up callback with `finally`
  cleanup. No installation command exists on the wire.
- `protocol.py` owns bounded binary framing, strict JSON validation and response
  envelopes. `worker.py` owns sequential dispatch, per-response flushing,
  shutdown/EOF and `finally: service.close()`. Keep the authoritative
  [consumer contract](../../docs/protocol-v1.md) and conformance tests aligned.
- `service.py` owns lazy readiness: `info` does not initialize; first health or
  supported translation initializes once and caches initialization failure until
  restart. Health inspection can succeed while `ready` is false. No automatic
  retry, reload or pivot is implemented.
- `config.py` resolves explicit models before `ARGOS_PACKAGES_DIR`, requires
  writable state, rejects overlapping paths and frozen state inside the executable
  directory. `configure_argos()` sets process-global isolated paths and CPU/MiniSBD
  settings before Argos imports. Preserve this order; multi-config backends in one
  process are not an established isolation mechanism.

## Backend and resource invariants

`backends/argos.py` validates the sole pinned direct package and distribution
versions, configures the environment, constructs `PackageTranslation`, adapts its
tokenizer and warms it with fixed text before retaining the engine. Retain the
native translator, MiniSBD detector and lazy tokenizer across requests. `close()`
drops the engine reference; it does not implement explicit native unload or hot
replacement. Full process reclamation belongs to the supervising host.

`backends/tokenizer.py` adapts only the validated package's uninitialized exact
Argos `SentencePieceTokenizer`. It reads bounded serialized bytes through Python
for Windows Unicode paths, retaining upstream encode/decode and lazy processor
reuse. Do not switch back to native filename loading or patch Argos globally.

`assets.py` supplies runtime asset constants; reconcile changes with
[`models/provenance.json`](../../models/provenance.json) and release metadata.
`provision.py` verifies hashes, archive identity/path/size/link safety and installed
receipts. It stages beneath the destination, validates and warms before rename,
cleans temporary staging on failure, and never replaces existing installations.
Idempotent calls revalidate existing files. Use a new models directory and restart
for replacements. Missing/corrupt/ambiguous ONNX must fail before any downloader
fallback. See [provisioning](../../README.md).

## Failures and checks

Use `EngineError(code, message, retryable=False)` for public failures. Keep
third-party stdout redirected to stderr and Argos text logging suppressed.
Initialization may log a traceback for fixed warm-up failures; request failures
must not leak user text or tracebacks into responses. Broken pipes return nonzero;
valid shutdown flushes acknowledgement and skips subsequent frames. Hosts must
drain stderr separately and enforce timeouts; health cannot interrupt inference.

Run from the repository root:

```bat
scripts\test.cmd tests\unit\test_worker.py tests\unit\test_backend.py tests\unit\test_tokenizer.py -q
```

Worker/protocol changes require malformed-input recovery, byte bounds,
correlation, flush and cleanup coverage. Provisioning changes require synthetic
archive/integrity/preservation tests. Backend/tokenizer/config changes also need
the opt-in real-model regressions described in [test guidance](../../tests/AGENTS.md);
source success alone does not verify a frozen worker.
