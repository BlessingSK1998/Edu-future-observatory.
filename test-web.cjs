const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const base=fs.existsSync('dist')?'dist':fs.existsSync('docs')?'docs':'.';
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync(base+'/analytics.js','utf8'),ctx);vm.runInContext(fs.readFileSync(base+'/data.js','utf8'),ctx);
const {analyze,median,keys}=ctx.EduAnalytics,data=ctx.EDU_DATA,names=[...new Set(data.map(r=>r.country))];
assert.equal(data.length,140);assert.equal(names.length,10);assert.equal(median([1,3,8,10]),5.5);
for(const indicator of keys)for(const mode of ['latest','same']){const r=analyze(data,names,2010,2023,indicator,mode,2023);assert.ok(r.coverage>=0&&r.coverage<=100);assert.equal(r.expected,140);assert.ok(r.snap.every(d=>Number.isFinite(d[indicator])));if(mode==='same')assert.ok(r.snap.every(d=>d.year===2023));}
let r=analyze(data,names,2010,2023,keys[0],'latest',2023);assert.equal(r.count,112);assert.equal(r.coverage,80);assert.equal(r.snap.length,10);
assert.equal(analyze(data,[],2010,2023,keys[0],'latest',2023).snap.length,0);
assert.throws(()=>analyze(data,names,2023,2010,keys[0],'same',2023));
assert.throws(()=>analyze(data,names,2010,2020,keys[0],'same',2023));
const synthetic=[{country:'X',year:2021,[keys[0]]:1},{country:'X',year:2023,[keys[0]]:null}];r=analyze(synthetic,['X'],2021,2023,keys[0],'latest',2023);assert.equal(r.snap[0].year,2021);assert.equal(r.expected,3);assert.equal(r.count,1);
JSON.parse(fs.readFileSync(base+'/geo/world_110m.json','utf8'));assert.ok(fs.statSync(base+'/plotly.min.js').size>1000000);
console.log('Web checks passed: 140 records, all indicators/modes, latest years, coverage, empty/invalid filters, bundled assets.');
