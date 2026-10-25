'use strict';
const A=EduAnalytics,DATA=EDU_DATA,keys=A.keys;
const labels=['Education spending · % GDP','Tertiary enrolment · gross %','Youth unemployment · %','GDP per capita · PPP 2021 $'];
const codes=['SE.XPD.TOTL.GD.ZS','SE.TER.ENRR','SL.UEM.1524.ZS','NY.GDP.PCAP.PP.KD'];
const colors=['#65e1c8','#8e9dff','#f0b56b','#f38ba8','#55b8ea','#bf91df','#acd77c','#ecdc8d','#81b1a1','#d78b72'];
const names=[...new Set(DATA.map(r=>r.country))].sort();
const el=id=>document.getElementById(id),fmt=v=>A.valid(v)?v.toLocaleString('en',{maximumFractionDigits:2}):'No data';
const opt=(value,label)=>{let o=document.createElement('option');o.value=value;o.textContent=label;return o;};
const label=k=>labels[keys.indexOf(k)];
let state;
const base={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:'-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif',color:'#c3d0e2',size:11},margin:{l:55,r:25,t:30,b:70},autosize:true,xaxis:{gridcolor:'rgba(255,255,255,.1)',zeroline:false},yaxis:{gridcolor:'rgba(255,255,255,.1)',zeroline:false},legend:{orientation:'h',y:-.2},colorway:colors};
const config={responsive:true,displaylogo:false,modeBarButtonsToRemove:['select2d','lasso2d'],topojsonURL:'./geo/'};
function plot(id,traces,layout={}){return Plotly.react(id,traces,{...base,...layout},config);}
function blank(id,message){plot(id,[],{annotations:[{text:message,x:.5,y:.5,xref:'paper',yref:'paper',showarrow:false}],xaxis:{visible:false},yaxis:{visible:false}});}
function selected(){return [...document.querySelectorAll('#countries input:checked')].map(n=>n.value);}
function params(){return {countries:selected(),start:+el('start').value,end:+el('end').value,year:+el('year').value,indicator:el('indicator').value,mode:el('mode').value};}
function metric(title,value,sub){const d=document.createElement('div');d.className='metric';const l=document.createElement('div');l.className='label';l.textContent=title;const v=document.createElement('strong');v.textContent=value;const s=document.createElement('small');s.textContent=sub;d.append(l,v,s);return d;}
function render(){
 const p=params();let r;try{r=A.analyze(DATA,p.countries,p.start,p.end,p.indicator,p.mode,p.year);el('error').textContent='';}catch(e){el('error').textContent=e.message;return;}
 state={...p,...r};
 el('metrics').replaceChildren(metric('SELECTED COUNTRIES',p.countries.length,'Of 10 countries in the sample'),metric('YEAR WINDOW',`${p.start}–${p.end}`,'Annual observations'),metric('INDICATOR COVERAGE',`${r.coverage.toFixed(1)}%`,`${r.count} / ${r.expected} expected values`),metric('SAMPLE MEDIAN',fmt(r.median),`${r.snap.length} countries with valid values`));
 const lead=r.snap.slice().sort((a,b)=>b[p.indicator]-a[p.indicator])[0];
 el('summary').textContent=(p.mode==='latest'?'Latest valid observation per country; observation years may differ.':`Same-year comparison: ${p.year}.`)+` This is a selected-country sample, not a global estimate.`+(lead?` Highest observed ${label(p.indicator)}: ${lead.country}, ${fmt(lead[p.indicator])} (${lead.year}). Higher does not necessarily mean better.`:' No valid observations for this selection.');
 if(r.snap.length){
 plot('map',[{type:'choropleth',locations:r.snap.map(d=>d.iso3),z:r.snap.map(d=>d[p.indicator]),text:r.snap.map(d=>`${d.country} · ${d.year}`),colorscale:[[0,'#244d56'],[1,'#74efc7']],colorbar:{thickness:10,len:.6},hovertemplate:'%{text}<br>%{z:,.2f}<extra></extra>'}],{geo:{projection:{type:'natural earth'},bgcolor:'#111b2b',showland:true,landcolor:'#26364a',showcountries:true,countrycolor:'#5a6a7c',showframe:false,showcoastlines:false},margin:{l:0,r:0,t:15,b:0}});
 const sorted=r.snap.slice().sort((a,b)=>a[p.indicator]-b[p.indicator]);
 plot('ranking',[{type:'bar',orientation:'h',x:sorted.map(d=>d[p.indicator]),y:sorted.map(d=>d.country),customdata:sorted.map(d=>d.year),marker:{color:'#65e1c8'},hovertemplate:'%{y} · %{customdata}<br>%{x:,.2f}<extra></extra>'}],{margin:{l:105,r:25,t:20,b:70},xaxis:{...base.xaxis,title:{text:label(p.indicator)}}});
 }else{blank('map','Select countries with available data');blank('ranking','No valid observations');}
 const years=Array.from({length:p.end-p.start+1},(_,i)=>p.start+i);
 plot('trends',p.countries.map(c=>({type:'scatter',mode:'lines+markers',name:c,x:years,y:years.map(y=>r.period.find(d=>d.country===c&&d.year===y)?.[p.indicator]??null),connectgaps:false,marker:{size:5}})),{yaxis:{...base.yaxis,title:{text:label(p.indicator)}},xaxis:{...base.xaxis,dtick:2}});
 plot('heatmap',[{type:'heatmap',x:years,y:p.countries,z:p.countries.map(c=>years.map(y=>A.valid(r.period.find(d=>d.country===c&&d.year===y)?.[p.indicator])?1:0)),zmin:0,zmax:1,colorscale:[[0,'#a64e68'],[1,'#54cbae']],xgap:3,ygap:4,colorbar:{tickvals:[0,1],ticktext:['Missing','Available'],thickness:10},hovertemplate:'%{y} · %{x}<br>Available: %{z}<extra></extra>'}],{margin:{l:110,r:100,t:25,b:45},yaxis:{autorange:'reversed'}});
 const table=document.createElement('table'),head=document.createElement('tr');['Country','ISO3','Observation year',label(p.indicator)].forEach(t=>{let th=document.createElement('th');th.textContent=t;head.append(th);});table.append(head);
 r.snap.forEach(d=>{let tr=document.createElement('tr');[d.country,d.iso3,d.year,fmt(d[p.indicator])].forEach(t=>{let td=document.createElement('td');td.textContent=t;tr.append(td);});table.append(tr);});el('table').replaceChildren(table);
 renderScatter();renderProfile();resize();
}
function renderScatter(){if(!state)return;const x=el('scatterx').value;const clean=state.period.filter(d=>d.year===state.year&&[x,keys[2],keys[3]].every(k=>A.valid(d[k]))&&d[keys[3]]>0);
 if(!clean.length)blank('scatter','No complete same-year records; try another year');else plot('scatter',clean.map(d=>({type:'scatter',mode:'markers',name:d.country,x:[d[x]],y:[d[keys[2]]],marker:{size:[d[keys[3]]],sizemode:'area',sizeref:2*Math.max(...clean.map(d=>d[keys[3]]))/(48**2),sizemin:5,line:{width:1,color:'#e5fff8'}},text:[`${d.country} · ${d.year}<br>GDP per capita: ${fmt(d[keys[3]])}`],hovertemplate:'%{text}<br>X: %{x:,.2f}<br>Youth unemployment: %{y:,.2f}%<extra></extra>'})),{xaxis:{...base.xaxis,title:{text:label(x)}},yaxis:{...base.yaxis,title:{text:labels[2]}}});
 el('scatter-note').textContent=`Common year: ${state.year} · ${clean.length} of ${state.countries.length} selected countries included; ${state.countries.length-clean.length} excluded for missing coordinates or nonpositive GDP.`;
}
function renderProfile(){if(!state)return;const c=el('profile').value,years=Array.from({length:state.end-state.start+1},(_,i)=>state.start+i),rows=DATA.filter(d=>d.country===c&&d.year>=state.start&&d.year<=state.end).sort((a,b)=>a.year-b.year);el('profile-metrics').replaceChildren();
 keys.forEach((k,i)=>{let valid=rows.filter(d=>A.valid(d[k])),box=document.createElement('div'),title=document.createElement('small');title.textContent=labels[i];box.append(title);if(valid.length){const a=valid[0],b=valid[valid.length-1],v=document.createElement('strong');v.textContent=`${fmt(b[k])} (${b.year})`;box.append(v);let change=document.createElement('small');let delta=i===3&&a[k]!==0?(b[k]/a[k]-1)*100:b[k]-a[k];change.textContent=valid.length>1?`${delta>=0?'+':''}${fmt(delta)} ${i===3?(a[k]===0?'international $':'%'):'pp'} · ${a.year}–${b.year}`:'Insufficient observations for change';box.append(change);}else box.append(document.createTextNode('No data'));el('profile-metrics').append(box);
 plot('profile'+i,[{type:'scatter',mode:'lines+markers',x:years,y:years.map(y=>rows.find(d=>d.year===y)?.[k]??null),line:{color:colors[i]},connectgaps:false}],{title:{text:labels[i],font:{size:13}},showlegend:false,xaxis:{...base.xaxis,dtick:4}});});}
