"""使用原版英文名称与效果模板生成英文目录；组件 ID 与中文共用。"""
import json
import re
from pathlib import Path
from aura_descriptions import english, description

folder=Path(__file__).parent
auras=json.loads((folder/'auras.json').read_text(encoding='utf-8'))
recipes=json.loads((folder/'recipes.json').read_text(encoding='utf-8'))
def name(i):return re.sub(r'\[.*?\]','',english['relic_name_'+str(i)])
for a in auras:
    a['name']=name(a['id'])
    a['description']='Rarity: '+{1:'Common',2:'Rare',3:'Epic',4:'Astral'}[a['quality']]+'\n'+description(a['id'],'en')
rows=[
('Missiles + Ice Swords','Sabre summons and Allergic Reaction form the ice sword / missile cycle.'),
('Snowflakes + Ice Shards','Glacial Soul generates snowflakes; Brittle Ice adds ice shards and freeze criticals.'),
('Thundercloud Summons','Refreshes, mana spending and kills create thunderclouds; the storm mark strengthens them.'),
('Low-cost Spell Cycle','Low-cost spells with mana leech and sacred sword / sabre triggers as a general engine.'),
('3D Hunter (Marked Ice Swords)','Community 3D Hunter: Mountain Hunter\'s Illusion and Durandal Fragment cycle marks, spirit swords and ice swords.'),
('Ice Shards + Ice Idols','Ice Pebble and Subzero Dash cycle ice shards and idols.'),
('Spark Loop','Flashing Dash and Storm Strike trigger sparks and shocks in a loop.'),
('Slimes + Sparks','Sickening Spark and Yellow Jelly form a spark / slime cycle.'),
('Burning Idols + Homing Shields','Burning idols convert into fire idols, with homing shields adding tracking projectiles.'),
('Ice Idols + Poison Chain','Idols generate poison gas, linking spirit swords, slimes and sparks; an extended recipe.'),
('Full-life First Strike Missiles','First strike triggers missiles and joins the ice sword cycle; a clearing variant.'),
('Ice Strike + Brittle Ice','Ice Strike applies freeze and frostbite; Brittle Ice adds shards and criticals.'),
]
for r,(title,desc) in zip(recipes,rows,strict=True):
    r.update(name=title,description=desc,auraNames=[name(i) for i in r['auras']])
    if 'gambitSlots' in r:
        r['description']+='\nSpells: '+' / '.join(re.sub(r'\[.*?\]','',english['skill_name_'+str(i)]) for i in r['spells'])+' (1 mana each, multiple hits).\nEach spell: on-hit ice sword + mana recovery + mana recovery + casting barrier.'
for filename,value in [('auras.en.json',auras),('recipes.en.json',recipes)]:
    assert not any(re.search(r'[\u4e00-\u9fff]',x['name']+x['description']) for x in value)
    (folder/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('English catalog:',len(recipes),'builds,',len(auras),'auras')
