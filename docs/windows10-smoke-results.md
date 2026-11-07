# Windows 10 rc.1 core smoke acceptance record

Recorded 2026-11-08 for OpenSpec change `001-build-offline-translation-engine`,
tasks 4.5b/4.6. **Core smoke passed; full Windows 10 acceptance remains partial.**
Windows 11 has no supplied clean-VM result. No new execution, build, dependency,
packaging or candidate-byte change was performed to record this evidence.

## Evidence and identity

The user supplied the [unaltered CMD transcript](evidence/windows10-rc1-cmd-2026-11-08.txt)
and identified the environment as a clean Windows 10 x64 VirtualBox VM. The
transcript prints build **19045.3803** (Windows 10 22H2 family). VM type and x64
are user-reported; edition, servicing/update/ESU state, CPU, RAM, storage, VM
allocation, power settings and absence of installed Python/global Argos are not
independently inventoried in the capture. The test date/time is not printed;
the recording date above is not an inferred execution timestamp.

Transcript SHA-256:
`7bf2949e1b9f30e6f3a0d0d082713f4bdfe1312304728c348e3a376c82ebb1ac`.

| Input | Captured SHA-256 |
| --- | --- |
| Candidate `0.1.0-rc.1` worker ZIP | `708add4798814b8e7d2298ad36ae9697368afa639a4ae6ea99e391f4457fb28d` |
| Extracted EXE | `ec06bf07399b9d96d140e2c828772666aa12124b8991a2d622ebca52ced79d7d` |
| Original `translate-zh_en-1_9.argosmodel` | `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d` |
| Original `zh-hans.onnx` | `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e` |

These match the [candidate results](release-candidate-results.md) and
[`release-candidate.json`](../packaging/release-candidate.json). The candidate's
recorded worker source commit is `b064e29517fb793b2fcf0bf309b6fc78f623367d`;
the VM did not independently inspect that commit. The checksum verifier reported
that all candidate checksums and top-level coverage matched. Matching checksums
establish integrity against supplied metadata, not independent publisher identity.

## Captured results and acceptance credit

| Subrequirement | Review result |
| --- | --- |
| Candidate checksum verifier and worker ZIP/EXE identity | Passed. Full onedir extracted under `C:\WorkerAcceptance\translation-engine-worker`. |
| Initial startup without an evidenced x64 VC prerequisite | Failed before Python initialization; original loader diagnostic retained below. Not a readiness pass. |
| Startup after prerequisite remedy | `--version` returned `0.1.0` on the same unchanged EXE (user-confirmed unchanged); no rebuild or replacement is reported. |
| Original external assets | Both `certutil` hashes match the pins above. |
| Explicit local-file provisioning | Reported `Provisioned C:\WorkerAcceptance\models\translate-zh_en-1_9.`; repeated provisioning also succeeded. No provisioning exit code is printed separately. |
| Health/readiness | Correlated protocol-v1 `h` response: `ok:true`, `alive:true`, `ready:true`, ready pair `zh` -> `en`, `error:null`. |
| Translation | Correlated `t` response: `ok:true`, text `Hello, world!` for the escaped Chinese smoke input. |
| Shutdown and exit | Correlated `s` response: `ok:true`, `shutdown:true`; captured worker exit code `0`. |
| Normal stdout/stderr | Only the three expected NDJSON responses are printed; `type smoke.stderr.txt` prints no content. |
| Repetition | Two fully displayed smoke results pass, each with exit `0` and empty normal stderr. An intervening invocation has no separately printed result and receives no additional credit. |

The file-driven smoke demonstrates health, translation and shutdown in one
process, then a successful new process using the existing install. It does not
demonstrate multiple translation requests within a retained process, immediate
per-frame flushing before exit, clean EOF behavior or complete cleanup/native
resource reclamation.

## Prerequisite failure and manual command error

Initial `--version` failed with:

```text
Failed to load Python DLL 'C:\WorkerAcceptance\translation-engine-worker\_internal\python312.dll'.
LoadLibrary: The specified module could not be found.
```

`dir` confirms `python312.dll` was present (6,945,272 bytes). The x64 VC runtime
registry query then reported the key/value missing. The user reports resolving
the runtime prerequisite before the next successful `--version`. This is the
expected missing-prerequisite failure class documented for the post-003 candidate,
not evidence that Python was omitted or that the engine needs a packaging fix.
The generic loader message does not identify the exact unresolved dependency;
installation/repair commands, installer identity, actual installed VC++ version,
post-remedy registry output, initial exit code and DLL load origins were not
captured. Do not substitute the development host's tested runtime version.
See [existing remediation](native-dependencies.md#external-vc-prerequisite-for-change-003).

The later `The filename, directory name, or volume label syntax is incorrect.`
follows JSON entered at a CMD prompt, outside the worker. It is a manual shell
command error, not a worker request failure or a passed malformed-request recovery
test. The tester recreated the request file and the subsequent worker run passed.

## Unproven criteria and task disposition

Local-file provisioning succeeded, but **OS-level network denial was not
demonstrated**. No network controls or attempted-download audit were captured.
Unicode/spaces relocation, missing/corrupt-resource rejection and preservation,
broader corpus/error recovery/flush checks, installed runtime version and native
origins, clean-image inventory and full target performance measurements remain
pending. There is no Windows 11 result.

This supplies partial Windows 10 evidence for 4.5b/4.6, without completing either
task or the OS row. Keep 3.8b (both-OS network denial), 4.7b (target measurements)
and all other unfulfilled public gates open. Overall task completion remains
**38/54 (LOCAL 37/37; PUBLIC 1/17)**. See the
[remaining-test checklist and publication gates](windows-acceptance.md).
