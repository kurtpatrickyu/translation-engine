## Completion levels and evidence accounting

Current evidence review, 2026-11-08: **38/54 overall; LOCAL 37/37; PUBLIC 1/17**.
The exact 0.1.0-rc.1 Windows 10 VirtualBox core smoke passed (build 19045.3803),
with partial acceptance credit below. No top-level checkbox advances from this
transcript. Windows 10 full acceptance remains partial; Windows 11 is pending.
The snapshots below retain their historical scope; task 5.2 is already complete.

Level A = locally usable and manually testable worker. Level B = publicly
redistributable Windows release. Tasks default to LOCAL unless labelled PUBLIC;
all A5 tasks are PUBLIC. Pending public gates do not block local tests or docs.
Preserve A1–A5 task IDs/history: `a`/`b` suffixes split combined obligations.
The earlier 29/47 snapshot remains historical; this planning amendment credits
already verified local evidence, not newly implemented work. No model binaries
are project release/CI assets. Unknown external model terms stay recorded;
future model hosting needs separate review and clearance.

Amendment snapshot: **34/54 overall; LOCAL 34/37; PUBLIC 0/17**. Five existing
local evidence items (3.8a, 4.3a, 4.4a, 4.5a, 4.7a) are now credited separately.
Seven additional checkboxes arise from obligation splits and the two manual
tasks; this is not a new implementation/test run. Documentation task 4.9's
snapshot was **35/54 overall; LOCAL 35/37; PUBLIC 0/17**. After reviewing the
user's full CMD transcript and additional PowerShell recovery/translation log, 4.10
and 4.8 are complete: **37/54 overall; LOCAL 37/37; PUBLIC 0/17**. Level A is
complete; no local task remains. See `docs/manual-test-results.md` for evidence,
source distinctions and acceptance reconciliation. Historical reports retaining
old model-hosting/combined-gate wording are evidence, not the current policy;
reconcile active usage/public docs in 4.9/5.7 without rewriting raw history.

## 1. A1 — Repository foundation and isolated development environment

- [x] 1.1 Record refined proposal review/approval before implementation; preserve the MIT license, project identity, OpenSpec schema, and the user's existing `.gitignore`. Verify reviewed OpenSpec planning files are explicitly tracked despite `openspec/` being ignored. Keep reviewed provenance metadata tracked when introduced in A3, including under ignored `/models/`; never commit model binaries, the adjacent ZIP export, or generated outputs.
- [x] 1.2 Verify and record an exact CPython 3.12 x64 patch and Windows build baseline; resolve the candidate Argos 1.11.0, CTranslate2 4.8.5, SentencePiece 0.2.1, and PyInstaller 6.22.3 graph on Windows. Record host-local OS details; exact clean Windows 10/11 test images remain an A4 final-acceptance requirement, not an early-development prerequisite. Report incompatibility or unavailable verification separately instead of silently substituting versions or dropping an OS row.
- [x] 1.3 Create `pyproject.toml`, minimal `src/translation_engine` packaging/module entry point, and test configuration with separate runtime and development/build dependency declarations.
- [x] 1.4 Pin bootstrap and lock-generation tools; generate exact transitive hash locks from `pyproject.toml` for Windows CPython 3.12, including mandatory Argos dependencies and local build requirements; verify clean installation and `pip check`.
- [x] 1.5 Add CMD-compatible setup/activation instructions and environment-bound script wrappers; verify test/build helpers refuse a missing `.venv` instead of using global Python.
- [x] 1.6 Verify existing ignore rules cover `.venv`, build/dist, caches, downloaded/installed model binaries, state, and temporary files; add only missing coverage while preserving entries. Ensure reviewed planning/provenance text is explicitly tracked, including metadata under `/models/`, without tracking model binaries.
- [x] 1.7 Verify A1 exit: recreate `.venv` from documented commands, import the full dependency graph, run the module entry point, and record versions with no global project dependency installation.

