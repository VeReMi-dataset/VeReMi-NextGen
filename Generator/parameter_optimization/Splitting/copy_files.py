import csv
import os
import shutil
import argparse


def copy_files_from_csv(csv_file, source_dir, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                file_name = row[0]
                source_file_path = os.path.join(source_dir, file_name)

                if os.path.isfile(source_file_path):
                    destination_file_path = os.path.join(destination_dir, file_name)
                    shutil.copy2(source_file_path, destination_file_path)
                    print(f"Copied: {file_name}")
                else:
                    print(f"File not found: {file_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files for train/validation/test split.")

    parser.add_argument("-trainCsv", type=str, required=True)
    parser.add_argument("-valCsv", type=str, required=True)
    parser.add_argument("-testCsv", type=str, required=True)
    parser.add_argument("-sourceDirectory", type=str, required=True)
    parser.add_argument("-trainDestination", type=str, required=True)
    parser.add_argument("-valDestination", type=str, required=True)
    parser.add_argument("-testDestination", type=str, required=True)

    args = parser.parse_args()

    print("Copying train files...")
    copy_files_from_csv(args.trainCsv, args.sourceDirectory, args.trainDestination)

    print("\nCopying validation files...")
    copy_files_from_csv(args.valCsv, args.sourceDirectory, args.valDestination)

    print("\nCopying test files...")
    copy_files_from_csv(args.testCsv, args.sourceDirectory, args.testDestination)