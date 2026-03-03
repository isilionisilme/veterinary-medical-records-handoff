param(
    [int]$FocusDelayMs = 250
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
"@

$codeProcess = Get-Process -Name Code -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 } |
    Sort-Object StartTime -Descending |
    Select-Object -First 1

if (-not $codeProcess) {
    throw "No se encontro una ventana activa de VS Code."
}

# Restore (if minimized) and focus window.
[Win32]::ShowWindowAsync($codeProcess.MainWindowHandle, 9) | Out-Null
[Win32]::SetForegroundWindow($codeProcess.MainWindowHandle) | Out-Null

Start-Sleep -Milliseconds $FocusDelayMs

# Open command palette and run Developer: Reload Window
[System.Windows.Forms.SendKeys]::SendWait("^+p")
Start-Sleep -Milliseconds 100
[System.Windows.Forms.SendKeys]::SendWait("Developer: Reload Window")
Start-Sleep -Milliseconds 100
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

