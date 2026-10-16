<# Decode a finalized private ETL through the Windows Event Log API.
   Original ETL/tracerpt XML are retained. No timestamps are corrected by hand.
   This script can run unelevated; its output is still private process data. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $CaptureDirectory,
    [string] $ExpectedEtlSha256
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repository = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$privateRoot = [IO.Path]::Combine($repository, 'runs') + [IO.Path]::DirectorySeparatorChar
$capture = [IO.Path]::GetFullPath($CaptureDirectory)
if (-not $capture.StartsWith($privateRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Decode only private captures beneath runs/.' }
$etl = Join-Path $capture 'process-events.etl'
$xml = Join-Path $capture 'process-events-winapi.xml'
$partial = "$xml.partial"
$metadata = Join-Path $capture 'winapi-decode-status.json'
foreach ($target in @($xml, $partial, $metadata, "$metadata.tmp")) {
    if (Test-Path -LiteralPath $target) { throw 'Canonical decode output already exists; no evidence will be overwritten.' }
}
if ([string]::IsNullOrWhiteSpace($ExpectedEtlSha256)) {
    $captureStatus = Get-Content -LiteralPath (Join-Path $capture 'capture-status.json') -Raw | ConvertFrom-Json
    if (-not $captureStatus.finalized -or -not $captureStatus.stopped_own_session) { throw 'Retrospective decoding requires a finalized, stopped capture.' }
    $ExpectedEtlSha256 = $captureStatus.etl.sha256
}
$beforeHash = (Get-FileHash -LiteralPath $etl -Algorithm SHA256).Hash.ToLowerInvariant()
if ($beforeHash -ne $ExpectedEtlSha256.ToLowerInvariant()) { throw 'ETL hash differs from the finalized capture.' }
$provider = [Guid]'22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716'
$utf8 = New-Object Text.UTF8Encoding($false)
$stream = New-Object IO.FileStream($partial, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
$writer = New-Object IO.StreamWriter($stream, $utf8)
$count = 0
$started = [DateTime]::UtcNow.ToString('o')
try {
    $writer.WriteLine('<Events>')
    Get-WinEvent -Path $etl -Oldest -ErrorAction Stop | ForEach-Object {
        $record = $_
        try {
            if ($null -ne $record.ProviderId -and $record.ProviderId -eq $provider) {
                # ToXml supplies native UTC SystemTime and named provider data.
                # Do not rewrite, offset, synthesize or infer event timestamps.
                $writer.WriteLine($record.ToXml())
                $count++
            }
        } finally { $record.Dispose() }
    }
    $writer.WriteLine('</Events>')
} finally { $writer.Dispose(); $stream.Dispose() }
$afterHash = (Get-FileHash -LiteralPath $etl -Algorithm SHA256).Hash.ToLowerInvariant()
if ($beforeHash -ne $afterHash) { throw 'ETL changed while decoding; partial XML retained as unverified.' }
if ($count -eq 0) { throw 'No process-provider events decoded; partial XML retained as unverified.' }
[IO.File]::Move($partial, $xml)
$result = [ordered]@{
    schema_version = 1; status = 'decoded'; decoder = 'Get-WinEvent.ToXml'
    source_etl_sha256 = $afterHash
    xml_sha256 = (Get-FileHash -LiteralPath $xml -Algorithm SHA256).Hash.ToLowerInvariant()
    decoded_event_count = $count; provider_guid = $provider.ToString('B')
    started_utc = $started; ended_utc = [DateTime]::UtcNow.ToString('o')
    decoder_script_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    xml_file = 'process-events-winapi.xml'; xml_bytes = (Get-Item -LiteralPath $xml).Length
    errors = @()
}
[IO.File]::WriteAllText("$metadata.tmp", (($result | ConvertTo-Json -Depth 6) + "`n"), $utf8)
[IO.File]::Move("$metadata.tmp", $metadata)
Write-Host "Canonical Windows API decode complete: $count process-provider records."
