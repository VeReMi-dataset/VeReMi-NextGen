# CaTCH-MBD System - Misbehavior Detection

The core module for detecting misbehavior in V2X messages using plausibility and consistency checks.

## Files

| File | Function |
|------|----------|
| `main.py` | Entry point, CLI, parallelization |
| `data_processing.py` | Check orchestration, metrics calculation |
| `data_structures.py` | Data classes, parameters, mapper |
| `catch_checks.py` | Probabilistic checks with confidence factors [0,1] |
| `legacy_checks.py` | Binary checks {0,1} |
| `mdm_lib.py` | Mathematical helper functions (geometry, intersections) |

---

## Usage

```bash
# Catch-based checks (Type 0) - recommended
python main.py --input_folder ./data --type 0

# Legacy checks (Type 1) - simpler, binary
python main.py --input_folder ./data --type 1

# With optimized parameters from file
python main.py --input_folder ./data --type 0 --parameter best_trial.json

# With custom parameters
python main.py --input_folder ./data --type 0 --mpr 400 --mps 50
```

---

## Catch vs Legacy: Key Differences

| Aspect | Catch Checks | Legacy Checks |
|--------|--------------|---------------|
| **Output** | Confidence factor [0.0 - 1.0] | Binary {0, 1} |
| **Uncertainty** | Uses `pos_noise`, `spd_noise` etc. | Ignores noise values |
| **Geometry** | Circle-circle intersections, ellipses | Simple distance comparisons |
| **Decision** | `factor < 0.5` → Misbehavior | `result == 0` → Misbehavior |
| **Accuracy** | Higher (fewer false positives) | Lower (more false positives) |

---

## Detection Logic

A message is flagged as **misbehavior** (`prediction = 1`) if **any single check** returns a value below the threshold:

```python
# Catch Checks
if any(check_result < 0.5 for check_result in all_checks):
    prediction = 1  # Misbehavior detected

# Legacy Checks  
if any(check_result == 0 for check_result in all_checks):
    prediction = 1  # Misbehavior detected
```

---

## Parameters

| Flag | Name | Default | Unit | Description |
|------|------|---------|------|-------------|
| `--mpr` | MAX_PLAUSIBLE_RANGE | 418.1 | m | Maximum V2X communication range |
| `--mps` | MAX_PLAUSIBLE_SPEED | 62.3 | m/s | Maximum physically possible speed (~224 km/h) |
| `--mpa` | MAX_PLAUSIBLE_ACCEL | 5.4 | m/s² | Maximum acceleration |
| `--mpd` | MAX_PLAUSIBLE_DECEL | 5.0 | m/s² | Maximum deceleration (braking) |
| `--mhc` | MAX_HEADING_CHANGE | 76.2 | ° | Maximum heading change between messages |
| `--mdi` | MAX_DELTA_INTERSECTION | 4.3 | s | Time window for intersection check |
| `--mtd` | MAX_TIME_DELTA | 4.7 | s | Maximum Δt for consistency checks |
| `--mpdn` | MAX_PLAUSIBLE_DIST_NEGATIVE | -4.5 | m | Minimum distance to road edge (negative = off-road) |
| `--pht` | POS_HEADING_TIME | 0.4 | s | Time window for heading consistency |
| `--mmru` | MAX_MGT_RNG_UP | 0.7 | m | Upper tolerance margin for position-speed |
| `--mmrd` | MAX_MGT_RNG_DOWN | 1.0 | m | Lower tolerance margin for position-speed |
| `--mnrs` | MAX_NON_ROUTE_SPEED | 0.68 | m/s | Speed below which off-road position is allowed |
| `--msar` | MAX_SA_RANGE | 150.0 | m | Range for sudden appearance check |
| `--msat` | MAX_SA_TIME | 2.1 | s | Time threshold for sudden appearance |

---

## Implemented Checks

### 1. Range Plausibility Check

**Purpose:** Verify that the sender is within V2X communication range.

**Inputs:**
- `receiver_pos`, `receiver_pos_conf` - Receiver position and confidence
- `sender_pos`, `sender_pos_conf` - Sender position and confidence

