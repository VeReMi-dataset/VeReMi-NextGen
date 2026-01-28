import argparse
import json
import os
import glob


def split_json_by_timestamp(input_folder, output_folder, split_timestamp):
    train_dir = os.path.join(output_folder, "train")
    val_dir = os.path.join(output_folder, "validation")

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    search_pattern = os.path.join(input_folder, "*.json")
    json_files = glob.glob(search_pattern)

    if not json_files:
        print(f"No JSON files found in: {input_folder}")
        return

    print(f"Split Threshold: {split_timestamp}")
    print(f"Processing {len(json_files)} files...")

    for file_path in json_files:
        filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)

                if not isinstance(data, list):
                    print(f"Skipping {filename}: Root element is not a list.")
                    continue

                train_messages = [m for m in data if int(m['sendTime']) <= split_timestamp]
                val_messages = [m for m in data if int(m['sendTime']) > split_timestamp]

                if train_messages:
                    with open(os.path.join(train_dir, filename), 'w', encoding='utf-8') as f_out:
                        json.dump(train_messages, f_out, indent=2)

                if val_messages:
                    with open(os.path.join(val_dir, filename), 'w', encoding='utf-8') as f_out:
                        json.dump(val_messages, f_out, indent=2)

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("\nProcess completed successfully!")
    print(f"Results stored in: {output_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split vehicle JSON data into train/val folders by timestamp.")

    parser.add_argument("--input", required=True, help="Path to the source JSON files")
    parser.add_argument("--output", required=True, help="Base path for the output folders")
    parser.add_argument("--timestamp", required=True, type=int, help="The integer timestamp cutoff")

    args = parser.parse_args()

    split_json_by_timestamp(args.input, args.output, args.timestamp)
