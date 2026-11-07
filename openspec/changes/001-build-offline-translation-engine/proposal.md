## Why

External desktop applications need a reusable offline translation subprocess that can be distributed independently of their own installers and release cycles. The original scaffold has progressed to a locally working Chinese-to-English Windows worker; this amendment separates local usability/manual testing from publicly redistributable release readiness without discarding A1–A5 history.

## What Changes

- Introduce the `translation_engine` Python package and `python -m translation_engine`, separating process lifecycle, protocol, service, configuration, diagnostics, and the sole Argos backend.
- Define protocol v1: bounded UTF-8 newline-delimited JSON, correlated requests, translation, readiness, version/capabilities, structured errors, and graceful shutdown; reserve stdout for responses.
- Establish project-local `.venv`, `pyproject.toml`, hash-locked dependencies, CMD instructions, and independent CI environments.
- Provide explicit external model provisioning, isolated Argos paths, reusable model loading, and verified offline sentence splitting.
- Explicitly provision a separately pinned Chinese Simplified MiniSBD ONNX resource through Argos's supported package-local path, preserving the original translation archive and dependency pins; review AGPLv3/code/model redistribution obligations before publication.
- Build `translation-engine-worker.exe` using Windows x64 PyInstaller onedir packaging, with runtime dependencies and external model loading; validate Windows 10 and Windows 11 separately before claiming support.
- Distribute only the worker binary ZIP through GitHub Releases, with its integrity manifest/checksums, third-party notices and required code/source compliance materials. Users obtain original `.argosmodel` and MiniSBD `.onnx` assets directly from recorded upstream URLs, verify exact hashes and provision locally; no model binaries are hosted in releases or public CI artifacts.
- Add deterministic unit tests, real-model integration, packaged smoke tests, clean-machine acceptance evidence, packaging performance baselines, and an authoritative versioned protocol reference for all external consumers.
- Organize implementation into A1 foundation, A2 protocol/backend, A3 models/offline, A4 packaging, and A5 release/CI/documentation. Start A2 with a minimal real zh-to-en runtime/model/offline-SBD spike immediately after A1, before extensive protocol or distribution work. Implementation starts only after proposal approval.

Two completion levels apply. **Level A: locally usable and manually testable worker** requires source/frozen functionality, safe local provisioning, local no-network-attempt instrumentation, native inventory, relocation, measured local diagnostics, usage instructions and a recorded manual smoke test. **Level B: publicly redistributable Windows release** additionally requires clean Windows 10 22H2/Windows 11 x64 support evidence, OS-denied networking, complete target measurements, bundled-code/native redistribution compliance, verified worker-only release materials and explicit publication approval. Missing Level B evidence does not block Level A testing or documentation. The existing strict Teruten isolation finding remains a development-host limitation, not proof of an application dependency.

## Capabilities

### New Capabilities

- `isolated-development`: Reproducible project-local development/build environments and scripts.
- `worker-protocol`: Persistent bounded JSON subprocess communication, lifecycle, and diagnostics.
- `offline-argos-translation`: Isolated external model discovery and reusable offline Argos translation.
- `model-provisioning`: Explicit checksum-pinned model acquisition, installation, compatibility, and attribution.
- `windows-worker-distribution`: Independent onedir executable packaging and clean Windows acceptance.
- `release-artifacts`: Verified worker-only versioned releases, external asset metadata, bundled-component compliance, trust model, and consumer documentation.

### Modified Capabilities

None. There are no existing capability specs or application implementation to preserve.

## Impact

Future implementation adds Python source, tests, packaging/provisioning scripts, dependency locks, GitHub Actions, and documentation. Preserve the existing MIT license, OpenSpec configuration, and user's `.gitignore` entries. OpenSpec planning artifacts must be tracked in Git even under the existing `openspec/` ignore rule; explicitly add the relevant planning files without adding model binaries or generated outputs. Keep `.venv`, downloaded models, and build outputs ignored.

Proposed baseline: CPython 3.12 x64, Argos Translate 1.11.0, CTranslate2 4.8.5, SentencePiece 0.2.1, and PyInstaller 6.22.3. Published metadata supports this candidate combination, but a complete Windows dependency resolution, sentence-boundary configuration, and frozen execution remain verification gates, not proven compatibility.

Approved on 2026-11-07: replace only the Argos source artifact with unmodified upstream commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` (metadata version 1.11.1), which makes Stanza optional. Isolated real-model evaluation passed without Stanza/Torch, including simulated spaCy absence. Prefer this exact upstream source over maintaining a backport. Preserve the old 1.11.0 environment and failure reports; use a reviewed source-to-wheel recipe and hash-locked artifact, fresh dependency resolution, actual worker revalidation, and evidenced frozen exclusions. Preserve other retained runtime pins, both model assets, protocol, and A1-A5 exits. See `docs/upstream-argos-evaluation.md`; source success does not resolve frozen provisioning or establish a memory baseline.

The model remains upstream `translate-zh_en-1_9.argosmodel` (package 1.9, declared Argos 1.9.0), with the unchanged separately pinned MiniSBD ONNX asset. Preserve the passed compatibility spike and production provisioning evidence, exact hashes, source attribution, and known/unknown license status. Model redistribution clearance is not a Level A gate or a prerequisite to the worker-only release merely because external models are referenced; unknown model licenses are not declared cleared. Any future model hosting requires a separate reviewed scope and legal clearance. MiniSBD AGPLv3 code/source/notices, Visual C++/native DLL rights, and other bundled components remain mandatory Level B compliance gates. This amendment changes planning only.

Windows 10 22H2 x64 and Windows 11 x64 are candidate acceptance rows based on upstream platform documentation; neither is validated yet. Record technical failures before restricting support. A4 measures ZIP/extracted size, cold start, model initialization, memory, and repeated translation latency with environment details, establishing a baseline without invented thresholds. Native stdout redirection and release automation remain as simple as observed behavior permits while retaining protocol purity, integrity checks, and clean-machine verification.

Out of scope: Freya integration/installer/download manager, Sheets/catalog logic, migrations, network APIs, GUI, other backends, cloud providers, auto-updates, translation caching, persistent databases, implicit model installation, and unrelated refactors. Level A may complete before clean Windows acceptance or publication compliance. Level B retains both clean OS rows for the same worker/model hashes. Advanced CI/publication automation, mandatory platform immutability integration and attestation infrastructure are deferred; versioned non-overwritten artifacts, integrity checks and explicit approval remain required.
