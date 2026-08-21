param(
    [string]$BaseUrl = "http://localhost/api",
    [string]$Username = $(if ($env:ADMIN_BOOTSTRAP_USER) { $env:ADMIN_BOOTSTRAP_USER } else { "admin" }),
    [string]$Password = $(if ($env:ADMIN_BOOTSTRAP_PASSWORD) { $env:ADMIN_BOOTSTRAP_PASSWORD } else { "change-me-now" })
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

python "$repoRoot/scripts/gis/xianlin_pipeline.py" validate | Out-Null
if ($LASTEXITCODE -ne 0) { throw "GIS validation failed; import stopped." }

$summary = [ordered]@{ created = 0; updated = 0; failed = 0 }
$files = @("campus", "surfaces", "buildings", "pois", "roads", "entrances")
& curl.exe --silent --show-error --fail-with-body -u "$Username`:$Password" `
    -X POST "$BaseUrl/admin/imports/dataset-mode/real/refresh" | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Unable to prepare authoritative real dataset refresh" }

foreach ($layer in $files) {
    $path = "$repoRoot/data/real/xianlin/$layer.geojson"
    $response = & curl.exe --silent --show-error --fail-with-body `
        -u "$Username`:$Password" -F "file=@$path" "$BaseUrl/admin/imports/geojson"
    if ($LASTEXITCODE -ne 0) { throw "Import request failed for $layer" }
    $result = $response | ConvertFrom-Json
    if ($result.failed -gt 0) { throw "Import validation failed for ${layer}: $($result.errors | ConvertTo-Json -Compress)" }
    $summary.created += $result.created
    $summary.updated += $result.updated
    $summary.failed += $result.failed
    Write-Output "$layer`: created=$($result.created), updated=$($result.updated)"
}

Write-Output "Real Xianlin GIS import complete: $($summary | ConvertTo-Json -Compress)"
