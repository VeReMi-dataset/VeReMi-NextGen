# Attack Generator

Generates realistic attacks on V2X messages by manipulating vehicle data.

## Attacker Ratio

By default, **20%** of vehicles are randomly selected as attackers:
```python
misbehavior_config['ratio'] = 0.2
```

## Attack Types

### Position-based Attacks

#### `constantPositionOffset`

Adds a constant offset to the reported position for each attacker vehicle.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `offset_lat` | ±20 to ±70 m | Constant offset in X direction |
| `offset_lon` | ±20 to ±70 m | Constant offset in Y direction |

**Attack labeling:**
- `attacker=1`: Always (every message from attacker)
- The offset is randomly chosen once per attacker and stays constant

#### `randomPositionOffset`

Adds a random offset to the position that changes with each message.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `offset_lat` | ±20 to ±70 m | Random offset per message |
| `offset_lon` | ±20 to ±70 m | Random offset per message |

**Attack labeling:**
- `attacker=1`: Always (every message from attacker)
- New random offset generated for each message

#### `positionMirroring`

Mirrors the vehicle position to the opposite side of the road.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `offset` | Calculated | Distance from vehicle to road edge × 2 |

**Attack labeling:**
- `attacker=1`: Always
- Requires SUMO for road edge calculation

### Speed-based Attacks

#### `constantSpeedOffset`

Adds a constant offset to the reported speed.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `speedOffset` | ±1 to ±7 m/s | Constant speed modification |

**Attack labeling:**
- `attacker=1`: Always (every message from attacker)

#### `randomSpeedOffset`

Adds a random offset to speed that changes with each message.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `offset` | ±1 to ±7 m/s | Random offset per message |

**Attack labeling:**
- `attacker=1`: Always (every message from attacker)

#### `zeroSpeedReport`

Reports speed as 0 regardless of actual movement.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `sender_spd` | 0 | Speed always set to zero |

**Attack labeling:**
- `attacker=1`: Only if original speed > 1 m/s AND vehicle has moved > 1m since last message
- `attacker=0`: If vehicle is actually stationary or nearly stationary

This prevents false positives when a vehicle legitimately stops.

#### `suddenConstantSpeed`

Speed value freezes at a certain point while actual speed changes.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `suddenConstantSpeed` | 0.05 (5%) | Probability to trigger freeze |
| `saved_speed` | Float | Speed value that gets frozen |
| `speed_freeze_time` | Timestamp | When freeze was triggered |

**Attack labeling:**
- `attacker=1`: Only if |current_speed - frozen_speed| > 1 m/s
- `attacker=0`: If speed difference is minimal (vehicle maintains similar speed)

### Acceleration-based Attacks

#### `feignedBraking`

Reports fake braking by negating and multiplying acceleration.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `feigned_braking` | 2.0 to 4.0 | Multiplier for negated acceleration |

**Attack labeling:**
- `attacker=1`: Only if original acceleration > 0.25 m/s² (actually accelerating)
- `attacker=0`: If vehicle is not accelerating or barely accelerating

#### `accelerationMultiplication`

Multiplies the reported acceleration value.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `accelerationMult` | 2.0 to 4.0 | Multiplier for acceleration |

**Attack labeling:**
- `attacker=1`: Only if |original_accel| > 0.5 m/s²
- `attacker=0`: If acceleration is minimal (multiplication has little effect)

### Heading-based Attacks

#### `reversedHeading`

Reports heading rotated by 180° (driving direction reversed).

| Parameter | Value | Description |
|-----------|-------|-------------|
| Heading modification | +180° | Added to original heading (mod 360) |

**Attack labeling:**
- `attacker=1`: Only if speed > 1 m/s AND vehicle has moved > 1m
- `attacker=0`: If vehicle is stationary (heading doesn't matter when not moving)

### Time-based Attacks

#### `timeDelayAttack`

Delays the timestamps of messages.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `timeDelay` | 2-4 seconds | Delay added to sendTime and rcvTime |

**Attack labeling:**
- `attacker=1`: Always (every message from attacker)

### Multi-parameter Attacks

#### `dosAttack`

Duplicates messages to flood the network.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `amount` | 2-4 | Number of duplicate messages |
| Frequency | 500ms / amount | Time between duplicates |

**Attack labeling:**
- `attacker=1`: Always (original and all copies)

#### `trafficCongestionSybil`

Creates phantom vehicles around the attacker to simulate traffic congestion.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `amount` | 4-6 | Number of phantom vehicles |
| `frequency` | 1,000-100,000 ns | Time offset between phantoms |
| Lateral offset | ±2-3 m | Distance to side of attacker |
| Longitudinal offset | ±5-6 m | Distance in front/behind |
| Position noise | ±2 m | Random variation |
| Speed variation | ±5% | Slight speed differences |

**Attack labeling:**
- `attacker=1`: Always (all phantom vehicles)
- Original attacker message remains unchanged

#### `suddenStop`

Simulates a sudden stop - the vehicle reports stopped position/speed while actually moving.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `suddenStop` | 0.05 (5%) | Probability to trigger the stop |
| `msg` | Saved message | Position where "stop" occurred |
| `stop_time` | Timestamp | When the stop was triggered |

**Attack labeling:**
- `attacker=1` at trigger: Only if original speed > 1 m/s AND acceleration ≥ 0
- `attacker=1` after trigger: Only if original speed > 1 m/s OR distance to "stopped" position ≥ 20m
- `attacker=0`: If vehicle was already slow/stopping

#### `dataReplay`

Replays messages from nearby vehicles as if they were the attacker's own.

| Parameter | Value Range | Description |
|-----------|-------------|-------------|
| `max_replay_seq` | 4-8 | Messages to replay from same victim |
| `replay_seq` | Counter | Current replay count |
| `saved_alias` | Vehicle ID | Currently replayed victim |
| Detection radius | 400m | Range to find victim vehicles |
| Time window | 5 seconds | How far back to look for messages |

**Attack labeling:**
- `attacker=1`: Always when a message is replaced with replayed data
- Messages without nearby victims remain unchanged

### Mix Modes

#### `mixAll`

Randomly assigns one of all 15 attack types to each attacker vehicle.

#### `mixThree`

Randomly assigns one of three attacks to each attacker:
- `constantPositionOffset`
- `randomSpeedOffset`
- `suddenStop`

## Summary: Attack Labeling Logic

| Attack Type | Always Labeled | Conditionally Labeled |
|-------------|----------------|----------------------|
| constantPositionOffset | ✅ | - |
| randomPositionOffset | ✅ | - |
| positionMirroring | ✅ | - |
| constantSpeedOffset | ✅ | - |
| randomSpeedOffset | ✅ | - |
| timeDelayAttack | ✅ | - |
| dosAttack | ✅ | - |
| trafficCongestionSybil | ✅ | - |
| dataReplay | ✅ (when replaying) | - |
| zeroSpeedReport | - | speed > 1 m/s AND moved |
| suddenStop | - | speed > 1 m/s or distance ≥ 20m |
| suddenConstantSpeed | - | speed diff > 1 m/s |
| reversedHeading | - | speed > 1 m/s AND moved |
| feignedBraking | - | accel > 0.25 m/s² |
| accelerationMultiplication | - | |accel| > 0.5 m/s² |

The conditional labeling prevents false positives when the manipulation has no practical effect (e.g., reversing heading of a stationary vehicle).