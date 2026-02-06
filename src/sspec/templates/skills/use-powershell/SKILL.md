---
name: use-powershell
description: "Use PowerShell to analyze, process, search, and manipulate files on Windows systems. Trigger when operating in a Windows environment and the task involves any of: (1) Searching file contents (grep-like operations), (2) Listing or finding files by name, size, date, or pattern, (3) Reading, comparing, or inspecting file contents, (4) Batch file operations (rename, move, copy, transform), (5) Extracting metadata (size, hash, timestamps, permissions), (6) Processing large files or directories efficiently. This skill provides Windows-specific workflows and non-obvious patterns that complement Claude's general PowerShell knowledge."
---

# PowerShell File Operations (Windows)

## Task Routing

Determine the task type, then follow the corresponding workflow:

**Content search** (find text in files) → `Select-String` workflow
**File search** (find files by name/attribute) → `Get-ChildItem` workflow
**Read & inspect** (view file contents or metadata) → `Get-Content` / `Get-Item` workflow
**Batch transform** (rename, move, copy at scale) → Pipeline workflow
**Compare** (diff two files) → `Compare-Object` workflow

For detailed command patterns and examples, see [references/patterns.md](./references/patterns.md).

## Critical Windows Gotchas

These are the high-impact pitfalls that cause silent failures or wrong results on Windows.

### Encoding

Windows files frequently use non-UTF-8 encodings. Always consider encoding when reading text:

```powershell
# Detect BOM to determine encoding
$bytes = Get-Content -Path "file.txt" -AsByteStream -TotalCount 4
# EF BB BF = UTF-8 BOM, FF FE = UTF-16 LE, FE FF = UTF-16 BE

# Explicit encoding prevents mojibake
$content = Get-Content -Path "file.txt" -Encoding UTF8
```

When writing output, default to UTF-8 with `-Encoding UTF8` to avoid producing UTF-16 files (PowerShell 5.1 default for `Out-File` / `Set-Content`).

### Path Handling

```powershell
# ALWAYS use Join-Path — never string concatenation
$path = Join-Path $folder $filename

# Use -LiteralPath for paths with brackets or wildcards
Get-Content -LiteralPath "log[2025].txt"

# Quote paths with spaces
Get-Item -Path "C:\Program Files\My App\config.json"
```

Windows 260-character path limit causes silent failures. For deep directory trees:

```powershell
# Use \\?\ prefix for long paths
Get-ChildItem -LiteralPath "\\?\C:\Very\Deep\Path" -Recurse
```

### Execution Policy

Scripts may be blocked by default. Check and adjust if needed:

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Line Endings

Windows uses CRLF (`\r\n`). When comparing or processing cross-platform files:

```powershell
$content = (Get-Content "file.txt" -Raw) -replace "`r`n", "`n"
```

## Workflow: Content Search

The primary tool is `Select-String` (Windows equivalent of grep).

```powershell
# Basic: search for pattern in files
Select-String -Path "*.log" -Pattern "error"

# Recursive: search all .cs files under current directory
Get-ChildItem -Recurse -Filter "*.cs" | Select-String -Pattern "class\s+\w+"

# With context lines (like grep -C)
Select-String -Path "app.log" -Pattern "exception" -Context 3,3

# Extract only matched text (not full lines)
Select-String -Path "data.csv" -Pattern "\d{3}-\d{4}" -AllMatches |
    ForEach-Object { $_.Matches.Value }
```

Key flags:
- `-SimpleMatch` — literal string (disable regex)
- `-CaseSensitive` — exact case match
- `-AllMatches` — multiple matches per line
- `-Context N,M` — show N lines before, M after

## Workflow: File Search

```powershell
# By name pattern (fast: -Filter is provider-level)
Get-ChildItem -Path "C:\Projects" -Recurse -Filter "*.config" -File

# By regex on filename
Get-ChildItem -Recurse -File |
    Where-Object { $_.Name -match "^\d{4}-\d{2}-\d{2}" }

# By date range
Get-ChildItem -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }

# By size threshold
Get-ChildItem -Recurse -File |
    Where-Object { $_.Length -gt 1MB }

# Limit recursion depth
Get-ChildItem -Recurse -Depth 3 -Filter "*.json"
```

**Performance rule:** Always prefer `-Filter` over `-Include` or `Where-Object` for name patterns — `-Filter` operates at the filesystem provider level, significantly faster on large trees.

## Workflow: Large File Processing

Avoid loading entire files into memory. Use streaming patterns:

```powershell
# Read first/last N lines without loading full file
Get-Content "huge.log" -TotalCount 100    # first 100 lines
Get-Content "huge.log" -Tail 50           # last 50 lines

# Batch streaming (1000 lines per batch)
Get-Content "huge.log" -ReadCount 1000 | ForEach-Object {
    $batch = $_
    # process batch
}

# .NET StreamReader for maximum efficiency
$reader = [System.IO.File]::OpenText("huge.csv")
try {
    while ($null -ne ($line = $reader.ReadLine())) {
        if ($line -match "target") { Write-Output $line }
    }
} finally { $reader.Close() }
```

## Workflow: File Comparison

```powershell
# Line-by-line diff
Compare-Object (Get-Content "v1.txt") (Get-Content "v2.txt")
# <= means only in v1, => means only in v2

# Hash comparison (binary-safe)
$h1 = (Get-FileHash "file1.bin").Hash
$h2 = (Get-FileHash "file2.bin").Hash
$h1 -eq $h2  # True if identical
```

## Safety Checklist

Before destructive operations (delete, overwrite, bulk rename):

1. **Preview first** — use `-WhatIf` to see what would happen
2. **Count targets** — `(Get-ChildItem -Filter "*.tmp").Count`
3. **Test on subset** — pipe through `Select-Object -First 5` before full run
4. **Use -Confirm** for interactive verification on critical operations
