"""EDU / FUTURE — education and employment observatory."""
from pathlib import Path
import html, tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import load, INDICATORS

LABELS={k:v[1] for k,v in INDICATORS.items()}
GDP=list(INDICATORS)[3]
YOUTH='youth_unemployment_pct'
CSS='''
.gradio-container {max-width:1480px!important;background:#080f1d!important;color:#dce6f5!important;}
.hero {padding:36px;border:1px solid #26364e;border-radius:18px;background:linear-gradient(120deg,#142a42,#101829);margin-bottom:20px;}
.hero h1 {font-size:42px;margin:8px 0;color:#f0f9ff;letter-spacing:-1.5px;}
.eyebrow {color:#56dfd0;letter-spacing:3px;font-size:12px;font-weight:700;}
.cards {display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0;}
.card {padding:20px;border:1px solid #283b52;border-radius:12px;background:#111e30;}
.card small {color:#a5b8ce;}.card strong {display:block;color:#65e1d3;font-size:27px;margin:6px 0;}
@media(max-width:700px){.cards{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:30px}}
'''

def style(fig,title=None):
    fig.update_layout(template='plotly_dark',paper_bgcolor='#101c2d',plot_bgcolor='#101c2d',font=dict(family='Arial',color='#dce6f5'),margin=dict(l=35,r=25,t=65,b=45),height=440,title=title)
    return fig

def empty(message):
    f=go.Figure();f.add_annotation(text=message,x=.5,y=.5,xref='paper',yref='paper',showarrow=False);return style(f)

def snapshot(period,indicator,latest,year):
    if latest:return period.dropna(subset=[indicator]).sort_values('year').groupby('country',as_index=False).tail(1)
    return period[period.year==year].dropna(subset=[indicator])

def analyze(df,countries,start,end,indicator,latest,year,x):
    countries=[c for c in (countries or []) if c in set(df.country)]
    start,end,year=int(start),int(end),int(year)
    if start>end:raise ValueError('Start year must be no later than end year.')
    if not latest and not start<=year<=end:raise ValueError('Snapshot year must be within the selected window.')
    period=df[df.country.isin(countries)&df.year.between(start,end)]
    snap=snapshot(period,indicator,latest,year)
    expected=len(countries)*(end-start+1)
    valid=int(period[indicator].notna().sum())
    coverage=100*valid/expected if expected else 0
    med=f'{snap[indicator].median():,.2f}' if len(snap) else '—'
    cards='<div class="cards">'+''.join(f'<div class="card"><small>{a}</small><strong>{b}</strong><small>{c}</small></div>' for a,b,c in [
        ('COUNTRIES',len(countries),'Selected comparison sample'),('WINDOW',f'{start}–{end}','Annual observations'),('INDICATOR COVERAGE',f'{coverage:.1f}%',f'{valid} / {expected} expected values'),('SAMPLE MEDIAN',med,f'{len(snap)} countries with valid values')])+'</div>'
    mode='Latest valid value per country; observation years may differ.' if latest else f'Same-year comparison: {year}.'
    note=f'{mode} This is a selected-country sample, not a global estimate. Missing values remain missing.'
    if len(snap):
        top=snap.loc[snap[indicator].idxmax()]
        note+=f' Highest observed {LABELS[indicator]}: {top.country}, {top[indicator]:,.2f} ({int(top.year)}). Higher does not necessarily mean better.'
        m=px.choropleth(snap,locations='iso3',color=indicator,hover_name='country',hover_data=['year'],labels=LABELS,color_continuous_scale='Teal')
        m.update_geos(projection_type='natural earth',bgcolor='#101c2d',landcolor='#25364b',showland=True,showcountries=True,countrycolor='#526479')
        b=px.bar(snap.sort_values(indicator),x=indicator,y='country',orientation='h',color=indicator,color_continuous_scale='Teal',hover_data=['year'],labels=LABELS)
    else:m=b=empty('No valid observations for these filters')
    # Full grid preserves gaps even when complete country-year rows are absent.
    grid=pd.MultiIndex.from_product([countries,range(start,end+1)],names=['country','year'])
    full=period.set_index(['country','year']).reindex(grid).reset_index()
    t=px.line(full,x='year',y=indicator,color='country',markers=True,labels=LABELS) if countries else empty('Select countries')
    t.update_traces(connectgaps=False)
    mask=full.pivot(index='country',columns='year',values=indicator).reindex(index=countries,columns=range(start,end+1)).notna().astype(int)
    h=go.Figure(go.Heatmap(z=mask.values,x=list(mask.columns),y=list(mask.index),zmin=0,zmax=1,colorscale=[[0,'#b64a65'],[1,'#3dd6b3']],colorbar=dict(tickvals=[0,1],ticktext=['Missing','Available']),hovertemplate='%{y} · %{x}<br>Available: %{z}<extra></extra>')) if countries else empty('Select countries')
    # Scatter always uses one common year, even when the map uses latest values.
    pair=period[period.year==year].dropna(subset=list(dict.fromkeys([x,YOUTH,GDP])))
    pair=pair[pair[GDP]>0]
    s=px.scatter(pair,x=x,y=YOUTH,size=GDP,color='country',hover_name='country',hover_data=['year'],labels=LABELS,size_max=42) if len(pair) else empty('No complete same-year records; try another year')
    title=f'Education & youth employment · {year} · n={len(pair)} / {len(countries)}'
    if not start<=year<=end:title+=' · outside window: no records'
    out=snap[['country','iso3','year',indicator]].rename(columns={'year':'observation_year'})
    return cards,note,style(m,'Geographic comparison'),style(b,'Country comparison'),style(t,'Historical trends · gaps preserved'),style(s,title),style(h,'Data availability · selected indicator'),out

