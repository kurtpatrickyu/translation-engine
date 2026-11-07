## Context

See proposal.md for motivation and scope. Initial inspection on 2026-11-06 found no application source, tests, packaging, dependency configuration, workflows, or existing capability specs. Preserve `LICENSE` (MIT, 2026 kurtpatrickyu), README project identity, and `openspec/config.yaml` (`spec-driven`). `.agent/` and `.codex/` contain local skills, not application code. At refinement, `.gitignore` is tracked and already excludes virtual environments, model downloads/state, build outputs, local tooling, and `openspec/`. Preserve its entries and explicitly add this change's planning artifacts to Git despite that rule; do not stage the adjacent ZIP or generated files. A1 verifies continued planning-artifact tracking and ignored development outputs. No ignore-file edit is needed for this scoped refinement.

The installed CLI works through `openspec.cmd` with access to its user-profile installation. PowerShell's `.ps1` launcher is blocked by execution policy. Git inspection used a command-scoped safe-directory override, without changing global Git configuration. This refinement updates the existing repo-local `001-build-offline-translation-engine` change in place; there is no registered-store indication.

The initial research established a candidate baseline. Implementation now verifies the locked host-local graph and real translation with package-local MiniSBD; no clean-machine verification has occurred. See `docs/compatibility-spike.md` for measured evidence and limitations.

## Goals / Non-Goals

**Goals:** Keep the subprocess contract stable while isolating the Argos implementation, model state, and packaging concerns. Make readiness mean usable offline translation. Make every publication input traceable and fail closed when evidence is missing.

**Non-Goals:** Backend discovery, registry, dependency injection framework, runtime downloads, GUI, HTTP service, consumer-specific path conventions, and changes to external applications. Engine release automation ends at this repository's artifacts.

## Decisions

### 1. Small package with explicit construction

Proposed layout:

```text
src/translation_engine/
  __main__.py          # argument parsing and process exit
  worker.py            # sequential request loop and lifecycle
  protocol.py          # bounded framing, validation, response envelopes
  service.py           # operations and readiness; narrow backend contract
  backends/argos.py    # sole backend, package selection and retained translator
  config.py           # resolved paths and supported settings
  errors.py           # stable public codes; private exception mapping
  diagnostics.py      # stderr logging and dependency-output protection
tests/{unit,integration,packaging}/
scripts/              # environment, model, build, validation, release tools
packaging/            # PyInstaller spec and justified hooks only
models/               # small reviewed provenance metadata, no model bytes
docs/                 # protocol, integration, compatibility, release references
```

Construct one backend and service explicitly. A small typed interface for readiness, supported pairs, translation, and close is sufficient. Unit tests supply a deterministic fake at this boundary. No registry or dynamic plugin loading. This limits dependency imports during protocol-only tests and permits a future backend to reuse the wire contract.

### 2. Dependency baseline and reproducibility

Select CPython **3.12 x64**, with the exact supported patch recorded in A1 after verifying availability. Restrict Milestone A's tested development/build Python to 3.12; the executable carries its own runtime. Proposed exact direct pins are Argos **1.11.0**, CTranslate2 **4.8.5**, SentencePiece **0.2.1**, and PyInstaller **6.22.3**. These are candidate pins until the complete Windows graph resolves and tests pass; do not silently change them on failure.

Evidence:

