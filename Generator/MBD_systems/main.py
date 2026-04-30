import argparse
import json
import sys
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any

import pandas as pd

from data_structures import Parameters
import data_processing


def worker_process_json(input_file: str, option: int, params_dict: Dict[str, Any], source_file: str):
    """Worker for JSON-File Processing"""
    try:
        input_path = Path(input_file)
        params = Parameters(**params_dict)
        result = data_processing.process(input_path, option, params, pd.DataFrame(), source_file)
        return {'status': 'ok', 'metrics': result, 'source': source_file}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'source': source_file}


def worker_process_parquet_group(parquet_file: str, option: int, params_dict: Dict[str, Any], source_file: str):
    """Worker for Parquet-Group Processing"""
    try:
        parquet_path = Path(parquet_file)
        params = Parameters(**params_dict)
        df_all = pd.read_parquet(parquet_path)

        if 'source_file' in df_all.columns:
            group_df = df_all[df_all['source_file'] == source_file].copy()
        else:
            group_df = df_all

        result = data_processing.process(parquet_path, option, params, group_df, source_file)
        return {'status': 'ok', 'metrics': result, 'source': source_file}
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'source': source_file}


def evaluate_predictions(scenario_stats):
    total_tp = sum(s.get('tp', 0) for s in scenario_stats)
    total_tn = sum(s.get('tn', 0) for s in scenario_stats)
    total_fp = sum(s.get('fp', 0) for s in scenario_stats)
    total_fn = sum(s.get('fn', 0) for s in scenario_stats)

    total_messages = total_tp + total_tn + total_fp + total_fn

    aggregated_metrics = {
        'tp': total_tp,
        'tn': total_tn,
        'fp': total_fp,
        'fn': total_fn,
        'accuracy': (total_tp + total_tn) / total_messages if total_messages > 0 else 0,
        'precision': total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0,
        'recall': total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0,
    }
    aggregated_metrics['f1'] = (2 * aggregated_metrics['precision'] * aggregated_metrics['recall'] /
                                (aggregated_metrics['precision'] + aggregated_metrics['recall'])
                                if (aggregated_metrics['precision'] + aggregated_metrics['recall']) > 0 else 0)
    return aggregated_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", help="Pfad zu den Eingabedateien", required=True)
    parser.add_argument("--type", help="0 = catch-checks, 1 = legacy checks", required=True)
    parser.add_argument("--train", type=float)
    parser.add_argument("--parameter", required=False,default=None)
    parser.add_argument('--mpr', required=False, type=float)
    parser.add_argument('--msar', required=False, type=float)
    parser.add_argument('--mpdn', required=False, type=float)
    parser.add_argument('--mps', required=False, type=float)
    parser.add_argument('--mpa', required=False, type=float)
    parser.add_argument('--mpd', required=False, type=float)
    parser.add_argument('--mhc', required=False, type=float)
    parser.add_argument('--mdi', required=False, type=float)
    parser.add_argument('--mtd', required=False, type=float)
    parser.add_argument('--pht', required=False, type=float)
    parser.add_argument('--mmru', required=False, type=float)
    parser.add_argument('--mmrd', required=False, type=float)
    parser.add_argument('--msat', required=False, type=float)
    parser.add_argument('--mnrs', required=False, type=float)
    parser.add_argument('--workers', required=False, type=int, default=os.cpu_count() or 4,
                        help="Number of parallel processes (default: CPU count)")
    args = parser.parse_args()

    input_folder = Path(args.input_folder)
    scenario_stats = []

    # Parameter Setup
    if args.train == 1:
        params = Parameters(MAX_PLAUSIBLE_RANGE=args.mpr,
                            MAX_SA_RANGE=args.msar,
                            MAX_PLAUSIBLE_DIST_NEGATIVE=args.mpdn,
                            MAX_PLAUSIBLE_SPEED=args.mps,
                            MAX_PLAUSIBLE_ACCEL=args.mpa,
                            MAX_PLAUSIBLE_DECEL=args.mpd,
                            MAX_HEADING_CHANGE=args.mhc,
                            MAX_DELTA_INTERSECTION=args.mdi,
                            MAX_TIME_DELTA=args.mtd,
                            POS_HEADING_TIME=args.pht,
                            MAX_MGT_RNG_UP=args.mmru,
                            MAX_MGT_RNG_DOWN=args.mmrd,
                            MAX_SA_TIME=args.msat,
                            MAX_NON_ROUTE_SPEED=args.mnrs)
    elif args.parameter is not None:
        with open(args.parameter, 'r') as f:
            data = json.load(f)

        p = data['parameters']

        params = Parameters(
            MAX_PLAUSIBLE_RANGE=p['mpr'],
            MAX_SA_RANGE=args.msar,
            MAX_PLAUSIBLE_DIST_NEGATIVE=p['mpdn'],
            MAX_PLAUSIBLE_SPEED=p['mps'],
            MAX_PLAUSIBLE_ACCEL=p['mpa'],
            MAX_PLAUSIBLE_DECEL=p['mpd'],
            MAX_HEADING_CHANGE=p['mhc'],
            MAX_DELTA_INTERSECTION=p['mdi'],
            MAX_TIME_DELTA=p['mtd'],
            POS_HEADING_TIME=p['pht'],
            MAX_MGT_RNG_UP=p['mmru'],
            MAX_MGT_RNG_DOWN=p['mmrd'],
            MAX_SA_TIME=args.msat,
            MAX_NON_ROUTE_SPEED=p['mnrs']
        )
    else:
        params = Parameters()

    params_dict = vars(params)
    count = 0
    max_workers = args.workers

    print(f"Starting processing with {max_workers} workers...", file=sys.stderr)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        parquet_files = list(input_folder.glob('*.parquet'))

        if parquet_files:
            # Parquet Verarbeitung
            parquet_file = parquet_files[0]
            df_all = pd.read_parquet(parquet_file)

            if 'source_file' in df_all.columns:
                grouped = df_all.groupby('source_file')
                total_files = len(grouped)
                for vehicle_id, _ in grouped:
                    f = executor.submit(worker_process_parquet_group, str(parquet_file),
                                        int(args.type), params_dict, vehicle_id)
                    futures[f] = vehicle_id
            else:
                total_files = 1
                source_name = parquet_file.stem
                f = executor.submit(worker_process_parquet_group, str(parquet_file),
                                    int(args.type), params_dict, source_name)
                futures[f] = source_name
        else:
            # JSON Verarbeitung
            json_files = [f for f in input_folder.glob('*.json')
                          if "ground_truth" not in f.name.lower()]
            total_files = len(json_files)

            for json_file in json_files:
                source_name = json_file.stem
                f = executor.submit(worker_process_json, str(json_file),
                                    int(args.type), params_dict, source_name)
                futures[f] = source_name

        # Ergebnisse sammeln
        for future in as_completed(futures):
            source = futures[future]
            try:
                res = future.result()
                if res.get('status') == 'ok':
                    scenario_stats.append(res.get('metrics', {}))
                    count += 1
                    print(f"Processed prediction for file {count}/{total_files}: {source}", file=sys.stderr)
                else:
                    count += 1
                    print(f"[ERROR] {source}: {res.get('error')}", file=sys.stderr)
            except Exception as e:
                count += 1
                print(f"[ERROR] processing {source}: {e}", file=sys.stderr)

    # Auswertung
    aggregated_metrics = evaluate_predictions(scenario_stats)
    print(aggregated_metrics['f1'])

    if args.train == 0:
        output_dir = input_folder.parent / "results"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{input_folder.name}_predicted.json"
        print(f"Saved in {output_file}")
        with open(output_file, 'w') as f:
            json.dump(aggregated_metrics, f, indent=4)


if __name__ == "__main__":
    main()