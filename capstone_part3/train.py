"""Chronological evaluation, training-only preprocessing, local MLflow tracking."""
import json,logging,time
from pathlib import Path
import joblib,numpy as np,pandas as pd,mlflow
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge,LogisticRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error,r2_score,accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
from capstone_part2.pipeline import load_raw,clean,hourly,configure_logging
from capstone_part2.feature_engineering import engineer
logger=logging.getLogger(__name__)
NUM=['hour','day_of_week','month','weekend','hour_sin','hour_cos','day_of_week_sin','day_of_week_cos','temp','rain_1h','snow_1h','clouds_all','holiday_flag','is_low_visibility','severe_weather']
CAT=['weather_main']
FEATURES=NUM+CAT

def preprocessor():return ColumnTransformer([('numeric',StandardScaler(),NUM),('weather',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CAT)])
def metrics(y,p,classification=False,prob=None):
    if not classification:return {'mae':mean_absolute_error(y,p),'r2':r2_score(y,p)}
    return {'accuracy':accuracy_score(y,p),'precision':precision_score(y,p,zero_division=0),'recall':recall_score(y,p,zero_division=0),'f1':f1_score(y,p,zero_division=0),'roc_auc':roc_auc_score(y,prob) if len(np.unique(y))==2 else float('nan')}