**Logic (Catch):**
```
distance = euclidean_distance(sender_pos, receiver_pos)
factor = circle_circle_intersection_factor(distance, sender_conf, receiver_conf, MAX_PLAUSIBLE_RANGE)
```

The `circle_circle_factor` calculates what fraction of the uncertainty circles lies within the communication range. This accounts for GPS noise in both positions.

**Logic (Legacy):**
```
distance = euclidean_distance(sender_pos, receiver_pos)
return 1.0 if distance < MAX_PLAUSIBLE_RANGE else 0.0
```

**Misbehavior detected when:**
- Catch: `factor < 0.5` (less than 50% of uncertainty area within range)
- Legacy: `distance ≥ MAX_PLAUSIBLE_RANGE`

---

### 2. Position Plausibility Check

**Purpose:** Verify that the sender is on or near a road (not in impossible locations).

**Inputs:**
- `sender_pos_conf` - Position confidence (uncertainty radius)
- `sender_speed`, `sender_speed_conf` - Speed and confidence
- `distance_to_road_edge` - Calculated by Data Enrichment module

**Logic (Catch):**
```python
# Stationary vehicles may be off-road (parking)
if speed - speed_conf <= MAX_NON_ROUTE_SPEED and distance <= 0:
    return 1.0  # OK

# Calculate what fraction of uncertainty circle is on valid road area
# Using circle segment geometry
if distance + radius <= MAX_PLAUSIBLE_DIST_NEGATIVE:
    return 0.0  # Entirely off-road
elif distance - radius >= MAX_PLAUSIBLE_DIST_NEGATIVE:
    return 1.0  # Entirely on-road
else:
    # Partial overlap - calculate area ratio
    factor = valid_area / total_circle_area
```

**Logic (Legacy):**
```python
if speed <= MAX_NON_ROUTE_SPEED:
    return 1.0  # Slow vehicles allowed off-road

return 1.0 if distance >= MAX_PLAUSIBLE_DIST_NEGATIVE else 0.0
```

**Misbehavior detected when:**
- Catch: `factor < 0.5` (most of uncertainty area off-road)
- Legacy: `distance < MAX_PLAUSIBLE_DIST_NEGATIVE` (position too far from road)

---

### 3. Speed Plausibility Check

**Purpose:** Verify that reported speed is physically possible.

**Inputs:**
- `speed` - Reported speed
- `speed_conf` - Speed confidence/uncertainty

**Logic (Catch):**
```python
if |speed| + speed_conf/2 < MAX_PLAUSIBLE_SPEED:
    return 1.0  # Definitely plausible
elif |speed| - speed_conf/2 > MAX_PLAUSIBLE_SPEED:
    return 0.0  # Definitely implausible
else:
    # Partial overlap with threshold
    factor = (speed_conf/2 + (MAX_PLAUSIBLE_SPEED - |speed|)) / speed_conf
```

**Logic (Legacy):**
```python
return 1.0 if |speed| < MAX_PLAUSIBLE_SPEED else 0.0
```

**Misbehavior detected when:**
- Catch: `factor < 0.5`
- Legacy: `|speed| ≥ MAX_PLAUSIBLE_SPEED`

---

### 4. Position Consistency Check

**Purpose:** Verify that position change between consecutive messages is physically possible.

**Inputs:**
- `cur_pos`, `cur_pos_conf` - Current position and confidence
- `old_pos`, `old_pos_conf` - Previous position and confidence
- `time_delta` - Time between messages (seconds)

**Logic (Catch):**
```python
distance = euclidean_distance(cur_pos, old_pos)
max_possible_distance = MAX_PLAUSIBLE_SPEED × time_delta

factor = circle_circle_factor(distance, cur_conf, old_conf, max_possible_distance)
```

**Logic (Legacy):**
```python
distance = euclidean_distance(cur_pos, old_pos)
max_distance = MAX_PLAUSIBLE_SPEED × time_delta

return 1.0 if distance < max_distance else 0.0
```

**Misbehavior detected when:**
- Position change exceeds what's possible at maximum speed

