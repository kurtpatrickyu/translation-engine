## Purpose

Deliver a standalone Windows x64 worker whose runtime and external model behavior can be verified independently of developer installations.

## ADDED Requirements

### Requirement: Standalone onedir artifact
A Windows x64 build SHALL produce `translation-engine-worker-win-x64.zip` containing an onedir application with `translation-engine-worker.exe`, Python runtime, required native dependencies, metadata, and notices. The archive SHALL exclude translation models and SHALL require neither system Python, a development `.venv`, a global Argos installation, nor GPU software on the target. Builds SHALL run on Windows from locked inputs.

#### Scenario: Relocated artifact
- **WHEN** the complete archive is extracted to a different directory including spaces and Unicode characters
- **THEN** the executable starts using its bundled runtime and explicitly configured external models

Unicode model, executable, and writable state directories SHALL also be tested
independently, then together, to expose distinct native path dependencies.
Each check SHALL use the unchanged model/SBD bytes and exercise production
provisioning, readiness, repeated translation, integrity failures, stdout purity,
and shutdown. Local diagnostic evidence SHALL remain distinct from clean OS acceptance.

#### Scenario: Approved optional-dependency runtime candidate
- **WHEN** an approved source-pinned Argos candidate passes source-level MiniSBD inference without Stanza/Torch
- **THEN** reduced frozen collection is independently checked for complete required runtime/DLL resources, metadata, stdout purity, startup and relocated provisioning; absent unused SBD frameworks do not justify skipping packaged acceptance

### Requirement: Evidence-based Windows acceptance matrix
The candidate acceptance matrix SHALL include Windows 10 22H2 x64 and Windows 11 x64 CPU. Each row SHALL identify exact tested edition/version/build and validate the pinned runtime/model graph and actual onedir artifact independently. Both rows SHALL use the same exact worker ZIP and model SHA-256 hashes; OS-specific rebuilds or substituted models SHALL NOT satisfy this shared-artifact acceptance. Compatibility claims SHALL be limited to validated rows/builds. A support reduction SHALL require a reviewed amendment with the technical dependency/API/DLL/OS failure evidence; inability to access a test image SHALL remain pending verification rather than prove incompatibility.

#### Scenario: Only one operating system has passed
- **WHEN** Windows 11 passes but the Windows 10 row has not been exercised, or conversely
- **THEN** the other row remains pending and the two-platform release acceptance gate remains closed

#### Scenario: Operating system limitation is demonstrated
- **WHEN** the unchanged pinned graph or packaged executable fails on a candidate OS
- **THEN** the failing build/dependency and diagnostic evidence are recorded before support or version changes are proposed

### Requirement: Clean Windows acceptance evidence
Milestone A completion and release publication SHALL require evidence that the actual packaged executable provisions a local model and translates on both clean Windows 10 22H2 x64 and clean Windows 11 x64 using the same exact worker ZIP/model hashes, with no system Python, no global Argos, and network access disabled. Evidence SHALL identify OS, CPU, release commit, artifact/model checksums, commands, network controls, and results for each row. Mocked tests and hosted runner smoke tests SHALL NOT be represented as clean-machine proof.

#### Scenario: Shared artifact passes both clean operating systems
- **WHEN** the same candidate worker ZIP and model are tested on clean Windows 10 22H2 x64 and Windows 11 x64
- **THEN** each row records matching ZIP/model SHA-256 hashes and successful local provisioning and repeated offline translation without system Python or global Argos

#### Scenario: Clean verification unavailable
- **WHEN** clean Windows verification has not run
- **THEN** final acceptance remains pending and publication stays blocked, while local development and executable production may proceed after the host-local spike passes

### Requirement: Packaging performance baseline
A4 packaging acceptance SHALL record worker ZIP bytes, complete extracted onedir file bytes, cold process launch to first uninitialized info response, model/SBD initialization through ready warm-up, idle/ready/peak memory consumption, and repeated warmed translation latency. External model size SHALL be recorded separately. Evidence SHALL bind measurements to artifact/model hashes and record OS/build, CPU, RAM, storage/VM allocation, settings, measurement methods, cache conditions, corpus/input sizes, repetitions, and raw results with summary statistics. Acceptance SHALL require a reproducible baseline without inventing size, speed, or memory budgets before that baseline is reviewed.

Approved diagnostic builds SHALL additionally capture build-process-tree memory and system commit/available memory separately from runtime inference measurements. Source-level module absence alone SHALL NOT establish build memory savings, runtime memory reduction, or executable size.

#### Scenario: First independently working executable
- **WHEN** A4 validates the candidate on each OS matrix row
- **THEN** all size/startup/initialization/memory/latency measurements and environment details are recorded without presenting unestablished thresholds as pass/fail requirements
