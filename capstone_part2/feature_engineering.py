import logging
import numpy as np
import pandas as pd
logger=logging.getLogger(__name__)
SEVERE_WEATHER={'Thunderstorm','Squall','Snow'}
LOW_VISIBILITY={'Fog','Mist','Haze','Smoke'}

def engineer(df,state=None):
    logger.info('Before feature engineering: %s rows, %s columns',*df.shape)
    x=df.copy();dt=pd.to_datetime(x.date_time)
    x['hour']=dt.dt.hour;x['day_of_week']=dt.dt.dayofweek;x['month']=dt.dt.month;x['weekend']=(x.day_of_week>=5).astype(int)
    x['temp_c']=x.temp-273.15
    for col,period in [('hour',24),('day_of_week',7)]:
        x[col+'_sin']=np.sin(2*np.pi*x[col]/period);x[col+'_cos']=np.cos(2*np.pi*x[col]/period)
    x['is_low_visibility']=x.weather_main.isin(LOW_VISIBILITY).astype(int)
    x['severe_weather']=x.weather_main.isin(SEVERE_WEATHER).astype(int)
    x['wet_weather']=((x.rain_1h>0)|(x.snow_1h>0)).astype(int)
    if 'holiday_flag' not in x: x['holiday_flag']=x.holiday.ne('None').astype(int)
    if state is None:
        state={'quartiles':x.traffic_volume.quantile([.25,.5,.75]).tolist(),
               'scales':{c:[float(x[c].mean()),float(x[c].std() or 1)] for c in ['temp','clouds_all']},
               'weather_categories':sorted(x.weather_main.unique().tolist())}
    logger.debug('Reference quartiles: %s; scaling parameters: %s',state['quartiles'],state['scales'])
    for col,(mean,std) in state['scales'].items(): x[col+'_scaled']=(x[col]-mean)/std
    for cat in state['weather_categories']: x['weather_'+cat]=x.weather_main.eq(cat).astype(int)
    x['congestion_category']=pd.cut(x.traffic_volume,[-np.inf,*state['quartiles'],np.inf],labels=['Low','Medium','High','Severe'])
    x['traffic_category']=np.select([x.traffic_volume<4500,x.traffic_volume<=5500],['Low','Medium'],default='High')
    x['high_risk']=(x.congestion_category.isin(['High','Severe']) & ((x.severe_weather==1)|(x.is_low_visibility==1))).astype(int)
    logger.info('After feature engineering: %s rows, %s columns',*x.shape)
    return x,state