## 2. A2 — Worker protocol and Argos backend

- [x] 2.1 Immediately after A1, run the blocking minimal real-model compatibility spike: validate pinned Argos 1.11.0 with zh-to-en model 1.9, actual local sentence-boundary resources, repeated real translation, and no network attempts during imports, initialization, or inference with empty caches. Acquire/inspect only that model; record URL, immutable index revision, SHA-256, resources, unchanged dependency versions, commands, and results using isolated temporary package/state paths. Use 2.2 for SBD evaluation and 2.3 for the host-local gate; retain VM evidence under A4; do not mark this task passed or begin extensive protocol/packaging/release work until those spike checks pass. On failure, stop without silently changing pins/model/assets. Do not redistribute evaluation bytes before rights review.
- [x] 2.2 Evaluate the actual SBD resources and supported dependency configuration with empty user caches and network attempts instrumented/denied; choose the simplest validated offline path. Test short Chinese, paragraphs, punctuation, mixed Unicode, long inputs, and repeated translations; record quality/compatibility tradeoffs and observed stdout/stderr. Use Stanza-specific adaptation only if evidence requires it; no implicit downloads, assumed equivalent no-SBD splitter, or process-wide monkey patch.
- [x] 2.3 Gate full local integration on successful host-local real zh-to-en translation, retained resources, documented quality/segmentation limits, exact asset hashes, and Python no-network-attempt instrumentation. Local worker implementation and packaging may proceed after this gate passes. Keep clean Windows 10 22H2/Windows 11 validation pending under A4; do not declare untested platforms supported or require OS acceptance before producing the executable.
- [x] 2.4 After the spike gate passes, implement strict protocol-v1 request/response envelopes, valid string IDs, supported fields/commands, error codes, and UTF-8 handling according to `worker-protocol/spec.md` and design examples.
- [x] 2.5 Implement bounded binary line framing, CRLF support, byte/text/response limits, oversized-line draining, strict JSON/Unicode validation, and immediate response flushing.
- [x] 2.6 Implement the persistent sequential worker, request dispatch, EOF/partial-frame behavior, graceful shutdown, process exit codes, and broken-pipe handling.
- [x] 2.7 After the 2.1–2.3 spike gate passes, add the small backend boundary and explicitly constructed service; implement health/info with separate liveness and cached readiness, reporting configured and actually ready pairs and real versions. Runtime readiness requires the current configured model/tokenizer/SBD to initialize and pass offline warm-up; the earlier spike alone is not readiness proof for a different installation. A3 must revalidate this behavior through production provisioning before A4 acceptance.
- [x] 2.8 Implement production model/state path validation and precedence; configure isolated Argos data/config/cache and CPU/local-provider settings before backend imports; exclude unintended global or environment-injected package roots.
- [x] 2.9 Implement direct zh-to-en package selection, duplicate/missing/incompatible model errors, retained Argos translator resources, and guarded lazy initialization using the spike's validated SBD path. Require real offline warm-up before readiness; A3 revalidates through production provisioning.
- [x] 2.10 Configure stderr diagnostics and stable public error mapping; exclude text from default logs. Test response-only stdout first; add scoped Python redirection or native descriptor/handle redirection only where observed dependency leakage requires it, recording the evidence and retaining mandatory purity tests.
- [x] 2.11 Add deterministic fake-backend tests for IDs, repeated requests, Unicode, empty text, malformed JSON/UTF-8, invalid types/fields/versions, size boundaries and recovery, unsupported languages, readiness, shutdown/EOF, flush behavior, and stdout/stderr separation.
- [x] 2.12 Add isolated backend tests for missing/corrupt/ambiguous models, dependency incompatibility, path precedence, global-state isolation, and resource reuse; verify no package index/download/install functions are reachable through ordinary requests.
- [x] 2.13 Verify A2 exit: retain the host-local real-model evidence and explicit pending final OS checklist, run the deterministic suite in a fresh locked environment, and drive multiple commands through one subprocess. Confirm the versioned consumer contract matches behavior and contains no Freya-specific extensions.

