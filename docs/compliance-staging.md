# Candidate compliance staging (task 5.3)

The existing stager now targets the latest validated post-003 candidate,
`diagnostic-20261107-211131`: **176 files, 49 native binaries, 17 third-party
Python roots, 30 component groups**. It rehashes the actual onedir, original
build/freezer/audit evidence and candidate ZIP. No executable rebuild, repack,
translation, dependency change, model acquisition or publication is performed.
The older 180-file diagnostic is retained only as historical evidence and the
original monitored build helper's native-retention baseline.

See [source availability](../SOURCE_AVAILABILITY.md),
[third-party notices](../THIRD_PARTY_NOTICES.md),
[rebuilding instructions](rebuilding-worker.md), and original
[redistribution review](redistribution-review.md). The decision to keep MiniSBD
and supply AGPL corresponding source is established. Native permissions and
unverified supplier/source mappings remain publication blockers.

## Generate and verify

Use Node.js 22 or later from the repository root; no npm packages are required.
The ignored candidate evidence and exact cached wheels named by the single
[compliance inventory](../packaging/compliance-inventory.json) must be retained.
The tracked `LICENSES/` and `packaging/sources/` supply collected supplier texts
and the MiniSBD/tqdm original source distributions.

```bat
node --test tests\compliance-staging.test.cjs
node scripts\stage_compliance.cjs candidate-staging\post003-source-notices
node scripts\stage_compliance.cjs --check candidate-staging\post003-source-notices
```

Use a fresh destination below `candidate-staging/`; existing destinations are
refused. Exit **2** means valid preparation with readiness still blocked; exit
**1** means invalid/stale evidence or failed integrity. The stager deliberately
cannot declare release/compliance readiness. No worker or original build/dist
bytes are changed. Repeated outputs are deterministic, without timestamps or
output-directory identity. Review `BLOCKERS.txt`, `manifest.json`, the original
license texts and source correspondence evidence before using any material.

`--check` verifies exact staged file coverage, hashes/sizes, source/material
pins, required-material accounting, retained blockers, candidate identity,
source correspondence and checksums. It cannot prove legal permission or that
future GitHub source download links work. Missing required materials become
explicit blockers. Candidate/source/hash mismatches stop staging before writes.

## Source and license evidence

- MiniSBD 0.9.5: original PyPI sdist SHA-256
  `b40d0a32ad0b3aeb8477e06a9e4723b7fa34a30121731f6a5063d39b7b3a464e`;
  all nine Python members byte-identical to the exact locked wheel. Preserve
  AGPLv3, original README/pyproject, Stanza CREDITS and Apache copyright/license.
  No local modifications; no unverified GitHub revision is asserted.
- tqdm 4.70.1: original PyPI sdist SHA-256
  `cefd0eca11b2a37a3aee776544d4f4ae913f02688135b5556b8788dfa474afc4`;
  wheel Python members identical. Preserve its MPL/MIT attribution and full MPL
  text. Matching source accompanies the preparation rather than a moving link.
- Embedded source comparison: 319 Python modules, including all 17 frozen
  third-party distribution roots, worker source and PyInstaller runtime modules/
  hooks, compile equal after recursively normalizing only `co_filename`.
  `scripts/verify_frozen_sources.py` reads actual embedded code; it does not
  execute package code. Run with the existing build interpreter:

  ```bat
  scripts\python.cmd scripts\verify_frozen_sources.py --report runtime\new-source-correspondence.json
  ```

- Wheel payload comparison: 131 frozen wheel-supplied files matched original
  wheel bytes. Installation-generated RECORD files are not wheel byte matches;
  they remain included in the audit's complete 176-file hashes. Matching Python
  code is not evidence of native/static source correspondence.
- Original supplier texts are retained byte-for-byte in `LICENSES/`, with
  provenance and SHA-256 in each material record. This includes ONNX Runtime's
  complete supplier notices and NumPy's complete wheel license directory,
  CTranslate2 v4.8.5 primary MIT text, SentencePiece 0.2.1 sdist primary and
  dependency licenses, CPython's actual Store-supplier license/history/notices,
  and PyInstaller COPYING/exception, runtime source headers and full Apache text.
  Missing binary-to-supplier mapping remains explicit; collecting a license text
  does not clear the corresponding native bytes.

