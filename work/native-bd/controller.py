"""连接游戏内界面的原生运行时；仅匹配已验明的 EXE 指纹。"""
import aura_plans
import localization
from collections import deque
import argparse
import ctypes as C
import hashlib
import json
import os
import sys
import time
from pathlib import Path
root=Path(__file__).resolve().parents[2]
folder=Path(__file__).resolve().parent
package=(folder/'astral_bd_overlay.dll').exists()
assets=folder if package else root/'outputs/astral-bd'
recipes=json.loads((folder/'recipes.json').read_text(encoding='utf-8'))
auras=json.loads((folder/'auras.json').read_text(encoding='utf-8'))
sys.path.insert(0,str(folder/'runtime' if package else root/'work/frida-runtime'))
import frida

DATA_HASHES={
 'array_relicsbook.json':'445bef5e745844fa0c508de51c97f4a4ae218188f26e3582c8e0452e30ec1c04',
 'array_modificatorsbook.json':'d33123dd1dacdc3ff88f1db20f24abec3aad1ae76fc5ac50fea5227e7b264a70',
 'dictionary_spellbook.json':'87397723e709e0af689bc8ccb306a77a0e8fe6ae32ec3f0c47f0729221347552',
}

def validate_profile(profile):
 if not isinstance(profile,dict) or set(profile)!={'selected','mode','enabled','appliedRun','growth'}:raise ValueError('Mod 配置字段无效')
 if profile['selected'] is not None and (type(profile['selected']) is not int or profile['selected'] not in range(len(recipes))):raise ValueError('配方编号无效')
 if profile['mode'] not in ('formed','growth') or type(profile['enabled']) is not bool:raise ValueError('Mod 模式无效')
 if profile['appliedRun'] is not None and (type(profile['appliedRun']) is not int or profile['appliedRun']<0):raise ValueError('局编号无效')
 growth=profile['growth']
 if growth is not None:
  if not isinstance(growth,dict) or not {'run','seed','recipe','stage','available'}<=set(growth) or set(growth)-{'run','seed','recipe','stage','available','baseRoom','baseWorld'}:raise ValueError('成长配置字段无效')
  if any(type(growth[k]) is not int for k in growth) or growth['run']<0 or growth['recipe'] not in range(len(recipes)) or growth['stage'] not in range(5) or growth['available']<0:raise ValueError('成长进度无效')
 return profile

def process_id():
 matches=[p.pid for p in frida.get_local_device().enumerate_processes() if p.name.lower()=='astral ascent.exe']
 if len(matches)>1:raise RuntimeError('检测到多个游戏进程，请保留一个游戏实例')
 return matches[0] if matches else None

def launch():
 if process_id() is not None:return
 os.startfile('steam://rungameid/1280930')
 user=C.WinDLL('user32');visitor_type=C.WINFUNCTYPE(C.c_int,C.c_void_p,C.c_void_p)
 user.EnumWindows.argtypes=[visitor_type,C.c_void_p]
 user.IsWindowVisible.argtypes=[C.c_void_p]
 user.GetWindowThreadProcessId.argtypes=[C.c_void_p,C.POINTER(C.c_ulong)]
 user.GetClientRect.argtypes=[C.c_void_p,C.c_void_p]
 class Rect(C.Structure):_fields_=[('left',C.c_long),('top',C.c_long),('right',C.c_long),('bottom',C.c_long)]
 deadline=time.monotonic()+60;stable_pid=None;stable_since=None
 while time.monotonic()<deadline:
  pid=process_id();windows=[]
  @visitor_type
  def visitor(hwnd,_):
   owner=C.c_ulong();rect=Rect();user.GetWindowThreadProcessId(hwnd,C.byref(owner))
   if owner.value==pid and user.IsWindowVisible(hwnd) and user.GetClientRect(hwnd,C.byref(rect)) and rect.right*rect.bottom>300000:windows.append(hwnd)
   return 1
  user.EnumWindows(visitor,None)
  if pid and windows:
   if stable_pid!=pid:stable_pid=pid;stable_since=time.monotonic()
   elif time.monotonic()-stable_since>=.6:return
  else:stable_pid=None;stable_since=None
  time.sleep(.2)
 raise RuntimeError('Steam 未在 60 秒内打开游戏窗口')

def executable(pid):
 k=C.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[C.c_uint,C.c_int,C.c_uint];k.OpenProcess.restype=C.c_void_p
 k.QueryFullProcessImageNameW.argtypes=[C.c_void_p,C.c_uint,C.c_wchar_p,C.POINTER(C.c_uint)];k.CloseHandle.argtypes=[C.c_void_p]
 handle=k.OpenProcess(0x1000,False,pid)
 if not handle:raise C.WinError(C.get_last_error())
 try:
  path=C.create_unicode_buffer(32768);length=C.c_uint(len(path))
  if not k.QueryFullProcessImageNameW(handle,0,path,C.byref(length)):raise C.WinError(C.get_last_error())
  return Path(path.value)
 finally:k.CloseHandle(handle)