---

### 5. Speed Consistency Check

**Purpose:** Verify that speed change between messages respects acceleration/deceleration limits.

**Inputs:**
- `cur_speed`, `cur_speed_conf` - Current speed and confidence
- `old_speed`, `old_speed_conf` - Previous speed and confidence
- `time_delta` - Time between messages

**Logic (Catch):**
```python
speed_delta = cur_speed - old_speed

if speed_delta > 0:  # Accelerating
    max_change = MAX_PLAUSIBLE_ACCEL × time_delta
else:  # Decelerating
    max_change = MAX_PLAUSIBLE_DECEL × time_delta

factor = segment_segment_factor(|speed_delta|, cur_conf, old_conf, max_change)
```

**Logic (Legacy):**
```python
speed_delta = cur_speed - old_speed
max_delta = (MAX_PLAUSIBLE_ACCEL if speed_delta > 0 else MAX_PLAUSIBLE_DECEL) × time_delta

return 1.0 if |speed_delta| < max_delta else 0.0
```

**Misbehavior detected when:**
- Acceleration or deceleration exceeds physical limits

---

### 6. Position-Speed Consistency Check

**Purpose:** Verify that traveled distance matches reported speeds (cross-validation).

**Inputs:**
- `cur_pos`, `cur_pos_conf`, `old_pos`, `old_pos_conf`
- `cur_speed`, `cur_speed_conf`, `old_speed`, `old_speed_conf`
- `time_delta`

**Logic (Catch):**
```python
if time_delta >= MAX_TIME_DELTA:
    return 1.0  # Skip for large time gaps

# Skip for very slow vehicles
if max(cur_speed, old_speed) < 1.0:
    if distance - position_confidence <= max_possible_dist:
        return 1.0

# Calculate expected distance range based on speeds
# Uses three speed scenarios: optimistic, nominal, pessimistic
# Accounts for acceleration/deceleration during interval

min_dist, max_dist = calculate_expected_distance_range(...)

# Additional tolerance based on speed (higher speed = more tolerance)
addon_tolerance = MAX_MGT_RNG_DOWN + 0.3571×min_speed - 0.01694×min_speed²

# Calculate how well actual distance matches expected range
factor_min = one_sided_circle_segment_factor(distance, ..., min_dist - addon_tolerance)
factor_max = one_sided_circle_segment_factor(distance, ..., max_dist + MAX_MGT_RNG_UP)

return min(factor_min, factor_max)
```

**Misbehavior detected when:**
- Traveled distance doesn't match what's possible with reported speeds
- Example: High speed reported but position barely changed

---

### 7. Position-Heading Consistency Check

**Purpose:** Verify that heading (driving direction) matches actual movement direction.

**Inputs:**
- `cur_heading`, `cur_heading_conf` - Reported heading and confidence
- `cur_pos`, `cur_pos_conf`, `old_pos`, `old_pos_conf`
- `cur_speed`, `cur_speed_conf`
- `time_delta`

**Logic (Catch):**
```python
if time_delta >= POS_HEADING_TIME:
    return 1.0  # Skip for large time gaps

distance = euclidean_distance(cur_pos, old_pos)
if distance < 1:
    return 1.0  # Not enough movement to determine direction

if cur_speed - cur_speed_conf < 1:
    return 1.0  # Too slow to reliably determine heading

# Calculate actual movement direction from position change
position_angle = atan2(Δx, Δy)

# Compare with reported heading
angle_delta = |cur_heading - position_angle|
if angle_delta > 180:
    angle_delta = 360 - angle_delta

# Calculate factor based on angle difference and uncertainties
# Uses circle segment geometry to account for position noise
factor = average(cur_factor_low, old_factor_low, cur_factor_high, old_factor_high)
```

**Logic (Legacy):**
```python
if time_delta >= POS_HEADING_TIME or distance < 1 or cur_speed < 1:
    return 1.0

position_angle = atan2(Δx, Δy)
angle_delta = |cur_heading - position_angle|

return 1.0 if angle_delta <= MAX_HEADING_CHANGE else 0.0
```

