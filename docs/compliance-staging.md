# Candidate compliance staging (task 5.3 preparation)

This workflow stages licensing and available source material for the exact
existing `diagnostic-20261107-133601` worker. It does not rebuild, repack, execute
or modify the worker, fetch dependencies/models, approve licenses, or publish.
The dependency graph remains unchanged. See [redistribution review](redistribution-review.md)
for the legal/source decisions that still gate release.

## Generate and inspect from Windows CMD

Change 003 uses an [external official x64 VC runtime](native-dependencies.md#external-vc-prerequisite-for-change-003)
for new candidates. This staging workflow/inventory remains bound to the old
diagnostic and its 180 files. Do not remove its ordinary-VC ownership entries or
substitute candidate hashes without the separate PUBLIC candidate-rebinding work.
The new diagnostic build/regression need not wait for that work. NumPy's renamed
DLL, Intel OpenMP, AGPL source/notices and all actual bundled-material blockers
remain independently required. No Microsoft installer is staged or redistributed.

Run from the repository root with an existing **Node.js 22 or later** installation.
No npm packages are needed. Node is a maintainer tooling requirement only; the
worker does not require it. This runner was chosen because the review account
cannot launch the existing Store-backed `.venv` Python. No engine changes or
environment repairs are needed to use it.

```bat
node --version
node --test tests\compliance-staging.test.cjs
node scripts\stage_compliance.cjs candidate-staging\diagnostic-20261107-compliance
echo %ERRORLEVEL%
type candidate-staging\diagnostic-20261107-compliance\BLOCKERS.txt
type candidate-staging\diagnostic-20261107-compliance\THIRD_PARTY_NOTICES.txt
node scripts\stage_compliance.cjs --check candidate-staging\diagnostic-20261107-compliance
echo %ERRORLEVEL%
```

Use a new directory name for every generation; existing outputs are refused,
including incomplete earlier attempts. Outputs must be descendants of the ignored
`candidate-staging/` root. Build/dist and arbitrary output paths are rejected.
Do not upload this preparatory directory as a release asset.

Exit codes:

| Code | Meaning |
|---|---|
| 2 | Staging/check completed with valid integrity, **readiness remains blocked**. This is the expected result for the current preparatory scope. |
| 1 | Invalid/stale candidate or inventory, unsafe input/output, or staged integrity failure. Inspect the error and preserve the failed directory for diagnosis. |

The CLI deliberately never returns a successful release-readiness result. Both
`compliance_ready` and `release_ready` are always false in this preparatory tool.
Changing those fields in its output fails verification. Missing/changed
supplier material does not disappear silently: configured required material
that cannot be copied is recorded as a material blocker and the component becomes
incomplete. Candidate identity/coverage failures stop generation before writes.

`--check` validates staged hashes, byte counts, exact file coverage, inventory/tool
identity, required-material accounting, preserved blockers, checksums and the
unchanged candidate/build inputs. It does not re-download supplier material or
require the original supplier files to remain available after staging. It cannot
establish legal approval or source-host availability.

## Inputs and maintenance

[packaging/compliance-inventory.json](../packaging/compliance-inventory.json) is
the reviewed, candidate-specific input, not generated automatically by the stager.
It contains 31 component entries covering the 17 frozen third-party Python
distributions, the project, Python, PyInstaller runtime and identified native or
statically incorporated component groups. Each entry records name/version,
redistributed form, license identity/evidence, source obligation, source identity,
source/license paths and hashes, status, blockers, frozen file ownership and
Python module roots. Native versions that remain unknown are labelled unresolved,
not represented as independently verified pins.

`verified` means the recorded identity/material facts are verified for this
preparation, **not that redistribution is legally cleared**. `incomplete` and
`blocked` entries carry specific reasons. Global obligations remain blocking even
for components with verified permissive-license facts. Source completeness is
not claimed by this workflow.

The inventory pins the audit/build/PYZ/EXE-table evidence, candidate EXE and ZIP
identity, exact frozen file ownership and module roots. The stager rehashes all
180 worker files, checks for unexpected/missing files, verifies the successful
audit/build records, and rehashes the 21 original build inputs. Candidate-specific
PYZ table identity and module roots are checked; the stager does not independently
decompile the executable or reconstruct its original compilation. The retained
audit is the trusted link to the embedded PYZ. Preserve that evidence dossier.

Supplier wheel hashes are present in the existing candidate locks. The inventory
also pins each selected archive member's hash. License texts/notices and available
MiniSBD/tqdm Python sources are read directly from those exact cached wheels,
without executing their code. Moving branches are not used. The installed
PyInstaller license/hooks and Python supplier license have separately observed
file hashes; those observations do not establish missing supplier grants.

The inventory includes the observed Store Python supplier `LICENSE.txt` path.
On a machine where it is unavailable, generation records a material blocker.
Do not substitute a generic upstream Python license: the supplier text includes
additional Windows binary terms. A future reviewed relocation must preserve and
pin the same applicable supplier evidence.

To support a different candidate, explicitly review its new audit, frozen graph,
build inputs, wheel/source identities and license provenance; then update the
inventory and tests. Do not simply learn current hashes from mutable installed
files to bypass a mismatch. `null` source revisions/checksums mean unavailable
identity evidence. Argos is the exception with an already reviewed exact commit,
source archive hash and wheel mapping. The staging script has no acquisition,
inventory-regeneration, dependency-resolution or license-election operation.

## Output layout

| Path | Content |
|---|---|
| `licenses/` | Supplier license and third-party notice texts copied byte-for-byte. |
| `sources/argostranslate/` | Original hash-pinned Argos source ZIP; valid relative source symlinks remain inside the original archive, never extracted. |
| `sources/minisbd/`, `sources/tqdm/` | Available `.py` source members from the exact locked wheels; complete corresponding-source scope/delivery not asserted. |
| `sources/worker/` | Exact original build inputs, Argos wheel recipe and explicitly selected build/install/provenance documentation. |
| `sources/pyinstaller/` | Three collected runtime-hook source files. |
| `evidence/` | Original candidate audit/build/freezer tables, distribution metadata, reviewed inventory and the running stager's source. |
| `THIRD_PARTY_NOTICES.txt` | Component/license/material index; does not replace full supplier texts. |
| `BLOCKERS.txt` | Human-readable exact unresolved obligations and missing/changed material failures. |
| `manifest.json` | Deterministic input/component/blocker/file manifest with SHA-256 hashes and byte counts. No timestamp or output-directory dependence. |
| `SHA256SUMS` | All staged files including the manifest, except itself. No manifest self-hash. |

The ZIP reader is bounded and read-only. Whole source archives are checked for
model members; selected wheel members may be read from wheels containing unselected
sample datasets, but those datasets are never copied. Plain `.argosmodel` and
`.onnx` staging paths are rejected. No complete wheel or worker binary is copied
as a compliance asset. External model attribution and digests remain solely in
the preserved provenance JSON; this is not model license clearance.

## Demonstrated result and remaining blockers

Recorded run: `candidate-staging/diagnostic-20261107-compliance/`, with an identical
second run at `candidate-staging/diagnostic-20261107-compliance-repeat/`.

- 31 component entries; 180 worker files hash-verified and owned; all 17 known
  third-party frozen distribution roots covered.
- 136 payload files, plus manifest and checksum file: **138 staged files**.
- 40 license/notice files; 17 distribution metadata files; 40 available MiniSBD/tqdm
  Python source files; one original Argos source archive; three PyInstaller hook
  sources; 21 original build inputs, Argos recipe and selected documentation/evidence.
- All configured material copies succeeded; **25 review/approval blockers remain**.
  Ten inventory components have verified preparation facts, 18 are incomplete,
  and three are blocked. These counts are not a legal-clearance score.
- All 12 focused automated tests pass; generation and `--check` both return expected code
  2. Repeat outputs are byte-for-byte identical. No worker or original build/dist
  evidence bytes changed. No external model files were staged.

Recorded manifest SHA-256:
`60f717a04f52443ae65bbcda837d1f067c99af776d96a7f686e345ab7981d9d6`.
This binds the demonstrated staging output, not a published release or legal approval.

The exact reasons are recorded in `BLOCKERS.txt`; the unresolved acceptance work is:

| Area | Remaining evidence/decision |
|---|---|
| AGPL / delivery | Maintainer/legal approval of covered-work boundaries, complete Corresponding Source/build/install scope and exclusions; recipient source-delivery/availability and full frozen-source correspondence. |
| MiniSBD | Exact source revision and inherited Stanza source/notices; available wheel Python files alone do not settle completeness. |
| tqdm | Approve matching frozen-source correspondence and MPL recipient source availability; the wheel Python sources are now locally available. |
| Microsoft ordinary DLLs | Approved acquisition, licensed entitlement, matching product terms and servicing for four System32-collected DLLs. |
| Microsoft NumPy copy | Renamed MSVCP repair/redistribution provenance and downstream entitlement. |
| Intel | Exact OpenMP supplier grant, redistribution designation, notices and compatibility. |
| CTranslate2 / SentencePiece | Version-matched primary license texts are absent from cached wheels; obtain them with reviewed provenance. Reconcile static MKL/oneDNN/spdlog/pybind11 and protobuf-lite/Abseil sources/notices as applicable. |
| ONNX Runtime | License and full third-party notices are staged; exact CPU build BOM, applicability of Intel/nonpermissive terms and any embedded source duties remain unresolved. |
| NumPy / OpenBLAS | Full available license tree is staged; resolve GCC exception eligibility and exact OpenBLAS/LAPACK/compiler runtime revisions. |
| CPython / support libraries | Supplier license is staged; review Microsoft binary conditions and incorporated versions/notices (Expat, libmpdec, bzip2, XZ, zlib), exact OpenSSL notices, actual libffi build and SQLite dedication evidence. |
| Other frozen components | charset-normalizer compiled-runtime notices; joblib/loky/copied CPython notices; sacremoses inherited data attribution; PyYAML/LibYAML build/notices; complete PyInstaller Apache-hook text/notices and source mapping. |
| Other public gates | Clean Windows rows, OS-denied networking, target measurements, final integrity/material assembly and explicit publication approval remain separate tasks. |

Task 5.3 preparation is implemented; its reviewed delivery/acceptance gate stays
unchecked. Level A stays 37/37 and Level B stays 0/17. The smallest next task is
to obtain and pin the missing exact-version CTranslate2/SentencePiece license
texts and complete PyInstaller Apache runtime-hook notices, then regenerate this
staging set. Maintainer/legal/native-provenance decisions proceed separately.
