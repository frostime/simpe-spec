# PowerShell Command Patterns Reference

Detailed patterns organized by task type. Load this file when the task requires patterns beyond what SKILL.md covers.

## Table of Contents

- [Content Reading Patterns](#content-reading-patterns) (L17-48) — Get-Content, Select-String
- [Advanced Search Patterns](#advanced-search-patterns) (L51-86) — Regex, context, multi-file
- [File Discovery Patterns](#file-discovery-patterns) (L89-123) — Get-ChildItem, filtering
- [Metadata & Inspection](#metadata--inspection) (L126-163) — Properties, hashing, comparing
- [Batch Operations](#batch-operations) (L166-198) — Renaming, moving, transforming
- [Output Formatting](#output-formatting) (L201-235) — Tables, custom objects, export
- [Performance Patterns](#performance-patterns) (L238-END) — Optimization, parallelization

---

## Content Reading Patterns

### Partial reads

```powershell
# Specific line range (lines 10–20)
Get-Content "file.txt" | Select-Object -Skip 9 -First 11

# Single line by index (0-based array)
(Get-Content "file.txt")[14]  # line 15

# Read as single string (preserves newlines)
$raw = Get-Content "file.txt" -Raw
```

### Binary reads

```powershell
# PowerShell 7+
$bytes = Get-Content "image.png" -AsByteStream

# PowerShell 5.1
$bytes = Get-Content "image.png" -Encoding Byte
```

### Encoding conversion

```powershell
Get-Content "source.txt" -Encoding UTF8 |
    Set-Content "target.txt" -Encoding ASCII
```

---

## Advanced Search Patterns

### Multi-file with exclusions

```powershell
Get-ChildItem -Recurse -Include "*.log" -Exclude "debug.log" |
    Select-String -Pattern "exception"
```

### Capture group extraction

```powershell
$results = Select-String -Path "config.ini" -Pattern "(\w+)=(.+)"
foreach ($m in $results) {
    $key   = $m.Matches.Groups[1].Value
    $value = $m.Matches.Groups[2].Value
    Write-Host "${key}: ${value}"
}
```

### Match counting

```powershell
# Lines containing pattern
(Select-String -Path "app.log" -Pattern "error").Count

# Total occurrences (multiple per line)
(Select-String -Path "app.log" -Pattern "error" -AllMatches).Matches.Count
```

### Inverted search (lines NOT matching)

```powershell
Select-String -Path "app.log" -Pattern "DEBUG" -NotMatch
```

---

## File Discovery Patterns

### Multiple extensions

```powershell
Get-ChildItem -Recurse -Include "*.txt","*.log","*.csv"
```

### Regex on full path

```powershell
Get-ChildItem -Recurse -File |
    Where-Object { $_.FullName -match "src\\models\\.+\.py$" }
```

### Date range filter

```powershell
$start = Get-Date "2025-01-01"
$end   = Get-Date "2025-01-31"
Get-ChildItem -File |
    Where-Object { $_.LastWriteTime -ge $start -and $_.LastWriteTime -le $end }
```

### Empty files / directories

```powershell
# Zero-byte files
Get-ChildItem -Recurse -File | Where-Object { $_.Length -eq 0 }

# Empty directories
Get-ChildItem -Recurse -Directory |
    Where-Object { (Get-ChildItem $_.FullName -File -Recurse).Count -eq 0 }
```

---

## Metadata & Inspection

### Key properties

```powershell
$f = Get-Item "document.pdf"
$f.Name            # filename
$f.FullName        # absolute path
$f.Length          # bytes
$f.Extension       # .pdf
$f.CreationTime    # created
$f.LastWriteTime   # modified
$f.Attributes      # ReadOnly, Hidden, etc.
```

### Existence checks

```powershell
Test-Path "file.txt"                       # exists?
Test-Path "file.txt" -PathType Leaf        # is file?
Test-Path "folder"   -PathType Container   # is directory?
```

### Hash computation

```powershell
Get-FileHash "release.zip"                           # SHA256 (default)
Get-FileHash "release.zip" -Algorithm MD5             # MD5
Get-ChildItem *.dll | Get-FileHash | Select-Object Hash, Path  # batch
```

### Toggle read-only

```powershell
Set-ItemProperty "file.txt" -Name IsReadOnly -Value $true   # lock
Set-ItemProperty "file.txt" -Name IsReadOnly -Value $false  # unlock
```

---

## Batch Operations

### Bulk rename

```powershell
# Add prefix
Get-ChildItem -Filter "*.jpg" |
    Rename-Item -NewName { "photo_" + $_.Name }

# Regex replace in filename
Get-ChildItem -Filter "*.log" |
    Rename-Item -NewName { $_.Name -replace "old", "new" }
```

### Bulk copy / move

```powershell
# Pipeline is faster than foreach loop
Get-ChildItem -Filter "*.txt" | Copy-Item -Destination "backup\"
Get-ChildItem -Filter "*.tmp" | Move-Item -Destination "archive\"
```

### Conditional processing

```powershell
Get-ChildItem -Recurse -File | Where-Object {
    $_.Length -gt 10MB -and $_.Extension -eq ".log"
} | ForEach-Object {
    Compress-Archive -Path $_.FullName -DestinationPath "$($_.FullName).zip"
    Remove-Item $_.FullName
}
```

---

## Output Formatting

### Table view

```powershell
Get-ChildItem | Format-Table Name, Length, LastWriteTime -AutoSize

# Custom columns
Get-ChildItem -File | Select-Object Name,
    @{Name="SizeKB"; Expression={[math]::Round($_.Length/1KB,2)}},
    LastWriteTime
```

### Sorted output

```powershell
Get-ChildItem -File | Sort-Object Length -Descending      # by size
Get-ChildItem | Sort-Object LastWriteTime -Descending      # by date

# Natural sort for numbered filenames
Get-ChildItem | Sort-Object {
    [regex]::Replace($_.Name, '\d+', { $args[0].Value.PadLeft(20) })
}
```

### Tree-like listing

```powershell
# Quick recursive directory names
Get-ChildItem -Recurse -Directory | ForEach-Object { $_.FullName }

# Or use built-in tree command
tree /F  # includes files
```

---

## Performance Patterns

### Filter early, pipe late

```powershell
# SLOW: filter after enumeration
Get-ChildItem -Recurse | Where-Object { $_.Extension -eq ".log" }

# FAST: provider-level filter
Get-ChildItem -Recurse -Filter "*.log"
```

### Cache repeated lookups

```powershell
# SLOW: Get-Item called every iteration
Get-Content "file.txt" | ForEach-Object { (Get-Item "file.txt").Length }

# FAST: single lookup
$file = Get-Item "file.txt"
Get-Content "file.txt" | ForEach-Object { $file.Length }
```

### Limit recursion scope

```powershell
# Scan only 2 levels deep instead of full tree
Get-ChildItem -Recurse -Depth 2 -Filter "*.json" -File
```

### Parallel processing (PowerShell 7+)

```powershell
Get-ChildItem -Recurse -Filter "*.log" | ForEach-Object -Parallel {
    Select-String -Path $_.FullName -Pattern "error"
} -ThrottleLimit 4
```
