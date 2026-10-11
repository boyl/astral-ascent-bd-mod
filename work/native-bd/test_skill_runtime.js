// 执行生产装配和成长函数；模拟原生字段，避免修改用户存档。
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(__dirname+'/runtime.js','utf8');
const recipes=JSON.parse(fs.readFileSync(__dirname+'/recipes.json','utf8'));
class Field{
 constructor(type,value){this.type=type;this.value=value;}
 readU8(){return this.type;} add(){return this;} readDouble(){return this.value;} writeDouble(v){this.value=v;}
}
let fields,events,saves,icons,refreshCalls;
function reset(){
 fields={};events=[];saves=0;icons=[160,160,160,160].map(id=>new Field(0,id));refreshCalls=[];
 for(let s=1;s<=5;s++)fields['P1_relic_'+s]=new Field(0,0);
 for(let s=1;s<=4;s++){fields['P1_spell_'+s]=new Field(0,0);fields['P1_spell_'+s+'_modificators']=new Field(1,'0*0x*0x*0x*1000');}
}
const context=vm.createContext({recipes,L:{equipment:0},state:{},freshRun:10,
 dictionary:()=>fields,requireFrame:()=>({}),text:p=>p.value,
 assign:(p,value)=>{p.value=value;},Memory:{allocUtf8String:s=>s},
 spellIcons:()=>icons,refresh:()=>{},gambitRefresh:(state,player,slot)=>{assert.equal(player,1);assert.ok(slot>=1&&slot<=4);refreshCalls.push(slot);},
 seed:()=>123,room:()=>1,progress:()=>1,persist:()=>{},growthUI:()=>{},
 sameGrowthRun:()=>true,eligibility:()=>4,prepareCheckpoint:()=>({}),saveEquipment:()=>saves++,
 notify:()=>{},send:m=>events.push(m),t:(zh,en)=>en,Number,Error});
vm.runInContext('var mode="formed",enabled=true,selected=null,growth=null,appliedRun=null;',context);
vm.runInContext(source.slice(source.indexOf('function prepareGambit('),source.indexOf('function notify(')),context);
vm.runInContext(source.slice(source.indexOf('function apply(index)'),source.indexOf('const frameHook')),context);
function rowString(row){return `${row[0]}*${row[1]}x*${row[2]}x*${row[3]}x*1111`;}
// 捕获真实声明，避免模拟函数掩盖 Windows x64 浮点参数契约错误。
const abi=[];vm.runInNewContext(source.match(/const gambitRefresh=new NativeFunction[^;]+;/)[0],{b:{add:x=>x},L:{gambitRefresh:1},NativeFunction:function(address,result,args){abi.push({result,args});}});
assert.equal(abi[0].result,'double');assert.deepEqual(Array.from(abi[0].args),['pointer','double','double']);
reset();const beforeUnavailable=JSON.stringify(fields);const realIcons=context.spellIcons;
context.spellIcons=()=>{throw Error('Four spell icons are not ready');};
assert.throws(()=>vm.runInContext('apply(0)',context),/icons are not ready/);
assert.equal(JSON.stringify(fields),beforeUnavailable);context.spellIcons=realIcons;
// 同一进程状态连续切换，绝不能每次 reset 后再验证。
reset();context.mode='formed';
for(const index of [...Array(12).keys(),...Array(12).keys()].reverse()){
 vm.runInContext(`apply(${index})`,context);
 assert.deepEqual(icons.map(p=>p.value),recipes[index].spells);
 assert.deepEqual(refreshCalls.slice(-4),[1,2,3,4]);
}
for(let index=0;index<12;index++){
 const recipe=recipes[index];reset();context.mode='formed';vm.runInContext(`apply(${index})`,context);
 for(let s=1;s<=5;s++)assert.equal(fields['P1_relic_'+s].value,recipe.auras[s-1]);
 for(let s=1;s<=4;s++){
  assert.equal(fields['P1_spell_'+s].value,recipe.spells[s-1]);
  assert.equal(fields['P1_spell_'+s+'_modificators'].value,rowString(recipe.gambitSlots[s-1]));
 }
 reset();context.mode='growth';vm.runInContext(`apply(${index})`,context);
 assert.deepEqual([1,2,3,4,5].map(s=>fields['P1_relic_'+s].value),[0,0,0,0,0]);
 vm.runInContext('claim()',context);
 assert.equal(fields.P1_spell_1_modificators.value,rowString(recipe.gambitSlots[0]));
 vm.runInContext('claim();claim();claim()',context);
 for(let s=1;s<=5;s++)assert.equal(fields['P1_relic_'+s].value,recipe.auras[s-1]);
 for(let s=1;s<=4;s++)assert.equal(fields['P1_spell_'+s+'_modificators'].value,rowString(recipe.gambitSlots[s-1]));
 assert.equal(saves,4);assert.equal(context.growth.stage,4);
}
// 领取前发现未解锁首槽，必须失败且不写入其他符文。
reset();fields.P1_spell_2_modificators.value='0*0x*0x*0x*0000';context.growth={recipe:0,stage:3};
assert.throws(()=>vm.runInContext('claim()',context),/first gambit slot is locked/);
assert.equal(fields.P1_spell_3_modificators.value,'0*0x*0x*0x*1000');
// 同一份运行时中的光环自选与方案应用必须保留四个法术及其完整符文。
context.b={add:()=>({readU32:()=>2})};
context.auras=JSON.parse(fs.readFileSync(__dirname+'/auras.json','utf8'));
context.auraSlots=()=>{};context.equipmentCheckpoint=()=>null;context.commitEquipmentSave=()=>{};
vm.runInContext(source.slice(source.indexOf('class AuraSlotError'),source.indexOf('function applyCurrent')),context);
reset();context.mode='formed';vm.runInContext('apply(0)',context);
const spellState=()=>JSON.stringify([1,2,3,4].map(s=>[fields['P1_spell_'+s].value,fields['P1_spell_'+s+'_modificators'].value]));
const originalSpells=spellState();
vm.runInContext('equipAura(3,144)',context);assert.equal(fields.P1_relic_3.value,144);assert.equal(spellState(),originalSpells);
context.auraPlans=[{id:'test',name:'test',auras:[144,294,144,294,0]}];
vm.runInContext('applyAuraPlan(0)',context);assert.equal(spellState(),originalSpells);
assert.deepEqual([1,2,3,4,5].map(s=>fields['P1_relic_'+s].value),[144,294,144,294,0]);
console.log('PASS: 24 consecutive replacements + 12 formed + 12 growth, native ABI and current definitions, aura regression');
