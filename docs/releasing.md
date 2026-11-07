# Release preparation and current status

No production release or tag has been published. Local assembly verifies bytes;
it does not establish legal clearance, clean Windows support or publication
approval. The current candidate is `0.1.0-rc.1` for initial `v0.1.0`.

## Current evidence and release scope

The maintainer waived separate Windows 11 clean acceptance on **2026-11-08** for
initial v0.1.0 only. Windows 11 is **expected compatible, UNTESTED**; validation
is optional future work. Later releases need their own scope decision.
Windows 10 x64 VirtualBox build 19045.3803 is core smoke-tested with limitations.
The [original transcript](evidence/windows10-rc1-cmd-2026-11-08.txt) has SHA-256
`7bf2949e1b9f30e6f3a0d0d082713f4bdfe1312304728c348e3a376c82ebb1ac`.
Checksums, startup after external-runtime remediation, local provisioning,
ready health, translation, shutdown, exit 0 and empty normal stderr passed in
two captured runs. The initial Python-DLL loader failure and missing x64 runtime
registration remain evidence. Remediation commands, actual installed VC version
and native origins were not captured. JSON entered at CMD was a shell error,
not a malformed-request recovery test.

Full Windows 10 acceptance remains partial. VM cleanliness/x64 are user-reported;
the transcript is not a complete machine inventory or proof of OS network denial.
Development-host Unicode/native functional tests passed, but strict native
isolation retained two Teruten host modules as findings; do not allowlist or
distribute those modules. Python audit hooks are not OS firewall proof.

Final candidate: `candidate-staging/worker-0.1.0-rc.1-final/`; independent repeat:
`candidate-staging/worker-0.1.0-rc.1-final-repeat/`. All eight files match between
the assemblies. `SHA256SUMS` covers the other seven, including the manifest.

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


