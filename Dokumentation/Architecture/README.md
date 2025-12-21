# Architecture

## High-Level Overview

The VeReMi NextGen project follows a modular pipeline architecture for generating, enriching, and evaluating misbehavior in V2X communications.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            VeReMi NextGen Repository                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         VeReMi_NextGen/ (Dataset)                        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │   │
│  │  │ constPos... │ │ randSpeed...│ │ suddenStop  │ │   mixAll    │  ...    │   │
│  │  │  *.json     │ │  *.json     │ │  *.json     │ │  *.json     │         │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘         │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                      Test_Train_Split/ (ML-Ready)                        │   │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │   │
│  │  │ constantPositionOffset/    randomSpeedOffset/    suddenStop/   ...  │ │   │
│  │  │  ├── train/                 ├── train/            ├── train/        │ │   │
│  │  │  ├── test/                  ├── test/             ├── test/         │ │   │
│  │  └─────────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        Implementation/ (Code)                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │   │
│  │  │  Attack    │  │   Data     │  │    MBD     │  │    Parameter       │  │   │
│  │  │ Generator  │─▶│ Enrichment │─▶│  Systems   │◀─│   Optimization     │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Implementation Module Structure

```
Implementation/
│
├── MBD_systems/                          # Misbehavior Detection System
│   │
│   ├── main.py                           # Entry point & CLI
│   │   ├── Argument parsing
│   │   ├── Worker process management
│   │   ├── Result aggregation
│   │   └── Metrics calculation
│   │
│   ├── data_processing.py                # Check orchestration
│   │   ├── perform_catch_checks()
│   │   ├── perform_legacy_checks()
│   │   ├── calculate_metrics()
│   │   └── Message history management
│   │
│   ├── data_structures.py                # Data models
│   │   ├── Coord (x, y, z)
│   │   ├── VehicleData (pos, spd, acl, hed, ...)
│   │   ├── Message (sender, receiver, metadata)
│   │   ├── Parameters (thresholds)
│   │   └── Mapper (row ↔ object conversion)
│   │
│   ├── catch_checks.py                   # Probabilistic checks [0,1]
│   │   ├── range_plausibility_check()
│   │   ├── position_plausibility_check()
│   │   ├── speed_plausibility_check()
│   │   ├── position_consistency_check()
│   │   ├── speed_consistency_check()
│   │   ├── position_speed_consistency_check()
│   │   ├── position_heading_consistency_check()
│   │   ├── intersection_check()
│   │   └── sudden_appearance_check()
│   │
│   ├── legacy_checks.py                  # Binary checks {0,1}
│   │   └── [Same checks, simpler logic]
│   │
│   └── mdm_lib.py                        # Math utilities
│       ├── Geometry (circle, ellipse, rectangle)
│       ├── Distance calculations
│       ├── Intersection computations
│       └── Gaussian distributions
│
├── attackGenerator/                       # Attack Injection
│   │
│   └── attackGenerator.py
│       ├── 15 attack functions
│       ├── Mixed mode dispatcher
│       ├── Attacker selection (20%)
│       └── Configuration management
│
├── enrichMsgsWithFutherInfo/             # SUMO Integration
│   │
│   └── enrichMsgs.py
│       ├── TraCI connection management
│       ├── Road edge distance calculation
│       ├── Parallel worker processes
│       └── JSON in-place modification
│
|── simulation/                    # Simulation Setup
│   └── mosaic/
│       ├── bin/                   # bin of federates
│       ├── etc/                   # config files
│       ├── lib/                   # MOSAIC and third party app source folder
│       ├── scenarios/             # InTAS Sumo scenario
│       ├── tools/                 # visualization
│       └── application/           # app running on vehicle OS
│           └── CamApp/
│               └── src/main/java/
|                   ├── etsi/
|                   |   ├── AbstractCamSendingApp.java    # Abstract base class (ETSI-compliant)
|                   |   └── VehicleCamSendingApp.java     # Vehicle-specific implementation
|                   |
|                   ├── entities/
|                   |   ├── ConfigSettings.java           # Configuration parameters
|                   |   ├── DriverProfile.java            # Driver profiles (AGGRESSIVE, NORMAL, PASSIVE)
|                   |   └── VehicleAdditionalInformation.java  # Additional CAM payload data
|                   |
|                   └── util/
|                       ├── SensorErrorModel.java         # Sensor error model
|                       ├── GaussMarkovNoise.java         # Gauss-Markov noise process
|                       ├── JSONParser.java               # JSON output
|                       ├── SerializationUtils.java       # Byte serialization
|                       └── Pair.java                     # Utility class
|
└── parameter_optimization/                # Hyperparameter Tuning
    │
    ├── test.py                           # Optuna optimization
    │   ├── Objective function
    │   ├── Parameter search spaces
    │   └── Best trial tracking
    │
    ├── Bin_generator/
    │   └── convert_to_bin.py             # JSON → Parquet
    │
    └── Splitting/
        ├── csv_table.py                  # Statistics generation
        ├── train_test_dataset.py         # KS-test based splitting
        └── copy_files.py                 # File organization
```

---

## Parallelization Strategy

### Multi-Processing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Main Process                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ • Parse arguments                                                       │    │
│  │ • Discover input files                                                  │    │
│  │ • Create ProcessPoolExecutor(max_workers=N)                             │    │
│  │ • Submit tasks                                                          │    │
│  │ • Collect results                                                       │    │
│  │ • Aggregate metrics                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
          │                    │                    │                    │
          ▼                    ▼                    ▼                    ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Worker 0   │      │   Worker 1   │      │   Worker 2   │      │  Worker N-1  │
│              │      │              │      │              │      │              │
│ • Load file  │      │ • Load file  │      │ • Load file  │      │ • Load file  │
│ • Run checks │      │ • Run checks │      │ • Run checks │      │ • Run checks │
│ • Return     │      │ • Return     │      │ • Return     │      │ • Return     │
│   metrics    │      │   metrics    │      │   metrics    │      │   metrics    │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

### Module-Specific Parallelization

| Module | Strategy | Reason |
|--------|----------|--------|
| **MBD Systems** | Parallel per file/vehicle | Independent processing |
| **Data Enrichment** | Parallel per file, shared SUMO | TraCI connection reuse |
| **Attack Generator** | Sequential | Cross-message dependencies |
| **Optuna** | Parallel per trial | Independent evaluations |

---

## File Format Conversions

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    JSON     │────▶│   Parquet   │────▶│  DataFrame  │
│  (on disk)  │     │  (on disk)  │     │ (in memory) │
└─────────────┘     └─────────────┘     └─────────────┘
     │                    │                    │
     │                    │                    │
  Original            Optimized           Processing
  format              storage              format
  
  • Human readable    • Compressed         • Fast access
  • Per-vehicle       • All vehicles       • Column-wise
                                           • operations
```

---