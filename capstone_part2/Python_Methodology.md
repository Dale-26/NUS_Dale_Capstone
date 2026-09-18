# Reproducible traffic data pipeline

## Method and data lineage

The pipeline preserves the supplied CSV unchanged, validates all nine required columns before processing, and writes cleaned records and a separate hourly feature table. keep_default_na=False preserves the legitimate holiday string None. Invalid dates and targets are removed; categorical whitespace and weather-description case are standardised. Exact duplicate rows are removed before hourly consolidation.

## Cleaning outcomes

The successful run removed 17 exact duplicates, standardised 1,730 weather descriptions, imputed 10 temperature readings outside 200–330 K, and imputed one rainfall reading above 9,000 mm. Temperature, precipitation and cloud-cover bounds are explicit documented validation rules. Monthly medians are used for replacements, with a global reference fallback where a month has no valid data. No invalid dates or traffic targets were found. These physical plausibility thresholds are assumptions and should be reviewed for other locations.

## Repeated hours and holiday semantics

After exact deduplication, 7,612 additional weather records share already observed timestamps. The model table retains one row per hour, using a deterministic severity priority to preserve adverse weather signals; conflicting traffic counts would use a median. This yields 40,575 hours. Holiday markers are propagated across the observed calendar date. Missing hours are not manufactured, and date gaps must remain visible when interpreting annual totals.

## Feature engineering

Features include hour, weekday, month, weekend, sine/cosine encodings of hour and weekday, temperature Celsius, weather one-hot indicators, severe-weather and visibility flags, and scaled temperature/cloud cover. Exploratory quartiles are 1,248.5, 3,427 and 4,952 vehicles for Low, Medium, High and Severe categories. These differ deliberately from the dashboard’s fixed 4,500/5,500 thresholds. ML preprocessing is refitted on training records only; target-derived fields are never predictors.

## Logging and failure handling

Each module defines logging.getLogger(__name__). Entry points configure console and file handlers with timestamp, severity, module and message. INFO records dimensions, milestones and figure paths; WARNING records the count and reason for every recoverable modification; DEBUG exposes reference quartiles and scaling values; ERROR records unrecoverable failures. Debug values are absent unless --debug is supplied. File I/O, schema and parsing failures return a nonzero exit status without a bare except clause. MLflow migration logging is reset at its boundary to preserve the training audit trail.

## Visual evidence

figures/hourly.png compares weekday and weekend hourly means and supports time-aware planning. figures/weather.png shows hourly means by selected weather report; scarce categories require caution. figures/temperature.png shows broad overlap and a weak marginal temperature association after removing impossible readings. figures/distribution.png documents the wide distribution and separation of lower overnight versus higher daytime volumes. These are descriptive, not estimates of causal weather effects.

## Mini application and reproducibility

The CLI supports at, high, compare and recommend. Example: python -m capstone_part2.app at "2017-01-01 00:00:00". A strict timestamp parser rejects malformed input. The high query validates thresholds and limits; absent timestamps return a clear message. CLI examples and a sample pipeline.log are included. Actual answers can use print; internal progress uses logging.

Run from the repository root using the pinned requirements, then execute the pipeline, Part 1 analysis and Part 3 training modules. Incremental Git commits document development stages. Unit checks cover invalid schemas, cleaning, timestamp separation, target leakage exclusions and valid/invalid API requests. No private credentials or course download tokens are required to reproduce the project.