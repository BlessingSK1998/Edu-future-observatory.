# Put the complete project on GitHub

Suggested repository name: `edu-future-observatory`.
Suggested description: Interactive World Bank education and youth employment observatory: 10 countries, 2010–2023, reproducible Python analytics and a public browser dashboard.

1. Create a new public GitHub repository with that name. Do not initialize it with a README if you plan to push this complete folder using Git.
2. Extract this ZIP and upload the **contents** of the `edu-future` folder to the repository root. Include the entire `docs` directory. Use Git for the workflow and other dotfiles; GitHub's browser uploader may not include hidden folders.
3. To host directly from GitHub, open **Settings → Pages**. Select **Deploy from a branch**, choose **main** and **/docs**, then save. This requires no Python server. Alternatively choose **GitHub Actions** and use the included workflow. Choose only one publishing method.
4. Wait for Pages to report success and copy the exact URL it shows. Add that URL to the repository's About → Website field.
5. Recommended topics: `education`, `data-analysis`, `world-bank`, `python`, `plotly`, `gradio`, `dashboard`, `data-visualization`.

Using Git from this extracted folder:

```bash
git init
git branch -M main
git add .
git commit -m "Add complete EDU FUTURE observatory"
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the URL GitHub gives you. Never put passwords or tokens in project files.

## Which files do what?

- `docs/`: full browser dashboard, self-contained chart assets, data snapshot and map geography. Works on static hosting; no Colab runtime.
- `app.py`, `data.py`, `requirements.txt`: original Python dashboard, validation and reproducible acquisition.
- `global-education-employment.ipynb`: self-contained Colab notebook.
- `global_education_employment_2010_2023.csv`, `provenance.json`: original data snapshot and source details.
- `test_app.py`: Python regression checks.
- `test-web.cjs`: browser analytics and bundled asset checks. Run `cd docs && node ../test-web.cjs`.
- `.github/workflows/pages.yml`: optional GitHub Actions publication.

A stable hosting URL persists while the host, account and project remain active. No host can promise literal lifetime availability. The included files let you redeploy to another provider.

## Rebuild the browser data snapshot after a refresh

From the repository root, with pandas installed:

```python
from pathlib import Path
import pandas as pd
frame = pd.read_csv('global_education_employment_2010_2023.csv')
Path('docs/data.js').write_text('globalThis.EDU_DATA = ' + frame.to_json(orient='records') + ';\n')
```

Update the snapshot date text in `docs/index.html` and the included provenance after refreshing. Review and commit data updates deliberately; no automatic refresh is configured.
