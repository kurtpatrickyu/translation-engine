# Windows native dependency audit — 2026-11-07

## External VC++ prerequisite for change 003

New builds exclude exactly `msvcp140.dll`, `msvcp140_1.dll`, `vcruntime140.dll`
and `vcruntime140_1.dll` from PyInstaller's post-Analysis binary collection.
Keep the complete onedir/ZIP; Python, CTranslate2, ONNX Runtime, SentencePiece,
Intel OpenMP and all other required dependencies remain bundled. In particular,
`numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` remains unchanged:
NumPy's core and FFT extensions import that exact filename. The ordinary system
runtime cannot substitute for it without changing the wheel.

Install the **latest supported official Microsoft Visual C++ v14 x64
Redistributable** if needed: [official Microsoft download](https://aka.ms/vc14/vc_redist.x64.exe).
Run the Microsoft installer separately, complete any restart it requests, then
retry the worker. Offline users can transfer a separately obtained official
installer. This project does not bundle/redistribute it, and the worker never
downloads or installs prerequisites. A compatible newer x64 installation needs
no downgrade or forced reinstallation. An x86-only or arbitrary old v14 runtime
does not establish compatibility.

Microsoft requires the runtime to be at least as recent as the newest MSVC build
tools used by any component, with matching application architecture. See
[supported downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
and [binary compatibility](https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017?view=msvc-170).
The project therefore recommends the latest supported official x64 package.
**14.50.35719.0 is a provisional conservative candidate, not a proven minimum.**
The host registers `v14.50.35719.00`, `Installed=1`; all four System32 files are
14.50.35719.0 with valid Microsoft Authenticode signatures. CPython reports
`MSC v.1943`; installed ONNX metadata identifies 1.31.1 but not its compiler.
Available evidence does not establish every wheel's newest toolset or a lowest
numeric minimum. Record actual tested runtimes below; do not infer support for
older runtimes or obtain a historical installer solely to test the provisional
number. Clean Windows 10 acceptance remains a PUBLIC gate for initial v0.1.0;
separate Windows 11 acceptance is waived, expected compatible but UNTESTED and
optional future validation. See the [2026-11-08 scope decision](v0.1.0-acceptance-scope.md);
the historical audit results below retain their original scope.

To inspect an existing x64 installation from CMD or PowerShell:

```bat
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /reg:64
```

Registration is a useful hint, not loader proof. Actual module snapshots must
show the four ordinary DLLs from the installed Microsoft runtime (normally
`%SystemRoot%\System32` for x64), and NumPy's renamed DLL from the bundle.
If startup fails with a missing-DLL message, PyInstaller's Python-library-load
error, or a native import failure, install/update/repair the official x64 package
and retry. Python may never initialize, so no NDJSON error is guaranteed. Keep
the original exit status/stdout/stderr or dialog details; absent health or failed
initialization is not `ready=true`. No new startup detector/launcher is added.

One monitored candidate build and existing frozen/native checks are used for
003; exhaustive prerequisite version/architecture matrices are deferred unless
a concrete issue requires a targeted check. Ordinary VC imports are declared
explicitly with the audit's `--external-vc-runtime` option, not assumed to be OS
contracts. Unrelated native dependencies and unexpected host modules retain
their existing checks. The historical evidence below remains unchanged.

AGPL source delivery/notices, Intel OpenMP rights, NumPy's renamed Microsoft
DLL provenance and all other actual bundled-material requirements remain
separate mandatory PUBLIC release work. Externalizing four DLLs clears none of
those obligations. Candidate compliance rebinding is also separate release work.

## Change 003 candidate: local verification

One monitored build produced `diagnostic-20261107-211131` in 38.01 seconds,
without a resource abort or build-input drift. It retains **176 files / 49 AMD64
PEs**. The four ordinary VC DLLs are absent throughout the onedir and ZIP; all
**48 retained native dependency files** match the historical native hashes,
including NumPy's renamed DLL. No installer, translation model or ONNX asset was
added. Complete ZIP/extracted file-set and byte comparison passed.

| Candidate identity | Value |
|---|---|
| Directory | `dist/diagnostic-20261107-211131/translation-engine-worker/` |
| ZIP | `build/diagnostic-20261107-211131/frozen-unicode-all.worker.zip` |
| ZIP bytes | 57,783,318 |
| Extracted bytes | 159,167,808 |
| ZIP SHA-256 | `8bf0010042f2259d477a29b19c7fa5e15aa53d9ae8a7ba238900926fd2ed5fd0` |
| EXE SHA-256 | `ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d` |

The installed **14.50.35719.0 x64 runtime** passed local frozen execution:
all four ordinary DLLs loaded from System32 at readiness and after translation,
with hashes matching the inspected Microsoft-signed installed files. NumPy's
renamed DLL and Python loaded from the bundle. This identifies an actually
tested runtime, **not a proven lowest compatible version** or clean-OS support
claim. Recommend the latest supported official x64 package; available wheel
metadata still does not establish every component's newest toolset. No historical
installer was acquired and no runtime installation was changed.

The locked source suite with real-model integration passed **64 tests**, including
the single focused policy test; the four focused policy/audit guards also passed
after adding explicit external-VC classification assertions. Four frozen runs
(independent Unicode model, executable and state paths, then combined Unicode)
pass version/startup, production provisioning, `health ready=true`, persistent
requests/error recovery/shutdown, integrity rejection/failed-reprovision safety
and missing-model handling. The native run passes the same functional checks.
Across those five runs, **75 translation outputs match the historical baseline
exactly**, with unchanged original model and ONNX hashes and identical candidate
ZIP hashes. Minimal child PATH/environment and native origins demonstrate no
loaded development/global Python dependency locally; the host itself has Python,
so clean no-system-Python acceptance remains pending.

Strict native isolation remains **failed**, with `functional_smoke_passed=true`:
the same two external Teruten DLLs (`T_Prevent64.dll`, `TDCommonLib64.dll`) appear
in both snapshots. They were not allowlisted and host security software was not
modified. The local/static success is separate from that strict failure. No clean
Windows 10 22H2 or Windows 11 VM/Sandbox acceptance environment was available in
this session; OS-denied networking and both PUBLIC OS rows remain unexecuted.

Evidence in `build/diagnostic-20261107-211131/`: `build-result.json`,
`native-static-audit.json`, `native-runtime-audit.json`,
`frozen-unicode-{all,model,executable,state}.json`,
`installed-runtime-signatures.json` and `candidate-comparison.json`.
Source/guard results are `runtime/external-vc-prebuild-tests.xml` and
`runtime/external-vc-postbuild-guard-tests.xml`. The preservation comparison
rehashed all **180 historical distribution files** and **26 evidence/input
files**, with zero mismatches, including original diagnostics/ZIPs, manual
transcripts, locks, Argos identity, model/ONNX assets and `001` task records.

To recheck this candidate without rebuilding, choose unused report names:

```bat
.venv\Scripts\python scripts\audit_windows_package.py --build-dir build\diagnostic-20261107-211131 --external-vc-runtime --report build\diagnostic-20261107-211131\native-static-recheck.json
.venv\Scripts\python scripts\validate_windows.py --exe dist\diagnostic-20261107-211131\translation-engine-worker\translation-engine-worker.exe --native-audit --external-vc-runtime --report build\diagnostic-20261107-211131\native-runtime-recheck.json
```

No release is authorized by these local results. Task 5.3 preparation now binds
the compliance inventory to this 176-file candidate; see
[compliance staging](compliance-staging.md). PUBLIC source-delivery/native-rights
gates remain pending; `001` Level A is unchanged.

## Historical bundled-runtime diagnostic audit

The existing Unicode-fixed diagnostic artifact has no demonstrated missing native
dependency and is ready to be taken into clean-machine testing. This is a local
technical assessment, not platform acceptance or redistribution clearance.
No executable, spec, dependency pin, lock, model, or validated ZIP was changed;
no build was run. The development host contains external Teruten modules in the
worker process, so the strict runtime-isolation check deliberately remains failed.

## Artifact and integrity

Audited directory:
`dist/diagnostic-20261107-133601/translation-engine-worker/`.
All 180 files match the previously validated ZIP byte for byte, including the
53 AMD64 PE files. Regular and delay imports were checked. Every non-OS import
has a bundled DLL and its directly imported named/ordinal exports are present.
There are no duplicate PE basenames, unresolved imports, or final parser warnings.
The inventory records all file/native hashes, versions, import names/symbols,
collection sources, metadata, and external OS contracts:

`build/diagnostic-20261107-133601/native-static-audit-complete.json`.

- Extracted size: 159,927,584 bytes; ZIP: 58,072,023 bytes.
- EXE SHA-256: `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941`.
- ZIP SHA-256: `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`.

All recorded production/build input hashes still match the successful build.
All 52 collected PE dependency files still match their recorded collection
sources. The remaining PE is the generated executable, separately bound to the
validated hash. Version resources are not always distribution version numbers:
Python's resource is `3.12.10150.1013`, while the bundled interpreter is 3.12.10.
Required metadata identifies Argos 1.11.1, CTranslate2 4.8.5, SentencePiece 0.2.1,
MiniSBD 0.9.5, and NumPy 2.5.4. The spec includes metadata explicitly for the
first four; NumPy metadata is included by its hook. No production inputs changed.

## Native inventory

Paths below are relative to `_internal/`, except the executable. The machine
field is AMD64 (`0x8664`) for all 53 files; all are covered by the JSON inventory.

| Component | Bundled binaries | Main dependency / observation |
|---|---|---|
| Bootloader / Python | `translation-engine-worker.exe`, `python312.dll` | Bundled Python; bootloader uses Windows DLLs |
| CTranslate2 4.8.5 | `ctranslate2/_ext.cp312-win_amd64.pyd`, `ctranslate2/ctranslate2.dll`, `ctranslate2/libiomp5md.dll` | C++ runtime and Intel OpenMP 5.0.2025.910 bundled; CPU inference loads all three |
| SentencePiece 0.2.1 | `sentencepiece/_sentencepiece.cp312-win_amd64.pyd` | Python and C++ runtime bundled; serialized tokenizer uses unchanged model bytes |
| ONNX Runtime 1.31.1 | `onnxruntime/capi/onnxruntime_pybind11_state.pyd`, `onnxruntime.dll`, `onnxruntime_providers_shared.dll` in that folder | C++ runtime including `MSVCP140_1.dll`; pybind/shared provider load in MiniSBD; separate C API DLL is present but not loaded in snapshots |
| Visual C++ v14 | `msvcp140.dll`, `MSVCP140_1.dll`, `vcruntime140.dll`, `vcruntime140_1.dll` | All four version 14.50.35719.0, loaded from bundle |
| NumPy / BLAS | `numpy.libs/libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll`, `numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` | Wheel-local OpenBLAS and renamed MSVCP 14.40.33810.0; both loaded locally |
| NumPy core/FFT/linalg | `numpy/_core/_multiarray_umath.cp312-win_amd64.pyd`, `_multiarray_tests.cp312-win_amd64.pyd` in that folder; `numpy/fft/_pocketfft_umath.cp312-win_amd64.pyd`; `numpy/linalg/_umath_linalg.cp312-win_amd64.pyd` | Linked wheel-local BLAS/MSVCP exports present |
| NumPy random (9) | `numpy/random/{bit_generator,mtrand,_bounded_integers,_common,_generator,_mt19937,_pcg64,_philox,_sfc64}.cp312-win_amd64.pyd` | Python/C runtime dependencies included |
| Other package extensions (4) | `charset_normalizer/{cd,md}.cp312-win_amd64.pyd`, `regex/_regex.cp312-win_amd64.pyd`, `yaml/_yaml.cp312-win_amd64.pyd` | Python/C runtime dependencies included |
| CPython extensions (17) | `{pyexpat,select,unicodedata,_asyncio,_bz2,_ctypes,_decimal,_hashlib,_lzma,_multiprocessing,_overlapped,_queue,_socket,_sqlite3,_ssl,_uuid,_wmi}.pyd` | Python/C runtime dependencies included |
| Python support libraries (4) | `libcrypto-3.dll`, `libssl-3.dll`, `libffi-8.dll`, `sqlite3.dll` | OpenSSL 3.0.16, SQLite 3.49.1; interpreter distribution supplies these |

The CPython extensions come from the CPython 3.12.10 Microsoft Store
installation, copied into the artifact; runtime snapshots find no WindowsApps,
development `.venv`, or globally installed Python modules loaded as native DLLs.

## Windows dependencies and Visual C++ provenance

Unbundled regular imports are Windows desktop DLLs: `advapi32`, `bcrypt`,
`crypt32`, `dbghelp`, `dxgi`, `imagehlp`, `iphlpapi`, `kernel32`, `ole32`,
`oleaut32`, `propsys`, `rpcrt4`, `setupapi`, `shell32`, `user32`, `version`,
`wintrust`, and `ws2_32` (all `.dll`). Three delay descriptors reference
`ole32.dll` from `_wmi.pyd` and `SHELL32.dll` from each ONNX main/pybind binary.
Windows API contracts include `api-ms-win-core-path-l1-1-0.dll` and CRT conio,
convert, environment, filesystem, heap, locale, math, private, process, runtime,
stdio, string, time, and utility contracts. API sets are loader contracts, not
necessarily physical files to copy. [Microsoft API-set documentation](https://learn.microsoft.com/en-us/windows/win32/apiindex/windows-apisets)
explains this distinction.

The UCRT is part of Windows 10 and later; on Windows 10/11 the OS copy is used
even when a local copy exists. Exact imported/forwarded APIs must still be
verified on the target image; OS component presence alone is insufficient.
See [Microsoft UCRT deployment](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment?view=msvc-170).
The current host's newer System32, DXCore, and DirectX support cannot stand in
for Windows 10 22H2 evidence. CPU inference needs no CUDA/ROCm/GPU provider
libraries in the exercised path; Windows graphics-system DLLs may nevertheless
be loaded during runtime/OS initialization.

Specifically, NumPy's OpenBLAS imports `api-ms-win-crt-private-l1-1-0.dll`
(`__C_specific_handler`, `__intrinsic_setjmpex`, `longjmp` and memory/string
functions). Python and both ONNX main binaries import the core-path contract
(`PathCch*` functions). These exact contract/export requirements belong on the
Windows 10/11 checks; this audit does not assert their availability on untested
images or propose copying host API-set/UCRT files into the bundle.

ONNX documents a Visual C++ runtime requirement. This artifact supplies its
imported v14 runtime locally, rather than demonstrating a need for a target
redistributable installation. [ONNX installation requirements](https://onnxruntime.ai/docs/install/)
and [Microsoft local deployment](https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170)
describe those dependencies and deployment options. Microsoft also requires
compatible runtime/toolset versions; export presence and local tests do not
replace target-OS validation or distribution rights review.

PyInstaller collected the four ordinary v14 files from `C:\Windows\System32`,
not from a separately pinned redist installer. Their hashes are recorded here
and in the inventory:

| File | SHA-256 |
|---|---|
| `msvcp140.dll` | `def46aa6a8f72f27bafac0c43334419486a4d1dcdb6c479a8ef7034b3e1fa4cb` |
| `MSVCP140_1.dll` | `2dd670f874562fbdca5b022df1943d70a57ba91fde559280e3a1daebe4db2380` |
| `vcruntime140.dll` | `184146852727a9db4eea06178716bec3cdbb1015c911f6b0f915b184ad7775b2` |
| `vcruntime140_1.dll` | `e6bfb3662ab4b1969a73441dbe35c96d51441b6bff8cf1fe7430bd5b246ca605` |

This is a build-input provenance/servicing risk: a future build after a host
runtime update can collect different bytes despite unchanged Python locks. It is
not evidence that the current target needs the development host's installation;
the current runtime loads the bundled copies. Before final distribution, review
an approved redistributable source/rights and bind exact native bytes to the
candidate. No System32 copying, installer download, runtime replacement, or
licensing implementation was performed in this audit.

## Actual loader and isolation evidence

The augmented harness runs the same existing executable from relocated combined
Unicode paths and a disposable working directory, outside the repository. Its
child environment contains only `SystemRoot`, `WINDIR`, System32-only `PATH`,
and private `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP`. It inherits no
Python/Argos/HIP/CUDA/CT2/OMP settings, global package paths or user cache roots.
The worker's CPU/MiniSBD settings remain set by production code.

At readiness and after 15 translations, each snapshot lists 85 loaded modules:
31 bundled, 50 System32, two Windows side-by-side components (GDI+/common
controls), and two external host modules. Every loaded bundled file hash matches
the static artifact inventory. All application runtimes listed above load from
the bundle, including all four ordinary v14 DLLs. No CUDA/ROCm library was found.

The external modules are `C:\Windows\SysWOW64\T_Prevent64.dll` and
`TDCommonLib64.dll`, both version 5.0.2.4, with Teruten Inc. product metadata and
valid Teruten Inc. Authenticode signatures when inspected on this host. They are
not in the distribution or its PE import tables. Host injection is a reasonable
explanation, but the injection mechanism and whether they influence behavior
were not established. They must not be added to the artifact or silently
allowlisted as Windows dependencies. The initial snapshot also treated Windows
WinSxS components as external; the final classifier distinguishes only the two
reviewed OS component families and still flags Teruten. No host software was
disabled or modified.

`native-runtime-audit-complete.json` records `functional_smoke_passed: true`
and `passed: false` with both external modules retained as isolation findings.
Provisioning, readiness, all 15 translations, integrity rejection/preservation,
missing-model handling, stdout purity, empty normal stderr and shutdown pass;
outputs match the previous 15-sample validation exactly. The diagnostic ZIP/EXE
hashes are unchanged. This host is unsuitable for clean-isolation certification;
the artifact can still be tested on clean images. Loader snapshots miss
short-lived DLL loads and do not trace file access or native network attempts.

## Exclusions, inspection tools, and remaining gates

Stanza, Torch, spaCy, and Thinc are absent from the actual executable's embedded
PYZ and file tree. The current MiniSBD path uses ONNX CPU inference and inherits
no framework-selection input. Installed default source spaCy dependencies do not
imply their frozen inclusion. Existing warnings for optional training, framework,
converter, Unix-only, or tokenizer fallback imports do not justify collecting
these packages; current real worker tests exercise the intended inference path.
No missing native library warning occurs in the build log.

The first static attempt (`native-static-audit.json`) is retained but superseded:
pefile's default 8192 export limit truncated CTranslate2's 13,884 named exports
and OpenBLAS exports, producing false missing-symbol results. The final auditor
uses the supported bounded 65,536 export option and full decorated names bounded
to 4096 bytes, with correct ordinal handling and no parser warnings. This was
an inspection-tool limit, not a packaging change. Three focused guard tests pass
(`runtime/native-audit-tests.xml`), covering VC DLLs not being assumed OS-provided,
API-set classification, and rejecting unexpected host DLL locations.

Reproduce without rebuilding (choose new report names; evidence is not overwritten):

```bat
.venv\Scripts\python scripts\audit_windows_package.py --build-dir build\diagnostic-20261107-133601 --report build\diagnostic-20261107-133601\native-static-recheck.json
.venv\Scripts\python scripts\validate_windows.py --exe dist\diagnostic-20261107-133601\translation-engine-worker\translation-engine-worker.exe --native-audit --report build\diagnostic-20261107-133601\native-runtime-recheck.json
```

No verified packaging defect requires a new build. Required next evidence is
the same exact artifact/model/SBD on clean Windows 10 22H2 x64 and Windows 11 x64,
with OS networking disabled, no Python/global Argos/VC installer prerequisites,
actual module origins, full protocol/resource failure tests, and complete
measurements. A failure must retain its underlying loader/API error; do not
preinstall a redist to hide it. Static bundled-export checks do not fully resolve
forwarders, dynamically selected providers, unsupported CPUs, or target API sets.

A4 task 4.3's technical local audit is documented; its required native distribution
rights review remains pending and out of this turn's scope. Task 4.4 needs final
notices, 4.5/4.6 need both OS rows, and 4.7/4.8 need complete target evidence.
No task checkbox is advanced: progress remains **29/47**. No A5 work, release,
clean acceptance, or licensing implementation was performed.
