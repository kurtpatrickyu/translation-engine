# Manual transcript provenance

## Evidence sources and dates

- **CMD: transcript-reviewed.** The user personally followed the
  then-current CMD procedure and supplied the full console transcript.
  A tracked text copy is [manual-cmd-2026-11-07.txt](manual-cmd-2026-11-07.txt).
  Its commands, outputs, file listings and printed exit codes record the
  observed behavior. This is the user's actual session, distinct from earlier
  agent documentation-command verification in `runtime/cmd-guide-*`.
- **PowerShell: transcript-reviewed for the captured sequence; broader completion
  user-confirmed.** The subsequently supplied
  [PowerShell transcript](manual-powershell-2026-11-07.txt) records initial
  missing-asset failures, corrected copying/verification/provisioning, malformed
  request rejection, readiness, translation, shutdown and empty stderr. It does
  not independently show every optional guide step; broader walkthrough success
  is the user's confirmation. Do not infer unprinted outputs or timings.
- **Prior technical evidence:** source/frozen/offline/native/performance reports
  were not rerun while recording these supplied transcripts.

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

