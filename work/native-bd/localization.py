"""界面语言偏好；独立于构筑和光环方案文件。"""
import ctypes
import json
from pathlib import Path


def load(path):
    path = Path(path)
    if not path.exists():
        return 'zh-CN' if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3ff == 4 else 'en'
    language = json.loads(path.read_text(encoding='utf-8'))['language']
    if language not in ('zh-CN', 'en'):
        raise ValueError('Unsupported UI language / 不支持的界面语言')
    return language


def save(path, language):
    if language not in ('zh-CN', 'en'):
        raise ValueError('Unsupported UI language / 不支持的界面语言')
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'language': language}), encoding='utf-8')
    temporary.replace(path)
