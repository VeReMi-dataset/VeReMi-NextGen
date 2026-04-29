<p align="right">
  <i>Image: <code>ghcr.io/vs-uulm/veremi-nextgen:latest</code></i><br>
  <a href="./Dataset/" align="left">
    <img src="https://img.shields.io/badge/To%20The%20Downloads-Dataset-2ea44f?style=flat-square&logo=github" alt="To the downloads">
  </a>
  <img src="https://img.shields.io/badge/MOSAIC-25.2-blue?style=flat-square">
  <img src="https://img.shields.io/badge/SUMO-1.25.0-orange?style=flat-square">
  <img src="https://img.shields.io/badge/OMNeT%2B%2B-6.1-green?style=flat-square">
  <img src="https://img.shields.io/badge/INET-4.5.4-red?style=flat-square">
</p>

# VeReMi NextGen

A comprehensive dataset and dataset generator for evaluating **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.

## Paper Reference
If you are using our dataset, please use the following citation:

> Hermann, A., Remmers, J. N.,  Eissermann, D., Erb, B and Kargl, F. 2026. VeReMi NextGen: A Dataset for Evaluating Misbehavior Detection Systems in VANETs. *Proceedings of the 2026 IEEE Vehicular Networking Conference Conference (Montreal, Canada, 2026)*.
```
@inproceedings{Hermann2026vereminextgen,
	author = {Hermann, Artur and Remmers, Jan Niklas and Eisermann, Dennis and Erb, Benjamin and Kargl, Frank},
	booktitle = {2026 {IEEE} {Vehicular} {Networking} {Conference} ({VNC})},
	date = {2026-06},
	location = {Montreal, Canada},
	title = {VeReMi {NextGen}: A {Dataset} for {Evaluating} {Misbehavior} {Detection} {Systems} in {VANETs}},
}
```

## Overview

VeReMi NextGen provides:

- **Dataset** with 15 attack types on V2X Cooperative Awareness Messages
- **Train/Val/Test Sets** for machine learning experiments
- **Plug'n Play Solution** for recreating the VeReMi Baseline with the option to change parameters
- **Attack Generator** to create custom attack scenarios 
- **CaTCH-MBD System** implementing CaTCH adopted to VeReMi NextGen
- **Parameter Optimization** for systematically obtaining the best thresholds  
  


## Repository Structure

```
VeReMi-NextGen/
├── Dataset/          # Download-Links for each set of VeReMi NextGen
├── Generator/        # Everything to recreate VeReMi NextGen or an own new Dataset
└── Documentation/    # Detailed documentation of VeReMi NextGen 
```

## Documentation

**[Full Documentation](./Documentation)**

- [Home](./Documentation) – Overview, message format, quick start
- [Getting Started](./Documentation/Getting%20Started) - Guide to run the simulation on you own machine
- [Architecture](./Documentation/Architecture) – System design & Overview
- [Processes](./Documentation/Processes) – Processes that occure during simulation
- [Evaluation](./Documentation/Evaluation) – Tools used for evluating VeReMi NextGen 
- [Post-Processing](./Documentation/Post-Processing) – Post-Processing pipeline for integrating MB and more
- [Eclipse MOSAIC](./Documentation/Eclipse%20MOSAIC) - Eclipse MOSAIC Simulation Setup
