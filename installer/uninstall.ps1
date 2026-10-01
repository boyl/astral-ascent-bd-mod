#Requires -Version 7.0
param([switch]$NoPause,[switch]$Elevated)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'installer-core.ps1')
$statePath=Join-Path $env:LOCALAPPDATA 'AstralAscentBD/install.json'
$code=0
try {
 if(Get-Process -Name 'Astral Ascent' -ErrorAction SilentlyContinue){throw 'Close Astral Ascent first. / 请先退出星界战士。'}
 if(-not (Test-Path -LiteralPath $statePath)){throw 'No installation record found. / 未找到本 Mod 的安装记录。'}
 $state=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json -AsHashtable
 $targets=@(foreach($item in $state.files.GetEnumerator()){
  $path=Resolve-InstallFile $state.gameDirectory $item.Key
  if(Test-Path -LiteralPath $path){if((Get-InstallHash $path).ToLowerInvariant() -ne $item.Value){throw "已安装文件被修改，停止删除：$($item.Key)"};$path}
 })
 # 先检查所有目标权限，再按安装清单移除；不递归删除游戏目录。
 try {foreach($path in $targets){$s=[IO.File]::Open($path,'Open','Write','ReadWrite');$s.Dispose()}}
 catch [UnauthorizedAccessException] {
  if($Elevated){throw}
  $pwsh=(Get-Command pwsh.exe -CommandType Application | Select-Object -First 1).Source
  $args='-NoLogo -NoProfile -ExecutionPolicy Bypass -File "{0}" -NoPause -Elevated' -f $PSCommandPath
  $p=Start-Process -FilePath $pwsh -ArgumentList $args -Verb RunAs -WindowStyle Hidden -Wait -PassThru
  if($p.ExitCode -ne 0){throw 'Elevated uninstall failed. / 提权卸载未成功。'}
  $targets=@()
 }
 foreach($path in $targets){Remove-Item -LiteralPath $path -Force}
 if(Test-Path -LiteralPath (Join-Path $state.gameDirectory 'version.dll')){throw 'The loader has not been removed. / 自动加载入口尚未移除。'}
 if(Test-Path -LiteralPath $statePath){Remove-Item -LiteralPath $statePath -Force}
 Write-Host 'Uninstalled. Original saves and user settings are retained. / 自动加载已卸载。原版存档与用户 BD 配置保留。' -ForegroundColor Green
} catch {Write-Host $_ -ForegroundColor Red;$code=1}
if(-not $NoPause){[void](Read-Host 'Press Enter to close / 按 Enter 关闭')}
exit $code
