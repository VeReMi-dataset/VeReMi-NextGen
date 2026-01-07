# VeReMi NextGen

A comprehensive dataset and dataset generator for evaluating **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.
---

## Overview

VeReMi NextGen provides:

- **Dataset** with 15+ attack types on V2X Basic Safety Messages
- **Train/Val/Test Splits** for machine learning experiments
- **Plug'n Play Solution** for recreating the VeReMi Baseline with the option to change parameters
- **Attack Generator** to create custom attack scenarios 
- **CaTCH-MBD System** implementing CaTCH adopted to VeReMi NextGen
- **Parameter Optimization** for systematically obtaining the best thresholds  
  
---

## Repository Structure

```
VeReMi-NextGen/
├── Dataset/          # VeReMi-NextGen and Train/Val/Test Split
├── Generator/        # Everything to recreate VeReMi NextGen or an own new Dataset
└── Documentation/    # Detailed documentation of VeReMi NextGen 
```

---

## Documentation

**[Full Documentation](./Documentation)**

- [Home](./Documentation) – Overview, message format, quick start
- [Architecture](./Documentation/Architecture) – System design & Overview
- [Processes](./Documentation/Processes) – Processes that occure during simulation
- [Evaluation](./Documentation/Evaluation) – Tools used for evluating VeReMi NextGen 
- [Post-Processing](./Documentation/Post-Processing) – Post-Processing pipeline for integrating MB and more
- [Eclipse MOSAIC](./Documentation/Eclipse%20MOSAIC) - Eclipse MOSAIC Simulation Setup
