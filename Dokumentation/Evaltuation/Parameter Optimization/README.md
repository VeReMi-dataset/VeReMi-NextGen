# Parameter Optimization

Hyperparameter optimization of MBD system parameters using Optuna.

## Files

| File | Function |
|------|----------|
| `test.py` | Optuna optimization, calls MBD_systems |
| `Bin_generator/convert_to_bin.py` | JSON → Parquet conversion |
| `Splitting/csv_table.py` | Generate statistics per file |
| `Splitting/train_test_dataset.py` | Train/test split with KS test |
| `Splitting/copy_files.py` | Copy files after split |

## Workflow

```
1. JSON → Parquet    (convert_to_bin.py)
2. Statistics        (csv_table.py)
3. Train/Test Split  (train_test_dataset.py)
4. Copy files        (copy_files.py)
5. Optimization      (test.py)
```

## 1. JSON to Parquet

```bash
python Bin_generator/convert_to_bin.py ./json_folder -o output.parquet
```

Aggregates all JSON files into a single Parquet file for faster access.

## 2. Generate Statistics

```bash
python Splitting/csv_table.py -path ./json_folder -attack attackName
```

Output: `<attack>_output.csv` with columns:
- Filename
- Average message rate
- Number of messages
- Number of malicious messages
- Driver profile distribution (Normal, Aggressive, Cautious)

## 3. Train/Test Split

```bash
python Splitting/train_validation_test_dataset.py -file stats.csv -attack attackName -division 0.7
```

Uses **Kolmogorov-Smirnov test** to ensure train and test sets have similar distributions. Runs 30,000 iterations and selects the split with highest average p-value (all p > 0.05).

Output:
- `<attack>_train.csv`
- `<attack>_test.csv`  
- `<attack>_p_d_values.csv`

## 4. Copy Files

```bash
python Splitting/copy_files.py -csvFile train.csv -sourceDirectory ./all -destinationDirectory ./train
```

## 5. Optuna Optimization

```bash
python test.py <input_folder> <output_file> <type>
```

**Example:**
```bash
python test.py ./train_data results.json 0
```

### Optimized Parameters

| Parameter | Search Space |
|-----------|--------------|
| mdi | 1.0 - 5.0 |
| mpr | 300.0 - 500.0 |
| mps | 30.0 - 70.0 |
| mpa | 3.0 - 10.0 |
| mpd | 3.0 - 20.0 |
| mhc | 45.0 - 145.0 |
| mpdn | -5.0 - 0.0 |
| mtd | 1.0 - 5.0 |
| pht | 1.0 - 5.0 |
| mmru | 0.0 - 7.0 |
| mmrd | 0.0 - 7.0 |
| mnrs | 0.0 - 3.0 |

### Configuration

```python
n_trials = 100000    # Number of trials
n_threads = 15       # Parallel jobs
direction = "maximize"  # Maximize F1-Score
```

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

## Using Optimized Parameters

```bash
python MBD_systems/main.py --input_folder ./test --type 0 --parameter best_trial.json
```
