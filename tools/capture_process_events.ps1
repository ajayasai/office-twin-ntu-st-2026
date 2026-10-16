<#
.SYNOPSIS
Capture a bounded, private Windows process lifecycle ETW trace.
.DESCRIPTION
Run this script from an elevated PowerShell. It uses only the in-box logman,
tracerpt and ControlTraceW facilities. It does not install software, change audit
policy, enable an Event Log channel, or save a scheduled data collector.

OutputDirectory must be a NEW directory beneath this repository's ignored runs
directory. Raw ETL/XML can contain process paths and security metadata: do not
publish them. A separate verifier must validate canaries and task coverage before
calling a capture verified. Zero ETW loss counters alone do not prove coverage.

Wait for capture-ready.json before starting the normal, unelevated task worker. Create
stop.request in OutputDirectory after the worker and post-run canaries have
exited. A duration limit ends collection but marks it incomplete. This script
never runs the task itself and stops only its uniquely named, path-checked trace.

RequestRundown asks the existing process provider to capture its state before
readiness and before stopping. A successful API request is not proof that a
rundown was emitted: the canonical XML must contain and validate Event 15.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $OutputDirectory,
    [ValidateRange(5, 900)] [int] $MaxSeconds = 900,
    [switch] $RequestRundown
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$providerName = 'Microsoft-Windows-Kernel-Process'
$providerGuid = '{22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}'
$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$runsRoot = [IO.Path]::Combine($repoRoot, 'runs') + [IO.Path]::DirectorySeparatorChar
$outputPath = [IO.Path]::GetFullPath($(if ([IO.Path]::IsPathRooted($OutputDirectory)) { $OutputDirectory } else { Join-Path (Get-Location).Path $OutputDirectory }))
if (-not $outputPath.StartsWith($runsRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputDirectory must be a fresh directory beneath this repository''s ignored runs directory.'
}
if (Test-Path -LiteralPath $outputPath) { throw 'OutputDirectory already exists; no evidence will be overwritten.' }
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'An elevated Administrator token is required. Run the reviewed script in an Administrator PowerShell; no settings were changed.'
}
$logman = Join-Path $env:SystemRoot 'System32\logman.exe'
$tracerpt = Join-Path $env:SystemRoot 'System32\tracerpt.exe'
$wevtutil = Join-Path $env:SystemRoot 'System32\wevtutil.exe'
foreach ($nativeTool in @($logman, $tracerpt, $wevtutil)) {
    if (-not (Test-Path -LiteralPath $nativeTool -PathType Leaf)) { throw "Missing in-box tool: $nativeTool" }
}
# Refuse a changed ignore policy: these files must not enter the public package.
& git -C $repoRoot check-ignore --quiet -- $outputPath
if ($LASTEXITCODE -ne 0) { throw 'Output directory is not covered by repository ignore rules.' }
New-Item -ItemType Directory -Path $outputPath | Out-Null
$utf8 = New-Object Text.UTF8Encoding($false)
function Write-NewJson([string] $Name, $Value) {
    $target = Join-Path $outputPath $Name
    $temporary = "$target.tmp"
    if ((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $temporary)) { throw "Refusing to overwrite $Name" }
    [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 12) + "`n"), $utf8)
    [IO.File]::Move($temporary, $target)
}
function Invoke-RecordedTool([string] $Name, [string] $Executable, [string[]] $Arguments) {
    $started = [DateTime]::UtcNow.ToString('o')
    $previous = $ErrorActionPreference
    try {
        # Windows PowerShell treats native stderr as ErrorRecord; retain it locally.
        $ErrorActionPreference = 'Continue'
        $lines = @(& $Executable @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        $exitCode = $LASTEXITCODE
    } finally { $ErrorActionPreference = $previous }
    $text = $lines -join "`n"
    [IO.File]::WriteAllText((Join-Path $outputPath "$Name.log"), $text + "`n", $utf8)
    Write-NewJson "$Name.command.json" ([ordered]@{
        executable = [IO.Path]::GetFileName($Executable); arguments = $Arguments
        started_utc = $started; ended_utc = [DateTime]::UtcNow.ToString('o'); exit_code = $exitCode
    })
    return [pscustomobject]@{ ExitCode = $exitCode; Text = $text }
}

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace OfficeTwinEtw {
    [StructLayout(LayoutKind.Sequential)]
    public struct WnodeHeader {
        public uint BufferSize, ProviderId;
        public ulong HistoricalContext;
        public long TimeStamp;
        public Guid Guid;
        public uint ClientContext, Flags;
    }
    [StructLayout(LayoutKind.Sequential)]
    public struct TraceProperties {
        public WnodeHeader Wnode;
        public uint BufferSize, MinimumBuffers, MaximumBuffers, MaximumFileSize;
        public uint LogFileMode, FlushTimer, EnableFlags, AgeLimit;
        public uint NumberOfBuffers, FreeBuffers, EventsLost, BuffersWritten;
        public uint LogBuffersLost, RealTimeBuffersLost;
        public IntPtr LoggerThreadId;
        public uint LogFileNameOffset, LoggerNameOffset;
    }
    public sealed class TraceResult {
        public uint ReturnCode;
        public string Operation, SessionName, LogFileName;
        public ulong SessionHandle;
        public uint EventsLost, LogBuffersLost, RealTimeBuffersLost, BuffersWritten;
        public uint NumberOfBuffers, BufferSizeKiB, LogFileMode;
    }
    public static class Native {
        [DllImport("advapi32.dll", EntryPoint="ControlTraceW", CharSet=CharSet.Unicode)]
        private static extern uint ControlTrace(ulong handle, string name, IntPtr properties, uint code);
        [DllImport("advapi32.dll", EntryPoint="EnableTraceEx2")]
        private static extern uint EnableTraceEx2(ulong handle, ref Guid provider,
            uint controlCode, byte level, ulong matchAnyKeyword, ulong matchAllKeyword,
            uint timeoutMilliseconds, IntPtr parameters);
        public static uint CaptureProcessState(ulong handle) {
            if (handle == 0) return 87; // ERROR_INVALID_PARAMETER, no native call.
            Guid provider = new Guid("22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716");
            // EVENT_CONTROL_CODE_CAPTURE_STATE only. Keep the already enabled
            // process keyword/level; no provider/filter/security-policy change.
            return EnableTraceEx2(handle, ref provider, 2, 4, 0x10, 0, 5000, IntPtr.Zero);
        }
        public static TraceResult Control(string name, uint code) {
            int size = Marshal.SizeOf(typeof(TraceProperties));
            int bytes = size + 4096;
            IntPtr memory = Marshal.AllocHGlobal(bytes);
            try {
                // Explicitly zero the entire allocation, including string buffers.
                Marshal.Copy(new byte[bytes], 0, memory, bytes);
                TraceProperties properties = new TraceProperties();
                properties.Wnode.BufferSize = (uint)bytes;
                properties.LoggerNameOffset = (uint)size;
                properties.LogFileNameOffset = (uint)(size + 2048);
                Marshal.StructureToPtr(properties, memory, false);
                uint result = ControlTrace(0, name, memory, code);
                properties = (TraceProperties)Marshal.PtrToStructure(memory, typeof(TraceProperties));
                TraceResult stats = new TraceResult();
                stats.ReturnCode = result;
                stats.Operation = code == 1 ? "stop_final" : "query_running";
                if (result == 0) {
                    // WNODE_HEADER.HistoricalContext is the session handle on
                    // output, not a handle inferred from a PID or session name.
                    stats.SessionHandle = properties.Wnode.HistoricalContext;
                    if (properties.LoggerNameOffset >= size && properties.LoggerNameOffset < bytes)
                        stats.SessionName = Marshal.PtrToStringUni(IntPtr.Add(memory, (int)properties.LoggerNameOffset));
                    if (properties.LogFileNameOffset >= size && properties.LogFileNameOffset < bytes)
                        stats.LogFileName = Marshal.PtrToStringUni(IntPtr.Add(memory, (int)properties.LogFileNameOffset));
                    stats.EventsLost = properties.EventsLost;
                    stats.LogBuffersLost = properties.LogBuffersLost;
                    stats.RealTimeBuffersLost = properties.RealTimeBuffersLost;
                    stats.BuffersWritten = properties.BuffersWritten;
                    stats.NumberOfBuffers = properties.NumberOfBuffers;
                    stats.BufferSizeKiB = properties.BufferSize;
                    stats.LogFileMode = properties.LogFileMode;
                }
                return stats;
            } finally { Marshal.FreeHGlobal(memory); }
        }
    }
}
'@

$sessionName = 'OfficeTwinProcessEvidence-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$etlPath = Join-Path $outputPath 'process-events.etl'
$xmlPath = Join-Path $outputPath 'process-events.xml'
$summaryPath = Join-Path $outputPath 'tracerpt-summary.txt'
$stopMarker = Join-Path $outputPath 'stop.request'
$startedUtc = [DateTime]::UtcNow.ToString('o')
$clock = [Diagnostics.Stopwatch]::StartNew()
$startedTrace = $false
$creationSucceeded = $false
$stoppedTrace = $false
$readyWritten = $false
$preStop = $null
$finalStats = $null
$captureErrors = New-Object 'System.Collections.Generic.List[string]'
$stopReason = 'startup_failed'
$conversionCode = $null
$etlHash = $null
$xmlHash = $null
$etlBytes = $null
$xmlBytes = $null
$canonicalDecodeCompleted = $false
$maximumLoopGapSeconds = 0.0
$collectionElapsedAtStop = $null
$status = 'failed'
$traceStartedUtc = $null
$traceStoppedUtc = $null
$captureStateRequests = New-Object 'System.Collections.Generic.List[object]'

function Test-OwnedTrace($Stats, [bool] $AllowPrivateDirectory = $false) {
    if ($Stats.ReturnCode -ne 0 -or $Stats.SessionName -ne $sessionName -or [string]::IsNullOrEmpty($Stats.LogFileName)) { return $false }
    $reportedPath = $Stats.LogFileName
    if ($reportedPath.StartsWith('\??\')) { $reportedPath = $reportedPath.Substring(4) }
    try {
        $normalized = [IO.Path]::GetFullPath($reportedPath)
        if ($normalized.Equals($etlPath, [StringComparison]::OrdinalIgnoreCase)) { return $true }
        # logman's output versioning may vary across Windows versions. A failed
        # expected-file check must still allow cleanup of the trace we created
        # inside this previously nonexistent private directory.
        return $AllowPrivateDirectory -and $creationSucceeded -and [IO.Path]::GetDirectoryName($normalized).Equals($outputPath, [StringComparison]::OrdinalIgnoreCase)
    }
    catch { return $false }
}

function Invoke-OwnedCaptureState([string] $Phase) {
    # Query a fresh handle only after verifying this exact session and ETL path.
    # Reusing an unrelated logger handle or creating a new provider is forbidden.
    $before = [OfficeTwinEtw.Native]::Control($sessionName, 2)
    if (-not (Test-OwnedTrace $before) -or $before.SessionHandle -eq 0) {
        throw "Cannot bind capture-state request to the owned session ($Phase)."
    }
    $requestStarted = [DateTime]::UtcNow.ToString('o')
    $requestClock = [Diagnostics.Stopwatch]::StartNew()
    $returnCode = [OfficeTwinEtw.Native]::CaptureProcessState($before.SessionHandle)
    $requestClock.Stop()
    $requestEnded = [DateTime]::UtcNow.ToString('o')
    $withinWallBudget = $requestClock.Elapsed.TotalSeconds -le 5.5
    $after = [OfficeTwinEtw.Native]::Control($sessionName, 2)
    $revalidated = (Test-OwnedTrace $after) -and $after.SessionHandle -eq $before.SessionHandle
    $request = [ordered]@{
        phase = $Phase; provider = $providerName; provider_guid = $providerGuid
        control_code = 2; control_name = 'EVENT_CONTROL_CODE_CAPTURE_STATE'
        level = 4; match_any_keyword = '0x10'; match_all_keyword = '0x0'; timeout_ms = 5000
        session_name = $sessionName; session_handle = $before.SessionHandle
        started_utc = $requestStarted; ended_utc = $requestEnded; elapsed_seconds = $requestClock.Elapsed.TotalSeconds
        return_code = $returnCode; callback_request_succeeded = ($returnCode -eq 0)
        within_wall_time_budget = $withinWallBudget
        session_revalidated_after = $revalidated
        meaning = 'Provider state was requested; emitted ProcessRundown events and ancestry still require independent decode/identity validation.'
    }
    $captureStateRequests.Add($request)
    Write-NewJson "capture-state-$Phase.json" $request
    if ($returnCode -ne 0 -or -not $revalidated -or -not $withinWallBudget) {
        throw "Capture-state request failed or session identity changed ($Phase, return $returnCode)."
    }
}

try {
    $existing = [OfficeTwinEtw.Native]::Control($sessionName, 2)
    # ERROR_WMI_INSTANCE_NOT_FOUND (4201) is the expected missing-session result.
    if ($existing.ReturnCode -ne 4201) { throw "Cannot establish fresh trace name (ControlTrace code $($existing.ReturnCode))." }
    $metadata = Invoke-RecordedTool 'provider-metadata' $wevtutil @('gp', $providerName, '/ge:true', '/gm:false', '/f:xml')
    if ($metadata.ExitCode -ne 0) { throw 'Cannot read provider metadata.' }
    $providers = Invoke-RecordedTool 'provider-query' $logman @('query', 'providers', $providerGuid)
    if ($providers.ExitCode -ne 0) { throw 'Process provider is unavailable.' }
    $start = Invoke-RecordedTool 'trace-start' $logman @('create', 'trace', $sessionName,
        '-p', $providerGuid, '0x10', '4', '-o', $etlPath, '-f', 'bin',
        '-ct', 'perf', '-bs', '64', '-nb', '16', '64', '-ft', '1', '-ets')
    $creationSucceeded = $start.ExitCode -eq 0
    $live = [OfficeTwinEtw.Native]::Control($sessionName, 2)
    if (Test-OwnedTrace $live) { $startedTrace = $true }
    if ($start.ExitCode -ne 0 -or -not $startedTrace) { throw "Trace did not start with the expected identity/path (logman $($start.ExitCode), ControlTrace $($live.ReturnCode))." }
    $traceStartedUtc = [DateTime]::UtcNow.ToString('o')
    $query = Invoke-RecordedTool 'trace-query' $logman @('query', $sessionName, '-ets')
    if ($query.ExitCode -ne 0 -or $query.Text -notmatch [Regex]::Escape($providerGuid)) { throw 'Live session query did not confirm the expected process provider.' }
    if ($RequestRundown) { Invoke-OwnedCaptureState 'before_ready' }
    Write-NewJson 'capture-ready.json' ([ordered]@{
        schema_version = 1; status = 'recording'; session_name = $sessionName
        provider = $providerName; provider_guid = $providerGuid; keyword = '0x10'; level = 4
        ready_utc = [DateTime]::UtcNow.ToString('o'); collector_pid = $PID; elevated = $true
        collector_created_utc = (Get-Process -Id $PID).StartTime.ToUniversalTime().ToString('o')
        trace_started_utc = $traceStartedUtc
        max_seconds = $MaxSeconds; output_directory = $outputPath; etl_path = $etlPath
        script_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
        initial_session_counters = $live
        request_rundown = [bool]$RequestRundown
        capture_state_requests = @($captureStateRequests.ToArray())
        scope = 'Process lifecycle provider only; system-wide raw trace kept private; no task worker launched elevated.'
    })
    $readyWritten = $true
    $stopReason = 'duration_limit'
    Write-Host "Recording $sessionName. Start the unelevated worker now. Create stop.request after it and the final canaries exit."
    $lastLoopTime = $clock.Elapsed.TotalSeconds
    while ($clock.Elapsed.TotalSeconds -lt $MaxSeconds) {
        $loopTime = $clock.Elapsed.TotalSeconds
        $maximumLoopGapSeconds = [Math]::Max($maximumLoopGapSeconds, $loopTime - $lastLoopTime)
        $lastLoopTime = $loopTime
        if ($maximumLoopGapSeconds -gt 5.0) { $stopReason = 'collector_scheduling_gap'; break }
        if (Test-Path -LiteralPath $stopMarker -PathType Leaf) { $stopReason = 'stop_request'; break }
        Start-Sleep -Milliseconds 200
    }
    # A suspend can resume after the while condition is already false. Preserve
    # that late scheduling gap instead of describing the 900s target as a hard
    # guarantee while Windows is asleep.
    $maximumLoopGapSeconds = [Math]::Max($maximumLoopGapSeconds, $clock.Elapsed.TotalSeconds - $lastLoopTime)
    if ($maximumLoopGapSeconds -gt 5.0) { $stopReason = 'collector_scheduling_gap'; $captureErrors.Add('Collector scheduling gap exceeded five seconds; the attempt is incomplete.') }
} catch {
    $captureErrors.Add($_.Exception.Message)
} finally {
    # Query before stopping and keep the final STOP response separate. Only the
    # exact session created here with its expected private ETL path is eligible.
    if ($startedTrace -or $creationSucceeded) {
        try {
            if ($RequestRundown -and $readyWritten) {
                # A request error must not skip finally's exact-session cleanup.
                try { Invoke-OwnedCaptureState 'before_stop' }
                catch { $captureErrors.Add($_.Exception.Message) }
            }
            $preStop = [OfficeTwinEtw.Native]::Control($sessionName, 2)
            if (-not (Test-OwnedTrace $preStop $true)) { throw 'Owned trace identity/path cannot be verified before stop.' }
            $finalStats = [OfficeTwinEtw.Native]::Control($sessionName, 1)
            if ($finalStats.ReturnCode -ne 0) { throw "ControlTrace STOP failed: $($finalStats.ReturnCode)." }
            $stoppedTrace = $true
            $traceStoppedUtc = [DateTime]::UtcNow.ToString('o')
            $collectionElapsedAtStop = $clock.Elapsed.TotalSeconds
            $afterStop = [OfficeTwinEtw.Native]::Control($sessionName, 2)
            if ($afterStop.ReturnCode -ne 4201) { throw "Stopped trace still queryable or confirmation failed: $($afterStop.ReturnCode)." }
        } catch {
            $captureErrors.Add($_.Exception.Message)
            # Last-resort cleanup never supplies a broad session name or stops a
            # session whose output path does not match this new capture folder.
            try {
                $cleanupQuery = [OfficeTwinEtw.Native]::Control($sessionName, 2)
                if (Test-OwnedTrace $cleanupQuery $true) {
                    $cleanup = Invoke-RecordedTool 'trace-stop-fallback' $logman @('stop', $sessionName, '-ets')
                    if ($cleanup.ExitCode -eq 0) { $stoppedTrace = $true; $traceStoppedUtc = [DateTime]::UtcNow.ToString('o'); $collectionElapsedAtStop = $clock.Elapsed.TotalSeconds }
                }
            } catch { $captureErrors.Add('Fallback stop failed: ' + $_.Exception.Message) }
        }
    }
    if ($stoppedTrace -and (Test-Path -LiteralPath $etlPath -PathType Leaf)) {
        try {
            $etlHash = (Get-FileHash -LiteralPath $etlPath -Algorithm SHA256).Hash.ToLowerInvariant()
            $etlBytes = (Get-Item -LiteralPath $etlPath).Length
            $conversion = Invoke-RecordedTool 'trace-convert' $tracerpt @($etlPath, '-o', $xmlPath, '-of', 'XML', '-summary', $summaryPath)
            $conversionCode = $conversion.ExitCode
            if ($conversionCode -ne 0 -or -not (Test-Path -LiteralPath $xmlPath -PathType Leaf)) { throw 'ETL conversion failed; raw ETL retained.' }
            $xmlHash = (Get-FileHash -LiteralPath $xmlPath -Algorithm SHA256).Hash.ToLowerInvariant()
            $xmlBytes = (Get-Item -LiteralPath $xmlPath).Length
            & (Join-Path $PSScriptRoot 'decode_process_events.ps1') -CaptureDirectory $outputPath -ExpectedEtlSha256 $etlHash
            $canonicalDecodeCompleted = $true
        } catch { $captureErrors.Add($_.Exception.Message) }
    } else { $captureErrors.Add('No confirmed stopped trace/ETL is available for conversion.') }
    $finalCountersAvailable = $null -ne $finalStats -and $finalStats.ReturnCode -eq 0
    $zeroLoss = $finalCountersAvailable -and $finalStats.EventsLost -eq 0 -and $finalStats.LogBuffersLost -eq 0 -and $finalStats.RealTimeBuffersLost -eq 0
    if ($readyWritten -and $stoppedTrace -and $stopReason -eq 'stop_request' -and $zeroLoss -and $conversionCode -eq 0 -and $canonicalDecodeCompleted -and $captureErrors.Count -eq 0) { $status = 'captured_pending_verification' }
    elseif ($stoppedTrace -and $conversionCode -eq 0) { $status = 'incomplete' }
    $clock.Stop()
    Write-NewJson 'capture-status.json' ([ordered]@{
        schema_version = 1; status = $status; verified = $false
        finalized = ($stoppedTrace -and $finalCountersAvailable)
        started_utc = $startedUtc; ended_utc = [DateTime]::UtcNow.ToString('o'); duration_seconds = $clock.Elapsed.TotalSeconds
        trace_started_utc = $traceStartedUtc; trace_stopped_utc = $traceStoppedUtc
        requested_max_seconds = $MaxSeconds; collection_elapsed_at_stop_seconds = $collectionElapsedAtStop
        observed_deadline_overrun_seconds = $(if ($null -ne $collectionElapsedAtStop) { [Math]::Max(0.0, $collectionElapsedAtStop - $MaxSeconds) } else { $null })
        maximum_collector_loop_gap_seconds = $maximumLoopGapSeconds
        session_name = $sessionName; provider = $providerName; provider_guid = $providerGuid; keyword = '0x10'
        request_rundown = [bool]$RequestRundown
        capture_state_requests = @($captureStateRequests.ToArray())
        ready_marker_written = $readyWritten; stopped_own_session = $stoppedTrace; stop_reason = $stopReason
        pre_stop_counters = $preStop; final_stop_counters = $finalStats
        final_loss_counters_available = $finalCountersAvailable; zero_reported_etw_loss = $zeroLoss
        loss_counters = $(if ($finalCountersAvailable) { @{ events_lost = $finalStats.EventsLost; log_buffers_lost = $finalStats.LogBuffersLost; real_time_buffers_lost = $finalStats.RealTimeBuffersLost } } else { $null })
        etl = @{ file = 'process-events.etl'; bytes = $etlBytes; sha256 = $etlHash }
        xml = @{ file = 'process-events.xml'; bytes = $xmlBytes; sha256 = $xmlHash }
        conversion_exit_code = $conversionCode; errors = @($captureErrors.ToArray())
        canonical_winapi_decode_completed = $canonicalDecodeCompleted
        required_verification = @('Decoded process-start, stop and rundown semantics', 'Matching before/after canary lifecycle pairs', 'Trace covers the full unelevated worker interval', 'PID plus CreateTime or sequence-number identity, including parent relationships', 'Allowlisted public export; raw ETL/XML remain private')
        limitations = @('ETW loss counters measure reported session loss, not all possible provider or coverage failures.', 'Already-running processes may appear as rundown; rundown is not an observed start.', 'A successful capture-state API request does not prove emitted rundown events or resolve absent/exited parent identities; decoded event evidence is required.', 'Process lifecycle events do not prove input delivery, task correctness or human similarity.', 'The duration limit is checked while scheduled; system suspend or collector stalls can delay stopping. Actual overrun and scheduling gaps are reported.', 'A duration-limit stop, scheduling gap, unknown final loss counters or a conversion error never qualifies as verified evidence.')
    })
}
Write-Host "Capture status: $status. Raw evidence: $outputPath"
if ($status -eq 'captured_pending_verification') { exit 0 }
exit 1
