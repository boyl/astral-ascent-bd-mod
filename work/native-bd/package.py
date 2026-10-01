"""打包本机已有 Python 标准库和 Frida，生成无需安装依赖的测试包。"""
import json,hashlib,shutil,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
output=root/'outputs/astral-bd';runtime=output/'runtime';runtime.mkdir(exist_ok=True)
python=Path(sys.executable).parent
for name in ['python.exe','python3.dll','python312.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt']:
 shutil.copy2(python/name,runtime/name)
shutil.copytree(python/'DLLs',runtime/'DLLs',dirs_exist_ok=True)
with zipfile.ZipFile(runtime/'python312.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in (python/'Lib').rglob('*'):
  relative=path.relative_to(python/'Lib')
  if path.is_file() and path.suffix in ('.py','.txt','.json','.pem') and not any(p in ('site-packages','__pycache__','test','tests','idlelib','tkinter','turtledemo','ensurepip') for p in relative.parts):z.write(path,relative.as_posix())
(runtime/'python312._pth').write_text('python312.zip\nDLLs\n.\n..\nimport site\n',encoding='ascii')
for name in ['frida','frida-17.19.0.dist-info']:shutil.copytree(root/'work/frida-runtime'/name,runtime/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['runtime.js','controller.py','aura_plans.py','localization.py','recipes.json','auras.json','recipes.en.json','auras.en.json']:shutil.copy2(Path(__file__).parent/name,output/name)
shutil.copy2(Path(__file__).parent/'vendor/imgui/LICENSE.txt',output/'ImGui-LICENSE.txt')
manifest={str(p.relative_to(output)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('manifest.json','profile.json','runtime.jsonl')}
(output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('测试包已生成：',output)
