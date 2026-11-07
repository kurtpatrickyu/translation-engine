## Context

See `proposal.md` for scope. The baseline is active `001-build-offline-translation-engine`, with Level A complete at 37/37. Preserve its tasks, diagnostic artifact and regression/manual evidence. Current artifact: `dist/diagnostic-20261107-133601/translation-engine-worker/`; existing static/runtime reports are in `build/diagnostic-20261107-133601/` and described in `docs/native-dependencies.md`.

The earlier read-only verification matched the four ordinary DLLs at version 14.50.35719.0 against the retained static audit. NumPy's separate `numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` is version 14.40.33810.0. NumPy's core and FFT extensions import that hashed filename directly, so the ordinary system DLL cannot replace it without wheel changes. Retain its exact name and bytes. Use the existing audit for full identities rather than duplicating an inventory here.

## Goals / Non-Goals

**Goals:** exclude only the four ordinary DLLs, explain the official prerequisite, and verify one candidate using existing tooling.

**Non-Goals:** dependency or translation changes, a prerequisite manager, a new native/licensing framework, exhaustive prerequisite matrices, Freya integration or publication. AGPL source/notices and all actual bundled-native rights remain separate existing PUBLIC release obligations.

## Decisions

### A. Packaging and prerequisite documentation

Immediately after `Analysis(...)` in `packaging/worker.spec`, before `PYZ`/`EXE`/`COLLECT`, use this exact destination-basename filter:

```python
external_vc = {'msvcp140.dll', 'msvcp140_1.dll',
               'vcruntime140.dll', 'vcruntime140_1.dll'}
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.casefold() not in external_vc]
```

The Windows build already imports `Path`. Preserve existing metadata, hooks and framework exclusions. Broad prefix/glob filters or module exclusions could remove NumPy's renamed DLL or unrelated native files and are unsuitable. One focused packaging policy test must exercise the actual filter with mixed-case/subdirectory names and representative retained files, including the hashed NumPy DLL. No general dependency test framework is needed.

Document the **latest supported official Microsoft Visual C++ v14 x64 Redistributable**, using <https://aka.ms/vc14/vc_redist.x64.exe>. Users install it separately if needed, obtain model/ONNX assets upstream, provision locally and run the frozen worker offline without Python. Offline users can transfer their separately obtained Microsoft installer. The project does not redistribute that installer, and startup never downloads or installs prerequisites.

Microsoft requires the runtime to match the application's architecture and be at least as recent as the newest MSVC build tools used by its components. See [supported downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) and [binary compatibility](https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017?view=msvc-170), checked 2026-11-07. **14.50.35719.0 is a provisional conservative candidate, not a proven minimum or mandatory historical test target.** Existing DLL versions show what worked locally, not every component's compiler identity; installed ONNX package metadata does not establish its toolset.

Use available supplier/toolset evidence and the official runtime actually exercised in B/C to document a supportable requirement and exact tested version(s). If evidence does not establish a lowest numeric minimum, state that plainly, recommend the latest supported official x64 runtime, and limit compatibility claims to tested runtimes/environments. Do not invent a lower bound, require complete reconstruction of every wheel's build history, or acquire a historical installer solely to test 14.50.35719.0. A known newer toolset requirement must be satisfied before candidate acceptance. Compatible newer installations need no downgrade; an arbitrary old v14 or x86-only installation is not sufficient evidence.

Missing/broken runtimes may cause Windows/PyInstaller to fail before Python/NDJSON initialization. Document the observed or representative loader failure and manual install/update/repair remedy through Microsoft. Preserve error/exit/timeout details if encountered; failed startup or absence of health is never success. No custom launcher, production registry detector or mandatory missing-runtime VM experiment is added.

### B. One candidate build and focused regression

After A's packaging change and focused policy test pass, run `scripts/build_windows.py` once with its existing monitoring into fresh build/dist paths. Retain logs and failures; no silent rebuild loop. Verify the complete extracted onedir and ZIP: identical file sets and bytes, the four ordinary names absent recursively, NumPy's hashed DLL unchanged, and all other required native files retained with baseline hashes. The generated EXE may change. No installer or model/ONNX binary may appear. Reuse existing inventory/ZIP checks; a small post-build assertion is sufficient.

Reuse `scripts/audit_windows_package.py` and `scripts/validate_windows.py`, with only necessary changes to recognize those four explicitly external imports and check the loaded module paths against the installed Microsoft runtime. Do not classify VC as an unconditional Windows OS dependency. Existing import inspection plus successful provisioning/inference and module snapshots establish resolution; no new registry/version-state engine, expanded export auditor or prerequisite matrix is required. Record installed runtime versions and paths, retain NumPy's bundle origin, and keep unknown DLLs or unexpected injected modules visible. Preserve the existing Teruten isolation finding as a host limitation; functional success does not certify clean isolation.

Run the existing version/startup, provisioning, ready-health, real Chinese-English corpus/output comparison, persistent NDJSON/error-recovery/shutdown and Unicode model/executable/state checks, including combined relocation. Preserve original model/ONNX hashes, protocol behavior and provisioning integrity/rollback. Minimal child environment/PATH checks provide local independence evidence; clean no-system-Python acceptance belongs to C. Reuse existing reports and manual procedures, rather than creating another regression harness.

Do not rebind `packaging/compliance-inventory.json` to guessed candidate identities. Its old candidate bindings and staging evidence stay accurate. New-candidate compliance rebinding remains with the existing PUBLIC release preparation tasks; it is not a prerequisite to this focused diagnostic build/regression.

### C. Remaining public clean-machine acceptance

Keep clean Windows 10 22H2 x64 and Windows 11 x64 acceptance explicitly pending until both execute the same candidate ZIP/model/ONNX hashes with a compatible official x64 runtime, no system Python/global Argos and OS networking disabled. Reuse existing `001` PUBLIC checks and measurement requirements; do not duplicate or weaken them. Python audit scripts stay on the maintainer side; target checks use the frozen EXE and existing CMD/PowerShell procedures/module inspection, without installing Python.

Record actual OS/runtime versions, native origins and results. Do not claim untested environments are supported. Exhaustive older/newer/x86-only or missing-runtime matrices are deferred unless a concrete loader, version or compatibility issue warrants a targeted additional check. Documentation still covers missing-runtime failure/remediation and compatible newer installations.

## Risks / Trade-offs

- [A filter removes too much or a hook recollects VC] -> one focused policy test plus complete onedir/ZIP verification and retained-native hash comparison.
- [A development host masks a runtime dependency] -> actual installed-runtime load paths and separate clean Windows PUBLIC acceptance.
- [An unsupported minimum is claimed] -> distinguish provisional 14.50.35719.0 from available toolset evidence and actual tested versions; recommend the latest supported official package.
- [Startup fails before Python] -> document install/repair instructions and retain failure details; no false readiness claim.
- [External VC is mistaken for compliance clearance] -> NumPy's renamed DLL, Intel OpenMP, AGPL source/notices and all other actual bundled-material gates remain separate and mandatory.

## Migration Plan

Review A, B and C independently. A/B produce a locally verified candidate; C remains a PUBLIC release gate. Preserve the old successful artifact and all existing regression evidence, using new paths for candidate reports. Leave `001` Level A records unchanged. On failure retain evidence and resolve the concrete cause without changing pins/assets or broadening the architecture. Reverting the packaging change is a local diagnostic rollback, not permission to publish the old bundle. No part of this plan authorizes publication or Freya changes.