## 3. A3 — Language model provisioning and offline validation

- [x] 3.1 Promote A2's exact inspected model identity/digest, immutable index revision, retrieval evidence, resource inventory, and original filename into reviewed small provenance metadata; verify any reacquired bytes against that digest rather than selecting or learning a new model version. Include the separate ONNX release, asset identity, hash, and conversion/source provenance.
- [ ] 3.2 [PUBLIC] Review obligations for the MiniSBD AGPLv3 code actually bundled with the worker, including covered combined-distribution, corresponding-source/build/install materials and notices. Preserve external model/ONNX attribution and known/unknown provenance without claiming model clearance. No current model hosting is planned; any future hosting requires separate scope/legal clearance. Deliver reviewed worker compliance materials in 5.3; this review does not gate local usage.
- [x] 3.3 Provision the pinned MiniSBD v0.0.1 zh-hans ONNX asset into the external package-local minisbd directory, validate its digest and missing/corrupt/ambiguous-resource failure before fallback downloads, and configure MINISBD before imports. Preserve the original archive and pins, retain initialized resources, and regression-test sentence splitting and recorded quality limits.
- [x] 3.4 Implement checksum-pinned maintainer acquisition separately from local provisioning; reject mismatches without updating pins or fetching a newer model.
- [x] 3.5 Implement explicit `provision-model` CLI with local `.argosmodel` and `--sbd-file` ONNX inputs and managed destination/state paths, safe bounded archive inspection, staging, identity validation, offline compatibility checks, and atomic promotion preserving previous installations.
- [x] 3.6 Add provisioning tests for changed hashes, corrupt/unsafe archives, extraction bounds, unexpected identity/version, interrupted staging, concurrent active-worker mutation, and preservation of unrelated/global packages.
- [x] 3.7 Add real-model integration tests for Chinese, mixed Unicode, paragraphs, empty input, repeated translations, actual readiness, missing local SBD resources, and initialized-resource reuse. These may be opt-in during routine local development, but must pass through A3's production provisioning path for A3 exit, then again for A4 acceptance and release validation; A2 spike evidence does not replace production validation.
- [x] 3.8a [LOCAL] Verify Python network/process-attempt instrumentation before backend imports, production provisioning, readiness/warm-up and repeated translation with isolated fresh state/caches. Evidence: `docs/argos-migration.md`, `docs/unicode-path-validation.md`, `runtime/unicode-source-tests-fixed.xml` (60 passing source tests). Record Python/native coverage limits; do not call this OS-denied networking proof.
- [ ] 3.8b [PUBLIC] Verify startup, provisioning/readiness and repeated inference with OS-level networking denied on clean Windows 10 22H2 x64 and Windows 11 x64; retain network controls and attempted-download evidence for the same candidate, coordinated with 4.5b/4.6.
- [x] 3.9 Verify A3 local exit: exact model/SBD identities/provenance, compatibility, local immutable provisioning, global-state safety and integration evidence are recorded. Worker redistribution compliance (3.2/4.3b/5.3) and clean OS isolation (3.8b) remain independent PUBLIC gates, not local completion gates. External model redistribution clearance is outside the current worker-only scope.

## 4. A4 — Windows executable packaging

