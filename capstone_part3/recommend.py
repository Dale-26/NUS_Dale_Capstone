import logging
logger=logging.getLogger(__name__)
def recommend(df,day_type='weekday',weather='Clear',start=6,end=22):
    """Rank observed daylight/evening hours, requiring >=20 supporting records."""
    x=df[(df.weekend==int(day_type=='weekend'))&df.weather_main.eq(weather)&df.hour.between(start,end-1)]
    stats=x.groupby('hour').traffic_volume.agg(['mean','count']);stats=stats[stats['count']>=20]
    if stats.empty:return 'Insufficient observations for a supported recommendation; choose another weather condition.'
    hour=int(stats['mean'].idxmin());r=stats.loc[hour]
    logger.info('Recommended hour=%s day_type=%s weather=%s support=%s',hour,day_type,weather,int(r['count']))
    return (f'For a {day_type} journey in {weather} weather, consider {hour:02d}:00–{hour+1:02d}:00. '
            f'Historical mean is {r["mean"]:.0f} vehicles/hour from {int(r["count"])} observations, '
            f'the lowest supported mean within {start:02d}:00–{end:02d}:00. '
            'This is a single-corridor timing suggestion, not a route, travel-time or safety guarantee.')
