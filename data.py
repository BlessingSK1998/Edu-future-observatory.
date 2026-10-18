"""World Bank WDI acquisition and strict panel validation."""
from pathlib import Path
from datetime import datetime, timezone
import json, urllib.request
import pandas as pd

BASE = Path(__file__).resolve().parent
CSV = BASE / 'global_education_employment_2010_2023.csv'
COUNTRIES = {'BWA':'Botswana','DEU':'Germany','GHA':'Ghana','IND':'India','KEN':'Kenya','NGA':'Nigeria','ZAF':'South Africa','GBR':'United Kingdom','USA':'United States','ZWE':'Zimbabwe'}
INDICATORS = {
 'education_expenditure_pct_gdp': ('SE.XPD.TOTL.GD.ZS','Education spending · % GDP'),
 'tertiary_enrolment_pct_gross': ('SE.TER.ENRR','Tertiary enrolment · gross %'),
 'youth_unemployment_pct': ('SL.UEM.1524.ZS','Youth unemployment · %'),
 'gdp_per_capita_ppp_constant_2021_intl_dollars': ('NY.GDP.PCAP.PP.KD','GDP per capita · PPP 2021 $'),
}

def download():
    panel = pd.MultiIndex.from_product([COUNTRIES,range(2010,2024)],names=['iso3','year']).to_frame(index=False)
    panel['country'] = panel.iso3.map(COUNTRIES)
    metadata = {'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sources':{}}
    for column,(code,label) in INDICATORS.items():
        url = f'https://api.worldbank.org/v2/country/{";".join(COUNTRIES)}/indicator/{code}?date=2010:2023&format=json&per_page=20000'
        with urllib.request.urlopen(url,timeout=60) as response:
            payload=json.load(response)
        if not isinstance(payload,list) or len(payload)!=2 or not payload[1]:
            raise RuntimeError(f'World Bank returned no records for {code}')
        if int(payload[0]['pages'])!=1:
            raise RuntimeError('Unexpected pagination: refusing partial data')
        records=pd.DataFrame([{'iso3':r['countryiso3code'],'year':int(r['date']),column:r['value']} for r in payload[1]])
        panel=panel.merge(records,on=['iso3','year'],how='left',validate='one_to_one')
        metadata['sources'][column]={'indicator':code,'label':label,'url':url,'last_updated':payload[0].get('lastupdated')}
    panel['retrieved_date']=metadata['retrieved_utc'][:10]
    panel.to_csv(CSV,index=False)
    (BASE/'provenance.json').write_text(json.dumps(metadata,indent=2))
    return validate(panel)

def validate(df):
    required=['country','iso3','year',*INDICATORS]
    missing=set(required)-set(df.columns)
    if missing:raise ValueError(f'Missing columns: {sorted(missing)}')
    df=df.copy()
    years=pd.to_numeric(df.year,errors='raise')
    if years.isna().any() or (years%1!=0).any():raise ValueError('Years must be whole numbers')
    df['year']=years.astype(int)
    if df[['country','iso3']].isna().any().any():raise ValueError('Missing country identifiers')
    if df.duplicated(['iso3','year']).any():raise ValueError('Duplicate country-year records')
    if df.groupby('iso3').country.nunique().gt(1).any() or df.groupby('country').iso3.nunique().gt(1).any():raise ValueError('Inconsistent country identifiers')
    for col in INDICATORS:
        df[col]=pd.to_numeric(df[col],errors='raise')
        if (df[col].dropna()<0).any() or df[col].isin([float('inf'),float('-inf')]).any():raise ValueError(f'Invalid values: {col}')
    if df.youth_unemployment_pct.dropna().gt(100).any():raise ValueError('Unemployment exceeds 100%')
    return df.sort_values(['country','year']).reset_index(drop=True)

def load():
    if not CSV.exists():return download()
    return validate(pd.read_csv(CSV))

if __name__=='__main__':
    d=download();print(f'Downloaded {len(d)} country-year rows; {len(COUNTRIES)} countries')