- [x] 4.1 Add the checked-in console/stdio PyInstaller onedir spec and `.venv`-bound Windows build script producing `translation-engine-worker.exe` and preserving external model loading and provisioning CLI.
- [x] 4.2 Inspect frozen imports, metadata, resources, and native dependencies for the complete approved graph. Use the 2026-11-07 approval for the unmodified Argos commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` (metadata 1.11.1), record source-to-wheel provenance and reviewed wheel hash, update Argos declaration/backend/spike expectations and both hash locks in a fresh environment, and revalidate the actual worker/provisioning path without Stanza/Torch. Preserve other referenced runtime pins and model/SBD hashes. Evaluate spaCy exclusion with Thinc absence, then inspect reduced collection while retaining CTranslate2, SentencePiece, MiniSBD/ONNX Runtime, NumPy and all required native libraries. Preserve historical baseline evidence; isolated source tests do not pass frozen acceptance. Add only demonstrably necessary hooks with recorded reasons; only one controlled diagnostic build after passing source-worker tests is authorized in this migration; stop on source failure or serious resource pressure.
- [x] 4.3a [LOCAL] Complete technical native inventory/import/export/metadata and actual DLL-origin audit of the existing worker. Evidence: `docs/native-dependencies.md` and `native-static-audit-complete.json` for build `diagnostic-20261107-133601`: 53 AMD64 PEs, all 180 ZIP files matching, application runtimes loaded from the bundle. Preserve the strict native runtime audit failure from two external Teruten modules as a development-host limitation, not a proven app dependency. Do not alter security software or certify clean isolation.
- [ ] 4.3b [PUBLIC] Review Visual C++/OpenMP and other native redistribution rights, approved acquisition provenance and servicing. Bind exact redistributable bytes/notices to the release candidate; host-System32 collection hashes alone do not establish rights or reproducible acquisition. Implement only reviewed requirements before public distribution.
- [x] 4.4a [LOCAL] Produce and hash-check the complete diagnostic worker-only ZIP, excluding external translation/ONNX assets. Existing evidence: `frozen-unicode-all.worker.zip` in build `diagnostic-20261107-133601`, 58,072,023 ZIP bytes / 159,927,584 extracted bytes; full file comparison passed in the native audit. This local diagnostic is not a compliant public release asset.
- [ ] 4.4b [PUBLIC] Assemble the final versioned `translation-engine-worker-win-x64.zip` with runtime, reviewed notices/compliance materials, no model/ONNX binaries or development files; record final source/tool/lock/native and artifact hashes. Revalidate any changed candidate; do not substitute diagnostic hashes after repackaging.

  Local candidate assembly implemented 2026-11-07 without a PyInstaller rebuild:
  `scripts/assemble_release.cjs`, pinned `packaging/release-candidate.json`,
  current post-003 176-file runtime plus 62 notice/instruction files. Two final
  assemblies are byte-identical; all 238 extracted files match the manifest and
  extracted `--version` returns 0.1.0. New worker ZIP has its own hash; original
  executable/native bytes are unchanged. See `docs/release-candidate-results.md`.
  Keep unchecked: reviewed native/source compliance and final public acceptance
  remain unresolved; this candidate is ready for clean-machine testing only.
- [x] 4.5a [LOCAL] Complete host-local ASCII/spaces, separate Unicode model/executable/state and combined Unicode relocation smoke tests, with environment paths removed, actual provisioning/readiness, repeated translation, integrity/failure preservation, stdout purity and shutdown. Evidence: five passing frozen reports and 75 matching translation outputs in `docs/unicode-path-validation.md`; the later minimal-environment functional smoke also passed in `docs/native-dependencies.md`. This is not clean OS isolation.
- [ ] 4.5b [PUBLIC] Execute the packaged protocol/provisioning/relocation/error/flush/stdout/shutdown checks on both clean OS matrix rows against the same candidate and external model hashes, retaining full results and loader errors. Add native stdout redirection only if leakage is demonstrated.
- [ ] 4.6 [PUBLIC] Execute clean Windows 10 22H2 x64 and Windows 11 x64 acceptance using the same exact ZIP/model/ONNX hashes on clean VMs or Windows Sandbox where available, without system Python/Argos and with network access disabled. Record exact edition/build/update state, CPU, commit, commands, network controls, stderr/stdout, and results. Document any technical incompatibility before proposing a support reduction. Coordinate distinct 3.8b offline and 4.5b protocol/relocation assertions; no duplicate claim of completed evidence.

  Partial Windows 10 evidence reviewed 2026-11-08 for 4.5b/4.6: user-reported
  clean x64 VirtualBox VM, build 19045.3803; exact rc.1 worker ZIP
  `708add4798814b8e7d2298ad36ae9697368afa639a4ae6ea99e391f4457fb28d`
  and EXE `ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
  See [review](../../../docs/windows10-smoke-results.md) and
  [matrix/remaining tests](../../../docs/windows-acceptance.md).

  | Windows 10 acceptance subrequirement | Supplied evidence status |
  | --- | --- |
  | Candidate coverage/checksums, EXE and both original asset hashes | Passed. |
  | Startup after user-reported external runtime remedy | Passed: unchanged EXE returns 0.1.0. Initial Python-DLL loader failure and missing x64 runtime registry key preserved; remedy commands/version/origins not captured. Apply change-003's external prerequisite contract, not the historical bundled-VC assumption. |
  | Local-file provisioning, health ready, Chinese-English smoke, shutdown | Passed in two fully captured runs: `Hello, world!`, correlated NDJSON, exit 0, empty normal stderr. Local-file use does not prove network denial. |
  | OS-denied networking / attempted-download evidence (3.8b) | Not evidenced; remains open. |
  | Unicode/spaces relocation, broader corpus and repeated in-process translation, resource failures/preservation, malformed-request recovery, immediate flush/EOF (4.5b) | Not evidenced in this VM; CMD syntax error outside the worker is not recovery coverage. |
  | Exact environment/clean-image inventory, installed VC version and native origins (4.6), complete target measurements (4.7b) | Incomplete/not captured; remains open. |
  | Windows 11 clean acceptance | No result supplied; remains open. |

  No build, inference rerun, dependency/packaging/model change, compliance
  clearance, tag or release occurred during this recording task. Keep 4.5b/4.6
  unchecked and do not substitute old diagnostic or development-host evidence
  for the missing clean-target criteria. Overall stays 38/54.
