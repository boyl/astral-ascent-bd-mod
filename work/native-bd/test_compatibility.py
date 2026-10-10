"""针对真实 EXE 的离线兼容边界回归；不会启动或修改游戏。"""
import json
import hashlib
import re
import struct
import sys
import unittest
from pathlib import Path
import compatibility


class NativeCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = Path(sys.argv[1]).read_bytes()
        cls.spec = json.loads(Path(__file__).with_name('compatibility.json').read_text(encoding='utf-8'))
        pe = struct.unpack_from('<I', cls.image, 0x3c)[0]
        optional_size = struct.unpack_from('<H', cls.image, pe + 20)[0]
        cls.text_header = pe + 24 + optional_size
        cls.text_raw = struct.unpack_from('<I', cls.image, cls.text_header + 20)[0]
        cls.text_size = struct.unpack_from('<I', cls.image, cls.text_header + 16)[0]

    def pattern(self, name):
        anchor = self.spec['anchors'][name]
        raw = bytes.fromhex(anchor['bytes'])
        pattern = b''.join(re.escape(bytes([v])) if fixed == '1' else b'.' for v, fixed in zip(raw, anchor['mask']))
        return anchor, raw, re.compile(pattern, re.DOTALL)

    def test_real_layout(self):
        result = compatibility.resolve_image(self.image)
        fixtures = {
            '9bf346e5815ebc3f86e2e17f3d86e8c3925ef257bf7b91424d92e90f02b0e21c':
                (0x150a470, 0x341a880, 0xc6a14e0, 0x1c4850),
            # 2026-10-11 本机 EXE：锚点通过原生函数表检查，equipment 经只读实机五槽采样。
            'f46d2391e2725d68e11ea842e0e610b8ab0f690a3a8acc59b4a11a1180db2cf2':
                (22097296, 54700624, 208469872, 1853520),
        }
        fingerprint = hashlib.sha256(self.image).hexdigest()
        self.assertIn(fingerprint, fixtures, '新 EXE 需要独立核对测试预期；运行时不按指纹拦截')
        self.assertEqual(tuple(result[k] for k in ('refresh', 'runStart', 'equipment', 'runField')), fixtures[fingerprint])

    def test_unrelated_executable_change_remains_compatible(self):
        self.assertEqual(compatibility.resolve_image(self.image + b'UNRELATED_FILE_CONTENT_CHANGE'), compatibility.resolve_image(self.image))

    def test_missing_interface_fails(self):
        anchor, _, pattern = self.pattern('refresh')
        changed = bytearray(self.image)
        match = pattern.search(changed, self.text_raw, self.text_raw + self.text_size)
        changed[match.start()] ^= 0xff
        with self.assertRaisesRegex(compatibility.CompatibilityError, 'refresh'):
            compatibility.resolve_image(changed)

    def test_ambiguous_interface_fails(self):
        _, raw, _ = self.pattern('refresh')
        changed = bytearray(self.image)
        changed[self.text_raw + 0x2000:self.text_raw + 0x2000 + len(raw)] = raw
        with self.assertRaisesRegex(compatibility.CompatibilityError, '歧义.*refresh'):
            compatibility.resolve_image(changed)

    def test_call_into_middle_of_function_fails(self):
        anchor, _, pattern = self.pattern('assign')
        changed = bytearray(self.image)
        match = pattern.search(changed, self.text_raw, self.text_raw + self.text_size)
        offset = match.start() + anchor['instructionOffset'] + anchor['operandOffset']
        displacement = struct.unpack_from('<i', changed, offset)[0]
        struct.pack_into('<i', changed, offset, displacement + 1)
        with self.assertRaisesRegex(compatibility.CompatibilityError, '完整函数.*assign'):
            compatibility.resolve_image(changed)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativeCompatibilityTests))
    sys.exit(0 if result.wasSuccessful() else 1)
