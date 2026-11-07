# Manual validation and Level A acceptance — 2026-11-07

**Level A (locally usable, manually testable worker) is complete.** Tasks 4.9,
4.10 and 4.8 are complete; LOCAL is **37/37**, overall **37/54**. All **17 PUBLIC
tasks remain pending**. This acceptance concerns the identified local diagnostic,
not a publicly redistributable release or certified Windows support matrix.

## Evidence sources and dates

- **CMD: transcript-reviewed.** The user personally followed the
  [CMD guide](manual-testing-cmd.md) and supplied the full console transcript.
  A tracked text copy is [manual-cmd-2026-11-07.txt](evidence/manual-cmd-2026-11-07.txt).
  Its commands, outputs, file listings and printed exit codes substantiate the
  observations below. This is the user's actual session, distinct from earlier
  agent documentation-command verification in `runtime/cmd-guide-*`.
- **PowerShell: transcript-reviewed for the captured sequence; broader completion
  user-confirmed.** The subsequently supplied
  [PowerShell transcript](evidence/manual-powershell-2026-11-07.txt) records initial
  missing-asset failures, corrected copying/verification/provisioning, malformed
  request rejection, readiness, translation, shutdown and empty stderr. It does
  not independently show every optional guide step; broader walkthrough success
  is the user's confirmation. Do not infer unprinted outputs or timings.
- **Prior technical evidence:** existing source/frozen/offline/native/performance
  reports listed in the acceptance matrix below. Those checks are not rerun in
  this evidence-recording session.

Report/acceptance date: **2026-11-07**, repository timezone **Asia/Manila (UTC+08)**.
CMD file listings show **11/07/2026**, approximately **5:12–5:15 PM** for session
files, consistent with the report date. These are file timestamps, not measured
test durations; the console does not independently identify its timezone or
exact start/end times. PowerShell's supplied text has no session date/time;
its retained filename identifies the report/capture date. No manual performance
timings are claimed.

The original pasted attachment has SHA-256
`a986c4b003ab613800fc40565a9ff7369a848ba8fdb0997fea49a5cb36b98b5e`.
The retained UTF-8 text copy normalizes CRLF to LF and adds a final newline.
At the user's request, the personal profile name in the first two CMD prompts
is replaced with `[REDACTED]`; command arguments, responses and diagnostic
display artifacts are unchanged. The current privacy-redacted copy has SHA-256
`f97d65e0667c76a0c3f3785b9fcc4165e50c34cf3622e985d44e2c87f1d30f2b`.
This copy records supplied console evidence; it is not a capture of original
pipe bytes, cryptographic execution attestation or independent observation.

PowerShell attachment SHA-256:
`8b015d646f68e67e884e2a8757b409d72d614694657ef851bf230dc457672d07`.
Its retained UTF-8/LF text copy (same normalization policy) has SHA-256
`0bd63998f5be1c5132209f99e3b1dd78d9d3f8d243384e046f9a1fb9efdbe01c`.
Both original failed steps and successful recovery are preserved verbatim as
supplied, including console paste/render artifacts.

## Host and tested artifact

