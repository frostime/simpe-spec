param(
    [switch]$RunNow
)

Set-StrictMode -Version Latest

$cwd = Get-Location
$tmpRoot = Join-Path $cwd "tmp"
if (-not (Test-Path $tmpRoot)) {
    Write-Error "tmp directory not found at $tmpRoot. Run this script from the repository root."
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$shortGuid = [guid]::NewGuid().ToString().Substring(0,8)
$dirName = "sspec_test_$timestamp-$shortGuid"
$dest = Join-Path $tmpRoot $dirName
New-Item -ItemType Directory -Path $dest | Out-Null
Write-Host "Created temporary directory: $dest"

Push-Location $dest

function Run-Command($cmd) {
    Write-Host "---- Running: $cmd ----"
    try {
        & $cmd 2>&1 | ForEach-Object { Write-Host $_ }
    } catch {
        Write-Warning "Command failed: $cmd -> $_"
    }
}

Write-Host "==> Initializing project (uv run sspec project init)"
# Run-Command "uv run sspec project init"
uv run sspec project init

function Show-SkillDir($name) {
    $path = Join-Path (Get-Location) $name
    if (-not (Test-Path $path)) {
        return
    }
    # $item = Get-Item $path
    # if ($item.LinkType -eq "SymbolicLink") {
    #     Write-Host "$name is a symbolic link pointing to: $($item.Target)"
    # }
    $skillsPath = Join-Path $path "skills"
    # if (-not (Test-Path $skillsPath)) {
    #     Write-Host "No 'skills' directory under $name"
    #     return
    # }
    $skillsItem = Get-Item $skillsPath
    # if ($skillsItem.LinkType -eq "SymbolicLink") {
    #     Write-Host "$name\skills is a symbolic link pointing to: $($skillsItem.Target)"
    # }
    # Write-Host "Contents of $name\skills:"
    ls $skillsPath
}

$checkDirs = @('.sspec','copilot','.claude','.agent')
foreach ($d in $checkDirs) { Show-SkillDir $d }

Write-Host "==> Updating project (uv run sspec project update)"
# Run-Command "uv run sspec project update"
uv run sspec project update

Write-Host "==> Listing skill directories again"
foreach ($d in $checkDirs) { Show-SkillDir $d }

Pop-Location

Write-Host "Script completed. Temporary directory: $dest"

if ($RunNow) { exit 0 }
