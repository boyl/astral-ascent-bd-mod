$ErrorActionPreference='Stop'
if($PSVersionTable.PSVersion.Major -lt 7){throw 'PowerShell 7 is required / 需要 PowerShell 7'}
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONDONTWRITEBYTECODE='1'
$python=Join-Path $PSScriptRoot 'runtime/python.exe'
try {
 $manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json -AsHashtable
 foreach($item in $manifest.GetEnumerator()) {
  $path=Join-Path $PSScriptRoot $item.Key
  if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.Value){throw "文件校验失败：$($item.Key)"}
 }
 Write-Host 'Starting Astral Ascent via Steam. Ctrl+C stops the helper. / 启动 Steam 星界战士，并连接游戏内 BD 界面。Ctrl+C 退出 Mod。'
 & $python -c "import sys;sys.path.insert(0,sys.argv.pop(1));import controller;controller.launch();controller.main()" $PSScriptRoot
 if($LASTEXITCODE -ne 0){throw "运行时退出：$LASTEXITCODE"}
} catch {
 Write-Host $_ -ForegroundColor Red
 Read-Host 'Press Enter to close / 按 Enter 关闭窗口'
 exit 1
}
