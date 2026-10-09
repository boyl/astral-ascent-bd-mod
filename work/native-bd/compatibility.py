"""按原生代码锚点解析布局；不以版本号或 EXE 整体哈希决定兼容性。"""
import json
import re
import struct
from pathlib import Path


class CompatibilityError(RuntimeError):
    pass


def resolve(executable, specification=None):
    image = Path(executable).read_bytes()
    return resolve_image(image, specification)


def resolve_image(image, specification=None):
    if image[:2] != b'MZ':
        raise CompatibilityError('游戏文件不是 Windows PE')
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    if image[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', image, pe + 4)[0] != 0x8664:
        raise CompatibilityError('需要 Windows x64 游戏')
    count = struct.unpack_from('<H', image, pe + 6)[0]
    optional_size = struct.unpack_from('<H', image, pe + 20)[0]
    sections = {}
    for i in range(count):
        offset = pe + 24 + optional_size + i * 40
        name = image[offset:offset + 8].rstrip(b'\0').decode('ascii')
        size, rva, raw_size, raw = struct.unpack_from('<IIII', image, offset + 8)
        sections[name] = (rva, size, raw, raw_size)
    if '.text' not in sections or '.pdata' not in sections:
        raise CompatibilityError('游戏缺少代码或原生函数表')
    text_rva, _, text_raw, text_size = sections['.text']
    code = image[text_raw:text_raw + text_size]
    _, _, unwind_raw, unwind_size = sections['.pdata']
    functions = {struct.unpack_from('<I', image, i)[0] for i in range(unwind_raw, unwind_raw + unwind_size - 11, 12)}
    spec = specification or json.loads(Path(__file__).with_name('compatibility.json').read_text(encoding='utf-8'))
    resolved = {}
    for name, anchor in spec['anchors'].items():
        raw = bytes.fromhex(anchor['bytes'])
        if len(raw) != len(anchor['mask']) or len(raw) < 20:
            raise CompatibilityError('无效的兼容锚点：' + name)
        pattern = b''.join(re.escape(bytes([value])) if fixed == '1' else b'.' for value, fixed in zip(raw, anchor['mask']))
        matches = re.finditer(pattern, code, re.DOTALL)
        first = next(matches, None)
        if first is None or next(matches, None) is not None:
            raise CompatibilityError('原生接口缺失或存在歧义：' + name + '；需要更新接口适配')
        site = first.start() + anchor['instructionOffset']
        kind = anchor['kind']
        if kind == 'entry':
            value = text_rva + site
        else:
            offset = site + anchor['operandOffset']
            operand = int.from_bytes(code[offset:offset + anchor['operandSize']], 'little', signed=True)
            value = operand if kind == 'field' else text_rva + site + anchor['instructionSize'] + operand
        value += anchor.get('add', 0)
        if kind in ('entry', 'call') and value not in functions:
            raise CompatibilityError('原生入口不是完整函数：' + name)
        if kind == 'rip' and not any(rva <= value < rva + size for rva, size, _, _ in sections.values()):
            raise CompatibilityError('全局对象超出游戏映像：' + name)
        if kind == 'field' and not 0 <= value < 0x400000:
            raise CompatibilityError('对象字段超出合理范围：' + name)
        resolved[name] = value
    return resolved
