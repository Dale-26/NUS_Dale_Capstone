# NUS_Dale_Capstone

Capstone portfolio covering SQL analytics, a logged Python pipeline, machine learning, explainability and a local deployment simulation. The supplied Metro Interstate dataset contains **48,204 records and 40,575 distinct hours**. No actual accident dataset was provided: the classifier learns a documented **proxy label**, not accident probabilities.

## Results

The validation-selected random forest achieved held-out 2018 MAE **228.62 vehicles/hour** and R² **0.9617**. The linear baseline MAE was 803.61 and the two-hidden-layer neural network MAE was 271.29. Forest proxy-classification F1 was 0.9319. Snow demand error was materially higher than Clear, so overall metrics must not obscure adverse-weather limitations.

## Clone and run

```bash
git clone https://github.com/Dale-26/NUS_Dale_Capstone.git
cd NUS_Dale_Capstone
```

The source, data, reports and models are available directly in the folders below. No archive extraction is needed after cloning. `NUS_Dale_Capstone.zip` is an optional snapshot; the repository folders contain the complete project, including deployment and MLflow artifacts.

## Reproduce

Tested with Python 3.9, NumPy 1.26.4 and pinned dependencies. A recent Python 3.9-compatible environment is needed for the exact lockfile; resolve equivalent packages if using a newer Python version.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m capstone_part2.pipeline --debug
python -m capstone_part1.analyse
python -m capstone_part3.train
python -m unittest discover -s tests -v
```

Run all commands from the repository root. The raw CSV is included; no course login or download token is needed. Model training uses a fixed chronological split: before 2017 / 2017 / 2018. Preprocessing and proxy quartiles are fitted on training data; target-derived features are excluded from predictors. BLAS threads are limited for predictable runtime.

## Inspect the work

- `capstone_part1/`: SQL, SQLite database, annual and holiday query results, statistics/probabilities, a two-page report and native Power BI project source.
- `capstone_part2/`: pipeline, feature engineering, four Matplotlib figures, CLI, sample logs and two-page methodology report.
- `capstone_part3/`: models, evaluation and subgroup CSVs, clustering/rules, SHAP, recommendations, MLflow database, Flask API, monitoring JSON, final report and bias report.
- `data/`: unchanged source CSV, cleaned records and engineered hourly table.
- `tests/`: schema, cleaning, chronological separation, leakage exclusion and API checks.
- `mlruns/`: MLflow model artifacts. The SQLite store preserves metrics and experiment history, including development runs. Existing artifact paths may refer to the original checkout; rerun training after moving the project to regenerate local artifact links. Standalone model files remain available in `capstone_part3/models/`.

## Query the CLI

```bash
python -m capstone_part2.app at '2017-01-01 00:00:00'
python -m capstone_part2.app high --threshold 5500 --limit 5
python -m capstone_part2.app compare
python -m capstone_part2.app recommend --day-type weekday --weather Clear
```

The recommendation compares historically lower-volume windows, not different routes. It needs at least 20 observations and searches 06:00–22:00 by default. Saved model recommendations use training data; the exploratory CLI uses all processed historical hours.

## Deployment and experiment tracking

```bash
python -m capstone_part3.api
mlflow ui --backend-store-uri sqlite:///capstone_part3/mlflow.db --port 5002
```

POST JSON to `http://127.0.0.1:5001/predict`:

```json
{"datetime":"2018-07-10 10:00:00","temp":295,"rain_1h":0,"snow_1h":0,"clouds_all":20,"weather_main":"Clear","holiday_flag":0}
```

This localhost mock-up is not a production service. Predictions assume supplied weather is known. Monitoring reports PASS on observed test errors and ALERT for a documented synthetic +3,000-vehicle error stress test. Thresholds are illustrative and need operational calibration.

## Logging

Each module uses `logging.getLogger(__name__)`. Entry points configure console and file handlers, with timestamp, level, module and message. Files include `capstone_part2/pipeline.log`, `capstone_part2/app.log`, `capstone_part1/analysis.log`, `capstone_part3/training.log` and `capstone_part3/api.log`. DEBUG records internal thresholds; INFO records milestones; WARNING records affected-row counts and recoverable changes; ERROR records failures. `--debug` enables detailed pipeline output. Only direct CLI answers use print.

## Power BI verification still required

Open `capstone_part1/powerbi/Traffic.pbip` in Power BI Desktop on Windows, set DataFile to the raw CSV location, refresh, and check all visuals and filters. The package contains native report/model definitions, Power Query and DAX; **Desktop rendering/refresh is not verified and no verified PBIX is claimed**. Confirm this component before final submission. Microsoft documents PBIR external editing at https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report.

## Data assumptions and responsible use

Raw SQL/statistical results preserve record weighting; the model table consolidates repeated hours using severity-prioritised weather. Volume is neither speed nor observed congestion delay. The fixed dashboard threshold (>5,500) differs intentionally from training-derived quartile labels. The proxy accident label is unsuitable for safety, enforcement or individual decisions. See the bias report for coverage, subgroup error and governance limitations. 