- [x] 4.7a [LOCAL] Record the diagnostic worker ZIP/extracted size, fresh-process startup, warm-up/init, idle/ready/observed peak working set/private bytes and repeated latency, separately from monitored build memory/system headroom. Evidence: raw build/frozen reports and `docs/argos-migration.md`, `docs/unicode-path-validation.md`; record known host/CPU/RAM/settings/corpus/cache/sample methods and explicitly missing storage/power/cold-cache conditions. This limited local baseline does not complete target measurements or invent performance budgets.
- [ ] 4.7b [PUBLIC] Capture complete clean-target measurements on both OS rows with final artifact/external model hashes, OS/CPU/RAM/storage/VM allocation/power details, SBD/thread/compute settings, cache/warm-up policy, corpus/input sizes, repetitions, raw timing/memory observations and median/tail summaries. Review a baseline without arbitrary thresholds.
- [x] 4.8 [LOCAL] Verify Level A exit after 4.9/4.10: source/frozen/provisioning/local-attempt/native/relocation/limited measurement evidence and manual guides/user session reconciled in `docs/manual-test-results.md` (2026-11-07). All 37 LOCAL tasks complete. Retain native/OS-network, Teruten, timing/environment and licensing limits; no PUBLIC task or unsupported OS claim is advanced. This sign-off uses actual user CMD transcript evidence in addition to prior technical checks, not automated evidence alone.
- [x] 4.9 [LOCAL] Write a distinct manual testing/usage guide for the existing onedir: upstream model/ONNX URLs and exact hashes, user acquisition/verification, offline `provision-model`, explicit Unicode-capable model/state paths, launch/readiness, protocol-v1 repeated translations/errors, stderr handling and shutdown. Link existing developer/protocol docs; label unknown external terms, Teruten host limits and unvalidated OS support. Evidence: `docs/manual-usage.md`, linked from README/development/provisioning, plus `docs/manual-testing-cmd.md`. Initial documentation checks covered six PowerShell blocks, 13 request examples, seven links, help/version and existing hashes, without inference. 4.10/4.8 were pending at that documentation snapshot and are subsequently completed below/above from actual user evidence.
- [x] 4.10 [LOCAL] User personally completed CMD and PowerShell walkthroughs using the existing artifact without rebuilding. Full CMD transcript is retained in `docs/evidence/manual-cmd-2026-11-07.txt`; additional PowerShell transcript is in `docs/evidence/manual-powershell-2026-11-07.txt`. `docs/manual-test-results.md` records hashes, Unicode provisioning, persistence/custom/repeated translation, request errors/recovery, exits/stderr and CMD cleanup. Preserve initial PowerShell missing-asset failures and successful recovery; broader PowerShell completion remains user-confirmed beyond the captured subset. No unprinted outputs/timings or clean host/network claims are inferred; no new heavy test was run to record this evidence.

