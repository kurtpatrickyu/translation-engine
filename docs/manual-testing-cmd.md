# Windows CMD: standalone worker usage and manual testing

Use **Command Prompt (`cmd.exe`)**, not PowerShell, for this guide. No Python installation, `.venv` or rebuild is needed to run the extracted
worker. The [PowerShell guide](manual-usage.md) remains available; both follow
the [same protocol v1](protocol-v1.md) and [local provisioning rules](model-provisioning.md).
This guide does not sign off OpenSpec task 4.10 or Level A acceptance for you.

The user's subsequent full CMD transcript and additional PowerShell recovery/
translation transcript are recorded in [manual-test-results.md](manual-test-results.md), where
4.10/4.8 and Level A are now accepted. The original documentation-check account
at the end of this guide remains historical and is not that user session.

## Shell and tool assumptions

New change-003 ZIPs require the separately installed latest supported official
[Microsoft VC++ x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe),
unless a compatible x64 runtime is already installed. See
[runtime requirements/remediation](native-dependencies.md#external-vc-prerequisite-for-change-003).
The historical commands/hashes in this guide remain for the preserved older
diagnostic; use the new candidate's own hashes when testing it. After extraction,
obtain upstream assets, provision and run offline without target Python. Worker
startup never downloads or installs prerequisites.

Open Command Prompt and enter this once to use a fresh nested CMD with normal
8-bit redirected output, AutoRun disabled and delayed expansion disabled:

```bat
cmd.exe /d /a /v:off
chcp 65001
ver
where tar.exe
tar.exe --version
where certutil.exe
```

Windows 10/11 installations normally provide Windows [tar.exe](https://learn.microsoft.com/en-us/windows/tar/)
(bsdtar, capable of reading ZIPs) and [certutil.exe](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil).
Verify the commands above on your machine;
stop if either tool is unavailable. This guide does not require an installer or
use PowerShell as an extraction helper. The documentation check used Windows
11 build 26300.9818, inbox `tar.exe`/bsdtar 3.8.9 and `certutil.exe` in System32.
That host check does not certify clean Windows 10/11 support.

Paste commands one line at a time into this **same** CMD window. Do not paste
Markdown fences or prompt prefixes. Stop on any unexpected error or nonzero
exit code. `set "NAME=value"` stores the value without quotation marks; quote
each `"%NAME%"` when passing a path. `%NAME%` expands an environment variable,
not a PowerShell variable. Do not define an environment variable named
`ERRORLEVEL`: it can shadow CMD's dynamic `%ERRORLEVEL%` value.

Use `cd /d` to change drives as well as directories. Spaces/Unicode in quoted
filesystem paths are supported by the worker and tested with this workflow.
Code page 65001 helps display Unicode; terminal fonts can still affect display.
The JSON examples use ASCII Unicode escapes, independent of input encoding.
CMD uses `^`, not backslash, for shell escaping; `\u4f60` remains literal JSON
input until the worker decodes it. Keep delayed expansion off so `!` in paths
is not expanded. Literal `%` or other shell metacharacters require special care;
for arbitrary request text use JSON escapes such as `\u0025` (`%`) and
`\u0026` (`&`). Do not group these examples into parenthesized command blocks:
CMD expands `%variables%` for a whole block before it executes.

## 1. Locate the existing validated artifact and create a workspace

Set `REPO` to the folder holding the existing `build`, `dist` and `downloads`
directories. The path below matches this checkout; edit only that line if your
copy lives elsewhere. This is a location convenience, not a runtime dependency
on repository source files. The executable later runs from the extracted copy.

```bat
set "REPO=D:\Documents\GitHub\translation-engine"
cd /d "%REPO%"
dir "dist\diagnostic-20261107-133601\translation-engine-worker"
set "ZIP=%REPO%\build\diagnostic-20261107-133601\frozen-unicode-all.worker.zip"
dir "%ZIP%"
set "WORK=%REPO%\runtime\CMD Café 中文 %RANDOM%-%RANDOM%"
if exist "%WORK%" (echo STOP: Workspace already exists. & exit /b 1)
mkdir "%WORK%"
if errorlevel 1 (echo STOP: Cannot create workspace. & exit /b 1)
set "APP=%WORK%\app Café 中文"
set "ASSETS=%WORK%\upstream assets"
set "MODELS=%WORK%\models Café 中文"
set "STATE=%WORK%\state Café 中文"
mkdir "%APP%" "%ASSETS%"
if errorlevel 1 (echo STOP: Cannot create subdirectories. & exit /b 1)
echo Workspace: "%WORK%"
```

The random suffix plus existence check avoids reusing an old test installation.
`exit /b 1` in the failure guards stops the nested CMD/session or batch; do not
continue after it. Model/state directories are siblings, not overlapping, and
state is outside the executable directory. They are created during CLI use.

Reviewed identities (diagnostic build `diagnostic-20261107-133601`):

| File | Bytes | SHA-256 |
|---|---:|---|
| Worker ZIP | 58,072,023 | `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b` |
| Worker EXE | 5,655,172 | `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941` |
| `translate-zh_en-1_9.argosmodel` | 74,481,402 | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| `zh-hans.onnx` | 616,442 | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

Do not substitute another diagnostic or invent a release URL. If files are
missing, identify their location rather than rebuilding. Hashes verify integrity
relative to trusted metadata; they do not independently authenticate a publisher.

## 2. Verify and extract the ZIP using Windows tools

`certutil` returning zero means hashing succeeded, **not** that it matched the
expected value. The separate exact-line `findstr` check detects a mismatch.
Use `<` exactly as shown: this host's `findstr` cannot open some Unicode paths
as filename arguments, while CMD's input redirection opens them correctly.

```bat
certutil -hashfile "%ZIP%" SHA256 > "%WORK%\zip.sha256.txt"
if errorlevel 1 (echo STOP: ZIP hashing failed. & exit /b 1)
type "%WORK%\zip.sha256.txt"
findstr /i /x /c:"965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b" < "%WORK%\zip.sha256.txt" >nul
if errorlevel 1 (echo STOP: ZIP hash does not match. & exit /b 1)
copy /b "%ZIP%" "%APP%\worker-input.zip" >nul
if errorlevel 1 (echo STOP: Cannot stage ZIP. & exit /b 1)
pushd "%APP%"
if errorlevel 1 (echo STOP: Cannot enter extraction directory. & exit /b 1)
tar.exe -xf worker-input.zip
set "EXTRACT_RC=%ERRORLEVEL%"
popd
if not "%EXTRACT_RC%"=="0" (echo STOP: ZIP extraction failed. & exit /b 1)
set "EXE=%APP%\translation-engine-worker\translation-engine-worker.exe"
certutil -hashfile "%EXE%" SHA256 > "%WORK%\exe.sha256.txt"
if errorlevel 1 (echo STOP: EXE hashing failed. & exit /b 1)
findstr /i /x /c:"627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941" < "%WORK%\exe.sha256.txt" >nul
if errorlevel 1 (echo STOP: EXE hash does not match. & exit /b 1)
dir "%APP%\translation-engine-worker\_internal"
"%EXE%" --version
if errorlevel 1 (echo STOP: Worker cannot start. & exit /b 1)
```

Expected version: `0.1.0`. Retain the **whole** extracted directory, including
`_internal`, Python/native DLLs and metadata. A lone EXE is not standalone.
The complete extracted artifact is 159,927,584 file bytes. If the hash display
format differs on another Windows version, stop and compare the complete digest
manually; never treat a failed exact-line check as permission to skip integrity.

This host's `tar.exe` also failed with a Unicode `-C` pathname. The commands
instead use CMD's Unicode-capable `copy`/`pushd` and pass tar only an ASCII
relative archive filename. This was verified inside the Unicode workspace;
`worker-input.zip` is a temporary copy outside the actual onedir and is removed
with the workspace later. Do not replace this with an untested Unicode `-C` call.

## 3. Reuse and verify original local assets

These commands copy the existing local originals; they do not download or modify
them. If either original is absent, obtain it explicitly from its provider and
verify it before proceeding. This project's worker releases do not host models.

- [Original Argos zh→en package 1.9](https://argos-net.com/v1/translate-zh_en-1_9.argosmodel)
- [Original MiniSBD v0.0.1 zh-hans ONNX](https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx)

```bat
copy /b "%REPO%\downloads\translate-zh_en-1_9.argosmodel" "%ASSETS%\translate-zh_en-1_9.argosmodel"
if errorlevel 1 (echo STOP: Original translation asset missing or unreadable. & exit /b 1)
copy /b "%REPO%\downloads\zh-hans.onnx" "%ASSETS%\zh-hans.onnx"
if errorlevel 1 (echo STOP: Original ONNX asset missing or unreadable. & exit /b 1)
set "MODELFILE=%ASSETS%\translate-zh_en-1_9.argosmodel"
set "SBDFILE=%ASSETS%\zh-hans.onnx"
certutil -hashfile "%MODELFILE%" SHA256 > "%WORK%\model.sha256.txt"
if errorlevel 1 (echo STOP: Translation hashing failed. & exit /b 1)
findstr /i /x /c:"62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d" < "%WORK%\model.sha256.txt" >nul
if errorlevel 1 (echo STOP: Translation hash mismatch. & exit /b 1)
certutil -hashfile "%SBDFILE%" SHA256 > "%WORK%\sbd.sha256.txt"
if errorlevel 1 (echo STOP: ONNX hashing failed. & exit /b 1)
findstr /i /x /c:"b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e" < "%WORK%\sbd.sha256.txt" >nul
if errorlevel 1 (echo STOP: ONNX hash mismatch. & exit /b 1)
```

Do not select a newer asset, replace a hash, or use an HTML error page as a
model. See [provenance/attribution](../models/provenance.json); external model
terms are not declared cleared. Public distribution of bundled MiniSBD code,
native DLLs and other components still requires compliance review.

## 4. Provision from local files

No network access is needed from here. Provisioning validates both original
hashes, safe bounded extraction, local ONNX and runtime warm-up before atomic
promotion. It preserves existing immutable installations on failure.

```bat
"%EXE%" provision-model --file "%MODELFILE%" --sbd-file "%SBDFILE%" --models-dir "%MODELS%" --state-dir "%STATE%" > "%WORK%\provision.stdout.txt" 2> "%WORK%\provision.stderr.txt"
set "PROVISION_RC=%ERRORLEVEL%"
echo Provisioning exit code: %PROVISION_RC%
type "%WORK%\provision.stderr.txt"
if not "%PROVISION_RC%"=="0" (echo STOP: Provisioning failed. & exit /b 1)
```

Expect exit **0**, empty stdout, and `Provisioned <path>. Restart any running
worker.` on stderr. Stderr is the correct place for this success diagnostic.
Non-ASCII paths in diagnostic text may be escaped or displayed differently
because native tool/frozen stderr encodings vary; this does not change the
actual directory name or the worker's UTF-8 protocol output.
Nonzero CLI failure codes must be investigated, even if some files exist.
Use `%MODELS%` as the package **parent**, not the archive or installed package
subdirectory. Use a new managed directory for a replacement; never edit receipts
or installed model bytes to bypass validation.

Capture `%ERRORLEVEL%` immediately on the **next line**, before `type`, `findstr`
or another command changes it. Do not write `command & echo %ERRORLEVEL%`: the
value can expand before that command runs. `if errorlevel 1` tests “at least 1”,
not equality. A worker process may exit zero despite request-level errors;
always inspect JSON readiness/errors as well as its process exit status.

## 5. Short happy-path smoke test: one persistent worker, six requests

CMD `/a` plus ASCII-only `echo` lines creates ordinary single-byte ASCII, also
valid UTF-8, **without a BOM or UTF-16**. Every command writes exactly one CRLF
line. Backslashes in JSON escapes are literal. Leading `>` starts a new file;
`>>` appends. Do not add blank lines or redirect `echo` with a trailing space
inside a JSON string. Do not run this from `cmd /u`.

```bat
> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"i0","command":"info"}
>> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"h","command":"health"}
>> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"t1","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
>> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"t2","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
>> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"i1","command":"info"}
>> "%WORK%\smoke.ndjson" echo {"protocol_version":1,"id":"s","command":"shutdown"}
"%EXE%" --models-dir "%MODELS%" --state-dir "%STATE%" < "%WORK%\smoke.ndjson" > "%WORK%\smoke.stdout.ndjson" 2> "%WORK%\smoke.stderr.txt"
set "SMOKE_RC=%ERRORLEVEL%"
echo Worker exit code: %SMOKE_RC%
type "%WORK%\smoke.stdout.ndjson"
type "%WORK%\smoke.stderr.txt"
find /v /c "" < "%WORK%\smoke.stdout.ndjson"
```

Expect exit 0, exactly six response lines in ID order `i0,h,t1,t2,i1,s`, and
empty stderr. `i0` has no ready pairs; `h` reports `ready:true`; `t1` and `t2`
translate `你好，世界！` to matching English (retained evidence: `Hello, world!`).
`i1` lists the ready pair, and `s` acknowledges shutdown before process exit.
The single EXE invocation processes all six requests using retained resources.
The line count alone does not prove success: inspect every response's `ok`,
`result`/`error`, IDs and readiness. Do not append later commands after shutdown.

`>` captures **only stdout**; `2>` captures **only stderr**. Do not use `2>&1`.
The worker writes UTF-8 JSON itself; CMD redirection preserves those bytes.
The first initialization takes longer than later requests; this guide sets no
performance deadline. Retain unexpected logs/nonzero codes instead of rebuilding.

## 6. Interactive usage

To type requests yourself, start a new worker without `<` or stdout redirection:

```bat
"%EXE%" --models-dir "%MODELS%" --state-dir "%STATE%" 2> "%WORK%\interactive.stderr.txt"
```

There is no greeting; it is waiting for input. Paste each line separately and
press Enter, reading the response before the next line. These lines are **worker
input**, not CMD commands; do not prefix them with `echo` or paste fences:

```json
{"protocol_version":1,"id":"health","command":"health"}
{"protocol_version":1,"id":"info","command":"info"}
{"protocol_version":1,"id":"translate","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
{"protocol_version":1,"id":"shutdown","command":"shutdown"}
```

Expect successful ready health, version/capability info, English translation and
shutdown acknowledgment. Console input echo is not unsolicited worker stdout.
Only **after returning to CMD**, inspect exit/stderr:

```bat
set "INTERACTIVE_RC=%ERRORLEVEL%"
echo Interactive exit code: %INTERACTIVE_RC%
type "%WORK%\interactive.stderr.txt"
```

Do not send CMD commands to the waiting worker. Processing is sequential;
shutdown cannot cancel an active translation. If stuck, record the last request
and stop only your own worker if necessary; do not record forced interruption
as normal shutdown.

## 7. Optional deeper checks

Run an independent worker with paragraph/empty/error/recovery requests, using
new filenames so the happy-path evidence is retained:

```bat
> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"p","command":"translate","source":"zh","target":"en","text":"\u8fd9\u662f\u7b2c\u4e00\u6bb5\u3002\n\u8fd9\u662f\u7b2c\u4e8c\u6bb5\u3002"}
>> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"empty","command":"translate","source":"zh","target":"en","text":""}
>> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"unsupported","command":"translate","source":"fr","target":"en","text":"Bonjour"}
>> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"bad","command":"not-a-command"}
>> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"recovered","command":"health"}
>> "%WORK%\deeper.ndjson" echo {"protocol_version":1,"id":"done","command":"shutdown"}
"%EXE%" --models-dir "%MODELS%" --state-dir "%STATE%" < "%WORK%\deeper.ndjson" > "%WORK%\deeper.stdout.ndjson" 2> "%WORK%\deeper.stderr.txt"
set "DEEPER_RC=%ERRORLEVEL%"
echo Deeper exit code: %DEEPER_RC%
type "%WORK%\deeper.stdout.ndjson"
type "%WORK%\deeper.stderr.txt"
```

Expect six correlated responses, translated paragraph text containing an escaped
`\n`, empty output for `empty`, `UNSUPPORTED_LANGUAGE`, `UNKNOWN_COMMAND`, then
ready health and shutdown. Request errors do not imply a nonzero process exit.
Model quality is not lossless Unicode preservation; see [quality limits](compatibility-spike.md).

For missing-model handling, do not corrupt the good installation:

```bat
> "%WORK%\missing.ndjson" echo {"protocol_version":1,"id":"missing","command":"health"}
>> "%WORK%\missing.ndjson" echo {"protocol_version":1,"id":"done","command":"shutdown"}
"%EXE%" --models-dir "%WORK%\never provisioned" --state-dir "%WORK%\missing state" < "%WORK%\missing.ndjson" > "%WORK%\missing.stdout.ndjson" 2> "%WORK%\missing.stderr.txt"
set "MISSING_RC=%ERRORLEVEL%"
echo Missing-model process exit code: %MISSING_RC%
type "%WORK%\missing.stdout.ndjson"
type "%WORK%\missing.stderr.txt"
```

Expect process exit 0, a health envelope with `ok:true` but `ready:false` and
`result.error.code:"MODEL_MISSING"`, then shutdown. No download occurs. Cached
readiness failures require a worker restart after correcting resources.

Optionally verify a genuine nonzero CLI failure without loading a model: omit
the required `--state-dir` deliberately. Keep this separate from worker input.

```bat
"%EXE%" --models-dir "%MODELS%" > "%WORK%\cli-error.stdout.txt" 2> "%WORK%\cli-error.stderr.txt"
set "CLI_ERROR_RC=%ERRORLEVEL%"
echo Expected CLI error exit code 2, actual: %CLI_ERROR_RC%
type "%WORK%\cli-error.stderr.txt"
```

Expect argparse's missing-`--state-dir` error on stderr, no protocol responses,
and exit 2. This is an intentional failure, not a translation readiness result.

## 8. Retain results, then clean up only this workspace

Before cleanup, save any wanted hashes, request/response files, stderr, actual
exit codes, OS/shell version and acquisition/reuse details outside `%WORK%`.
Do not claim clean-OS networking or task 4.10 completion from these documentation
checks. Unknown model terms and bundled-code/native compliance stay pending.
The [native audit](native-dependencies.md) observed external Teruten modules on
the development host; they are not proven app dependencies. Do not modify
security software or bundle/allowlist those modules to force an isolation pass.

Close workers and move outside the workspace. The following delete is permanent
and asks for confirmation: confirm the full displayed path is exactly the new
`%REPO%\runtime\CMD Café 中文 <suffix>` directory you created, never the repo,
`runtime` itself, `downloads` or an original artifact directory. If the variable
is missing/changed or the directory is unexpected, stop and resolve it first.

```bat
cd /d "%REPO%"
echo Workspace to remove: "%WORK%"
dir /a "%WORK%"
rmdir /s "%WORK%"
```

Answer `Y` only after checking that exact workspace. Originals remain outside
it. To leave it for later inspection, skip `rmdir`. To exit the nested CMD after
finishing, type `exit`.

These snippets are for interactive CMD. If adapting into a `.cmd` file, keep
its non-ASCII path text UTF-8 without BOM, use Windows CRLF line endings and
`chcp 65001` before those lines, and replace
interactive `for %F` variables with `%%F` if you add loops. This guide avoids
such loops and keeps exit-code capture on separate lines. Do not introduce
PowerShell's `Out-File`, CMD `/u`, or an editor's UTF-16/BOM save for NDJSON.

## Documentation verification boundary

The documented file-driven commands are checked with the existing executable,
cached assets, CMD-generated ASCII/CRLF input, Unicode/spaces paths and separated
output files. This is command verification, not a manual tester sign-off or
clean Windows support evidence. Interactive console rendering, your own paths,
human-pasted inputs and your chosen networking conditions still need your
walkthrough. No rebuild, model download or publication is part of this guide.

Documentation check on 2026-11-07: provisioned successfully from copied verified
originals; happy/deeper/missing sessions produced 6/6/2 correlated responses,
all three worker exits were zero and their stderr files empty. Happy-path
translations were `Hello, world!`; deeper paragraph/empty/error/recovery checks
passed. Raw request files were ASCII, CRLF-terminated with no BOM or NUL bytes.
Missing-state CLI failure returned 2 and a deliberately wrong hash comparison
returned 1. Exact-directory workspace cleanup also passed. Initial helper/path
failures were retained, then corrected in these snippets; none required a
worker change. Maintainer-local raw logs are under
`runtime/cmd-guide-verification-20261107*.log`,
`runtime/cmd-guide-negative-cleanup-20261107.log` and
`runtime/cmd-guide-evidence-20261107/` (ignored test evidence, not part of the
standalone distribution). The documentation-only verification batches use UTF-8
without BOM and CRLF line endings. OpenSpec 4.10 remains unchanged.
