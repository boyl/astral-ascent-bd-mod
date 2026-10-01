"""本机光环方案存储，与原版存档及 BD 默认配置分离。"""
import json
import uuid
from pathlib import Path


def validate(document):
    if not isinstance(document, dict) or document.get('version') != 1 or not isinstance(document.get('plans'), list):
        raise ValueError('光环方案文件格式无效')
    ids = set()
    for plan in document['plans']:
        if not isinstance(plan, dict) or not isinstance(plan.get('id'), str) or not plan['id'] or plan['id'] in ids:
            raise ValueError('光环方案编号无效或重复')
        if not isinstance(plan.get('name'), str) or not plan['name'].strip() or len(plan['name']) > 48:
            raise ValueError('光环方案名称无效')
        if not isinstance(plan.get('auras'), list) or len(plan['auras']) != 5 or any(type(x) is not int or x < 0 for x in plan['auras']):
            raise ValueError('光环方案必须包含五个有效槽位')
        ids.add(plan['id'])
    return document


def load(path):
    path = Path(path)
    return validate(json.loads(path.read_text(encoding='utf-8'))) if path.exists() else {'version': 1, 'plans': []}


def save(path, name, auras, language='zh-CN'):
    path = Path(path)
    document = load(path)
    name = name.strip() or f'{"Aura Plan" if language == "en" else "光环方案"} {len(document["plans"]) + 1}'
    names = {plan['name'] for plan in document['plans']}
    base = name[:48]
    name = base
    serial = 2
    while name in names:
        suffix = f' ({serial})'
        name = base[:48-len(suffix)] + suffix
        serial += 1
    plan = {'id': uuid.uuid4().hex, 'name': name, 'auras': auras}
    document['plans'].append(plan)
    validate(document)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)
    return document, plan