function resize(){setTimeout(()=>document.querySelectorAll('.panel.active .js-plotly-plot').forEach(d=>Plotly.Plots.resize(d)),50);}
function tab(id){document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id===id));document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('active',b.dataset.tab===id));resize();}
function csv(){if(!state)return;let cols=Object.keys(DATA[0]),rows=state.period;const escape=v=>'"'+String(v??'').replaceAll('"','""')+'"';const content=[cols,...rows.map(r=>cols.map(c=>r[c]))].map(r=>r.map(escape).join(',')).join('\r\n');let url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=`edu_future_${state.start}_${state.end}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
names.forEach(c=>{let l=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=c;input.checked=true;l.append(input,document.createTextNode(c));el('countries').append(l);el('profile').append(opt(c,c));});el('profile').value='Zimbabwe';
keys.forEach((k,i)=>el('indicator').append(opt(k,labels[i])));keys.slice(0,2).forEach((k,i)=>el('scatterx').append(opt(k,labels[i])));
for(let y=2010;y<=2023;y++)['start','end','year'].forEach(id=>el(id).append(opt(y,y)));el('end').value=el('year').value=2023;
codes.forEach((c,i)=>{let li=document.createElement('li'),a=document.createElement('a');a.href='https://data.worldbank.org/indicator/'+c;a.target='_blank';a.rel='noopener';a.textContent=labels[i]+' · '+c;li.append(a);el('sources').append(li);});
el('update').onclick=render;el('all').onclick=()=>document.querySelectorAll('#countries input').forEach(d=>d.checked=true);el('clear').onclick=()=>document.querySelectorAll('#countries input').forEach(d=>d.checked=false);el('scatterx').onchange=renderScatter;el('profile').onchange=()=>{renderProfile();resize();};el('export').onclick=csv;document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>tab(b.dataset.tab));document.querySelector('header a[href="#methodology"]').onclick=()=>tab('methodology');window.addEventListener('resize',resize);
if(typeof Plotly==='undefined'){el('error').textContent='Chart library could not load. Refresh the page.';}else render();
