import json,logging,sqlite3
from pathlib import Path
import pandas as pd
from capstone_part2.pipeline import configure_logging,load_raw
logger=logging.getLogger(__name__)
def run():
    out=Path('capstone_part1');raw=load_raw('data/Metro_Interstate_Traffic_Volume.csv');h=pd.read_csv('data/processed_hourly.csv')
    with sqlite3.connect(out/'traffic.sqlite') as con:
        raw.to_sql('traffic_raw',con,if_exists='replace',index=False);h.to_sql('traffic_hourly',con,if_exists='replace',index=False)
        assert con.execute('SELECT COUNT(*) FROM traffic_raw').fetchone()[0]==len(raw)
        queries='\n'.join(line for line in (out/'analysis.sql').read_text().splitlines() if not line.lstrip().startswith('--')).split(';')
        for q,name in zip(queries,['annual_raw','holiday_temperatures','annual_hourly']):
            result=pd.read_sql_query(q,con);result.to_csv(out/(name+'.csv'),index=False)
            logger.info('Saved SQL result %s (%s rows)',name,len(result))
    v=raw.traffic_volume;c=v>5500;clear=raw.weather_main.eq('Clear');cloud=raw.weather_main.eq('Clouds')
    a=int((c&clear).sum());b=int((~c&clear).sum());cc=int((c&cloud).sum());d=int((~c&cloud).sum())
    result={'rows':len(raw),'columns':len(raw.columns),'missing':raw.eq('').sum().to_dict(),'unique_hours':raw.date_time.nunique(),
    'mean':v.mean(),'median':v.median(),'sample_std':v.std(),'sample_variance':v.var(),'range':int(v.max()-v.min()),
    'temperature_correlation_raw':raw.temp.corr(v),'temperature_correlation_clean_hourly':h.temp.corr(h.traffic_volume),
    'p_congestion':c.mean(),'p_clear':clear.mean(),'p_congestion_and_clear':(c&clear).mean(),
    'p_clear_given_congestion':clear[c].mean(),'p_high_temp_given_congestion':raw.temp.gt(292)[c].mean(),
    'independence_product':c.mean()*clear.mean(),'odds_cells':{'clear_congested':a,'clear_other':b,'clouds_congested':cc,'clouds_other':d},'odds_ratio_clear_clouds':a*d/(b*cc)}
    (out/'statistics.json').write_text(json.dumps(result,indent=2,default=float))
    raw.groupby('weather_main').traffic_volume.agg(['mean','count']).sort_values('mean').to_csv(out/'weather_raw.csv')
    logger.info('Saved statistics, probabilities and weather summaries')
if __name__=='__main__':
    configure_logging('capstone_part1/analysis.log');run()
