# CamApp - ETSI CAM Sending Application

## Overview

The CamApp is an Eclipse MOSAIC application for simulating Cooperative Awareness Messages (CAM). It extends the standard MOSAIC framework with realistic sensor error models, driver profiles, and pseudonym changes for creating Misbehavior Detection datasets.

>[!NOTE]
> If you are interested in detailed process-diagrams related to the simulation and models which are explained down below, have a look at the [Processes](../../Processes) documentation

## Architecture

```
etsi/
├── AbstractCamSendingApp.java    # Abstract base class
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

### Parameter Explanation
- **tau**: Driver reaction time
- **accel/decel**: Maximum acceleration/deceleration
- **speedFactor**: Factor relative to allowed speed
- **sigma**: Imperfection parameter (driver error)
- **minGap**: Minimum gap to the vehicle ahead
- **LaneChangeMode**: Controls how and why a vehicle changes lanes
- **SpeedMode**: Controls how fast a vehicle drives and its acceleration/braking logic

### Characteristics of the different profiles

#### Normal Driver

- Represents the average driver and serves as the baseline profile
- Uses mostly SUMO default parameters
- Balanced reaction time, acceleration, and deceleration

- Speed Mode (Normal)
  - Observes safe speed limits
  - Observes maximum acceleration and deceleration
  - Observes right-of-way at intersections
  - Does **not** brake hard to avoid running a red light

- Lane-Change Model (Default)
  - Strategic lane changes
  - Cooperative lane changes
  - Speed-gain maneuvers
  - Right-lane changes
  - Consideration of other vehicles’ speed and braking gaps

#### Aggressive Driver

- Models assertive and fast driving behavior
- Shorter reaction time and smaller safety gaps
- Stronger acceleration and braking

- Speed Mode (Aggressive)
  - Does **not** observe safe speed limits
  - Observes maximum acceleration
  - Observes maximum deceleration
  - Does **not** respect right-of-way at intersections
  - Does **not** brake hard at red lights

- Lane-Change Model (Aggressive)
  - Strategic lane changes
  - Speed-gain lane changes
  - No cooperative behavior
  - No right-lane changes
  - Limited consideration of other vehicles


#### Cautious Driver

- Models defensive and conservative driving behavior
- Longer reaction time and larger safety gaps
- Lower acceleration and deceleration

- Speed Mode (Cautious)
  - Observes safe speed limits
  - Observes maximum acceleration
  - Observes maximum deceleration
  - Respects right-of-way at intersections
  - Brakes hard to avoid running red lights

- Lane-Change Model (Cautious)
  - Strategic lane changes
  - Cooperative lane changes
  - Considers speed and braking gaps of others
  - Avoids unnecessary acceleration and deceleration
  - Right-lane changes when possible

## Sensor Error Model

The `SensorErrorModels` simulate realistic vehicle sensor errors for the position, speed, acceleration and heading.

### Position Noise

Position noise models inaccuracies of the GPS sensor. The error is generated using a temporally correlated Gaussian process.

$$
\mathcal{E}_{0}^{P} \sim U([-5,5])
$$

$$
\mu = \frac{\mathcal{E}_{0}^{P} + \mathcal{E}_{t-1}^{P}}{2}, \quad
\sigma = 0.03\,\mathcal{E}_{0}^{P}
$$

$$
\mathcal{E}_{t}^{P} \sim N(\mu,\ \sigma^{2})
$$

$$
P_{t}^{\mathcal{E}} = P_{t} + \mathcal{E}_{t}^{P}
$$

where $E_{t}^{P}$ denotes the position error at time t, $P_{t}$ the true position, and $P_{t}^{E}$ the noisy position. The initial error is sampled uniformly, while subsequent errors depend on previous values.

### Speed Noise

Speed noise is modeled as a relative error proportional to the current velocity.

$$
\mu = 0, \quad \sigma = 0.00016
$$

$$
\mathcal{E}_{0}^{V} \sim N(\mu,\ \sigma^{2})
$$

$$
V_{t}^{\mathcal{E}} = V_{t} + V_{t} \cdot \mathcal{E}_{0}^{V}
$$

where $\mathcal{E}^{V}$ represents the relative speed error, $V_t$ the true velocity, and $V_{t}^{\mathcal{E}}$ the noisy velocity.


### Acceleration Noise

Acceleration noise is derived from the temporal change in speed error.

$$
A_{t}^{\mathcal{E}} = A_{t} + \frac{\mathcal{E}_{t}^{V} - \mathcal{E}_{t-1}^{V}}{\delta t}
$$

where $A_t$ is the true acceleration, $\delta t$ the time interval, and $A_{t}^{\mathcal{E}}$ the noisy acceleration.


### Heading Noise

Heading accuracy depends on vehicle speed and degrades at low velocities.

$$
\mathcal{E}_{0}^{H} \sim U([-20,20])
$$

$$
\mathcal{E}_{t}^{H} = \mathcal{E}_{0}^{H} \cdot e^{-0.1\,V_{t}}
$$

$$
H_{t}^{\mathcal{E}} = H_{t} + \mathcal{E}_{t}^{H}
$$

where $E_{t}^{H}$ is the heading error, $H_{t}$ the true heading, and $H_{t}^{E}$ the noisy heading.


## Pseudonym Change Model

The **Pseudonym Change Model** determines whether a vehicle should update its pseudonym after a successful message transmission. The decision is based on a combination of distance-based and time-based criteria to introduce randomness and improve location privacy.


### Configuration Parameters

The model uses thresholds generated from predefined intervals to avoid static and predictable behavior.

| Parameter          | Symbol       | Interval        | Generation Behavior                                                        |
|--------------------|--------------|-----------------|----------------------------------------------------------------------------|
| Distance Threshold | $D_{thresh}$ | $[800, 1500]$ m | Generated **once** during the first pseudonym change and remains constant. |
| Time Threshold     | $T_{thresh}$ | $[120, 360]$ s  | **Regenerated** randomly after every successful pseudonym change.          |


### Functional Logic

The decision process is divided into two phases: the initial pseudonym change and all subsequent changes.

### A. Initial Change (First Exchange)

- **Condition**: Only the **distance-based** criterion must be satisfied.
- **Workflow**:  
  During the first evaluation, the system generates a random distance threshold $D_{thresh}$.  
  The vehicle's traveled distance is monitored, and the pseudonym is changed immediately once the distance exceeds $D_{thresh}$.

#### B. Subsequent Changes

- **Condition**: Both **distance** and **time** criteria must be satisfied.
- **Workflow**:
  - The system first checks whether the traveled distance since the last change exceeds the constant threshold $D_{thresh}$.
  - Once the distance condition is fulfilled, a new random time threshold $T_{thresh}$ is generated.
  - The pseudonym change is executed only after the elapsed time also exceeds $T_{thresh}$.
  - After a successful change, the process restarts with a newly generated time threshold.

### Summary

After each successful message transmission, the following evaluation is performed:

1. **Check Phase**: Is this the *first pseudonym change*?
   - **Yes**: Change the pseudonym if the traveled distance $\geq D_{thresh}$.
   - **No**: Change the pseudonym only if  
     $(\text{distance} \geq D_{thresh}) \;\land\; (\text{time} \geq T_{thresh})$.

2. **Post-Change**:  
   If a pseudonym change occurs, reset all counters and regenerate the time threshold $T_{thresh}$ for the next cycle.

### Pseudonym Format
10-digit random number: `1,000,000,000` to `9,999,999,999`

## CAM Trigger Logic

The system determines whether to transmit a message based on two main criteria:

1. **Sufficient data change**  
2. **Expiration of the maximum inter-message interval**

The decision-making process is as follows:

### Initial Message Check
- The system first verifies if there is existing data to determine whether this is the first message.  
- **If this is the first message:**
  - New data generation begins, but only if vehicle data is available.
  - **If vehicle data is unavailable**, the process terminates and no message is sent.
  - **If vehicle data is available**:
    - Sensor errors are generated.
    - Current vehicle values are stored.
    - Transmission is withheld to establish a baseline for future comparisons.

### Subsequent Messages
- For messages following the initial one, the system performs the same validation checks.
- **Data generation failure** prevents message transmission.
- Successfully generated data is compared to existing values to calculate the delta.

### Transmission Criteria Evaluation
The system evaluates the following four conditions for transmission:

1. Maximum inter-message interval has expired.
2. Heading change exceeds the defined threshold.
3. Speed change exceeds the defined threshold.
4. Position change exceeds the defined threshold.

- **If any of the criteria are met**, the message is transmitted.
- **If none of the criteria are met**, the message is suppressed.

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

