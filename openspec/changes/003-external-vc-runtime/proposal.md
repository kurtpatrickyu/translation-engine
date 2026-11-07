## Why

The working standalone worker currently bundles four ordinary Microsoft VC++ DLLs collected from System32. Use the approved official x64 Redistributable prerequisite while preserving the existing Argos/MiniSBD worker, protocol and ZIP workflow.

## What Changes

- **BREAKING deployment prerequisite:** new candidates require Microsoft's officially installed Visual C++ v14 x64 Redistributable. Recommend the latest supported package at `https://aka.ms/vc14/vc_redist.x64.exe`; do not bundle the installer or download/install anything during startup.
- Exclude only the exact, case-insensitive ordinary basenames `msvcp140.dll`, `msvcp140_1.dll`, `vcruntime140.dll`, and `vcruntime140_1.dll` from the post-Analysis binary collection. Retain NumPy's renamed DLL and all other required dependencies unchanged.
- Add one focused packaging policy test and verify the complete candidate onedir and ZIP. Reuse existing native inspection and regression tools with only the small adjustments needed to recognize the external runtime and verify its actual load paths and startup outcome.
- Treat 14.50.35719.0 as a provisional conservative candidate, not a proven minimum. Determine the documented runtime requirement from available toolset evidence and the official runtime actually tested; do not acquire a historical installer solely to test that provisional number.
- Use six tasks in three reviewable groups: A, packaging/test/prerequisite documentation; B, one monitored candidate build and focused regression; C, remaining PUBLIC clean Windows 10/11 acceptance. Exhaustive older/newer/x86-only prerequisite matrices are deferred unless a concrete issue warrants them.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `windows-worker-distribution`: exact exclusion/retention boundary, external prerequisite, focused candidate verification and separate public clean-machine gate.
- `release-artifacts`: prerequisite instructions and continued compliance obligations for materials actually bundled.

These deltas extend the active `001-build-offline-translation-engine` baseline. Preserve its Level A completion record (37/37) and successful diagnostic/manual evidence. Resolve these deltas against `001` during eventual archival; unrelated nested specs or MiniSBD-replacement material are not the baseline for this change.

## Impact

Expected implementation edits are limited to `packaging/worker.spec`, a focused packaging policy test, small verification adjustments to `scripts/build_windows.py`, `scripts/audit_windows_package.py` or `scripts/validate_windows.py` only where needed, and prerequisite/candidate notes in `docs/native-dependencies.md`, `docs/manual-usage.md` and directly linked build/usage documentation. Update the relevant Microsoft deployment statements in `docs/redistribution-review.md` and `docs/compliance-staging.md` without reopening the broader review.

Candidate-specific compliance inventory rebinding, AGPL source delivery, license notices, Intel OpenMP rights and other actual redistribution obligations remain separate existing PUBLIC release work. Do not weaken them or add a compliance framework to 003. Old candidate bindings remain accurate until that release work binds a new candidate.

No dependency/lock, Argos, MiniSBD, translation, model/ONNX hash, provisioning/rollback, offline inference, NDJSON v1 or Freya changes are included. This revision changes planning artifacts only; no build, implementation or publication is performed.