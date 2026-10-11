"""校验社区类别要求、原版触发语义和光环冻结基线。"""
import json, subprocess, sys, unittest
from pathlib import Path
folder=Path(__file__).parent
game=Path(sys.argv[1])
recipes=json.loads((folder/'recipes.json').read_text(encoding='utf-8'))
spells=json.loads((game/'dictionary_spellbook.json').read_text(encoding='utf-8'))['data']
book=json.loads((game/'array_modificatorsbook.json').read_text(encoding='utf-8'))['data']
baseline=json.loads(subprocess.check_output(['git','show','fa2901d:work/native-bd/recipes.json']))
# 期望描述业务效果；不读取生成器的 skill_loadouts.json。
effects=['iceSword','snowFlake','storm','manaSteal','iceSword','iceIdol','addEffect_electrify','slime','iceIdol','iceIdol','castMissile','addEffect_freeze']
class SkillTests(unittest.TestCase):
 def test_all_twelve_have_full_slots_and_correct_effects(self):
  for i,r in enumerate(recipes):
   with self.subTest(recipe=i):
    self.assertEqual(len(r['spells']),4)
    self.assertEqual(len(r.get('gambitSlots',[])),4)
    self.assertEqual(r['gambits'],[row[0] for row in r['gambitSlots']])
    for row in r['gambitSlots']:
     self.assertEqual(len(row),4)
     self.assertEqual(book[2][row[0]][0],'modEffect_'+effects[i])
     for identifier in row:
      self.assertIn(book[0][identifier][0],('modTrigger_onHit','modTrigger_onLaunch'))
    for identifier in r['spells']:
     fields=spells['spell_'+str(identifier)].split('|')
     self.assertEqual(int(fields[1].strip()),0,'只能使用公共法术，避免角色/DLC依赖')
     self.assertGreater(int(fields[2].strip()),0)
     self.assertNotEqual(fields[-1].strip(),'1','不能用单段占位技能替代多段发动机')
     if i in (0,1,3,4,10):self.assertEqual(int(fields[2].strip()),1)
 def test_aura_baseline_and_order_are_unchanged(self):
  self.assertEqual(len(recipes),12)
  for a,b in zip(recipes,baseline):
   self.assertEqual(a['auras'],b['auras'])
   self.assertEqual(a['name'],b['name'])
  for path in ('auras.json','auras.en.json','aura_plans.py'):
   self.assertEqual((folder/path).read_bytes().replace(b'\r\n',b'\n'),subprocess.check_output(['git','show','fa2901d:work/native-bd/'+path]).replace(b'\r\n',b'\n'))
 def test_language_parameters_match(self):
  english=json.loads((folder/'recipes.en.json').read_text(encoding='utf-8'))
  for a,b in zip(recipes,english):
   for key in ('auras','spells','gambits','gambitSlots'):self.assertEqual(a[key],b[key])
if __name__=='__main__':
 unittest.main(argv=[sys.argv[0]])
