# Remaining Windows acceptance checklist

## Exact candidate and current matrix

**v0.1.0 scope decision (2026-11-08):** the maintainer explicitly waived separate
Windows 11 clean-machine acceptance for the initial release. Windows 11 remains
**expected compatible, UNTESTED**, optional future validation. Windows 10's
remaining criteria and all other release gates below are unchanged. See the
[recorded decision](v0.1.0-acceptance-scope.md).

Use **0.1.0-rc.1**, the complete eight-file candidate described in
[candidate results](release-candidate-results.md) and the
[candidate CMD workflow](windows-release-candidate.md). This checklist supersedes
its earlier pre-003 diagnostic hashes and bundled-VC instructions. Historical
native/Unicode reports remain evidence for their own artifacts.

- Worker ZIP: `708add4798814b8e7d2298ad36ae9697368afa639a4ae6ea99e391f4457fb28d`.
- Worker EXE: `ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
- Model: `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d`.
- ONNX: `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e`.

The post-003 payload has 49 native binaries / 176 original files, plus 62
release-info files in the candidate worker ZIP. It requires a separately installed
official VC++ v14 x64 runtime; the four ordinary VC DLLs are excluded. NumPy's
renamed Microsoft DLL remains bundled. Preserve original loader errors and use
[documented prerequisite remediation](native-dependencies.md#external-vc-prerequisite-for-change-003).
Do not require a new missing/older/newer-runtime matrix to finish acceptance.

| Target | Supplied evidence | Full row status |
| --- | --- | --- |
| Windows 10 22H2 x64, build 19045.3803, VirtualBox (user-reported clean VM) | Exact checksums, local provisioning and two captured successful core smoke runs after prerequisite remedy; [reviewed transcript](windows10-smoke-results.md). | Partial; OS-denied networking, relocation, native origins, broader checks and target measurements pending. |
| Windows 11 x64 | Expected compatible, UNTESTED; no clean-VM result supplied. | Separate acceptance waived for initial v0.1.0; optional future validation, no pass claimed. |

The Windows 10 transcript does not identify edition/update/ESU state, hardware/VM
allocation, actual installed VC version, loaded DLL origins or independently
inventory Python/Argos absence. It proves neither OS-level network denial nor
full platform support. Local-file provisioning is distinct from proven offline
isolation. The initial prerequisite failure is retained, not relabelled success.

## Remaining mandatory v0.1.0 Windows 10 checks

For Windows 10, retain the passed core smoke credit and complete the following.
Windows 11 is optional future work: if exercised, reuse the candidate smoke and
the same checklist/hashes, recording actual results without inferring a pass.

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
  OS-level isolation. For v0.1.0 this supplies 3.8b evidence on required Windows 10;
  Windows 11 networking validation is optional with its waived acceptance.
- [ ] Reuse the candidate CMD workflow and existing manual guide's interactive
  and deeper checks with the rc.1 EXE/models/state paths. Exercise multiple
  translations per persistent process, product/mixed Unicode/paragraph/empty/long
  inputs, malformed-request recovery, unsupported languages, response-only stdout,
  separate stderr, per-response flush before exit, shutdown/EOF and process exit.
  Send JSON through worker stdin or a redirected NDJSON file, never as CMD commands.
- [ ] Exercise spaces and separate Unicode executable/model/state paths, then
  combined relocation, plus missing/corrupt resources and failed-provisioning
  preservation using disposable model copies/fresh destinations. Retain exact
  commands, expected/actual errors and outputs. Do not mutate the original assets
  or immutable accepted installation. These remain part of 4.5b/4.6.
- [ ] Capture 4.7b measurements: worker ZIP/extracted and separate asset sizes;
  fresh-process launch to uninitialized info; initialization/warm-up to ready;
  idle/ready/observed peak working set/private bytes; repeated warmed per-request
  latency with raw observations, sample counts, median/tail, corpus/input sizes,
  cache/warm-up conditions, thread/compute settings and timing/sampling methods.
  Review baselines without inventing performance thresholds.

Reuse [manual CMD checks](manual-testing-cmd.md#6-interactive-usage) and
[deeper cases](manual-testing-cmd.md#7-optional-deeper-checks), but take candidate
paths/hashes from this page and the rc.1 workflow: the general guide's default
artifact is an older diagnostic. Existing `scripts/validate_windows.py` provides
`--exe`, `--unicode-component model|executable|state|all`, `--native-audit`,
`--external-vc-runtime` and fresh `--report` paths for instrumented regression and
measurement reuse. The external-runtime flag requires native audit. The harness
requires the project's Windows `.venv`, local pinned assets and a checkout; it
labels reports `clean_machine: false` / `os_firewall_isolation: false` and omits
some target details. Use an instrumented replica for that harness, preserve its
labels and supplement raw reports with actual environment/network records;
it does not replace executable-only Python-free clean-VM proof. Do not install
Python into the clean test image just to claim that proof. No harness/build was
run while recording this transcript.

## Exact remaining publication gates

This review credits no new top-level task: **38/54 complete; LOCAL 37/37;
PUBLIC 1/17**. The Windows 10 core smoke is partial evidence under 4.5b/4.6.
The following groups account for all 16 open tasks in the
[current checklist](../openspec/changes/001-build-offline-translation-engine/tasks.md):

| Open task IDs | Remaining gate |
| --- | --- |
| 3.8b, 4.5b, 4.6, 4.7b | Finish required Windows 10 acceptance, network denial, full protocol/resource/relocation/native-origin evidence and complete target measurements above. Windows 11 is expected compatible but UNTESTED, waived for v0.1.0 and optional future validation. |
| 3.2, 4.3b, 5.3 | Resolve existing bundled-component review/source obligations and bind final immutable source/build/install delivery to this exact binary. The candidate dossier retains 19 blockers, including Intel/native terms, NumPy renamed Microsoft DLL entitlement and remaining supplier/static source/notice mappings; see the existing [compliance record](compliance-staging.md#remaining-task-53-gates) and candidate compliance ZIP's `BLOCKERS.txt`. No legal clearance is inferred from VM success. |
| 4.4b, 5.1 | Finalize the reviewed public asset set and immutable tag-specific worker/source URL binding. The local candidate exists and checksum mechanics (5.2) passed; public tag/release URLs remain null. |
| 5.6, 5.7, 5.8 | Finalize trust/version/rollback, support/performance/troubleshooting and neutral consumer documentation against accepted evidence. |
| 5.4, 5.9, 5.10 | Complete candidate-bound evidence review and full release rehearsal; missing/stale/mismatched gates must fail readiness. Local deterministic assembly alone does not complete these tasks. |
| 5.5 | Obtain explicit approval for the exact verified public candidate after all gates pass; no release or tag is authorized here. |

The 19 compliance blocker IDs remain: `charset_normalizer/review`,
`ct2-static/review`, `ctranslate2/review`, `distribution/native-static`,
`distribution/source-delivery`, `intel-openmp/review`, `joblib/review`,
`libffi/review`, `msvc-numpy/review`, `openblas/review`, `openssl/review`,
`ort-static/review`, `python/review`, `python-incorporated/review`,
`sacremoses/review`, `sentencepiece/review`, `sentencepiece-static/review`,
`sqlite/review`, `yaml/review`. These identify existing dossier entries, not a new
review or framework. External model hosting is outside this worker-only release;
unknown external terms stay recorded without adding a model-hosting clearance gate.
