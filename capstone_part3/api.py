"""Local Flask deployment simulation. Supply forecast weather for prospective use."""
import logging
from pathlib import Path
import joblib,pandas as pd,numpy as np
from flask import Flask,request,jsonify
from capstone_part2.feature_engineering import SEVERE_WEATHER,LOW_VISIBILITY
from capstone_part2.pipeline import configure_logging
logger=logging.getLogger(__name__)
app=Flask(__name__)
MODEL=Path(__file__).parent/'models'/'deployment.joblib'
def make_features(payload):
    dt=pd.to_datetime(payload['datetime'],format='%Y-%m-%d %H:%M:%S');weather=str(payload['weather_main'])
    if pd.isna(dt):raise ValueError('Invalid datetime')
    values={c:float(payload[c]) for c in ['temp','rain_1h','snow_1h','clouds_all']}
    for c,(lo,hi) in {'temp':(200,330),'rain_1h':(0,9000),'snow_1h':(0,1000),'clouds_all':(0,100)}.items():
        if not np.isfinite(values[c]) or not lo<=values[c]<=hi:raise ValueError(f'{c} outside supported range')
    holiday=int(payload.get('holiday_flag',0))
    if holiday not in [0,1]:raise ValueError('holiday_flag must be 0 or 1')
    values.update(hour=dt.hour,day_of_week=dt.dayofweek,month=dt.month,weekend=int(dt.dayofweek>=5),holiday_flag=holiday,weather_main=weather,is_low_visibility=int(weather in LOW_VISIBILITY),severe_weather=int(weather in SEVERE_WEATHER))
    for c,period in [('hour',24),('day_of_week',7)]:values[c+'_sin']=np.sin(2*np.pi*values[c]/period);values[c+'_cos']=np.cos(2*np.pi*values[c]/period)
    return pd.DataFrame([values])
@app.post('/predict')
def predict():
    try:
        frame=make_features(request.get_json());model=joblib.load(MODEL);prediction=float(model.predict(frame)[0]);logger.info('Demand prediction served')
        return jsonify(traffic_volume=prediction,units='vehicles/hour',version='v1',limitation='Historical single-corridor demonstration, not a safety prediction')
    except (ValueError,KeyError,TypeError) as e:logger.error('Invalid request: %s',e);return jsonify(error=str(e)),400
@app.get('/health')
def health():return jsonify(status='ready' if MODEL.exists() else 'model_missing')
if __name__=='__main__':
    configure_logging('capstone_part3/api.log');app.run(host='127.0.0.1',port=5001,debug=False)
