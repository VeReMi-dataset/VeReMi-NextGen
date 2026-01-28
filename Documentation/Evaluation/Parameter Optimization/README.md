# Parameter Optimization

Documentation of the hyperparameter optimization for the MBD system parameters using Optuna based on [1].

## Files

| File                              | Function                                 |
|-----------------------------------|------------------------------------------|
| `test.py`                         | Optuna optimization, calls MBD_systems   |
| `split_into_train_val.py`         | Creates Train and Validation parts by splitting at an defined timestamp |
| `Bin_generator/convert_to_bin.py` | JSON → Parquet conversion                |

> The optimization directly uses the **already provided Train or Validation datasets**.

## Workflow


## 1. JSON to Parquet (`convert_to_bin.py`)

Aggregates all JSON files from a folder into a single Parquet file for faster I/O access.

**Process:**
- Iterates through all files in the input folder (skips ground truth files)
- Loads each JSON file and adds a `source_file` column for traceability
- Flattens nested JSON structures using `pd.json_normalize()`
- Writes all messages to a Parquet file with Snappy compression

**Output:** Statistics on processed files, message count, and file size.

## 2. Optuna Optimization (`test.py`)

Performs hyperparameter optimization using Optuna to find the best MBD parameters.

**Dataset usage:**
- The optimization is executed on an **existing dataset split**.
- Depending on the experiment setup, either the **Train** or the **Validation** dataset is used as input.

**Optimization Process:**
- Optuna samples parameters from defined search spaces
- For each trial, the MBD system is called as a subprocess
- The F1 score is read from standard output and used as the optimization objective
- On each new best score, `<name>_best_trial.json` is updated

**Configuration:**
- 100,000 trials
- 50 parallel jobs
- Optimization objective: Maximize F1 score

### Parameter Search Space

| Parameter | Range         | Unit | 
|-----------|---------------|------|
| mdi       | 1.0 - 5.0     | s    | 
| mpr       | 300.0 - 500.0 | m    |
| mps       | 30.0 - 70.0   | m/s  |
| mpa       | 3.0 - 10.0    | m/s² |
| mpd       | 3.0 - 20.0    | m/s² | 
| mhc       | 45.0 - 145.0  | °    | 
| mpdn      | -5.0 - 0.0    | m    |
| mtd       | 1.0 - 5.0     | s    | 
| pht       | 1.0 - 5.0     | s    | 
| mmru      | 0.0 - 7.0     | m    | 
| mmrd      | 0.0 - 7.0     | m    |
| mnrs      | 0.0 - 3.0     | m/s  |

### Output

`<name>_best_trial.json`:
```json
{
  "trial_number": 42,
  "f1_score": 0.85,
  "parameters": {
    "mdi": 4.2,
    "mpr": 418.0,
    ...
  }
}



## References

1. A. Hermann, N. Trkulja, D. Eisermann, B. Erb, and F. Kargl,  *Hyperparameter Optimization-Based Trust Quantification for Misbehavior Detection Systems*, In Proceedings of the 2025 IEEE International Conference on Intelligent Transportation Systems (ITSC), Gold Coast, Australia,  https://doi.org/10.18725/OPARU-57502
