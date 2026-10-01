"""从已核对的原版数据生成配方和手动光环目录。"""
import json,re
from aura_descriptions import description
from pathlib import Path
game=Path('C:/Program Files (x86)/Steam/steamapps/common/Astral Ascent')
folder=Path(__file__).parent
loc=json.loads((game/'dictionary_localisation_chinese_simplified.json').read_text(encoding='utf-8'))['data']
book=json.loads((game/'array_relicsbook.json').read_text(encoding='utf-8'))['data']
def name(i):return re.sub(r'\[.*?\]','',loc.get('relic_name_'+str(i),''))
ice='https://www.bilibili.com/opus/999341346789523458'
cycle='https://game.3loumao.org/723945734'
rows=[
 ('导弹＋冰剑',[143,392,143,392,414],[113,151,113,151],'军刀召唤与过敏反应形成冰剑、导弹循环。',ice),
 ('雪花＋冰碎片',[136,136,108,108,122],[96,107,96,107],'冰川之魂持续补雪花，脆冰补碎片与冻结暴击。',ice),
 ('雷云召唤',[166,350,172,335,171],[80,80,80,80],'刷新、耗蓝与击杀补雷云；风暴之主印记加强雷云。','https://www.bilibili.com/video/BV1QxVrzXE8R/'),
 ('低费连放',[230,261,255,258,140],[138,113,138,113],'低费法术配合法力吸取与圣剑军刀；作为通用发动机。','https://www.vgover.com/news/152849'),
 ('3D 猎人（标记冰剑）',[144,294,144,294,140],[116,116,116,116],'社区所称 3D 猎人：山地猎人的幻象＋杜伦达尔碎片，以标记、灵剑和冰剑循环。',cycle),
 ('冰碎片＋冰偶像',[118,127,108,124,405],[107,106,107,106],'冰卵石与零下冲刺形成碎片、偶像循环。',cycle),
 ('火花自循环',[150,153,147,157,153],[71,71,71,71],'闪光冲刺与风暴打击以火花、电击互相触发。',cycle),
 ('史莱姆＋火花',[399,377,377,203,220],[21,21,21,21],'恶心火花与黄色果冻形成火花、史莱姆循环。',cycle),
 ('燃烧偶像＋追踪盾',[410,398,118,127,124],[106,107,106,107],'烧毁偶像转化火偶像，热追盾提供追踪弹分支。',ice),
 ('冰偶像＋毒气连锁',[365,297,221,220,377],[106,38,106,38],'偶像生成毒气，衔接灵剑、史莱姆与火花；扩展配方。',ice),
 ('满血先攻导弹',[414,287,291,392,143],[151,113,151,113],'先攻触发导弹，并接入冰剑循环；清场变体。','https://www.vgover.com/news/152849'),
 ('冰击＋脆冰',[112,112,108,108,404],[90,107,90,107],'冰击施加冻结与冻伤，脆冰提供碎片和暴击。',ice),
]
recipes=[]
for i,(title,ids,gambits,desc,source) in enumerate(rows):
 spells=[30,31,38,42] if i==4 else [38,39,43,38] if i==1 else [31,42,31,42] if i==2 else [34,45,34,45]
 assert all(name(a) and 1<=book[9][a][0]<=4 for a in ids)
 recipes.append(dict(name=title,auras=ids,spells=spells,gambits=gambits,description=desc,source=source,auraNames=[name(a) for a in ids]))
 if i==4:
  recipes[-1]['gambitSlots']=[[116,140,140,172] for _ in range(4)]
  recipes[-1]['description']+='\n配套法术：'+ ' / '.join(re.sub(r'\[.*?\]','',loc['skill_name_'+str(x)]) for x in spells)+'（全部 1 费、多段）。\n每个法术：命中冰剑＋回蓝＋回蓝＋施法屏障。'
auras=[dict(id=i,name=name(i),description='品质：'+{1:'普通',2:'稀有',3:'史诗',4:'星界'}[book[9][i][0]]+'\n'+description(i)) for i in range(len(book[0])) if name(i) and book[9][i][0] in (1,2,3,4)]
for a in auras:
 a['quality']=book[9][a['id']][0]
 tags=str(book[11][a['id']][0]).replace('!','').split(';')
 a['elements']=sum(1<<i for i,e in enumerate(['fire','ice','electric','poison','neutral']) if e in tags)
for filename,value in [('recipes.json',recipes),('auras.json',auras)]:
 (folder/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(recipes),'套配方，',len(auras),'项光环')
