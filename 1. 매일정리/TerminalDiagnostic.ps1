# Windows Terminal Loading Diagnostic Script
# 윈도우 터미널 로딩 지연 원인 진단 스크립트

Write-Host "`n=== WINDOWS TERMINAL LOADING DIAGNOSTIC ===" -ForegroundColor Cyan
Write-Host "Started at: $(Get-Date)" -ForegroundColor Gray
Write-Host "==========================================`n" -ForegroundColor Cyan

# 1. PowerShell 프로필 로딩 시간 측정
Write-Host "=== 1. PowerShell Profile Loading Analysis ===" -ForegroundColor Yellow
Write-Host "Checking PowerShell profiles..." -ForegroundColor Gray

$ProfilePaths = @(
    $PROFILE.CurrentUserAllHosts,
    $PROFILE.CurrentUserCurrentHost,
    $PROFILE.AllUsersAllHosts,
    $PROFILE.AllUsersCurrentHost
)

foreach ($ProfilePath in $ProfilePaths) {
    if (Test-Path $ProfilePath) {
        $FileSize = (Get-Item $ProfilePath).Length
        $LineCount = (Get-Content $ProfilePath | Measure-Object -Line).Lines
        Write-Host "Profile found: $ProfilePath" -ForegroundColor Green
        Write-Host "  Size: $FileSize bytes, Lines: $LineCount" -ForegroundColor Gray

        # Check for time-consuming operations
        $Content = Get-Content $ProfilePath -Raw
        if ($Content -match "Import-Module") {
            Write-Host "  ⚠️  Contains Import-Module statements" -ForegroundColor Yellow
        }
        if ($Content -match "Start-Service|Get-Service") {
            Write-Host "  ⚠️  Contains service operations" -ForegroundColor Yellow
        }
        if ($Content -match "Invoke-WebRequest|Invoke-RestMethod") {
            Write-Host "  ⚠️  Contains network requests" -ForegroundColor Yellow
        }
    }
}

# Profile loading time test
Write-Host "`nProfile loading time test:" -ForegroundColor Gray
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
& { . $PROFILE.CurrentUserAllHosts 2>$null } 6>$null
$Stopwatch.Stop()
Write-Host "Profile loading time: $($Stopwatch.ElapsedMilliseconds)ms" -ForegroundColor $(if($Stopwatch.ElapsedMilliseconds -gt 1000) {"Red"} else {"Green"})

# 2. OneDrive 및 클라우드 서비스 확인
Write-Host "`n=== 2. Cloud Services Analysis ===" -ForegroundColor Yellow

# OneDrive check
$OneDriveProcesses = Get-Process | Where-Object {$_.ProcessName -like "*OneDrive*"} -ErrorAction SilentlyContinue
if ($OneDriveProcesses) {
    Write-Host "OneDrive processes found:" -ForegroundColor Yellow
    $OneDriveProcesses | ForEach-Object {
        Write-Host "  $($_.ProcessName) - CPU: $($_.CPU)ms, Memory: $([math]::Round($_.WorkingSet/1MB,2))MB" -ForegroundColor Gray
    }
} else {
    Write-Host "OneDrive processes not found" -ForegroundColor Green
}