def _main():
 parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=0);parser.add_argument('--recipe',type=int,choices=range(len(recipes)));parser.add_argument('--mode',choices=['formed','growth'],default='formed');parser.add_argument('--data-dir',type=Path,default=assets);args=parser.parse_args()
 args.data_dir.mkdir(parents=True,exist_ok=True)
 pid=process_id()
 if pid is None:raise RuntimeError('请先启动星界战士，再运行 BD Mod')
 game_exe=executable(pid)
 if hashlib.sha256(game_exe.read_bytes()).hexdigest().upper()!='CA376D2B741F65C75C416317517D24C316DD8A32A4EAE6559030797B3B9AA88B':raise RuntimeError('游戏版本不匹配：本版仅支持核对过的 2.6.4 EXE')
 for name,digest in DATA_HASHES.items():
  if hashlib.sha256((game_exe.parent/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('组件数据版本不匹配：'+name)
 path=assets/'astral_bd_overlay.dll'
 local=C.CDLL(str(path));local.BDPresentAddress.restype=C.c_void_p
 k=C.WinDLL('kernel32');k.GetModuleHandleW.argtypes=[C.c_wchar_p];k.GetModuleHandleW.restype=C.c_void_p
 address=local.BDPresentAddress()
 if not address:raise RuntimeError('无法探测 D3D11 Present')
 rva=address-k.GetModuleHandleW('dxgi.dll')
 language_path=args.data_dir/'ui-settings.json'
 language=localization.load(language_path)
 catalogs={'zh-CN':{'recipes':recipes,'auras':auras},'en':{name:json.loads((folder/(name+'.en.json')).read_text(encoding='utf-8')) for name in ('recipes','auras')}}
 source=(folder/'runtime.js').read_text(encoding='utf-8').replace('DLL_PATH',json.dumps(str(path))).replace('PRESENT_RVA',str(rva)).replace('CATALOG_DATA',json.dumps(catalogs,ensure_ascii=False)).replace('LANGUAGE_DATA',json.dumps(language))
 session=frida.attach(pid)
 probe=session.create_script("rpc.exports.ready=()=>!!Process.findModuleByName('dxgi.dll');")
 try:
  probe.load();deadline=time.monotonic()+30
  while not probe.exports_sync.ready():
   if time.monotonic()>=deadline:raise RuntimeError('游戏图形运行时未就绪，无法连接 BD 界面')
   time.sleep(.2)
 except Exception:
  session.detach();raise
 finally:
  try:probe.unload()
  except frida.InvalidOperationError:pass
 script=session.create_script(source)
 stopped=False
 connected=True
 runtime_error=None
 profile_path=args.data_dir/'profile.json'
 plans_path=args.data_dir/'aura-plans.json'
 plan_document=aura_plans.load(plans_path)
 plan_requests=deque()
 log=(args.data_dir/'runtime.jsonl').open('a',encoding='utf-8')
 def message(m,d):
  nonlocal stopped,runtime_error
  log.write(json.dumps(m,ensure_ascii=False)+'\n');log.flush();print(json.dumps(m,ensure_ascii=False),flush=True)
  if m.get('payload',{}).get('event')=='stopped':stopped=True
  if m.get('type')=='error':runtime_error=m.get('description','原生运行时错误')
  if m.get('payload',{}).get('event')=='aura-plan-save':plan_requests.append(m['payload'])
  if m.get('payload',{}).get('event')=='language':localization.save(language_path,m['payload']['language'])
  if m.get('payload',{}).get('event')=='profile':
   temporary=profile_path.with_suffix('.tmp');temporary.write_text(json.dumps(m['payload']['profile'],ensure_ascii=False,indent=2),encoding='utf-8');temporary.replace(profile_path)
 script.on('message',message)
 def detached(reason,crash):
  nonlocal connected
  connected=False
  print('游戏连接已结束：'+reason,flush=True)
 session.on('detached',detached)
 try:
  script.load()
  script.exports_sync.plans(plan_document)
  if profile_path.exists():
   profile=validate_profile(json.loads(profile_path.read_text(encoding='utf-8')))
   script.exports_sync.restore(profile)
   time.sleep(.1)
  if args.recipe is not None:script.exports_sync.select(args.recipe,args.mode)
  end=time.monotonic()+args.seconds if args.seconds else float('inf')
  while connected and time.monotonic()<end:
   if runtime_error:raise RuntimeError(runtime_error)
   while plan_requests:
    request=plan_requests.popleft()
    try:
     document,_=aura_plans.save(plans_path,request['name'],request['auras'],request.get('language','zh-CN'))
    except (ValueError,OSError) as e:
     script.exports_sync.plans(None,('Failed to save aura plan: ' if request.get('language')=='en' else '保存光环方案失败：')+str(e))
    else:script.exports_sync.plans(document)
   time.sleep(.2)
 except KeyboardInterrupt:pass
 finally:
  try:
   script.exports_sync.stop();end=time.monotonic()+3
   while not stopped and time.monotonic()<end:time.sleep(.05)
  except frida.InvalidOperationError:pass
  if connected:session.detach()
  log.close()

def main():
 pid=process_id()
 if pid is None:raise RuntimeError('请先启动星界战士，再运行 BD Mod')
 k=C.WinDLL('kernel32',use_last_error=True)
 k.CreateMutexW.argtypes=[C.c_void_p,C.c_int,C.c_wchar_p];k.CreateMutexW.restype=C.c_void_p
 k.CloseHandle.argtypes=[C.c_void_p]
 handle=k.CreateMutexW(None,False,'Local\\AstralAscentBD-'+str(pid));error=C.get_last_error()
 if not handle:raise C.WinError(error)
 try:
  if error==183:
   print('本局 BD Mod 已自动加载。按 F8 打开界面。',flush=True)
   return
  _main()
 finally:k.CloseHandle(handle)

if __name__=='__main__':main()
