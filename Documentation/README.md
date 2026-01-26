# VeReMi NextGen

Welcome to the documentation of the **VeReMi NextGen** project – A comprehensive dataset and dataset generator for evaluating **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.

## Table of Contents
- [Getting Started](./Getting%20Started) - Guide to run the simulation on you own machine
- [Architecture](./Architecture) – System design & Overview
- [Processes](./Processes) – Processes that occur during simulation
- [Evaluation](./Evaluation) – Tools used for evaluating VeReMi NextGen 
- [Post-Processing](./Post-Processing) – Post-Processing pipeline for integrating MB and more
- [Eclipse MOSAIC](./Eclipse%20MOSAIC) - Eclipse MOSAIC Simulation Setup

## Project Overview

VeReMi NextGen is a comprehensive resource for researching and evaluating misbehavior detection systems in vehicular ad-hoc networks (VANETs). 
It extends the original VeReMi and VeReMi extension datasets with additional attack types, variation of driver profiles, an up-to-date traffic scenario
and a complete refactored structure.

The project consists of three main components:

1. **Datasets/** – Containing both the dataset itself and the Train/Validation/Test Split for every attack type, incl. ground truth files and base datasets without MB implementation
2. **Documentation/** – Containing the project documentation
3. **Generator/** – Containing the dataset generator to recreate and extend **VeReMi NextGen**

## Repository Structure

```

VeReMi-NextGen/
│
├── Dataset/
│   ├── <Scenario>_constant_position_offset/                     # Attack subset
│   │   ├── train/
│   │   │   ├── vehicle_001.json
│   │   │   └── ...
│   │   ├── validaiton/
│   │   │   ├── vehicle_0026.json
│   │   │   └── ...
│   │   └── test/
│   │       ├── vehicle_050.json
│   │       └── ...
│   ├── <Scenario>_random_speed_offset/
│   ├── <Scenario>_sudden_stop/
│   └── [15 attack type folders per scenario]
│
├── Documentation/
│   └── [project documentation]
│
└── Generator/  
    │── simulation/                                                 # Simulation Setup
    │   └── mosaic/
    │       ├── bin/                                                # bin of federates
    │       ├── etc/                                                # config files
    │       ├── lib/                                                # MOSAIC and third party app source folder
    │       ├── scenarios/                                          # InTAS Sumo scenario
    │       ├── tools/                                              # visualization
    │       └── application/                                        # app running on vehicle OS
    │           └── CamApp/
    │               └── src/main/java/
    │                   ├── entities/
    │                   │   ├── ConfigSettings.java 
    │                   │   ├── DriverProfile.java
    │                   │   └── VehicleAdditionalInformation 
    │                   ├── etsi/ 
    │                   │   ├── AbstractCamSendingApp.java
    │                   │   └── VehicleCamSendingApp.java   
    │                   └── util/
    │                       ├── GaussMarkovNoise.java 
    │                       ├── JSONParser.java
    │                       ├── Pair.java 
    │                       ├── SensorErrorModel.java
    │                       └── SerializationUtil.java
    │
    ├── MBD_systems/                                                # Misbehavior Detection
    │   ├── main.py
    │   ├── data_processing.py
    │   ├── data_structures.py
    │   ├── catch_checks.py
    │   ├── legacy_checks.py
    │   └── mdm_lib.py
    │
    ├── attackGenerator/                                            # Attack Injection
    │   └── attackGenerator.py
    │
    ├── enrichMsgsWithFutherInfo/                                   # Data Enrichment
    │   └── enrichMsgs.py
    ├── docker/
    │   ├── scenarios/
    │   ├── Dockerfile                                
    │   └── entrypoint.sh
    │
    └── parameter_optimization/                                     # Hyperparameter optimization
        ├── test.py
        ├── Bin_generator/
        │   └── convert_to_bin.py
        └── Splitting/
            ├── csv_table.py
            ├── train_test_dataset.py
            └── copy_files.py
```

## Dataset: VeReMi NextGen

The dataset contains V2X Cooperative Awareness Messages (CAM) captured from traffic simulations with injected misbehavior. Each subset represents a different attack type.

### Available Attack Subsets

| Category                    | Attack Type                  | Description                          |
|-----------------------------|------------------------------|--------------------------------------|
| **Position**                | `constantPositionOffset`     | Fixed position offset                |
|                             | `randomPositionOffset`       | Random position offset per message   |
|                             | `positionMirroring`          | Position mirrored to opposite lane   |
| **Speed**                   | `constantSpeedOffset`        | Fixed speed offset                   |
|                             | `randomSpeedOffset`          | Random speed offset per message      |
|                             | `zeroSpeedReport`            | Always reports speed = 0             |
|                             | `suddenConstantSpeed`        | Speed value freezes                  |
| **Heading**                 | `reversedHeading`            | Heading rotated 180°                 |
| **Accel**                   | `feignedBraking`             | Fake braking (negative acceleration) |
|                             | `accelerationMultiplication` | Acceleration multiplied              |
| **Timing**                  | `timeDelayAttack`            | Delayed timestamps                   |
| **Multi-parameter Attacks** | `dosAttack`                  | Message duplication (flooding)       |
|                             | `trafficCongestionSybil`     | Creates phantom vehicles             |
|                             | `suddenStop`                 | Fake sudden stop while moving        |
|                             | `dataReplay`                 | Replays messages from other vehicles |


### Message Format

Each JSON file contains an array of CAM messages:

```json
[
  {
  "rcvTime": "ℝ[0,+∞)",
  "sendTime": "ℝ[0,+∞)",
  "sender_id": "String",
  "sender_alias": "ℤ[0,+∞)",
  "messageID": "ℤ[0,+∞)",
  "attacker": "ℤ[0,1]",
  "receiver": {
    "pos": ["ℝ(-∞,+∞)", "ℝ(-∞,+∞)", "ℝ(-∞,+∞)"],
    "pos_noise": ["ℝ(-∞,+∞)", "ℝ(-∞,+∞)", "ℝ(-∞,+∞)"],
    "spd": "ℝ(-∞,+∞)",
    "spd_noise": "ℝ(-∞,+∞)",
    "acl": "ℝ(-∞,+∞)",
    "acl_noise": "ℝ(-∞,+∞)",
    "hed": "ℝ[0,360]",
    "hed_noise": "ℝ(-∞,+∞)",
    "driversProfile": "Normal | Cautious | Aggressive"
  },
  "sender": {
    "pos": ["ℝ(-∞,+∞)", "ℝ(-∞,+∞)", "ℝ(-∞,+∞)"],
    "pos_noise": ["ℝ(-∞,+∞)", "ℝ(-∞,+∞)", "ℝ(-∞,+∞)"],
    "spd": "ℝ(-∞,+∞)",
    "spd_noise": "ℝ(-∞,+∞)",
    "acl": "ℝ(-∞,+∞)",
    "acl_noise": "ℝ(-∞,+∞)",
    "hed": "ℝ[0,360]",
    "hed_noise": "ℝ(-∞,+∞)",
    "driversProfile": "Normal | Cautious | Aggressive",
    "distance_to_road_edge": "ℝ(-∞,+∞)"
  }
  }
]
```

### Field Descriptions

| Field                   | Type    | Description                      |
|-------------------------|---------|----------------------------------|
| `rcvTime`               | int     | Receive timestamp (nanoseconds)  |
| `sendTime`              | int     | Send timestamp (nanoseconds)     |
| `sender_id`             | string  | Unique vehicle identifier        |
| `sender_alias`          | int     | Pseudonym (changes periodically) |
| `messageID`             | int     | Unique message ID                |
| `attacker`              | int     | Ground truth: 0=benign, 1=attack |
| `pos`                   | [float] | Position as "x,y,z" in meters    |
| `pos_noise`             | [float] | Position uncertainty/confidence  |
| `spd`                   | float   | Speed in m/s                     |
| `spd_noise`             | float   | Speed uncertainty                |
| `acl`                   | float   | Acceleration in m/s²             |
| `acl_noise`             | float   | Acceleration uncertainty         |
| `hed`                   | float   | Heading in degrees (0-360)       |
| `hed_noise`             | float   | Heading uncertainty              |
| `driversProfile`        | ENUM    | NORMAL, AGGRESSIVE, or CAUTIOUS  |
| `distance_to_road_edge` | float   | Distance to road edge (m)        |

## Train/Validation/Test-Splits

Pre-computed splits for machine learning experiments. Each attack type has its own Train/Validation/Test split:

- **Second Simulation for Training and Validation**: To Train and validate the model on differend data as well as to generelize the capabilities of the model, we simulated a complete distict area.
- **Time-related splits**: The Train/Validation Splits were splited based on the timestamp to represent differend realistic timeframes   
- **Split ratio**: 50% train / 10% Validation / 40% test


## Links

- [Getting Started](./Getting%20Started)
- [Architecture Overview](./Architecture)
- [Eclipse MOSAIC](./Eclipse%20MOSAIC)
- [Evaluation](./Evaltuation)
- [Post-Processing](./Post-Processing)
- [Processes during the simulation](./Processes)
