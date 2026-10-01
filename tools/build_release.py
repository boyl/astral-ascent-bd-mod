"""从已提交源码和指定依赖运行时建立允许列表发行包。"""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--runtime-dir',type=Path,required=True)
parser.add_argument('--commit',required=True)
args=parser.parse_args()
if len(args.commit)!=40 or any(c not in '0123456789abcdef' for c in args.commit):raise ValueError('无效 Git 提交')
version=(root/'VERSION').read_text().strip()
package=root/'outputs/astral-bd';package.mkdir(parents=True,exist_ok=True)
source=root/'work/native-bd'
for name in ['runtime.js','controller.py','aura_plans.py','localization.py','autoload.py','recipes.json','auras.json','recipes.en.json','auras.en.json']:
    shutil.copy2(source/name,package/name)
for path in (root/'installer').iterdir():shutil.copy2(path,package/path.name)
for name in ['README.md','README.en.md']:shutil.copy2(root/name,package/name)
shutil.copy2(root/'LICENSE',package/'LICENSE-Mod.txt')
shutil.copy2(source/'vendor/imgui/LICENSE.txt',package/'ImGui-LICENSE.txt')
shutil.copytree(args.runtime_dir,package/'runtime',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
required={'autoload/version.dll','astral_bd_overlay.dll','runtime/python.exe','runtime/frida/_frida.pyd','runtime/LICENSE.txt','runtime/frida-17.19.0.dist-info/licenses/COPYING'}
assert all((package/p).is_file() for p in required)
(package/'release.json').write_text(json.dumps({'modVersion':version,'gameVersion':'2.6.4','sourceCommit':args.commit,'languages':['zh-CN','en'],'channel':'beta'},indent=2),encoding='utf-8')
allowed=['autoload/version.dll','astral_bd_overlay.dll','release.json','ImGui-LICENSE.txt','LICENSE-Mod.txt','README.md','README.en.md']
allowed += ['runtime.js','controller.py','aura_plans.py','localization.py','autoload.py','recipes.json','auras.json','recipes.en.json','auras.en.json']
allowed += [p.name for p in (root/'installer').iterdir()]
allowed += [p.relative_to(package).as_posix() for p in (package/'runtime').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
manifest={name:hashlib.sha256((package/name).read_bytes()).hexdigest() for name in sorted(allowed)}
(package/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive_path=root/'outputs'/f'AstralAscent-BD-Mod-v{version}.zip'
with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for name in [*manifest,'manifest.json']:archive.write(package/name,'astral-bd/'+name)
with zipfile.ZipFile(archive_path) as archive:
    assert len(archive.namelist())==len(manifest)+1
    for name,digest in manifest.items():assert hashlib.sha256(archive.read('astral-bd/'+name)).hexdigest()==digest,name
    assert not any(Path(p).name in ('profile.json','aura-plans.json','ui-settings.json') or p.endswith(('.sav','.jsonl','.log')) for p in archive.namelist())
digest=hashlib.sha256(archive_path.read_bytes()).hexdigest()
(root/'outputs/SHA256SUMS.txt').write_text(digest+'  '+archive_path.name+'\n',encoding='ascii')
print(json.dumps({'archive':str(archive_path),'size':archive_path.stat().st_size,'sha256':digest,'files':len(manifest)+1,'commit':args.commit}))
