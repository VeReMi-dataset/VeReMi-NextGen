from scipy.stats import ks_2samp
import numpy as np
import csv
import random
import argparse


def read_csv_to_2d_array(file_path):
    two_d_array = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            two_d_array.append([
                row[0],
                float(row[1]),
                int(row[2]),
                int(row[3]),
                int(row[4]),
                int(row[5]),
                int(row[6])
            ])
    return two_d_array


def split_array_into_three(data, train_ratio, val_ratio, random_seed=None):
    """Split data into train/validation/test based on sum of column 2."""
    if random_seed is not None:
        random.seed(random_seed)

    data = data.copy()
    random.shuffle(data)

    total_sum = sum(row[2] for row in data)

    train_set, val_set, test_set = [], [], []
    train_sum, val_sum = 0, 0

    for row in data:
        current_train_ratio = train_sum / total_sum if total_sum > 0 else 0
        current_val_ratio = val_sum / total_sum if total_sum > 0 else 0

        if current_train_ratio < train_ratio:
            train_set.append(row)
            train_sum += row[2]
        elif current_val_ratio < val_ratio:
            val_set.append(row)
            val_sum += row[2]
        else:
            test_set.append(row)

    return train_set, val_set, test_set


def extract_columns(data):
    """Extract columns 1-6 from data."""
    return (
        [row[1] for row in data],  # rcvRate
        [row[2] for row in data],  # sumMsgs
        [row[3] for row in data],  # sumMalMsgs
        [row[4] for row in data],  # normalProfiles
        [row[5] for row in data],  # aggressiveProfiles
        [row[6] for row in data]  # cautiousProfiles
    )


def pairwise_ks_tests(set1_cols, set2_cols):
    """Perform KS tests between two sets, return (d, p) tuples for each column."""
    results = []
    for col1, col2 in zip(set1_cols, set2_cols):
        d, p = ks_2samp(col1, col2)
        results.append((d, p))
    return results


def all_p_values_valid(ks_results, threshold=0.05):
    """Check if all p-values are above threshold."""
    return all(p > threshold for _, p in ks_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command-line attributes.")
    parser.add_argument("-file", type=str, required=True)
    parser.add_argument("-attack", type=str, required=True)
    parser.add_argument("-train_ratio", type=float, required=True, help="e.g. 0.6 for 60%")
    parser.add_argument("-val_ratio", type=float, required=True, help="e.g. 0.2 for 20%")

    args = parser.parse_args()
    file_path = args.file
    attack = args.attack
    train_ratio = args.train_ratio
    val_ratio = args.val_ratio

    data = read_csv_to_2d_array(file_path)

    best_avg_p = 0
    best_train, best_val, best_test = [], [], []
    best_ks_results = None

    col_names = ["rcvRate", "sumMsgs", "sumMalMsgs", "normalProfile", "aggressiveProfile", "cautiousProfile"]

    for x in range(30000):
        train_set, val_set, test_set = split_array_into_three(data, train_ratio, val_ratio)

        train_cols = extract_columns(train_set)
        val_cols = extract_columns(val_set)
        test_cols = extract_columns(test_set)

        # Pairwise KS tests
        ks_train_val = pairwise_ks_tests(train_cols, val_cols)
        ks_train_test = pairwise_ks_tests(train_cols, test_cols)
        ks_val_test = pairwise_ks_tests(val_cols, test_cols)

        # Check if all p-values are valid
        if (all_p_values_valid(ks_train_val) and
                all_p_values_valid(ks_train_test) and
                all_p_values_valid(ks_val_test)):

            all_p_values = [p for _, p in ks_train_val + ks_train_test + ks_val_test]
            avg_p = sum(all_p_values) / len(all_p_values)

            if avg_p > best_avg_p:
                best_avg_p = avg_p
                best_train = train_set
                best_val = val_set
                best_test = test_set
                best_ks_results = (ks_train_val, ks_train_test, ks_val_test)

    # Write output files
    with open(f"{attack}_train.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(best_train)

    with open(f"{attack}_val.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(best_val)

    with open(f"{attack}_test.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(best_test)

    # Write KS test results
    with open(f"{attack}_p_d_values.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["metric", "train_val_p", "train_val_d", "train_test_p", "train_test_d", "val_test_p", "val_test_d"])

        if best_ks_results:
            ks_tv, ks_tt, ks_vt = best_ks_results
            for i, name in enumerate(col_names):
                writer.writerow([
                    name,
                    ks_tv[i][1], ks_tv[i][0],
                    ks_tt[i][1], ks_tt[i][0],
                    ks_vt[i][1], ks_vt[i][0]
                ])