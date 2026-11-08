# Release policy and publication

This is the authoritative release policy. Assembly verifies materials and bytes;
publication requires a separate explicit maintainer approval. Research notes and
historical acceptance checklists do not themselves create release gates.

For v0.1.0, the maintainer directed on 2026-11-08 that remaining testing,
missing acceptance artifacts, provenance research and the two unresolved
permission reviews be deferred until after release. These are disclosed open
items, not completed tests or established redistribution permissions. The
deferral applies only to v0.1.0 and must be reassessed before the next release.

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
non-deferred material permission questions without an evidence-backed disposition;
and missing explicit approval block publication. Verification failures return exit 1.

Compiler revisions, upstream binary BOM mapping and open-ended provenance research
are informational unless tied to a specific applicable obligation. Classifications
and rationale are retained in packaging/compliance-inventory.json, alongside the
original findings. Finding counts never determine readiness.

Deferred permission reviews for v0.1.0, retained for follow-up:

- Intel OpenMP: the exact DLL matches Intel's 2025.3.0 package and August 2024
  Developer Tools EULA. Obtain a version-matched redistribution designation and
  disposition of its end-user, reciprocal-license and applicable nested-notice
  conditions for this MiniSBD AGPL worker.
- NumPy's wheel-local renamed MSVC DLL: obtain an applicable downstream grant
  covering the existing signed, hash-renamed 14.40.33810.0 file and its end-user
  conditions. Runtime installation/use rights alone do not supply that grant.

The OpenBLAS disposition is permitted for the byte-identical supplier combination
under the BSD terms and GCC Runtime Library Exception 3.1, supported by the
version-matched supplier recipe. Complete supplier notices are retained; a
separate standalone GCC runtime is not distributed. Exact binary identities,
evidence and the single clarification question for each remaining issue are in
the existing inventory's three review records.

The two remaining issues are unresolved permissions. The maintainer has deferred
them for v0.1.0; their inventory reviews are classified non-blocking with explicit
release-scoped deferral records and null dispositions. This policy decision does
not supply a grant or waive supplier terms. Supplier hosting and valid signatures
do not establish a grant.
An adequate disposition needs the reviewer, rationale and hash-pinned supporting
evidence in the relevant release_review entry: disposition has outcome permitted
or prohibited, reviewer, rationale and evidence entries with path and sha256.
A prohibited outcome always blocks. Missing required materials and demonstrated
incompatibility remain blocking; approval cannot waive them. No permission or
legal clearance is inferred from a deferral, successful assembly or approval record.

## Platform evidence for v0.1.0

Windows 10 x64 clean-VM core smoke validation passed with limitations; retain the
[original transcript](evidence/windows10-rc1-cmd-2026-11-08.txt). Full machine/runtime
inventory, OS-denied networking, broader error/relocation coverage and target
performance measurements were not completed. These are disclosed limitations,
not claimed passes or additional mandatory test matrices for this release.
Windows 11 is **expected compatible, UNTESTED**; separate acceptance is explicitly
deferred for v0.1.0. Development-host native isolation findings are not clean-VM
results. Retain original diagnostics without copying host-injected modules.

## Deferred work after v0.1.0

The following work and its resulting testing artifacts are explicitly outside
the v0.1.0 acceptance gate. No completion date or later version is promised;
review this list before the next release and record actual results when available.

| Deferred work | Evidence to collect later |
| --- | --- |
| Separate Windows 11 x64 clean-machine acceptance | OS/runtime inventory, exact asset hashes and provisioning/request/shutdown transcript |
| Complete Windows 10 target-machine inventory | Machine configuration, VC runtime version and prerequisite installation/restart record |
| OS-denied networking validation | Firewall policy and native network-attempt observations during provisioning and requests |
| Broader clean-machine error and relocation coverage | ASCII/spaces/Unicode executable, model and state paths; malformed requests, missing/corrupt assets and failed-install recovery reports |
| Target performance and resource baselines | Hardware/storage/power/cache conditions, startup and warm-up timing, repeated translation latency and process-tree memory measurements |
| Broader translation-quality coverage | Representative Chinese corpora, mixed language, punctuation, paragraphs and Unicode/emoji observations |
| Remaining supplier provenance research | Version/build/BOM and incorporated-notice mappings retained in inventory review records |
| Intel OpenMP and NumPy MSVC redistribution permissions | Answers to the inventory questions, applicable grant/conditions and evidence-backed dispositions |

