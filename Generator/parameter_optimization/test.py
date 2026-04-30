import argparse
from pathlib import Path

import optuna
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("input_folder", help="Pfad zu den Eingabedateien")
parser.add_argument("output_file")
parser.add_argument("type", help="0 = catch-checks, 1 = legacy checks")
args = parser.parse_args()

results = []
train = 1
pattern = args.type
path = args.input_folder


def format_float_safe(value):
    formatted = f"{value:.15f}"
    formatted = formatted.rstrip('0').rstrip('.')
    return formatted


import json

# Global variable to track best score
best_score = -1


def objective(trial):
    global best_score

    mdi = trial.suggest_float('mdi', 1, 5.0)
    mpr = trial.suggest_float('mpr', 300.0, 500.0)
    mps = trial.suggest_float('mps', 30.0, 70.0)
    mpa = trial.suggest_float('mpa', 3.0, 10.0)
    mpd = trial.suggest_float('mpd', 3.0, 20.0)
    mhc = trial.suggest_float('mhc', 45.0, 145.0)
    mpdn = trial.suggest_float('mpdn', -5, 0)
    mtd = trial.suggest_float('mtd', 1, 5)
    pht = trial.suggest_float('pht', 1, 5)
    mmru = trial.suggest_float('mmru', 0, 7)
    mmrd = trial.suggest_float('mmrd', 0, 7)
    mnrs = trial.suggest_float('mnrs', 0, 3)

    command = [
        'python',
        '../MBD_systems/main.py',
        '--input_folder', str(path),
        '--type', str(pattern),
        '--train', str(train),
        '--mdi', format_float_safe(mdi),
        '--mpr', format_float_safe(mpr),
        '--mps', format_float_safe(mps),
        '--mpa', format_float_safe(mpa),
        '--mpd', format_float_safe(mpd),
        '--mhc', format_float_safe(mhc),
        '--mpdn', format_float_safe(mpdn),
        '--mtd', format_float_safe(mtd),
        '--pht', format_float_safe(pht),
        '--mmru', format_float_safe(mmru),
        '--mmrd', format_float_safe(mmrd),
        '--mnrs', format_float_safe(mnrs)
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        print(f"ERROR: Script has returned error code {process.returncode}")
        print(f"STDERR: {process.stderr}")
        print(f"STDOUT: {process.stdout}")
        raise RuntimeError(f"Script failed with error code {process.returncode}")

    output = process.stdout.strip().splitlines()
    f1_score = float(output[0])

    if f1_score > best_score:
        best_score = f1_score
        best_params = {
            'trial_number': trial.number,
            'f1_score': f1_score,
            'parameters': {
                'mdi': mdi,
                'mpr': mpr,
                'mps': mps,
                'mpa': mpa,
                'mpd': mpd,
                'mhc': mhc,
                'mpdn': mpdn,
                'mtd': mtd,
                'pht': pht,
                'mmru': mmru,
                'mmrd': mmrd,
                'mnrs': mnrs
            }
        }

        name = Path(args.output_file).stem

        with open(f'{name}_best_trial.json', 'w') as f:
            json.dump(best_params, f, indent=2)

    return f1_score


# Set up the study with multi-threading
def run_optimization():
    # Create a study object
    study = optuna.create_study(directions=["maximize"])  # or 'minimize', depending on your objective
    
    # Define the number of trials and the number of threads
    n_trials = 100000
    n_threads = 15  # Adjust the number of threads based on your CPU cores

    study.optimize(objective, n_trials=n_trials, n_jobs=n_threads, show_progress_bar=True)

    best_trial = study.best_trial

    output = path.parent/args.output_file
    with open(output, 'w') as f:
        json.dump({
            'best_f1_score': best_trial.value,
            'best_params': best_trial.params,
            'trial_number': best_trial.number
        }, f, indent=2)


def write_list_to_file(strings, file_path):
    with open(file_path, 'w') as file:
        for string in strings:
            file.write(string + '\n')  # Write each string follow    


if __name__ == "__main__":
    run_optimization()

    write_list_to_file(results, "output/train_precision_recall.json")
