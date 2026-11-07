# Windows PowerShell 5.1; invoke from CMD. Integrity is relative to trusted sums.
$ErrorActionPreference = 'Stop'
try {
    $candidateRoot = $PSScriptRoot
    $expectedNames = @{}
    foreach ($line in [IO.File]::ReadAllLines((Join-Path $candidateRoot 'SHA256SUMS'))) {
        if ($line -notmatch '^([a-f0-9]{64})  ([A-Za-z0-9._-]+)$') { throw 'Invalid SHA256SUMS entry' }
        $expectedHash = $Matches[1]
        $artifactName = $Matches[2]
        if ($artifactName -eq 'SHA256SUMS' -or $expectedNames.ContainsKey($artifactName)) { throw 'Duplicate/self checksum entry' }
        $expectedNames[$artifactName] = $true
        $artifactPath = Join-Path $candidateRoot $artifactName
        $item = Get-Item -LiteralPath $artifactPath
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Unsafe artifact: $artifactName" }
        if ((Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { throw "Hash mismatch: $artifactName" }
    }
    foreach ($required in @('manifest.json', 'manifest.schema.json', 'translation-engine-worker-win-x64.zip', 'translation-engine-compliance.zip', 'translation-engine-corresponding-source.zip', 'WINDOWS-CANDIDATE.md', 'verify-checksums.ps1')) {
        if (-not $expectedNames.ContainsKey($required)) { throw "Missing checksum: $required" }
    }
    foreach ($item in Get-ChildItem -LiteralPath $candidateRoot -Force) {
        if ($item.Name -ne 'SHA256SUMS' -and -not $expectedNames.ContainsKey($item.Name)) { throw "Unexpected candidate file: $($item.Name)" }
    }
    Write-Output 'Integrity verified: all checksums and top-level files match. Publication approval is verified separately.'
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
