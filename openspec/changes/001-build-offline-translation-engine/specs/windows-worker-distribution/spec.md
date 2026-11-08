## Purpose

Deliver a standalone Windows x64 worker whose runtime and external model behavior can be verified independently of developer installations.

## ADDED Requirements

### Requirement: Distinct local and public completion levels
Level A SHALL mean a locally usable, manually testable worker: passed source/real-model integration, verified local provisioning/integrity/failure safety, Python network-attempt checks with declared coverage limits, a working frozen onedir/diagnostic ZIP, host-local relocation and technical native inventory, recorded local measurements, and a manual usage guide with a completed manual test session. Level B SHALL mean a publicly redistributable Windows release: Level A plus clean support/isolation evidence for the mandatory release target, complete target measurements, compliant bundled code/native redistribution, final worker-only integrity/compliance assets, consumer documentation and explicit publication approval. For initial v0.1.0, Windows 10 22H2 x64 SHALL be the mandatory target; the maintainer's 2026-11-08 waiver SHALL make Windows 11 validation optional and SHALL NOT count as a test pass. Pending Level B evidence SHALL NOT block Level A completion, manual testing, or documentation. Local completion SHALL NOT imply OS support or legal clearance.

#### Scenario: Technical worker is ready for manual testing
- **WHEN** local technical checks pass but the manual guide/walkthrough is not yet recorded
- **THEN** the worker is available for manual testing while Level A sign-off stays pending only its remaining local tasks, independently of Level B gates

#### Scenario: Externally loaded development-host modules
- **WHEN** native audit observes external Teruten modules absent from the bundle and static imports
- **THEN** strict isolation findings remain recorded as host limitations, not proven application dependencies or automatic local functionality failures; clean OS certification remains pending and security software is not modified

### Requirement: Standalone onedir artifact
A Windows x64 build SHALL produce a complete onedir application with `translation-engine-worker.exe`, Python runtime, required native dependencies and metadata, plus a hash-verified diagnostic ZIP for local testing. The public `translation-engine-worker-win-x64.zip` SHALL additionally include reviewed notices/compliance materials. Archives SHALL exclude `.argosmodel` and MiniSBD ONNX model binaries and SHALL require neither system Python, a development `.venv`, a global Argos installation, nor GPU software on the target. Builds SHALL run on Windows from locked inputs; native collection provenance SHALL be recorded separately from Python locks. Users SHALL obtain external assets directly from upstream and provision through the existing local CLI without automatic worker downloads.

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
The v0.1.0 acceptance matrix SHALL include mandatory Windows 10 22H2 x64 CPU and optional Windows 11 x64 compatibility validation. Windows 10 SHALL identify exact tested edition/version/build and validate the pinned runtime/model graph and actual onedir artifact. Windows 11 SHALL be described as expected compatible but UNTESTED until actual evidence exists; it SHALL NOT block initial v0.1.0 release. Optional future Windows 11 validation SHALL use the same exact worker ZIP/model/ONNX hashes when comparing this candidate; OS-specific rebuilds or substituted models SHALL NOT count as validation of these bytes. Validated compatibility claims SHALL be limited to tested rows/builds. The explicit 2026-11-08 maintainer waiver is a version-limited scope amendment, not evidence of incompatibility or authority to waive other gates. Later release scope SHALL be reviewed separately; inability to access a test image SHALL NOT prove incompatibility.

#### Scenario: Windows 11 acceptance waived for initial release
- **WHEN** v0.1.0 is reviewed under the explicit maintainer waiver and no Windows 11 result exists
- **THEN** Windows 11 remains expected compatible but UNTESTED, its validation is optional future work, and only the remaining mandatory v0.1.0 gates block publication

#### Scenario: Windows 10 smoke is partial
- **WHEN** Windows 10 build 19045.3803 passes the recorded core smoke after resolving the VC++ prerequisite
- **THEN** its existing evidence and initial loader failure are preserved, and missing network-isolation, relocation, native-origin, broader protocol/resource and measurement criteria remain required rather than inferred passed

#### Scenario: Operating system limitation is demonstrated
- **WHEN** the unchanged pinned graph or packaged executable fails on a candidate OS
- **THEN** the failing build/dependency and diagnostic evidence are recorded before support or version changes are proposed

### Requirement: Clean Windows acceptance evidence
For initial v0.1.0, Level B public Windows release acceptance SHALL require evidence that the actual packaged executable provisions externally obtained model/ONNX files and translates on clean Windows 10 22H2 x64 using the exact candidate worker ZIP/model/ONNX hashes, with no system Python, no global Argos, the documented official external VC++ x64 prerequisite and network access disabled. Evidence SHALL identify OS, CPU, release commit, checksums, commands, network controls, installed runtime version, native load origins and results. Separate Windows 11 acceptance SHALL be waived for v0.1.0 only and SHALL remain optional future validation, never a presumed pass. Mocked tests and hosted runner smoke tests SHALL NOT be represented as clean-machine proof. These requirements SHALL NOT gate Level A manual use, local documentation or technical completion.

#### Scenario: Required Windows 10 acceptance
- **WHEN** the candidate is tested on clean Windows 10 22H2 x64 for v0.1.0
- **THEN** evidence records exact ZIP/model/ONNX hashes and successful local provisioning and repeated offline translation without system Python or global Argos, independently of optional Windows 11 validation

#### Scenario: Clean verification unavailable
- **WHEN** required Windows 10 clean verification is missing or incomplete
- **THEN** Level B acceptance/publication remains pending, while Level A testing/documentation/completion can proceed using host-local evidence with its stated limitations

### Requirement: Packaging performance baseline
Level A SHALL record a local diagnostic baseline: worker ZIP/extracted bytes, fresh-process launch to uninitialized info, model/SBD initialization/warm-up, idle/ready/observed peak working set/private bytes, repeated warmed latency, and separate external model sizes. Evidence SHALL bind artifact/model hashes, known host/CPU/RAM/settings/corpus/cache/sample conditions and raw results; unavailable storage/power/cache-cold information SHALL be explicit limitations, not fabricated completeness. This local baseline SHALL NOT require clean target images. Level B SHALL additionally require complete mandatory-target OS/build, CPU, RAM, storage/VM allocation, power/settings, measurement methods, cache conditions, corpus/input sizes, repetitions, raw observations and summary statistics. For v0.1.0 these target measurements SHALL remain mandatory on Windows 10; Windows 11 measurements SHALL be optional with its waived acceptance test. Neither level SHALL invent performance budgets before reviewing a baseline.

Approved diagnostic builds SHALL additionally capture build-process-tree memory and system commit/available memory separately from runtime inference measurements. Source-level module absence alone SHALL NOT establish build memory savings, runtime memory reduction, or executable size.

#### Scenario: First independently working executable
- **WHEN** A4 validates the candidate on the mandatory release target
- **THEN** all size/startup/initialization/memory/latency measurements and environment details are recorded without presenting unestablished thresholds as pass/fail requirements

#### Scenario: Limited local baseline already exists
- **WHEN** local diagnostic reports bind measured size/time/memory/latency to identified artifacts while storage/power or target details remain unrecorded
- **THEN** the local measurement task can complete with those limitations and the clean-target measurement task stays pending
