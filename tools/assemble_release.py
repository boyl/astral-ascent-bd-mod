"""从已发布依赖与已验收差量构建完整包；每个输出字节受清单约束。"""
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

base = Path('AstralAscent-BD-Mod-v1.0.0-beta.1.zip')
delta = Path('verified-release-delta.zip')
assert digest(base.read_bytes()) == 'ab308835b695bf08dceb28f8828b66c4f7e71afdefeeff7f4c672abd1428d1b9'
for key in ('DELTA_SHA256', 'MANIFEST_SHA256'):
    assert re.fullmatch('[0-9a-f]{64}', os.environ[key])
assert digest(delta.read_bytes()) == os.environ['DELTA_SHA256']
with zipfile.ZipFile(base) as archive:
    files = {name.removeprefix('astral-bd/'): archive.read(name) for name in archive.namelist() if not name.endswith('/')}
with zipfile.ZipFile(delta) as archive:
    for name in archive.namelist():
        assert not name.startswith('/') and '..' not in Path(name).parts
        files[name] = archive.read(name)
assert digest(files['manifest.json']) == os.environ['MANIFEST_SHA256']
manifest = json.loads(files['manifest.json'])
assert len(manifest) == 82
metadata = json.loads(files['release.json'])
assert metadata['modVersion'] == '1.0.1'
assert metadata['sourceCommit'] == os.environ['GITHUB_SHA']
for name, expected in manifest.items():
    assert digest(files[name]) == expected, name
    assert Path(name).name not in ('profile.json', 'aura-plans.json', 'ui-settings.json')
    assert not name.endswith(('.sav', '.jsonl', '.log'))
output = Path('AstralAscent-BD-Mod-v1.0.1.zip')
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for name in [*manifest, 'manifest.json']:
        archive.writestr('astral-bd/' + name, files[name])
with zipfile.ZipFile(output) as archive:
    assert len(archive.namelist()) == 83
    for name, expected in manifest.items():
        assert digest(archive.read('astral-bd/' + name)) == expected
checksum = digest(output.read_bytes())
Path('SHA256SUMS.txt').write_text(checksum + '  ' + output.name + '\n', encoding='ascii')
print(json.dumps({'sha256': checksum, 'files': 83, 'bytes': output.stat().st_size, 'sourceCommit': metadata['sourceCommit']}))
