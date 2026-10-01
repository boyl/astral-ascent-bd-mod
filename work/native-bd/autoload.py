"""游戏入口自动启动；配置与日志保存在当前用户目录。"""
import ctypes as C
import os
import sys
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
data=Path(os.environ['LOCALAPPDATA'])/'AstralAscentBD'
data.mkdir(parents=True,exist_ok=True)
try:
 import controller
 sys.argv=[sys.argv[0],'--data-dir',str(data)]
 controller.main()
except Exception:
 message=traceback.format_exc()
 (data/'autoload-error.log').write_text(message,encoding='utf-8')
 C.WinDLL('user32').MessageBoxW(None,'BD Mod failed to load / BD Mod 自动加载失败\nDetails / 详情：'+str(data/'autoload-error.log'),'Astral Ascent BD Mod / 星界战士 BD Mod',0x10)
 raise