Focused 4.5 evidence, 2026-11-07: a package-local lazy serialized SentencePiece
tokenizer resolves the reproduced Unicode native-path failure. One additional
monitored build and source/frozen ASCII, separate Unicode model/executable/state,
and combined Unicode checks pass on the development host. See
`docs/unicode-path-validation.md`; retain the earlier failure reports. The old
combined 4.5 is now completed 4.5a and pending public 4.5b; no OS result is inferred.

## 5. A5 — Worker-only public release, compliance, and consumer documentation

- [ ] 5.1 [PUBLIC] Implement a small strict worker integrity manifest/schema/example and verification helpers: project worker URL/version/hash, runtime/source-wheel/build identities and compatibility; external original model/ONNX upstream URLs, versions/hashes/provenance/known-unknown terms and package layout. Do not treat external files as attached release assets.

  Local-candidate contract/helper/example implemented in
  `packaging/release-manifest.schema.json`, `packaging/release-manifest.example.json`,
  `scripts/assemble_release.cjs` and the Windows checksum verifier. It binds the
  original source commit, later materials commit, exact runtime/native/build
  identities, archive contents, prerequisites and external model metadata.
  Publication is explicitly local-only with null tag/release URL, not a fabricated
  download address. Keep unchecked until the existing public tag-specific worker
  URL requirement is bound; no tag/release has been created.

- [x] 5.2 [PUBLIC] Generate manifest and `SHA256SUMS` from final worker/compliance files; reject hash/schema/identity/version/URL conflicts, duplicate entries, missing files and placeholders. Cover all distributed files except the checksum file itself; external model digests belong in manifest metadata, not attached-file checksum entries.

  Completed mechanically for local 0.1.0-rc.1, 2026-11-07: all seven distributed
  files other than `SHA256SUMS` are covered, including manifest, three ZIPs,
  schema, Windows instructions and checksum verifier. The manifest has no
  self-hash. Full candidate verification and negative integrity/source-identity
  tests pass; independent assembly is byte-identical. Public URL/tag binding
  (5.1), compliance (5.3), clean acceptance and publication remain separate.
  Overall progress is now 38/54; LOCAL stays 37/37 and PUBLIC is 1/17.