## Exact build input preservation

The original build hashed the then-current compliance inventory as non-runtime
metadata. Before editing it, its exact original bytes were preserved at
`runtime/compliance-preparation/original-build-inventory.json`. The active
inventory records one narrowly allowed relocation for this input. The stager
verifies the original build hash and stages those bytes at their original path
under `sources/worker/`. Runtime/source/spec/lock pins have no such exception.
All other original build inputs are still required to match. Current compliance
metadata is staged separately at `evidence/component-inventory.json`.

This avoids a self-referential inventory hash and does not rewrite historical
build evidence. Retain this original input with the local dossier; it is also
available from the generated source package. No second active inventory is used.

## Output and future GitHub Release layout

| Path | Content |
|---|---|
| `licenses/` | Unmodified supplier license/notice texts. |
| `sources/minisbd/`, `sources/tqdm/` | Complete original versioned sdists and selected preferred Python source. |
| `sources/argostranslate/` | Exact commit source ZIP and matching frozen Python source. |
| `sources/<component>/` | Preferred source for other actually frozen Python modules, plus runtime hook/loader sources. |
| `sources/worker/` | Exact build inputs, setup/build helpers, protocol/usage/build instructions, unit tests and original retention baseline. |
| `evidence/` | Candidate audit/build/PYZ/EXE tables, frozen-source and wheel correspondence reports, distribution metadata, active inventory and stager. |
| `SOURCE_AVAILABILITY.md`, `THIRD_PARTY_NOTICES.md`, `docs/rebuilding-worker.md` | Recipient source/license/build instructions. |
| `THIRD_PARTY_NOTICES.txt` | Deterministic component/material index. |
| `BLOCKERS.txt` | Concise unresolved obligations and material failures. |
| `manifest.json`, `SHA256SUMS` | Component/source identities and every staged file hash/size; no self-hash. |

For a future release, attach the compliance package and complete corresponding
source beside the worker ZIP, with an immutable matching public commit and
explicit source links in the release description. Preserve original source
archives and source/build/install materials. Complete the native/source gates
before calling this full Corresponding Source. Do not publish this preparatory
output as an approved release or silently bind it to a repackaged executable.

ZIP and tar/gzip member inspection rejects external model binaries and unsafe
paths/links. No complete wheel, worker executable, model, cache or installer is
staged. External asset identities/URLs/expected hashes remain metadata only.
The official VC++ x64 runtime is a separately installed prerequisite: the four
ordinary DLLs have no ownership entries in this candidate. NumPy's renamed
Microsoft DLL remains inventoried and unresolved.

## Remaining task 5.3 gates

MiniSBD/tqdm exact-source mechanics and collected Python notices are prepared.
Final publication still requires immutable public source delivery tied to the
final executable; any missing covered native/dependency source or justified
exclusion; Intel OpenMP terms/notices, NumPy's wheel-local Microsoft permission,
and remaining native/static-library supplier attribution/source mappings.
`BLOCKERS.txt` preserves the component-specific details. No permission is marked
legally cleared. Task 5.3 remains unchecked; unrelated Level B tasks are unchanged.

## Verified preparation result (2026-11-07)

Final local output: `candidate-staging/post003-release-materials/`; independent
repeat: `candidate-staging/post003-release-materials-repeat/`.

- All **17 focused Node tests pass**; OpenSpec strict validation passes.
- Generation and `--check` return the expected **2**, with **zero missing-material
  failures** and **19 retained review/source-delivery blockers**.
- **470 payload files / 472 total files**, including 52 original license/notice
  files plus the generated notice index. The complete repeat is byte-identical.
- The finalized embedded-source verifier again matches **319 modules**, with
  zero mismatches; its report is byte-identical to the pinned initial report.
- Candidate onedir, ZIP and original build-source pins still verify; no model
  binary or installer is staged. No original build/dist evidence was rewritten.

Final manifest SHA-256:
`4caf7ea74c028b05ca75d798ea93b6e49a9fbf78488ce97bd80fa8601b295308`.
This identifies the preparatory package, not a public release or legal approval.
