"""持久化契约验证：真实写盘重载、重复名称、空槽与非法输入。"""
import tempfile,json
from pathlib import Path
import aura_plans
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder)/'aura-plans.json'
 assert aura_plans.load(p)=={'version':1,'plans':[]}
 d,a=aura_plans.save(p,'猎人方案',[144,294,144,294,0])
 _,b=aura_plans.save(p,'猎人方案',[136,136,108,108,122])
 _,c=aura_plans.save(p,'',[0,0,0,0,0])
 read=aura_plans.load(p)
 assert read['plans'][0]['auras']==[144,294,144,294,0]
 assert [x['name'] for x in read['plans']]==['猎人方案','猎人方案 (2)','光环方案 3']
 assert len({x['id'] for x in read['plans']})==3
 before=p.read_bytes()
 try:aura_plans.save(p,'无效',[144])
 except ValueError:pass
 else:raise AssertionError('五槽契约未检查')
 assert p.read_bytes()==before
 try:aura_plans.validate({'version':1,'plans':[{'id':'a','name':'坏','auras':[False,0,0,0,0]}]})
 except ValueError:pass
 else:raise AssertionError('布尔类型不能作为组件 ID')
 p.write_text('{坏文件',encoding='utf-8')
 try:aura_plans.load(p)
 except json.JSONDecodeError:pass
 else:raise AssertionError('坏文件不能静默清空')
print('光环方案持久化契约通过：空槽、同名、重载、非法输入与损坏文件')
