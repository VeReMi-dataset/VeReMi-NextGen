import csv
import json
import os
import argparse
import pandas as pd

def read_files_in_directory(directory_path):
    """
    Iterates through all files in a directory, opens each file,
    and reads its contents line by line.

    Args:
        directory_path (str): Path to the directory containing files.
    """

    csvData = []
    try:
        # Iterate through all files in the directory
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)

            numMessages = 0
            numMaliciousMessages = 0
            sumRcvMsgDistance =0.0
            lastTimeStamp = 0.0
            avgRcvMsg = 0.0

            if "traceGroundTruthJSON" in file_name:
                continue

            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                print(f"\nReading file: {file_name}")
                try:
                    with open(file_path, 'r') as file:
                        messages = json.load(file)  # Load entire JSON array
                        df = pd.json_normalize(messages, sep='_')
                        df = df.drop(['receiver_pos', 'receiver_pos_noise', 'receiver_spd', 'receiver_spd_noise', 'receiver_acl', 'receiver_acl_noise', 'receiver_hed', 'receiver_hed_noise', 'receiver_driversProfile'], axis=1)

                        df['rcvTime'] = df['rcvTime'].astype(int)
                        df['sendTime'] = df['sendTime'].astype(int)
                        df['sender'] = df['sender_id'].astype(str)
                        df['sender_alias'] = df['sender_alias'].astype(int)
                        df['messageID'] = df['messageID'].astype(int)
                        df['attacker'] = df['attacker'].astype(bool)

                        # Sender Felder
                        df['pos'] = df['sender_pos'].apply(lambda x: [float(i) for i in x.split(',')])
                        df['pos_noise'] = df['sender_pos_noise'].apply(lambda x: [float(i) for i in x.split(',')])
                        df['spd'] = df['sender_spd'].astype(float)
                        df['spd_noise'] = df['sender_spd_noise'].astype(float)
                        df['acl'] = df['sender_acl'].astype(float)
                        df['acl_noise'] = df['sender_acl_noise'].astype(float)
                        df['hed'] = df['sender_hed'].astype(float)
                        df['hed_noise'] = df['sender_hed_noise'].astype(float)
                        df['driversProfile'] = df['sender_driversProfile'].astype(str)

                        profile_counts = df['driversProfile'].value_counts().to_dict()

                        for index, data in df.iterrows():
                            numMessages = numMessages + 1
                            if data["attacker"]:
                                numMaliciousMessages = numMaliciousMessages + 1
                            if lastTimeStamp < 0.1:
                                lastTimeStamp = data["rcvTime"]
                            else:
                                sumRcvMsgDistance = sumRcvMsgDistance + (data["rcvTime"] - lastTimeStamp)
                                lastTimeStamp = data["rcvTime"]

                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")
            else:
                print(f"Skipping non-file item: {file_name}")

            avgRcvMsg = sumRcvMsgDistance / numMessages

            csvData.append([
                file_name,
                avgRcvMsg,
                numMessages,
                numMaliciousMessages,
                profile_counts.get('NORMAL', 0),
                profile_counts.get('AGGRESSIVE', 0),
                profile_counts.get('CAUTIOUS', 0)
            ])

    except FileNotFoundError:
        print(f"Error: Directory not found at {directory_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return csvData


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command-line attributes.")

    # Add arguments
    parser.add_argument("-path", type=str, required=True)
    parser.add_argument("-attack", type=str, required=True)

    args = parser.parse_args()

    path = args.path

    # Create the map
    csvData = read_files_in_directory(path)

    with open(args.attack + "_output.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write rows
        writer.writerows(csvData)



