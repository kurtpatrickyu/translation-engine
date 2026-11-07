## Context

See proposal.md for motivation and scope. Initial inspection on 2026-11-06 found no application source, tests, packaging, dependency configuration, workflows, or existing capability specs. Preserve the existing MIT `LICENSE`, README project identity, and `openspec/config.yaml` (`spec-driven`). `.agent/` and `.codex/` contain local skills, not application code. At refinement, `.gitignore` is tracked and already excludes virtual environments, model downloads/state, build outputs, local tooling, and `openspec/`. Preserve its entries and explicitly add this change's planning artifacts to Git despite that rule; do not stage the adjacent ZIP or generated files. A1 verifies continued planning-artifact tracking and ignored development outputs. No ignore-file edit is needed for this scoped refinement.

The installed CLI works through `openspec.cmd` with access to its user-profile installation. PowerShell's `.ps1` launcher is blocked by execution policy. Git inspection used a command-scoped safe-directory override, without changing global Git configuration. This refinement updates the existing repo-local `001-build-offline-translation-engine` change in place; there is no registered-store indication.

The initial research established a candidate baseline. Implementation now verifies the locked host-local graph and real translation with package-local MiniSBD; no clean-machine verification has occurred. See `docs/compatibility-spike.md` for measured evidence and limitations.

## Goals / Non-Goals

**Goals:** Keep the subprocess contract stable while isolating the Argos implementation, model state, and packaging concerns. Make readiness mean usable offline translation. Make every publication input traceable and fail closed when evidence is missing.

**Non-Goals:** Backend discovery, registry, dependency injection framework, runtime downloads, GUI, HTTP service, consumer-specific path conventions, and changes to external applications. Engine release automation ends at this repository's artifacts.

## Completion levels and current evidence

This approved amendment separates **Level A (local usability/manual testing)**
from **Level B (public Windows redistribution/support)** within the same A1–A5
change. It supersedes the earlier combined model-hosting/completion gates;
historical evidence documents and raw success/failure reports remain unchanged.

Level A requires locked source/frozen worker functionality, exact-hash external
asset provisioning and rollback/integrity, protocol/stdout/shutdown correctness,
local network-attempt instrumentation, technical native inventory, host-local
ASCII/Unicode relocation, limited local performance measurements, and a manual
usage guide plus a recorded manual walkthrough. Local checks report their
coverage limits rather than require clean OS images or redistribution clearance.
Task 4.9's guide is complete in `docs/manual-usage.md`, with syntax/schema/link,
CLI-help/version and existing artifact/asset hash checks, plus the CMD guide in
`docs/manual-testing-cmd.md`. The user's subsequent actual CMD transcript and
additional PowerShell recovery/translation transcript are recorded in
`docs/manual-test-results.md`. Tasks 4.10 and 4.8 are now complete: Level A is
accepted, LOCAL 37/37 and overall 37/54; PUBLIC remains 0/17. The PowerShell
capture includes initial failures and recovery; broader guide completion beyond
that subset is user-confirmed, without invented outputs/timings. Earlier documentation
checks are not relabelled as the user's session, and no test is rerun here.

Existing verified evidence includes 60 passing source tests; five frozen path
scenarios and 75 matching translations; 53 AMD64 native binaries and all 180 ZIP
files checked; and local size/startup/init/memory/latency/build-resource reports.
See `docs/unicode-path-validation.md`, `docs/argos-migration.md` and
`docs/native-dependencies.md`, plus their referenced raw reports. Artifact:
`diagnostic-20261107-133601`, ZIP SHA-256
`965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`.
This is a diagnostic, not a compliant public release ZIP.

Level B additionally requires clean Windows 10 22H2 x64 and Windows 11 x64 with
OS-denied networking, matching final worker/external model hashes and complete
target measurements; bundled-code/native redistribution compliance; final
worker-only manifest/checksums/notices/source-delivery and consumer docs;
candidate verification and explicit publication approval. None is inferred from
Level A. A1–A5 remain independently verifiable phases, with LOCAL/PUBLIC task
labels and split suffixes. The old 29/47 count is historical, not an OS result.

