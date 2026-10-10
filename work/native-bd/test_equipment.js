// 使用运行时原函数验证读取与刷新；不连接游戏、不写装备。
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(__dirname+'/runtime.js','utf8');
let values={},events=[],labels=[];
const context=vm.createContext({dictionary:()=>values,L:{equipment:0},text:p=>p.value,
 Number,Error,JSON,Memory:{allocUtf8String:s=>s},auraSlots:s=>labels.push(s),
 auras:[],t:(zh,en)=>en,send:e=>events.push(e)});
vm.runInContext(source.slice(source.indexOf('class AuraSlotError'),source.indexOf('function equipAura')),context);
const numeric=n=>({readU8:()=>0,add:()=>({readDouble:()=>n})});
const string=s=>({readU8:()=>1,add:()=>({value:s})});
function all(){values=Object.fromEntries([1,2,3,4,5].map(s=>['P1_relic_'+s,numeric(0)]));}
all();assert.equal(JSON.stringify(vm.runInContext('equipment()',context)),'[0,0,0,0,0]');
// 每一个槽位缺失、原生空字符串和未知类型均不可写；显示错误不得退出。
for(let slot=1;slot<=5;slot++)for(const value of [undefined,string(''),string('123'),{readU8:()=>9}]){
 all();if(value===undefined)delete values['P1_relic_'+slot];else values['P1_relic_'+slot]=value;
 assert.throws(()=>vm.runInContext('equipment()',context),/Aura slot unavailable/);
 assert.doesNotThrow(()=>vm.runInContext('updateAuraSlots()',context));
}
all();values.P1_relic_1=numeric(-1);assert.throws(()=>vm.runInContext('equipment()',context),/Aura slot unavailable/);
const before=events.length;vm.runInContext('updateAuraSlots();updateAuraSlots()',context);assert.equal(events.length,before+1);
all();vm.runInContext('updateAuraSlots()',context);assert.equal(events.at(-1).event,'equipment-ready');
// 其他内存/字典错误仍明确失败，不被槽位状态处理吞掉。
context.dictionary=()=>{throw Error('Invalid dictionary layout');};
assert.throws(()=>vm.runInContext('updateAuraSlots()',context),/Invalid dictionary layout/);
console.log('PASS: five-slot lifecycle, diagnostics, recovery and error boundaries');
