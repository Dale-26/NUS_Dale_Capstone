# Traffic patterns and analytical insights

## Scope and principal finding

The supplied file contains 48,204 records and nine columns, covering 40,575 distinct observed hours from October 2012 to September 2018. Repeated weather reports can share a timestamp and traffic count. Raw records are used for the prescribed calculations; hourly deduplication is used separately for modelling. Time of day and day type are more informative for demand planning than the weak marginal temperature relationship.

## Annual traffic totals and coverage

SQL raw-record totals are 8,208,767 (2012), 28,177,412 (2013), 15,731,289 (2014), 14,181,206 (2015), 29,494,821 (2016) and 35,428,156 (2017). Changes are +243.26%, −44.17%, −9.85%, +107.99% and +20.12%, respectively. These are sums of recorded values, not comparable complete-year traffic counts.

Observed-hour coverage varies sharply: 2,103; 7,294; 4,501; 3,593; 7,838; and 8,713 hours. The partial 2012 year and sparse 2014–2015 coverage explain why the apparent growth and decline cannot be treated as demand trends. Raw mean traffic is much steadier, ranging from 3,169 to 3,341 across these years. Use hour-normalised and matched-period comparisons before changing capacity.

## Holiday temperatures

Labor Day mean labelled-record temperature was 295.02 K in 2015, 293.17 K in 2016 and 295.54 K in 2017: changes of −1.85 K and +2.37 K. New Year’s Day has no labelled observation in 2015; 2016 and 2017 values are 265.94 K and 270.62 K, a +4.68 K change. Do not invent the missing 2015 value. Each comparison has only one or two weather records, sometimes at the same timestamp; these cannot establish a weather effect on holiday traffic.

## Distribution and correlation

Mean traffic is 3,259.82, median 3,380, sample standard deviation 1,986.86, sample variance 3,947,615.32, and range 7,280 vehicles. The wide spread reflects strong variation across hours. Raw temperature–traffic Pearson correlation is 0.1303; after cleaning and hourly consolidation it is 0.1394. Both indicate a weak positive association. Season, hour and commuting patterns confound this relationship; correlation does not demonstrate causation.

## Probability and clear weather

Congestion means traffic_volume > 5,500. P(congestion) = 0.147291; P(clear) = 0.277799; P(congestion AND clear) = 0.036574. P(clear | congestion) = 0.248310 and P(temperature > 292 K | congestion) = 0.262958. The product P(congestion) × P(clear) = 0.040917 differs from the observed intersection. Thus exact empirical independence does not hold; this descriptive calculation alone is not a causal or formal inferential test.

## Odds ratio and interpretation

The clear-weather contingency cells are 1,763 congested and 11,628 other records; Clouds has 2,592 congested and 12,572 other records. The odds ratio is (1763/11628)/(2592/12572) = 0.7354. Congestion odds are approximately 26.5% lower for Clear than Clouds in these records. Weather labels, time-of-day composition and repeated observations limit causal interpretation. “Cloudy” here means weather_main exactly equal to Clouds.

## Dashboard and weather findings

The supplied Power BI project defines daily average trends for 2015–2017, hourly means for 2017, weather comparisons, a temperature scatter plot, KPI cards and hour/weather/category slicers. The source contains no blank cells; holiday None is a legitimate category. DateTime is parsed, Hour extracted, Celsius computed and fixed Low/Medium/High categories applied. Total Hours uses distinct timestamps. The native project requires a Windows Desktop refresh and visual check before it is treated as final.

Clouds has the highest raw mean traffic (3,618.45), while Squall has the lowest (2,061.75), a difference of 1,556.70 vehicles. Squall has only four records, so its ranking is unstable. High traffic occurs across a broad plausible temperature range, rather than a narrow temperature band; zero-K readings are sensor errors and should not be interpreted as physical weather.

## Actionable implications

Plan staffing around the observed weekday demand peaks, use lower-demand time windows for corridor maintenance, and retain live operational checks. Do not infer journey speed, queue length or accident likelihood from volume alone. Before expanding the system, obtain road speed, incident labels and additional corridors. SQL outputs, statistics.json and the hourly figures provide the numerical audit trail.