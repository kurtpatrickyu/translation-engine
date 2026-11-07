# Troubleshooting

## Startup and DLL loading

Keep the whole extracted onedir, including `_internal`. A Python DLL loader error
can mean a missing dependency even when `python312.dll` exists. Install, update
or repair the official [VC++ v14 x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe),
complete any requested restart, then retry. Keep compatible newer runtimes;
14.50.35719.0 was locally tested, not established as the minimum. Do not copy DLLs
from System32 or unrelated Python installations.

```bat
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /reg:64
"%EXE%" --version
```

Use the `EXE` path set in [README](../README.md). Registration is only a hint;
successful loading is the check. Record original loader errors and exit codes.
Failures before Python starts may produce no NDJSON response. If repair fails,
retain OS build, architecture, runtime version and actual DLL origins for review.

## Provisioning and model readiness

Compare original asset hashes to README and `models/provenance.json`. Use
`provision-model` with both local `--file` and `--sbd-file` paths, a dedicated
`--models-dir` and separate writable `--state-dir`. No request can download or
install models. Missing, corrupt or multiple ONNX files fail before downloader
fallback. Archive/hash/path/size failures return nonzero diagnostics on stderr.
Do not edit an installed model or delete retained evidence. Provision a fresh
model directory and restart after correcting resources; existing installations
are never overwritten. Idempotent provisioning revalidates the installed files.

`MODEL_MISSING` means the required installed model was not found;
`MODEL_INCOMPATIBLE` means its identity/resources failed validation.
`BACKEND_UNAVAILABLE` indicates backend initialization failed. Health inspection
can return `ok:true` with `ready:false`; inspect its nested error. Initialization
failure remains cached until process restart. Unicode paths are supported by the
package-local serialized tokenizer; use the current complete worker rather than
patching dependencies globally.

## Requests and translation

Use one strict UTF-8 JSON object per line, with protocol version, ID and command.
Send it to worker stdin; JSON pasted at a CMD prompt is a shell command error.
Only direct `zh` to `en` is supported. See [protocol v1](protocol-v1.md) for
limits, all stable error codes and malformed-frame recovery. Model output can
normalize punctuation, mixed-language text and paragraphs; translation is not
lossless preservation. Retain IDs/error codes and input size when reporting
failures, without publishing private request text.

Drain stdout and stderr separately. A host that stops draining stderr can
deadlock the process. Health/shutdown cannot interrupt inference; the host owns
timeouts and restart. Clean EOF exits zero; broken pipes/fatal configuration
failures exit nonzero. Use README's redirected smoke to inspect exit status,
responses and stderr. Developer diagnostics:

```bat
scripts\python.cmd scripts\check_environment.py
scripts\python.cmd scripts\verify_dependency_locks.py
scripts\test.cmd tests\unit\test_worker.py -q
```