def profile(df,country,start,end):
    d=df[(df.country==country)&df.year.between(int(start),int(end))].sort_values('year')
    f=make_subplots(rows=2,cols=2,subplot_titles=list(LABELS.values()))
    lines=[]
    for i,col in enumerate(LABELS):
        valid=d.dropna(subset=[col])
        f.add_trace(go.Scatter(x=d.year,y=d[col],mode='lines+markers',name=LABELS[col],connectgaps=False),row=i//2+1,col=i%2+1)
        if len(valid):
            first,last=valid.iloc[0],valid.iloc[-1]
            change=(last[col]/first[col]-1)*100 if col==GDP and first[col]!=0 else last[col]-first[col]
            unit='%' if col==GDP and first[col]!=0 else ('international $' if col==GDP else 'percentage points')
            lines.append(f'**{LABELS[col]}:** {last[col]:,.2f} ({int(last.year)}); change {change:+,.2f} {unit} from {int(first.year)} to {int(last.year)}.' if len(valid)>1 else f'**{LABELS[col]}:** {last[col]:,.2f} ({int(last.year)}); insufficient observations for change.')
        else:lines.append(f'**{LABELS[col]}:** no available data.')
    f=style(f,f'{country} · country profile');f.update_layout(height=650,showlegend=False)
    return '\n\n'.join(lines),f

def export_csv(df,countries,start,end):
    if int(start)>int(end):raise ValueError('Invalid year window')
    out=df[df.country.isin(countries or [])&df.year.between(int(start),int(end))]
    with tempfile.NamedTemporaryFile(suffix='.csv',prefix='edu_future_',delete=False,mode='w') as fp:
        out.to_csv(fp,index=False);return fp.name

def build_app(df=None):
    import gradio as gr
    df=load() if df is None else df
    names=sorted(df.country.unique());low=int(df.year.min());high=int(df.year.max());default=list(LABELS)[0]
    with gr.Blocks(title='EDU / FUTURE') as app:
        gr.HTML('<div class="hero"><div class="eyebrow">EDUCATION × ECONOMIC OPPORTUNITY</div><h1>EDU / FUTURE</h1><p>Explore education investment, participation and youth employment across ten selected countries.</p><small>WORLD BANK WDI · 2010–2023 · Built by Blessing Sekeramavi</small></div>')
        with gr.Row():
            countries=gr.Dropdown(names,value=names,multiselect=True,label='Comparison countries')
            indicator=gr.Dropdown([(v,k) for k,v in LABELS.items()],value=default,label='Main indicator')
        with gr.Row():
            start=gr.Slider(low,high,value=low,step=1,label='Start year')
            end=gr.Slider(low,high,value=high,step=1,label='End year')
            year=gr.Slider(low,high,value=high,step=1,label='Snapshot / scatter year')
        with gr.Row():
            latest=gr.Checkbox(True,label='Map & ranking: latest available within window')
            x=gr.Dropdown([(LABELS[k],k) for k in list(LABELS)[:2]],value=default,label='Scatter X axis')
            run=gr.Button('Update observatory',variant='primary')
        cards=gr.HTML();note=gr.Markdown()
        with gr.Tab('Overview'):
            with gr.Row():m=gr.Plot();b=gr.Plot()
            t=gr.Plot()
        with gr.Tab('Relationships'):
            gr.Markdown('Bubble area represents GDP per capita. All coordinates use the same year. These associations do not establish causation; youth unemployment is a share of the youth labour force, not all young people.')
            s=gr.Plot()
        with gr.Tab('Data quality & export'):
            h=gr.Plot();table=gr.Dataframe(label='Selected indicator snapshot',interactive=False)
            download=gr.Button('Export filtered historical data');file=gr.File(label='CSV download')
        with gr.Tab('Country profiles'):
            country=gr.Dropdown(names,value='Zimbabwe' if 'Zimbabwe' in names else names[0],label='Country')
            pnote=gr.Markdown();pfig=gr.Plot()
        with gr.Tab('Sources & methodology'):
            gr.Markdown('## Read the evidence carefully\nTen purposively selected countries; no representative global or regional estimates. Medians are unweighted sample summaries. Latest mode may mix years; scatter always uses a common year. No interpolation or zero filling. Missingness includes absent country-year rows. Gross tertiary enrolment can exceed 100%. Education spending is not a direct measure of quality. GDP uses PPP constant 2021 international dollars. Historical values can be revised by the source.\n\n'+ '\n\n'.join(f'- [{v[1]}](https://data.worldbank.org/indicator/{v[0]}) · `{v[0]}`' for v in INDICATORS.values())+'\n\nSee provenance.json for retrieval time and source update dates. World Bank WDI, CC BY 4.0; original indicator providers are identified on the source pages.')
        inputs=[countries,start,end,indicator,latest,year,x];outputs=[cards,note,m,b,t,s,h,table]
        def update(*args):
            try:return analyze(df,*args)
            except ValueError as err:raise gr.Error(str(err))
        run.click(update,inputs,outputs)
        app.load(update,inputs,outputs)
        def update_profile(c,a,b):return profile(df,c,a,b)
        country.change(update_profile,[country,start,end],[pnote,pfig])
        run.click(update_profile,[country,start,end],[pnote,pfig])
        app.load(update_profile,[country,start,end],[pnote,pfig])
        download.click(lambda c,a,b:export_csv(df,c,a,b),[countries,start,end],file)
    return app

if __name__=='__main__':
    import gradio as gr
    build_app().launch(theme=gr.themes.Base(),css=CSS)
