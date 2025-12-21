# VeReMi NextGen

Welcome to the documentation of the **VeReMi NextGen** project – an extended dataset and evaluation framework for Misbehavior Detection in Vehicle-to-Everything (V2X) communication.

## Project Overview

VeReMi NextGen is a comprehensive resource for researching and evaluating misbehavior detection systems in vehicular ad-hoc networks (VANETs). It extends the original VeReMi and VeReMi extension datasets with additional attack types, realistic noise models, and a complete detection pipeline.

The project consists of three main components:

1. **VeReMi_NextGen/** – The dataset containing V2X message traces with injected attacks
2. **Implementation/** – Tools for simulation, attack generation, detection, and parameter optimization
3. **Test_Train_Split/** – Pre-split datasets for machine learning experiments

---

## Repository Structure

```
VeReMi-NextGen/
│
├── VeReMi_NextGen/                    # Dataset
│   ├── <Scenario>_constant_position_offset/        # Attack subset
│   │   ├── vehicle_001.json
│   │   ├── vehicle_002.json
│   │   └── ...
│   ├── <Scenario>_random_speed_offset/
│   ├── <Scenario>_sudden_stop/
│   ├── <Scenario>_mix_all/
│   └── [15 attack type folders per scenario]
│
├── Test_Train_Split/                  # ML-ready splits
│   ├── <Scenario>_constant_position_offset/
│   │   ├── train/
│   │   │   ├── vehicle_001.json
│   │   │   └── ...
│   │   ├── test/
│   │   │   ├── vehicle_050.json
│   │   │   └── ...
│   │   └── split_statistics.csv
│   ├── <Scenario>_random_speed_offset/
│   │   ├── train/
│   │   └── test/
│   └── [splits for all attack types]
│
└── Implementation/  
    |── simulation/                    # Simulation Setup
    |   └── mosaic/
    |       ├── bin/                   # bin of federates
    |       ├── etc/                   # config files
    |       ├── lib/                   # MOSAIC and third party app source folder
    |       ├── scenarios/             # InTAS Sumo scenario
    |       ├── tools/                 # visualization
    |       └── application/           # app running on vehicle OS
    |           └── CamApp/
    |               └── src/main/java/
    |                   ├── entities/
    |                   |   ├── ConfigSettings.java 
    |                   |   ├── DriverProfile.java
    |                   |   └── VehicleAdditionalInformation 
    |                   ├── etsi/ 
    |                   |   ├── AbstractCamSendingApp.java
    |                   |   └── VehicleCamSendingApp.java   
    |                   └── util/
    |                       ├── GaussMarkovNoise.java 
    |                       ├── JSONParser.java
    |                       ├── Pair.java 
    |                       ├── SensorErrorModel.java
    |                       └── SerializationUtil.java
    |
    ├── MBD_systems/                   # Misbehavior Detection
    │   ├── main.py
    │   ├── data_processing.py
    │   ├── data_structures.py
    │   ├── catch_checks.py
    │   ├── legacy_checks.py
    │   └── mdm_lib.py
    │
    ├── attackGenerator/               # Attack Injection
    │   └── attackGenerator.py
    │
    ├── enrichMsgsWithFutherInfo/      # Data Enrichment
    │   └── enrichMsgs.py
    │
    └── parameter_optimization/        # Hyperparameter Tuning
        ├── test.py
        ├── Bin_generator/
        │   └── convert_to_bin.py
        └── Splitting/
            ├── csv_table.py
            ├── train_test_dataset.py
            └── copy_files.py
```

---

## Dataset: VeReMi_NextGen

The dataset contains V2X Basic Safety Messages (BSMs) captured from traffic simulations with injected misbehavior. Each subset represents a different attack type.

### Available Attack Subsets

| Category | Attack Type | Description |
|----------|-------------|-------------|
| **Position** | `constantPositionOffset` | Fixed position shift (±20-70m) |
| | `randomPositionOffset` | Random position shift per message |
| | `positionMirroring` | Position mirrored to opposite lane |
| **Speed** | `constantSpeedOffset` | Fixed speed manipulation (±1-7 m/s) |
| | `randomSpeedOffset` | Random speed offset per message |
| | `zeroSpeedReport` | Always reports speed = 0 |
| | `suddenStop` | Fake sudden stop while moving |
| | `suddenConstantSpeed` | Speed value freezes |
| **Heading/Accel** | `reversedHeading` | Heading rotated 180° |
| | `feignedBraking` | Fake braking (negative acceleration) |
| | `accelerationMultiplication` | Acceleration multiplied |
| **Timing** | `timeDelayAttack` | Delayed timestamps (2-4s) |
| | `dataReplay` | Replays messages from other vehicles |
| **Sybil** | `dosAttack` | Message duplication (flooding) |
| | `trafficCongestionSybil` | Creates phantom vehicles |
| **Mixed** | `mixAll` | All 15 attacks randomly distributed |
| | `mixThree` | Position, speed, suddenStop mixed |

### Message Format

Each JSON file contains an array of BSM messages:

```json
[
  {
    "rcvTime": 1609459200000000000,
    "sendTime": 1609459200000000000,
    "sender_id": "veh_42",
    "sender_alias": 1234567890,
    "messageID": 1,
    "attacker": 0,
    "sender": {
      "pos": "5234.12,3421.87,0.0",
      "pos_noise": "2.5,2.5,0.0",
      "spd": 15.4,
      "spd_noise": 0.5,
      "acl": 0.2,
      "acl_noise": 0.1,
      "hed": 90.0,
      "hed_noise": 2.0,
      "driversProfile": "NORMAL",
      "distance_to_road_edge": 3.2
    },
    "receiver": {
      "pos": "5200.00,3400.00,0.0",
      "pos_noise": "2.5,2.5,0.0",
      "spd": 12.0,
      "spd_noise": 0.5,
      "acl": 0.0,
      "acl_noise": 0.1,
      "hed": 85.0,
      "hed_noise": 2.0,
      "driversProfile": "NORMAL"
    }
  }
]
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `rcvTime` | int | Receive timestamp (nanoseconds) |
| `sendTime` | int | Send timestamp (nanoseconds) |
| `sender_id` | string | Unique vehicle identifier |
| `sender_alias` | int | Pseudonym (changes periodically) |
| `messageID` | int | Unique message ID |
| `attacker` | int | Ground truth: 0=benign, 1=attack |
| `pos` | string | Position as "x,y,z" in meters |
| `pos_noise` | string | Position uncertainty/confidence |
| `spd` | float | Speed in m/s |
| `spd_noise` | float | Speed uncertainty |
| `acl` | float | Acceleration in m/s² |
| `hed` | float | Heading in degrees (0-360) |
| `driversProfile` | string | NORMAL, AGGRESSIVE, or CAUTIOUS |
| `distance_to_road_edge` | float | Distance to road boundary (m) |

---

## Test/Train Splits

Pre-computed splits for machine learning experiments. Each attack type has its own train/test split ensuring:

- **Statistical similarity** between train and test sets (Kolmogorov-Smirnov test)
- **Balanced distribution** of message counts, attack ratios, and driver profiles
- **Default split ratio**: 70% train / 30% test

### Split Statistics

Each split folder contains `split_statistics.csv` with:
- p-values for distribution similarity tests
- Message counts per set
- Attack message ratios

---

## Implementation Modules

### [CaTCH-MBD Systems](MBD-Systems)
Core detection module implementing 9 plausibility and consistency checks. Supports both probabilistic (Catch) and binary (Legacy) detection modes.

### [Attack Generator](Attack-Generator)
Injects 15 different attack types into clean V2X traces. Configurable attacker ratio and attack parameters.

### [Parameter Optimization](Parameter-Optimization)
Optuna-based hyperparameter tuning for detection thresholds. Maximizes F1-score through parallel trial evaluation.

### [Data Enrichment](Data-Enrichment)
Calculates road distance information via SUMO/TraCI integration. Required for position plausibility checks.

---

## Links

- [Architecture Overview](Architecture)
- [CaTCH-MBD Systems Documentation](MBD-Systems)
- [Attack Generator Documentation](Attack-Generator)
- [Parameter Optimization Guide](Parameter-Optimization)
- [Data Enrichment Guide](Data-Enrichment)