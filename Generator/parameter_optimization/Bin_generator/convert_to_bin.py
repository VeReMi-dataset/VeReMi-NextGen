import json
import pandas as pd
from pathlib import Path
import argparse
import sys


def json_folder_to_parquet(input_folder, output_file):
    all_data = []
    file_count = 0

    json_files = list(Path(input_folder).glob('*'))
    total_files = len([f for f in json_files if 'ground_truth' not in f.name])

    for file_path in json_files:
        if 'ground_truth' in file_path.name:
            continue

        file_count += 1
        print(f"Verarbeite {file_count}/{total_files}: {file_path.name}", file=sys.stderr)

        try:
            with open(file_path, 'r') as f:
                messages = json.load(f)

            if isinstance(messages, dict):
                messages = [messages]

            for msg in messages:
                msg['source_file'] = file_path.stem

            all_data.extend(messages)

        except Exception as e:
            print(f"Error at {file_path.name}: {e}", file=sys.stderr)
            continue

    df = pd.json_normalize(all_data, sep='_')

    df.to_parquet(output_file, compression='snappy', index=False)

    file_size_gb = Path(output_file).stat().st_size / (1024 ** 3)
    print(f"\n=== Finished ===")
    print(f"Files processed: {file_count}")
    print(f"Total messages: {len(df)}")
    print(f"Comumns: {len(df.columns)}")
    print(f"Unique source_files: {df['source_file'].nunique()}")
    print(f"File size: {file_size_gb:.2f} GB")
    print(f"Messages per file: {len(df) / df['source_file'].nunique():.1f}")

    return df


def main():
    parser = argparse.ArgumentParser(description='Convert JSON-Files to Parquet')
    parser.add_argument('input_folder', help='Directory with JSON-Files')
    parser.add_argument('-o', '--output', default='combined_data.parquet',
                        help='Output Parquet-Datei (default: combined_data.parquet)')

    args = parser.parse_args()

    if not Path(args.input_folder).exists():
        print(f"Error: Directory {args.input_folder} does not exist!")
        sys.exit(1)

    df = json_folder_to_parquet(args.input_folder, args.output)


if __name__ == "__main__":
    main()
