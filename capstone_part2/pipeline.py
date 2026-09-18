"""Validate before cleaning; retain raw input and record every modification."""
import argparse
import logging
from pathlib import Path
import numpy as np
import pandas as pd
logger = logging.getLogger(__name__)
EXPECTED = ['holiday','temp','rain_1h','snow_1h','clouds_all','weather_main','weather_description','date_time','traffic_volume']
NUMERIC = ['temp','rain_1h','snow_1h','clouds_all','traffic_volume']

def configure_logging(path, debug=False):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[logging.StreamHandler(), logging.FileHandler(path, mode='w')], force=True)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

def load_raw(path):
    df = pd.read_csv(path, keep_default_na=False)
    missing = set(EXPECTED) - set(df.columns)
    if missing: raise ValueError(f'Missing schema columns: {sorted(missing)}')
    logger.info('Loaded %s rows and %s columns; schema validated', *df.shape)
    return df

def clean(df, reference=None):
    """Fit imputation on reference when supplied (training-only for ML)."""
    df = df.copy()
    for col in ['holiday','weather_main','weather_description']:
        old = df[col].copy()
        df[col] = df[col].astype('string').str.strip()
        if col == 'weather_main': df[col] = df[col].str.title()
        if col == 'weather_description': df[col] = df[col].str.lower()
        df[col] = df[col].replace('', 'None' if col == 'holiday' else 'Unknown').fillna('Unknown')
        n = int((old != df[col]).sum())
        (logger.warning if n else logger.info)('%s categorical standardisation: %s rows modified',col,n)
    old = df.date_time.copy()
    df['date_time'] = pd.to_datetime(df.date_time, errors='coerce')
    n = int(df.date_time.isna().sum())
    (logger.warning if n else logger.info)('Invalid date removal: %s rows',n)
    df = df.dropna(subset=['date_time'])
    n = int(df.duplicated().sum()); df = df.drop_duplicates()
    (logger.warning if n else logger.info)('Exact duplicate removal: %s rows',n)
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col],errors='coerce')
    invalid_target = df.traffic_volume.isna() | (df.traffic_volume < 0)
    n = int(invalid_target.sum()); df = df.loc[~invalid_target].copy()
    (logger.warning if n else logger.info)('Invalid traffic target removal: %s rows',n)
    bounds = {'temp':(200,330),'rain_1h':(0,9000),'snow_1h':(0,1000),'clouds_all':(0,100)}
    for col,(lo,hi) in bounds.items():
        bad = ~df[col].between(lo,hi) | df[col].isna()
        ref = df if reference is None else reference
        valid = ref.loc[pd.to_numeric(ref[col],errors='coerce').between(lo,hi)].copy()
        valid[col] = pd.to_numeric(valid[col])
        valid['date_time'] = pd.to_datetime(valid.date_time)
        med = valid.groupby(valid.date_time.dt.month)[col].median()
        fallback = valid[col].median()
        if pd.isna(fallback): raise ValueError(f'No plausible reference values for {col}')
        for month in sorted(df.date_time.dt.month.unique()):
            mask = bad & (df.date_time.dt.month == month)
            if mask.any():
                value = med.get(month,fallback)
                df.loc[mask,col] = value
                logger.warning('%s month %s: imputed %s missing/impossible rows with reference median %s',col,month,int(mask.sum()),value)
        logger.info('%s range validation complete; %s affected rows',col,int(bad.sum()))
    return df.sort_values('date_time',kind='stable').reset_index(drop=True)

def hourly(df):
    """One sample per observed hour. Choose the most severe weather report deterministically."""
    severity = {'Thunderstorm':6,'Squall':6,'Snow':5,'Fog':4,'Smoke':4,'Mist':3,'Haze':3,'Rain':2,'Drizzle':1}
    x=df.copy(); x['_severity']=x.weather_main.map(severity).fillna(0)
    conflicts=x.groupby('date_time').traffic_volume.nunique().gt(1).sum()
    if conflicts: logger.warning('%s timestamps have conflicting traffic values; median retained',conflicts)
    values=x.groupby('date_time').traffic_volume.median()
    x=x.sort_values(['date_time','_severity','weather_main','weather_description'],kind='stable').drop_duplicates('date_time',keep='last').drop(columns='_severity')
    x['traffic_volume']=x.date_time.map(values)
    logger.warning('Collapsed %s repeated timestamp records into %s distinct observed hours',len(df)-len(x),len(x))
    # Holiday markers commonly occur only at midnight; propagate across the observed calendar date.
    dates=x.date_time.dt.date
    holiday_dates=set(dates[x.holiday.ne('None') & x.holiday.ne('Unknown')])
    x['holiday_flag']=dates.isin(holiday_dates).astype(int)
    return x.reset_index(drop=True)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',default='data/Metro_Interstate_Traffic_Volume.csv');p.add_argument('--debug',action='store_true');a=p.parse_args()
    configure_logging('capstone_part2/pipeline.log',a.debug)
    try:
        from capstone_part2.feature_engineering import engineer
        from capstone_part2.visualizations import plot_all
        df=clean(load_raw(a.input)); df.to_csv('data/cleaned_records.csv',index=False)
        h=hourly(df); features,state=engineer(h);features.to_csv('data/processed_hourly.csv',index=False)
        import json
        Path('capstone_part2/feature_state.json').write_text(json.dumps(state,indent=2))
        logger.info('Saved cleaned record and engineered hourly data')
        plot_all(features,Path('capstone_part2/figures'))
    except (OSError,ValueError,KeyError,pd.errors.ParserError) as e:
        logger.error('Pipeline failed: %s',e,exc_info=True);return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
