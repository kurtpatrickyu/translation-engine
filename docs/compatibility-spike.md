# Pinned Argos/model compatibility experiment

This page preserves the original 1.11.0 compatibility evidence. The subsequently
approved 1.11.1 source-artifact migration and actual-worker/frozen results are
recorded in [argos-migration.md](argos-migration.md); model/SBD hashes are unchanged.

Status: **host-local compatibility passed with MiniSBD**, 2026-11-06. The legacy
Stanza failures below are preserved as root-cause evidence. This is a
development-host experiment, not clean-machine or OS firewall acceptance.

## Inputs

- CPython 3.12.10 x64 on Windows 11 build 26300 (development host).
- Unchanged Argos 1.11.0, CTranslate2 4.8.5, SentencePiece 0.2.1,
  Stanza 1.10.1; full resolved graph in `requirements-dev.lock`.
- [Captured upstream index](https://raw.githubusercontent.com/argosopentech/argospm-index/ff90de60728f7c1338ff6b75974e4c89b2442d22/index.json),
  commit `ff90de60728f7c1338ff6b75974e4c89b2442d22`.
- [Exact upstream model](https://argos-net.com/v1/translate-zh_en-1_9.argosmodel):
  `translate-zh_en-1_9.argosmodel`, package 1.9, declared Argos 1.9.0,
  74,481,402 bytes.
- Observed SHA-256:
  `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d`.
  The experiment now refuses differing bytes. This is a captured evaluation
  identity, not independent authentication or completed redistribution review.

The original archive is unchanged and remains in ignored `downloads/`.
It contains SentencePiece data, a CTranslate2 model, and Stanza resources with
`zh-hans/tokenize/gsdsimp.pt`. There is no packaged MiniSBD ONNX or SpaCy model.
Stanza `resources.json` uses legacy `default_processors` metadata and lacks the
`packages` mapping expected by the installed Stanza default path.

## Reproduction

Run from the repository root in CMD after the existing setup. Each invocation
extracts the pinned archive into fresh temporary ignored `runtime/` state, sets
isolated Argos/data/config/cache/Stanza/Hugging Face/Torch paths before imports,
and blocks audited Python socket connection/DNS/send and process-launch events.

```bat
scripts\python.cmd scripts\spike_argos.py --model downloads\translate-zh_en-1_9.argosmodel --sbd default --report runtime\spike-default.json
scripts\python.cmd scripts\spike_argos.py --model downloads\translate-zh_en-1_9.argosmodel --sbd stanza-offline --report runtime\spike-stanza-offline.json
scripts\python.cmd scripts\spike_argos.py --model downloads\translate-zh_en-1_9.argosmodel --sbd stanza-local-tokenizer --report runtime\spike-stanza-local-tokenizer.json
```

All three currently exit 1, as recorded below. These are experiments exposing
the blocker, not a production adapter or provisioning command.

| Experiment | Observed result |
|---|---|
| Unmodified Argos default selection | Selects the bundled Stanza path and attempts DNS for `raw.githubusercontent.com`; the audit hook blocks it before connection. This fails strict no-network-attempt requirements. |
| Explicit Stanza `download_method=None`, tokenizer defaults | No audited network attempt; fails in Stanza processor selection with `KeyError: 'packages'` against bundled legacy metadata. |
| Explicit no-download Stanza, `package=None`, `processors={"tokenize":"gsdsimp","mwt":[]}` | Uses the installed API's explicit processor selection, avoiding optional MWT discovery without modifying metadata or pretokenizing text. Reaches the bundled checkpoint loader but fails with `KeyError: 'feat_dropout'` in Stanza's tokenizer trainer. No audited network attempt. |

The third result establishes that bypassing only metadata selection does not
make the bundled checkpoint load with the pinned Stanza version. No checkpoint
arguments, dependency code, package metadata, or model weights were patched.

## Historical Stanza blocker

At this historical stage no translation completed. Repeated inference, native translator reuse,
segmentation quality, long-input quality, and end-to-end runtime/model
compatibility remain unverified. Empty caches and Python audit hooks make
implicit Python downloads observable, but do not establish OS firewall controls
or rule out every possible native network path. The host is not a clean VM.
Neither Windows acceptance row is passed.

The reviewed design requires a pause before replacing SBD assets, transforming
the model, or changing dependency/model pins. A compatibility amendment must
choose and validate an approach: retain the current pins with a reviewed local
legacy-checkpoint compatibility strategy, provision an independently pinned
compatible SBD asset, or explicitly revise the runtime/model combination.
At that stage each option needed repeated real translation, representative Chinese sentence
and paragraph/Unicode/long-input quality checks, offline resource validation,
and licensing/provenance review. The subsequent MiniSBD results below supersede
this historical compatibility blocker; licensing and clean OS gates remain.

The subsequent targeted amendment authorized evaluating a separate MiniSBD asset
without changing the versioned protocol or architecture. Clean OS checks remained
separate from local compatibility validation.

## Successful MiniSBD experiment and selected strategy

The installed Argos 1.11.0 supports `ARGOS_CHUNK_TYPE=MINISBD` and package-local
`minisbd/*.onnx` lookup. Explicitly place exactly one pinned `zh-hans.onnx` there
before importing/initializing the backend; preserve original archive bytes.
No dependency internals are patched. Legacy Stanza is not used for inference.

- Upstream resource: [MiniSBD v0.0.1 zh-hans.onnx](https://github.com/LibreTranslate/MiniSBD/releases/download/v0.0.1/zh-hans.onnx).
- Release ID 273975424; asset ID 336220945; 616,442 bytes.
- SHA-256: `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e`,
  matching GitHub's asset digest and locally computed bytes.
- Release tag target: `27772c68437a368c23a26dbf4fbc2fe1c7df82a2`.
- Inspected upstream source: `bc63bb09ee61050433323f255c07a3497b93b9c8`,
  identifying library 0.9.5 and Stanza-to-ONNX conversion/quantization. This
  source-inspection revision is not claimed to prove the exact asset build chain.
- All original runtime/translation-model versions and archive digest are unchanged.

```bat
scripts\python.cmd scripts\spike_argos.py --model downloads\translate-zh_en-1_9.argosmodel --sbd minisbd --sbd-model downloads\zh-hans.onnx --report runtime\spike-minisbd.json
```

This exits zero. Nine actual requests cover single/multiple sentences, product
description, Chinese punctuation, mixed Chinese/English, Unicode, paragraphs,
40 repeated sentences, and a repeated request in the same process. Translator,
sentence splitter, and ONNX detector identities remain unchanged. With isolated
fresh cache/config/data/model paths, Python audit hooks recorded **zero** network
or subprocess attempts. No inference download occurred on the exercised paths.

| Input/observation | Actual result |
|---|---|
| `你好，世界！` | `Hello, world!`, including the repeated request |
| Two Chinese full-stop sentences | Two SBD segments; nonempty English translation |
| Stainless steel cup, 500 ml, travel/daily use | Two segments; English preserves cup material, 500 ml, and intended use |
| Two paragraphs | Output retains the paragraph newline |
| Forty full-stop sentences | Forty segments and repeated English translation |
| Exclamation/question punctuation | MiniSBD groups the short example into one segment, while translation still contains English sentence punctuation |
| Mixed English `fast charging` | Model mistranslates it as `past charge`; known quality limit |
| Mixed Unicode/emoji example | SBD preserves the input segment, but the translation model drops part of the content; Unicode transport correctness is not a promise of lossless model output |

This distinguishes the prior failures as legacy SBD metadata/checkpoint
compatibility issues rather than a proven core CTranslate2/SentencePiece model
failure. No direct-CTranslate2 bypass was necessary. MiniSBD adds a 616 KB ONNX
asset and uses already locked ONNX Runtime, avoiding a bespoke Stanza adapter;
mandatory Argos dependencies still remain in the package graph, so no reduced
executable footprint is claimed without measurement.

## Regression and production-path checks

The actual worker uses the same supported MiniSBD path. Tests verify real local
CLI provisioning with warm-up before promotion, repeated JSON requests,
representative English output, paragraph/empty input handling, model/detector
reuse, and response-only stdout with no source/translation logs. Fresh-state
worker subprocesses run Python network-attempt instrumentation. Missing,
corrupt, and ambiguous ONNX installations fail without downloads. Failed
provisioning validation never promotes a partial installation.

## Remaining gates

Python instrumentation does not prove OS firewall isolation or every native
network path. Both clean Windows 10 22H2 x64 and Windows 11 x64 acceptance rows
remain pending and must use the same eventual worker/model/SBD hashes. Local
worker implementation and packaging can continue without those VMs.

MiniSBD code is AGPLv3, and upstream describes Stanza-derived ONNX assets. Review
covered combined-distribution source/notices obligations and model-specific
terms before publishing. The original translation README identifies the OPUS
model as CC-BY 4.0 and provides attribution. See
[provenance and redistribution notes](../README.md). No license
clearance, production release, perfect translation quality, or clean-machine
compatibility is implied by the local experiment.