| Field | Recorded evidence |
|---|---|
| Tester | Repository user, personally performed both walkthroughs |
| CMD host | Console header: `Microsoft Windows [Version 10.0.26300.9818]` |
| Host scope | Existing Windows development machine; Windows 11 build family per prior evidence, not a clean VM |
| Shell | `cmd.exe`; exact shell binary version/options are not printed in this transcript |
| PowerShell context | Activated `.venv` prompt and process-scoped execution-policy/activation commands are visible; exact PowerShell version is not printed. Commands invoke the copied EXE, not Python. This is not a Python-free host claim. |
| CPU/RAM | Not measured in the manual log; earlier diagnostic reports record Intel64 Family 6 Model 158 and approximately 15.9 GiB RAM |
| Other host details | Windows edition, storage/power conditions and manual network controls not recorded |
| Original artifact | `build/diagnostic-20261107-133601/frozen-unicode-all.worker.zip` |
| Original onedir | `dist/diagnostic-20261107-133601/translation-engine-worker/` |
| Executed copy | Extracted whole onedir under the Unicode workspace below, including `_internal` |
| Versions observed | Worker `0.1.0`, protocol 1, Argos `1.11.1`, model `1.9`, SBD `v0.0.1` |
| Runtime provenance | Unmodified Argos commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`; see [runtime identity](../packaging/argos-upstream.json) |
| Rebuild/integration | User confirms existing executable, no rebuild, no Freya integration or system Python installation required |

Actual CMD workspace:
`D:\Documents\GitHub\translation-engine\runtime\CMD Café 中文 30680-2775`.
Its executable was under `app Café 中文\translation-engine-worker\`, assets under
`upstream assets\`, installed model root under `models Café 中文\`, and state
under `state Café 中文\`. Unicode/spaces were therefore present in executable,
model and state paths in the manual session.

### Artifact and external asset identities

| Item | Reviewed bytes | SHA-256 |
|---|---:|---|
| Worker ZIP | 58,072,023 | `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b` |
| Worker EXE | 5,655,172 | `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941` |
| Original `translate-zh_en-1_9.argosmodel` | 74,481,402 | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| Original `zh-hans.onnx` | 616,442 | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

The ZIP digest is printed directly in the transcript. EXE/model/ONNX hash files
are checked against the above exact constants with `findstr`, followed by
failure guards; the walkthrough continues without a STOP. The user also
explicitly confirms all four hash checks passed. Model/ONNX byte counts and
upstream identities come from [reviewed provenance](../models/provenance.json),
not a new measurement of the cleaned-up workspace. Package 1.9 declares Argos
1.9.0; its validated runtime here is Argos 1.11.1. MiniSBD library 0.9.5 uses
the separately pinned Chinese Simplified v0.0.1 ONNX asset.

Both external assets were copied from the existing local `downloads/` originals,
not redownloaded. Their recorded upstream sources are
[Argos](https://argos-net.com/v1/translate-zh_en-1_9.argosmodel) and
[MiniSBD](https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx).
The whole worker ZIP was staged and extracted via relative `tar.exe` inside a
CMD `pushd` directory; no source checkout or installed Python was used to run
the copied executable. This does not certify a clean target environment.

## CMD results from the supplied transcript

| Check | Observed result |
|---|---|
| Artifact/assets | ZIP digest shown, EXE/model/ONNX exact-match commands and guards pass; cached originals copied |
| Provisioning | Unicode model/state paths; printed exit **0**, successful installation diagnostic on stderr |
| Version/capabilities | `--version` prints `0.1.0`; info reports Argos `1.11.1`, protocol 1 and configured zh→en |
| Six-request persistence | Six stdout envelopes in order `i0,h,t1,t2,i1,s`; `find` prints **6**; process exit **0** |
| Lazy readiness | `i0.ready_pairs` empty; health ready true; `i1` includes ready zh→en |
| Repeated translation | Both `t1` and `t2` return `Hello, world!` |
| Interactive session | Health/info/translation/custom translation/shutdown succeed, then printed exit **0** |
| Paragraph/empty | `This is the first paragraph.\nThis is the second paragraph.` and empty string respectively |
| Structured errors | `UNSUPPORTED_LANGUAGE` and `UNKNOWN_COMMAND` with correlated IDs and `retryable:false` |
| Recovery | Subsequent `recovered` health is ready true; shutdown succeeds; deeper-session exit **0** |
| Missing model | Health envelope `ok:true`, readiness false, error `MODEL_MISSING`; shutdown succeeds; process exit **0** |
| Invalid CLI | Missing `--state-dir` prints argparse diagnostic; captured exit **2** |
| Stdout/stderr | Normal worker stderr displays empty; workspace listing confirms all four normal worker stderr files have **0 bytes** |
| Provisioning/invalid CLI streams | Provisioning stdout and invalid-CLI stdout both listed as 0 bytes; expected diagnostics are separate stderr files |
| Cleanup | Exact workspace displayed, `rmdir /s` confirmation `Y`, prompt returns without deletion error; user confirms cleanup |

The transcript contains six smoke, five interactive, six deeper and two
missing-model response envelopes. Interactive input echo is distinct from
worker output; the six-request stdout file is printed separately. The original
pipe/request files were removed with the workspace, so this pasted transcript
does not independently prove their original encoding/BOM properties. Earlier
CMD command verification separately checked ASCII/CRLF/no-BOM inputs.

### Representative actual commands and responses

These commands occur in the retained CMD transcript, with variables resolving
to the paths above. They are documentation excerpts, not commands rerun for
this acceptance update:

```bat
"%EXE%" provision-model --file "%MODELFILE%" --sbd-file "%SBDFILE%" --models-dir "%MODELS%" --state-dir "%STATE%" > "%WORK%\provision.stdout.txt" 2> "%WORK%\provision.stderr.txt"
set "PROVISION_RC=%ERRORLEVEL%"
"%EXE%" --models-dir "%MODELS%" --state-dir "%STATE%" < "%WORK%\smoke.ndjson" > "%WORK%\smoke.stdout.ndjson" 2> "%WORK%\smoke.stderr.txt"
set "SMOKE_RC=%ERRORLEVEL%"
"%EXE%" --models-dir "%MODELS%" --state-dir "%STATE%" 2> "%WORK%\interactive.stderr.txt"
```

Actual custom request and response from the interactive session:

```json
{"protocol_version":1,"id":"translate","command":"translate","source":"zh","target":"en","text":"天哪，它居然起作用了，我该怎么办？"}
{"protocol_version":1,"id":"translate","ok":true,"result":{"source":"zh","target":"en","text":"God, it's working. What do I do?"}}
```

The user reused the completed `translate` ID sequentially; there were no
simultaneously outstanding requests with that ID. Other representative responses:

```json
{"protocol_version":1,"id":"t1","ok":true,"result":{"source":"zh","target":"en","text":"Hello, world!"}}
{"protocol_version":1,"id":"unsupported","ok":false,"error":{"code":"UNSUPPORTED_LANGUAGE","message":"Only configured zh to en translation is supported.","retryable":false}}
{"protocol_version":1,"id":"missing","ok":true,"result":{"alive":true,"ready":false,"ready_pairs":[],"error":{"code":"MODEL_MISSING","message":"Provision the pinned model and zh-hans MiniSBD resource, then restart.","retryable":false}}}
```

## PowerShell result — captured failures and recovery

The user confirms completing the PowerShell guide with the existing diagnostic,
without rebuilding. The additional transcript substantiates this captured path:

1. ZIP/EXE hash-check commands and `--version` succeed. Initially the expected
   `.argosmodel` is absent from the new `upstream assets` directory: two hash
   attempts report `Resolve-Path` failure, and provisioning fails with a missing
   file. The nonzero guard throws; its exact numeric exit value is not printed.
   These are retained setup errors, not a successful first attempt or a new
   SentencePiece/Unicode failure.
2. The user creates a new workspace, copies both original files from local
   `downloads/`, verifies the recorded hashes, and prints
   `Both models verified successfully.` The copied executable reports `0.1.0`
   and provisions successfully. The resulting path includes
   `runtime\manual Café 中文 21e385f557e644e5b0fe4716b4c489e9\models Café 中文\translate-zh_en-1_9`.
3. A JSON object missing protocol/id/command yields `INVALID_REQUEST` with a
   null ID. A proper `health` (`id:"1"`) returns ready true. Two blank/whitespace
   inputs produce `INVALID_JSON`; a subsequent proper translation (`id:"2"`)
   returns `Hello, world!`. The process remains usable throughout request errors.
4. Shutdown (`id:"4"`) is acknowledged, `$LASTEXITCODE` prints **0**, and
   `Get-Content` of the normal worker stderr log displays no content.

The captured worker sequence has six response envelopes: three expected
request-validation errors and three successes (health, translation, shutdown).
It does not show a six-request PowerShell smoke file, PowerShell cleanup,
individual performance timings or all optional guide requests; no such detail
is invented. The PowerShell log also shows an activated development `.venv`.
Running the copied frozen EXE does not require that activation, but this log
cannot establish a Python-free/clean environment. No execution policy or host
environment is modified by this evidence-recording session.

The complete CMD manual session independently satisfies the local walkthrough
criterion; PowerShell provides additional observed recovery evidence and the
user's broader confirmation, not a second fabricated copy of the CMD results.

## Level A acceptance reconciliation

| Local criterion / tasks | Evidence and assessment |
|---|---|
| Isolated foundation, approved runtime/locks (A1, 4.2) | [Argos migration](argos-migration.md): fresh locked environment, exact source/wheel provenance and Stanza/Torch removal; no current pin changes |
| Actual source and frozen translation (A2, 3.7) | [Unicode repair](unicode-path-validation.md): 60 passing source tests and five frozen scenarios; manual CMD adds actual user translation |
| Exact assets, provisioning/integrity/rollback (3.1, 3.3–3.6, 3.9) | Existing source/frozen integrity and preservation tests plus transcript hash checks and successful local provisioning |
| Local no-network-attempt checks (3.8a) | Prior Python audit-hook evidence before imports/provisioning/warm-up/repeated translation, with fresh isolated state; native/OS isolation remains expressly unproven |
| Protocol/stdout/error recovery/shutdown (A2, 4.5a) | Prior protocol tests plus CMD six-response persistence, interactive custom input, structured errors, recovery and exits/stderr observations |
| Native inventory and diagnostic ZIP (4.3a, 4.4a) | [Native audit](native-dependencies.md): 53 AMD64 PEs, all 180 ZIP files matched, required application runtimes loaded from bundle; Teruten limitation retained |
| Unicode/spaces relocation (4.5a) | Five existing separate/combined path tests plus actual user's Unicode workspace |
| Limited local performance baseline (4.7a) | Existing build/frozen reports and migration/Unicode documentation; no manual timings invented; missing storage/power/cold-cache details remain explicit limits |
| Manual guides (4.9) | CMD and PowerShell guides available, with reviewed command/protocol/hash checks |
| Recorded manual use (4.10) | Complete CMD transcript; supplied PowerShell recovery/translation/shutdown sequence, with broader PowerShell completion user-confirmed and captured limits separately labelled |
| Local sign-off (4.8) | All local criteria satisfied by the combined existing and manual evidence; **Level A complete** |

No genuine Level A requirement remains unmet. Exact manual CPU/shell-version,
timezone and performance metadata not present in the transcripts are limitations,
not newly imposed public-target measurement gates. The partial PowerShell
capture does not withhold the complete CMD-supported local sign-off.

## Limits and remaining Level B gates

- This is a development-host result, not clean Windows 10 22H2 x64 or clean
  Windows 11 x64 acceptance. OS-denied networking was not demonstrated in this
  manual transcript. Local Python instrumentation does not cover every native
  network path.
- Prior external Teruten modules remain an unresolved host isolation finding,
  not a proven application dependency. No security software was modified and
  no clean-isolation result is inferred from successful functionality.
- The provisioning diagnostic displays `CafΘ` and escaped Chinese characters
  in the pasted console text. Actual Unicode paths and successful initialization
  are separately shown; the display artifact is preserved, not hidden or
  interpreted as a new model-loading failure.
- Translation quality remains model-dependent; this custom success does not
  establish general accuracy or lossless Unicode behavior.
- Public gates remain: both clean support rows and OS-denied networking, complete
  target measurements, MiniSBD AGPLv3/source/notices compliance, Visual C++/native
  and other bundled-component redistribution review, final worker-only ZIP,
  manifest/checksums/compliance delivery, consumer documentation, verified release
  candidate and explicit publication approval. No GitHub Release is created.
- Models/ONNX remain external upstream assets with recorded known/unknown terms;
  no model redistribution clearance is claimed or needed for this local sign-off.

This session records/reconciles evidence only: no implementation, dependency,
lock, original asset or executable changes; no rebuild, download or heavy test
rerun. Historical failed/successful diagnostic reports remain intact.
