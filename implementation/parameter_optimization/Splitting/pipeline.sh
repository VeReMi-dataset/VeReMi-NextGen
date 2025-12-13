#!/bin/bash

ZIP_DIR="../../../veremi_nextGen"
OUTPUT_ROOT="../../../test_train_splits/"
TRAIN_RATIO=0.8

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
    echo "Running Train/Test Split"
    python3 train_test_dataset.py -file "$CSV_FILE" -attack "$NAME" -division "$TRAIN_RATIO"

    TRAIN_CSV="${NAME}_train.csv"
    TEST_CSV="${NAME}_test.csv"

    # 4. Save data to specified folders
    TRAIN_DST="$OUTPUT_ROOT/${NAME}/train/"
    TEST_DST="$OUTPUT_ROOT/${NAME}/test/"
    mkdir -p "$TRAIN_DST" "$TEST_DST"

    echo "Copy Train Files"
    python3 copy_files.py -csvFile "$TRAIN_CSV" -sourceDirectory "$DATA_DIR" -destinationDirectory "$TRAIN_DST"

    echo "Copy Test Files"
    python3 copy_files.py -csvFile "$TEST_CSV" -sourceDirectory "$DATA_DIR" -destinationDirectory "$TEST_DST"
    
    sudo mv *_p_d_values.csv "$OUTPUT_ROOT"/
    rm ./*.csv
    echo "Results stored in: $OURPUT_ROOT"

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
