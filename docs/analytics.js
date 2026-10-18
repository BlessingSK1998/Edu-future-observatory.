(function(root){
 const keys=['education_expenditure_pct_gdp','tertiary_enrolment_pct_gross','youth_unemployment_pct','gdp_per_capita_ppp_constant_2021_intl_dollars'];
 const valid=v=>typeof v==='number'&&Number.isFinite(v);
 function median(values){let a=values.filter(valid).sort((a,b)=>a-b),n=a.length;return n?(n%2?a[(n-1)/2]:(a[n/2-1]+a[n/2])/2):null;}
 function analyze(data,countries,start,end,indicator,mode,year){
  if(start>end)throw Error('Start year must be no later than end year.');
  if(mode==='same'&&(year<start||year>end))throw Error('Snapshot year must be within the selected window.');
  const period=data.filter(r=>countries.includes(r.country)&&r.year>=start&&r.year<=end);
  const snap=countries.map(c=>period.filter(r=>r.country===c&&valid(r[indicator])&&(mode==='latest'||r.year===year)).sort((a,b)=>b.year-a.year)[0]).filter(Boolean);
  const expected=countries.length*(end-start+1),count=period.filter(r=>valid(r[indicator])).length;
  return {period,snap,expected,count,coverage:expected?count/expected*100:0,median:median(snap.map(r=>r[indicator]))};
 }
 root.EduAnalytics={keys,valid,median,analyze};
})(typeof module==='object'?module.exports:globalThis);
