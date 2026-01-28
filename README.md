<p align="right">
  <i>Image: <code>ghcr.io/vs-uulm/veremi-nextgen:latest</code></i><br>
  <img src="https://img.shields.io/badge/MOSAIC-25.2-blue?style=flat-square">
  <img src="https://img.shields.io/badge/SUMO-1.25.0-orange?style=flat-square">
  <img src="https://img.shields.io/badge/OMNeT%2B%2B-6.1-green?style=flat-square">
  <img src="https://img.shields.io/badge/INET-4.5.4-red?style=flat-square">
</p>

# VeReMi NextGen

A comprehensive dataset and dataset generator for evaluating **Misbehavior Detection** in Vehicle-to-Everything (V2X) communication.

## Overview

VeReMi NextGen provides:

- **Dataset** with 15+ attack types on V2X Basic Safety Messages
- **Train/Val/Test Sets** for machine learning experiments
- **Plug'n Play Solution** for recreating the VeReMi Baseline with the option to change parameters
- **Attack Generator** to create custom attack scenarios 
- **CaTCH-MBD System** implementing CaTCH adopted to VeReMi NextGen
- **Parameter Optimization** for systematically obtaining the best thresholds  
  

## Repository Structure

```
VeReMi-NextGen/
├── Generator/        # Everything to recreate VeReMi NextGen or an own new Dataset
└── Documentation/    # Detailed documentation of VeReMi NextGen 
```

## Assets (v1.0.0)

> Click **Download** badges to download single files directly.  
> For **selected** / **all** downloads in one go, see the GitHub CLI section below.

### InTAS_highway_2
| Asset | Download |
|---|---|
| `InTAS_highway_2.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2.zip) |
| `InTAS_highway_2_accelerationMultiplication.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_accelerationMultiplication.zip) |
| `InTAS_highway_2_constantPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_constantPositionOffset.zip) |
| `InTAS_highway_2_constantSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_constantSpeedOffset.zip) |
| `InTAS_highway_2_dataReplay.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_dataReplay.zip) |
| `InTAS_highway_2_dosAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_dosAttack.zip) |
| `InTAS_highway_2_feignedBraking.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_feignedBraking.zip) |
| `InTAS_highway_2_positionMirroring.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_positionMirroring.zip) |
| `InTAS_highway_2_randomPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_randomPositionOffset.zip) |
| `InTAS_highway_2_randomSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_randomSpeedOffset.zip) |
| `InTAS_highway_2_reversedHeading.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_reversedHeading.zip) |
| `InTAS_highway_2_suddenConstantSpeed.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_suddenConstantSpeed.zip) |
| `InTAS_highway_2_suddenStop.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_suddenStop.zip) |
| `InTAS_highway_2_timeDelayAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_timeDelayAttack.zip) |
| `InTAS_highway_2_trafficCongestionSybil.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_trafficCongestionSybil.zip) |
| `InTAS_highway_2_zeroSpeedReport.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_zeroSpeedReport.zip) |
| `InTAS_highway_2_Train_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_Train_groundTruth.json) |
| `InTAS_highway_2_Validation_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_Validation_groundTruth.json) |
| `InTAS_highway_2_Test_ground_truth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_2_Test_ground_truth.json) |

### InTAS_highway_7
| Asset | Download |
|---|---|
| `InTAS_highway_7.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7.zip) |
| `InTAS_highway_7_accelerationMultiplication.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_accelerationMultiplication.zip) |
| `InTAS_highway_7_constantPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_constantPositionOffset.zip) |
| `InTAS_highway_7_constantSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_constantSpeedOffset.zip) |
| `InTAS_highway_7_dataReplay.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_dataReplay.zip) |
| `InTAS_highway_7_dosAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_dosAttack.zip) |
| `InTAS_highway_7_feignedBraking.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_feignedBraking.zip) |
| `InTAS_highway_7_positionMirroring.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_positionMirroring.zip) |
| `InTAS_highway_7_randomPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_randomPositionOffset.zip) |
| `InTAS_highway_7_randomSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_randomSpeedOffset.zip) |
| `InTAS_highway_7_reversedHeading.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_reversedHeading.zip) |
| `InTAS_highway_7_suddenConstantSpeed.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_suddenConstantSpeed.zip) |
| `InTAS_highway_7_suddenStop.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_suddenStop.zip) |
| `InTAS_highway_7_timeDelayAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_timeDelayAttack.zip) |
| `InTAS_highway_7_trafficCongestionSybil.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_trafficCongestionSybil.zip) |
| `InTAS_highway_7_zeroSpeedReport.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_zeroSpeedReport.zip) |
| `InTAS_highway_7_Train_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_Train_groundTruth.json) |
| `InTAS_highway_7_Validation_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_Validation_groundTruth.json) |
| `InTAS_highway_7_Test_ground_truth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_highway_7_Test_ground_truth.json) |

