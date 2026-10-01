@echo off
setlocal
set "pwshExe="
for %%I in (pwsh.exe) do set "pwshExe=%%~$PATH:I"
if not defined pwshExe (
  echo PowerShell 7 was not found on PATH.
  pause
  exit /b 1
)
"%pwshExe%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "rc=%errorlevel%"
if not "%rc%"=="0" pause
exit /b %rc%
