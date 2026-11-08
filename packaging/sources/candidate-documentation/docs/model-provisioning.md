# Explicit model and sentence-boundary provisioning

The original `translate-zh_en-1_9.argosmodel` is unchanged. The installed copy
adds a separately acquired, pinned `minisbd/zh-hans.onnx`. Dependency/model
versions and the Argos backend remain unchanged. No worker request downloads or
installs resources. See [provenance](../models/provenance.json).

Maintainer acquisition is explicit and networked:

```bat
scripts\python.cmd scripts\acquire_assets.py
```

The script uses only the recorded URLs and hashes. It verifies existing files,
rejects changed bytes, and never selects newer versions. Downloaded binaries
remain ignored. Consumers obtain the originals directly from the recorded
upstream providers; this project's releases will distribute the worker only,
not model/ONNX binaries. No production release exists yet. The
[manual usage guide](manual-usage.md) lists upstream URLs, exact hashes, the
existing diagnostic ZIP and executable-only local provisioning/testing.
For Command Prompt without PowerShell, use the [CMD guide](manual-testing-cmd.md).

Provisioning accepts **local files** and works without network access:

```bat
scripts\python.cmd -m translation_engine provision-model --file downloads\translate-zh_en-1_9.argosmodel --sbd-file downloads\zh-hans.onnx --models-dir runtime\local-models --state-dir runtime\local-state
scripts\python.cmd -m translation_engine --models-dir runtime\local-models --state-dir runtime\local-state
```

Provisioning verifies both hashes, safely extracts into a bounded staging
directory, adds the ONNX resource, records installed-file integrity information,
and performs a real offline-configured warm-up before atomic promotion. Failure
preserves existing installations. Installed packages are immutable: provisioning
never overwrites them, so active workers cannot see partially replaced models.
Use a new managed model directory for a replacement and restart the worker.
An idempotent invocation validates an existing installation before returning.

The existing packaged executable exposes the same `provision-model` command; it
does not require a separate system Python. CLI failures return nonzero with
stderr diagnostics. Ordinary stdin/stdout commands cannot provision.

Local source and frozen provisioning pass ASCII and Unicode paths, including
spaces. A package-local adapter reads the verified tokenizer model through
Python and passes serialized bytes to SentencePiece, retaining Argos's lazy
processor and encode/decode behavior. The original native file-opening failure
and traceback are retained. See [Unicode repair evidence](unicode-path-validation.md).
Clean Windows acceptance remains pending.

Missing, corrupt, or multiple ONNX files fail before Argos can fall back to a
download. `--models-dir` overrides `ARGOS_PACKAGES_DIR`; `--state-dir` is required
and must not overlap models. All backend config/cache paths are isolated there.

Run real regressions after explicitly acquiring assets:

```bat
set ENGINE_INTEGRATION=1
scripts\test.cmd
```

Python audit-hook tests block and record connection/DNS/send/process attempts.
They prove the exercised Python paths did not attempt network access; they are
not OS firewall or clean-machine proof. Final Windows acceptance remains pending.

## Redistribution gate

The source project remains MIT. MiniSBD 0.9.5 includes AGPLv3 code. The upstream
[MiniSBD README](https://github.com/LibreTranslate/MiniSBD) identifies its ONNX
models as converted/quantized Stanza tokenizers. Do not assume this gives every
model the same license or that an independent executable removes copyleft
obligations. The [AGPLv3 text](https://www.gnu.org/licenses/agpl-3.0.html) sets
conditions on conveying covered works, including applicable notices/license and
corresponding-source obligations. A combined binary distribution needs an
explicit compliance review and source-delivery plan, including dependency source
versions and build/install material; private local builds can proceed.

The original translation archive's README credits Jörg Tiedemann and Santhosh
Thottingal, *OPUS-MT — Building open translation services for the World*, EAMT
2020, and identifies the original OPUS model as CC-BY 4.0. Preserve attribution
and the known/unknown packaged-model and ONNX terms; do not claim they are
cleared. The current scope does not host models. Future model hosting requires
separate review/clearance. Public worker distribution still requires bundled
code/native compliance and clean Windows evidence; these are not prerequisites
for local usage documentation/testing. `models/provenance.json` retains its
recorded pending status; this guide does not grant distribution rights.
