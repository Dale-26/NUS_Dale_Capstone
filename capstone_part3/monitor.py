import logging
import numpy as np
from scipy.stats import ks_2samp
logger=logging.getLogger(__name__)
def monitor(reference,current,predictions,baseline_mae):
    mae=float(np.mean(abs(current.traffic_volume.to_numpy()-predictions)))
    drift={c:float(ks_2samp(reference[c],current[c]).statistic) for c in ['temp','hour','clouds_all']}
    alert=mae>baseline_mae*1.25 or max(drift.values())>.2
    result={'status':'ALERT' if alert else 'PASS','mae':mae,'reference_validation_mae':baseline_mae,'mae_threshold':baseline_mae*1.25,'ks_statistics':drift,'ks_threshold':.2}
    (logger.warning if alert else logger.info)('Monitoring %s',result)
    return result