### InTAS_urban_2
| Asset | Download |
|---|---|
| `InTAS_urban_2.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2.zip) |
| `InTAS_urban_2_accelerationMultiplication.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_accelerationMultiplication.zip) |
| `InTAS_urban_2_constantPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_constantPositionOffset.zip) |
| `InTAS_urban_2_constantSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_constantSpeedOffset.zip) |
| `InTAS_urban_2_dataReplay.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_dataReplay.zip) |
| `InTAS_urban_2_dosAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_dosAttack.zip) |
| `InTAS_urban_2_feignedBraking.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_feignedBraking.zip) |
| `InTAS_urban_2_positionMirroring.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_positionMirroring.zip) |
| `InTAS_urban_2_randomPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_randomPositionOffset.zip) |
| `InTAS_urban_2_randomSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_randomSpeedOffset.zip) |
| `InTAS_urban_2_reversedHeading.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_reversedHeading.zip) |
| `InTAS_urban_2_suddenConstantSpeed.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_suddenConstantSpeed.zip) |
| `InTAS_urban_2_suddenStop.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_suddenStop.zip) |
| `InTAS_urban_2_timeDelayAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_timeDelayAttack.zip) |
| `InTAS_urban_2_trafficCongestionSybil.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_trafficCongestionSybil.zip) |
| `InTAS_urban_2_zeroSpeedReport.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_zeroSpeedReport.zip) |
| `InTAS_urban_2_Train_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_Train_groundTruth.json) |
| `InTAS_urban_2_Validation_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_Validation_groundTruth.json) |
| `InTAS_urban_2_Test_ground_truth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_2_Test_ground_truth.json) |

### InTAS_urban_7
| Asset | Download |
|---|---|
| `InTAS_urban_7.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7.zip) |
| `InTAS_urban_7_accelerationMultiplication.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_accelerationMultiplication.zip) |
| `InTAS_urban_7_constantPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_constantPositionOffset.zip) |
| `InTAS_urban_7_constantSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_constantSpeedOffset.zip) |
| `InTAS_urban_7_dataReplay.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_dataReplay.zip) |
| `InTAS_urban_7_dosAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_dosAttack.zip) |
| `InTAS_urban_7_feignedBraking.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_feignedBraking.zip) |
| `InTAS_urban_7_positionMirroring.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_positionMirroring.zip) |
| `InTAS_urban_7_randomPositionOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_randomPositionOffset.zip) |
| `InTAS_urban_7_randomSpeedOffset.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_randomSpeedOffset.zip) |
| `InTAS_urban_7_reversedHeading.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_reversedHeading.zip) |
| `InTAS_urban_7_suddenConstantSpeed.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_suddenConstantSpeed.zip) |
| `InTAS_urban_7_suddenStop.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_suddenStop.zip) |
| `InTAS_urban_7_timeDelayAttack.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_timeDelayAttack.zip) |
| `InTAS_urban_7_trafficCongestionSybil.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_trafficCongestionSybil.zip) |
| `InTAS_urban_7_zeroSpeedReport.zip` | [![Download](https://img.shields.io/badge/Download-zip-2ea44f?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_zeroSpeedReport.zip) |
| `InTAS_urban_7_Train_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_Train_groundTruth.json) |
| `InTAS_urban_7_Validation_groundTruth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_Validation_groundTruth.json) |
| `InTAS_urban_7_Test_ground_truth.json` | [![Download](https://img.shields.io/badge/Download-json-8250df?style=for-the-badge&logo=github)](https://github.com/vs-uulm/VeReMi-NextGen/releases/download/v1.0.0/InTAS_urban_7_Test_ground_truth.json) |


## Download selected assets (GitHub CLI)

> Install `gh` (GitHub CLI), then:

```bash
# Example: download all highway_2 assets (zip + json)
gh release download v1.0.0 -R vs-uulm/VeReMi-NextGen -p "InTAS_highway_2*" 
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
