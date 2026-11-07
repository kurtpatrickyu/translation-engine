## Why

External desktop applications need a reusable offline translation subprocess that can be distributed independently of their own installers and release cycles. This repository currently contains only a README title, MIT license, OpenSpec scaffold, and local tooling; Milestone A establishes an independently testable Chinese-to-English engine and Windows distribution.

## What Changes

- Introduce the `translation_engine` Python package and `python -m translation_engine`, separating process lifecycle, protocol, service, configuration, diagnostics, and the sole Argos backend.
- Define protocol v1: bounded UTF-8 newline-delimited JSON, correlated requests, translation, readiness, version/capabilities, structured errors, and graceful shutdown; reserve stdout for responses.
- Establish project-local `.venv`, `pyproject.toml`, hash-locked dependencies, CMD instructions, and independent CI environments.
- Provide explicit external model provisioning, isolated Argos paths, reusable model loading, and verified offline sentence splitting.
- Explicitly provision a separately pinned Chinese Simplified MiniSBD ONNX resource through Argos's supported package-local path, preserving the original translation archive and dependency pins; review AGPLv3/code/model redistribution obligations before publication.
- Build `translation-engine-worker.exe` using Windows x64 PyInstaller onedir packaging, with runtime dependencies and external model loading; validate Windows 10 and Windows 11 separately before claiming support.
- Define pinned model provenance, checksum and redistribution evidence; publish validated worker/model assets, manifest, checksums, and notices through immutable GitHub Releases.
- Add deterministic unit tests, real-model integration, packaged smoke tests, clean-machine acceptance evidence, packaging performance baselines, and an authoritative versioned protocol reference for all external consumers.
- Organize implementation into A1 foundation, A2 protocol/backend, A3 models/offline, A4 packaging, and A5 release/CI/documentation. Start A2 with a minimal real zh-to-en runtime/model/offline-SBD spike immediately after A1, before extensive protocol or distribution work. Implementation starts only after proposal approval.

## Capabilities

### New Capabilities

- `isolated-development`: Reproducible project-local development/build environments and scripts.
- `worker-protocol`: Persistent bounded JSON subprocess communication, lifecycle, and diagnostics.
- `offline-argos-translation`: Isolated external model discovery and reusable offline Argos translation.
- `model-provisioning`: Explicit checksum-pinned model acquisition, installation, compatibility, and attribution.
- `windows-worker-distribution`: Independent onedir executable packaging and clean Windows acceptance.
- `release-artifacts`: Validated immutable releases, manifest contract, trust model, and consumer documentation.

### Modified Capabilities

None. There are no existing capability specs or application implementation to preserve.

## Impact

Future implementation adds Python source, tests, packaging/provisioning scripts, dependency locks, GitHub Actions, and documentation. Preserve the existing MIT license, OpenSpec configuration, and user's `.gitignore` entries. OpenSpec planning artifacts must be tracked in Git even under the existing `openspec/` ignore rule; explicitly add the relevant planning files without adding model binaries or generated outputs. Keep `.venv`, downloaded models, and build outputs ignored.

Proposed baseline: CPython 3.12 x64, Argos Translate 1.11.0, CTranslate2 4.8.5, SentencePiece 0.2.1, and PyInstaller 6.22.3. Published metadata supports this candidate combination, but a complete Windows dependency resolution, sentence-boundary configuration, and frozen execution remain verification gates, not proven compatibility.

Approved on 2026-11-07: replace only the Argos source artifact with unmodified upstream commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` (metadata version 1.11.1), which makes Stanza optional. Isolated real-model evaluation passed without Stanza/Torch, including simulated spaCy absence. Prefer this exact upstream source over maintaining a backport. Preserve the old 1.11.0 environment and failure reports; use a reviewed source-to-wheel recipe and hash-locked artifact, fresh dependency resolution, actual worker revalidation, and evidenced frozen exclusions. Preserve other retained runtime pins, both model assets, protocol, and A1-A5 exits. See `docs/upstream-argos-evaluation.md`; source success does not resolve frozen provisioning or establish a memory baseline.

Candidate model is upstream `translate-zh_en-1_9.argosmodel` (package 1.9, declared Argos 1.9.0). Inspect its actual assets and prove minimal real offline translation at the beginning of A2; select the simplest supported, validated SBD path rather than requiring a Stanza-specific adapter in advance. Compatibility failure blocks further extensive work and requires a reviewed amendment, not a silent pin change. Model redistribution evidence and production provisioning remain A3 gates. No model binaries, dependency installation, implementation, or production release are part of this proposal.

Windows 10 22H2 x64 and Windows 11 x64 are candidate acceptance rows based on upstream platform documentation; neither is validated yet. Record technical failures before restricting support. A4 measures ZIP/extracted size, cold start, model initialization, memory, and repeated translation latency with environment details, establishing a baseline without invented thresholds. Native stdout redirection and release automation remain as simple as observed behavior permits while retaining protocol purity, integrity checks, and clean-machine verification.

Out of scope: Freya integration/installer/download manager, Sheets/catalog logic, migrations, network APIs, GUI, other backends, cloud providers, auto-updates, translation caching, persistent databases, implicit model installation, and unrelated refactors. Milestone A completes only after the actual packaged worker translates zh to en on clean Windows without system Python or network access after provisioning.
