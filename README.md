# VeReMi NextGen

A comprehensive dataset and dataset generator for evaluating **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.
---

## Overview

VeReMi NextGen provides:

- **Dataset** with 15+ attack types on V2X Basic Safety Messages
- **CaTCH-MBD System** implementing CaTCH adopted to VeReMi NextGen
- **Attack Generator** to create custom attack scenarios 
- **Parameter Optimization** via Optuna hyperparameter tuning
- **Train/Val/Test Splits** for machine learning experiments
- **Plug'n Play Solution** for recreating the VeReMi Baseline with the option to change parameters

---

## Repository Structure

```
VeReMi-NextGen/
├── Dataset/          # VeReMi-NextGen and Train/Val/Test Split
├── Generator/        # Everything to recreate VeReMi NextGen or an own new Dataset
└── Dokumentation/    # Detailed documentation of VeReMi NextGen 
```

---

## Documentation

**[Full Documentation (Wiki)](./Documentation)**

- [Home](../../wiki/Home) – Overview, message format, quick start
- [Architecture](../../wiki/Architecture) – System design & Overview
- [CaTCH-MBD Systems](../../wiki/MBD-Systems) – CaTCH-MBD System explained
- [Attack Generator](../../wiki/Attack-Generator) – Attack types & parameters
- [Parameter Optimization](../../wiki/Parameter-Optimization) – Tuning guide
- [Data Enrichment](../../wiki/Data-Enrichment) – SUMO integration
- [Eclipse MOSAIC](../../wiki/Eclipse-Mosaic) - Eclipse MOSAIC Simulation Setup
