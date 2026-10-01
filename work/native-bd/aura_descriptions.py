"""将原版效果模板和组件数值展开成光环中文说明。"""
import json,re
from pathlib import Path
game=Path('C:/Program Files (x86)/Steam/steamapps/common/Astral Ascent')
loc=json.loads((game/'dictionary_localisation_chinese_simplified.json').read_text(encoding='utf-8'))['data']
book=json.loads((game/'array_relicsbook.json').read_text(encoding='utf-8'))['data']
builder=json.loads((game/'array_effectbuilder.json').read_text(encoding='utf-8'))['data']
loc['effect_fireshield']=loc['effect_fireShield']
loc['effect_moveSpeed']='移动速度'
# 生命状态阈值由运行时提供，静态目录不编造数值。
loc['playerLife_high']='处于高生命值状态'
loc['playerLife_low']='处于低生命值状态'

english=json.loads((game/'dictionary_localisation_english.json').read_text(encoding='utf-8'))['data']
english['effect_fireshield']=english['effect_fireShield']
english['effect_moveSpeed']='Movement speed'
english['playerLife_high']='at high life'
english['playerLife_low']='at low life'

def clean(value,language='zh-CN'):return re.sub(r'\[.*?\]','',str(value)).replace('⏳','Cooldown / interval: ' if language=='en' else '冷却 / 触发间隔：').strip()
def expand(value,params=None,depth=0,language='zh-CN'):
 data=english if language=='en' else loc
 params=params or {}
 if depth>12:raise ValueError('效果模板循环引用')
 def sub(m):
  k=m[1]
  if k in params:return str(params[k])
  if k in data:return expand(clean(data[k],language),params,depth+1,language)
  return '{'+k+'}'
 return re.sub(r'\{([^{}]+)\}',sub,clean(value,language))
def numeric(value):return str(value).removesuffix('%')
def description(i,language='zh-CN'):
 data=english if language=='en' else loc
 lines=[]
 for c in [0,2,4]:
  tag=str(book[c][i][0]);value=book[c+1][i][0]
  if not tag:continue
  params={'aura_effectValue':numeric(value),'aura_effectCD':book[8][i][0]}
  template=data.get('auraEffect_'+tag)
  if template is None and '@' in tag:
   row=int(tag.split('@')[1]);trigger=builder[1][row][0];gimmick=builder[2][row][0]
   params.update(effectValue=numeric(value),effectChance=builder[5][row][0],effectCooldown=builder[4][row][0])
   params['template_effectBuild']=expand(data['effectGimmick_'+{'snowflake':'snowFlake'}.get(gimmick,gimmick)],params,language=language)
   template=data[trigger]
   if builder[5][row][0]!=100:template=(str(builder[5][row][0])+'% chance: ' if language=='en' else '有'+str(builder[5][row][0])+'%几率：')+template
   if builder[4][row][0]!='':template+=(' (Interval: ' if language=='en' else '（触发间隔：')+expand(data['effectCooldown_'+builder[3][row][0]],params,language=language)+(')' if language=='en' else '）')
  if template is None and tag=='upgradeAura':template='This aura can be upgraded.' if language=='en' else '此光环可升级。'
  if template is None:raise ValueError('缺少原版效果模板：'+tag)
  line=expand(template,params,language=language)
  if '!' in tag and book[7][i][0]:line+=' ('+expand(data['aura_cooldownText_'+book[7][i][0]],params,language=language)+')'
  lines.append('• '+line)
 return '\n'.join(lines)
