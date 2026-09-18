# Bias fairness and governance assessment

## Coverage and representation

The data describes one westbound I-94 corridor near Minneapolis–St Paul, with incomplete historical coverage and repeated weather reports. It does not represent a citywide network, contemporary traffic, other travel modes, demographics or socioeconomic exposure. Different years contain different numbers of observed hours. Missingness can bias seasonal and annual comparisons; dropping repeated weather reports changes how weather categories are represented.

## Proxy label risks

No accident outcomes are available. The classification target combines volume quartiles with hand-chosen adverse weather labels. Congestion volume is not a direct measurement of speed, queue length or crash probability; severe congestion can even coincide with lower vehicle counts. The proxy definition partly reuses weather predictors, so excellent classification scores mainly indicate recovery of the engineered rule. Never label the returned score a crash probability or use it for enforcement, insurance or road safety decisions.

## Uneven errors

Held-out demand MAE is approximately 202 vehicles/hour in Clear, 225 in Clouds and 530 in Snow. Snow error is about 2.6 times Clear error, suggesting weaker reliability precisely under adverse conditions. Smoke has only two test observations and an unstable MAE around 450; there are no test Squall observations to validate that category. Weather and hour subgroup CSVs expose support and error rather than relying only on an overall score. Sparse categories should prompt abstention or explicit uncertainty.

## What fairness can and cannot mean here

Condition-level performance comparisons are an operational reliability audit, not proof of demographic fairness. There are no protected-group attributes, trip origins, transit accessibility measures or individual outcomes. Assessing distributional impacts would require an appropriately governed new dataset and stakeholder participation. Training-only thresholds and chronological splits reduce leakage but do not correct coverage bias.

## Controls before operational use

Assign a named model owner and data steward; verify sensor calibration, legal data-use rights and retention; record versions, thresholds and approvals. Validate on current data and other corridors, acquire actual incident and speed labels, and establish performance requirements for each weather/time subgroup. Use shadow deployment and human-reviewed alerts first. Provide a rollback path, documented incident process, periodic audits and a way for operators to question model outputs.

## Monitoring and transparency

The local PASS/ALERT demonstration uses error and distribution thresholds. An alert should trigger investigation, not automatic retraining or road controls. Delayed labels, holiday shifts, roadworks and sensor failures can create false alarms. Keep monitoring windows and baseline periods explicit. Report sample sizes, uncertainty and missing categories alongside headline accuracy, and document every change to the proxy label.

## Sustainability tradeoffs

Compact tabular models reduce computation compared with unnecessarily large architectures. Limit repeated fits and unnecessary feature storage; use monitored, scheduled retraining rather than continuous retraining by default. Model storage and training times are observable resource indicators, not carbon estimates. The project has no measured energy or emissions data and makes no quantified environmental claim. Departure-time suggestions may shift congestion rather than eliminate it; evaluate network-wide effects before assuming sustainability benefits.

## Deployment boundary

The Flask API is a localhost educational mock-up without production authentication, service-level guarantees or calibrated uncertainty. Use only trusted generated model files, since joblib deserialisation executes Python objects. The current recommendation system advises timing on a single corridor, with a minimum-support rule. The work supports analysis and further validation; it does not justify safety-critical automation.