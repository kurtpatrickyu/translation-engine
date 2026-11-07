# translation-engine

Standalone offline Argos translation worker for direct Chinese (`zh`) to
English (`en`). A persistent process accepts NDJSON requests, reuses its loaded
model, and never downloads resources or falls back to a cloud service. It runs
independently of the consuming application; the host owns process supervision.

Windows 10 x64 build 19045.3803 has passed core smoke testing with limitations.
Windows 11 is **expected compatible, UNTESTED**. Full Windows 10 acceptance and
redistribution clearance remain pending. **No production release is published.**
The prepared stable asset set is `0.1.0`; see [release status and requirements](docs/releasing.md).

## Install and try the Windows worker

These are Windows CMD commands. Use the local candidate only if supplied by the
maintainer; otherwise wait for a published release. When available, open
[GitHub Releases](https://github.com/kurtpatrickyu/translation-engine/releases)
and download the Windows x64 worker ZIP, `SHA256SUMS`, `verify-checksums.ps1`,
manifest/schema, usage guide and corresponding-source/compliance ZIPs together.
Verify against trusted publisher materials; checksums alone do not authenticate
the publisher. From the directory containing those files:

```bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verify-checksums.ps1
```

Stop on verification failure. The ZIP is **not a Windows installer**. Extract the
complete directory, including `_internal` and `release-info`:

```bat
mkdir C:\TranslationEngine
tar.exe -xf translation-engine-worker-win-x64.zip -C C:\TranslationEngine
set "EXE=C:\TranslationEngine\translation-engine-worker\translation-engine-worker.exe"
```

Install the official [Microsoft Visual C++ v14 x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe)
if needed, complete any requested restart, and keep compatible newer versions.
This is an external prerequisite; the worker does not install it. **No system
Python or Node.js is required** for the packaged worker.

```bat
"%EXE%" --version
mkdir C:\WorkerAssets
curl.exe -fL "https://argos-net.com/v1/translate-zh_en-1_9.argosmodel" -o C:\WorkerAssets\translate-zh_en-1_9.argosmodel
curl.exe -fL "https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx" -o C:\WorkerAssets\zh-hans.onnx
certutil -hashfile C:\WorkerAssets\translate-zh_en-1_9.argosmodel SHA256
certutil -hashfile C:\WorkerAssets\zh-hans.onnx SHA256
```

Models are acquired separately from these upstream providers, on a connected
machine if necessary, then transferred for offline use. Compare the **entire**
digests below and stop on any mismatch:

| File | SHA-256 |
| --- | --- |
| translate-zh_en-1_9.argosmodel | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| zh-hans.onnx | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

Provision from local files into separate model and state directories:

```bat
"%EXE%" provision-model --file C:\WorkerAssets\translate-zh_en-1_9.argosmodel --sbd-file C:\WorkerAssets\zh-hans.onnx --models-dir C:\TranslationModels --state-dir C:\TranslationState
```

Stop if provisioning fails. It verifies both assets and warms the model before
making the installation available. Existing installations are immutable; use a
new model directory for replacements and restart the worker. The explicit
`--models-dir` overrides `ARGOS_PACKAGES_DIR`; writable `--state-dir` is required
and must not overlap models or reside inside the packaged application directory.

Create three requests and launch one worker to process them in order:

```bat
> C:\TranslationEngine\requests.ndjson echo {"protocol_version":1,"id":"h","command":"health"}
>> C:\TranslationEngine\requests.ndjson echo {"protocol_version":1,"id":"t","command":"translate","source":"zh","target":"en","text":"\u4f60\u597d\uff0c\u4e16\u754c\uff01"}
>> C:\TranslationEngine\requests.ndjson echo {"protocol_version":1,"id":"s","command":"shutdown"}
"%EXE%" --models-dir C:\TranslationModels --state-dir C:\TranslationState < C:\TranslationEngine\requests.ndjson > C:\TranslationEngine\responses.ndjson 2> C:\TranslationEngine\worker.stderr.txt
echo %ERRORLEVEL%
type C:\TranslationEngine\responses.ndjson
type C:\TranslationEngine\worker.stderr.txt
```

Expect ready health, English translation, a shutdown acknowledgement and exit 0.
JSON belongs on worker stdin, not directly at the CMD prompt. For interactive
use, launch the same command without redirections and enter one JSON line at a
time. See [protocol v1](docs/protocol-v1.md) for response fields and errors.

## Further reading and licensing

- [Development, tests, architecture and builds](docs/development.md)
- [Release procedure, current evidence and unresolved obligations](docs/releasing.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Source availability](SOURCE_AVAILABILITY.md) and [third-party notices](THIRD_PARTY_NOTICES.md)

Project source is [MIT licensed](LICENSE). The bundle includes AGPLv3 MiniSBD
and other separately licensed components. External model terms and attribution
remain recorded in [provenance](models/provenance.json); no models are distributed.
