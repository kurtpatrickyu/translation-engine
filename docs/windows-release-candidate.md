# Windows worker 0.1.0-rc.1: local acceptance candidate

This candidate uses the validated post-003 executable, without rebuilding it.
It is assembled for clean-machine acceptance, with publication still blocked.
Intel/native terms, NumPy's renamed Microsoft DLL rights, remaining source/notice
correspondence, both clean Windows rows, OS-denied networking, complete target
measurements and final publication approval remain pending. No model is included.

The worker source commit is
`b064e29517fb793b2fcf0bf309b6fc78f623367d`; licensing materials come from
`6faf8a8d40713e7f5bafb787a2e900b104995ddb`. The executable's SHA-256 is
`ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d`.
The newly assembled ZIP has its own hash in `manifest.json` and `SHA256SUMS`;
do not use the older diagnostic ZIP's digest for it.

Use CMD (`cmd.exe /d /a /v:off`). Node.js 22 is needed only on the maintainer
machine for assembly. On the maintainer machine, retain the exact existing
build/dist evidence and cached source/wheels, then run from the repository root:

```bat
node scripts\stage_compliance.cjs candidate-staging\release-rc1-compliance
rem Expected exit code 2: intact preparation with unresolved readiness.
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
node scripts\assemble_release.cjs candidate-staging\worker-0.1.0-rc.1
node scripts\assemble_release.cjs --check candidate-staging\worker-0.1.0-rc.1
node scripts\assemble_release.cjs candidate-staging\worker-0.1.0-rc.1-repeat
```

Use fresh directories. The reviewed release configuration pins the compliance
manifest, source commits, asset metadata and existing regression evidence.
If the compliance directory already exists, use the stager's `--check` instead
of regenerating in place. Assembly and verification return zero for a valid
local candidate; this never means public release readiness. `--check` rebuilds
expected bytes in memory and rejects missing/extra/tampered files or metadata.
ZIP paths, timestamps, permissions and compression settings are deterministic.
Assembly never rebuilds PyInstaller, downloads assets or creates tags/releases.

Transfer the entire eight-file candidate directory to a clean Windows test
machine, outside any model or development directories. Keep it unchanged;
extract the worker elsewhere. Verify against a separately trusted copy of the
manifest/checksums. Checksums alone do not authenticate the publisher.

```bat
cd /d C:\WorkerCandidate
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verify-checksums.ps1
if errorlevel 1 exit /b 1
certutil -hashfile translation-engine-worker-win-x64.zip SHA256
mkdir C:\WorkerAcceptance
cd /d C:\WorkerAcceptance
tar.exe -xf C:\WorkerCandidate\translation-engine-worker-win-x64.zip
set "EXE=C:\WorkerAcceptance\translation-engine-worker\translation-engine-worker.exe"
certutil -hashfile "%EXE%" SHA256
```

Compare the displayed EXE digest with the value above. Keep the complete onedir,
including `_internal` and `release-info`. No target Python, Node.js or global
Argos installation is required. No ordinary VC++ DLL or installer is bundled.
NumPy's wheel-local renamed DLL remains unchanged.

Obtain the latest supported official **VC++ v14 x64 Redistributable** separately:
<https://aka.ms/vc14/vc_redist.x64.exe>. Install/update/repair it if necessary;
keep a compatible newer installation and complete any requested restart. An
offline tester can transfer a separately acquired official installer. The worker
does not download or install prerequisites. Locally tested 14.50.35719.0 is not
a proven minimum. Registration is a hint, not proof that the loader succeeds:

```bat
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /reg:64
"%EXE%" --version
```

Expect `0.1.0`. Preserve original loader errors and exit codes if startup fails;
Python may never initialize, so no protocol response is guaranteed.

Acquire these original assets directly from upstream on a connected machine,
verify them, and transfer them to `C:\WorkerAssets`. Do not put them inside the
candidate or extracted worker. Their terms/provenance remain as recorded in
the manifest; this project does not redistribute them.

| File | Upstream | SHA-256 |
|---|---|---|
| translate-zh_en-1_9.argosmodel | https://argos-net.com/v1/translate-zh_en-1_9.argosmodel | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| zh-hans.onnx | https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

```bat
certutil -hashfile C:\WorkerAssets\translate-zh_en-1_9.argosmodel SHA256
certutil -hashfile C:\WorkerAssets\zh-hans.onnx SHA256
```

Stop if either complete digest differs. With networking denied at the OS level,
use fresh nonoverlapping model/state directories, then provision and test:

```bat
"%EXE%" provision-model --file C:\WorkerAssets\translate-zh_en-1_9.argosmodel --sbd-file C:\WorkerAssets\zh-hans.onnx --models-dir C:\WorkerAcceptance\models --state-dir C:\WorkerAcceptance\state
if errorlevel 1 exit /b 1
> C:\WorkerAcceptance\smoke.ndjson echo {"protocol_version":1,"id":"h","command":"health"}
>> C:\WorkerAcceptance\smoke.ndjson echo {"protocol_version":1,"id":"t","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
>> C:\WorkerAcceptance\smoke.ndjson echo {"protocol_version":1,"id":"s","command":"shutdown"}
"%EXE%" --models-dir C:\WorkerAcceptance\models --state-dir C:\WorkerAcceptance\state < C:\WorkerAcceptance\smoke.ndjson > C:\WorkerAcceptance\smoke.stdout.ndjson 2> C:\WorkerAcceptance\smoke.stderr.txt
echo %ERRORLEVEL%
type C:\WorkerAcceptance\smoke.stdout.ndjson
type C:\WorkerAcceptance\smoke.stderr.txt
```

Expect readiness true, a successful English translation and shutdown response,
response-only stdout, and exit zero. This smoke is only the beginning of clean
acceptance. On both Windows 10 22H2 x64 and Windows 11 x64, record edition/build,
official runtime version, CPU/RAM/storage/VM/power details, candidate/model
hashes, actual OS network-denial controls, native origins, repeated requests,
Unicode relocation, errors/flush/shutdown and the existing target measurements.
Use the same ZIP and external asset hashes for both rows. No clean result is
claimed by local assembly or the development-host regressions.

The compliance ZIP contains the existing prepared notices/source dossier and
its detailed blockers. The corresponding-source ZIP adds a Git snapshot of the
binary's source commit alongside matching staged third-party sources and exact
original build inputs. It is source preparation while native/source questions
remain unresolved. The public repository is the primary worker-source location.
A future immutable release tag must resolve to a commit retaining these exact
binary build inputs; changed code requires a new build and validation. Record
the final tag/commit and same-release source asset URLs before publication.
