param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PublishArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-UvToken {
    param(
        [string[]]$Hosts
    )

    foreach ($serviceHost in $Hosts) {
        try {
            $candidate = uv auth token $serviceHost 2>$null
            if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($candidate)) {
                return $candidate.Trim()
            }
        }
        catch {
            # Try next host.
        }
    }

    return $null
}

$token = Get-UvToken -Hosts @("upload.pypi.org", "pypi.org")
if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Error "No PyPI token found in uv auth store. Run: uv auth login upload.pypi.org --token <pypi-token>"
    exit 1
}

$hadPrevious = $false
$previous = [Environment]::GetEnvironmentVariable("UV_PUBLISH_TOKEN", "Process")
if ($null -ne $previous) {
    $hadPrevious = $true
}

try {
    $env:UV_PUBLISH_TOKEN = $token
    uv publish @PublishArgs
    exit $LASTEXITCODE
}
finally {
    if ($hadPrevious) {
        $env:UV_PUBLISH_TOKEN = $previous
    }
    else {
        Remove-Item Env:UV_PUBLISH_TOKEN -ErrorAction SilentlyContinue
    }
}