def run():
    out=Path('capstone_part3');(out/'models').mkdir(exist_ok=True)
    raw=load_raw('data/Metro_Interstate_Traffic_Volume.csv');dt=pd.to_datetime(raw.date_time)
    # Fixed calendar boundaries, not random records; no shared timestamps across sets.
    ref=raw[dt<'2017-01-01'];frames=[];state=None
    for name,mask in [('train',dt<'2017-01-01'),('validation',(dt>='2017-01-01')&(dt<'2018-01-01')),('test',dt>='2018-01-01')]:
        f=hourly(clean(raw[mask],reference=ref));f,state=engineer(f,state);f['split']=name;frames.append(f)
    train,val,test=frames
    (out/'feature_state.json').write_text(json.dumps(state,indent=2))
    pd.concat(frames).to_csv(out/'evaluation_data.csv',index=False)
    mlflow.set_tracking_uri('sqlite:///'+str((out/'mlflow.db').resolve()))
    mlflow.set_experiment('traffic-intelligence-chronological')
    # MLflow database migration logging can disable previously constructed loggers.
    for item in logging.root.manager.loggerDict.values():
        if isinstance(item,logging.Logger): item.disabled=False
    configure_logging('capstone_part3/training.log',mode='a')
    logger.info('Experiment initialized; training begins')
    specs=[('ridge',Ridge(alpha=10),False),('forest_regression',RandomForestRegressor(n_estimators=120,max_depth=16,min_samples_leaf=4,n_jobs=-1,random_state=42),False),('logistic',LogisticRegression(max_iter=1000,class_weight='balanced'),True),('forest_classifier',RandomForestClassifier(n_estimators=120,max_depth=16,min_samples_leaf=4,class_weight='balanced',n_jobs=-1,random_state=42),True),('neural_network',MLPRegressor(hidden_layer_sizes=(64,32),max_iter=100,early_stopping=False,random_state=42,batch_size=256),False)]
    rows=[];fitted={}
    for name,model,classification in specs:
        target='high_risk' if classification else 'traffic_volume';pipe=Pipeline([('prepare',preprocessor()),('model',model)])
        start=time.perf_counter()
        with mlflow.start_run(run_name=name+'-v1') as run:
            mlflow.log_params({'version':'v1','seed':42,'train_end':'2016-12-31','validation_year':2017,'test_year':2018,'target':target,'algorithm':type(model).__name__})
            mlflow.log_params({k:str(v) for k,v in model.get_params().items()})
            pipe.fit(train[FEATURES],train[target]);elapsed=time.perf_counter()-start
            row={'model':name,'version':'v1','train_seconds':elapsed,'train_rows':len(train),'validation_rows':len(val),'test_rows':len(test),'run_id':run.info.run_id}
            for label,data in [('validation',val),('test',test)]:
                pred=pipe.predict(data[FEATURES]);prob=pipe.predict_proba(data[FEATURES])[:,1] if classification else None
                m=metrics(data[target],pred,classification,prob);row.update({label+'_'+k:v for k,v in m.items()});mlflow.log_metrics({label+'_'+k:v for k,v in m.items()})
            path=out/'models'/(name+'_v1.joblib');joblib.dump(pipe,path,compress=3)
            mlflow.log_artifact(str(path),artifact_path='models');mlflow.log_artifact(str(out/'feature_state.json'))
            logger.info('Trained %s in %.2fs; metrics %s',name,elapsed,row)
        rows.append(row);fitted[name]=pipe
    results=pd.DataFrame(rows);results.to_csv(out/'model_metrics.csv',index=False)
    # Select by validation only; test scores are final evaluation, not selection.
    candidates=results[results.validation_mae.notna()];selected=candidates.loc[candidates.validation_mae.idxmin(),'model']
    joblib.dump(fitted[selected],out/'models'/'deployment.joblib',compress=3)
    (out/'model_manifest.json').write_text(json.dumps({'selected_by':'minimum validation MAE','model':selected,'version':'v1','features':FEATURES,'proxy_only':True,'train_end':'2016-12-31'},indent=2))
    reg=fitted[selected];pred=reg.predict(test[FEATURES]);test_out=test[['date_time','hour','weekend','weather_main','traffic_volume','high_risk']].copy();test_out['predicted_volume']=pred;test_out['absolute_error']=abs(pred-test.traffic_volume)
    test_out.to_csv(out/'test_predictions.csv',index=False)
    test_out.groupby('weather_main').absolute_error.agg(['count','mean','median']).to_csv(out/'fairness_weather.csv')
    test_out.groupby('hour').absolute_error.agg(['count','mean']).to_csv(out/'fairness_hour.csv')
    cp=fitted['forest_classifier'].predict(test[FEATURES]);test_out['classified_proxy']=cp
    fair=[]
    for label,g in test_out.groupby('weather_main'):
        fair.append({'weather':label,'n':len(g),**metrics(g.high_risk,g.classified_proxy,True,np.zeros(len(g)))})
    pd.DataFrame(fair).drop(columns='roc_auc').to_csv(out/'proxy_subgroup_metrics.csv',index=False)
    # Explain a comparable forest on the same demand problem, regardless of deployment selection.
    import shap,matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    f=fitted['forest_regression'];sample=test.sample(min(300,len(test)),random_state=42);z=f.named_steps['prepare'].transform(sample[FEATURES]);names=f.named_steps['prepare'].get_feature_names_out()
    explainer=shap.TreeExplainer(f.named_steps['model']);values=explainer.shap_values(z,check_additivity=False)
    pd.DataFrame({'feature':names,'mean_abs_shap':np.abs(values).mean(axis=0)}).sort_values('mean_abs_shap',ascending=False).to_csv(out/'shap_importance.csv',index=False)
    shap.summary_plot(values,z,feature_names=names,show=False,max_display=15);plt.tight_layout();plt.savefig(out/'shap_summary.png',dpi=160,bbox_inches='tight');plt.close();logger.info('Saved SHAP explanation figure')
    baseline=reg.predict(val[FEATURES]);validation_mae=mean_absolute_error(val.traffic_volume,baseline)
    from capstone_part3.monitor import monitor
    normal=monitor(train,test,pred,validation_mae);stress=monitor(train,test,pred+3000,validation_mae)
    (out/'monitoring.json').write_text(json.dumps({'observed_test':normal,'synthetic_error_stress':stress},indent=2))
    from capstone_part3.unsupervised import analyse
    analyse(train,out)
    from capstone_part3.recommend import recommend
    (out/'recommendations.txt').write_text('\n\n'.join(recommend(train,d,w) for d,w in [('weekday','Clear'),('weekend','Clear'),('weekday','Rain')]))
if __name__=='__main__':
    configure_logging('capstone_part3/training.log')
    try:
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=2): run()
    except Exception as e:
        logger.error('Training failed: %s',e,exc_info=True);raise SystemExit(1)
