[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blessing-edu-future.streamlit.app/)

**[Open the hosted app](https://blessing-edu-future.streamlit.app/)**

# EDU / FUTURE

[Open the public dashboard](https://edu-future-blessing-observatory.pearlypanda9.chatgpt.site)

An interactive education and employment observatory by Blessing Sekeramavi. Compare education spending, gross tertiary enrolment, youth unemployment and GDP per capita across ten selected countries, 2010–2023.

## Public browser dashboard

The `docs/` folder contains the complete browser version with bundled Plotly and map geography. It runs without a Python server and can be hosted on GitHub Pages. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for repository and publishing steps.

## Run in Google Colab
Open the included `global-education-employment.ipynb`, select **Runtime → Run all**, then open the Gradio link printed by the final cell. The notebook embeds the original CSV and project source, so there is no manual upload step. The final cell stays running while you use the dashboard. Stop it to end the server. Rerunning the launch cell closes the previous instance.

## Run locally
Use Python 3.11 or 3.12 in a virtual environment:

```bash
pip install -r requirements.txt
python app.py
```

Open the local URL printed in the terminal. To verify the analytics and interface construction:

```bash
python -m unittest -v
```

## Explore
- Overview: country choropleth, rankings and annual trends.
- Relationships: common-year education/unemployment scatter; bubble area represents GDP per capita.
- Data quality: availability matrix including entirely absent rows, exact indicator coverage and filtered CSV export.
- Country profiles: four separate indicator panels with explicit observation years and endpoint changes.
- Sources: methodology and official indicator links.

Choose filters and click **Update observatory**. The scatter always uses the selected common year; latest-value mode applies to the map, ranking and snapshot table. Choose a year within the selected window to use same-year mode. An empty country selection produces an empty view.

## Data and interpretation
The bundled CSV is the original project dataset retrieved 17 October 2026, with source URLs and update dates retained. `provenance.json` describes this snapshot. No indicator values were changed. Ten countries are purposively selected, not statistically representative. Sample medians are unweighted and are not global or regional estimates. Missing values are never set to zero or interpolated. The heatmap reindexes the complete selected country-year grid. Higher spending and enrolment do not necessarily indicate better outcomes. Gross enrolment can exceed 100%. Youth unemployment is a share of the youth labour force, not all youth. Associations do not demonstrate causality.

World Bank WDI indicator codes: `SE.XPD.TOTL.GD.ZS`, `SE.TER.ENRR`, `SL.UEM.1524.ZS`, `NY.GDP.PCAP.PP.KD`. See the source pages for original providers. Data attribution: World Bank, World Development Indicators, CC BY 4.0.

Optional refresh: `python data.py` fetches the same country/year scope from the official API and replaces the local CSV and provenance only after all four requests succeed. Historical values may be revised. The notebook contains a fixed snapshot; regenerate its embedded assets if you want it to include a refreshed dataset.

## Interview walkthrough
1. Explain the question: how do education investment and participation differ alongside youth labour-market outcomes?
2. Show the overview, then compare Germany and Zimbabwe with a third country.
3. Switch from latest available to a common year and explain why alignment matters.
4. Use the missing-data matrix to explain why comparisons can be incomplete.
5. Show a country profile and export its data. Emphasize descriptive findings, data validation and reproducibility; avoid causal claims.

## Repair notes
Replaced truncated code-generator cells and unsafe nested string escaping. Removed obsolete launch patches and import-cache problems. Corrected coverage denominators and missing-row handling; made source years explicit and restricted cross-indicator comparisons to a common year. Added eight regression checks and validated all four indicators in both snapshot modes on the original dataset.