- [ ] 5.3 [PUBLIC] Deliver reviewed third-party notices/license texts and required corresponding source/build/install material for MiniSBD AGPLv3, Visual C++/OpenMP/native and other bundled code, following 3.2/4.3b. Verify the source-delivery mechanism covers the exact binary; not shipping models does not waive bundled-code obligations.

  Extended implementation 2026-11-07: the existing inventory/stager now binds
  post-003 `diagnostic-20261107-211131` (176 frozen files, 49 native binaries,
  17 third-party Python roots, 30 component groups). Added `LICENSES/`, original
  MiniSBD/tqdm source distributions, `SOURCE_AVAILABILITY.md`,
  `THIRD_PARTY_NOTICES.md`, rebuild instructions and a frozen-source comparison
  helper. All 319 compared Python modules match embedded code; 131 wheel-supplied
  runtime files match cached wheels. MiniSBD's nine Python members match the
  exact 0.9.5 publisher sdist and locked wheel; inherited Stanza credits/notices,
  full AGPL/Apache text, tqdm MPL text/source and missing primary supplier texts
  are collected without local source modifications. The original build metadata
  inventory is preserved at its original hash, with one explicit input relocation;
  ordinary excluded VC DLLs are not current redistributed files. See
  `docs/compliance-staging.md` for staging/verification results: 17 focused tests
  pass; final `post003-release-materials` staging/check return expected code 2,
  with 470 payload / 472 total files, zero missing-material failures and 19
  retained review/source-delivery blockers. Independent repeat is byte-identical.
  Task 5.3 remains partial: final immutable public source delivery must cover
  the exact final executable, and Intel OpenMP/NumPy Microsoft permissions,
  native/static attribution/source mappings and required source/exclusions
  remain unresolved. No supplier permission is declared cleared. PUBLIC stays
  0/17, LOCAL 37/37, overall 37/54; other tasks are unchanged. No rebuild,
  dependency/lock/model change, tag or publication was performed.

- [ ] 5.4 [PUBLIC] Use focused verification helpers and a reviewed checklist binding clean OS rows, offline isolation, target measurements, compliance and hashes to one candidate. Reject missing/stale/failed/mismatched evidence. Manual evidence review is acceptable; no generic attestation service or advanced CI is required.
- [ ] 5.5 [PUBLIC] Prepare the exact verified worker-only candidate for explicit user publication approval after all Level B gates pass. If approved, attach/verify only worker/compliance/integrity assets through a direct reviewed release procedure, never overwrite published versions, and use minimal permissions. No implementation or candidate preparation authorizes publication by itself.
- [ ] 5.6 [PUBLIC] Document trusted repository/release identity, versioned non-overwritten artifacts, SemVer/protocol/external-model compatibility, integrity versus authenticity, trusted offline metadata and rollback. Platform immutability/attestation infrastructure is deferred; do not promise an unimplemented authentication mechanism.
- [ ] 5.7 [PUBLIC] Finalize public README/development/build/provisioning/protocol/support/performance/troubleshooting references and accurate bundled/external attribution. Reuse the Level A manual guide without making local instructions wait for OS acceptance. Verify examples against the consumer contract.
- [ ] 5.8 [PUBLIC] Finalize neutral consumer subprocess guidance for paths, framing/IDs, stderr, readiness, timeouts, shutdown, recovery and upstream asset provisioning. Future consumer integration follows protocol v1 in its own repository; no Freya-specific worker behavior.
- [ ] 5.9 [PUBLIC] Rehearse and verify the complete worker-only release candidate without publishing: ZIP, manifest, checksums, notices/source delivery, support/offline/measurement evidence and documentation agree on exact bytes. Confirm there are no hosted model/ONNX assets, including public CI uploads.

  Local artifact portion rehearsed: deterministic worker/compliance/source ZIPs,
  manifest and checksums, source commit binding, candidate-specific CMD guide,
  exclusions, original payload equality and extracted startup are verified.
  Keep unchecked: reviewed final source delivery plus both clean-OS/offline/
  target-measurement rows remain pending. No public upload or CI change occurred.
- [ ] 5.10 [PUBLIC] Verify Level B readiness independently of completed Level A: both clean Windows rows and OS-denied networking, final measurements, bundled-component compliance, authoritative consumer docs, and candidate verification pass for the same artifact/external model hashes. Report publication approval/status separately; no automatic release.

Deferred, not required for Level A/B completion: advanced CI orchestration,
protected automated publication pipelines, platform immutability integration,
release attestation services. Future model hosting is outside this scope and
requires separate legal clearance. Existing integrity, code/source-delivery,
OS support, and explicit publication gates remain mandatory.