EXE SHA-256: `ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
Binary source commit: `b064e29517fb793b2fcf0bf309b6fc78f623367d`;
licensing materials commit: `6faf8a8d40713e7f5bafb787a2e900b104995ddb`.
The baseline `diagnostic-20261107-211131` has 176 original files / 49 native
binaries. The worker ZIP adds 62 release-info files without changing those bytes.
`packaging/release-manifest.example.json` is the actual local manifest, with
null public URLs and `release_ready:false`. Diagnostic ZIP hashes are distinct
from the candidate ZIP hash above.

## Verify or prepare artifacts

Use Windows CMD from the root, Node.js 22+ with no npm dependencies, and the
project interpreter for Python helpers. Retain the exact ignored build/dist
dossier, cached source/wheels, original build inventory and supplier license
input named by `packaging/compliance-inventory.json`. A fresh checkout lacks
these inputs. Do not regenerate evidence merely to satisfy a pin.

```bat
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
node scripts\stage_compliance.cjs --check candidate-staging\release-rc1-compliance
node scripts\assemble_release.cjs --check candidate-staging\worker-0.1.0-rc.1-final
```

Compliance exit **2** means valid preparation with unresolved readiness; **1**
means failure. Assembly/check returns **0** for a valid local candidate only.
Existing artifacts are checked without writes. The frozen candidate preserves
assembly-time instructions, including superseded Windows 11 gate wording.
Current requirements are the ones in this guide; do not edit hashed artifacts.

To prepare a fresh compliance dossier, choose a never-used destination:

```bat
node scripts\stage_compliance.cjs candidate-staging\NEW-compliance
node scripts\stage_compliance.cjs --check candidate-staging\NEW-compliance
scripts\python.cmd scripts\verify_frozen_sources.py --report runtime\NEW-source-correspondence.json
```

Review `BLOCKERS.txt`, source correspondence, notices and every material pin.
The existing compliance preparation has 19 blockers and no missing-material
failures; Python comparison covers 319 modules and wheel comparison 131 payload
files. Python correspondence does not establish native/static source completeness.
The retained original preparation at `candidate-staging/post003-release-materials/`
has manifest hash `4caf7ea74c028b05ca75d798ea93b6e49a9fbf78488ce97bd80fa8601b295308`.

The inventory remains the single active component record. Historical build-input
bytes for its one permitted metadata relocation live at
`runtime/compliance-preparation/original-build-inventory.json`; runtime/spec/lock
hashes have no exception. Exact byte-pinned historical documentation is retained
under `packaging/sources/candidate-documentation/` solely for source correspondence.
It is not current guidance. The stager verifies those bytes against existing
material hashes. Original supplier texts and source archives remain unchanged.

For new local assembly, `packaging/release-candidate.json` binds the reviewed
compliance directory/manifest, source commits, regression reports and external
asset metadata. Update those bindings only after review when intentionally
preparing a different dossier. Use a fresh assembly directory:

```bat
node scripts\assemble_release.cjs candidate-staging\NEW-candidate
node scripts\assemble_release.cjs --check candidate-staging\NEW-candidate
```

Assembly never freezes code, acquires models, tags or publishes. It verifies
the original worker, build inputs and Git correspondence; changed executable
inputs require a new build and validation using [development](development.md).
ZIP paths/timestamps/permissions/compression are deterministic. New assembly
instructions use current README; retained source snapshots and compliance
materials keep their historical bytes. Verify a repeat assembly byte for byte.

Transfer the complete candidate directory to the target machine, verify with
`verify-checksums.ps1` against trusted materials, extract elsewhere and follow
[README's CMD procedure](../README.md). Use independently obtained, verified
upstream assets; deny networking before provisioning for acceptance.

## Remaining mandatory Windows 10 acceptance

- [ ] Record edition/version/build, servicing/update/ESU state, CPU/features, RAM,
  storage, VM allocation and power settings; inventory no system Python/global
  Argos and no inherited development paths/caches. Capture official x64 runtime
  version, registration and actual loaded module origins, including ordinary VC
  DLLs from the installed runtime and NumPy's renamed DLL from the bundle. Keep
  unexpected modules visible; do not copy/allowlist development-host Teruten DLLs.
  Retain native API-set/UCRT/delay-import failures on the exact OS build; do not
  infer target compatibility from development-host System32 files or alter host
  security software to force an isolation pass.
- [ ] Deny networking at the VM/OS boundary **before** fresh-state local
  provisioning, startup/readiness and repeated inference; retain exact controls
  and attempted-download observations. Hash the same upstream-obtained files;
  do not download assets during the test or substitute Python audit hooks for
  OS-level isolation. For v0.1.0 this evidence is required on Windows 10;
  Windows 11 networking validation is optional with its waived acceptance.
- [ ] Use README's CMD procedure and the protocol reference with the rc.1
  EXE/models/state paths. Exercise multiple
  translations per persistent process, product/mixed Unicode/paragraph/empty/long
  inputs, malformed-request recovery, unsupported languages, response-only stdout,
  separate stderr, per-response flush before exit, shutdown/EOF and process exit.
  Send JSON through worker stdin or a redirected NDJSON file, never as CMD commands.
- [ ] Exercise spaces and separate Unicode executable/model/state paths, then
  combined relocation, plus missing/corrupt resources and failed-provisioning
  preservation using disposable model copies/fresh destinations. Retain exact
  commands, expected/actual errors and outputs. Do not mutate the original assets
  or immutable accepted installation.
- [ ] Capture target measurements: worker ZIP/extracted and separate asset sizes;
  fresh-process launch to uninitialized info; initialization/warm-up to ready;
  idle/ready/observed peak working set/private bytes; repeated warmed per-request
  latency with raw observations, sample counts, median/tail, corpus/input sizes,
  cache/warm-up conditions, thread/compute settings and timing/sampling methods.
  Review baselines without inventing performance thresholds.


Use `scripts/validate_windows.py` for developer frozen/native diagnostics with
explicit executable and fresh report paths. Do not install Python into a clean
test image just to claim executable-only acceptance. Preserve all original
failure reports and keep test inputs/outputs bound to exact candidate hashes.

## Unresolved publication obligations

- Finish the Windows 10 evidence above, including OS-denied networking and target
  measurements. The Windows 11 waiver is not a test pass or publication approval.
- Resolve existing Intel/native terms, NumPy's renamed Microsoft DLL entitlement,
  remaining supplier/static source and notice mappings, and any missing covered
  dependency source or evidence-backed exclusions. The 19 detailed blocker
  entries remain in the inventory and candidate `BLOCKERS.txt`.
- Supply final immutable corresponding-source/build/install materials and notices
  tied to the exact executable. Preserve MiniSBD AGPLv3 and tqdm MPL/MIT materials,
  original source archives and all supplier notices. Follow
  [SOURCE_AVAILABILITY.md](../SOURCE_AVAILABILITY.md) and
  [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md); no legal clearance is inferred.
- Finalize the reviewed public asset set, immutable source/tag/URL binding,
  trust/version/rollback and support/performance/consumer guidance against accepted
  evidence. Rehearse candidate-bound release verification; stale or missing gates
  must fail readiness. Obtain explicit approval of the exact verified public set.

External model hosting is outside this worker-only release. Keep unresolved
external terms in provenance; do not silently add models or installers to assets.

## Publication procedure after all gates pass

Review the complete diff, source correspondence, checksum/manifest coverage and
license/source delivery together. Choose a version-specific immutable tag and
record its full commit plus same-release source asset URLs. A tag must preserve
the exact binary build inputs; changed inputs need a rebuilt, revalidated worker.
The current local-candidate schema deliberately cannot declare a public release;
final public metadata must be reviewed before publication.

After explicit publication approval, create the reviewed version tag and GitHub
Release, attach the complete worker, verification materials, corresponding-source
and compliance packages, and explain the external VC prerequisite/model acquisition
and tested platform limits. Do not overwrite versioned assets; issue a new version
for corrections and retain prior verified versions for rollback. Download published
assets afresh, verify all hashes and source links, test the documented user flow,
and keep source accessible at no extra charge for as long as the binary is offered.
No publication or tag creation is authorized by repository cleanup.
