param([switch]$UIFixture)
$ErrorActionPreference='Stop'
if($PSVersionTable.PSVersion.Major -lt 7){throw '需要 PowerShell 7'}
$compilerRoot=Get-ChildItem 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC' -Directory | Sort-Object Name -Descending | Select-Object -First 1
$sdkRoot=Get-ChildItem 'C:/Program Files (x86)/Windows Kits/10/Include' -Directory | Sort-Object Name -Descending | Select-Object -First 1
$kitRoot=Split-Path (Split-Path $sdkRoot.FullName -Parent) -Parent
$env:INCLUDE=@((Join-Path $compilerRoot.FullName 'include'),(Join-Path $sdkRoot.FullName 'ucrt'),(Join-Path $sdkRoot.FullName 'shared'),(Join-Path $sdkRoot.FullName 'um')) -join ';'
$env:LIB=@((Join-Path $compilerRoot.FullName 'lib/x64'),(Join-Path $kitRoot ('Lib/'+$sdkRoot.Name+'/ucrt/x64')),(Join-Path $kitRoot ('Lib/'+$sdkRoot.Name+'/um/x64'))) -join ';'
$compiler=Join-Path $compilerRoot.FullName 'bin/Hostx64/x64/cl.exe'
$output=Join-Path $PSScriptRoot '../../outputs/astral-bd'
if($UIFixture){$output=Join-Path $PSScriptRoot '../ui-fixture'}
New-Item -ItemType Directory -Path $output -Force | Out-Null
Push-Location $PSScriptRoot
try{
 $defines=@();if($UIFixture){$defines=@('/DBD_UI_TEST')}
 & $compiler /nologo /LD /O2 /EHsc /std:c++17 /utf-8 /MT @defines /Ivendor/imgui overlay.cpp vendor/imgui/imgui.cpp vendor/imgui/imgui_draw.cpp vendor/imgui/imgui_tables.cpp vendor/imgui/imgui_widgets.cpp vendor/imgui/backends/imgui_impl_win32.cpp vendor/imgui/backends/imgui_impl_dx11.cpp /link ('/OUT:'+(Join-Path $output 'astral_bd_overlay.dll')) d3d11.lib dxgi.lib d3dcompiler.lib user32.lib gdi32.lib dwmapi.lib
 if($LASTEXITCODE -ne 0){throw "原生构建失败：$LASTEXITCODE"}
 if(-not $UIFixture){
  $assembler=Join-Path $compilerRoot.FullName 'bin/Hostx64/x64/ml64.exe'
  & $assembler /nologo /c autoload_stubs.asm
  if($LASTEXITCODE -ne 0){throw "加载器汇编失败：$LASTEXITCODE"}
  New-Item -ItemType Directory -Path (Join-Path $output 'autoload') -Force | Out-Null
  & $compiler /nologo /LD /O2 /EHsc /std:c++17 /utf-8 /MT autoload.cpp autoload_stubs.obj /link /DEF:autoload.def ('/OUT:'+(Join-Path $output 'autoload/version.dll')) user32.lib
  if($LASTEXITCODE -ne 0){throw "加载器构建失败：$LASTEXITCODE"}
 }
 & $compiler /nologo /O2 /EHsc /utf-8 /MT ui_fixture.cpp /link /SUBSYSTEM:WINDOWS ('/OUT:'+(Join-Path $PSScriptRoot 'AstralBDUITest.exe')) d3d11.lib dxgi.lib user32.lib
 if($LASTEXITCODE -ne 0){throw "界面测试窗口构建失败：$LASTEXITCODE"}
}finally{Pop-Location}
