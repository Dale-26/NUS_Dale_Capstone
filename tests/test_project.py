import unittest,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from capstone_part2.pipeline import load_raw,clean,hourly
from capstone_part2.feature_engineering import engineer
from capstone_part3.api import app
class ProjectTests(unittest.TestCase):
 def test_schema_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.csv';p.write_text('temp\n280\n')
   with self.assertRaises(ValueError):load_raw(p)
 def test_cleaning_and_hourly(self):
  df=pd.read_csv('data/Metro_Interstate_Traffic_Volume.csv',keep_default_na=False).head(10)
  df.loc[0,'temp']=0;df=pd.concat([df,df.iloc[[1]]],ignore_index=True)
  c=clean(df);self.assertEqual(len(c),10);self.assertTrue(c.temp.between(200,330).all());self.assertTrue(hourly(c).date_time.is_unique)
 def test_training_reference_and_no_leakage(self):
  df=pd.read_csv('capstone_part3/evaluation_data.csv');sets=[set(df[df.split==s].date_time) for s in ['train','validation','test']]
  self.assertFalse(sets[0]&sets[1]);self.assertFalse(sets[1]&sets[2])
  from capstone_part3.train import FEATURES
  self.assertTrue(set(FEATURES).isdisjoint({'traffic_volume','high_risk','congestion_category','traffic_category'}))
  self.assertTrue(np.isfinite(df[['temp','clouds_all','traffic_volume']]).all().all())
 def test_api_valid_and_invalid(self):
  client=app.test_client();payload={'datetime':'2018-07-10 10:00:00','temp':295,'rain_1h':0,'snow_1h':0,'clouds_all':20,'weather_main':'Clear','holiday_flag':0}
  response=client.post('/predict',json=payload);self.assertEqual(response.status_code,200);self.assertTrue(np.isfinite(response.json['traffic_volume']))
  payload['temp']=0;self.assertEqual(client.post('/predict',json=payload).status_code,400)
  self.assertEqual(client.post('/predict',json={'datetime':'bad'}).status_code,400)
if __name__=='__main__':unittest.main()
