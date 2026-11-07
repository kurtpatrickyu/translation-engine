# Manual usage and testing: existing Windows worker

Prefer Command Prompt? Use the [CMD-only guide](manual-testing-cmd.md), which
uses Windows tar/certutil and the same executable/protocol without PowerShell.

The user's subsequent completed CMD walkthrough and PowerShell recovery/session
evidence are recorded in [manual-test-results.md](manual-test-results.md).
Level A has since been accepted. The documentation-verification descriptions
and blank record template below remain distinct from that later user session.

Use the existing Windows x64 CPU diagnostic without installing Python, dependencies
or rebuilding. There is no public production release yet. Future GitHub Releases
distribute the worker and integrity/compliance material; users obtain original
model/ONNX files directly from upstream.

This is task **4.9's guide**, not a completed manual session. Task 4.10 records
the walkthrough; task 4.8 signs off local usability afterward. Pending public
Windows support, OS-denied networking and redistribution review do not prevent
local testing. Do not publish this diagnostic as a cleared release.

## 1. Verify and extract the existing worker

For **new change-003 ZIPs**, first install the latest supported official
[Microsoft Visual C++ x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe)
separately if needed. Keep a compatible newer installation. See
[runtime requirements and missing-runtime remediation](native-dependencies.md#external-vc-prerequisite-for-change-003).
Then verify/extract the complete candidate ZIP using its own recorded hashes,
obtain the upstream model/ONNX assets, provision locally and run offline; target
Python is not needed. No prerequisite is downloaded/installed at worker startup.
The commands/hashes below intentionally identify the preserved older diagnostic,
which bundles the four ordinary VC DLLs; do not apply those hashes to a new ZIP.

Use Windows PowerShell 5.1 or PowerShell 7 in a console, starting at the
repository root. These commands are **PowerShell, not CMD**. If you have custom
shell/error settings, open `powershell.exe -NoProfile` with normal defaults.
Keep the same console/variables throughout. JSON examples later go to the
running worker, not to the PowerShell prompt.

| Item | Reviewed identity |
|---|---|
| Build | `diagnostic-20261107-133601` |
| ZIP | `build/diagnostic-20261107-133601/frozen-unicode-all.worker.zip` |
| ZIP bytes / SHA-256 | 58,072,023 / `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b` |
| EXE SHA-256 | `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941` |
| Extracted files | 159,927,584 bytes |
| Engine / protocol | `0.1.0` / `1` |
| Argos | `1.11.1`, unmodified commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` |

If the artifact is absent or its hash differs, stop and identify the intended
artifact. Do not rebuild, substitute another distribution or change the expected
hash to make verification pass. Hashes provide integrity relative to trusted
metadata, not independent authenticity.

Create a unique workspace containing spaces/Unicode. Verify before extraction
and retain the complete application folder, including `_internal`:

```powershell
$repo = (Get-Location).Path
$zip = Join-Path $repo 'build\diagnostic-20261107-133601\frozen-unicode-all.worker.zip'
$expectedZip = '965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b'
if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256 -ErrorAction Stop).Hash -ine $expectedZip) {
    throw 'Worker ZIP checksum mismatch. Stop.'
}
$work = Join-Path $repo ('runtime\manual Café 中文 ' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work -ErrorAction Stop | Out-Null
$app = Join-Path $work 'app Café 中文'
Expand-Archive -LiteralPath $zip -DestinationPath $app -ErrorAction Stop
$exe = Join-Path $app 'translation-engine-worker\translation-engine-worker.exe'
$expectedExe = '627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941'
if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256 -ErrorAction Stop).Hash -ine $expectedExe) {
    throw 'Extracted executable checksum mismatch. Stop.'
}
$assets = Join-Path $work 'upstream assets'
New-Item -ItemType Directory -Path $assets -ErrorAction Stop | Out-Null
$models = Join-Path $work 'models Café 中文'
$state = Join-Path $work 'state Café 中文'
$assetsVerified = $false
```

Model/state paths must be separate and writable, with state outside the app
directory. The CLI creates them as needed. Pass the full paths held in these
variables; the call operator `&` handles the executable path correctly. Never
copy only the EXE or place state inside `_internal`.

## 2. Obtain and verify the original upstream files

The new `$assets` directory starts empty. **Populate it before hashing.** The
block below copies missing files from this repository's existing `downloads/`
originals using `Copy-Item -LiteralPath ... -ErrorAction Stop`; it does not
redownload or modify those originals. An existing workspace asset is left in
place and must still pass its hash check.

If you do not already have an original in `downloads/`, obtain it explicitly
from the upstream links below and save it into `$assets` with the exact filename,
then rerun the whole block. Acquisition may use networking and browser
redirects; the worker never downloads assets. Record the actual source/date,
including reuse. Do not skip a failed check or continue to provisioning.

| Asset | Upstream URL | Version / bytes / SHA-256 |
|---|---|---|
| `translate-zh_en-1_9.argosmodel` | [Argos provider](https://argos-net.com/v1/translate-zh_en-1_9.argosmodel) | Package 1.9, declared Argos 1.9.0; 74,481,402 bytes; `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| `zh-hans.onnx` | [MiniSBD upstream v0.0.1](https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx) | Chinese Simplified; 616,442 bytes; `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

```powershell
$assetsVerified = $false
$modelFile = Join-Path $assets 'translate-zh_en-1_9.argosmodel'
$sbdFile = Join-Path $assets 'zh-hans.onnx'
if (-not (Test-Path -LiteralPath $modelFile -PathType Leaf -ErrorAction Stop)) {
    $localModel = Join-Path $repo 'downloads\translate-zh_en-1_9.argosmodel'
    if (-not (Test-Path -LiteralPath $localModel -PathType Leaf -ErrorAction Stop)) {
        throw "Missing translation asset: $localModel. Obtain the original from the upstream link, save it as $modelFile, then rerun step 2. Stop before provisioning."
    }
    Copy-Item -LiteralPath (Join-Path $repo 'downloads\translate-zh_en-1_9.argosmodel') -Destination $modelFile -ErrorAction Stop
}
if (-not (Test-Path -LiteralPath $sbdFile -PathType Leaf -ErrorAction Stop)) {
    $localSbd = Join-Path $repo 'downloads\zh-hans.onnx'
    if (-not (Test-Path -LiteralPath $localSbd -PathType Leaf -ErrorAction Stop)) {
        throw "Missing MiniSBD asset: $localSbd. Obtain the original from the upstream link, save it as $sbdFile, then rerun step 2. Stop before provisioning."
    }
    Copy-Item -LiteralPath (Join-Path $repo 'downloads\zh-hans.onnx') -Destination $sbdFile -ErrorAction Stop
}
foreach ($assetPath in @($modelFile, $sbdFile)) {
    if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf -ErrorAction Stop)) {
        throw "Required asset is missing: $assetPath. Stop before hashing or provisioning."
    }
}
$expectedModel = '62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d'
$expectedSbd = 'b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e'
if ((Get-FileHash -LiteralPath $modelFile -Algorithm SHA256 -ErrorAction Stop).Hash -ine $expectedModel) {
    throw 'Translation asset checksum mismatch. Stop before provisioning.'
}
if ((Get-FileHash -LiteralPath $sbdFile -Algorithm SHA256 -ErrorAction Stop).Hash -ine $expectedSbd) {
    throw 'MiniSBD asset checksum mismatch. Stop before provisioning.'
}
Get-Item -LiteralPath $modelFile, $sbdFile -ErrorAction Stop | Select-Object Name, Length
$assetsVerified = $true
```

Run the block from its first line, not selected hash/copy lines out of order.
It starts with verification false; a missing file, copy error or wrong hash
throws immediately, and verification becomes true only after **both** assets
exist and match. Step 3 refuses to provision unless this block completed.

Stop if upstream is unavailable, returns an HTML/error page, or changes bytes.
Do not substitute a newer model, rename another resource, or relax hashes.
See [reviewed provenance](../models/provenance.json). The archive credits OPUS-MT
and identifies the original OPUS model as CC-BY 4.0; unknown packaged model/ONNX
terms are not declared cleared. Preserve attribution/known-unknown terms. This
project does not host these binaries. MiniSBD AGPLv3 code/source/notices and
bundled native/component redistribution obligations still gate public worker
distribution; excluding models does not remove them.

## 3. Provision offline from local files

Acquisition is finished. The worker needs no network for the remaining steps
and does not fetch models, update indexes or download missing SBD resources.
For a manual record, state whether this host remained online or had an existing
network restriction; an online run is not OS-denied-network proof. Do not change
security software or system networking just to complete this local guide.

```powershell
if ($assetsVerified -ne $true) {
    throw 'Assets are not verified. Complete step 2 successfully before provisioning.'
}
& $exe --version
if ($LASTEXITCODE -ne 0) { throw 'Executable version check failed.' }
& $exe provision-model --file $modelFile --sbd-file $sbdFile --models-dir $models --state-dir $state
if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed. Retain stderr and stop.' }
```

Expected version: `0.1.0`. Provisioning exits zero and prints
`Provisioned <installed package path>. Restart any running worker.` on **stderr**.
That diagnostic is expected; provisioning emits no protocol responses. Judge
the exit code/message, not the console's stderr display color.

The CLI verifies hashes and bounded safe extraction, stages package-local ONNX,
validates installed integrity, performs real warm-up, then atomically promotes
`translate-zh_en-1_9`. Failure must not activate a partial package. Installations
are immutable: rerunning validates an existing installation without overwriting
active files. Use a new model directory for replacements. Never edit installed
models, receipts or hashes to bypass a failure. See [provisioning details](model-provisioning.md).

## 4. Drive one persistent worker

Use code page 65001 for readable UTF-8 output. The requests below use ASCII JSON
`\u` escapes decoded by the worker to real Chinese, avoiding input-code-page
ambiguity. Literal Chinese is valid when sent as UTF-8. Do not generate protocol
input with a default PowerShell text pipeline or `Out-File`: Windows PowerShell
encoding defaults may alter its bytes.

```powershell
chcp.com 65001 > $null
$stderrFile = Join-Path $work 'worker.stderr.log'
& $exe --models-dir $models --state-dir $state 2> $stderrFile
```

There is **no greeting**. It is waiting for a **request**, not PowerShell code.
Every `json` block below contains complete **requests to send**; expected
responses are described separately in prose and are **read-only output**.

- Paste only one complete request object on exactly **one line**, press Enter,
  then wait for its response before sending the next request.
- Each request needs `protocol_version`, `id`, `command`, plus `source`, `target`
  and `text` for translation. Copy the whole object, including those fields.
- **Do not paste response JSON**, such as an object containing `ok`/`result`,
  or a response's inner `source`/`target`/`text` object. It is not a request.
- **Do not paste blank/whitespace-only lines, Markdown fences, headings, or
  console prompts.** Blank lines are invalid JSON, not separators. A block with
  two examples means two separate sends, with no blank line between them.
- Keep a paragraph break inside a JSON string as the literal escape `\n`, not
  an actual newline splitting that request. The `\u` escapes are ready to paste.

A response-shaped object missing request fields yields `INVALID_REQUEST`;
blank lines yield `INVALID_JSON`. After either error, send the next complete
request rather than pasting the error response back. Console input echo is not
worker stdout; a transcript alone does not establish byte-level stdout purity.

**Request to send — inspect before initialization:**

```json
{"protocol_version":1,"id":"info-before","command":"info"}
```

**Expected response (read, do not paste):** `ok:true`, engine `0.1.0`, Argos
`1.11.1`, protocol 1, configured `zh`→`en` and empty `ready_pairs`. Info does not
initialize or prove readiness.

**Request to send — initialize:**

```json
{"protocol_version":1,"id":"health","command":"health"}
```

Expect `ok:true`, `result.alive:true`, `result.ready:true`, null error. First
health can take longer than subsequent calls; this is not a performance budget.
If not ready, retain error/stderr and troubleshoot. Provisioning warm-up is not
a substitute for readiness in this new process.

**Requests to send separately — translate `你好，世界！` twice in the same process:**

```json
{"protocol_version":1,"id":"t1","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
{"protocol_version":1,"id":"t2","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
```

Expect successful responses correlated to `t1` and `t2`, with matching nonempty
English. The pinned-model evidence records `Hello, world!`; record what this
run actually returns. The worker retains initialized resources across requests.
**Requests to send separately — paragraph newlines and empty input:**

```json
{"protocol_version":1,"id":"paragraph","command":"translate","source":"zh","target":"en","text":"\u8fd9\u662f\u7b2c\u4e00\u6bb5\u3002\n\u8fd9\u662f\u7b2c\u4e8c\u6bb5\u3002"}
{"protocol_version":1,"id":"empty","command":"translate","source":"zh","target":"en","text":""}
```

Expect translated paragraph text with an escaped `\n` in its JSON string and
`result.text:""` for empty input. Translation quality/Unicode preservation is
not lossless; see [known model limits](compatibility-spike.md).
**Requests to send separately — intentional errors and recovery:**

```json
{"protocol_version":1,"id":"unsupported","command":"translate","source":"fr","target":"en","text":"Bonjour"}
{"protocol_version":1,"id":"bad-command","command":"not-a-command"}
{"protocol_version":1,"id":"info-after","command":"info"}
```

Expect `ok:false` / `error.code:"UNSUPPORTED_LANGUAGE"`, then `UNKNOWN_COMMAND`,
with the corresponding IDs preserved. `info-after` must succeed and list the
ready pair. Responses contain `protocol_version`, `id`, `ok` and exactly one of
`result`/`error`. Follow the [authoritative protocol v1 and limits](protocol-v1.md);
the unknown command above is deliberately invalid. No command installs assets.
**Request to send — finish this same process:**

```json
{"protocol_version":1,"id":"shutdown","command":"shutdown"}
```

Expect `ok:true`, `result.shutdown:true`, then return to PowerShell. Only after
the worker exits, run:

```powershell
$workerExit = $LASTEXITCODE
if ($workerExit -ne 0) { throw "Worker exited with code $workerExit. Retain diagnostics." }
Get-Content -LiteralPath $stderrFile
```

Normal worker stderr should be empty. Retain unexpected diagnostics separately;
never merge stderr into protocol stdout. Send no requests after shutdown. If an
operation stalls, record the last request/time. Processing is sequential and
shutdown cannot interrupt inference; there is no cancellation/automatic retry
contract. If necessary, stop only the worker you started and record abnormal exit.

## 5. Optional missing-model check

After normal shutdown, start another worker with a never-provisioned model path.
Do not damage the working installation to test errors:

```powershell
$missingModels = Join-Path $work 'missing models'
$missingState = Join-Path $work 'missing state'
$missingStderr = Join-Path $work 'missing-model.stderr.log'
& $exe --models-dir $missingModels --state-dir $missingState 2> $missingStderr
```

**Requests to send individually** to that running worker (not to PowerShell):

```json
{"protocol_version":1,"id":"missing-health","command":"health"}
{"protocol_version":1,"id":"missing-info","command":"info"}
{"protocol_version":1,"id":"missing-shutdown","command":"shutdown"}
```

Health inspection has `ok:true`, but `result.ready:false` and
`result.error.code:"MODEL_MISSING"`. Info/shutdown still work. On return, check
`$LASTEXITCODE` is zero and inspect `$missingStderr`. No download should occur;
a successful health envelope does not mean translation is ready.

## Troubleshooting and evidence limits

| Observation | Action |
|---|---|
| Hash differs or upstream is unavailable | Stop; record actual source/error/size/hash. Never replace a trusted digest to accept new bytes. |
| DLL/loader failure or executable cannot start | Retain exact Windows error, artifact hash and OS build. Restore the full onedir from the same verified ZIP; do not copy random DLLs or preinstall a redist to conceal the original failure. |
| CLI/path failure | Check arguments, writable state, non-overlapping model/state and state outside the app directory. |
| `MODEL_MISSING` | Point `--models-dir` at the parent containing installed `translate-zh_en-1_9`, not the archive or package subdirectory itself. |
| `MODEL_INCOMPATIBLE` | Verify originals and provision into a new managed directory. Do not edit installed files/receipts or add fallback ONNX files. |
| Backend/translation failure | Retain readiness/error/stderr and paths. Initialization failures are cached until restart; fix the cause first, without automatic reinstall/downgrade/rebuild. |
| JSON/encoding failure | Send one complete LF/CRLF-terminated UTF-8 JSON line, no BOM/fences/blank lines. Use ASCII escapes above if console input is uncertain. |

Neither clean Windows 10 22H2 x64 nor clean Windows 11 x64 support is certified
by development-host success. The [native audit](native-dependencies.md) observed
external Teruten `T_Prevent64.dll` / `TDCommonLib64.dll`; they are not proven app
dependencies. Retain this strict isolation finding without bundling/allowlisting
them or altering security software. See [Unicode evidence](unicode-path-validation.md).
Python network-attempt instrumentation does not prove all native networking is
denied. This guide does not complete public OS/compliance/publication gates.

Historical evidence retains old counts/gates. The [current OpenSpec tasks](../openspec/changes/001-build-offline-translation-engine/tasks.md)
separate local usability from public readiness. The earlier automated tests and
reports are evidence, not a newly executed manual session.

## Blank record for task 4.10

Copy into a new local note **when that task is authorized**. Leave results
pending until observed; the guide itself does not satisfy the walkthrough.

| Field | Record |
|---|---|
| Status / tester / time | Pending; actual tester/date/time/timezone |
| Host / console | OS edition/build, CPU/RAM, shell/version, known host limitations |
| Worker | Build identity, ZIP/EXE paths and actual hashes |
| Assets | Acquisition/reuse source/date, filenames, sizes and actual hashes |
| Paths / network | Full paths and Unicode/spaces; actual online/offline controls without inferred OS denial |
| Provisioning | Invocation, exit, stdout/stderr, installed path |
| Worker requests | Actual IDs/JSON, readiness, repeated/paragraph/empty/error/recovery observations |
| Lifecycle | Shutdown response/exit, stderr, any interruption/timeout |
| Optional check | Missing-model observations, or explicitly not run |
| Conclusion | Passed/failed/unrun steps and limitations; no inferred Level A sign-off or public clearance |

Documentation verification checks CLI help, request schemas, local links and
recorded asset/artifact identities. It does not execute the manual workflow.
