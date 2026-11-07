## Context

See `proposal.md` for motivation. This is a proposal based on read-only inspection on 2026-11-07, not a replacement implementation or a fresh translation experiment. Change 001 and its completed Level A evidence remain authoritative for the existing worker. This design changes the candidate only after implementation is authorized.

### Verified dependency and runtime graph

| Stage | Actual current behavior / evidence |
|---|---|
| Declaration/resolution | `pyproject.toml` requires Argos 1.11.1, CTranslate2 4.8.5 and SentencePiece 0.2.1. The reviewed Argos wheel's METADATA requires MiniSBD, spaCy, packaging and sacremoses as well. Both locks pin MiniSBD 0.9.5. MiniSBD requires filelock, NumPy and ONNX Runtime; its dev extras are not inference requirements. Argos is used directly; LibreTranslate's application/API is not in this path. |
| Configuration | `Config.configure_argos()` sets isolated XDG/model/cache locations, CPU/OpenNMT settings and `ARGOS_CHUNK_TYPE=MINISBD` before backend imports. |
| Import | `backends/argos.py` imports `argostranslate.package, translate`; `translate.py` imports `sbd` and its concrete classes. `sbd.py:18` unconditionally imports `SBDetect` and MiniSBD models, then assigns their cache directory. MiniSBD's `__init__` imports its implementation, which imports inference/model utilities. Its package metadata says 0.9.5 although its internal `__version__` string says 0.9.0; use distribution/wheel identities. |
| Initialization | `validate_install()` verifies archive-derived receipt files plus exactly one pinned `minisbd/zh-hans.onnx`. Backend checks distribution versions including MiniSBD, constructs a package, adapts its tokenizer, constructs `PackageTranslation`, asserts `MiniSBDSentencizer`, and warms up `你好，世界！`. |
| Segmentation/inference | Package discovery prioritizes `minisbd/` over bundled Stanza. `MiniSBDSentencizer` chooses the first package-local ONNX; without one it selects a language/cache/download route, mapping `zh` to `zh-hans`, possibly falling back to English. `lazy_detector()` retains `SBDetect`, which creates an ONNX inference session. Argos splits paragraphs, calls `sentencizer.split_sentences`, encodes each segment with package SentencePiece, translates batches, concatenates hypothesis tokens in returned order, decodes once per paragraph and joins paragraphs. |
| Freeze | `packaging/worker.spec` copies MiniSBD metadata and excludes spaCy/Stanza/Torch, but does not exclude MiniSBD. The retained PYZ inventory includes `minisbd`; native files include ONNX Runtime. Excluding unused packages does not remove MiniSBD's incorporated Stanza-derived code. |

