import csv
import os
import shutil
import argparse

def copy_files_from_csv(csv_file, source_dir, destination_dir):
    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        
        for row in reader:
            if row:  # Check if the row is not empty
                file_name = row[0]
                source_file_path = os.path.join(source_dir, file_name)
                
                if os.path.isfile(source_file_path):  # Check if the file exists
                    destination_file_path = os.path.join(destination_dir, file_name)
                    shutil.copy2(source_file_path, destination_file_path)  # Copy the file
                    print(f"Copied: {file_name}")
                else:
                    print(f"File not found: {file_name}")
        
        file_name = "traceGroundTruthJSON-7.json"
        source_file_path = os.path.join(source_dir, file_name)
                
        if os.path.isfile(source_file_path):  # Check if the file exists
            destination_file_path = os.path.join(destination_dir, file_name)
            shutil.copy2(source_file_path, destination_file_path)  # Copy the file
            print(f"Copied: {file_name}")
        else:
            print(f"File not found: {file_name}")

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command-line attributes.")

    # Add arguments
    parser.add_argument("-csvFile", type=str, required=True)
    parser.add_argument("-sourceDirectory", type=str, required=True)
    parser.add_argument("-destinationDirectory", type=str, required=True)

    args = parser.parse_args()

    csv_file_path = args.csvFile
    source_directory = args.sourceDirectory
    destination_directory = args.destinationDirectory

    copy_files_from_csv(csv_file_path, source_directory, destination_directory)