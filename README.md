# VeReMi NextGen

An extended dataset and evaluation framework for **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.

---

## Overview

VeReMi NextGen provides:

- **Dataset** with 15+ attack types on V2X Basic Safety Messages
- **Detection System** implementing CATCH adopted to VeReMi NextGen
- **Attack Generator** to create custom attack scenarios
- **Parameter Optimization** via Optuna hyperparameter tuning
- **Train/Test Splits** for machine learning experiments
- **Simulation Setup** for reproduce VeReMi NextGen Baseline

---

## Repository Structure

```
VeReMi-NextGen/
├── VeReMi_NextGen/          # Dataset (15+ attack subsets)
├── Test_Train_Split/        # Pre-computed 70/30 ML splits
└── Implementation/          # Simulation Setup, Processing pipeline & tools
```

---

## Quick Start

### Run Eclipse Mosaic

TBA

### Generate Attacks

```bash
cd Implementation/attackGenerator
python attackGenerator.py ./clean_traces suddenStop ./scenario.sumocfg
```

### Optimize Parameters

```bash
cd Implementation/parameter_optimization
python test.py ../../Test_Train_Split/mixAll/train results.json 0
```

### Run Detection

```bash
cd Implementation/MBD_systems
python main.py --input_folder ../../VeReMi_NextGen/constantPositionOffset --type 0
```

---

## Attack Types

| Category | Attacks |
|----------|---------|
| **Position** | constantPositionOffset, randomPositionOffset, positionMirroring |
| **Speed** | constantSpeedOffset, randomSpeedOffset, zeroSpeedReport, suddenStop, suddenConstantSpeed |
| **Heading** | reversedHeading, feignedBraking, accelerationMultiplication |
| **Timing** | timeDelayAttack, dataReplay |
| **Sybil** | dosAttack, trafficCongestionSybil |
| **Mixed** | mixAll, mixThree |

---

## Detection Checks

| Check | Purpose |
|-------|---------|
| Range Plausibility | Sender within communication range |
| Position Plausibility | Position on/near road |
| Speed Plausibility | Speed physically possible |
| Position Consistency | Position change plausible |
| Speed Consistency | Acceleration within limits |
| Position-Speed Consistency | Distance matches speed |
| Position-Heading Consistency | Heading matches movement |
| Intersection Check | No vehicle overlap |
| Sudden Appearance | No instant appearance |

---

## Requirements

- Python 3.10+
- SUMO 1.18+ (for data enrichment)

```bash
pip install pandas numpy optuna traci shapely
```

---

## Documentation

**[Full Documentation (Wiki)](../../wiki)**

- [Home](../../wiki/Home) – Overview, message format, quick start
- [Architecture](../../wiki/Architecture) – System design, data flow
- [MBD Systems](../../wiki/MBD-Systems) – Detection checks explained
- [Attack Generator](../../wiki/Attack-Generator) – Attack types & parameters
- [Parameter Optimization](../../wiki/Parameter-Optimization) – Tuning guide
- [Data Enrichment](../../wiki/Data-Enrichment) – SUMO integration
