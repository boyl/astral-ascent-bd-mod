#Requires -Version 7.0
param([switch]$NoPause,[switch]$Elevated,[string]$GameDirectory)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'installer-core.ps1')
$statePath=Join-Path $env:LOCALAPPDATA 'AstralAscentBD/install.json'
$code=0
try {
 if(Get-Process -Name 'Astral Ascent' -ErrorAction SilentlyContinue){throw 'Close Astral Ascent first. / 请先退出星界战士。'}
 if(-not $GameDirectory){
  $steam=(Get-ItemProperty 'HKCU:/Software/Valve/Steam').SteamPath
  $libraries=@($steam)
  $vdf=Join-Path $steam 'steamapps/libraryfolders.vdf'
  if(Test-Path -LiteralPath $vdf){$libraries+=@([regex]::Matches((Get-Content -LiteralPath $vdf -Raw),'"path"\s*"([^"]+)"') | ForEach-Object {$_.Groups[1].Value.Replace('\\','\')})}
  $candidates=@($libraries | ForEach-Object {Join-Path $_ 'steamapps/common/Astral Ascent'} | Where-Object {Test-Path -LiteralPath (Join-Path $_ 'Astral Ascent.exe')} | ForEach-Object {(Resolve-Path -LiteralPath $_).Path} | Sort-Object -Unique)
  if($candidates.Count -ne 1){throw 'Cannot uniquely locate the game; specify -GameDirectory. / 无法唯一定位游戏，请用 -GameDirectory 指定游戏目录。'}
  $GameDirectory=$candidates[0]
 }
 $GameDirectory=(Resolve-Path -LiteralPath $GameDirectory).Path
 if((Get-InstallHash (Join-Path $GameDirectory 'Astral Ascent.exe')) -ne 'CA376D2B741F65C75C416317517D24C316DD8A32A4EAE6559030797B3B9AA88B'){throw 'Unsupported game build; only verified 2.6.4 is supported. / 游戏版本不匹配：只支持已核对的 2.6.4。'}
 $proxy=Resolve-InstallFile $GameDirectory 'version.dll'
 if(Test-Path -LiteralPath $proxy){
  if(-not (Test-Path -LiteralPath $statePath)){throw 'Unrelated version.dll exists; installation stopped. / 已有其他 version.dll，停止安装，避免覆盖其他 Mod。'}
  $old=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json -AsHashtable
  if($old.gameDirectory -ne $GameDirectory -or (Get-InstallHash $proxy).ToLowerInvariant() -ne $old.files['version.dll']){throw 'The loader belongs to another mod or was modified; stopped. / 加载入口不属于本 Mod 或已被修改，停止覆盖。'}
 }
 $manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json -AsHashtable
 $plan=@(foreach($name in (@($manifest.Keys)+'manifest.json')){
  $source=Resolve-InstallFile $PSScriptRoot $name
  $hash=Get-InstallHash $source
  if($name -ne 'manifest.json' -and $hash.ToLowerInvariant() -ne $manifest[$name]){throw "源文件校验失败：$name"}
  $target=Resolve-InstallFile $GameDirectory ('astral_bd/'+$name)
  [pscustomobject]@{Name=('astral_bd/'+$name);Source=$source;Target=$target;SourceHash=$hash;PreviousHash=if(Test-Path -LiteralPath $target){Get-InstallHash $target}else{$null}}
 })
 $source=Join-Path $PSScriptRoot 'autoload/version.dll'
 $plan+=[pscustomobject]@{Name='version.dll';Source=$source;Target=$proxy;SourceHash=Get-InstallHash $source;PreviousHash=if(Test-Path -LiteralPath $proxy){Get-InstallHash $proxy}else{$null}}
 $access=$true
 try {Test-InstallAccess $plan $GameDirectory}
 catch [UnauthorizedAccessException] {
  if($Elevated){throw}
  $access=$false
  if((Invoke-ElevatedInstall $PSCommandPath) -ne 0){throw 'Elevated installation failed. / 提权安装未成功。'}
 }
 if($access){
  Invoke-InstallTransaction $plan $GameDirectory
  $files=@{};foreach($file in $plan){$files[$file.Name]=$file.SourceHash.ToLowerInvariant()}
  New-Item -ItemType Directory -Path (Split-Path $statePath -Parent) -Force | Out-Null
  @{gameDirectory=$GameDirectory;files=$files} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding utf8NoBOM
 }
 foreach($file in $plan){if((Get-InstallHash $file.Target) -ne $file.SourceHash){throw "安装校验失败：$($file.Name)"}}
 Write-Host 'Installed and verified. Start the game normally; F8 opens Builds. / 自动加载已安装并验证。以后正常启动游戏即可自动加载，按 F8 选择 BD。' -ForegroundColor Green
} catch {Write-Host $_ -ForegroundColor Red;$code=1}
if(-not $NoPause){[void](Read-Host 'Press Enter to close / 按 Enter 关闭')}
exit $code
