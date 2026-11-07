## MODIFIED Requirements

### Requirement: Standalone onedir artifact
A Windows x64 build SHALL produce a complete onedir application with `translation-engine-worker.exe`, bundled Python runtime, required bundled native dependencies and metadata, plus a hash-verified diagnostic ZIP for local testing. New candidates under this change SHALL use the officially installed Microsoft Visual C++ v14 x64 Redistributable as an external prerequisite for the ordinary `msvcp140.dll`, `msvcp140_1.dll`, `vcruntime140.dll`, and `vcruntime140_1.dll` imports; those exact basenames SHALL be absent throughout the onedir and ZIP, case-insensitively. Other required native dependencies SHALL remain intact. The public `translation-engine-worker-win-x64.zip` SHALL additionally include reviewed notices/compliance materials. Archives SHALL exclude `.argosmodel` and MiniSBD ONNX model binaries and SHALL require neither system Python, a development `.venv`, a global Argos installation, nor GPU software on the target. Builds SHALL run on Windows from locked inputs; native collection provenance and the external prerequisite contract SHALL be recorded separately from Python locks. Users SHALL obtain external assets directly from upstream and provision through the existing local CLI without automatic worker downloads. The Microsoft installer SHALL NOT be bundled or redistributed by the project, and worker startup SHALL NOT download or install prerequisites.

#### Scenario: Relocated artifact
- **WHEN** the complete archive is extracted to a different directory including spaces and Unicode characters on a machine satisfying the documented x64 prerequisite
- **THEN** the executable starts using its bundled Python runtime, installed ordinary VC runtime and explicitly configured external models

Unicode model, executable, and writable state directories SHALL also be tested independently, then together, to expose distinct native path dependencies. Each check SHALL use the unchanged model/SBD bytes and exercise production provisioning, readiness, repeated translation, integrity failures, stdout purity, and shutdown. Local diagnostic evidence SHALL remain distinct from clean OS acceptance.

#### Scenario: Approved optional-dependency runtime candidate
- **WHEN** an approved source-pinned Argos candidate passes source-level MiniSBD inference without Stanza/Torch
- **THEN** reduced frozen collection is independently checked for complete required runtime/DLL resources, metadata, stdout purity, startup and relocated provisioning; absent unused SBD frameworks do not justify skipping packaged acceptance

#### Scenario: Exact native exclusion boundary
- **WHEN** the new candidate's onedir and ZIP are inventoried
- **THEN** the four ordinary runtime basenames are absent, NumPy's `numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` remains unchanged, and required Python, CTranslate2, ONNX Runtime, SentencePiece, Intel OpenMP, NumPy/OpenBLAS and other native files remain present with their established identities

### Requirement: Clean Windows acceptance evidence
Level B public Windows support/release acceptance SHALL require evidence that the actual packaged executable provisions externally obtained model/ONNX files and translates on both clean Windows 10 22H2 x64 and clean Windows 11 x64 using the same exact worker ZIP/model/ONNX hashes, with no system Python, no global Argos, a compatible official Microsoft VC++ x64 Redistributable installed, and network access disabled. Evidence SHALL identify OS, CPU, release commit, checksums, commands, network controls, installed runtime version, native load origins and results for each row. Mocked tests and hosted runner smoke tests SHALL NOT be represented as clean-machine proof. These requirements SHALL NOT gate Level A manual use, local documentation or technical completion. Historical Level A completion and diagnostic/manual results SHALL remain unchanged and SHALL NOT be substituted for acceptance of the changed candidate.

#### Scenario: Shared artifact passes both clean operating systems
- **WHEN** the same candidate worker ZIP and model are tested on clean Windows 10 22H2 x64 and Windows 11 x64 with a compatible official x64 runtime
- **THEN** each row records matching ZIP/model/ONNX SHA-256 hashes, actual installed ordinary VC module origins, successful local provisioning, `health` with `ready=true`, and repeated offline translation without system Python or global Argos

#### Scenario: Clean verification unavailable
- **WHEN** clean Windows verification has not run
- **THEN** Level B acceptance/publication remains pending, while Level A testing/documentation/completion can proceed using host-local evidence with its stated limitations

#### Scenario: Regression comparison
- **WHEN** the changed candidate is validated against the retained baseline
- **THEN** Chinese-English outputs match the baseline corpus exactly and repeated requests, error recovery, independent and combined Unicode paths, provisioning integrity/rollback, NDJSON v1 stdout purity, and shutdown still pass with unchanged model and ONNX hashes

## ADDED Requirements

### Requirement: Official external Microsoft runtime prerequisite
The candidate SHALL require Microsoft's officially installed Visual C++ v14 x64 Redistributable and recommend the latest supported official package at `https://aka.ms/vc14/vc_redist.x64.exe`. The documented version requirement SHALL reflect available component-toolset evidence and the official runtimes actually tested. Version 14.50.35719.0 SHALL remain a provisional conservative candidate, not a proven minimum. The runtime SHALL satisfy known toolset requirements; where a lowest numeric minimum is not established, documentation SHALL say so and identify tested versions instead of asserting one. Historical installer acquisition solely to test the provisional number SHALL NOT be required. Compatible newer installations SHALL NOT require downgrade or forced reinstallation.

#### Scenario: A candidate is tested with a supported official runtime
- **WHEN** validation records the installed official x64 runtime and available toolset evidence
- **THEN** documentation states a supportable requirement, exact tested version and remaining compatibility limits without claiming the provisional DLL version proves the minimum

### Requirement: Focused runtime resolution and startup verification
Candidate verification SHALL reuse existing tools to confirm that required ordinary VC imports resolve from the installed Microsoft runtime, NumPy's renamed DLL remains bundled unchanged, and no other required native dependencies were removed. Complete onedir/ZIP verification SHALL confirm matching file sets and bytes and the exact exclusion boundary. One focused packaging policy test SHALL guard that boundary. Unknown native dependencies and unexpected loaded host modules SHALL remain visible in audit results; local functional success SHALL NOT certify clean isolation.

Startup failure SHALL NOT be reported as success or readiness. Documentation SHALL explain that a missing/broken runtime can fail before Python/NDJSON initializes and direct users to install/update/repair the official x64 Redistributable manually. Available failure details SHALL be retained without requiring a protocol response before initialization. Exhaustive missing/older/newer/x86-only prerequisite matrices SHALL be deferred unless a concrete compatibility issue requires a targeted check; this deferral SHALL NOT replace clean Windows PUBLIC acceptance.

#### Scenario: Successful external runtime loading
- **WHEN** the candidate starts, provisions models, reaches ready health and performs repeated translation
- **THEN** existing native inspection records ordinary VC DLLs from the installed Microsoft runtime and the unchanged hashed NumPy DLL from the bundle, with no unexpected removal of other required native files

#### Scenario: Startup does not complete
- **WHEN** startup encounters a loader error, exits early or times out without successful initialization
- **THEN** verification records a failed startup with available diagnostics and no successful readiness claim; documentation provides the official prerequisite installation/repair remedy
