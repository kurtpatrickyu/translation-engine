# Source availability for the Windows worker

The project's own code retains the MIT grant in [LICENSE](LICENSE). The frozen
worker also includes MiniSBD 0.9.5 under AGPLv3 and other separately licensed
components. The complete bundled worker must not be described as MIT-only.
The chosen distribution strategy is to retain MiniSBD and supply corresponding
source with the worker, preserving compatible upstream grants and notices.

Primary worker source: <https://github.com/kurtpatrickyu/translation-engine>.
A future GitHub Release must identify an immutable full commit (optionally also
an immutable release tag) whose worker/build inputs match the executable. A
development branch or GitHub's moving default source link is insufficient.
No release/tag has been created for this preparation.

For each executable download, provide an adjacent, no-extra-charge
`translation-engine-corresponding-source.zip` and
`translation-engine-compliance.zip` on the same GitHub Release. Tell recipients
where these are in the release description and include this document with the
worker. This is the planned AGPL section 6(d) delivery mechanism, not a promise
to furnish source only on request. Preserve access for as long as the executable
is offered. Verify the public source and asset URLs before publication.

The compliance package's `sources/worker/` contains the individually hash-pinned
application source, PyInstaller spec/entry point, locks, Argos upstream identity
and wheel recipe, setup/build helpers, protocol definitions and build/install
instructions. `evidence/build.json` records the original build input hashes.
The original build's compliance inventory is historical build metadata; the
active `evidence/component-inventory.json` describes this preparation. Its only
build-input relocation preserves the original metadata bytes and hash.

`sources/minisbd/minisbd-0.9.5.tar.gz` is the publisher's complete 0.9.5 source
distribution, SHA-256
`b40d0a32ad0b3aeb8477e06a9e4723b7fa34a30121731f6a5063d39b7b3a464e`.
All nine Python source files match the locked wheel byte for byte. Every frozen
MiniSBD module matches compilation of those sources. No local MiniSBD changes
were found. A GitHub revision is deliberately not asserted: the exact PyPI
source distribution, wheel digest and per-file matches establish correspondence.
Its original README, build declaration, LibreTranslate/Piero Toffanin attribution,
AGPL text and inherited Stanza copyright, Apache notice and credits are retained.
The inherited changes are upstream MiniSBD changes, not changes by this project.

`sources/tqdm/tqdm-4.70.1.tar.gz` and the selected `.py` files supply the matching
MPL-covered source. Preserve tqdm's complete attribution/license notice and
the full MPL 2.0 text in `licenses/tqdm/`. Recipients may obtain and modify that
source under its applicable MPL/MIT terms; no local tqdm changes were found.

`sources/argostranslate/` preserves the exact approved Argos commit archive;
`sources/worker/packaging/argos-upstream.json` pins its archive and wheel hashes.
Other frozen Python preferred-source files are under their component directories.
`manifest.json` binds component versions, source identities and staged bytes;
`SHA256SUMS` covers all files except itself. See [rebuilding instructions](docs/rebuilding-worker.md).

Preparation currently targets `diagnostic-20261107-211131`, EXE SHA-256
`ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
319 Python modules compare equal after recursively normalizing only filenames.
This does not establish native/static source completeness. Before publication,
finish the native source/notice mappings and supplier permissions in
`BLOCKERS.txt`, include any further required covered dependency sources or
evidence-backed exclusions, and bind the final release commit and source assets
to the final executable. The current package does not claim full corresponding
source fulfillment or legal clearance while these items remain unresolved.

Translation `.argosmodel` files, MiniSBD ONNX models, caches and downloads of
models are not distributed. Their upstream identities/URLs/expected hashes
remain in `models/provenance.json`; recipients acquire them separately. Model
license status is not changed by these code materials. The official Microsoft
VC++ v14 x64 Redistributable is a separately installed prerequisite, obtained
from <https://aka.ms/vc14/vc_redist.x64.exe>. The four ordinary runtime DLLs and
the installer are not bundled. NumPy's renamed Microsoft DLL is still bundled
and its separate provenance/permission question remains unresolved.
