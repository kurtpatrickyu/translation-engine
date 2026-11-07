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
  and explicit unresolved obligations. `sources/` contains original MiniSBD/tqdm
  source archives; `../LICENSES/` holds collected supplier texts.
- `release-candidate.json` pins binary-source and materials commits, compliance
  manifest, external asset metadata and regression evidence.
  `release-manifest.schema.json` defines the candidate contract;
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

Distribute no external model/ONNX binaries or caches. Preserve provenance and
attribution without claiming model clearance. MiniSBD remains AGPLv3; source and
notice preparation does not settle all native rights or source obligations. The
[release workflow](../docs/releasing.md) prepares local acceptance
artifacts only. For initial v0.1.0, Windows 10 acceptance, OS-denied networking,
source/native clearance and publication remain separate gates. Windows 11 is
expected compatible but UNTESTED; separate acceptance is waived for v0.1.0 and
optional future validation. Follow the [scope decision](../docs/releasing.md).