# OneDrive folder check
try {
    $OneDrivePath = [Environment]::GetFolderPath("OneDrive")
    if (Test-Path $OneDrivePath) {
        Write-Host "OneDrive folder: $OneDrivePath" -ForegroundColor Gray
        $SyncStatus = Get-ItemProperty -Path "HKCU:\Software\Microsoft\OneDrive" -Name "UserFolder" -ErrorAction SilentlyContinue
        if ($SyncStatus) {
            Write-Host "OneDrive sync is configured" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "OneDrive configuration check failed" -ForegroundColor Red
}

# 3. GPU 드라이버 및 하드웨어 가속 확인
Write-Host "`n=== 3. GPU and Hardware Acceleration ===" -ForegroundColor Yellow

try {
    $GPUs = Get-WmiObject win32_VideoController
    foreach ($GPU in $GPUs) {
        Write-Host "GPU: $($GPU.Name)" -ForegroundColor Gray
        Write-Host "Driver Version: $($GPU.DriverVersion)" -ForegroundColor Gray
        Write-Host "Driver Date: $($GPU.DriverDate)" -ForegroundColor Gray
    }
} catch {
    Write-Host "GPU information retrieval failed" -ForegroundColor Red
}

# Terminal hardware acceleration check
$TerminalSettings = "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\Settings\settings.json"
if (Test-Path $TerminalSettings) {
    $Settings = Get-Content $TerminalSettings | ConvertFrom-Json
    if ($Settings.profiles.defaults.useAcrylic -eq $true) {
        Write-Host "⚠️  Acrylic background effect enabled (may cause performance issues)" -ForegroundColor Yellow
    }
    if ($Settings.profiles.defaults.experimental.rendering.forceFullRepaint -eq $true) {
        Write-Host "⚠️  Force full repaint enabled" -ForegroundColor Yellow
    }
}

# 4. Windows PowerShell 모듈 확인
Write-Host "`n=== 4. PowerShell Modules Analysis ===" -ForegroundColor Yellow

$LoadedModules = Get-Module | Where-Object {$_.ExportedCommands.Count -gt 0}
Write-Host "Currently loaded modules: $($LoadedModules.Count)" -ForegroundColor Gray

foreach ($Module in $LoadedModules) {
    if ($Module.ExportedCommands.Count -gt 50) {
        Write-Host "  Large module: $($Module.Name) - $($Module.ExportedCommands.Count) commands" -ForegroundColor Yellow
    }
}

# Check for auto-loading modules
$AutoLoadModules = Get-Module -ListAvailable | Where-Object {$_.ExportedCommands.Count -gt 100}
if ($AutoLoadModules) {
    Write-Host "Potentially slow auto-loading modules found:" -ForegroundColor Yellow
    $AutoLoadModules | ForEach-Object {
        Write-Host "  $($_.Name) - $($_.ExportedCommands.Count) commands" -ForegroundColor Gray
    }
}

# 5. 시작 프로그램 및 서비스 확인
Write-Host "`n=== 5. Startup Programs and Services ===" -ForegroundColor Yellow

# Check startup programs that might affect terminal
$StartupPrograms = Get-CimInstance Win32_StartupCommand | Where-Object {$_.Location -like "*Windows*" -or $_.Location -like "*Program*"}
if ($StartupPrograms) {
    Write-Host "Startup programs that might affect terminal:" -ForegroundColor Yellow
    $StartupPrograms | ForEach-Object {
        Write-Host "  $($_.Name) - $($_.Location)" -ForegroundColor Gray
    }
}

# 6. Windows 터미널 설정 확인
Write-Host "`n=== 6. Windows Terminal Configuration ===" -ForegroundColor Yellow

if (Test-Path $TerminalSettings) {
    $TerminalConfig = Get-Content $TerminalSettings | ConvertFrom-Json
    Write-Host "Windows Terminal settings file found" -ForegroundColor Green

    # Check for performance-affecting settings
    if ($TerminalConfig.profiles.defaults.font.face -and $TerminalConfig.profiles.defaults.font.face -like "*Cascadia*") {
        Write-Host "✓ Using CaskaydiaCove font (recommended)" -ForegroundColor Green
    }

    if ($TerminalConfig.profiles.defaults.fontSize -and $TerminalConfig.profiles.defaults.fontSize -gt 14) {
        Write-Host "⚠️  Large font size may affect rendering performance" -ForegroundColor Yellow
    }

    if ($TerminalConfig.profiles.defaults.cursorHeight -and $TerminalConfig.profiles.defaults.cursorHeight -ne 100) {
        Write-Host "Cursor height customization detected" -ForegroundColor Gray
    }
} else {
    Write-Host "Windows Terminal settings file not found" -ForegroundColor Red
}

# 7. 권장 조치 사항
Write-Host "`n=== RECOMMENDATIONS ===" -ForegroundColor Cyan
Write-Host "1. Profile optimization:" -ForegroundColor Yellow
Write-Host "   - Remove unnecessary Import-Module statements from profile" -ForegroundColor Gray
Write-Host "   - Move heavy operations to background jobs" -ForegroundColor Gray
Write-Host "   - Use conditional loading for modules" -ForegroundColor Gray

Write-Host "`n2. Terminal settings:" -ForegroundColor Yellow
Write-Host "   - Disable acrylic background if performance is slow" -ForegroundColor Gray
Write-Host "   - Reduce font size if rendering is slow" -ForegroundColor Gray
Write-Host "   - Update GPU drivers" -ForegroundColor Gray

Write-Host "`n3. System optimization:" -ForegroundColor Yellow
Write-Host "   - Temporarily disable OneDrive sync for testing" -ForegroundColor Gray
Write-Host "   - Close unnecessary background applications" -ForegroundColor Gray
Write-Host "   - Run Windows Terminal as administrator for testing" -ForegroundColor Gray

Write-Host "`n=== DIAGNOSTIC COMPLETE ===" -ForegroundColor Green
Write-Host "Completed at: $(Get-Date)" -ForegroundColor Gray

# 추가 확인을 위한 명령어 안내
Write-Host "`n=== ADDITIONAL TESTS YOU CAN RUN ===" -ForegroundColor Magenta
Write-Host "1. Test PowerShell without profile:" -ForegroundColor Gray
Write-Host "   powershell.exe -NoProfile" -ForegroundColor White

Write-Host "`n2. Check module loading times:" -ForegroundColor Gray
Write-Host "   Measure-Command { Import-Module <ModuleName> }" -ForegroundColor White

Write-Host "`n3. Test with minimal PowerShell:" -ForegroundColor Gray
Write-Host "   powershell.exe -Version 2.0 -NoProfile" -ForegroundColor White

Write-Host "`n4. Check Windows Terminal performance:" -ForegroundColor Gray
Write-Host "   Open Terminal Settings > Advanced > Debug Console" -ForegroundColor White