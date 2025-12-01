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

## Documentation

**[Full Documentation (Wiki)](../../wiki)**

- [Home](../../wiki/Home) – Overview, message format, quick start
- [Architecture](../../wiki/Architecture) – System design, data flow
- [MBD Systems](../../wiki/MBD-Systems) – Detection checks explained
- [Attack Generator](../../wiki/Attack-Generator) – Attack types & parameters
- [Parameter Optimization](../../wiki/Parameter-Optimization) – Tuning guide
- [Data Enrichment](../../wiki/Data-Enrichment) – SUMO integration
- [Eclipse MOSAIC](../../wiki/Eclipse-Mosaic)
