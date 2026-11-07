// Testa google_planilhas/Codigo.gs simulando o Google Planilhas.
// Rode: node tests/teste_planilha.js google_planilhas/Codigo.gs
const fs = require('fs'); const vm = require('vm'); const assert = require('assert');
const TZ = 'America/Sao_Paulo';
class Aba { constructor(n){this.n=n;this.d=[];}
  getDataRange(){const s=this;return{getValues:()=>s.d.map(r=>r.slice())}}
  getLastRow(){return this.d.length}
  getRange(r,c,nr,nc){const s=this;return{
    setValues(v){v.forEach((row,i)=>{s.d[r-1+i]=s.d[r-1+i]||[];row.forEach((x,j)=>s.d[r-1+i][c-1+j]=x)})},
    getValues(){return s.d.slice(r-1,r-1+nr).map(row=>row.slice(c-1,c-1+nc))}}}
  setFrozenRows(){} deleteRow(i){this.d.splice(i-1,1)} }
const abas={};
const planilha={getSheetByName:n=>abas[n]||null,insertSheet:n=>(abas[n]=new Aba(n)),getSpreadsheetTimeZone:()=>TZ};
function fmt(d,tz,p){const o=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',weekday:'short',hourCycle:'h23'}).formatToParts(d).map(x=>[x.type,x.value]));
  if(p==='u')return String(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].indexOf(o.weekday)+1);
  if(p==='yyyy-MM-dd')return `${o.year}-${o.month}-${o.day}`;
  return `${o.day}/${o.month}/${o.year} às ${o.hour}:${o.minute}`;}
const ctx={SpreadsheetApp:{getActive:()=>planilha},LockService:{getScriptLock:()=>({waitLock(){},releaseLock(){}})},
 Utilities:{formatDate:fmt},ContentService:{MimeType:{JSON:1},createTextOutput:t=>({t,setMimeType(){return this}})},JSON,Math,Date,Object,Array,Number,String};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2],'utf8').replace("'TROQUE-ESTA-CHAVE';","'abc123';"),ctx);
const post=(b,ch='abc123')=>JSON.parse(ctx.doPost({parameter:{chave:ch},postData:{contents:JSON.stringify(b)}}).t);
const lote={timestamp:'x',app_version:'1',timezone:TZ,
 steps:[{count:8000,start_time:'2026-11-02T00:00:00-03:00',end_time:'2026-11-03T00:00:00-03:00'},
        {count:3000,start_time:'2026-11-07T08:00:00-03:00',end_time:'2026-11-07T09:00:00-03:00',metadata:{id:'s1'}},
        {count:500,start_time:'2026-11-07T01:30:00Z',end_time:'2026-11-07T02:00:00Z'}], // 06/11 22:30 local
 heart_rate:[{bpm:70,time:'2026-11-07T10:00:00-03:00'},{bpm:66,time:'2026-11-07T11:30:00-03:00'}],
 exercise:[{type:'WALKING',start_time:'2026-11-06T18:00:00-03:00',end_time:'x',duration_seconds:2700,distance_meters:3500}],
 sleep:[{session_end_time:'2026-11-07T06:30:00-03:00',duration_seconds:27000,stages:[]}]};
assert.deepStrictEqual(post(lote,'errada'),{ok:false,erro:'chave inválida'});
assert.strictEqual(post(lote).ok,true);
// reenvio + edição do s1 não duplica
lote.steps[1].count=3210; post(lote);
assert.strictEqual(abas.steps.d.length,4);
const r=JSON.parse(ctx.doGet({parameter:{chave:'abc123'}}).t.replace(/^/,'')) && JSON.parse(ctx.resumo_ ? JSON.stringify(vm.runInContext("resumo_(new Date('2026-11-07T12:00:00-03:00'))",ctx)) : '{}');
console.log(JSON.stringify(r,null,1));
assert.strictEqual(r.passos_hoje,3210);
assert.strictEqual(r.passos_semana,8000+500+3210);
assert.strictEqual(r.ultima_frequencia_cardiaca.bpm,66);
assert.strictEqual(r.ultima_atividade.minutos,45);
assert.strictEqual(r.ultimo_sono.horas,7.5);
post({timestamp:'x',deleted:[{type:'steps',id:'s1'}]});
assert.strictEqual(abas.steps.d.length,3);
console.log('TUDO OK');
