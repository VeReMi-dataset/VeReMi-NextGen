#!/bin/bash

ZIP_DIR="../../../Dataset/veremi_nextGen"
OUTPUT_ROOT="../../../Dataset/train_validation_test_splits/"
TRAIN_RATIO=0.7
VAL_RATIO=0.1

python3 -m venv venv
source venv/bin/activate
pip install pandas scipy numpy scikit-learn tqdm matplotlib

for zipfile in "$ZIP_DIR"/*.zip; do
    echo "--------------------------------------------"
    echo "Process: $zipfile"
    echo "--------------------------------------------"

    # 1. Name extraction
    NAME=$(basename "$zipfile" .zip)
    UNPACK_DIR="./temp_$NAME"
    mkdir -p "$UNPACK_DIR"

    if [[ ! "$NAME" =~ _[A-Za-z]+$ ]]; then
        echo "Skipping due to none attack suffix: $NAME"
        continue
    fi

    echo "Unzip → $UNPACK_DIR"
    unzip -q "$zipfile" -d "$UNPACK_DIR"
    if [ -d "$UNPACK_DIR/$NAME" ]; then
      DATA_DIR="$UNPACK_DIR/$NAME"
    else
      DATA_DIR="$UNPACK_DIR"
    fi

    # 2. create CSV table
    echo "Running CSV Table Script"
    python3 csv_table.py -path "$DATA_DIR" -attack "$NAME"

    # 3. Dataset Split
    CSV_FILE="${NAME}_output.csv"
    echo "Running Train/Validation/Test Split"
    python3 train_validation_test_dataset.py -file "$CSV_FILE" -attack "$NAME" -train_ratio "$TRAIN_RATIO" -val_ratio "$VAL_RATIO"

    TRAIN_CSV="${NAME}_train.csv"
    VAL_CSV="${NAME}_val.csv"
    TEST_CSV="${NAME}_test.csv"

    # 4. Save data to specified folders
    TRAIN_DST="$OUTPUT_ROOT/${NAME}/train/"
    VAL_DST="$OUTPUT_ROOT/${NAME}/val/"
    TEST_DST="$OUTPUT_ROOT/${NAME}/test/"
    mkdir -p "$TRAIN_DST" "$VAL_DST" "$TEST_DST"

    echo "Copy Train/Validation/Test Files"
    python3 copy_files.py \
        -trainCsv "$TRAIN_CSV" \
        -valCsv "$VAL_CSV" \
        -testCsv "$TEST_CSV" \
        -sourceDirectory "$DATA_DIR" \
        -trainDestination "$TRAIN_DST" \
        -valDestination "$VAL_DST" \
        -testDestination "$TEST_DST"

    sudo mv *_p_d_values.csv "$OUTPUT_ROOT"/
    rm ./*.csv
    echo "Results stored in: $OUTPUT_ROOT"

    # 5. create output ZIP
    echo "ZIP Output"
    cd "$OUTPUT_ROOT"
    zip -rq "${NAME}_splitted.zip" "$NAME"
    cd -

    # 6. delete temporal data
    echo "Delete temporal data"
    rm -rf "$UNPACK_DIR"
    rm -rf "$OUTPUT_ROOT/$NAME"

    echo "Finished: $NAME"
    echo ""
done

echo "Processing done."