"""User-facing CLI. print is used only for query answers."""
import argparse,logging
import pandas as pd
from capstone_part2.pipeline import configure_logging
logger=logging.getLogger(__name__)
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    q=s.add_parser('at');q.add_argument('datetime');q=s.add_parser('high');q.add_argument('--threshold',type=float,default=5500);q.add_argument('--limit',type=int,default=10)
    s.add_parser('compare');q=s.add_parser('recommend');q.add_argument('--day-type',choices=['weekday','weekend'],default='weekday');q.add_argument('--weather',default='Clear')
    a=p.parse_args();configure_logging('capstone_part2/app.log');logger.info('Command %s arguments %s',a.command,vars(a))
    try:
        df=pd.read_csv('data/processed_hourly.csv',parse_dates=['date_time'])
        if a.command=='at':
            dt=pd.to_datetime(a.datetime,format='%Y-%m-%d %H:%M:%S');r=df[df.date_time.eq(dt)][['date_time','traffic_volume','weather_main','temp_c']];print(r.to_string(index=False) if len(r) else 'No observed data for this timestamp.')
        elif a.command=='high':
            if a.limit<1 or a.threshold<0:raise ValueError('Limit must be positive and threshold nonnegative')
            print(df[df.traffic_volume>a.threshold].nlargest(a.limit,'traffic_volume')[['date_time','traffic_volume','weather_main']].to_string(index=False))
        elif a.command=='compare':print(df.groupby('weekend').traffic_volume.agg(['mean','count']).rename(index={0:'Weekday',1:'Weekend'}).to_string())
        else:
            from capstone_part3.recommend import recommend
            print(recommend(df,a.day_type,a.weather))
    except (ValueError,OSError,KeyError) as e:logger.error('Invalid query: %s',e);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
