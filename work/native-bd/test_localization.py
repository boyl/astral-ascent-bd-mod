"""有限语言集合完整验证：展示切换不得改变任何装备 ID。"""
import json
import re
import tempfile
from pathlib import Path
import aura_plans
import localization

folder=Path(__file__).parent
for kind in ('recipes','auras'):
    zh=json.loads((folder/(kind+'.json')).read_text(encoding='utf-8'))
    en=json.loads((folder/(kind+'.en.json')).read_text(encoding='utf-8'))
    assert len(zh)==len(en)==(12 if kind=='recipes' else 355)
    for a,b in zip(zh,en,strict=True):
        assert a.keys()==b.keys()
        assert all(a[k]==b[k] for k in a if k not in ('name','description','auraNames'))
        assert not re.search(r'[\u4e00-\u9fff]',b['name']+b['description'])
        assert not re.search(r'\{[^{}]+\}',b['description']), b['name']
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'ui-settings.json'
    for language in ('zh-CN','en'):
        localization.save(path,language)
        assert localization.load(path)==language
        doc,plan=aura_plans.save(Path(tmp)/'plans.json','',[144,294,144,294,0],language)
        assert plan['name'].startswith('Aura Plan' if language=='en' else '光环方案')
    original=path.read_bytes()
    try:localization.save(path,'fr')
    except ValueError:pass
    else:raise AssertionError('Unsupported language accepted')
    assert path.read_bytes()==original
print('中英文目录、显示占位符、语言重载、方案命名和无效语言契约通过')
