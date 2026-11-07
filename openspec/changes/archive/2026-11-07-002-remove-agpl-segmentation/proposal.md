## Why

The working standalone worker freezes MiniSBD 0.9.5, whose AGPLv3 grant is independent of Argos Translate's MIT license. Before further public-release preparation, replace that dependency if a bounded, deterministic Chinese sentence splitter can preserve the essential offline translation behavior established by `001-build-offline-translation-engine`.

## What Changes

- Retain direct Argos translation, CTranslate2 4.8.5, SentencePiece 0.2.1, the exact Chinese-English model archive, and protocol v1. Introduce an engine-owned sentence splitter with Chinese punctuation rules, paragraph handling, and actual SentencePiece token limits.
- Use a narrowly patched, distinctly identified Argos wheel based on approved commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`: optional/lazy MiniSBD integration, explicit sentence-splitter injection, and a bounded inference seam. Remove MiniSBD from default dependencies. No import stubs, copied MiniSBD algorithms, process-wide monkey patches, or hidden bundled AGPL code.
- **BREAKING provisioning change:** new installations require only the original `.argosmodel`; remove `--sbd-file` from the candidate CLI and require a new receipt/layout version in a separate models directory. Preserve existing installations and original assets for rollback.
- Regenerate locks and rebuild only during separately authorized implementation, after source/real-model acceptance. Remove ONNX Runtime and orphaned dependencies only when the resolved graph proves them unused.
- Require artifact-level proof of no AGPL code, complete Python/native/data ownership mapping, quality comparison, and frozen offline/Unicode/lifecycle regression. Existing GPL runtime exceptions remain explicitly identified; this is not a promise of a GPL-free or permissive-only bundle.
- Preserve all completed Level A evidence. The new candidate needs its own evidence; Level B and remaining Microsoft/Intel/MPL/Apache/model obligations remain open.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `offline-argos-translation`: replace mandatory MiniSBD resources with bounded local segmentation, reject silent truncation, and revalidate the replacement runtime.
- `model-provisioning`: model-only provisioning with versioned immutable receipts and unchanged archive integrity.
- `windows-worker-distribution`: independently validate the new AGPL-free candidate and its actual frozen contents.
- `release-artifacts`: remove the ONNX requirement from new manifests and establish evidence-backed AGPL absence without clearing other obligations.

These capabilities currently live in change 001; `openspec/specs/` is empty. The delta files explicitly target those baseline requirements. Do not edit/archive 001 as part of this proposal. When archiving later, materialize/reconcile 001 first, then apply these deltas in order; do not archive 002 against an empty canonical baseline.

## Impact

Likely implementation surface: `src/translation_engine/{config.py,assets.py,provision.py,__main__.py,backends/argos.py}`, a new owned segmentation module, the existing Unicode tokenizer adapter, `pyproject.toml`, both dependency locks, Argos source identity/build recipe/patch and lock verifier, `packaging/worker.spec`, asset acquisition/provenance, compliance inventory/staging, packaging audits/validators, regression tests, manifest schema/examples, and manual/development/provisioning documentation. See `design.md` for exact call paths, evidence, tradeoffs and gates.

Recommendation: **worth implementing before final public-release candidate assembly**, starting with the blocking source/quality experiment. Source inspection establishes a feasible small extension seam, not measured equivalence. If source coverage, representative translation quality, resource use or artifact audit fails, retain the existing worker and pursue its explicit AGPL compliance path; do not weaken acceptance to force removal. Freya Automations remains separate and unchanged. This change contains planning artifacts only.