**Misbehavior detected when:**
- Reported heading differs significantly from actual movement direction
- Example: Vehicle claims to drive north but position moves east

---

### 8. Intersection Check

**Purpose:** Verify that two vehicles don't occupy the same physical space.

**Inputs:**
- `pos_1`, `pos_1_conf` - First vehicle position and confidence
- `pos_2`, `pos_2_conf` - Second vehicle position and confidence  
- `heading_1`, `heading_2` - Vehicle headings
- `size` - Vehicle dimensions (default: 5m × 1.8m × 1.5m)
- `delta_time` - Time difference between messages

**Logic (Catch):**
```python
# Model vehicles as ellipses (rectangle + uncertainty)
ellipse_width = vehicle_width + 2 × pos_conf
ellipse_length = vehicle_length + 2 × pos_conf

# Calculate intersection area using Shapely geometry
intersection_factor = ellipse_ellipse_intersection_factor(...)

# Weight by time difference (recent = more important)
time_factor = (MAX_DELTA_INTERSECTION - delta_time) / MAX_DELTA_INTERSECTION

factor = 1.01 - intersection_factor × time_factor
return clamp(factor, 0.0, 1.0)
```

**Logic (Legacy):**
```python
# Model vehicles as rectangles
intersection = rectangle_rectangle_intersection(...)
weighted = intersection × (MAX_DELTA_INTERSECTION - delta_time) / MAX_DELTA_INTERSECTION

return 0.0 if weighted > 0.5 else 1.0
```

**Misbehavior detected when:**
- Two vehicles claim positions that would physically overlap
- Checked against all recently seen vehicles within time window

---

### 9. Sudden Appearance Check

**Purpose:** Detect vehicles that suddenly appear within communication range (should approach gradually).

**Inputs:**
- `receiver_pos`, `receiver_pos_conf`
- `sender_pos`, `sender_pos_conf`

**Precondition:** Only checked when sender is new OR not seen for > MAX_SA_TIME seconds.

**Logic (Catch):**
```python
distance = euclidean_distance(sender_pos, receiver_pos)
detection_range = MAX_SA_RANGE + receiver_pos_conf

if sender_pos_conf <= 0:
    return 0.0 if distance < detection_range else 1.0
else:
    # Calculate what fraction of sender's uncertainty circle
    # falls within the sudden appearance detection zone
    overlap_area = circle_circle_intersection(sender_conf, detection_range, distance)
    factor = 1 - overlap_area / sender_circle_area
```

**Logic (Legacy):**
```python
distance = euclidean_distance(sender_pos, receiver_pos)
return 0.0 if distance < MAX_SA_RANGE else 1.0
```

**Misbehavior detected when:**
- A vehicle appears inside the detection zone without being tracked approaching
- Suggests spoofed vehicle or replay attack

---

## Output Metrics

```json
{
  "tp": 1234,      // True Positives: Correctly detected attacks
  "tn": 5678,      // True Negatives: Correctly passed benign messages
  "fp": 123,       // False Positives: Benign flagged as attack
  "fn": 456,       // False Negatives: Attacks missed
  "accuracy": 0.92,
  "precision": 0.91,
  "recall": 0.73,
  "f1": 0.81
}
```

**Formulas:**
```
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1-Score  = 2 × (Precision × Recall) / (Precision + Recall)
```

---

## Mathematical Helper Functions (mdm_lib.py)

| Function | Purpose |
|----------|---------|
| `calculate_distance(pos1, pos2)` | Euclidean distance between two points |
| `circle_circle_factor(d, r1, r2, range)` | Fraction of two circles within a range |
| `calculate_circle_circle_intersection(r1, r2, d)` | Intersection area of two circles |
| `calculate_max_min_dist(v1, v2, t, a, d)` | Expected distance range given speeds |
| `ellipse_ellipse_intersection_factor(...)` | Intersection of oriented ellipses |
| `calculate_heading_angle(coord)` | Convert position delta to heading angle |
| `ns_to_seconds(ns)` | Convert nanoseconds to seconds |