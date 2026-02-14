param(
    [switch]$AllowArchiveStale
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-UvInProject {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectDir,
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    Push-Location $ProjectDir
    try {
        Write-Host "`n> uv run $($Args -join ' ')" -ForegroundColor Cyan
        & uv run @Args
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed: uv run $($Args -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

function Assert-PathContains {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string]$Needle
    )

    $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
    if (-not $content.Contains($Needle)) {
        throw "Expected '$Needle' in $FilePath"
    }
}

function Find-SingleMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Glob
    )

    $matches = @(Get-ChildItem -Path $Glob -File)
    if ($matches.Count -eq 0) {
        throw "No match found: $Glob"
    }

    if ($matches.Count -gt 1) {
        $list = $matches | ForEach-Object { $_.FullName }
        throw "Multiple matches for '$Glob':`n$($list -join "`n")"
    }

    return $matches[0]
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$projectDir = Join-Path $repoRoot 'tmp/test-replace-archive-link-project'
$sspecDir = Join-Path $projectDir '.sspec'

if (-not (Test-Path $projectDir)) {
    New-Item -ItemType Directory -Path $projectDir -Force | Out-Null
}

if (-not (Test-Path $sspecDir)) {
    Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'project', 'init')
}

$suffix = (Get-Date -Format 'yyMMddHHmmss')
$rand = ([Guid]::NewGuid().ToString('N')).Substring(0, 6)

$requestName = "replace-link-$suffix-$rand"
$askName = "replace_ask_$suffix$rand"

Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'request', 'new', $requestName)
Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'change', 'new', '--from', $requestName)

$requestFile = Find-SingleMatch -Glob (Join-Path $sspecDir "requests/*_${requestName}.md")

$changeDirCandidates = @(Get-ChildItem -Path (Join-Path $sspecDir 'changes') -Directory |
    Where-Object { $_.Name -ne 'archive' -and $_.Name -like "*_${requestName}" })

if ($changeDirCandidates.Count -eq 0) {
    throw "Cannot locate change dir for request '$requestName'"
}

$changeDir = $changeDirCandidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$changeSpec = Join-Path $changeDir.FullName 'spec.md'
$changeHandover = Join-Path $changeDir.FullName 'handover.md'
$changeRefDir = Join-Path $changeDir.FullName 'reference'
$changeRefFile = Join-Path $changeRefDir 'link-check.md'

$askFileName = "$askName.md"
$askPath = Join-Path $sspecDir "asks/$askFileName"

$requestRel = ".sspec/requests/$($requestFile.Name)"
$changeDirRel = ".sspec/changes/$($changeDir.Name)"
$changeSpecRel = "$changeDirRel/spec.md"
$changeHandoverRel = "$changeDirRel/handover.md"
$askRel = ".sspec/asks/$askFileName"
$tmpRel = '.sspec/tmp/link-check.md'

$askContent = @"
---
created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
name: $askName
why: test archive link replacement
---

Ask references:
- $requestRel
- $changeSpecRel
- $changeHandoverRel
- $tmpRel
"@
Set-Content -Path $askPath -Value $askContent -Encoding UTF8

Add-Content -Path $requestFile.FullName -Value @"

## Link Replacement Test
- ask: $askRel
- change-spec: $changeSpecRel
- change-handover: $changeHandoverRel
"@ -Encoding UTF8

Add-Content -Path $changeSpec -Value @"

## Link Replacement Test
- request: $requestRel
- ask: $askRel
- request-again: $requestRel
"@ -Encoding UTF8

Add-Content -Path $changeHandover -Value @"

## Link Replacement Test
- request: $requestRel
- ask: $askRel
"@ -Encoding UTF8

Set-Content -Path $changeRefFile -Value @"
# Link Test

- request: $requestRel
- ask: $askRel
- spec: $changeSpecRel
"@ -Encoding UTF8

$tmpDir = Join-Path $sspecDir 'tmp'
if (-not (Test-Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
}

$tmpFile = Join-Path $tmpDir 'link-check.md'
Set-Content -Path $tmpFile -Value @"
# tmp link holder

- request: $requestRel
- ask: $askRel
- change-spec: $changeSpecRel
"@ -Encoding UTF8

Write-Host 'Initial setup complete. Starting archive process...' -ForegroundColor Yellow
# Pause

Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'request', 'archive', $requestName, '-y')
Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'change', 'archive', $requestName, '--yes')
Invoke-UvInProject -ProjectDir $projectDir -Args @('python', '-m', 'sspec.cli', 'ask', 'archive', $askName, '-y')

$requestArchivedRel = ".sspec/requests/archive/$($requestFile.Name)"
$changeArchivedDirRel = ".sspec/changes/archive/$($changeDir.Name)"
$askArchivedRel = ".sspec/asks/archive/$askFileName"

$checkDirs = @(
    (Join-Path $sspecDir 'requests'),
    (Join-Path $sspecDir 'changes'),
    (Join-Path $sspecDir 'asks'),
    (Join-Path $sspecDir 'tmp')
)

$mdFiles = @()
foreach ($dir in $checkDirs) {
    if (Test-Path $dir) {
        $mdFiles += Get-ChildItem -Path $dir -Filter '*.md' -Recurse -File
    }
}

foreach ($md in $mdFiles) {
    if ($md.FullName -like '*\archive\*') {
        continue
    }

    $content = Get-Content -Path $md.FullName -Raw -Encoding UTF8
    if ($content.Contains($requestRel)) {
        throw "Old request path still exists in: $($md.FullName)"
    }
    if ($content.Contains($changeDirRel)) {
        throw "Old change path still exists in: $($md.FullName)"
    }
    if ($content.Contains($askRel)) {
        throw "Old ask path still exists in: $($md.FullName)"
    }
}

if (-not $AllowArchiveStale) {
    $archiveFiles = $mdFiles | Where-Object { $_.FullName -like '*\archive\*' }
    foreach ($md in $archiveFiles) {
        $content = Get-Content -Path $md.FullName -Raw -Encoding UTF8
        if ($content.Contains($requestRel)) {
            throw "Archive file still contains old request path: $($md.FullName)"
        }
        if ($content.Contains($changeDirRel)) {
            throw "Archive file still contains old change path: $($md.FullName)"
        }
        if ($content.Contains($askRel)) {
            throw "Archive file still contains old ask path: $($md.FullName)"
        }
    }
}

Assert-PathContains -FilePath $tmpFile -Needle $requestArchivedRel
Assert-PathContains -FilePath $tmpFile -Needle $changeArchivedDirRel
Assert-PathContains -FilePath $tmpFile -Needle $askArchivedRel

Write-Host ''
Write-Host 'PASS: archive link replacement smoke test completed.' -ForegroundColor Green
Write-Host "Project: $projectDir" -ForegroundColor DarkGray
Write-Host "Request: $requestArchivedRel" -ForegroundColor DarkGray
Write-Host "Change : $changeArchivedDirRel" -ForegroundColor DarkGray
Write-Host "Ask    : $askArchivedRel" -ForegroundColor DarkGray
if ($AllowArchiveStale) {
    Write-Host 'Mode   : archive stale links are tolerated (AllowArchiveStale)' -ForegroundColor DarkGray
}