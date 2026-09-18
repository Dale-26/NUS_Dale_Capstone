import logging,json,itertools
import pandas as pd,numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
logger=logging.getLogger(__name__)
def analyse(train,out):
    cols=['hour_sin','hour_cos','severe_weather','is_low_visibility','traffic_volume']
    z=StandardScaler().fit_transform(train[cols]);evaluations=[];fitted={}
    for k in [3,4,5]:
        m=KMeans(n_clusters=k,n_init=10,random_state=42).fit(z);fitted[k]=m
        evaluations.append({'k':k,'silhouette':silhouette_score(z,m.labels_,sample_size=min(3000,len(z)),random_state=42)})
    k=max(evaluations,key=lambda r:r['silhouette'])['k'];x=train.copy();x['cluster']=fitted[k].labels_
    pd.DataFrame(evaluations).to_csv(out/'cluster_selection.csv',index=False)
    x.groupby('cluster')[['hour','traffic_volume','severe_weather','is_low_visibility','weekend']].agg(['mean','count']).to_csv(out/'cluster_profiles.csv')
    # Exact enumerative association mining over 3 categorical antecedent dimensions.
    x['day_type']=np.where(x.weekend==1,'weekend','weekday');x['period']=pd.cut(x.hour,[-1,5,9,15,19,23],labels=['night','morning','midday','evening','late'])
    rules=[];base=x.congestion_category.value_counts(normalize=True)
    for size in [1,2,3]:
        for cols in itertools.combinations(['period','day_type','weather_main'],size):
            for key,g in x.groupby(list(cols),observed=True):
                if not isinstance(key,tuple):key=(key,)
                counts=g.congestion_category.value_counts()
                for target,count in counts.items():
                    support=count/len(x);confidence=count/len(g)
                    if support>=.01 and confidence>=.6:
                        rules.append({'antecedent':'; '.join(f'{c}={v}' for c,v in zip(cols,key)),'consequent':str(target),'support':support,'confidence':confidence,'lift':confidence/base[target],'count':int(count)})
    pd.DataFrame(rules).sort_values('lift',ascending=False).to_csv(out/'association_rules.csv',index=False)
    logger.info('Saved clustering profiles and %s association rules',len(rules))
