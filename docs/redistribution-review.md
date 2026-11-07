# Worker redistribution review

Review date: 2026-11-07. Scope: Windows x64 standalone worker, existing
OpenSpec `001-build-offline-translation-engine`, PUBLIC tasks 3.2, 4.3b and
5.3. This is an evidence review, not release authorization or legal clearance.
Only this report was created. No code, dependency, license, model, executable,
or OpenSpec completion status was changed.

## Determination

Subsequent approved decision (change 003): retain Argos/MiniSBD and satisfy the
applicable AGPL source/notices obligations; new worker builds externalize the
four ordinary VC DLLs through the official Microsoft x64 prerequisite. See
[deployment contract](native-dependencies.md#external-vc-prerequisite-for-change-003).
The historical component matrix below describes the old diagnostic, not the
new candidate. NumPy's renamed MSVCP DLL still ships with unchanged bytes and
its separate provenance requirement; Intel OpenMP and all other actual bundled
materials retain their release gates. The installer is not redistributed.
This decision does not rebind the old compliance inventory or clear PUBLIC work.

**Redistribution appears feasible, but the current diagnostic artifact is not
ready for public distribution. Recommend option A: retain the working graph and
prepare its compliance materials.** MiniSBD's AGPLv3 requires a deliberate
distribution/source strategy; MIT at the repository root is not sufficient for
the bundle. Microsoft runtime provenance and Intel runtime/static-library terms
remain release gates. Missing license texts and notices also require packaging
work. These findings do not establish that MiniSBD must be replaced.

Immediate preparation can proceed: assemble an exact-component evidence ledger,
collect version-matched license/notice files, stage matching source and build
materials, and draft release licensing/source instructions. Before publication,
the maintainer must approve the combined-work treatment and source mechanism;
qualified legal review should resolve copyleft boundaries and any proprietary
native-library incompatibility. Approved VC++ acquisition must replace the
unsubstantiated System32 collection process unless rights to those exact bytes
can be established. No public gate is completed by this report. Level A remains
37/37; Level B remains 0/17.

## Evidence and inventory boundary

Primary local inputs inspected:

- [Project declaration](../pyproject.toml), [freezer spec](../packaging/worker.spec),
  [Argos identity](../packaging/argos-upstream.json), [repository license](../LICENSE).
- [Native audit narrative](native-dependencies.md),
  [external asset provenance](../models/provenance.json),
  [current tasks](../openspec/changes/001-build-offline-translation-engine/tasks.md).
- `requirements.lock`, `requirements-dev.lock`; installed `.venv/Lib/site-packages`
  distribution `METADATA`, `RECORD`, licenses, package sources and build configuration.
- `build/diagnostic-20261107-133601/native-static-audit-complete.json`,
  `build-result.json`, and `work/worker/{PYZ-00,EXE-00,Analysis-00}.toc`;
  the corresponding `dist/diagnostic-20261107-133601/translation-engine-worker/`.

The existing audit binds **180 files, 53 AMD64 PE files**, and the executable's
embedded archive to the build. This review independently rehashed all 180 recorded
files with PowerShell: zero mismatches. Candidate EXE SHA-256:
`627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941`;
recorded diagnostic ZIP SHA-256:
`965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`.
These identify evidence, not a final compliance ZIP. Generated build/dist records
are local evidence and must be preserved or exported with the release dossier.

The PYZ table identifies these **17 third-party Python distribution roots**:
`argostranslate`, `charset_normalizer`, `cloudpickle`, `colorama`, `ctranslate2`,
`filelock`, `joblib`, `minisbd`, `numpy`, `onnxruntime`, `packaging`, `regex`,
`sacremoses`, `sentencepiece`, `tqdm`, `typing_extensions`, `yaml`.
CPython, the project's code, and PyInstaller's embedded bootloader/loader and
runtime hooks are additional components. A lockfile's entire installed graph is
not the inventory.

Code frozen as Python bytecode is redistributed object code, even if not exercised
in the tested translation path. DLLs/PYDs, bundled data, runtime hooks and statically
incorporated code also count. A directory listing alone misses PYZ components.

Requests, urllib3, Certifi, idna, flatbuffers and protobuf Python distributions
are not roots in this candidate's PYZ or file tree. Neither are spaCy, Thinc,
Stanza or Torch. Their installed metadata is not evidence of frozen inclusion.
Native protobuf/other embedded libraries are a separate issue below. Windows OS
DLLs/API-set contracts, WinSxS OS components, and the host-injected Teruten DLLs
are not release files. Do not copy them into the distribution.

The environment's `.venv/Scripts/python.exe` could not launch its Store Python
under the review account. No worker execution, rebuilding, or new functional
acceptance was attempted. Inventory conclusions use retained freezer records,
installed files and hash-verified artifact files; this is not a fresh PYZ bytecode
decompilation or a complete static-link bill of materials.

## Component matrix

**Evidence labels:** V = identity/presence or license text verified locally;
U = unresolved release evidence. A permissive top-level license does not clear
unidentified embedded code. “No standalone source duty” below describes that
component's own license; the approved AGPL Corresponding Source scope may be wider.
All license conditions/notices must survive freezing. Local license paths below
are relative to `.venv/Lib/site-packages/` unless stated otherwise.

| Component / pinned identity | Redistributed form and license authority | Required materials / source obligations | Evidence and outstanding work |
|---|---|---|---|
| translation-engine 0.1.0 | Worker bytecode; [MIT](../LICENSE) | Preserve Kurt Patrick Yu's copyright, permission and disclaimer. No standalone source duty under MIT. | V: source and PYZ. U: combined AGPL distribution terms need approval; do not describe the entire bundle as MIT-only. |
| Argos Translate 1.11.1, commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` | Bytecode; [exact upstream MIT license][argos] | Preserve Argos copyright and full MIT text. No standalone source duty. Preserve source archive, wheel identity and recipe for combined-source delivery. | V: unmodified source recorded in `packaging/argos-upstream.json`; license already in frozen dist-info. Source SHA-256 `0cedceb52ca288b12bb4a33de97f7a8df13bc45dd46f6338754194a27b746343`; wheel SHA-256 `825b1bf872390547bad6c1fcf1f12e5967e2fe6b44ca1e8a82e17a8dd79a2aa0`. Argos MIT does not override MiniSBD. |
| MiniSBD 0.9.5 | Bytecode; AGPLv3, installed `minisbd-0.9.5.dist-info/licenses/LICENSE` and [upstream][minisbd] | AGPL text, copyright/attribution/warranty notices; exact Corresponding Source and build/install materials by an approved section 6 mechanism. Preserve inherited Stanza notices; mark actual modifications. | V: bundled version, AGPL text and package declaration. U: wheel-to-source revision and complete inherited notice chain. `bc63bb09...` in model provenance is an inspection revision, not proof of the wheel's source commit. No commercial exception or alternative grant evidenced. |
| CTranslate2 4.8.5 | Bytecode, `_ext...pyd`, `ctranslate2.dll`; [MIT][ct2] | SYSTRAN/OpenNMT copyright and MIT text; embedded third-party licenses/notices, Intel terms separately. No standalone source duty from MIT. | V: metadata/native hashes. U: MIT text absent from collected dist-info; exact wheel's static-library/source mapping incomplete. See native review. |
| SentencePiece 0.2.1 | Bytecode, `_sentencepiece...pyd`; [Apache-2.0][sp] | Apache text, applicable attribution/NOTICE, retained embedded-component notices; identify modifications if any. No standalone source duty. | V: version and upstream license. U: no license file in candidate; reconcile built-in protobuf-lite/Abseil and other third-party code against exact wheel source/build; root Apache text alone is insufficient. |
| ONNX Runtime 1.31.1 CPU wheel | Bytecode, `onnxruntime_pybind11_state.pyd`, `onnxruntime.dll`, provider-shared DLL; [MIT][ort] plus [third-party notices][ort-notices] | Microsoft MIT and version-matched `ThirdPartyNotices.txt`; comply with applicable embedded licenses, including source obligations if actually present. | V: installed `onnxruntime/LICENSE`, `ThirdPartyNotices.txt`, and `capi/build_and_package_info.py`; neither license/notices file is in candidate. U: reconcile broad upstream notice list to CPU binary build, including any Intel/nonpermissive code. An unused but shipped DLL still counts. |
| NumPy 2.5.4 | Bytecode, 13 NumPy PYDs, BLAS DLL; installed `numpy-2.5.4.dist-info/licenses/` and [upstream][numpy] | Preserve entire wheel license directory: BSD-3-Clause, MIT, 0BSD, Zlib, CC0 and component notices (random generators, pocketfft, highway, libdivide, etc.). Do not rely on metadata's SPDX summary for bundled BLAS/compiler code. | V: metadata, native inventory, license directory already bundled. No standalone source duty from those permissive terms. U: embedded-library mapping below. |
| SciPy OpenBLAS build `0.3.34.106.0`, LAPACK | `numpy.libs/libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll`; NumPy wheel `LICENSE.txt`, [OpenBLAS][openblas] | OpenBLAS BSD-3-Clause and LAPACK BSD-style notices/disclaimers/nonendorsement clauses; retain bundled compiler runtime licenses/exceptions. | V: NumPy `__config__.py` reports this OpenBLAS build; wheel license identifies LAPACK and statically linked GCC runtime. U: exact OpenBLAS/LAPACK/GCC build revisions and exception eligibility; build configuration is not an independent binary version attestation. |
| Intel OpenMP resource version 5.0.2025.910 | `ctranslate2/libiomp5md.dll`; supplier-specific Intel distribution terms unresolved | Obtain controlling license, redistributable list and third-party notices for these exact bytes; record redistribution conditions and attribution. Source duty depends on actual grant and combined-work analysis. | V: DLL/hash/collection from CTranslate2 wheel. U: no matching Intel license delivered. [LLVM OpenMP license][llvm] is not proof that Intel's DLL is Apache-licensed; [Intel says the bundled product license controls][intel]. |
| Microsoft VC++ v14 14.50.35719.0 (4 DLLs) | `msvcp140.dll`, `MSVCP140_1.dll`, `vcruntime140.dll`, `vcruntime140_1.dll`; [Microsoft redistribution rules][ms-redist] | Applicable Microsoft grant/REDIST eligibility, conditions and downstream protections; not MIT. No general Microsoft source grant. Preserve copyright and acquisition/servicing evidence. | V: all four collected from System32, exact hashes in native audit. U: licensed acquisition/redistribution entitlement and matching product terms; hashes do not supply permission. |
| Microsoft VC++ 14.40.33810.0, wheel-local renamed MSVCP | `numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll`; Microsoft terms | Same rights/provenance review; establish redistribution chain and whether renaming/repair is permitted. No general source grant. | V: actual bytes from NumPy wheel. U: wheel origin alone does not establish downstream rights or the repair tool's authority. Must not be overlooked when addressing the four ordinary DLLs. |
| CPython 3.12.10 x64 | `python312.dll`, 17 CPython PYDs, stdlib PYZ/base ZIP; [PSF and historical licenses][python] | Full PSF/history/incorporated-code notices; brief description of changes to Python where applicable (including packaging). No standalone source duty under PSF. | V: Store distribution path/resource version `3.12.10150.1013`, interpreter identity recorded by prior audit. Installed Store `LICENSE.txt` additionally has Windows binary/Microsoft Distributable Code conditions. U: license absent from artifact; preserve distribution-specific terms as well as upstream LICENSE. |
| OpenSSL 3.0.16 | `libcrypto-3.dll`, `libssl-3.dll`; [Apache-2.0 source license][openssl] | Apache text and applicable upstream notices/attribution for this build. No standalone source duty. | V: DLL versions and CPython source origin. U: collect exact binary-distribution notices and any incorporated third-party notices. |
| SQLite 3.49.1 | `sqlite3.dll`; [public-domain dedication][sqlite] | No upstream license-text/source requirement for deliverable SQLite; retain provenance/dedication as evidence. | V: binary version. Build scripts' licenses do not automatically apply to library output. |
| libffi, expected 3.4.4 | `libffi-8.dll`; Store Python LICENSE includes MIT-style libffi notice; [CPython dependency recipe][py-deps] | Retain libffi copyright and permission/disclaimer. No standalone source duty. | V: DLL present, no version resource. U: 3.4.4 is recipe evidence, not proven binary version; bind actual supplied build. |
| Other CPython incorporated libraries | Static code in `_bz2`, `_lzma`, `_decimal`, `pyexpat` and runtime/stdlib | Preserve applicable bzip2, XZ/liblzma, libmpdec, Expat, zlib and other CPython incorporated notices from exact distribution/source. Typically permissive/public-domain terms; review exact versions. | V: parent binaries present. Recipe specifies bzip2 1.0.8, XZ 5.2.5, zlib 1.3.1. U: exact binary build versions, Expat/libmpdec mapping and full notice reconciliation. These are not separately pip-pinned components. |
| PyInstaller 6.22.3 | Embedded bootloader/loader; inspect, multiprocessing, pkgutil runtime hooks; [COPYING/exception][pyinstaller] | Bootloader exception permits combined executable distribution without PyInstaller GPL source/credit requirements. Retain exception evidence; Apache-2.0 requirements apply to runtime hooks/additional runtime modules. | V: `EXE-00.toc`, installed `COPYING.txt`. No evidence of PyInstaller modifications. Build tools as a whole are not shipped merely because used to build. |

### Remaining frozen Python distributions

Versions below are exact installed metadata/lock pins associated with the PYZ
collection paths. License files are available locally in each distribution's
dist-info (usually `licenses/`); none of these texts except tqdm's is copied in
the candidate. The linked publisher repositories are authoritative source
locations, not substitutes for delivering the exact license text.

| Component / version | Redistributed form / authority | Required actions and source duty |
|---|---|---|
| charset-normalizer 3.5.2 | Bytecode and two PYDs; [MIT](https://github.com/jawah/charset_normalizer/blob/master/LICENSE) | Deliver installed LICENSE/copyright/disclaimer; resolve embedded compiler/runtime notices for extensions. No standalone source duty from MIT. |
| cloudpickle 3.1.2 | Bytecode; [BSD-3-Clause](https://github.com/cloudpipe/cloudpickle/blob/master/LICENSE) | Copyright, conditions, disclaimer; no standalone source duty. |
| colorama 0.4.6 | Bytecode; [BSD-3-Clause](https://github.com/tartley/colorama/blob/0.4.6/LICENSE.txt) | Copyright, conditions, disclaimer; no standalone source duty. |
| filelock 4.2.9 | Bytecode; [MIT](https://github.com/tox-dev/filelock/blob/main/LICENSE) | Full copyright/license/disclaimer; no standalone source duty. |
| joblib 1.6.0 | Bytecode incl. vendored loky 3.6.0; [BSD-3-Clause](https://github.com/joblib/joblib/blob/main/LICENSE.txt), [loky](https://github.com/joblib/loky/blob/master/LICENSE.txt) | Preserve joblib and vendored copyright/conditions/disclaimers. Reconcile copied CPython code notices. No standalone source duty from BSD. Loky version verified in installed `joblib/externals/loky/__init__.py`; no independent dependency pin. |
| packaging 26.3 | Bytecode; [Apache-2.0 OR BSD-2-Clause](https://github.com/pypa/packaging/blob/main/LICENSE) | Record selected licensing route (BSD is sufficient if applicable to shipped files); preserve LICENSE and corresponding text/notices. No standalone source duty. |
| regex 2026.9.29 | Bytecode and PYD; [Apache-2.0 AND CNRI-Python](https://github.com/mrabarnett/mrab-regex/blob/hg/LICENSE.txt) | Full installed LICENSE, including CNRI/Secret Labs provenance, and Apache requirements. Not simply MIT or Apache-only. No standalone source duty. |
| sacremoses 0.1.1 | Bytecode and nonbreaking-prefix/perluniprops data; [MIT](https://github.com/hplt-project/sacremoses/blob/master/LICENSE) | Preserve alvations copyright/MIT; reconcile inherited Moses/data notices, including Unicode attribution if applicable. Data files count even though external translation models do not ship. No standalone source duty from MIT. |
| tqdm 4.70.1 | Bytecode; installed `tqdm-4.70.1.dist-info/licenses/LICENCE`, [MPL-2.0 and MIT contributions][tqdm] | Retain complete attribution/license notice; make exact MPL-covered source available and tell recipients how to obtain it under [MPL sections 3.1–3.4][mpl]. Include license text. Existing LICENCE in ZIP alone is insufficient. Not an unrestricted choice of MIT for every file. |
| typing_extensions 4.16.0 | Bytecode; [PSF-2.0](https://github.com/python/typing_extensions/blob/main/LICENSE) | Retain full installed license/copyright and applicable change summary; no standalone source duty. |
| PyYAML 6.0.3 | Bytecode and `_yaml...pyd`; [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE) | Preserve PyYAML and linked LibYAML MIT notices. U: exact incorporated LibYAML version/build, not separately pinned in locks. No standalone source duty from MIT. |

## AGPLv3, MIT and source delivery

The installed MiniSBD license is AGPL version 3; do not infer an “or later”
election merely from the generic license text. Preserve the package's actual
grant and copyright headers when preparing sources. Its README acknowledges
code modified from Stanza; excluding the Stanza Python package does not erase
attribution for code already incorporated into MiniSBD.

The project imports Argos in-process; Argos uses MiniSBD in that same interpreter,
and both are frozen into the worker. This is concrete reason to review a covered
combination, rather than assert mere aggregation based on separate package names.
Whether particular boundaries create a derivative/combined work is a legal
determination. The root MIT grant can remain for the maintainer's own code and
its copyright notices must remain. Compatible permissive code can participate
in an AGPL-covered combination without erasing its original licenses. Conversely,
MIT does not authorize relicensing MiniSBD as MIT. A blanket claim that all
repository files automatically become AGPL would also be unjustified.

For an approved AGPL-covered distribution, prepare the preferred source form
of all covered portions and the material needed to build, install and modify
them: matching worker sources, MiniSBD, relevant dependency sources, interface
definitions, actual modifications, freezer spec/entry point, locks, Argos wheel
recipe/provenance and reproducible build/install instructions. Record why any
tools, system libraries or separate aggregates are outside Corresponding Source.
An exclusion must follow the license definitions; a bundled DLL is not exempt
solely because Windows applications commonly use it. A native import audit
cannot decide that question. See [AGPL sections 1, 4–6, 10, 12–13][agpl].

Recommended release mechanism: an adjacent, versioned source/compliance archive
with exact source hashes and clear download instructions accompanying the binary
(section 6(d) for network distribution). The distributor remains responsible for
availability; a homepage, moving branch, wheel-only download, or bare list of
upstream URLs does not establish delivery of complete matching source. A separate
server can be used only with the section's required directions and availability.
Do not substitute a casual “source on request” promise: section 6(b)'s written
offer has specific distribution circumstances and duration/recipient conditions.

Retain required notices, warranty disclaimers and license copies; clearly identify
actual changes and applicable dates. Assess interactive legal notices where the
license requires them. Installation Information under section 6 is conditional
on the User Product transaction; an ordinary downloadable worker does not alone
establish that condition. The current local stdio protocol does not itself
demonstrate remote network interaction triggering section 13's modified-program
requirement, but offline operation does not waive object-code distribution duties.
Reassess section 13 if a covered modified program is offered over a network.

**Required explicit decisions:** approve covered-work boundaries and release
licensing language; approve exact Corresponding Source scope and exclusions;
approve source hosting/retention and responsibility; resolve compatibility of
Microsoft/Intel terms with the covered combination. Review runtime-library
exceptions and System Library status on their facts. If obligations conflict,
do not distribute while unresolved. No license file should be changed by inference.

Tqdm's independent MPL source duty should be met even while AGPL scope is under
review. Supplying its matching source under MPL with the original notices is
straightforward; do not assume it is MIT-only or silently elect MPL secondary
licensing without checking the actual files and grant.

## Native licensing and acquisition gaps

### Microsoft DLLs

System32 location establishes collection origin, not entitlement to redistribute.
Microsoft expressly limits runtime redistribution to licensed Visual Studio users
under applicable terms and identifies authorized redist locations/lists. The
[VS 2022 REDIST list][ms-list] demonstrates the process, but does not prove that
14.50.35719.0 belongs to that product/version. Obtain the matching product's list
and license rather than applying a familiar list to newer bytes.

The four ordinary DLL hashes are already in `docs/native-dependencies.md` and
the JSON inventory. Signatures, matching exports and local runtime success would
not establish the missing legal grant. There is no evidence here that the DLLs
are categorically nonredistributable; their **current redistribution provenance
is insufficient**.

Smallest preferred remedy: establish a qualifying licensed Microsoft acquisition,
pin the approved x64 redistributable package/VS redist payload and terms, and
collect only the required app-local files from its authorized location. Record
product version, eligibility, URL, installer/payload SHA-256, signature and DLL
hashes, accepted terms, REDIST mapping and servicing owner. Verify equal bytes if
possible; if bytes differ, treat them as a changed candidate and repeat relevant
technical/OS validation. A Microsoft download alone does not prove redistribution
entitlement. App-local deployment is supported but leaves servicing to the app.

Fallback if entitlement cannot be established: require users to obtain/install
the official Microsoft x64 Redistributable directly, and omit affected ordinary
DLLs from a future candidate. This changes the no-prerequisite standalone promise
and needs explicit approval and validation. It does not solve NumPy's renamed
14.40 MSVCP copy or Microsoft's code embedded in CPython/extensions. Removing
that renamed file without relinking/repair analysis can break OpenBLAS imports.
The Store Python `LICENSE.txt` explicitly includes additional Microsoft binary
conditions; retain and review these rather than relying only on PSF's license.

### Intel and static code

CTranslate2's [versioned Windows build recipe][ct2-build] copies Intel oneAPI
`libiomp5md.dll`, enables oneDNN, and builds oneDNN 3.1.1 statically. Its CMake
configuration also supports/defaults to MKL. These are strong source-level leads,
not a fully proven bill of materials for the exact wheel. Obtain the wheel build
record/source revisions and identify compiled-in MKL, oneDNN, spdlog, pybind11
and other material. Absence of an MKL/oneDNN DLL does not prove absence of their
code; CPU-only use does not remove shipped compiled code obligations.

The exact Intel DLL license is not supplied by CTranslate2's MIT declaration.
Intel's [license directory][intel] explicitly makes the product-bundled license
controlling. Do not apply LLVM OpenMP's Apache/LLVM exception to Intel-branded
bytes without evidence. Obtain original Intel package notices and redistribution
designation, then assess any restrictions against the approved AGPL scope.
ONNX Runtime's broad third-party notices even include Intel MKL terms restricting
reverse engineering; determine applicability to this CPU build rather than
assuming the notice proves MKL inclusion or that ORT's MIT license resolves it.

NumPy's wheel license identifies statically linked GCC runtime code inside BLAS
under GPLv3-or-later with GCC Runtime Library Exception 3.1. Preserve that complete
text (already collected), and verify the exception's eligible-compilation and
independent-module conditions. It is not a reason to automatically label NumPy
GPL-only, nor a blanket exception for unrelated code. Resolve any residual runtime
source obligation against the actual build and exception.

## External assets: excluded, attribution retained

Neither `.argosmodel` nor `.onnx` files occur in the recorded 180-file candidate.
Translation weights, SentencePiece model data and MiniSBD ONNX resources are
acquired separately by users; they are not part of the worker redistribution
inventory. Do not download, attach or host them as compliance/release assets.
This scope choice does not clear their licensing or remove bundled-code duties.

Keep [provenance.json](../models/provenance.json) unchanged, including upstream
identities, attribution and `pending-review` state:

| External asset | Source | SHA-256 / unresolved attribution |
|---|---|---|
| `translate-zh_en-1_9.argosmodel`, package 1.9 | [Argos upstream](https://argos-net.com/v1/translate-zh_en-1_9.argosmodel) | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d`; archived README identifies original OPUS model as CC-BY 4.0; retain OPUS-MT attribution, not a clearance finding. |
| `zh-hans.onnx`, release v0.0.1, asset 336220945 | [MiniSBD upstream asset](https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx) | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e`; converted/quantized Stanza tokenizer chain and ONNX-specific terms remain unresolved. Library AGPL alone does not settle model rights. |

Preserve separate source attribution/digests in release manifest metadata; do not
list these as attached files in `SHA256SUMS`. If legal review concludes any
external resource is legally part of a covered work's required source, resolve
that scope/availability question before release; do not silently bundle it or
assume the external acquisition design overrides the license.

## Practical options

| Option | Benefit / required work | Decision |
|---|---|---|
| A. Keep dependencies; satisfy distribution obligations | Preserves tested translation, segmentation and packaging. Add complete texts/notices, matching AGPL/MPL source delivery and approved native provenance. A narrow acquisition/packaging correction may still be needed. | Recommended, conditional on resolving the gates above. No evidence currently establishes an unavoidable blocker requiring backend replacement. |
| B. Smallest change for an established blocker | For unresolved VC provenance, prefer approved redist acquisition with same dependencies. If AGPL is unacceptable or native compatibility cannot be resolved, investigate an alternative MiniSBD license from all relevant rightsholders or a narrowly scoped splitter/backend substitution. If Intel terms block release, evaluate a permitted runtime/build configuration. | Contingency only. No alternative has been legally or technically validated. Deleting MiniSBD metadata, using an arbitrary splitter, user-installing the same code, or moving it to a subprocess does not automatically resolve copyleft. Any real graph/build change needs proposal, compatibility/quality tests, inventory and acceptance evidence. |

## Required actions and OpenSpec disposition

| Gate | Prepare immediately | Evidence/decision needed before completion |
|---|---|---|
| 3.2 | Exact MiniSBD source mapping; source/compliance archive plan; draft bundle licensing statement; retain external attribution | Maintainer/legal decision on AGPL scope, source completeness/exclusions, compatibility and delivery mechanism. Review findings are not clearance. |
| 4.3b | Native evidence ledger keyed to candidate hashes; identify missing supplier grants and static subcomponents | Approved Microsoft acquisition/rights including NumPy copy and Python binary terms; exact Intel grant/notices; static-library reconciliation and servicing plan. |
| 5.3 | Assemble candidate-specific full third-party texts, notices, original copyright headers; stage matching MiniSBD/tqdm and approved covered-work source/build/install materials | Verify source-to-binary mapping and practical source availability; no placeholders, homepage-only entries or unproven license substitutions. |
| 4.4b / 5.2 | Define final archive layout and manifest/checksum coverage | New final archive hash, complete compliance/source entries, explicit external metadata distinction; repeat validation appropriate to any changed files. |
| Existing clean OS PUBLIC gates | Preserve local/manual evidence | Still require their own Windows 10/11 and OS-denied networking evidence; licensing work does not pass them. |

The current tasks already correctly separate local completion from public
redistribution and already require AGPL/native/source materials. **No new change,
renumbering, model-hosting gate or checkbox completion is recommended.** Only
necessary wording refinements for a later task edit:

- 4.3b: explicitly include the wheel-local renamed VC++ DLL, CPython Windows
  binary terms and statically incorporated native libraries; record the precise
  Microsoft/Intel license-to-byte mapping and any compatibility determination.
- 5.3: explicitly name tqdm's MPL source delivery, matching-source archive
  verification and the missing ONNX/SentencePiece/CPython notices. Its existing
  “other bundled code” scope already covers these; this clarifies acceptance.
- 3.2: link this review as investigation evidence and retain an explicit pending
  maintainer/legal decision. Do not mark complete based on the existence of a report.

**Smallest safe next implementation task:** prepare a candidate-specific compliance
staging directory and manifest, without rebuilding: collect the verified
version-matched license/notice files for the 17 frozen third-party Python
distributions, CPython/native dependencies and PyInstaller Apache runtime hooks;
stage matching MiniSBD/tqdm sources with hashes and build/install instructions;
record unproven source/native mappings as explicit blocking entries. Do not label
the staging directory complete, alter license grants, or publish it as clearance.
Native acquisition correction follows review of the controlling grants; backend
changes are not justified yet.

## Authoritative references

Upstream sources below were consulted during this review where accessible.
Main/master links establish publisher context, not exact-release source identity;
release assembly must use the local version-matched text and pinned source.
MiniSBD's attempted version/inspection-revision raw license retrieval was
unavailable; the installed wheel's full AGPL text is the verified local authority,
and the current upstream license corroborates it. Unresolved nested versions are
deliberately not presented as pins or cleared licenses.

[argos]: https://raw.githubusercontent.com/argosopentech/argos-translate/17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88/LICENSE
[minisbd]: https://github.com/LibreTranslate/MiniSBD/blob/main/LICENSE
[agpl]: https://www.gnu.org/licenses/agpl-3.0-standalone.html
[ct2]: https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.5/LICENSE
[ct2-build]: https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.5/python/tools/prepare_build_environment_windows.sh
[sp]: https://raw.githubusercontent.com/google/sentencepiece/v0.2.1/LICENSE
[ort]: https://raw.githubusercontent.com/microsoft/onnxruntime/v1.31.1/LICENSE
[ort-notices]: https://raw.githubusercontent.com/microsoft/onnxruntime/v1.31.1/ThirdPartyNotices.txt
[numpy]: https://github.com/numpy/numpy/blob/main/LICENSE.txt
[openblas]: https://github.com/OpenMathLib/OpenBLAS/blob/develop/LICENSE
[llvm]: https://raw.githubusercontent.com/llvm/llvm-project/main/openmp/LICENSE.TXT
[intel]: https://www.intel.com/content/www/us/en/developer/articles/license/end-user-license-agreement.html
[ms-redist]: https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files
[ms-list]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution
[python]: https://raw.githubusercontent.com/python/cpython/v3.12.10/LICENSE
[py-deps]: https://raw.githubusercontent.com/python/cpython/v3.12.10/PCbuild/get_externals.bat
[openssl]: https://github.com/openssl/openssl/blob/openssl-3.0.16/LICENSE.txt
[sqlite]: https://www.sqlite.org/copyright.html
[pyinstaller]: https://pyinstaller.org/en/stable/license.html
[tqdm]: https://raw.githubusercontent.com/tqdm/tqdm/master/LICENCE
[mpl]: https://www.mozilla.org/en-US/MPL/2.0/
