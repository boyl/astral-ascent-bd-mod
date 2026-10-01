@echo off
setlocal
set "pwshExe="
for %%I in (pwsh.exe) do set "pwshExe=%%~$PATH:I"
if not defined pwshExe (
  echo PowerShell 7 was not found on PATH.
  pause
  exit /b 1
)
"%pwshExe%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0START.ps1"
exit /b %errorlevel%
