# CamApp - ETSI CAM Sending Application

## Overview

The CamApp is an Eclipse MOSAIC application for simulating Cooperative Awareness Messages (CAM). It extends the standard MOSAIC framework with realistic sensor error models, driver profiles, and pseudonym changes for creating Misbehavior Detection datasets.

>[!NOTE]
> If you are interested in the detailed processes during the simulation, have a look at the [Processes](../../Processes) documentation

## Architecture

```
etsi/
├── AbstractCamSendingApp.java    # Abstract base class (ETSI-compliant)
└── VehicleCamSendingApp.java     # Vehicle-specific implementation

entities/
├── ConfigSettings.java           # Configuration parameters
├── DriverProfile.java            # Driver profiles (AGGRESSIVE, NORMAL, PASSIVE)
└── VehicleAdditionalInformation.java  # Additional CAM payload data

util/
├── SensorErrorModel.java         # Sensor error model
├── GaussMarkovNoise.java         # Gauss-Markov noise process
├── JSONParser.java               # JSON output
├── SerializationUtils.java       # Byte serialization
└── Pair.java                     # Utility class
```

## Configuration

The application is controlled via a JSON configuration file `EtsiApplication.json`.

### ConfigSettings Parameters

| Parameter              | Type    | Default                | Description                       |
|------------------------|---------|------------------------|-----------------------------------|
| `minimalPayloadLength` | long    | 200 Bytes              | Minimum CAM payload size          |
| `maxStartOffset`       | long    | 1,000,000,000 ns (1s)  | Maximum random start offset       |
| `minInterval`          | long    | 500,000,000 ns (500ms) | Minimum CAM sending interval      |
| `maxInterval`          | long    | 1,000,000,000 ns (1s)  | Maximum CAM sending interval      |
| `positionChange`       | double  | 4.0 m                  | Position change for CAM trigger   |
| `headingChange`        | double  | 4.0°                   | Heading change for CAM trigger    |
| `velocityChange`       | double  | 0.5 m/s                | Velocity change for CAM trigger   |
| `jsonPath`             | String  | /                      | Output path for JSON files        |
| `enableDriverProfiles` | boolean | false                  | Enables different driver profiles |

### SimulationArea

Defines the geographic area where CAMs are sent and received.

| Parameter | Default   | Description       |
|-----------|-----------|-------------------|
| `minX`    | 48.724467 | Minimum latitude  |
| `maxX`    | 48.801995 | Maximum latitude  |
| `minY`    | 11.353690 | Minimum longitude |
| `maxY`    | 11.498488 | Maximum longitude |

### SimulationTime

| Parameter | Default       | Description                     |
|-----------|---------------|---------------------------------|
| `start`   | 0 s           | Start time of message recording |
| `end`     | 86400 s (24h) | End time of message recording   |

### Example Configuration

```json
{
  "minimalPayloadLength": "200 B",
  "maxStartOffset": "1 s",
  "minInterval": "500 ms",
  "maxInterval": "1 s",
  "positionChange": "4 m",
  "headingChange": 4.0,
  "velocityChange": "0.5 m/s",
  "jsonPath": "/output/json/",
  "enableDriverProfiles": true,
  "simulationTime": {
    "start": "0 s",
    "end": "3600 s"
  },
  "simulationArea": {
    "minX": 48.724467,
    "minY": 11.353690,
    "maxX": 48.801995,
    "maxY": 11.498488
  }
}
```

## Driver Profiles

When `enableDriverProfiles` is enabled, each vehicle is randomly assigned a profile:

| Profile    | Probability | tau (s) | accel (m/s²) | decel (m/s²) | speedFactor | sigma | minGap (m) | LaneChangeMode | SpeedMode  |
|------------|-------------|---------|--------------|--------------|-------------|-------|------------|----------------|------------|
| AGGRESSIVE | 10%         | 0.5     | 3.1          | 5.0          | 1.1         | 0.5   | 2.0        | AGGRESSIVE     | AGGRESSIVE |
| NORMAL     | 80%         | 1.0     | 2.6          | 4.5          | 1.0         | 0.5   | 2.5        | DEFAULT        | NORMAL     |
| PASSIVE    | 10%         | 1.5     | 2.1          | 4.0          | 0.9         | 0.5   | 3.0        | CAUTIOUS       | CAUTIOUS   |

**Parameter Explanation:**
- **tau**: Driver reaction time
- **accel/decel**: Maximum acceleration/deceleration
- **speedFactor**: Factor relative to allowed speed
- **sigma**: Imperfection parameter (driver error)
- **minGap**: Minimum gap to the vehicle ahead

## Sensor Error Model

The `SensorErrorModel` simulates realistic GPS and vehicle sensor errors.

### Position Error

```
Initial error: Uniform(-5m, +5m) for X and Y
Subsequent errors: Gauss-Markov process
  μ = (initialError + previousError) / 2
  σ = 0.03 × |initialError|
```

### Speed Error

```
Initial error: Gaussian(μ=0, σ=0.00016)
correctedSpeed = trueSpeed × (1 + initialError)
speedError = trueSpeed - correctedSpeed
```

### Acceleration Error

Derived from the difference in speed errors:

```
accelerationError = (currentSpeedError - previousSpeedError) / Δt
```

### Heading Error

Velocity-dependent exponential decay:

```
initialError: Uniform(-20°, +20°)
currentError = initialError × exp(-0.1 × velocity)
```

## Pseudonym Change (Alias)

The application implements distance- and time-based pseudonym changes:

### Phase 1 (First Change)
- Change after random distance: **800m - 1500m**

### Phase 2 (Subsequent Changes)
- Condition 1: Distance since last change > randomDistance
- Condition 2: Time since last change > **120s - 360s** (random)
- Both conditions must be met

### Alias Format
10-digit random number: `1,000,000,000` to `9,999,999,999`

## CAM Trigger Logic

A CAM is sent when one of the following conditions is met:

1. **MAX_INTERVAL**: Time since last CAM ≥ `maxInterval`
2. **HEADING_CHANGE**: Δheading > `headingChange`
3. **VELOCITY_CHANGE**: Δspeed > `velocityChange`
4. **POSITION_CHANGE**: Δposition > `positionChange`

The check is performed at the `minInterval` rate.

## JSON Output Format

Each received CAM is stored as a JSON object:

```json
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
```

### Fields

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

## VehicleAdditionalInformation

Additional data transmitted via `userTaggedValue` in the CAM:

| Field               | Type           | Description              |
|---------------------|----------------|--------------------------|
| `speedNoise`        | float          | Speed uncertainty        |
| `headingNoise`      | float          | Acceleration uncertainty |
| `positionNoise`     | CartesianPoint | Position noise (x,y,z)   |
| `accelerationNoise` | float          | Acceleration error       |
| `alias`             | long           | Current pseudonym        |

