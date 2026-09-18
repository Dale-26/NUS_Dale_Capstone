# Smart city traffic intelligence findings

## Executive assessment

A connected pipeline turns the supplied traffic and weather records into auditable analytics, demand predictions, a proxy classification demonstration, travel-timing recommendations and a local deployment simulation. A random forest is selected using 2017 validation MAE, with approximately 229 vehicles/hour MAE on the later 2018 test period. This is a retrospective single-corridor demonstration. It is not an operational accident-risk or route-selection system.

## Analytics and engineering foundation

Part 1 provides SQLite queries, recorded annual totals, holiday comparisons, descriptive statistics and probability calculations. Part 2 removes exact duplicates and physically implausible readings with logged monthly imputation, resolves repeated timestamps, and supplies reproducible features and plots. Annual totals are not directly comparable because observation coverage differs. The raw temperature correlation is weak (0.1303), and weather associations are confounded by time and season.

## Evaluation design

Chronological split: 25,329 observed hours before 2017 for training; 8,713 hours in 2017 for validation; 6,533 hours in 2018 for final testing. All observations sharing a timestamp stay in one set. Imputation references, quartile labels, encoders and scalers are fitted on training data. Models use common time/weather/holiday features, including both hour and weekday cyclic encodings. Traffic volume, its buckets and the proxy target are excluded from predictors. Models are selected on validation, not test scores.

## Prediction setting and limitations

Weather variables are contemporaneous observations. The measured scores therefore assess conditional demand estimation with known weather, not an evaluated long-horizon forecast. Prospective use needs weather forecasts and a new evaluation that includes forecast error. The forest cannot extrapolate reliably to other roads, new capacity regimes or unprecedented conditions.

## Regression comparison

ridge: test MAE 803.61 vehicles/hour; R² 0.7347; validation MAE 802.18.

forest_regression: test MAE 228.62 vehicles/hour; R² 0.9617; validation MAE 238.84.

neural_network: test MAE 271.29 vehicles/hour; R² 0.9528; validation MAE 282.09.

## Proxy classification comparison

logistic: accuracy 0.9581, precision 0.7295, recall 0.9904, F1 0.8401, ROC AUC 0.9940.

forest_classifier: accuracy 0.9839, precision 0.8821, recall 0.9876, F1 0.9319, ROC AUC 0.9969.

## Proxy target construction

Training traffic quartiles define Low, Medium, High and Severe volume groups. high_risk is one only when High/Severe volume co-occurs with Thunderstorm, Squall or Snow, or with a low-visibility category (Fog, Mist, Haze or Smoke). These sets operationalise terms that the instructions leave unspecified. The same fixed training thresholds are applied to validation/test data. Strong scores reflect learning a constructed rule partly defined by observed weather; they are not evidence of accident prediction accuracy.

## Neural network choice

A dense neural network with hidden layers of 64 and 32 units predicts demand using the same features. This satisfies the demand-network option without claiming an LSTM. Two hidden layers, standardised numeric inputs, Adam optimisation, fixed seed, batch size 256 and 100 epochs make the baseline reproducible. The network is compared directly with the linear and forest models; convergence warnings and the epoch budget are retained as training limitations.

## Clustering traffic conditions

K-means is fitted to standardised hour sine/cosine, severe-weather, low-visibility and volume features. Candidates k=3,4,5 are compared using a fixed 3,000-row silhouette sample. The selected four clusters separate lower-volume ordinary weather (mean about 1,568), higher-volume ordinary weather (4,938), low-visibility conditions (3,028), and severe weather (2,994 vehicles/hour). Binary weather indicators influence this geometry; these are descriptive condition groups, not validated risk classes.

## Association rule mining

Exact enumeration mines one-, two- and three-variable antecedents from time period, day type and weather. Minimum support is 1% and confidence 60%. The strongest observed rule is weekend night → Low congestion, with support 0.0647, confidence 0.8971 and lift 3.5857, representing 1,639 training records. Weekday morning with Mist → Severe has confidence 0.8781 and lift 3.5131. Lift compares rule confidence with the overall consequent rate; it does not establish cause or out-of-sample stability.

## Explainability

SHAP TreeExplainer explains a comparable random forest trained on the same demand problem. This is explicitly an explanation of the forest, not of the neural network’s individual predictions. On a fixed random sample of 300 held-out hours, hour cosine, hour and hour sine dominate mean absolute SHAP importance, followed by weekday and weekend features. Correlated cyclic representations divide importance across related variables. The plot and feature importance CSV are included; SHAP attribution is not causal evidence.

## Advanced technique and MLOps

MLflow is used as both the chosen advanced technique and the experiment-tracking layer. A local SQLite tracking store records algorithms, hyperparameters, split dates, metrics and version v1; model artifacts and a deployment manifest are saved. This improves auditability and comparisons, but it does not by itself provide governance, production monitoring or automated model approval. Distinct algorithms have separate versioned artifacts, with the best validation model copied to deployment.joblib. Interrupted development runs may remain in the experiment history and are not selected results.

## Deployment and monitoring

A Flask mock-up exposes POST /predict with timestamp, Kelvin temperature, precipitation, cloud cover, weather and holiday flag. It validates types and ranges and returns a demand prediction with units/version. The service binds to localhost and is tested with valid and invalid payloads. Monitoring compares current MAE with 1.25 times validation MAE and checks feature KS statistics against 0.20. Observed test data passes; adding 3,000 vehicles to predictions triggers an ALERT. These are demonstration thresholds requiring operational calibration, and error monitoring assumes labels become available.

## Travel timing recommendation

The recommendation engine uses training-period historical means by day type, weather and hour. It limits the default search to 06:00–22:00 and requires at least 20 supporting records. It returns the lowest-volume supported one-hour window, sample size and a plain-language limitation. See recommendations.txt for computed examples. This uses analytical outputs to support departure timing on one corridor; it does not compare routes or guarantee lower travel time. Weather-specific support is checked before any recommendation.

## Responsible use and governance

The dedicated bias report examines geographic/temporal coverage, sparse weather groups, constructed-label risks and subgroup errors. Models cannot establish demographic fairness because relevant group attributes and exposure data are absent. A city should require model-owner approval, documented data provenance, incident response and human review before operational use. No automated road control, public safety warning or personal travel restriction is supported by this demonstration.

## Sustainability

The tabular forest and compact dense network use a small feature set and modest model sizes. Training duration is logged, but no energy meter was used, so no carbon savings are claimed. Avoid frequent unnecessary retraining; monitor drift and retrain only after investigation. Any emissions benefit from travel timing remains a hypothesis until measured with actual speed, vehicle mix and induced-demand effects.

## Delivery and remaining verification

The repository contains raw data, SQL/database outputs, pipeline and CLI, figures, models, SHAP, clustering/rules, MLflow evidence, Flask simulation, monitoring and reports. The generated Power BI PBIP project still needs a Windows Desktop refresh and visual validation; no verified PBIX is claimed. The submission template must contain the correct student name and an accessible repository URL before the single allowed Canvas attempt is used.

## Source and reproducibility

Data and task definitions are from the supplied Emeritus Week 33 capstone materials. Results are generated from that CSV; no external accident dataset is used. Method documentation: pandas.pydata.org/docs; scikit-learn.org/stable; shap.readthedocs.io; mlflow.org/docs/latest; flask.palletsprojects.com; and learn.microsoft.com/en-us/power-bi/developer/projects/projects-report. README commands regenerate the outputs. 