The approved source ZIP was rehashed as `0cedceb52ca288b12bb4a33de97f7a8df13bc45dd46f6338754194a27b746343`. Its `sbd.py`, `translate.py` and `settings.py` match installed sources after newline normalization. Source identity is commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`; the approved unmodified wheel hash is `825b1bf872390547bad6c1fcf1f12e5967e2fe6b44ca1e8a82e17a8dd79a2aa0`. Version 1.11.1 alone is insufficient identity.

### Actual supported Argos segmentation modes

| Mode | Behavior in the exact approved revision | Suitability |
|---|---|---|
| DEFAULT / ARGOSTRANSLATE | DEFAULT maps to ARGOSTRANSLATE. Constructor chooses bundled Stanza only if Stanza is installed; otherwise packaged MiniSBD or MiniSBD fallback. | Does not avoid MiniSBD. This is not the legacy few-shot algorithm. |
| NONE | Enum exists with an unsupported TODO; constructor leaves the sentencizer unset and raises `NotImplementedError`. | Unusable; unconditional import still happens. |
| MINISBD | Constructs MiniSBD adapter and loads detector on first split. | Current working baseline; AGPL code remains. |
| SPACY | Optional import, but explicit mode initializes cached multilingual model via `cache_spacy()` at module import; missing packages/cache cause failure or acquisition. | Heavy and unnecessary; not a lightweight offline replacement. |
| STANZA | Explicit Stanza path; import is optional, pipeline initialization is lazy. Historical local archive metadata/checkpoint failures remain documented. | Reintroduces excluded frameworks and old incompatibilities. |
| Legacy/few-shot functions | Helpers exist, but the old selection code inside `apply_packaged_translation()` is a triple-quoted inactive block. | No functioning setting-only alternative; requires another SBD model and implementation work. |

### Actual model and length constraints

The original archive was rehashed as `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` (74,481,402 bytes). Read-only ZIP inspection found metadata zh→en, package 1.9, Argos 1.9.0; SentencePiece 804,374 bytes; CTranslate2 model 82,713,318 bytes; shared vocabulary; and legacy Stanza resources. `model/config.json` sets `add_source_bos=false`, `add_source_eos=true`, `<s>`/`</s>` and no model context length. There is no `target_prefix` in package metadata (Argos default: empty).

A read-only .NET binary-header/tensor-table inspection, following the [versioned CTranslate2 model reader](https://github.com/OpenNMT/CTranslate2/blob/v4.8.5/src/models/model.cc), found format 6, TransformerSpec revision 7, 277 tensors and 3 aliases. The shared positional encoding tensor is `decoder/position_encodings/encodings`, shape **2048 × 512**, and `encoder/position_encodings/encodings` aliases it. Parsing tensors and aliases ended exactly at byte 82,713,318. The embedding vocabulary has 65,000 rows. This establishes a finite positional table, not a quality guarantee for 2,048-token prose; reserve automatic EOS/decoder start positions and stay far below it.

Argos does not pass source/decoding length options. CTranslate2 4.8.5 exposes default **1,024 source tokens** with truncation and **256 generated tokens**; see its [Translator API](https://opennmt.net/CTranslate2/python/ctranslate2.Translator.html). `max_batch_size=32, batch_type="tokens"` controls batching, not a per-sentence context safeguard. Existing 40-short-sentence coverage never proves safety of one long unpunctuated sentence. Character counts are not token counts, and splitting/reconstructing decoded token pieces can alter spaces, underscores or unknown characters.

### Licensing and current artifact boundary

Argos' inspected grant is MIT (the project generally describes MIT/CC0); MiniSBD's own declaration/text is AGPLv3. Neither controls the independent application license of host application. No MiniSBD algorithm/source will be reused in the owned splitter.

`docs/releasing.md`, `packaging/compliance-inventory.json` and the retained diagnostic audit identify 17 third-party PYZ roots and 180 distributed files / 53 PE files. The current diagnostic EXE hash is `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941`; ZIP hash is `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`. Its static audit reports passed with no errors. This proposal inspected the retained audit/TOC and compliance evidence; it did not execute/re-extract the frozen PYZ or certify a new artifact.

MiniSBD is the identified AGPL runtime package. There are also **GPL-bearing components**: PyInstaller's embedded bootloader/loader (GPL with bootloader exception) and GCC runtime material in NumPy's OpenBLAS DLL (GPL with GCC runtime exception). These are not unqualified AGPL dependencies and cannot be described as absent. Unknown CTranslate2/SentencePiece/ONNX Runtime static BOM details mean no exhaustive absence claim is justified yet. Removing ONNX Runtime removes its own component review only if the final artifact proves absence. NumPy is also needed by CTranslate2 and potentially other retained packages; its removal is not assumed. A literal requirement to remove every GPL-covered byte, including these exceptions, would require a broader packaging/native-toolchain project and is outside this smallest-change recommendation. Preserve and review exceptions separately; any newly discovered non-excepted GPL/AGPL runtime component blocks migration acceptance.

## Goals / Non-Goals

**Goals:** preserve direct Argos inference, the exact model and tokenizer behavior, deterministic ordered coverage of source spans, bounded CPU memory/inference, no download attempts, Unicode paths, NDJSON v1 and graceful lifecycle. Prove no AGPL code in the distributed candidate before making that claim.

**Non-Goals:** language expansion, neural-model quality improvements, model conversion, a new generic translation backend, host application changes, new OS support claims, deleting old assets/evidence, licensing clearance or publication. Preserve protocol limits (including 65,536 UTF-8 text bytes). No new native libraries, neural SBD assets, Stanza/PyTorch or LLMs.

## Decisions

### 1. Owned bounded segmentation and a narrow, explicit Argos extension

Use an independently authored engine module returning ordered source spans and corresponding original substrings. Keep the existing Unicode-safe serialized SentencePiece adapter. Do not bypass Argos with an independent CTranslate2 backend.

Maintain a small reviewed patch against the exact upstream base, with a distinct local wheel version such as `1.11.1+translationengine.1`, source/base/patch/wheel hashes, changed-source notices and reproducible build inputs. The patch has three responsibilities:

1. Move MiniSBD's import and cache configuration into its selected adapter path; make its dependency an explicit optional extra instead of a default requirement. No MiniSBD code copied into Argos or the worker. Existing upstream defaults may retain their behavior for other callers, but the engine always supplies its own splitter and never enters default selection.
2. Add an explicit keyword-only `sentencizer` parameter to `PackageTranslation`; when supplied, validate its interface and bypass automatic selection entirely. Avoid constructing a MiniSBD object and then replacing it. No `sys.modules` stubs, global class replacement, or mutation of installed site-packages. Keep the original optional spaCy/Stanza imports guarded and excluded in the frozen candidate.
3. Add explicit per-instance inference limits to the packaged-translation call and a typed internal generation-limit signal before decoding/returning a successful result. Keep all ordinary beam, score, prefix, token concatenation and paragraph behavior unchanged. This small seam is needed because source segmentation alone cannot detect decoder cap exhaustion.

The owned backend supplies a reusable splitter and candidate limits. Start with **256 SentencePiece source pieces per chunk**, reserve two extra positions for automatic special tokens, set `max_input_length=258`, and use **512 generated tokens**, below the inspected 2,048-position table. Validate every actual encoded chunk before submission; an over-budget chunk is a programming/compatibility failure, never silently sliced. Reject successful output when a returned hypothesis reaches the generation cap. Treat these as conservative engineering limits requiring real-model confirmation, not a claimed training-context optimum.

For decoder-cap saturation, discard the entire tentative result, retry with a smaller source budget (halve 256 down to 1), and never publish intermediate text. Retain the same native translator/tokenizer. At most nine full attempts are possible; stop early when an indivisible Unicode span cannot satisfy token limits or generation still saturates. Return existing `TRANSLATION_FAILED` without a partial translation if it cannot be completed safely. No blind overlap windows or concatenation of partially retried output. Tests must demonstrate the exact CTranslate2 cap signal/returned token count behavior; failure to distinguish saturation blocks adoption. Avoid retries for unrelated native failures.

### 2. Span rules, long-text handling and reconstruction

- Let Argos retain its paragraph split/join contract. Mirror its existing LF semantics and documented whitespace behavior; test CRLF, repeated/leading/trailing newlines explicitly. A byte-identical whitespace-preserving translator is not being promised.
- Within each paragraph, first recognize Chinese sentence endings `。！？`, ASCII `!?`, runs of terminal punctuation and adjacent closing quotes/brackets. Do not split every ASCII period: protect decimal values, versions, URLs, email addresses and product identifiers; treat ASCII full stop as a boundary only with context consistent with sentence termination. Keep punctuation with its source span. Include Chinese/ASCII ellipsis fixtures and quoted punctuation; prefer conservative under-splitting to destructive edits.
- For any oversized sentence, prefer safe clause separators (`，、；：` and ASCII equivalents) or whitespace close to the token budget. If none exists, subdivide the **original Unicode string** at deterministic boundaries without crossing a combining/variation/ZWJ sequence when possible. Re-encode candidate substrings using the exact retained tokenizer. Never split model tokens and decode them back into source text. If one indivisible unit itself exceeds capacity, fail explicitly.
- Require nonempty, nonoverlapping contiguous spans covering the entire paragraph, including its whitespace, in original order. Assert concatenating source spans equals the original paragraph. A simple bounded scan plus conservative chunk sizing avoids quadratic prefix tokenization of a full 65 KB string; tokenize bounded windows and account for re-encoding at every final boundary. Pin operation/input-size bounds in tests.
- Preserve existing Argos target-token concatenation and single decode per paragraph, prefix removal and order. Do not invent source/target alignment. Source span coverage proves every input character reaches tokenization once per attempt; it cannot guarantee that the neural model preserves all meaning or Unicode in its output.

### 3. Alternatives and tradeoffs

| Alternative | Evidence / advantage | Why not selected initially |
|---|---|---|
| A: pySBD | [MIT license](https://github.com/nipunsadvilkar/pySBD/blob/master/LICENSE), [Chinese rules](https://github.com/nipunsadvilkar/pySBD/blob/master/pysbd/lang/chinese.py), [language mapping](https://github.com/nipunsadvilkar/pySBD/blob/master/pysbd/languages.py); upstream setup declares no runtime dependencies. Pure Python, model-free, existing multilingual rules. | Still needs original-span/no-cleaning validation, exact release/hash/license review, token bounds and the same Argos extension. More multilingual rule surface than this single pair needs. Use as the next isolated comparison if owned rules show material boundary-quality failures; do not add both splitters to production. No pySBD code installed or tested in this proposal. |
| B: owned splitter (recommended) | No added dependency/native/model payload; straightforward source coverage and token budgeting; focused zh/en fixtures. | Own punctuation/quotation rules and maintenance; less contextual SBD and possible forced splits inside product names. Quality gate is mandatory. |
| C: existing Argos modes | No new owned splitter if one worked. | Exact mode table above rules out a safe setting-only solution. NONE/ARGOSTRANSLATE are not shortcuts. |
| Direct CT2 engine | Avoid importing Argos translation/SBD modules. | Duplicates model/tokenizer/paragraph/decoding policy, broadens the backend change and violates retained direct Argos design. Keep only as a future separately reviewed redesign. |
| Freeze exclusions alone / optional import only | Can prevent some collected modules. | Unconditional import or missing required metadata breaks readiness; default fallback remains unsafe and pip metadata remains inconsistent. Exclusion is a defense, not the architecture. |
| Retain MiniSBD and fulfill obligations | Existing functional evidence; no segmentation regression; historical redistribution review recommended this before alternatives were assessed. | Preserves AGPL combined-distribution/source work and unresolved native compatibility review. Correct fallback if the replacement fails essential tests; no disguised/out-of-process licensing workaround. |

pySBD links describe inspected upstream source, not an approved immutable release. Implementation must pin a reviewed release only if that alternative becomes necessary. Its selection would require updating the implementation design/evidence before adoption.

### 4. Provisioning, manifest and dependency migration

Use a new receipt schema (2), identifying unchanged archive hash, layout version, owned segmentation policy version and every installed resource hash. Continue validating metadata, safe extraction bounds, traversal/casefold duplicates/symlinks, package containment, tokenizer/native model bytes and runtime warm-up before atomic promotion. No `sbd_sha256` field or required ONNX file in new receipts. Segmenter version is code identity, not a synthetic model checksum.

Provision a fresh external directory. Reject legacy receipts with `MODEL_INCOMPATIBLE` and explicit new-directory provisioning guidance; do not mutate or implicitly convert them. Reject obsolete `--sbd-file` with a clear CLI migration message. Keep an idempotent existing schema-2 install immutable and revalidate it before success. Original `.argosmodel`, legacy ONNX, Stanza archive members and baseline installations remain untouched. Stanza files extracted from the unchanged archive may remain inert in external model storage, hashed in the receipt; they are not shipped with the worker or loaded by inference. Never copy archive/model binaries into releases.

Future model provenance and strict manifest entries keep the same external translation URL/hash/license evidence, remove the ONNX requirement for the new candidate, and identify receipt/segmenter/runtime patch versions. Preserve old ONNX provenance under a clearly historical baseline record instead of relabeling old acceptance as new. Keep manifest and checksums tied to actual release files; no fabricated current manifest is added now (release schema/assets are still pending).

Regenerate runtime and development locks in a new isolated candidate environment from the patched wheel's truthful metadata. MiniSBD must be absent from installed runtime distributions and loaded modules. Re-resolve ONNX Runtime, filelock and other transitive dependencies; remove only orphans. Retain dependencies still required by CTranslate2, spaCy's declared graph or other packages. `pip check` must pass without `--no-deps` masking. Preserve CTranslate2/SentencePiece pins. Update Argos wheel builder, setup and hash verifier to validate the explicit base-plus-patch recipe and distinctive version; set `source_modified=true` in future provenance. Do not label a patched wheel unmodified upstream.

Freezer metadata checks drop MiniSBD; exclusions add MiniSBD and, if genuinely unused, ONNX Runtime, while retaining existing framework exclusions. `service.py` currently reports `configured_pairs[].sbd_version="v0.0.1"`; keep the protocol-v1 field/type and report the owned policy version, e.g. `engine-zh-v1`. Report the actual patched Argos distribution version through the existing `argos_version` field. No envelope, command, error-code, framing, limits or lifecycle changes.

### 5. Correctness and regression acceptance

Record paired raw baseline/candidate inputs, segments/spans, source token counts, outputs, artifact/dependency/model hashes, compute type, latency, initialization and memory on the same host. Historical `runtime/spike-minisbd.json` is Argos 1.11.0 evidence; current 1.11.1 integration/manual/frozen evidence is separate. During implementation rerun the retained 1.11.1 baseline in its own preserved environment for a controlled comparison, without altering historical reports.

| Corpus | Baseline evidence / predicted change | Candidate acceptance |
|---|---|---|
| Single short `你好，世界！` | Recorded `Hello, world!` | Exact output retained on repeated calls. |
| Multiple `。` sentences | Recorded two segments / English sentences | Same source order and all propositions; no omitted/duplicated sentence. |
| Steel cup / 500 ml description | Recorded material, capacity and intended use preserved | Preserve material, 500 ml, travel/daily use; include names, model numbers, `USB-C`, decimals/versions and URLs. |
| Chinese quotes/`！？`/ellipsis | MiniSBD groups `你好！你好吗？我很好。` into one segment; owned rules will likely split three | English wording can differ; greeting/question/answer remain in order. Review quote and punctuation effects. |
| Mixed Chinese/English | `fast charging` historically becomes `past charge` | No new omissions or changed critical numbers/names; document inherited mistranslation separately. No promise to repair the model. |
| Newlines/paragraphs | Ordinary paragraph newline retained | Same LF paragraph contract; test blank lines, CRLF and whitespace-only paragraphs and report any existing normalization. |
| Long input | 40 short sentences pass; no evidence for one >1,024-piece sentence | Test unpunctuated, clause-heavy and mixed strings across 255/256/257, 1,023/1,024/1,025 and >2,048 pieces within wire limits. Every final chunk respects actual token budget; unique ordered markers at head/middle/tail survive representative real-model tests. Instrument token submission to distinguish model omission from adapter loss. |
| Empty/whitespace | Empty result is `""` | Empty result unchanged, no spurious native work; whitespace follows documented paragraph behavior. |
| Unicode input/paths | Transport/path tests pass; baseline model drops part of `café 😊` input | Exact original-string source coverage, no added Unicode normalization or path failures. Preserve known model loss as a limitation, not a new transport failure. Test accented/Chinese/emoji model, state and executable paths independently and together. |

For the finite reviewed corpus require **zero newly lost/repeated/reordered sentences or critical factual fields**, exact greeting/empty outputs, and all baseline semantic assertions. Review every changed translation/segmentation with paired evidence before adoption; one new critical loss blocks it. Target-output coverage cannot be proved by English substring counts alone. Unit tests use a deterministic fake translator for exhaustive span/order/retry/cap invariants; real-model bilingual review supplies semantic evidence. Repetition tests must use distinct numbered clauses too, so repeated boilerplate cannot conceal an omitted tail or reordered sentence.

Run protocol/unit/failure tests and actual production CLI/worker integrations with MiniSBD/ONNX absent and empty isolated caches, before any candidate freeze. Verify native translator/tokenizer reuse, no source/translation logging, no network/process attempts from before imports through readiness/translation, unchanged unsupported-pair behavior, health recovery/error behavior, sequential framing, EOF, broken pipe and shutdown. Re-run immutable provisioning, interrupted validation, concurrent provisioning, receipt corruption and Unicode-tokenizer tests. Check output-cap saturation, deterministic retries, extreme tokenizer expansion and a failing indivisible unit. Do not return partial successful output.

### 6. Artifact-level acceptance, not metadata-only evidence

After source gates pass and implementation is authorized, produce a new separately named diagnostic build. Extend existing `scripts/audit_windows_package.py`, `scripts/validate_windows.py`, compliance staging and tests:

1. Bind build inputs/source patches/wheels/locks and every distributed file to SHA-256. Extract/read the actual EXE CArchive, every embedded PYZ (using the existing archive reader), bootstrap/runtime-hook code, `base_library.zip`, nested archives and loose bytecode/data. Compare against freezer TOCs, but do not accept TOCs alone as proof.
2. Enumerate and decompress every Python code entry; map it to owned source or exact approved supplier source/wheel. Reject MiniSBD module roots, renamed/vendored MiniSBD implementations, unresolved code ownership, unexpected imports and AGPL-licensed supplier code even when never loaded. Name/AGPL-string scans are supplementary signals, not proof. Retaining license text in a historical evidence dossier does not itself mean executable AGPL code is bundled; classify content/form explicitly.
3. Inventory every DLL/PYD and PE regular/delay import, collection origin/hash, exact supplier grant and available static-link BOM. Map all native/data payloads and incorporated code to reviewed components; inspect renamed DLLs and supplier notices. Unknown ownership/static license scope is **pending**, never inferred permissive from parent-package metadata. Review bootloader/GCC exceptions explicitly. Reject additional non-excepted GPL or any AGPL code; preserve all other license requirements.
4. Audit both onedir and final candidate ZIP/compliance assets for identical file inventories/hashes, no hidden AGPL code, model archives/ONNX, developer caches or accidental sources from retired dependencies. Match all residual components to the new compliance inventory; remove retired component rows only with evidence, retaining the old inventory as baseline history. Use negative audit fixtures containing a MiniSBD PYZ entry, loose/renamed copy, native/unmapped payload and stale archive to prove checks fail closed.
5. Run frozen CLI provisioning and persistent worker requests after relocation, with network attempts observed/denied, no developer Python/global Argos and no MiniSBD/ONNX dependency. Validate Unicode/protocol/error/lifecycle cases against the exact audited candidate. Snapshot loaded native origins and distinguish OS contracts from bundled DLLs/external host injection. Keep host-only instrumentation limitations visible. Final Level B still needs clean Windows 10 22H2/Windows 11 rows and OS-denied networking on the same candidate/model hashes.

Acceptance report must state **AGPL absence established** only when full code/native/data reconciliation passes. It must separately list GPL exceptions and remaining compliance gates. A module denylist, `pip list`, lock grep, successful execution or absence from loaded modules is insufficient.

### 7. Affected files and interfaces

| Area | Expected implementation changes |
|---|---|
| Backend/config | `backends/argos.py`, new `backends/segmentation.py`, `config.py`: explicit injected splitter/policy, dependency identity checks, warm-up, cap retry/error mapping; preserve path isolation. |
| Tokenizer | `backends/tokenizer.py`: retain bounded serialized loading and Argos encode/decode. Add bounded token counting/span interfaces only if necessary; no normalization change. |
| Worker info | `service.py`, corresponding protocol examples/tests: truthful policy and patched Argos version values, unchanged v1 shape. `worker.py`/framing should need regression coverage only. |
| Assets/CLI | `assets.py`, `provision.py`, `__main__.py`, `scripts/acquire_assets.py`, `models/provenance.json`: model-only schema-2 path, obsolete flag guidance, active/historical asset distinction. |
| Dependency supply | `pyproject.toml`, `requirements.lock`, `requirements-dev.lock`, `packaging/argos-upstream.json`, `packaging/argos-build.lock` if build inputs change, new explicit patch, `scripts/build_argos_wheel.py`, `scripts/setup_environment.py`, `scripts/verify_dependency_locks.py`, identity/lock tests. |
| Packaging/compliance | `packaging/worker.spec`, `packaging/compliance-inventory.json`, `scripts/{build_windows.py,audit_windows_package.py,validate_windows.py,stage_compliance.cjs}`, related tests only where graph/CLI/audit assumptions change. Rebind compliance material hashes; keep unresolved statuses. |
| Tests/docs | Existing `tests/unit/test_backend.py`, `test_tokenizer.py`, `test_dependency_identity.py`, `test_package_audit.py`, `tests/integration/test_minisbd.py` (retain history, replace candidate assumptions with segmentation coverage), new focused splitter/cap/audit tests; README, model/manual/CMD/development/Argos/native/compliance/release guidance. Add a new migration report linking historical spike/manual evidence instead of overwriting it. Release manifest schema/examples are future baseline release tasks, not currently existing files. |
| OpenSpec | These four capability deltas and tasks; no edits to 001 completion boxes or original evidence. Later archive ordering must honor 001's not-yet-canonical baseline. |

## Risks / Trade-offs

- [Heuristic boundaries change neural context and translation] → paired semantic corpus gate before lock/freeze adoption; pySBD comparison if needed; retain baseline on failure.
- [Hard splitting harms a very long name or clause] → prefer punctuation/space, preserve original spans, conservative token budget, explicit documented long-text quality limits and critical-field review.
- [Model itself drops/repeats content or ends early] → distinguish adapter source coverage from semantic quality, check decoder saturation and real head/middle/tail facts. Early EOS is not detectable as correct translation by a cap check.
- [Small Argos fork adds maintenance] → one explicit patch with base and output hashes, narrow API tests, distinctive version, source delta/notices; upstreaming later is optional, never a dependency on a future release.
- [Retries cost CPU on adversarial input] → finite halving, no full-input quadratic token scan, max-wire-size tests and request-level resource observations; no unbounded native queues or target length.
- [No measured lightweight improvement yet] → compare candidate ZIP/extracted bytes, init/idle/peak working set/private bytes and latency to the same-host baseline. Candidate must add no neural/native dependency and must not exceed baseline extracted bytes or measured runtime peak beyond run-to-run baseline variation. Collect at least five comparable warm/cold-process samples; document cache/host limits. Investigate regressions before adoption; do not claim a size/RAM saving from graph reasoning alone.
- [Hidden incorporated code defeats a simple AGPL scan] → supplier/static BOM and ownership reconciliation; unresolved evidence blocks the absence claim. Microsoft/Intel rights, MPL source and Apache notices remain separate.

## Migration Plan

1. Preserve the exact baseline environment/artifact/model/ONNX/receipts and evidence; inventory current tracked/ignored state. Do not touch the running installation. Capture controlled comparison evidence in new paths.
2. In a disposable candidate environment, implement the narrow Argos patch and owned segmenter/policy; first run span, capacity and real-model quality/absence tests. If these fail essential acceptance, stop migration and record why retaining MiniSBD is preferable. Any pySBD fallback gets its own reviewed pin and updated design.
3. Only after source acceptance, generate new hash locks/wheel provenance, update model-only provisioning and documentation, and repeat production-path tests. The candidate uses a fresh model directory and fresh receipt schema; legacy bytes stay unchanged.
4. Build a separately named candidate, audit its actual archives/native/data files and run frozen regression, resource comparison and a new manual walkthrough. Preserve original Level A as historical; do not transfer its pass result to the candidate.
5. Proceed to public-release preparation only with the migration recommendation confirmed by evidence. Keep existing Level B requirements, other compliance tasks and explicit publication approval outstanding.

**Rollback:** stop the candidate process gracefully; launch the retained baseline executable/environment with its original model/state paths and legacy receipt/ONNX. Restore baseline code/lock/provenance as a coherent version-controlled set if adopted changes must be reverted; never make the new worker silently fall back to MiniSBD or read legacy installations. Keep the rejected candidate and paired evidence for diagnosis. Any baseline redistribution still requires its original AGPL/native compliance path; rollback is not release approval.
