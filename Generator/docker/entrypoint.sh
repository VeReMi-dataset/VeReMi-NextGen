#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "ERROR: No scenario name provided!"
    echo "Usage: docker run ... <image-name> <scenario_name>"
    echo ""
    echo "Current scenarios available in mounted volume:"
    ls -1 ./scenarios
    exit 1
fi

SCENARIO_NAME=$1

if [ ! -d "./scenarios/$SCENARIO_NAME" ]; then
    echo "ERROR: Scenario '$SCENARIO_NAME' not found in /opt/mosaic/scenarios/"
    echo "Please check your volume mount (-v)."
    exit 1
fi

echo "--- VeReMi-NextGen Co-Simulation ---"
echo "Starting Simulation: $SCENARIO_NAME"

./mosaic.sh -s "$SCENARIO_NAME"

echo "--- Simulation Finished ---"
echo "Results are available in your local 'logs' and 'JSON'  folders."
