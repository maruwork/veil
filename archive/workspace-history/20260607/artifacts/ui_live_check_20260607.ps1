param(
  [Parameter(Mandatory = $true)]
  [ValidateSet('initial', 'review', 'manual-switch', 'bulk-confirm', 'close')]
  [string]$Step
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win32Window {
  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")]
  public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
"@

$edgePath = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$url = 'http://127.0.0.1:8080'
$outDir = 'C:\Users\f_tan\project\veil\workspace'

function Activate-VeilWindow {
  for ($i = 0; $i -lt 30; $i++) {
    $proc = Get-Process msedge -ErrorAction SilentlyContinue |
      Where-Object { $_.MainWindowTitle -eq 'VEIL' -and $_.MainWindowHandle -ne 0 } |
      Select-Object -First 1
    if ($null -ne $proc) {
      [Win32Window]::ShowWindowAsync($proc.MainWindowHandle, 5) | Out-Null
      [Win32Window]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
      Start-Sleep -Milliseconds 300
      return $true
    }
    Start-Sleep -Seconds 1
  }
  return $false
}

function Save-Screenshot([string]$path) {
  $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
  $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $graphics.Dispose()
  $bitmap.Dispose()
}

function Send-StepKeys([string]$keys, [int]$sleepMs = 400) {
  [System.Windows.Forms.SendKeys]::SendWait($keys)
  Start-Sleep -Milliseconds $sleepMs
}

function Send-TabTimes([int]$count) {
  for ($i = 0; $i -lt $count; $i++) {
    Send-StepKeys('{TAB}', 250)
  }
}

if ($Step -eq 'initial') {
  Start-Process -FilePath $edgePath -ArgumentList "--app=$url"
  Start-Sleep -Seconds 5
  if (-not (Activate-VeilWindow)) { throw 'VEIL window not found' }
  Save-Screenshot (Join-Path $outDir 'ui_live_initial_20260607.png')
  exit 0
}

if (-not (Activate-VeilWindow)) { throw 'VEIL window not found' }

switch ($Step) {
  'review' {
    Send-TabTimes 9
    Send-StepKeys('~', 800)
    Save-Screenshot (Join-Path $outDir 'ui_live_review_20260607.png')
  }
  'manual-switch' {
    Send-StepKeys('+{TAB}', 300)
    Send-StepKeys('^a', 200)
    Send-StepKeys('manual-switch', 700)
    Save-Screenshot (Join-Path $outDir 'ui_live_manual_switch_20260607.png')
  }
  'bulk-confirm' {
    Send-StepKeys('^r', 1800)
    Send-TabTimes 10
    Send-StepKeys('~', 800)
    Save-Screenshot (Join-Path $outDir 'ui_live_bulk_confirm_20260607.png')
    Send-StepKeys('{ESC}', 300)
  }
  'close' {
    Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force
  }
}
