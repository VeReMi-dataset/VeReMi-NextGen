# Parameter Optimization

Hyperparameter optimization of MBD system parameters using Optuna.

## Files

| File                                         | Function                                 |
|----------------------------------------------|------------------------------------------|
| `test.py`                                    | Optuna optimization, calls MBD_systems   |
| `Bin_generator/convert_to_bin.py`            | JSON → Parquet conversion                |
| `Splitting/csv_table.py`                     | Generate statistics per file             |
| `Splitting/train_validation_test_dataset.py` | Train/Validation/Test split with KS test |
| `Splitting/copy_files.py`                    | Copy files after split                   |

## Workflow

```
1. JSON → Parquet               (convert_to_bin.py)
2. Statistics                   (csv_table.py)
3. Train/Validation/Test Split  (train_validation_test_dataset.py)
4. Copy files                   (copy_files.py)
5. Optimization                 (test.py)
```

## 1. JSON to Parquet (`convert_to_bin.py`)

Aggregates all JSON files from a folder into a single Parquet file for faster I/O access.

**Process:**
- Iterates through all files in the input folder (skips ground truth files)
- Loads each JSON file and adds a `source_file` column for traceability
- Flattens nested JSON structures using `pd.json_normalize()`
- Writes all messages to a Parquet file with Snappy compression

**Output:** Statistics on processed files, message count, and file size.

## 2. Generate Statistics (`csv_table.py`)

Extracts statistical features from each JSON file for subsequent distribution analysis.

**Calculated metrics per file:**
- **avgRcvMsg**: Average time between received messages
- **numMessages**: Total number of messages
- **numMaliciousMessages**: Number of attacker messages (`attacker = true`)
- **Driver Profile Distribution**: Count of NORMAL, AGGRESSIVE, and CAUTIOUS profiles

**Output:** `output.csv` with one row per file.

## 3. Train/Validation/Test Split (`train_validation_test_dataset.py`)

Splits the dataset into train/validation/test sets and ensures similar distributions across all subsets using the Kolmogorov-Smirnov test.

**Split Algorithm:**
- Files are randomly shuffled
- Splitting is based on message count (not file count) to ensure balanced data volume
- Files are sequentially assigned to train, validation, or test until the respective ratio is reached

**Distribution Validation:**
- 30,000 random splits are performed
- For each split, pairwise KS tests are executed between all combinations (Train↔Val, Train↔Test, Val↔Test)
- All 6 metrics are tested: avgRcvMsg, numMessages, numMaliciousMessages, and the three driver profiles
- A split is only valid if all p-values > 0.05 (null hypothesis: identical distribution)
- The split with the highest average p-value is selected

**Output:**
- `train.csv`, `val.csv`, `test.csv` – File lists
- `p_d_values.csv` – KS test results (p-values and D-statistics)

## 4. Copy Files (`copy_files.py`)

Copies the actual JSON files based on the split CSVs into separate folders.

**Process:**
- Reads filenames from the first column of each CSV
- Copies the corresponding files from source to destination folder

## 5. Optuna Optimization (`test.py`)

Performs hyperparameter optimization using Optuna to find the best MBD parameters.

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

| Parameter | Range         | Unit | Description                 |
|-----------|---------------|------|-----------------------------|
| mdi       | 1.0 - 5.0     | s    | MAX_DELTA_INTERSECTION      |
| mpr       | 300.0 - 500.0 | m    | MAX_PLAUSIBLE_RANGE         |
| mps       | 30.0 - 70.0   | m/s  | MAX_PLAUSIBLE_SPEED         |
| mpa       | 3.0 - 10.0    | m/s² | MAX_PLAUSIBLE_ACCEL         |
| mpd       | 3.0 - 20.0    | m/s² | MAX_PLAUSIBLE_DECEL         |
| mhc       | 45.0 - 145.0  | °    | MAX_HEADING_CHANGE          |
| mpdn      | -5.0 - 0.0    | m    | MAX_PLAUSIBLE_DIST_NEGATIVE |
| mtd       | 1.0 - 5.0     | s    | MAX_TIME_DELTA              |
| pht       | 1.0 - 5.0     | s    | POS_HEADING_TIME            |
| mmru      | 0.0 - 7.0     | m    | MAX_MGT_RNG_UP              |
| mmrd      | 0.0 - 7.0     | m    | MAX_MGT_RNG_DOWN            |
| mnrs      | 0.0 - 3.0     | m/s  | MAX_NON_ROUTE_SPEED         |

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
```
