// 仅支持已核对的 2.6.4 EXE；地址由主模块基址计算。
let language=LANGUAGE_DATA;
function t(zh,en){return language==='en'?en:zh;}
const b=Process.mainModule.base,state=b.add(0xa12acc8);
const loadLibrary=new NativeFunction(Process.getModuleByName('kernel32.dll').getExportByName('LoadLibraryW'),'pointer',['pointer']);
if(loadLibrary(Memory.allocUtf16String(DLL_PATH)).isNull())throw Error(t("原生界面加载失败","Native overlay failed to load"));
const dll=Process.getModuleByName('astral_bd_overlay.dll');
function exported(name,result,args){return new NativeFunction(dll.getExportByName(name),result,args);}
const render=exported('BDRender','void',['pointer']),command=exported('BDCommand','int',[]),
 status=exported('BDStatus','void',['pointer','int']),visible=exported('BDVisible','void',['int']),shutdown=exported('BDShutdown','void',[]),reward=exported('BDReward','void',['pointer','int']);
const isVisible=exported('BDIsVisible','int',[]),nativeEscape=exported('BDNativeEscape','int',[]),escapePending=exported('BDEscapePending','int',[]);
const uiSelection=exported('BDSelection','void',['int','int']);
const catalogs=CATALOG_DATA;
let recipes=catalogs[language].recipes,auras=catalogs[language].auras;
const nativeLanguage=exported('BDLanguage','void',['int']),clearCatalog=exported('BDCatalogClear','void',[]);
nativeLanguage(language==='en'?1:0);
let auraPlans=[],pendingPlans=null,planSaving=false;
const clearPlans=exported('BDAuraPlansClear','void',[]),addPlan=exported('BDAuraPlan','void',['int','pointer','pointer']),planName=exported('BDAuraPlanName','pointer',[]);
const addRecipe=exported('BDRecipe','void',['int','pointer','pointer']),addAura=exported('BDAura','void',['int','pointer','pointer','int','int']),auraSlots=exported('BDAuraSlots','void',['pointer']);
function populateCatalog(){
 recipes.forEach((r,i)=>addRecipe(i,Memory.allocUtf8String(r.name),Memory.allocUtf8String(r.description+'\n'+r.auraNames.join(' / '))));
 auras.forEach(a=>addAura(a.id,Memory.allocUtf8String(a.name),Memory.allocUtf8String(a.description),a.quality,a.elements));
}
populateCatalog();
function setLanguage(value){
 language=value;recipes=catalogs[language].recipes;auras=catalogs[language].auras;
 nativeLanguage(language==='en'?1:0);clearCatalog();populateCatalog();
 renderPlans({plans:auraPlans});uiSelectionRequested=true;growthUI();
 notify(t('界面已切换为简体中文。','Interface switched to English.'));send({event:'language',language});
}
function text(p){const f=p.readU8();return f&1?p.add(8).readPointer().readUtf8String(p.add(4).readU32()):p.add(1).readUtf8String(f>>1);}
function dictionary(rva){const o=b.add(rva).readPointer(),h=o.add(0x240).readPointer(),count=o.add(0x248).readU64().toNumber();let p=h.readPointer(),out={};for(let i=0;i<count;i++,p=p.readPointer())out[text(p.add(16))]=p.add(0x50);return out;}
function bits(v){const p=Memory.alloc(8);p.writeDouble(v);return p.readU64();}
const assign=new NativeFunction(b.add(0x63f9a0),'void',['pointer','pointer','uint']);
const refresh=new NativeFunction(b.add(0x1450440),'void',['pointer']);
const gambitRefresh=new NativeFunction(b.add(0x3582dc0),'uint64',['pointer','uint64','uint64']);
const checkpointSave=new NativeFunction(b.add(0x15fda50),'void',['pointer']);
function prepareCheckpoint(){
 if(b.add(0xc0b7ca0).readU32()<2)throw Error(t("当前房间存档点尚未准备好","The room checkpoint is not ready yet"));
 // 检查点缓存是在房间开始时生成的；仅同步当前 P1 装备，沿用原版检查点与写盘入口。
 const cached=b.add(0xc0b7cb0).readPointer().add(0x38).readPointer().add(0x40),snapshot=JSON.parse(text(cached));
 if(!snapshot.playerSpells||!snapshot.playerSpells.data)throw Error(t("检查点装备快照失效","Invalid checkpoint equipment snapshot"));
 const values=dictionary(0xc0d5cb0),data=snapshot.playerSpells.data;
 const keys=[1,2,3,4,5].map(s=>'P1_relic_'+s);
 for(let s=1;s<=4;s++)keys.push('P1_spell_'+s,'P1_spell_'+s+'_modificators');
 for(const key of keys)if(!(key in data)||!values[key])throw Error(t("检查点装备字段失效：","Invalid checkpoint equipment field: ")+key);
 return {cached,snapshot,keys,values};
}
function saveEquipment(checkpoint){
 const {cached,snapshot,keys,values}=checkpoint,data=snapshot.playerSpells.data;
 for(const key of keys)data[key]=values[key].readU8()===0?values[key].add(8).readDouble():text(values[key].add(8));
 const value=JSON.stringify(snapshot).replace(/[^\x00-\x7f]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
 assign(cached,Memory.allocUtf8String(value),value.length);state.add(0x1c95e0).writeDouble(1);checkpointSave(state);
}
let selected=null,mode='formed',enabled=true,freshRun=null,appliedRun=null,stopping=false;
let growth=null,restoration=null,tick=0,claimRequested=false;
let uiSelectionRequested=false;
let actionRequested=null;
let pendingEquipmentSave=false;
function equipmentCheckpoint(){
 // 大厅与起始平台没有房间检查点；装备刷新不依赖检查点。
 if(room()===0)return null;
 return prepareCheckpoint();
}
function commitEquipmentSave(checkpoint){
 if(checkpoint){saveEquipment(checkpoint);pendingEquipmentSave=false;}
 else pendingEquipmentSave=true;
}
function equipment(){const v=dictionary(0xc0d5cb0);return [1,2,3,4,5].map(s=>v['P1_relic_'+s].add(8).readDouble());}
function equipAura(slot,id){
 if(!Number.isInteger(slot)||slot<1||slot>5||id!==0&&!auras.some(a=>a.id===id))throw Error(t("光环或槽位无效","Invalid aura or slot"));
 if(b.add(0xc0dfa20).readU32()<2)throw Error(t("请先进入本轮游戏，再装备光环","Enter a run before equipping auras"));
 const checkpoint=equipmentCheckpoint(),v=checkpoint?checkpoint.values:dictionary(0xc0d5cb0),p=v['P1_relic_'+slot];
 p.add(8).writeDouble(id);refresh(state);commitEquipmentSave(checkpoint);
 notify(id?t('已立即装备「','Equipped ')+auras.find(a=>a.id===id).name+t('」至光环槽 ',' in aura slot ')+slot:t('已清空光环槽 ','Cleared aura slot ')+slot);
 send({event:'aura-equipped',slot,id,equipment:equipment()});
}
function renderPlans(document,error){
 if(error){planSaving=false;notify(error);return;}
 auraPlans=document.plans;clearPlans();
 auraPlans.forEach((p,i)=>addPlan(i,Memory.allocUtf8String(p.name),Memory.allocUtf8String(p.auras.map((id,slot)=>(slot+1)+': '+(id===0?t("空","Empty"):auras.find(a=>a.id===id)?.name||t('组件已失效（ID ','Unavailable aura (ID ')+id+t('）',')'))).join('\n'))));
 if(planSaving){planSaving=false;notify(t("光环方案已保存，可在「光环方案」页立即应用。","Aura plan saved. Apply it from the Aura Plans tab."));}
}
function saveAuraPlan(){
 if(planSaving)return;
 if(b.add(0xc0dfa20).readU32()<2)throw Error(t("请先进入本轮游戏，再保存当前光环","Enter a run before saving current auras"));
 planSaving=true;notify(t("正在保存光环方案…","Saving aura plan..."));send({event:'aura-plan-save',name:planName().readUtf8String(),auras:equipment(),language});
}
function applyAuraPlan(index){
 const plan=auraPlans[index];if(!plan)throw Error(t("光环方案不存在","Aura plan does not exist"));
 if(b.add(0xc0dfa20).readU32()<2)throw Error(t("请先进入本轮游戏，再应用光环方案","Enter a run before applying an aura plan"));
 for(const id of plan.auras)if(id!==0&&!auras.some(a=>a.id===id))throw Error(t('方案包含已失效的光环 ID：','Plan contains an unavailable aura ID: ')+id+t('。请重新保存方案。','. Save a new plan.'));
 const checkpoint=equipmentCheckpoint(),v=dictionary(0xc0d5cb0);
 for(let i=0;i<5;i++)if(!v['P1_relic_'+(i+1)]||v['P1_relic_'+(i+1)].readU8()!==0)throw Error(t("光环槽字段失效","Invalid aura slot field"));
 plan.auras.forEach((id,i)=>v['P1_relic_'+(i+1)].add(8).writeDouble(id));
 refresh(state);commitEquipmentSave(checkpoint);notify(t('已立即应用光环方案「','Applied aura plan: ')+plan.name+t('」。','.'));send({event:'aura-plan-applied',id:plan.id,equipment:equipment()});
}
function applyCurrent(index,value){
 if(!Number.isInteger(index)||!recipes[index])throw Error(t("配方编号无效","Invalid build index"));
 if(b.add(0xc0dfa20).readU32()<2)throw Error(t("请先进入本轮游戏，再装配 BD","Enter a run before equipping a build"));
 const checkpoint=equipmentCheckpoint();
 selected=index;mode=value;enabled=true;freshRun=state.add(0x1c4768).readDouble();
 apply(index);commitEquipmentSave(checkpoint);uiSelectionRequested=true;
 if(!checkpoint)notify(t('已立即装配「','Equipped ')+recipes[index].name+t('」。当前为大厅或起始平台；开始新局沿用此配方，进入房间后同步检查点。','. In the hub/start platform, equipment is saved at the next room checkpoint. Future runs use this build.'));
}
let lastVisible=false,pauseOwned=false,pauseStarted=0,resumeRequested=false,stopDeadline=null;
function gamePaused(){const list=b.add(0xc0db828).readPointer(),count=b.add(0xc0db830).readU32();for(let i=1;i<count;i++)if(list.add(i*16).readPointer().add(0x38).readPointer().add(0x890).readDouble()!==0)return true;return false;}
function syncPause(){
 const shown=!!isVisible();
 if(shown!==lastVisible){
  lastVisible=shown;
  if(shown){resumeRequested=false;if(!pauseOwned&&b.add(0xc0dfa20).readU32()>1&&b.add(0xc0db830).readU32()>1&&!gamePaused()&&!escapePending()){if(nativeEscape()){pauseOwned=true;pauseStarted=Date.now();}}}
  else if(pauseOwned)resumeRequested=true;
 }
 if(resumeRequested&&!shown&&!escapePending()&&Date.now()-pauseStarted>300){if(gamePaused())nativeEscape();pauseOwned=false;resumeRequested=false;}
 if(shown&&pauseOwned&&!gamePaused()&&!escapePending()&&Date.now()-pauseStarted>900){pauseOwned=false;visible(0);notify(t("原版暂停未响应，已收起界面。请先按 Esc 暂停，再按 F8 打开 BD 选择。","Pause did not respond; menu closed. Press Esc to pause, then F8 to open Builds."));}
}
const inputHooks=[],inputModules=new Set(),blockedPads=new Set();
function filterPad(index,output,shown){
 const buttons=output.add(4).readU16(),chord=(buttons&0x30)===0x30;
 if(shown||chord)blockedPads.add(index);
 if(!blockedPads.has(index))return;
 const moving=buttons||output.add(6).readU8()>30||output.add(7).readU8()>30||[8,10,12,14].some(offset=>Math.abs(output.add(offset).readS16())>8000);
 if(!shown&&!moving){blockedPads.delete(index);return;}
 output.add(4).writeByteArray(new Uint8Array(12));
}
const inputObserver=Process.attachModuleObserver({onAdded(module){
 if(!/^xinput.*\.dll$/i.test(module.name)||inputModules.has(module.base.toString()))return;
 const address=module.findExportByName('XInputGetState');if(!address)return;inputModules.add(module.base.toString());
 inputHooks.push(Interceptor.attach(address,{onEnter(a){this.index=a[0].toUInt32();this.output=a[1];this.fromGame=this.returnAddress.compare(b)>=0&&this.returnAddress.compare(b.add(Process.mainModule.size))<0;},onLeave(r){if(this.fromGame&&r.toUInt32()===0)filterPad(this.index,this.output,!!isVisible());}}));
}});
const jsonGet=new NativeFunction(b.add(0x499c1e0),'pointer',['pointer','pointer','pointer']),jsonOut=Memory.alloc(72);
function progress(path){jsonGet(b.add(0xc08c600).readPointer(),jsonOut,b.add(path));if(jsonOut.readU8()!==0)throw Error(t("房间进度字段失效","Invalid room progression field"));return jsonOut.add(8).readDouble();}
function room(){return progress(0xc43d250);}
function seed(){const p=dictionary(0xc068390)['global_val_masterSeed__progress'];if(!p||p.readU8()!==0)throw Error(t("局种子字段失效","Invalid run seed field"));return p.add(8).readDouble();}
function sameGrowthRun(){return growth&&growth.run===state.add(0x1c4768).readDouble()&&growth.seed===seed();}
function eligibility(){const reached=progress(0xc43c650)>(growth.baseWorld||1)?4:Math.max(0,room()-(growth.baseRoom||0));if(reached>(growth.available||0)){growth.available=reached;persist();}return growth.available||0;}
function persist(){send({event:'profile',profile:{selected,mode,enabled,appliedRun,growth}});}
function growthUI(){
 if(!enabled||!sameGrowthRun()){reward(Memory.allocUtf8String(''),0);return;}
 const names=[t("首个核心符文","first core gambit"),t("前两件核心光环","first two core auras"),t("其余三件光环","remaining three auras"),t("剩余核心符文","remaining core gambits")];
 if(growth.stage>=4){reward(Memory.allocUtf8String(t("成长补给已全部领取。","All growth rewards collected.")),0);return;}
 const available=eligibility()>=growth.stage+1;
 reward(Memory.allocUtf8String(t('下一件：','Next: ')+names[growth.stage]+t('。推进至第 ','; available after room ')+(growth.stage+1)+t(' 个房间后可领取，错过后仍保留。',' from selection. Unclaimed rewards remain available.')),available?1:0);
}
function prepareGambit(v,slot,id){
 const p=v['P1_spell_'+slot+'_modificators'];if(!p||p.readU8()!==1)throw Error(t("符文槽失效","Invalid gambit slot"));
 const old=text(p.add(8)),parts=old.split('*');
 if(parts.length!==5||parts[4][0]!=='1')throw Error(t("首个符文槽未解锁","The first gambit slot is locked"));
 parts[0]=String(id);return {p,slot,value:parts.join('*')};
}
function commitGambit(item){
 assign(item.p.add(8),Memory.allocUtf8String(item.value),item.value.length);gambitRefresh(state,bits(1),bits(item.slot));
}
function setGambit(v,slot,id){
 commitGambit(prepareGambit(v,slot,id));
}
function claim(){
 if(!enabled||!sameGrowthRun()||growth.stage>=4||eligibility()<growth.stage+1)return;
 const r=recipes[growth.recipe],v=dictionary(0xc0d5cb0),stage=growth.stage;
 const checkpoint=prepareCheckpoint();
 if(stage===0)setGambit(v,1,r.gambits[0]);
 else if(stage===3){const items=[2,3,4].map(s=>prepareGambit(v,s,r.gambits[s-1]));for(const item of items)commitGambit(item);}
 else{
  const ids=stage===1?r.auras.slice(0,2):r.auras.slice(2),slots=[1,2,3,4,5].filter(s=>v['P1_relic_'+s]&&v['P1_relic_'+s].readU8()===0&&v['P1_relic_'+s].add(8).readDouble()===0);
  if(slots.length<ids.length){notify(t('需要 ','Requires ')+ids.length+t(' 个空光环槽；请用光环自选页腾出槽位，再领取保留补给。',' empty aura slots. Clear slots in Custom Auras, then claim the retained reward.'));return;}
  ids.forEach((id,i)=>v['P1_relic_'+slots[i]].add(8).writeDouble(id));refresh(state);
 }
 saveEquipment(checkpoint);growth.stage++;persist();growthUI();notify(t("成长补给已领取，下一件会在后续房间保留。","Growth reward collected. The next reward remains available in later rooms."));send({event:'growth-claimed',stage:growth.stage,run:growth.run});
}
function notify(message,allowed=true){status(Memory.allocUtf8String(message),allowed?1:0);send({event:'status',message});}
function apply(index){
 const recipe=recipes[index],v=dictionary(0xc0d5cb0);
 const writes=[];
 if(mode==='formed')for(let slot=1;slot<=5;slot++)writes.push(['P1_relic_'+slot,recipe.auras[slot-1]||0]);
 for(let slot=1;slot<=4;slot++)writes.push(['P1_spell_'+slot,recipe.spells[slot-1]]);
 for(const [key] of writes)if(!v[key]||v[key].readU8()!==0)throw Error(t("装备字段失效：","Invalid equipment field: ")+key);
 for(let slot=1;slot<=4;slot++)if(!v['P1_spell_'+slot+'_modificators']||v['P1_spell_'+slot+'_modificators'].readU8()!==1)throw Error(t("符文字段失效","Invalid gambit field"));
 for(const [key,value] of writes)v[key].add(8).writeDouble(value);
 for(let slot=1;slot<=4;slot++){
  const slots=mode==='formed'?(recipe.gambitSlots?recipe.gambitSlots[slot-1]:[recipe.gambits[slot-1],0,0,0]):[0,0,0,0];
  const value=slots.map((id,i)=>id+(i?'x':'')).join('*')+'*'+(mode==='formed'&&recipe.gambitSlots?'1111':'1000');
  assign(v['P1_spell_'+slot+'_modificators'].add(8),Memory.allocUtf8String(value),value.length);
 }
 refresh(state);for(let slot=1;slot<=4;slot++)gambitRefresh(state,bits(1),bits(slot));
 appliedRun=freshRun;growth=mode==='growth'?{run:freshRun,seed:seed(),recipe:index,stage:0,available:0,baseRoom:room(),baseWorld:progress(0xc43c650)}:null;
 persist();growthUI();notify(mode==='growth'?recipe.name+t('：成长模式已开始。按 F8 查看和领取后续补给。',': growth mode started. Press F8 to view and claim rewards.'):t('已装配「','Equipped ')+recipe.name+t('」。本局不再重复发放；下一次新局仍使用此配方。','. Applied once this run. Future new runs use this build.'));
 send({event:'applied',recipe:index,run:freshRun});
}
const runHook=Interceptor.attach(b.add(0x31ddff0),{onLeave(){
 freshRun=state.add(0x1c4768).readDouble();
 if(enabled&&selected!==null){try{apply(selected);}catch(e){enabled=false;persist();notify(e.toString(),false);send({event:'error',error:e.toString()});}}
 else if(enabled){notify(t("本局使用原版装备。进入房间后可在此立即装配 BD。","This run uses your original loadout. Equip a build here during the run."));visible(1);}
}});
notify(t("进入本轮后，可立即装配 BD 或自选光环。","Enter a run to equip a build or custom auras immediately."));
visible(0);
const presentHook=Interceptor.attach(Process.getModuleByName('dxgi.dll').base.add(PRESENT_RVA),{
 onEnter(a){render(a[0]);},
 onLeave(){
  if(stopping){
   visible(0);syncPause();
   if(pauseOwned||resumeRequested||escapePending())return;
   if(stopDeadline===null){stopDeadline=Date.now()+150;return;}if(Date.now()<stopDeadline)return;
   presentHook.detach();runHook.detach();inputObserver.detach();for(const hook of inputHooks)hook.detach();shutdown();send({event:'stopped'});return;
  }
  syncPause();
  if(pendingPlans){const p=pendingPlans;pendingPlans=null;renderPlans(p.document,p.error);}
  if(restoration){const p=restoration;restoration=null;selected=p.selected;mode=p.mode;enabled=p.enabled;appliedRun=p.appliedRun;growth=p.growth;uiSelectionRequested=true;growthUI();}
  if(uiSelectionRequested){uiSelectionRequested=false;if(selected!==null)uiSelection(selected,mode==='growth'?1:0);}
  if(++tick%60===0){growthUI();if(b.add(0xc0dfa20).readU32()>1){auraSlots(Memory.allocUtf8String(equipment().map((id,i)=>(i+1)+': '+(auras.find(a=>a.id===id)?.name||t("空","Empty"))).join(' / ')));if(pendingEquipmentSave&&room()>0&&b.add(0xc0b7ca0).readU32()>=2){try{commitEquipmentSave(prepareCheckpoint());send({event:'equipment-checkpoint-synced'});}catch(e){pendingEquipmentSave=false;notify(e.toString());send({event:'action-error',error:e.toString()});}}}}
  if(actionRequested){const a=actionRequested;actionRequested=null;try{if(a.kind==='language')setLanguage(a.value);else if(a.kind==='aura')equipAura(a.slot,a.id);else if(a.kind==='plan')applyAuraPlan(a.index);else if(a.kind==='savePlan')saveAuraPlan();else applyCurrent(a.index,a.mode);}catch(e){notify(e.toString());send({event:'action-error',error:e.toString()});}}
  if(claimRequested){claimRequested=false;try{claim();}catch(e){enabled=false;persist();notify(e.toString(),false);send({event:'error',error:e.toString()});}}
  const c=command();if(!c)return;
  try{
   if(c===0x600000||c===0x600001)setLanguage(c===0x600001?'en':'zh-CN');
   else if(c===0x2000){enabled=false;selected=null;persist();growthUI();notify(t("Mod 已关闭。当前装备由原版游戏保留。","Mod disabled. The game retains the current loadout."));}
   else if(c===0x3000)claim();
   else if(c===0x500000)saveAuraPlan();
   else if(c>=0x510000&&c<0x520000)applyAuraPlan(c-0x510000);
   else if(c>=0x400000&&c<0x400000+5120){const a=c-0x400000;equipAura(Math.floor(a/1024)+1,a%1024);}
   else if((c>=1&&c<=recipes.length)||(c>=257&&c<257+recipes.length))applyCurrent((c-1)%256,c>=257?'growth':'formed');
  }catch(e){notify(e.toString());send({event:'action-error',error:e.toString()});}
 }
});
rpc.exports={language(value){if(value!=='en'&&value!=='zh-CN')throw Error('Unsupported language');actionRequested={kind:'language',value};},plans(document,error=null){pendingPlans={document,error};},saveplan(){actionRequested={kind:'savePlan'};},applyplan(index){actionRequested={kind:'plan',index};},stop(){stopping=true;},restore(profile){restoration=profile;},claim(){claimRequested=true;},equip(index,value='formed'){actionRequested={kind:'recipe',index,mode:value};},aura(slot,id){actionRequested={kind:'aura',slot,id};},select(index,value='formed'){selected=index;mode=value||'formed';enabled=true;uiSelectionRequested=true;},show(value){visible(value?1:0);},snapshot(){return{language,selected,mode,enabled,freshRun,appliedRun,growth,equipment:equipment(),paused:gamePaused(),pauseOwned,visible:!!isVisible()};}};
send({event:'ready',version:'2.6.4',modVersion:'1.0.0-beta.1',language});
