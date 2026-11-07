## MODIFIED Requirements

### Requirement: Public bundled-component compliance
Public worker publication SHALL require evidence-backed review and fulfillment of obligations for code/binaries actually distributed: retained MiniSBD AGPLv3 combined-distribution/source/notices obligations, actual bundled Microsoft/OpenMP/native DLL redistribution rights, and other bundled components. Required corresponding source and build/install materials SHALL be supplied through a reviewed license-compliant mechanism tied to the exact worker. The four ordinary VC++ DLLs excluded from new candidates SHALL be documented as an official externally installed x64 prerequisite rather than shipped components; neither those files nor Microsoft's installer SHALL be added to release assets or compliance payloads. NumPy's retained renamed MSVCP DLL SHALL retain its separate actual-byte redistribution/repair provenance requirement. Externalizing ordinary VC++ SHALL NOT clear Intel OpenMP, NumPy/OpenBLAS, statically incorporated libraries, or other bundled-material blockers. Worker-only distribution SHALL NOT eliminate these obligations. Unknown external model terms SHALL remain recorded; future model hosting SHALL require separate clearance and SHALL NOT be a current local completion gate.

#### Scenario: Bundled MiniSBD compliance is unresolved
- **WHEN** external models are not hosted but bundled MiniSBD code obligations are unresolved
- **THEN** public publication remains blocked while local development/manual testing can proceed without a clearance claim; MiniSBD replacement is not introduced by this change

#### Scenario: Ordinary VC files are excluded but NumPy's renamed DLL remains
- **WHEN** a candidate verifies absence of the four ordinary VC files and retains the wheel-local hashed DLL
- **THEN** its inventory records that exact remaining bundled component and preserves its unresolved provenance separately; the external prerequisite is not presented as clearance for it

AGPL source delivery, license notices, Intel OpenMP rights, other actual bundled-material obligations and exact new-candidate compliance inventory binding SHALL remain separate existing PUBLIC release tasks. The focused packaging candidate SHALL NOT be represented as release-ready merely because its runtime and regressions pass. Old-candidate inventory/evidence SHALL remain accurate until release preparation binds a new candidate.

#### Scenario: Candidate compliance remains separate
- **WHEN** local packaging and regression checks pass for the changed candidate
- **THEN** existing PUBLIC source/notices/native-compliance and candidate-inventory work remains mandatory, without becoming a new compliance framework or prerequisite to the diagnostic build

## ADDED Requirements

### Requirement: ZIP prerequisite instructions and neutral consumer contract
Standalone documentation SHALL describe obtaining/extracting the worker ZIP, installing the official x64 prerequisite separately if needed, acquiring the pinned model/ONNX assets directly from upstream, provisioning locally, and running offline without target Python. It SHALL recommend the latest supported official Microsoft package at `https://aka.ms/vc14/vc_redist.x64.exe`, document a version requirement supported by available toolset evidence and tested runtimes, label 14.50.35719.0 provisional rather than a proven minimum, and explain missing/broken installation remediation, acceptance of newer compatible installations, and early loader failure diagnostics. Users MAY obtain Microsoft's installer separately for offline transfer; the worker and project release SHALL NOT redistribute or automatically acquire it.

The architecture/version/failure/download contract SHALL remain application-neutral. Freya installer integration SHALL require a separate explicitly approved change; this worker change SHALL implement no Freya installer behavior. Existing Argos revision, MiniSBD implementation, locks, model/ONNX hashes, protocol v1, offline inference, provisioning integrity/rollback and successful historical evidence SHALL remain preserved. `001` Level A completion records SHALL remain unchanged.

#### Scenario: Independent ZIP user
- **WHEN** a user follows the standalone instructions with no system Python
- **THEN** they install the official prerequisite only if needed, obtain assets upstream, provision with the frozen CLI and run the offline worker without any worker-triggered prerequisite installation

#### Scenario: Future Freya installer author
- **WHEN** a future consumer consults the prerequisite contract
- **THEN** architecture, evidence-based version guidance, compatible-newer-version acceptance and installation remedy are available without changes to Freya or the NDJSON protocol in this change
