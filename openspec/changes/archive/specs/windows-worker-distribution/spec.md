## MODIFIED Requirements

### Requirement: Standalone onedir artifact
A Windows x64 candidate build SHALL produce a complete onedir application with `translation-engine-worker.exe`, Python runtime, required native dependencies and metadata, plus a hash-verified diagnostic ZIP for local testing. The public `translation-engine-worker-win-x64.zip` SHALL additionally include reviewed notices/compliance materials. Archives SHALL exclude translation and sentence-boundary model binaries and SHALL require neither system Python, a development `.venv`, a global Argos installation, MiniSBD, a sentence-boundary neural runtime nor GPU software on the target. Builds SHALL run on Windows from locked inputs; native collection provenance SHALL be recorded separately from Python locks. Users SHALL obtain the unchanged external translation archive directly from upstream and provision through the explicit local CLI without automatic worker downloads.

Unicode model, executable and writable state directories SHALL be tested independently, then together, to expose distinct native path dependencies. Each check SHALL use the unchanged translation archive and candidate receipt/layout and exercise production provisioning, readiness, repeated translation, integrity failures, stdout purity and shutdown. Local diagnostic evidence SHALL remain distinct from clean OS acceptance.

#### Scenario: Relocated artifact
- **WHEN** the complete archive is extracted to a different directory including spaces and Unicode characters
- **THEN** the executable starts using its bundled runtime and explicitly configured external models

#### Scenario: Approved dependency and segmentation candidate
- **WHEN** an explicitly source/patch-pinned Argos candidate passes source-level inference without MiniSBD/Stanza/Torch
- **THEN** reduced frozen collection is independently checked for complete required runtime/DLL resources, truthful metadata, stdout purity, startup and relocated model-only provisioning; absent source dependencies do not justify skipping packaged acceptance

### Requirement: Clean Windows acceptance evidence
Level B public Windows support/release acceptance SHALL require evidence that the actual packaged candidate executable provisions the externally obtained unchanged translation archive and translates on both clean Windows 10 22H2 x64 and clean Windows 11 x64 using the same exact worker ZIP/model hashes and candidate installation policy, with no system Python, no global Argos, no MiniSBD/ONNX requirement and network access disabled. Evidence SHALL identify OS, CPU, release commit, checksums, commands, network controls, native load origins and results for each row. Mocked tests and hosted runner smoke tests SHALL NOT be represented as clean-machine proof. These requirements SHALL NOT gate Level A manual use, local documentation or technical completion. The replacement SHALL obtain its own evidence without rewriting the baseline's completed Level A results.

#### Scenario: Shared artifact passes both clean operating systems
- **WHEN** the same candidate worker ZIP and model are tested on clean Windows 10 22H2 x64 and Windows 11 x64
- **THEN** each row records matching ZIP/model SHA-256 hashes and successful local model-only provisioning and repeated offline translation without system Python or global Argos

#### Scenario: Clean verification unavailable
- **WHEN** clean Windows verification has not run for the replacement candidate
- **THEN** Level B acceptance/publication remains pending, while Level A testing/documentation/completion can proceed using candidate-specific host-local evidence with its stated limitations

## ADDED Requirements

### Requirement: Evidence of absence of AGPL code in distributed artifacts
The candidate SHALL contain no MiniSBD or other AGPL-licensed runtime code, including unexecuted, renamed, vendored, embedded or statically incorporated code. Acceptance SHALL inspect the actual executable archives and frozen Python code, dependency archives, loose files, native binaries, embedded third-party code and all distribution files, reconciled to exact reviewed supplier/owned-source identities and grants. Build tables, package metadata, name scans and loaded-module checks SHALL NOT substitute for complete artifact reconciliation. Unknown code ownership or unresolved static license scope SHALL block an AGPL-absence claim. Identified GPL runtime exceptions SHALL remain explicitly listed and reviewed separately; the candidate SHALL NOT claim to be GPL-free or permissive-only. Any additional non-excepted GPL runtime component SHALL block adoption pending separate review.

#### Scenario: Unused MiniSBD remains frozen
- **WHEN** any executable/PYZ/loose or nested-archive entry contains MiniSBD code even though runtime tests never import it
- **THEN** artifact acceptance fails

#### Scenario: Renamed or unknown payload
- **WHEN** a Python/native/data payload lacks an approved code-ownership/license mapping or incorporates retired AGPL code under another name
- **THEN** acceptance fails or remains explicitly pending rather than treating a clean name scan as proof

#### Scenario: Final ZIP differs from audited directory
- **WHEN** the release ZIP or compliance payload includes unexpected files or differs from the audited candidate's hashes
- **THEN** acceptance fails and evidence is rebound only after the exact final contents are verified

### Requirement: Lightweight replacement evidence
The candidate SHALL add no neural segmentation model, large framework or unnecessary native dependency. It SHALL record comparable baseline/candidate ZIP/extracted sizes, initialization, working set/private bytes and warmed latency using identified hashes, host, corpus, settings and repeated sample conditions. Candidate extracted size SHALL NOT exceed the baseline; measured runtime peak SHALL NOT exceed baseline beyond observed run-to-run variation without resolving the regression before adoption. No numerical memory/size saving SHALL be claimed from dependency declarations alone.

#### Scenario: Smaller dependency graph without runtime measurements
- **WHEN** dependency removal succeeds but comparable artifact/runtime evidence is missing
- **THEN** lightweight acceptance remains pending and no measured footprint improvement is claimed
