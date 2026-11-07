# Local Windows release candidate results

Candidate `0.1.0-rc.1`, assembled 2026-11-07. This implements local artifact
assembly/integrity and consumer instructions, not publication or clean-machine
acceptance. No PyInstaller rebuild, backend change, dependency upgrade, model
download/modification, Git tag or GitHub Release occurred.

Final directory: `candidate-staging/worker-0.1.0-rc.1-final/`.
Independent repeat: `candidate-staging/worker-0.1.0-rc.1-final-repeat/`.
Earlier local attempts are preserved; use these final directories for acceptance.
The directory contains exactly eight files. All are byte-identical between the
two final assemblies. `SHA256SUMS` covers the other seven, including the manifest.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| translation-engine-worker-win-x64.zip | 58,819,680 | `708add4798814b8e7d2298ad36ae9697368afa639a4ae6ea99e391f4457fb28d` |
| translation-engine-compliance.zip | 4,948,689 | `f2df07332ae992abc10003dcf0924dd49b5cf26bb4162c8be83ee30789690df3` |
| translation-engine-corresponding-source.zip | 4,855,013 | `5e1e5edbc134f0659de8c8d3ce178cb64f513edea37aa152e6e213c3a8afdcc3` |
| manifest.json | 72,480 | `c3451790abf20551e470048a417d0653a6802a055ee3d382151c26029d02cb5f` |
| manifest.schema.json | 4,040 | `77759d970a18390182be5d06cbacbec5769db64b862435e4982458ab2b2bff60` |
| WINDOWS-CANDIDATE.md | 7,021 | `77d8d3cbd779ad8496d765f2a731dc984415a9d5a74a7ac59dd2c4e7dc32e0d3` |
| verify-checksums.ps1 | 1,804 | `530a6114e058549febe79173e7dc201a8bb1694f3e0207d6b5bb8cad0dfeac91` |
| SHA256SUMS | 655 | Not self-covered; obtain from the trusted candidate dossier. |

The actual example is checked in as `packaging/release-manifest.example.json`.
The schema intentionally represents a local candidate: tag/release URL are null
and release readiness is false. It does not invent a public download URL. Public
tag-specific URL binding remains task 5.1 acceptance work.

## Source and baseline identity

Worker source commit: `b064e29517fb793b2fcf0bf309b6fc78f623367d`.
Prepared licensing materials commit: `6faf8a8d40713e7f5bafb787a2e900b104995ddb`.
The assembler verifies original byte-pinned build inputs and Git correspondence
for runtime/build files, and rejects a source commit mismatch. The source archive
contains the binary commit's source snapshot, exact staged build inputs, matching
third-party preferred sources and source-commit metadata. The current assembly
tool/config/schema/instructions are included separately under `assembly/` and
hashed in the manifest; they are not claimed to belong to the older binary commit.

Baseline is `diagnostic-20261107-211131`, with 176 original files and 49 native
binaries. Executable SHA-256 remains
`ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
The old diagnostic ZIP hash is retained only as baseline evidence; it is not
the new release-candidate ZIP hash.

The worker ZIP preserves all original onedir bytes and adds 62 files under
`release-info/`: original licenses/notices, source availability, retained blockers
and build/protocol/usage instructions. No ordinary VC++ DLL is reintroduced;
NumPy's renamed DLL and every other original native file remain unchanged.
No external model, model cache, download directory, virtual environment or raw
runtime log is included. The compliance ZIP retains the existing prepared
build/static/source evidence dossier, rather than copying runtime directories.

## Verification

- 24 focused Node tests pass, covering deterministic ZIP metadata/CRC, complete
  original payload coverage, hashes, source identity, external asset exclusions,
  required materials, excluded VC DLLs and missing/tampered inputs/outputs.
- Final assembly and `--check` pass. The existing compliance stager's expected
  exit code remains 2; the assembler returns 0 for a valid local candidate.
- Independent final assembly matches all eight files byte for byte.
- The Windows PowerShell checksum verifier passes on the final candidate.
- Inbox Windows `tar.exe` extracts the worker ZIP. All 238 extracted files match
  the manifest; the extracted executable's `--version` returns `0.1.0` and exits 0.
- Four existing Unicode regressions and the native functional regression are
  pinned to the same executable/diagnostic ZIP and external model hashes.
  The native report's overall strict-isolation failure from Teruten host modules
  is preserved separately from its successful functional smoke.

## Pending publication and next acceptance step

The existing 19 compliance/source-delivery blockers remain in the compliance
archive. Intel/native redistribution terms, NumPy's renamed Microsoft DLL rights,
remaining source/license mappings, final immutable public source delivery,
both clean Windows rows, OS-denied networking, complete target measurements and
explicit publication approval remain pending. No permission or platform support
is declared cleared by assembly.

Transfer the complete final eight-file directory and separately user-acquired,
hash-verified external assets to clean Windows 10 22H2 x64 and Windows 11 x64
environments with no Python/global Argos. Follow
[the candidate CMD instructions](windows-release-candidate.md): verify checksums,
install/check the separately acquired official x64 VC++ runtime, deny networking
at the OS level, extract/provision and run the smoke. Then record the existing
protocol/Unicode/failure/native-origin and complete measurement checks against
the same ZIP/model hashes on both rows. These clean-machine tasks were not run
on this development host.

Task 5.2 is mechanically complete; overall progress is 38/54 (LOCAL 37/37,
PUBLIC 1/17). Tasks 4.4b, 5.1 and 5.9 have explicit local progress notes and remain
unchecked for their remaining public acceptance criteria. Other tasks are unchanged.
