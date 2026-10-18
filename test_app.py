import unittest
import pandas as pd
from data import INDICATORS,validate
from app import analyze,snapshot,build_app,export_csv

class ObservatoryTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame([dict(country=c,iso3=iso,year=y,**{k:float(y-2000) for k in INDICATORS}) for c,iso in [('Germany','DEU'),('Zimbabwe','ZWE')] for y in [2021,2022,2023]])
        self.df.loc[5,list(INDICATORS)[0]]=float('nan')
    def test_latest_uses_indicator_valid_year(self):
        s=snapshot(self.df,list(INDICATORS)[0],True,2023)
        self.assertEqual(int(s[s.country=='Zimbabwe'].year.iloc[0]),2022)
    def test_missing_rows_in_coverage_and_heatmap(self):
        d=self.df.drop(index=1)
        r=analyze(d,['Germany','Zimbabwe'],2021,2023,list(INDICATORS)[0],True,2023,list(INDICATORS)[0])
        self.assertIn('66.7%',r[0]);self.assertEqual(r[6].data[0].z.shape,(2,3));self.assertEqual(r[6].data[0].z[0][1],0)
    def test_empty_selection(self):
        r=analyze(self.df,[],2021,2023,list(INDICATORS)[0],True,2023,list(INDICATORS)[0]);self.assertTrue(r[-1].empty)
    def test_invalid_window(self):
        with self.assertRaises(ValueError):analyze(self.df,['Germany'],2023,2021,list(INDICATORS)[0],False,2023,list(INDICATORS)[0])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):validate(pd.concat([self.df,self.df.iloc[[0]]]))
    def test_all_missing_indicator(self):
        d=self.df.copy();d[list(INDICATORS)[0]]=float('nan')
        r=analyze(d,['Germany'],2021,2023,list(INDICATORS)[0],True,2023,list(INDICATORS)[0]);self.assertTrue(r[-1].empty)
    def test_scatter_uses_common_year(self):
        r=analyze(self.df,['Germany','Zimbabwe'],2021,2023,list(INDICATORS)[0],True,2023,list(INDICATORS)[0]);self.assertIn('n=1 / 2',r[5].layout.title.text)
    def test_build_and_csv(self):
        app=build_app(self.df);self.assertTrue(app.config['components'])
        p=export_csv(self.df,['Zimbabwe'],2022,2023);d=pd.read_csv(p);self.assertEqual(len(d),2);self.assertTrue(d.country.eq('Zimbabwe').all())

if __name__=='__main__':unittest.main()