Preserve existing transcripts, reports and hashes unchanged. Historical reports
may say publication was blocked under the policy at capture time; do not rewrite
them. Missing future reports are disclosed gaps, not placeholder passes. Existing
hash-pinned build, source-correspondence and regression inputs remain necessary
to verify the unchanged executable and assemble its distribution.

## Prepare, verify and approve

Run from the repository root in Windows CMD with Node.js 22+. Use fresh output
directories; preserve existing candidates unchanged. Retained build/dist inputs,
cached sources and original supplier files are required; a fresh checkout lacks
them. Historical documentation pins resolve only through
packaging/sources/candidate-documentation/. Runtime/spec/lock pins are unchanged.

The previous `worker-0.1.0-permissions` set predates these deferrals. It is retained
evidence, not the final asset set for this policy. Stage fresh materials after
the policy/inventory/docs changes; do not edit an existing staged manifest:

```bat
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
node scripts\stage_compliance.cjs candidate-staging\release-0.1.0-final-materials
```

Staging exit 0 means verified materials with no mandatory blocker; exit 2 means
valid materials with a mandatory requirement still unmet. Neither means approval.
Bind that directory and its manifest SHA-256 in packaging/release-candidate.json,
then assemble and check a fresh directory. The commands below use
candidate-staging/worker-0.1.0-final/; choose another fresh name if it exists:

```bat
node scripts\assemble_release.cjs candidate-staging\worker-0.1.0-final
node scripts\assemble_release.cjs --check candidate-staging\worker-0.1.0-final
powershell.exe -NoProfile -ExecutionPolicy Bypass -File candidate-staging\worker-0.1.0-final\verify-checksums.ps1
```

Assembly/check exit 0 establishes technical validity even with disclosed findings.
The checksum verifier reports integrity only. Review the manifest, source identity
and mandatory decisions, then explicitly approve with your own name:

```bat
node scripts\assemble_release.cjs --approve candidate-staging\worker-0.1.0-final --maintainer "Your name"
node scripts\assemble_release.cjs --verify-approved candidate-staging\worker-0.1.0-final
```

Approval rechecks all mandatory requirements and writes the adjacent
worker-0.1.0-final.approval.json audit record without altering the eight assets.
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
node scripts\assemble_release.cjs --verify-approved candidate-staging\worker-0.1.0-final
git fetch origin
git switch main
git merge --ff-only origin/main
git merge --no-ff development -m "Release translation-engine v0.1.0"
git diff --exit-code development -- .
powershell.exe -NoProfile -ExecutionPolicy Bypass -File candidate-staging\worker-0.1.0-final\verify-checksums.ps1
git tag -a v0.1.0 -m "translation-engine v0.1.0; binary source b064e29517fb793b2fcf0bf309b6fc78f623367d"
git push origin main
git push origin v0.1.0
```

On GitHub, draft a release for existing tag v0.1.0 and upload all eight files
from the approved directory. Identify the adjacent corresponding-source and
compliance assets, external VC prerequisite and separate model acquisition.
State Windows 10 core smoke passed with limitations and Windows 11 expected
compatible, untested. Disclose the deferred testing, provenance research and two
unresolved permission reviews; do not describe deferral as clearance. Explain that the executable retains its original build
source. Review public source links before publishing. Re-download the complete
published set and verify it. Never overwrite versioned assets; issue a new version
for corrections and retain source access and prior verified assets.
