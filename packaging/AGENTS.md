# Frozen distribution and candidate metadata

`worker_entry.py` delegates to the same `translation_engine.__main__.main` as
source execution. `worker.spec` builds a console PyInstaller **onedir** bundle:
retain the full directory, explicit distribution metadata required by backend
version checks, and targeted standard-hook behavior. Do not add broad collection
hooks without a demonstrated frozen failure. Stanza, Torch and spaCy are excluded.

The spec excludes exactly `msvcp140.dll`, `msvcp140_1.dll`, `vcruntime140.dll` and
`vcruntime140_1.dll`. The official separately installed VC++ v14 x64 runtime is a
prerequisite; preserve NumPy's differently named wheel-local Microsoft DLL. Do not
bundle an installer, auto-install prerequisites or treat ordinary VC DLLs as OS
components. Target machines need no Python or Node. See
[runtime requirements](../README.md) and
[rebuilding instructions](../docs/development.md).

## Metadata ownership

- `argos-upstream.json` pins exact upstream source and wheel identities;
  `argos-build.lock` pins the source-wheel build toolchain. Same-version artifact
  substitutions are rejected by setup and tests.
- `compliance-inventory.json` is the active candidate component/material/evidence
  inventory. Preserve exact file ownership, supplier bytes, source correspondence
  and classified review findings. Its `release_review` distinguishes mandatory
  conditions and material decisions from informational research. `sources/` contains
  original source archives and supplier build/terms evidence; `../LICENSES/` holds
  collected supplier texts. Preserve their original bytes using `.gitattributes`.
- `release-candidate.json` pins binary-source and materials commits, compliance
  manifest, external asset metadata and regression evidence.
  `release-manifest.schema.json` defines the candidate/prepared stable contract;
  `release-manifest.example.json` records an actual example, not a public release.
  Reconcile schema/config/example/assembler/tests when that contract changes.

Do not change historical executable/source hashes just because current docs or
tooling changed. The compliance inventory has one documented relocation for its
original build-input bytes; it is not permission to relax runtime/spec/lock pins.
Build input hashing includes top-level packaging files. See
[release evidence](../docs/releasing.md) for original-input handling and
source-versus-assembly identity. Changed executable inputs need a new build and validation.

`sources/candidate-documentation/` preserves exact historical material bytes at
the inventory's original hashes. Current docs may change independently; staging
resolves only documentation through this archive and still enforces every pin.
Inventory evidence paths referring to old guides identify these archived inputs,
not current procedures. Preserve original supplier files and machine metadata.

## Verification and release boundaries

Run root commands `scripts\test.cmd tests\unit\test_packaging_policy.py -q` and
`node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs`
for affected spec/metadata/policy changes. Frozen changes additionally require the
monitored build and explicit new native/relocation reports through the
[tooling guide](../scripts/AGENTS.md). Missing ignored dossiers are not evidence
of a passing candidate.

Distribute no external model/ONNX binaries or caches. Preserve original licenses,
notices and applicable MiniSBD AGPL/tqdm MPL source. The
[release policy](../docs/releasing.md) is authoritative for publication conditions,
platform limitations and explicit approval. Prepared manifests do not claim
approval; a separate record binds the exact verified assets and source identity.
The v0.1.0 permission deferrals are recorded as non-blocking reviews with null
dispositions; they do not establish permission. Reassess before the next release.
Research completeness and historic component status labels are not blanket vetoes.