External Teruten modules in this development host remain strict isolation
findings. They are absent from the artifact/static imports and are not proven
application dependencies. Record their observed signatures/paths and unknown
influence without copying/allowlisting them or modifying security software.
They limit clean-host claims but do not negate separately passed local worker
functionality or prevent documentation/manual testing.

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

MiniSBD's bundled AGPLv3 code requires a public worker compliance review covering applicable combined-distribution obligations, license/notices and corresponding-source/build/install delivery. Visual C++/OpenMP/native DLL rights and other bundled components remain independent public gates. Preserve the project's MIT license; it does not clear third-party obligations. The separately obtained Stanza-derived ONNX and translation model retain upstream provenance, attribution and known/unknown terms without a clearance claim. They are not hosted by this project; future model redistribution needs separate review. None of these publication gates blocks Level A testing/documentation.

### 5. Explicit model provisioning and provenance

The [upstream index](https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json) lists `zh` to `en` package **1.9**, declared Argos **1.9.0**, at `https://argos-net.com/v1/translate-zh_en-1_9.argosmodel`. Treat this as the candidate approved source, not a compatibility guarantee for Argos 1.11.0. `zt` is a separate upstream code; do not silently map Traditional Chinese aliases to `zh` or promise their quality.

The completed A2 spike inspected the original candidate and recorded its checksum/index identity. A3 preserves those exact asset identities and available provenance/attribution, including unknown terms, without claiming model license clearance. Users obtain the original `.argosmodel` and `zh-hans.onnx` directly from their recorded upstream providers and verify the reviewed hashes. Subsequent acquisition never learns a new digest or silently selects a new version. The index/engine license is not proof of model rights. No model/ONNX binaries are uploaded in this project's releases or public CI artifacts; future hosting requires separate scope/legal clearance rather than blocking the current local milestone or worker-only release path solely for model redistribution permission.

Provisioning preserves original `.argosmodel` bytes and accepts local upstream-obtained files plus an external destination. A separate explicit maintainer acquisition helper may fetch the pinned upstream URL; the public worker itself performs no downloads. Preserve the existing safe ZIP path/symlink/count/expansion bounds, staged extraction, metadata/tokenizer/native/SBD validation, exact hashes and atomic promotion. Immutable installations and failure rollback preserve prior valid/unrelated files and prevent active-worker mutation. No distribution-direction amendment weakens these checks.

Provisioning must work without target Python. Provide an explicit executable subcommand `provision-model --file <asset.argosmodel> --sbd-file <zh-hans.onnx> --models-dir <packages> --state-dir <state>`. Verify both hashes, stage archive extraction plus package-local ONNX, and validate metadata/native/tokenizer/SBD warm-up before promotion. Installations are immutable: never overwrite an active worker's files; use a new managed directory for replacements. Ordinary translation requests never provision. Additional languages require reviewed resource/provenance/compatibility updates without changing the protocol envelope.

### 6. Windows packaging and acceptance

Use the existing checked-in PyInstaller spec with console/stdio enabled, `onedir`, name `translation-engine-worker`, CPU execution, and external models. The `.venv`-bound monitored build helper preserves output/logs and controls resource pressure. ZIP the complete output directory including `_internal`; a lone EXE is not an artifact. The existing local diagnostic ZIP is verified; the final public ZIP must additionally include reviewed notices/compliance material. Pending public notices do not invalidate the separate diagnostic ZIP task or require a new build for this amendment.

