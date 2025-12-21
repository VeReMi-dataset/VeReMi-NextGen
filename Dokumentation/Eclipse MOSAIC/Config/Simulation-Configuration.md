# Simulation Configuration

This wiki page documents the configuration files for the **InTAS** (Ingolstadt Traffic Scenario) Eclipse MOSAIC simulation, designed for generating V2X communication datasets with CAM (Cooperative Awareness Message) transmission.

---

## Table of Contents

1. [Overview](#overview)
2. [Scenario Configuration](#scenario-configuration)
3. [Application Configuration](#application-configuration)
4. [Mapping Configuration](#mapping-configuration)
5. [OMNeT++ Configuration](#omnetpp-configuration)
6. [SUMO Configuration](#sumo-configuration)
7. [Output Configuration](#output-configuration)

---

## Overview

This simulation setup uses the following Eclipse MOSAIC federates:

| Federate | Enabled | Purpose |
|----------|---------|---------|
| Application | ✅ | Runs `VehicleCamSendingApp` on vehicles |
| OMNeT++ | ✅ | Network simulation (ITS-G5/802.11p) |
| SUMO | ✅ | Traffic simulation |
| Output | ✅ | Logging vehicle updates and V2X messages |
| Cell | ❌ | Cellular communication (disabled) |
| SNS | ❌ | Simple Network Simulator (disabled) |
| NS3 | ❌ | NS-3 network simulator (disabled) |

---

## Scenario Configuration

**File:** `scenario_config.json`

### Simulation Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `id` | `InTAS` | Scenario identifier (Ingolstadt Traffic Scenario) |
| `duration` | `24h` | Total simulation duration |
| `randomSeed` | `268965854` | Seed for reproducible results |

### Geographic Projection

The simulation is centered on **Ingolstadt, Germany**:

| Parameter | Value |
|-----------|-------|
| Center Latitude | `48.766666` |
| Center Longitude | `11.433333` |
| Cartesian Offset X | `-464198.88` |
| Cartesian Offset Y | `-4952821.58` |

### Network Configuration

IP address ranges for different entity types:

| Entity Type | Network Address | Netmask |
|-------------|-----------------|---------|
| Vehicles | `10.0.0.0` | `255.248.0.0` |
| RSUs | `10.8.0.0` | |
| Traffic Lights | `10.16.0.0` | |
| Charging Stations | `10.24.0.0` | |
| Servers | `10.32.0.0` | |
| TMC | `10.40.0.0` | |

---

## Application Configuration

### Main Configuration

**File:** `application/application_config.json`

Currently empty (`{}`). Application-specific configurations are defined in `EtsiApplication.json`.

### ETSI CAM Application

**File:** `application/EtsiApplication.json`

**Compiled Application:** `CamApp-0_0_1.jar`

#### CAM Generation Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `minimalPayloadLength` | `200` bytes | Minimum CAM payload size |
| `maxStartOffset` | `1s` | Maximum random delay before first CAM |
| `minInterval` | `500ms` | Minimum time between CAMs |
| `maxInterval` | `1s` | Maximum time between CAMs |

#### CAM Triggering Conditions

CAM messages are triggered when any of the following thresholds are exceeded:

| Condition | Threshold |
|-----------|-----------|
| Position change | `4` meters |
| Heading change | `4` degrees |
| Velocity change | `0.5` m/s |

#### Simulation Boundaries

**Time Window:**

| Traffic Density | Start Time | End Time | Duration | Description |
|-----------------|------------|----------|----------|-------------|
| Low Density | `7200` s (2:00h) | `14400` s (4:00h) | 2 hours | Early morning / low traffic period |
| High Density | `25200` s (7:00h) | `25600` s (7:07h) | ~7 minutes | Rush hour / high traffic period |

**Geographic Area (Bounding Box):**

| Simulated Area  | Min(Longitude/Latitude) | Max(Longitude/Latitude) |
|--------|----------|-----------|
| Highway | `48.749772`/`11.453732` | `48.767821`/`11.463387` |
| Urban | `48.756441`/`48.756441` | `48.773643`/`11.436188` |

Only vehicles within this area will send CAM messages.

#### Additional Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `jsonPath` | / | Output path for JSON files |
| `enableDriverProfiles` | `true` | Enable driver behavior profiles |

---

## Mapping Configuration

**File:** `mapping/mapping_config.json`

### Vehicle Prototypes

The configuration defines **45 vehicle prototypes**, all running the `etsi.VehicleCamSendingApp`:

| Prototype Pattern | Count | Application |
|-------------------|-------|-------------|
| `random_001` to `random_022` | 22 | `etsi.VehicleCamSendingApp` |
| `default_001` to `default_022` | 22 | `etsi.VehicleCamSendingApp` |
| `bus` | 1 | None (no V2X) |

All prototypes have a weight of `1.0`, meaning equal probability of spawning.

**Note:** The `bus` prototype has no applications assigned, meaning buses do not participate in V2X communication.

---

## OMNeT++ Configuration

### Federate Configuration

**File:** `omnetpp/omnetpp_config.json`

| Setting | Value |
|---------|-------|
| Configuration File | `omnetpp.ini` |
| Destination Type | AD_HOC_TOPOCAST |
| Address Type | IPv4 Broadcast |
| Protocol | UDP |

### Detailed OMNeT++ Settings

**File:** `omnetpp/omnetpp.ini`

#### General Settings

| Parameter | Value |
|-----------|-------|
| Network | `omnetpp_federate.mgmt.Simulation` |
| Time Resolution | `1ns` |
| Scheduler | `MosaicEventScheduler` |
| Host | `localhost` |
| Port | `4998` |

#### IEEE 802.11p / ITS-G5 Radio Configuration

| Parameter | Value |
|-----------|-------|
| Operation Mode | `p` (802.11p) |
| Frequency Band | `5.9 GHz` |
| Channel Number | `4` |
| Bandwidth | `10 MHz` |
| Carrier Frequency | `5.9 GHz` |
| Transmit Power | `0.02 W` (20 mW) |

#### Receiver Parameters

| Parameter | Value |
|-----------|-------|
| SNIR Threshold | `4 dB` |
| Sensitivity | `-81 dBm` |
| Background Noise | `-110 dBm` |
| Thermal Noise | `-110 dBm` |

#### MAC Layer Settings

| Parameter | Value |
|-----------|-------|
| Data Rate | `6 Mbps` |
| Queue Size | `10` packets |
| CW Min | `15` |
| CW Max | `1023` |
| Short Retry Limit | `7` |
| Long Retry Limit | `7` |

#### Propagation Model

| Component | Model |
|-----------|-------|
| Propagation | `ConstantSpeedPropagation` |
| Path Loss | `FreeSpacePathLoss` |
| Obstacle Loss | None (disabled) |

---

## SUMO Configuration

**File:** `sumo/sumo_config.json`

| Parameter | Value | Description |
|-----------|-------|-------------|
| `sumoConfigurationFile` | `InTAS_full_poly.sumocfg` | SUMO scenario configuration file |
| `updateInterval` | `1000` ms | Time step for SUMO updates (1 second) |

---

## Output Configuration

**File:** `output/output_config.xml`

### File Output

Writes simulation data to CSV files.

| Setting | Value |
|---------|-------|
| Filename | `output.csv` |
| Separator | `;` |
| Decimal Separator | `.` |
| Update Interval | `5` seconds |

#### Subscribed Events

**VehicleUpdates:**
- Timestamp, Vehicle Name, Latitude, Longitude, Speed, Heading

**V2xMessageReception:**
- Timestamp, Message ID, Receiver Name, Message Type

**V2xMessageTransmission:**
- Timestamp, Message ID, Source Name, Message Type

**VehicleRegistration:**
- Timestamp, Vehicle Name, Applications, Vehicle Type

**TrafficLightRegistration:**
- Timestamp, Name, Applications, Position (Lat/Lon)

**RsuRegistration:**
- Timestamp, Name, Applications, Position (Lat/Lon)

### WebSocket Output

Real-time visualization via WebSocket.

| Setting | Value |
|---------|-------|
| Port | `46587` |
| Synchronized | `true` |

---