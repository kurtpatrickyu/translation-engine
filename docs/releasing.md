# Release policy and publication

This is the authoritative release policy. Assembly verifies materials and bytes;
publication requires a separate explicit maintainer approval. Research notes and
historical acceptance checklists do not themselves create release gates.

## Required distribution materials

Ship the worker ZIP, manifest/schema, SHA256SUMS, checksum verifier, usage guide,
corresponding-source ZIP and compliance ZIP together. Preserve original licenses,
copyrights and notices. Supply MiniSBD AGPL corresponding source and applicable
tqdm MPL source alongside the executable at no extra charge, with access for as
long as the binary is offered. See [source availability](../SOURCE_AVAILABILITY.md)
and [third-party notices](../THIRD_PARTY_NOTICES.md).

The binary source is b064e29517fb793b2fcf0bf309b6fc78f623367d. The source ZIP's
repository/ contains that commit; sources/worker/ and evidence/build.json retain
original build inputs. assembly/ contains later release tooling and documentation.
SOURCE_COMMIT.json binds the original source, build hashes and planned delivery
URL. The release tag must preserve or clearly identify those inputs. Do not claim
the unchanged executable was rebuilt from newer documentation.

No translation model, MiniSBD ONNX model or Microsoft installer is distributed.
The official Microsoft VC++ v14 x64 runtime is an external prerequisite. The
packaged worker needs no system Python. Follow [README](../README.md).

## What blocks publication

Missing or mismatched artifacts, required licenses/notices or applicable source;
inconsistent source/build identity; demonstrated incompatible redistribution;
material permission questions without an evidence-backed disposition; and missing
explicit approval block publication. Verification failures return exit 1.

Compiler revisions, upstream binary BOM mapping and open-ended provenance research
are informational unless tied to a specific applicable obligation. Classifications
and rationale are retained in packaging/compliance-inventory.json, alongside the
original findings. Finding counts never determine readiness.

Current material decisions, recorded once here:

- Intel OpenMP: establish the redistribution grant and required notices, and
  compatibility with the bundled MiniSBD AGPL code.
- NumPy's wheel-local renamed MSVC DLL: establish downstream redistribution
  entitlement and applicable repair/renaming conditions.
- OpenBLAS's GCC runtime: establish exception eligibility and any resulting
  covered-source delivery duties.

These are unresolved interpretations, not demonstrated prohibitions. No specific
missing mandatory material is identified by the current pinned-material check.
An adequate disposition needs the reviewer, rationale and hash-pinned supporting
evidence in the relevant release_review entry: disposition has outcome permitted
or prohibited, reviewer, rationale and evidence entries with path and sha256.
A prohibited outcome always blocks. A blocking finding must actually be remedied
and reclassified with evidence; approval cannot waive it. No permission or legal
clearance is inferred from a successful assembly or an approval record.

## Platform evidence for v0.1.0

Windows 10 x64 clean-VM core smoke validation passed with limitations; retain the
[original transcript](evidence/windows10-rc1-cmd-2026-11-08.txt). Full machine/runtime
inventory, OS-denied networking, broader error/relocation coverage and target
performance measurements were not completed. These are disclosed limitations,
not claimed passes or additional mandatory test matrices for this release.
Windows 11 is **expected compatible, UNTESTED**; separate acceptance is explicitly
deferred for v0.1.0. Development-host native isolation findings are not clean-VM
results. Retain original diagnostics without copying host-injected modules.

## Prepare, verify and approve

Run from the repository root in Windows CMD with Node.js 22+. Use fresh output
directories; preserve existing candidates unchanged. Retained build/dist inputs,
cached sources and original supplier files are required; a fresh checkout lacks
them. Historical documentation pins resolve only through
packaging/sources/candidate-documentation/. Runtime/spec/lock pins are unchanged.

After recording any required dispositions, stage a new materials directory:

```bat
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
node scripts\stage_compliance.cjs candidate-staging\NEW-materials
```

Staging exit 0 means verified materials with no mandatory blocker; exit 2 means
valid materials with a mandatory requirement still unmet. Neither means approval.
Bind that directory and its manifest SHA-256 in packaging/release-candidate.json,
then assemble and check a fresh directory. The current review set is
candidate-staging/worker-0.1.0-policy/:

```bat
node scripts\assemble_release.cjs candidate-staging\NEW-worker
node scripts\assemble_release.cjs --check candidate-staging\worker-0.1.0-policy
powershell.exe -NoProfile -ExecutionPolicy Bypass -File candidate-staging\worker-0.1.0-policy\verify-checksums.ps1
```

Assembly/check exit 0 establishes technical validity even with disclosed findings.
The checksum verifier reports integrity only. Review the manifest, source identity
and mandatory decisions, then explicitly approve with your own name:

```bat
node scripts\assemble_release.cjs --approve candidate-staging\worker-0.1.0-policy --maintainer "Your name"
node scripts\assemble_release.cjs --verify-approved candidate-staging\worker-0.1.0-policy
```

Approval rechecks all mandatory requirements and writes the adjacent
worker-0.1.0-policy.approval.json audit record without altering the eight assets.
It binds every asset hash, source/executable identity, inventory and assembly
inputs. Verification rejects missing, stale or ineligible approval. Keep the
record with maintainer release evidence; it is an explicit declaration, not a
cryptographic signature or a finding that every legal question was proven clear.
The packaged manifest remains prepared-release with release_ready:false;
--verify-approved is the authority for the separate approved release_ready state.
Changes to release inputs require fresh assembly and fresh approval.

## Publish the approved set

Review and commit only the release changes on development first. Stop on a dirty
working tree, failed command, conflict or existing v0.1.0 tag. After approval:

```bat
git switch development
git status --short
node scripts\assemble_release.cjs --verify-approved candidate-staging\worker-0.1.0-policy
git fetch origin
git switch main
git merge --ff-only origin/main
git merge --no-ff development -m "Release translation-engine v0.1.0"
git diff --exit-code development -- .
powershell.exe -NoProfile -ExecutionPolicy Bypass -File candidate-staging\worker-0.1.0-policy\verify-checksums.ps1
git tag -a v0.1.0 -m "translation-engine v0.1.0; binary source b064e29517fb793b2fcf0bf309b6fc78f623367d"
git push origin main
git push origin v0.1.0
```

On GitHub, draft a release for existing tag v0.1.0 and upload all eight files
from the approved directory. Identify the adjacent corresponding-source and
compliance assets, external VC prerequisite and separate model acquisition.
State Windows 10 core smoke passed with limitations and Windows 11 expected
compatible, untested. Explain that the executable retains its original build
source. Review public source links before publishing. Re-download the complete
published set and verify it. Never overwrite versioned assets; issue a new version
for corrections and retain source access and prior verified assets.