First use pinned standard hooks. Inspect warnings, import graph, metadata lookups, and native dependencies for CTranslate2, SentencePiece, Stanza/Torch, SpaCy/Thinc, MiniSBD/ONNX Runtime, NumPy, and their transitive libraries. Only add targeted `collect_dynamic_libs`, data/metadata collection, hidden imports, or hooks when an observed frozen failure justifies each addition. Do not globally collect every optional package or exclude mandatory imports without evidence. Record hook rationale. Audit Visual C++/OpenMP DLL requirements and redistribution terms; include legally redistributable app-local dependencies where supported. If a system redistributable is still required, resolve it before claiming a self-contained artifact; do not quietly introduce a consumer installer prerequisite.

Assess **Windows 10 and Windows 11 x64 CPU** as candidate targets. [Python 3.12 Windows documentation](https://docs.python.org/3.12/using/windows.html) covers Windows 8.1 and newer, PyInstaller documents Windows 8+, and CTranslate2 publishes Windows x64 wheels without documenting an 11-only requirement. [PyTorch's Windows guidance](https://pytorch.org/get-started/locally/) includes Windows 10 and [ONNX Runtime compatibility](https://onnxruntime.ai/docs/reference/compatibility) reports Windows 10 testing. This is evidence of feasibility, not certification of the final pinned SpaCy/Thinc/Torch/ONNX/native DLL graph or a frozen artifact. No verified dependency reason currently justifies an 11-only limit. Keep the same pins while testing both; record a concrete failing dependency/API/DLL/OS build before proposing a narrower target. Do not infer support for older Windows, ARM64, or GPUs.

| Acceptance row | Required checks for the exact candidate | Current status |
|---|---|---|
| Windows 10 22H2 x64 (19045 family; record edition/update/ESU state) | Real runtime/model spike, native imports, relocated onedir/provisioning/protocol tests, clean Python-free offline inference, measurements | Candidate; pending validation |
| Windows 11 x64 (record tested edition/version/build) | Same checks against the same artifact/model hashes | Candidate; pending validation |

A successful host-local real translation spike gates local worker integration and packaging. Both clean Windows rows with the same final worker/model/SBD hashes are required for Level B public support/release acceptance; their availability does not gate Level A local completion, manual use or documentation. Keep VM tasks pending and label support unvalidated until tested. A support reduction needs reviewed evidence; OS servicing status is recorded separately from binary compatibility.

Host-local packaged smoke tests have passed full-folder relocation, separate/combined Unicode model/executable/state paths, provisioning, repeated translation, resource failures, stdout purity and shutdown. These satisfy 4.5a, not 4.5b/4.6. Each clean target row still needs its own OS-denied-network, Python/Argos-free, empty-cache evidence with artifact/model hashes, OS/CPU, logs and network controls. Hosted or Python-only instrumentation is not clean-machine proof. Both rows remain pending for Level B; no new tests/builds are performed by this planning amendment.

Split measurement evidence: 4.7a credits the recorded limited development-host diagnostic baseline with explicit missing storage/power/cold-cache details. 4.7b retains complete per-target measurements for Level B. Use candidate hashes and baseline evidence rather than invented budgets:

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

Engine uses SemVer with initial proposed `0.1.0`, protocol uses integer v1, and external model package version remains upstream 1.9. Protocol breaking changes increment its version and engine major; compatible additions require documented consumer handling. Dependency/external model changes require versioned metadata and revalidation. Never silently replace an external model identity/hash in published metadata.

Design the manifest JSON Schema as strict version 1 with these required fields:

| Field | Contract |
|---|---|
| `manifest_version` | Integer 1 |
| `engine_version`, `protocol_version` | Engine SemVer and integer protocol |
| `platform.os`, `platform.arch` | `windows`, `x64` |
| `worker.filename`, `worker.url`, `worker.sha256` | Exact ZIP, HTTPS tag-specific release URL, 64 lowercase hex characters |
| `runtime.argos_version` | Actual pinned Argos version |
| `models[]` | External original filenames, source/target codes, package/declared Argos versions, upstream HTTPS URLs, SHA-256, provenance/known-unknown terms and compatibility; not project release assets |
| `sentence_boundary` | External MiniSBD ONNX filename, language, upstream release URL/identity, version, SHA-256, provenance/known-unknown terms and compatible package-local layout |
| `compatibility` | Supported OS/build baseline, CPU requirements, protocol versions, tested runtime/model combinations, external package layout, SBD requirements, and any prerequisites |
| `build` | Source commit, Python/tool versions, lock/native input digests, manual build or CI identity; CI is not mandatory |

The project publishes only its worker ZIP and integrity/compliance material: manifest, `SHA256SUMS`, third-party notices/license texts and required corresponding source/build/install materials (or a reviewed compliant source-delivery mechanism). External model/ONNX files are never attached. Derive repository identity from actual configuration. Worker URLs are version-specific project release URLs; external model URLs refer directly to upstream original assets/release identities, not this project's tags or floating `latest`. Generate worker/compliance hashes from final verified files. `SHA256SUMS` covers all distributed files except itself, including the manifest, but not unattached external binaries. Do not embed a manifest self-hash. Validate external model metadata separately for exact trusted hashes, identity, provenance and compatibility; fail on unavailable/changed upstream bytes rather than replacing pins.

Keep A5 focused on the worker-only ZIP, integrity manifest/checksums, bundled third-party compliance/source delivery, consumer docs, verified candidate and explicit publication approval. Direct scripts and a reviewed manual checklist suffice. Advanced CI orchestration/publication pipelines, mandatory platform immutability integration and attestation infrastructure are deferred, not unfinished prerequisites to Level A or Level B. Existing integrity, non-overwrite, code/native compliance and support-evidence requirements remain mandatory.

Verify the exact candidate's tests, worker hash/file inventory, external model identities, clean OS rows, OS-level offline controls, target measurements, bundled-code/native compliance and source/notices delivery. Manual evidence review can be used but must bind to exact bytes and record commands/results; a checked boolean is insufficient. Any changed/repacked worker needs appropriately renewed evidence. Optional future CI must use locked environments, pinned external Actions and no public model uploads; it does not replace clean OS acceptance.

Prepare a verified candidate, obtain explicit approval for that exact version/asset set, then attach/check the worker-only assets and publish through a direct reviewed procedure with minimal permissions. Never replace published tags/assets; corrections require a new version. No proposal, build, or candidate rehearsal authorizes publication. Checksums detect corruption relative to trusted metadata and do not authenticate themselves; document repository identity, trust assumptions and independently trusted offline metadata without claiming deferred attestation or Authenticode signing exists.

No release settings are changed or release created during proposal work.

### 8. Validation and documentation

Unit tests use a deterministic fake backend and no real models. Cover parsing/encoding, strict types, IDs, limits and line-draining recovery, every command, sequential requests, Unicode, health state, errors, EOF/shutdown, output flush, and stderr isolation. Backend tests exercise isolated paths, dependency failure, incompatible metadata, duplicate/missing models, retained resource initialization, and forbidden network calls.

Preserve the completed mandatory A2 real-model spike and A3/A4 host-local tests. Local tests use explicit asset paths, fresh isolated state/caches and Python network-attempt instrumentation with stated native/OS limits. Level B separately adds OS-denied networking and complete measurements on both clean rows. Keep actual segmentation/quality limits, empty/paragraph behavior, retained-resource tests, archive/hash/schema/provenance rejection and stdout/protocol safety. Add a distinct manual guide and recorded manual session for Level A, without waiting for public support or compliance completion.

Documentation deliverables: expanded README; Windows setup/CMD and lock maintenance; test/build guide; explicit model acquisition/provisioning; authoritative versioned v1 protocol and error reference; manifest schema/example; validated Windows matrix and performance baseline; version/compatibility policy; release/trust process; third-party notices; troubleshooting native DLLs, missing models/SBD, malformed frames, path permissions, and timeouts; neutral external integration guide using argument lists, explicit paths, independent stderr draining, bounded buffering, request IDs, exit handling, restart and reprovisioning. The guide directs future Freya integration to the public protocol contract; no Freya-specific fields or code enter this repository.

## Risks / Trade-offs

- [Full Argos dependency graph is large and metadata is permissive] → Lock the complete Windows graph and validate it before backend work; do not treat top-level Python classifiers as proof.
- [Runtime/model/SBD incompatibility discovered late] → Gate extensive A2 work on the immediate post-A1 real-model spike; choose the simplest validated offline path and retain version-change blockers.
- [Windows dependency documentation is broader than frozen-artifact evidence] → Validate Windows 10/11 separately and record technical failures; unavailable test environments remain pending rather than unsupported.
- [External model terms/provenance incomplete] → Preserve exact known hashes and accurate attribution/unknown terms; do not host binaries. Future model hosting requires separate clearance; library/index licenses are insufficient evidence.
- [Native DLLs or descriptor output escape ordinary Python tests] → Frozen executable tests plus clean VM acceptance; add only evidenced hooks and app-local runtime files.
- [Sequential inference can block shutdown] → Document host timeouts/termination and restart; asynchronous cancellation is outside v1.
- [Reproducible inputs do not imply byte-identical ZIPs/EXEs] → Record tooling and hashes for each candidate and bind acceptance evidence to those exact bytes.
- [GitHub identity compromise can undermine trusted distribution] → Verify expected repository/version and independently trusted metadata, never overwrite published assets, and explain that hashes alone do not authenticate. Advanced immutability/attestation integration is deferred.
- [Ignore rules hide planning/provenance files] → Explicitly track reviewed text artifacts while preserving user's ignore entries and exclusions for binaries, `.venv`, and build outputs.
- [Large footprint or slow cold start from mandatory dependencies] → Measure A4 size/time/memory on recorded environments before setting budgets or attempting optimizations that could affect compatibility.

## Migration Plan

Retain the existing source/frozen worker, approved Argos revision, Unicode fix, locks, original assets and historical evidence. A1–A3 provide the local foundation/backend/provisioning exits; A4 local technical tasks are credited independently of public OS/compliance tasks. Finish the manual guide/session and sign off Level A without waiting for Level B. A5 prepares worker-only integrity/compliance/docs/candidate materials; clean target evidence and bundled-code/native obligations still gate public support/release. Rollback uses previous versioned worker metadata and exact external model identities, never rewrites published assets, and changes no external application.

## Outstanding Verification Blockers

These are planned evidence gates, not assumptions silently deferred as open architectural choices:

1. Level A: complete. Existing technical evidence plus the user's complete CMD session and additional PowerShell recovery/translation log satisfy 4.9/4.10/4.8; see `docs/manual-test-results.md`. Preserve PowerShell's initial missing-asset failures and limited capture; broader completion is user-confirmed. Unrecorded timings/host details remain evidence limits, not invented results or new public-gate prerequisites.
2. Level B: 3.8b/4.5b/4.6/4.7b still require clean OS-denied-network, support and complete target measurements for both Windows rows against the same final worker and external asset hashes. Teruten observations remain a host limitation; no clean-isolation or untested support claim is made.
3. Level B: 3.2/4.3b/5.3 retain bundled MiniSBD AGPLv3/source/notices, Visual C++/OpenMP/native and other component compliance. System32-collected VC hashes are technical provenance, not approved acquisition/rights clearance. Model hosting is excluded; preserve unknown external model terms without adding their redistribution clearance to the local milestone.
4. Level B: final worker-only ZIP, manifest/checksums/compliance materials, consumer docs and candidate verification remain pending. Explicit publication approval is still required. Advanced automation, mandatory platform immutability integration and attestations are deferred; versioned non-overwrite and integrity requirements remain mandatory.
