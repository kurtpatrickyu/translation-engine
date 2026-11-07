# Native candidate verification — 2026-11-07

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
[compliance staging](../../../docs/releasing.md). PUBLIC source-delivery/native-rights
gates remain pending; `001` Level A is unchanged.