- [Argos 1.11.0 release](https://pypi.org/project/argostranslate/1.11.0/) and its [tagged requirements](https://raw.githubusercontent.com/argosopentech/argos-translate/v1.11.0/requirements.txt) show CTranslate2 4.x and SentencePiece 0.2.x constraints and mandatory SpaCy, Stanza 1.10.1, MiniSBD, packaging, and Sacremoses dependencies. Do not infer that current master's optional-dependency instructions apply to this release or omit declared dependencies with `--no-deps`.
- [CTranslate2 installation](https://opennmt.net/CTranslate2/installation.html) documents Windows x64, Python >=3.9, and a Visual C++ runtime requirement. Its [4.8.5 release metadata](https://pypi.org/project/ctranslate2/4.8.5/) includes a CPython 3.12 Windows x64 wheel. CPU execution is selected; CUDA is not a target prerequisite.
- [SentencePiece 0.2.1](https://pypi.org/project/sentencepiece/0.2.1/) supports Python >=3.9 and Windows, including CPython 3.12 wheels.
- [PyInstaller manual](https://pyinstaller.org/en/stable/) supports Python 3.8+ and requires builds on the target OS. [Windows requirements](https://pyinstaller.org/en/stable/requirements.html) do not establish compatibility of the complete Argos dependency graph.

Use standard `venv` and `pyproject.toml` as dependency declarations. Generate committed Windows CPython 3.12 runtime and development/build requirement locks using a pinned pip-tools toolchain, with exact transitive versions and hashes. Record exact bootstrap pip, setuptools/build tooling, lock generator, Python patch, and runner image in build metadata. Lock generation is a deliberate maintainer operation; ordinary setup consumes locks with `--require-hashes`, then installs the local package with `--no-deps --no-build-isolation` after its locked build requirements are present. Run `pip check`. Include all relevant marker branches for the supported Windows baseline; other platforms are not promised by this lock.

Planned CMD instructions (paths and script names are design targets, not existing commands):

```bat
py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe scripts\build_windows.py
```

Local `.cmd` wrappers resolve the repository directory and require its `.venv\Scripts\python.exe`; Python helper scripts check their interpreter as well. CI bootstraps its own `.venv` rather than reusing contributor state. Preserve existing ignore entries for `.venv/`, caches, temporary files, acquired models, installed models, `build/`, and `dist/`. The current `/models/` rule also ignores small provenance metadata: explicitly track reviewed metadata files there while retaining the binary exclusions. Verify tracked planning/metadata paths with `git ls-files` and output exclusions with `git check-ignore --no-index`. Reproducibility means locked inputs and repeatable validated procedures; byte-identical native executables are not claimed without separate evidence.

Immediately after A1's environment setup/lock/import exit, the first A2 task is a minimal standalone real Argos zh-to-en spike using the unchanged candidate runtime and model. Acquire/inspect only that model, record its digest and upstream revision, isolate all paths/caches before imports, and test short Chinese, paragraphs, mixed Unicode, and repeated inference offline. Observe dependency output and identify the simplest supported local SBD path. Record actual versions, model/SBD resources, sample results, network-attempt observations, and reproducible commands before implementing extensive protocol, packaging, or release infrastructure. Do not wait until A3 to discover basic incompatibility. A3 reuses this evidence and develops production provisioning/license review. Failure to translate or prevent network attempts blocks subsequent extensive work; report the cause and seek a reviewed amendment before changing any pinned version, model, or required asset set. This spike is planned work after approval, not executed in this refinement.

### 2a. Approved optional-Stanza upstream adoption amendment

The user approved Approach A on 2026-11-07, including dependency migration, actual-worker validation, and one controlled diagnostic build after source tests pass. The current runtime is the unmodified upstream commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` (2026-08-08, metadata 1.11.1). It catches missing Stanza imports, avoids automatic Stanza selection when absent, and moves Stanza into an optional extra. It does not prevent importing Stanza if left installed, and spaCy remains a default dependency. Create a fresh reduced environment rather than relying on an in-place upgrade.

The revision is thirteen commits beyond v1.11.0 and also omits the explicit CTranslate2 compute argument for `auto`. Review that delta; do not describe it as only the optional-dependency patch. Isolated tests of the exact revision and a four-file functional/metadata backport both passed the unchanged ten-case real-model corpus, with identical outputs and `int8_float32` on this host. Stanza/Torch were absent from installation and loaded modules; a simulated unavailable spaCy import also left spaCy/Thinc unloaded. The full upstream approach avoids a maintained source patch. The disposable backport required derivative versioning and reconstructing a requirements file omitted from the published sdist. Keep it as comparison evidence, not the production strategy. See `docs/upstream-argos-evaluation.md` for identities, limits, and commands/material locations.

After approval, build the exact upstream source into a reviewed wheel using pinned tools and record source digest, commit, recipe/timestamp policy, wheel digest, and dependency provenance. Consume the identified wheel through hash-verified locks and controlled artifact storage; never substitute a floating branch, weaken hash mode for a VCS requirement, or assume a PyPI artifact with the same version is identical. Two local wheel builds with pinned tools and SOURCE_DATE_EPOCH produced the same SHA-256; cross-environment byte reproducibility remains unclaimed. Update the Argos declaration, strict backend/spike expectations, and both locks; retain all other referenced runtime pins and model/SBD hashes. Remove Stanza/Torch and orphaned dependencies from the regenerated closure without dropping shared requirements. Preserve default spaCy metadata for a consistent source environment; evaluate its exclusion only in the fixed-MiniSBD frozen worker. Production requests cannot choose another SBD implementation.

Candidate acceptance must prove real production provisioning/worker initialization, repeated translation, resource reuse, isolated offline behavior, and stdout purity with the new artifact. Only then validate reduced frozen collection, required native libraries, original and relocated paths, missing-resource failures, and memory/size baselines. Only one controlled diagnostic build is authorized in this focused migration; stop on source validation failure or serious resource exhaustion. Aggregate build-process-tree memory/commit evidence must distinguish hook collection from runtime working set/private bytes. Prior 1.11.0 results remain historical baseline evidence, not acceptance of the new artifact. The migration left licensing/source delivery, both clean Windows OS rows, and a relocated Unicode failure pending; section 2b addresses that path failure separately.

### 2b. Unicode SentencePiece path compatibility

The focused Unicode-path repair is authorized separately from the completed Argos migration. A standalone reproduction with SentencePiece 0.2.1 proves Python can read the unchanged 804,374-byte tokenizer model under Unicode paths while native `LoadFromFile` fails with Error #2; `model_proto` accepts those same bytes. Adapt only the validated package's tokenizer before constructing `PackageTranslation`: subclass the pinned Argos `SentencePieceTokenizer`, override only `lazy_processor`, read at most 1 MiB plus one overflow-detection byte through Python, and construct `SentencePieceProcessor(model_proto=...)`. Retain the processor, release the temporary byte buffer after construction, and inherit upstream encode/decode unchanged. Reject unexpected tokenizer types or already initialized instances. No installed dependency edits, global monkey patches, model rewrites, pin/lock changes, or backend replacement are needed. Revalidate upstream API/lifecycle, byte bound, token/decode compatibility, integrity and rollback when upgrading dependencies/models.

Source tests must pass before one additional monitored diagnostic build for this repair. Preserve earlier reports/artifacts; independently test Unicode model, executable, and state locations, then combined Unicode relocation, with real provisioning/readiness/repeated translation/stdout/shutdown. Local success does not complete clean Windows acceptance or OS-denied-network evidence.

### 3. Protocol v1

The finalized versioned protocol reference and corresponding capability spec are the authoritative consumer contract. Publish exact framing, fields, errors, limits, readiness/lifecycle semantics, and examples alongside the engine release and test the worker against them. Every external consumer, including a future Freya integration in its own repository, aligns to that contract; consumer expectations do not add application-specific commands, paths, fields, or behavior to this worker.

No unsolicited greeting. Commands use a common envelope with no optional field aliases. Allowed fields are `protocol_version`, `id`, `command`; `translate` additionally requires `source`, `target`, `text`. Unknown fields and duplicate keys fail validation. Integer checks reject booleans. IDs are nonempty strings, maximum 128 Unicode scalar values; callers use unique IDs for outstanding requests, but the sequential worker does not retain an ID history. JSON scalar strings must be valid Unicode, rejecting lone surrogates. Empty text translates successfully to an empty string when the pair is ready.

Example exchanges (each object is one physical line; translation shown is illustrative, not a golden output):

```json
{"protocol_version":1,"id":"t1","command":"translate","source":"zh","target":"en","text":"你好，世界！"}
{"protocol_version":1,"id":"t1","ok":true,"result":{"source":"zh","target":"en","text":"Hello, world!"}}
{"protocol_version":1,"id":"h1","command":"health"}
{"protocol_version":1,"id":"h1","ok":true,"result":{"alive":true,"ready":true,"ready_pairs":[{"source":"zh","target":"en"}],"error":null}}
{"protocol_version":1,"id":"i1","command":"info"}
{"protocol_version":1,"id":"i1","ok":true,"result":{"engine_version":"0.1.0","protocol_version":1,"backend":"argos","argos_version":"1.11.0","commands":["translate","health","info","shutdown"],"configured_pairs":[{"source":"zh","target":"en","model_version":"1.9"}],"ready_pairs":[{"source":"zh","target":"en"}],"limits":{"request_bytes":1048576,"text_bytes":65536,"response_bytes":1048576,"id_characters":128}}}
{"protocol_version":1,"id":"t2","command":"translate","source":"fr","target":"en","text":"Bonjour"}
{"protocol_version":1,"id":"t2","ok":false,"error":{"code":"UNSUPPORTED_LANGUAGE","message":"Only configured zh to en translation is supported.","retryable":false}}
{"protocol_version":1,"id":"s1","command":"shutdown"}
{"protocol_version":1,"id":"s1","ok":true,"result":{"shutdown":true}}
```

Health `ok:true` means inspection succeeded, even when `ready:false`; then its `error` contains the same public code/message/retryable structure as a failed translation. Info works without backend readiness and reports the actual built versions, configured model identity, and only successfully warmed pairs as ready. Version `0.1.0` is a proposed initial engine version, independent of consumers; it is not an existing release.

Stable errors: `INVALID_UTF8`, `INVALID_JSON`, `INVALID_REQUEST`, `REQUEST_TOO_LARGE`, `TEXT_TOO_LARGE`, `RESPONSE_TOO_LARGE`, `UNSUPPORTED_PROTOCOL`, `UNKNOWN_COMMAND`, `UNSUPPORTED_LANGUAGE`, `MODEL_MISSING`, `MODEL_INCOMPATIBLE`, `BACKEND_UNAVAILABLE`, `TRANSLATION_FAILED`, `INTERNAL_ERROR`. Public messages explain remediation without tracebacks or request contents. Retryable is false for validation and configuration/model failures requiring intervention; transient request failures can be true only when another request in the same process can reasonably succeed.

Use bounded binary reads, explicit UTF-8 decode, strict JSON parsing, LF framing with optional CRLF, and the limits in `worker-protocol/spec.md`. Reject nonstandard JSON numbers as malformed. Drain oversized frames in fixed-size chunks. Blank lines are invalid JSON requests. Invalid/unparseable IDs return null; preserve a valid ID even when another field is invalid. Reject overlarge serialized responses with a small correlated error. EOF without a partial frame closes cleanly; a partial final frame receives an invalid-request error before exit. Broken stdout is fatal and exits nonzero without a retry loop.

The process handles one request at a time, with no background request queue. First health/translation lazily initializes and warms the backend; subsequent health uses cached readiness. Initialization failure is retained until process restart after reprovisioning. A long inference blocks health/shutdown behind it. Consumers impose timeouts, drain both pipes, terminate and restart hung workers, and decide whether retrying a request is appropriate. There is no cancellation command in v1.

Configure application/dependency logging and warnings to stderr first, then observe imports, initialization, failures, and repeated inference in the early spike and subprocess/frozen tests. Add a scoped Python stdout redirect only where observed dependency output requires it. Implement native descriptor/Windows-handle redirection only if tests or dependency behavior demonstrate leakage that supported logging configuration cannot prevent; record that evidence and use the smallest reliable mechanism. If needed, preserve a dedicated protocol writer and flush dependency buffers safely. Do not accept stdout contamination to avoid complexity: response-only stdout remains a release gate, including native dependencies. Avoid logging input/translated text by default.

### 4. Configuration and offline backend

Invocation: `python -m translation_engine --models-dir <installed-packages> --state-dir <writable-state>` or the packaged executable with the same arguments. `--models-dir` overrides `ARGOS_PACKAGES_DIR`; absence of both is a fatal configuration error. State directory is required, independently configurable, and must not overlap the model installation or executable directory. Resolve both at startup; changing the working directory later has no effect. Validate paths before backend imports.

Set `ARGOS_PACKAGES_DIR`, isolated `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME` below state, and explicitly select CPU, local OPENNMT provider, disabled debug/dev mode, and the validated SBD strategy before importing Argos. Worker-owned settings override conflicting inherited Argos options; do not inherit user cloud/provider/SBD settings. [Tagged settings source](https://raw.githubusercontent.com/argosopentech/argos-translate/v1.11.0/argostranslate/settings.py) creates directories on import and reads configuration even when environment settings exist. Isolating only packages is insufficient. Reject unexpected extra package search roots, including environment-specific snap injection, or explicitly restrict discovery to the configured directory.

Use [tagged package APIs](https://raw.githubusercontent.com/argosopentech/argos-translate/v1.11.0/argostranslate/package.py) to inspect installed package identity and [tagged translation APIs](https://raw.githubusercontent.com/argosopentech/argos-translate/v1.11.0/argostranslate/translate.py) for a retained direct package translation. Validate exactly one approved `zh` to `en` package, avoiding automatic pivot routes and ambiguous duplicates. `PackageTranslation` retains its CTranslate2 translator after lazy initialization; force a small offline warm-up before reporting readiness. No ordinary worker path calls package index, download, update, or installation functions.

Selected SBD: Argos's supported **MINISBD** setting and exactly one explicitly provisioned `minisbd/zh-hans.onnx` in the external installed package. Set `ARGOS_CHUNK_TYPE=MINISBD` before imports. Preserve original `.argosmodel` bytes and all dependency/model pins; extract the archive and stage the ONNX separately without dependency monkey patches or legacy checkpoint edits. Fail before constructing the detector if ONNX is missing, corrupt, or ambiguous, preventing download/cache fallback.

Pin the separately acquired Chinese Simplified asset from MiniSBD release `v0.0.1`, release ID 273975424, asset ID 336220945, 616,442 bytes, SHA-256 `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e`, URL `https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx`. Capture upstream release metadata and source revision; provision explicitly before inference. The installed MiniSBD version remains 0.9.5. The user's targeted amendment authorizes this additional asset and local continuation, not publication or dependency upgrades.

The host-local real-model spike passed nine requests with fresh isolated paths, zero audited Python network attempts, and retained translator/detector identities. It covers sentences, products, punctuation, mixed scripts, Unicode, paragraphs, and longer input. Quality limits remain: some Chinese exclamation/question punctuation is grouped; the translation model can lose mixed Unicode content and mistranslate English terms. See `docs/compatibility-spike.md`. Python instrumentation is not OS firewall or clean-machine proof. A Stanza-specific adapter and direct-CTranslate2 production bypass are unnecessary.

MiniSBD's AGPLv3 code and Stanza-derived ONNX provenance require a redistribution compliance plan for covered combined distributions, license/notices and corresponding-source delivery, and explicit model-specific terms. Preserve the project's MIT license; it does not clear third-party obligations. This is a publication gate, not a block on private local experiments or local builds.

### 5. Explicit model provisioning and provenance

The [upstream index](https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json) lists `zh` to `en` package **1.9**, declared Argos **1.9.0**, at `https://argos-net.com/v1/translate-zh_en-1_9.argosmodel`. Treat this as the candidate approved source, not a compatibility guarantee for Argos 1.11.0. `zt` is a separate upstream code; do not silently map Traditional Chinese aliases to `zh` or promise their quality.

At the first A2 spike, retrieve the exact candidate once for local evaluation, inspect contents, compute SHA-256, and capture upstream index commit/retrieval evidence. A3 reuses those exact bytes/digest, reviews model-specific redistribution permission, and commits reviewed provenance metadata. Subsequent acquisition verifies that reviewed digest; never learn a new digest automatically in CI. The [index README license](https://github.com/argosopentech/argospm-index/blob/main/README.md) is not evidence that every model/training corpus has identical redistribution terms. Exact checksum and model license remain **unverified publication blockers**; no placeholder digest is usable. Do not upload the evaluation model as a public CI/release artifact before rights review.

Distribution preserves `.argosmodel` bytes. Provisioning is a separate explicit operation accepting a local file from this repository's release and an external destination; a maintainer-only acquisition option can fetch the pinned upstream URL. Before Argos `install_from_path`, inspect ZIP paths, symlinks, file count, and total extracted bytes with documented finite limits, then extract/install into staging. Validate identity, tokenizer, native model, and offline SBD; atomically promote on the same volume without replacing unrelated packages. Refuse concurrent active-worker mutation; stop worker before provisioning and restart afterward. Failures preserve the prior valid installation.

Provisioning must work without target Python. Provide an explicit executable subcommand `provision-model --file <asset.argosmodel> --sbd-file <zh-hans.onnx> --models-dir <packages> --state-dir <state>`. Verify both hashes, stage archive extraction plus package-local ONNX, and validate metadata/native/tokenizer/SBD warm-up before promotion. Installations are immutable: never overwrite an active worker's files; use a new managed directory for replacements. Ordinary translation requests never provision. Additional languages require reviewed resource/provenance/compatibility updates without changing the protocol envelope.

### 6. Windows packaging and acceptance

Use a checked-in PyInstaller spec with console/stdio enabled, `onedir`, name `translation-engine-worker`, CPU execution, and external models. Build with `.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm packaging\worker.spec` on Windows x64. ZIP the complete output directory, including `_internal` and notices; a lone EXE is not the artifact.

First use pinned standard hooks. Inspect warnings, import graph, metadata lookups, and native dependencies for CTranslate2, SentencePiece, Stanza/Torch, SpaCy/Thinc, MiniSBD/ONNX Runtime, NumPy, and their transitive libraries. Only add targeted `collect_dynamic_libs`, data/metadata collection, hidden imports, or hooks when an observed frozen failure justifies each addition. Do not globally collect every optional package or exclude mandatory imports without evidence. Record hook rationale. Audit Visual C++/OpenMP DLL requirements and redistribution terms; include legally redistributable app-local dependencies where supported. If a system redistributable is still required, resolve it before claiming a self-contained artifact; do not quietly introduce a consumer installer prerequisite.

Assess **Windows 10 and Windows 11 x64 CPU** as candidate targets. [Python 3.12 Windows documentation](https://docs.python.org/3.12/using/windows.html) covers Windows 8.1 and newer, PyInstaller documents Windows 8+, and CTranslate2 publishes Windows x64 wheels without documenting an 11-only requirement. [PyTorch's Windows guidance](https://pytorch.org/get-started/locally/) includes Windows 10 and [ONNX Runtime compatibility](https://onnxruntime.ai/docs/reference/compatibility) reports Windows 10 testing. This is evidence of feasibility, not certification of the final pinned SpaCy/Thinc/Torch/ONNX/native DLL graph or a frozen artifact. No verified dependency reason currently justifies an 11-only limit. Keep the same pins while testing both; record a concrete failing dependency/API/DLL/OS build before proposing a narrower target. Do not infer support for older Windows, ARM64, or GPUs.

| Acceptance row | Required checks for the exact candidate | Current status |
|---|---|---|
| Windows 10 22H2 x64 (19045 family; record edition/update/ESU state) | Real runtime/model spike, native imports, relocated onedir/provisioning/protocol tests, clean Python-free offline inference, measurements | Candidate; pending validation |
| Windows 11 x64 (record tested edition/version/build) | Same checks against the same artifact/model hashes | Candidate; pending validation |

A successful host-local real translation spike gates local worker integration and packaging. Exact Windows 10/11 VM images are identified when available for final A4 acceptance; their availability and completed OS acceptance do not gate A1 exit, local development, or producing the executable that must be tested. Keep VM-dependent tasks pending. Final acceptance and publication require both clean OS rows with the same worker/model/SBD hashes; claim only tested platforms. A support reduction needs reviewed evidence, and OS servicing status is recorded separately from binary compatibility.

Packaged smoke tests relocate the full folder, remove development paths and environment variables, use paths containing spaces/Unicode, provision locally, and exercise the real protocol. They verify repeated translations, errors, flush behavior, stdout purity, and missing resources. A clean VM or Windows Sandbox where available on each target, with networking disabled, no system Python/Argos, and no inherited model/SBD caches, performs final acceptance. Record artifact/model hashes, OS/CPU, process logs, network controls, and results per matrix row. Hosted runner tests or mocked sockets alone are not clean-machine evidence. **Pending manual verification** on both rows until actual evidence is captured; no build or executable verification has occurred in this proposal.

Record A4 packaging measurements for each matrix row using the final candidate hashes, as baseline evidence rather than invented pass/fail budgets:

| Measurement | Definition |
|---|---|
| ZIP size | Worker archive bytes; external `.argosmodel` reported separately |
| Extracted size | Sum of complete onedir file bytes; distinguish filesystem allocation and external model/state sizes |
| Cold-start time | Process launch to flushed first `info` response without model initialization; state fresh-process versus OS-cache-cold runs |
| Model initialization time | First health request to flushed ready response, including model/SBD loading and warm-up; record instrumentation and any overlap with startup |
| Memory consumption | Worker working set and private bytes at idle, after readiness, and observed peak during initialization/repeated inference; include relevant child processes and sampling interval |
| Repeated translation latency | Per-request wall time from write/flush through full correlated response after warm-up for a fixed versioned corpus; report sample count, input sizes, raw observations, median and tail summary |

Record OS edition/version/build, CPU/features, RAM, storage, VM allocation, power settings, Python/tool/lock versions, SBD choice, thread/compute settings, corpus identity, warm-up policy, cache conditions, repetition count, and timing/memory methods. Keep timings in harness diagnostics/evidence, not new protocol fields. Compare Windows 10/11 results without promising equal performance. Measurements must be complete and reproducible for acceptance; performance thresholds are decided only after reviewing the baseline. Retain correctness/offline/reliability gates regardless of measured speed or size.

### 7. Releases, manifest, and trust

Engine uses SemVer with initial proposed `0.1.0`, protocol uses integer v1, and model package version remains upstream 1.9. Protocol breaking changes increment its version and engine major; compatible additions require documented consumer handling. Dependency/model changes require new engine release metadata and revalidation. Never silently replace a model within a published release.

Design the manifest JSON Schema as strict version 1 with these required fields:

| Field | Contract |
|---|---|
| `manifest_version` | Integer 1 |
| `engine_version`, `protocol_version` | Engine SemVer and integer protocol |
| `platform.os`, `platform.arch` | `windows`, `x64` |
| `worker.filename`, `worker.url`, `worker.sha256` | Exact ZIP, HTTPS tag-specific release URL, 64 lowercase hex characters |
| `runtime.argos_version` | Actual pinned Argos version |
| `models[]` | Each has source/target codes, package version, declared Argos version, filename, HTTPS tag-specific URL, SHA-256, provenance/license reference |
| `compatibility` | Supported OS/build baseline, CPU requirements, protocol versions, tested runtime/model combinations, external package layout, SBD requirements, and any prerequisites |
| `build` | Source commit, Python/tool versions, lock digests, CI run identity |

Generate only from final validated bytes. Derive owner/repository from the actual configured repository in implementation; do not assume an origin from the license author. Asset URLs use `/releases/download/v<engine-version>/...`, never `latest`. Publish worker ZIP, original `.argosmodel`, manifest, `SHA256SUMS`, and `THIRD_PARTY_NOTICES.txt` plus required license texts. `SHA256SUMS` covers worker, model, manifest, and notices; do not embed the manifest's own hash in itself. Tests reject duplicate model entries, unknown schemas, wrong URL/tag identities, placeholders, and mismatched hashes/versions.

Build the first independently working Windows executable in A4 before implementing extensive release automation in A5. Start with direct build/validation scripts and a small explicit workflow; avoid a general release framework, plugin layer, or reusable pipeline abstraction without demonstrated reuse. This sequencing does not postpone correctness, model rights, or integrity requirements.

GitHub Actions stages: PR unit/protocol/manifest tests in an independent locked environment; controlled real-model offline job; Windows x64 build; relocated packaged-worker validation; checksum/manifest/notices generation; clean-machine matrix evidence validation; protected publication job with minimal `contents:write` permission. Pin third-party Actions by commit. Release jobs depend on all required validation jobs and the same commit/artifact digests. Clean-machine evidence can be produced manually on clean VMs and supplied for explicit review, but must bind to exact candidate hashes and identify each OS row; a checked boolean is insufficient. Use a focused schema/check script for evidence rather than a general attestation service. Routine integration can be optional locally after the early mandatory spike, but is mandatory for release.

Enable repository immutable releases before first production publication. Create a draft, attach and verify the full asset set, then publish only after gates pass. [GitHub immutable release documentation](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases) describes tag/asset locking and release attestations. Verify expected repository identity and attested release assets using [GitHub's verification guidance](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity). Checksums detect corruption only relative to trusted metadata; an unauthenticated manifest and matching digest can be replaced together. Document the GitHub account/platform trust assumption, attestation verification, and offline verification with previously trusted metadata. Do not equate GitHub attestation with Windows Authenticode signing.

No release settings are changed or release created during proposal work.

### 8. Validation and documentation

Unit tests use a deterministic fake backend and no real models. Cover parsing/encoding, strict types, IDs, limits and line-draining recovery, every command, sequential requests, Unicode, health state, errors, EOF/shutdown, output flush, and stderr isolation. Backend tests exercise isolated paths, dependency failure, incompatible metadata, duplicate/missing models, retained resource initialization, and forbidden network calls.

The minimal real-model spike is mandatory at A2 entry after A1. Thereafter real-model tests run opt-in during routine local development with explicit model paths and mandatorily at A3/A4 acceptance and before release, with caches empty and networking denied. Check nonempty sensible English output using reviewed sample assertions rather than fragile universal exact strings; preserve empty input and paragraph behavior, and record segmentation/quality tradeoffs for the selected SBD. Instrument initialization counts in unit tests, and run repeated real inference to detect resource-reload regressions. Archive/manifest tests cover hash mismatch, safe extraction, invalid schema, broken provenance, and publication gates. A4 captures the performance baseline on both Windows matrix rows without adding speculative thresholds.

Documentation deliverables: expanded README; Windows setup/CMD and lock maintenance; test/build guide; explicit model acquisition/provisioning; authoritative versioned v1 protocol and error reference; manifest schema/example; validated Windows matrix and performance baseline; version/compatibility policy; release/trust process; third-party notices; troubleshooting native DLLs, missing models/SBD, malformed frames, path permissions, and timeouts; neutral external integration guide using argument lists, explicit paths, independent stderr draining, bounded buffering, request IDs, exit handling, restart and reprovisioning. The guide directs future Freya integration to the public protocol contract; no Freya-specific fields or code enter this repository.

## Risks / Trade-offs

- [Full Argos dependency graph is large and metadata is permissive] → Lock the complete Windows graph and validate it before backend work; do not treat top-level Python classifiers as proof.
- [Runtime/model/SBD incompatibility discovered late] → Gate extensive A2 work on the immediate post-A1 real-model spike; choose the simplest validated offline path and retain version-change blockers.
- [Windows dependency documentation is broader than frozen-artifact evidence] → Validate Windows 10/11 separately and record technical failures; unavailable test environments remain pending rather than unsupported.
- [Exact model rights/checksum unknown] → Review and pin before any model publication; library/index licenses are insufficient evidence.
- [Native DLLs or descriptor output escape ordinary Python tests] → Frozen executable tests plus clean VM acceptance; add only evidenced hooks and app-local runtime files.
- [Sequential inference can block shutdown] → Document host timeouts/termination and restart; asynchronous cancellation is outside v1.
- [Reproducible inputs do not imply byte-identical ZIPs/EXEs] → Record tooling and hashes for each candidate and bind acceptance evidence to those exact bytes.
- [GitHub identity compromise can undermine authenticated distribution] → Immutable releases and attestations improve traceability; document the trust boundary rather than claiming hashes alone prove authenticity.
- [Ignore rules hide planning/provenance files] → Explicitly track reviewed text artifacts while preserving user's ignore entries and exclusions for binaries, `.venv`, and build outputs.
- [Large footprint or slow cold start from mandatory dependencies] → Measure A4 size/time/memory on recorded environments before setting budgets or attempting optimizations that could affect compatibility.

## Migration Plan

There is no existing runtime to migrate. Implement A1-A5 with independently checked exits. Host-local real translation compatibility blocks full integration until proven; its success permits local worker/provisioning development and executable builds while VM evidence and license review remain pending. A3 validates local provisioning; unresolved redistribution clearance blocks publication, not private local packaging. A4 produces the executable before clean OS acceptance. A5 can prepare focused release tooling after a working local executable, but production publication and milestone completion require every final gate. Rollback selects previous immutable engine/model/SBD assets without rewriting published versions. No external applications are changed.

## Outstanding Verification Blockers

These are planned evidence gates, not assumptions silently deferred as open architectural choices:

1. A1 host-local resolution, hash locks, and imports passed on CPython 3.12.10 x64. These checks do not establish frozen compatibility; see `docs/implementation-status.md` for recovery evidence.
2. A2's host-local real-model spike passed with unchanged runtime/model pins and the separately approved MiniSBD asset. A3 production-path tests exist; redistribution rights and OS-denied networking remain unverified. Failure of any new candidate still blocks its acceptance and requires a reviewed amendment before changing pins/assets.
3. A4: The approved optional-Stanza source migration passed. A subsequent focused package-local serialized tokenizer adapter resolves the demonstrated SentencePiece Unicode LoadFromFile failure on the development host; original tracebacks/artifacts remain preserved. See `docs/unicode-path-validation.md` for source/frozen path evidence and measured resources. The existing artifact's local native audit verifies 53 AMD64 PEs, bundled non-OS imports/exports, ZIP integrity, and local runtime loading; no packaging fix/rebuild was needed. Host-loaded Teruten modules keep strict isolation failed. Visual C++ DLL collection from System32 is recorded native provenance, not pinned redistributable acquisition or rights clearance; see `docs/native-dependencies.md`. Task 4.5 remains incomplete because both OS matrix rows have not run; licensing/native redistribution review also remains pending. Do not infer an 11-only limitation or full standalone acceptance.
4. A5: Confirm actual repository release identity, immutability availability/configuration, and attach all required evidence before publication. No production release is authorized by this proposal.
