# Evaluation

Documentation of the evaluation of the VeReMi NextGen dataset, incl. the MBD Systems used, the way the parameters were optimized
and the results.

### [CaTCH-MBD System](./CaTCH-MBD%20System)

Overview of the CaTCH-MBD system:

- Modular implementation of plausibility and consistency checks for V2X messages
- Comparison between uncertainty-aware CaTCH checks and binary legacy checks
- Definition of detection parameters and decision logic
- Detailed description of implemented checks and their mathematical foundations

### [Parameter Optimization](./Parameter%20Optimization)

Parameter optimization workflow for CaTCH:

- Data preprocessing pipeline
- Dataset splitting into train/validation/test using defined time periods
- Hyperparameter optimization with Optuna targeting F1 score
- Definition of parameter search spaces

### [Results](./Results)

Results acquired in the process of generating VeReMi NextGen

- Characteristics of driver profiles
- Optimized Parameter for Evaluation
- MBD Results for VeReMi NextGen
- Comparison with VeReMi Extension
