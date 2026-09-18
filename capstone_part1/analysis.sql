-- RAW record totals as requested; not corrected annual traffic exposure.
WITH yearly AS (
 SELECT strftime('%Y',date_time) AS year,COUNT(*) AS records,
 COUNT(DISTINCT date_time) AS observed_hours,SUM(traffic_volume) AS total,
 AVG(traffic_volume) AS mean_volume FROM traffic_raw
 WHERE strftime('%Y',date_time) BETWEEN '2012' AND '2017' GROUP BY year
)
SELECT *,total-LAG(total) OVER (ORDER BY year) AS change,
 100.0*(total-LAG(total) OVER (ORDER BY year))/LAG(total) OVER (ORDER BY year) AS change_pct
FROM yearly;

-- Holiday-labelled records, not automatically every hour on that date.
SELECT strftime('%Y',date_time) AS year,holiday,COUNT(*) AS n,
 AVG(temp) AS mean_temp_k,AVG(traffic_volume) AS mean_traffic
FROM traffic_raw WHERE holiday IN ('New Years Day','Labor Day')
AND strftime('%Y',date_time) BETWEEN '2015' AND '2017'
GROUP BY year,holiday ORDER BY holiday,year;

-- Exposure-aware sensitivity check, one row per observed hour.
SELECT strftime('%Y',date_time) AS year,COUNT(*) AS hours,
 SUM(traffic_volume) AS total,AVG(traffic_volume) AS mean_volume
FROM traffic_hourly GROUP BY year;
