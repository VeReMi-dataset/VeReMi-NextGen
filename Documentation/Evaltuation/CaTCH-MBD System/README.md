# CaTCH-MBD System - Misbehavior Detection

Documentation of the CaTCH-MBD System which utilizes plausibility and consistency checks.

## Files

| File                 | Function                                                |
|----------------------|---------------------------------------------------------|
| `main.py`            | Entry point, CLI, parallelization                       |
| `data_processing.py` | Check orchestration, metrics calculation                |
| `data_structures.py` | Data classes, parameters, mapper                        |
| `catch_checks.py`    | Probabilistic checks with confidence factors [0,1]      |
| `legacy_checks.py`   | Binary checks {0,1}                                     |
| `mdm_lib.py`         | Mathematical helper functions (geometry, intersections) |

## Catch vs Legacy: Key Differences

| Aspect          | Catch Checks                          | Legacy Checks                |
|-----------------|---------------------------------------|------------------------------|
| **Output**      | Confidence factor [0.0 - 1.0]         | Binary {0, 1}                |
| **Uncertainty** | Uses `pos_noise`, `spd_noise` etc.    | Ignores noise values         |
| **Geometry**    | Circle-circle intersections, ellipses | Simple distance comparisons  |
| **Decision**    | `factor < 0.5` → Misbehavior          | `result == 0` → Misbehavior  |
| **Accuracy**    | Higher (fewer false positives)        | Lower (more false positives) |

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

## Parameters

| Flag     | Name                        | Unit | Description                                         |
|----------|-----------------------------|------|-----------------------------------------------------|
| `--mpr`  | MAX_PLAUSIBLE_RANGE         | m    | Maximum V2X communication range                     |
| `--mps`  | MAX_PLAUSIBLE_SPEED         | m/s  | Maximum physically possible speed      |
| `--mpa`  | MAX_PLAUSIBLE_ACCEL         | m/s² | Maximum acceleration                                |
| `--mpd`  | MAX_PLAUSIBLE_DECEL         | m/s² | Maximum deceleration (braking)                      |
| `--mhc`  | MAX_HEADING_CHANGE          | °    | Maximum heading change between messages             |
| `--mdi`  | MAX_DELTA_INTERSECTION      | s    | Time window for intersection check                  |
| `--mtd`  | MAX_TIME_DELTA              | s    | Maximum Δt for consistency checks                   |
| `--mpdn` | MAX_PLAUSIBLE_DIST_NEGATIVE | m    | Minimum distance to road edge (negative = off-road) |
| `--pht`  | POS_HEADING_TIME            | s    | Time window for heading consistency                 |
| `--mmru` | MAX_MGT_RNG_UP              | m    | Upper tolerance margin for position-speed           |
| `--mmrd` | MAX_MGT_RNG_DOWN            | m    | Lower tolerance margin for position-speed           |
| `--mnrs` | MAX_NON_ROUTE_SPEED         | m/s  | Speed below which off-road position is allowed      |
| `--msar` | MAX_SA_RANGE                | m    | Range for sudden appearance check                   |
| `--msat` | MAX_SA_TIME                 | s    | Time threshold for sudden appearance                |

## Implemented Checks

### 1. Range Plausibility Check

**Purpose:** Verify that the sender is within V2X communication range.

**Inputs:**
- `receiver_pos`, `receiver_pos_conf` - Receiver position and confidence
- `sender_pos`, `sender_pos_conf` - Sender position and confidence

**CaTCH Implementation:**
```python
def range_plausibility_check(self, receiver_pos, receiver_pos_conf,
                             sender_pos, sender_pos_conf):
    distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
    
    # Calculate what fraction of the uncertainty circles 
    # lies within the communication range
    factor = self.mdm_lib.circle_circle_factor(
        distance, 
        sender_pos_conf.x,    # sender uncertainty radius
        receiver_pos_conf.x,  # receiver uncertainty radius
        self.params.MAX_PLAUSIBLE_RANGE
    )
    return factor
```

**Legacy Implementation:**
```python
def range_plausibility_check(self, sender_pos, receiver_pos):
    distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
    return 1.0 if distance < self.params.MAX_PLAUSIBLE_RANGE else 0.0
```

**Misbehavior detected when:**
- CaTCH: `factor < 0.5` (less than 50% of uncertainty area within range)
- Legacy: `distance >= MAX_PLAUSIBLE_RANGE`

### 2. Position Plausibility Check

**Purpose:** Verify that the sender is on or near a road (not in impossible locations).

**Inputs:**
- `sender_pos_conf` - Position confidence (uncertainty radius)
- `sender_speed`, `sender_speed_conf` - Speed and confidence
- `distance_to_road_edge` - Calculated by Data Enrichment module

**CaTCH Implementation:**
```python
def position_plausibility_check(self, sender_pos_conf, sender_speed,
                                sender_speed_conf, distance):
    # Adjust speed by confidence
    speed = max(0, sender_speed - sender_speed_conf)
    
    # Stationary vehicles may be off-road (parking)
    if speed <= self.params.MAX_NON_ROUTE_SPEED and distance <= 0:
        return 1.0
    
    radius = sender_pos_conf.x  # uncertainty radius
    circle_area = np.pi * radius * radius
    min_allowed = self.params.MAX_PLAUSIBLE_DIST_NEGATIVE
    
    # No uncertainty: simple threshold check
    if radius <= 0.0:
        return 1.0 if distance >= min_allowed else 0.0
    
    # Entirely off-road
    elif distance + radius <= min_allowed:
        return 0.0
    
    # Entirely on-road
    elif distance - radius >= min_allowed:
        return 1.0
    
    # Partial overlap: calculate area ratio using circle segment
    elif distance > min_allowed > distance - radius:
        d = abs(min_allowed - distance)
        seg = self.mdm_lib.berechne_kreisabschnitts_flaeche(radius, d)
        inside_area = circle_area - seg
        return max(0.0, min(1.0, inside_area / circle_area))
    
    elif distance < min_allowed < distance + radius:
        d = abs(min_allowed - distance)
        seg = self.mdm_lib.berechne_kreisabschnitts_flaeche(radius, d)
        return max(0.0, min(1.0, seg / circle_area))
    
    else:
        return 1.0
```

**Legacy Implementation:**
```python
def position_plausibility_check(self, sender_speed, distance_to_road):
    # Slow vehicles allowed off-road (parking)
    if sender_speed <= self.params.MAX_NON_ROUTE_SPEED:
        return 1.0
    
    return 1.0 if self.params.MAX_PLAUSIBLE_DIST_POSITIVE >= distance_to_road >= \
                  self.params.MAX_PLAUSIBLE_DIST_NEGATIVE else 0.0
```

**Misbehavior detected when:**
- CaTCH: `factor < 0.5` (most of uncertainty area off-road)
- Legacy: `distance < MAX_PLAUSIBLE_DIST_NEGATIVE`

### 3. Speed Plausibility Check

**Purpose:** Verify that reported speed is physically possible.

**Inputs:**
- `speed` - Reported speed
- `speed_conf` - Speed confidence/uncertainty

**CaTCH Implementation:**
```python
def speed_plausibility_check(self, speed, speed_conf):
    # Definitely plausible (entire confidence interval below max)
    if abs(speed) + abs(speed_conf) / 2 < self.params.MAX_PLAUSIBLE_SPEED:
        return 1.0
    
    # Definitely implausible (entire confidence interval above max)
    elif abs(speed) - abs(speed_conf) / 2 > self.params.MAX_PLAUSIBLE_SPEED:
        return 0.0
    
    # Partial overlap: calculate proportion within valid range
    else:
        factor = (abs(speed_conf) / 2 + 
                  (self.params.MAX_PLAUSIBLE_SPEED - abs(speed))) / abs(speed_conf)
        return factor
```

**Legacy Implementation:**
```python
def speed_plausibility_check(self, speed):
    return 1.0 if abs(speed) < self.params.MAX_PLAUSIBLE_SPEED else 0.0
```

**Misbehavior detected when:**
- CaTCH: `factor < 0.5`
- Legacy: `|speed| >= MAX_PLAUSIBLE_SPEED`

### 4. Position Consistency Check

**Purpose:** Verify that position change between consecutive messages is physically possible.

**Inputs:**
- `cur_pos`, `cur_pos_conf` - Current position and confidence
- `old_pos`, `old_pos_conf` - Previous position and confidence
- `time_delta` - Time between messages (seconds)

**CaTCH Implementation:**
```python
def position_consistency_check(self, cur_pos, cur_pos_conf,
                               old_pos, old_pos_conf, time_delta):
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    
    # Maximum possible distance at max speed
    max_range = self.params.MAX_PLAUSIBLE_SPEED * time_delta
    
    # Calculate overlap factor considering both position uncertainties
    factor = self.mdm_lib.circle_circle_factor(
        distance, 
        cur_pos_conf.x,   # current position uncertainty
        old_pos_conf.x,   # previous position uncertainty
        max_range
    )
    return factor
```

**Legacy Implementation:**
```python
def position_consistency_check(self, cur_pos, old_pos, time_delta):
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    max_distance = self.params.MAX_PLAUSIBLE_SPEED * time_delta
    return 1.0 if distance < max_distance else 0.0
```

**Misbehavior detected when:**
- Position change exceeds what's possible at maximum speed

### 5. Speed Consistency Check

**Purpose:** Verify that speed change between messages respects acceleration/deceleration limits.

**Inputs:**
- `cur_speed`, `cur_speed_conf` - Current speed and confidence
- `old_speed`, `old_speed_conf` - Previous speed and confidence
- `time_delta` - Time between messages

**CaTCH Implementation:**
```python
def speed_consistency_check(self, cur_speed, cur_speed_conf, 
                            old_speed, old_speed_conf, delta_time):
    speed_delta = cur_speed - old_speed
    
    if speed_delta > 0:  # Accelerating
        max_change = self.params.MAX_PLAUSIBLE_ACCEL * delta_time
    else:  # Decelerating
        max_change = self.params.MAX_PLAUSIBLE_DECEL * delta_time
    
    # Calculate factor using segment-segment overlap
    factor = self.mdm_lib.segment_segment_factor(
        abs(speed_delta), 
        cur_speed_conf, 
        old_speed_conf,
        max_change
    )
    return factor
```

**Legacy Implementation:**
```python
def speed_consistency_check(self, cur_speed, old_speed, time_delta):
    speed_delta = cur_speed - old_speed
    
    if speed_delta > 0:
        max_delta = self.params.MAX_PLAUSIBLE_ACCEL * time_delta
    else:
        max_delta = self.params.MAX_PLAUSIBLE_DECEL * time_delta
    
    return 1.0 if abs(speed_delta) < max_delta else 0.0
```

**Misbehavior detected when:**
- Acceleration or deceleration exceeds physical limits

### 6. Position-Speed Consistency Check

**Purpose:** Verify that traveled distance matches reported speeds (cross-validation).

**Inputs:**
- `cur_pos`, `cur_pos_conf`, `old_pos`, `old_pos_conf`
- `cur_speed`, `cur_speed_conf`, `old_speed`, `old_speed_conf`
- `delta_time`

**CaTCH Implementation:**
```python
def position_speed_consistency_check(self, cur_pos, cur_pos_conf, old_pos, old_pos_conf,
                                     cur_speed, cur_speed_conf, old_speed, old_speed_conf,
                                     delta_time):
    # Skip for large time gaps
    if delta_time >= self.params.MAX_TIME_DELTA:
        return 1.0
    
    # Special case: very slow vehicles
    if max(cur_speed, old_speed) < 1.0:
        distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
        max_possible_dist = max(cur_speed, old_speed) * delta_time
        if distance - (cur_pos_conf.x + old_pos_conf.x) <= max_possible_dist:
            return 1.0
    
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    
    # Three speed scenarios for robust checking:
    # 1. Optimistic: cur_speed + conf, old_speed - conf
    cur_speed_test_1 = cur_speed + cur_speed_conf
    old_speed_test_1 = old_speed - old_speed_conf
    
    # 2. Pessimistic: cur_speed - conf, old_speed + conf
    cur_speed_test_2 = cur_speed - cur_speed_conf
    old_speed_test_2 = old_speed + old_speed_conf
    
    # Ensure pessimistic scenario is consistent
    if cur_speed_test_2 < old_speed_test_2:
        cur_speed_test_2 = (cur_speed + old_speed) / 2
        old_speed_test_2 = (cur_speed + old_speed) / 2
    
    # Speed-dependent tolerance (quadratic formula)
    min_speed = min(cur_speed, old_speed)
    addon_mgt_range = max(0, self.params.MAX_MGT_RNG_DOWN + 
                          0.3571 * min_speed - 0.01694 * min_speed ** 2)
    
    # Calculate expected distance ranges for each scenario
    min_dist_1, max_dist_1 = self.mdm_lib.calculate_max_min_dist(
        cur_speed_test_1, old_speed_test_1, delta_time,
        self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)
    
    min_dist_2, max_dist_2 = self.mdm_lib.calculate_max_min_dist(
        cur_speed_test_2, old_speed_test_2, delta_time,
        self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)
    
    min_dist_0, max_dist_0 = self.mdm_lib.calculate_max_min_dist(
        cur_speed, old_speed, delta_time,
        self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)
    
    # Calculate factors for minimum distance violations
    factor_min_1 = 1 - self.mdm_lib.circle_circle_factor(
        distance, cur_pos_conf.x, old_pos_conf.x, min_dist_1)
    factor_min_2 = self.mdm_lib.one_sided_circle_segment_factor_minimum(
        distance, cur_pos_conf.x, old_pos_conf.x, min_dist_2 - addon_mgt_range)
    factor_min_0 = self.mdm_lib.one_sided_circle_segment_factor_minimum(
        distance, cur_pos_conf.x, old_pos_conf.x, min_dist_0 - addon_mgt_range)
    
    # Calculate factors for maximum distance violations
    factor_max_1 = self.mdm_lib.one_sided_circle_segment_factor(
        distance, cur_pos_conf.x, old_pos_conf.x, max_dist_1 + self.params.MAX_MGT_RNG_UP)
    factor_max_2 = self.mdm_lib.one_sided_circle_segment_factor(
        distance, cur_pos_conf.x, old_pos_conf.x, max_dist_2 + self.params.MAX_MGT_RNG_UP)
    factor_max_0 = self.mdm_lib.one_sided_circle_segment_factor(
        distance, cur_pos_conf.x, old_pos_conf.x, max_dist_0 + self.params.MAX_MGT_RNG_UP)
    
    # Average across all scenarios
    factor_min = (factor_min_1 + factor_min_0 + factor_min_2) / 3
    factor_max = (factor_max_0 + factor_max_1 + factor_max_2) / 3
    
    return min(factor_min, factor_max)
```

**Legacy Implementation:**
```python
def position_speed_consistency_check(self, cur_pos, old_pos,
                                     cur_speed, old_speed, time_delta):
    if time_delta >= self.params.MAX_TIME_DELTA:
        return 1.0
    
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    
    min_speed = min(cur_speed, old_speed)
    addon_mgt_range = max(0, self.params.MAX_MGT_RNG_DOWN + 
                          0.3571 * min_speed - 0.01694 * min_speed ** 2)
    
    min_dist, max_dist = self.mdm_lib.calculate_max_min_dist(
        cur_speed, old_speed, time_delta,
        self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL,
        self.params.MAX_PLAUSIBLE_SPEED)
    
    delta_min = distance - min_dist + addon_mgt_range
    delta_max = max_dist - distance + self.params.MAX_MGT_RNG_UP
    
    return 1.0 if (delta_min >= 0 and delta_max >= 0) else 0.0
```

**Misbehavior detected when:**
- Traveled distance doesn't match what's possible with reported speeds

### 7. Position-Heading Consistency Check

**Purpose:** Verify that heading (driving direction) matches actual movement direction.

**Inputs:**
- `cur_heading`, `cur_heading_conf` - Reported heading and confidence
- `cur_pos`, `cur_pos_conf`, `old_pos`, `old_pos_conf`
- `cur_speed`, `cur_speed_conf`
- `delta_time`

**CaTCH Implementation:**
```python
def position_heading_consistency_check(self, cur_heading, cur_heading_conf, 
                                       old_pos, old_pos_conf, cur_pos, cur_pos_conf, 
                                       delta_time, cur_speed, cur_speed_conf):
    # Skip for large time gaps
    if delta_time >= self.params.POS_HEADING_TIME:
        return 1.0
    
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    
    # Not enough movement to determine direction
    if distance < 1:
        return 1.0
    
    # Too slow to reliably determine heading
    if cur_speed - cur_speed_conf < 1:
        return 1.0
    
    # Calculate actual movement direction from position change
    relative_pos = Coord(cur_pos.x - old_pos.x, 
                         cur_pos.y - old_pos.y, 
                         cur_pos.z - old_pos.z)
    position_angle = self.mdm_lib.calculate_heading_angle(relative_pos)
    
    # Calculate angle difference
    angle_delta = abs(cur_heading - position_angle)
    if angle_delta > 180:
        angle_delta = 360 - angle_delta
    
    # Apply heading confidence to get angle bounds
    angle_low = max(0, angle_delta - cur_heading_conf)
    angle_high = min(180, angle_delta + cur_heading_conf)
    
    # Calculate factors using circle segment geometry
    x_low = distance * np.cos(angle_low * np.pi / 180)
    x_high = distance * np.cos(angle_high * np.pi / 180)
    
    # Factor for current position uncertainty
    if cur_pos_conf.x == 0:
        cur_factor_low = 1.0 if angle_low <= self.params.MAX_HEADING_CHANGE else 0.0
        cur_factor_high = 1.0 if angle_high <= self.params.MAX_HEADING_CHANGE else 0.0
    else:
        cur_factor_low = self.mdm_lib.calculate_circle_segment(
            cur_pos_conf.x, cur_pos_conf.x + x_low) / (np.pi * cur_pos_conf.x ** 2)
        cur_factor_high = self.mdm_lib.calculate_circle_segment(
            cur_pos_conf.x, cur_pos_conf.x + x_high) / (np.pi * cur_pos_conf.x ** 2)
    
    # Factor for old position uncertainty
    if old_pos_conf.x == 0:
        old_factor_low = 1.0 if angle_low <= self.params.MAX_HEADING_CHANGE else 0.0
        old_factor_high = 1.0 if angle_high <= self.params.MAX_HEADING_CHANGE else 0.0
    else:
        old_factor_low = 1 - self.mdm_lib.calculate_circle_segment(
            old_pos_conf.x, old_pos_conf.x - x_low) / (np.pi * old_pos_conf.x ** 2)
        old_factor_high = 1 - self.mdm_lib.calculate_circle_segment(
            old_pos_conf.x, old_pos_conf.x - x_high) / (np.pi * old_pos_conf.x ** 2)
    
    # Average all factors
    factor = (cur_factor_low + old_factor_low + cur_factor_high + old_factor_high) / 4
    return factor
```

**Legacy Implementation:**
```python
def position_heading_consistency_check(self, cur_heading, cur_pos,
                                       old_pos, time_delta, cur_speed):
    if time_delta >= self.params.POS_HEADING_TIME:
        return 1.0
    
    distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
    if distance < 1 or cur_speed < 1:
        return 1.0
    
    relative_pos = Coord(cur_pos.x - old_pos.x, 
                         cur_pos.y - old_pos.y, 
                         cur_pos.z - old_pos.z)
    position_angle = self.mdm_lib.calculate_heading_angle(relative_pos)
    
    angle_delta = abs(cur_heading - position_angle)
    if angle_delta > 180:
        angle_delta = 360 - angle_delta
    
    return 1.0 if angle_delta <= self.params.MAX_HEADING_CHANGE else 0.0
```

**Misbehavior detected when:**
- Reported heading differs significantly from actual movement direction

### 8. Intersection Check

**Purpose:** Verify that two vehicles don't occupy the same physical space.

**Inputs:**
- `pos_1`, `pos_1_conf` - First vehicle position and confidence
- `pos_2`, `pos_2_conf` - Second vehicle position and confidence  
- `heading_1`, `heading_2` - Vehicle headings
- `size` - Vehicle dimensions (default: 5m × 1.8m × 1.5m)
- `delta_time` - Time difference between messages

**CaTCH Implementation:**
```python
def intersection_check(self, pos_1, pos_1_conf, pos_2, pos_2_conf,
                       heading_1, heading_2, size, delta_time):
    # Normalize positions to local coordinate system
    origin_x = min(pos_1.x, pos_2.x)
    origin_y = min(pos_1.y, pos_2.y)
    
    pos_1_norm = Coord(pos_1.x - origin_x, pos_1.y - origin_y, pos_1.z)
    pos_2_norm = Coord(pos_2.x - origin_x, pos_2.y - origin_y, pos_2.z)
    
    # Model vehicles as ellipses (rectangle + uncertainty)
    # and calculate intersection factor using Shapely geometry
    factor = self.mdm_lib.ellipse_ellipse_intersection_factor(
        pos_1_norm, pos_1_conf, pos_2_norm, pos_2_conf,
        heading_1, heading_2, size, size
    )
    
    # Weight by time difference (recent = more important)
    time_factor = (self.params.MAX_DELTA_INTERSECTION - delta_time) / \
                   self.params.MAX_DELTA_INTERSECTION
    
    # Invert: high intersection → low factor (misbehavior)
    factor = 1.01 - factor * time_factor
    
    return max(0.0, min(1.0, factor))
```

**Legacy Implementation:**
```python
def intersection_check(self, pos_1, pos_2, node_size_1, node_size_2, 
                       heading_1, heading_2):
    # Model vehicles as rectangles
    intersection = self.mdm_lib.rect_rect_factor(
        pos_1, pos_2, heading_1, heading_2, node_size_1, node_size_2)
    
    # Weight by time window
    inter = intersection * ((self.params.MAX_DELTA_INTERSECTION - 
                             self.params.MAX_TIME_DELTA) / 
                            self.params.MAX_DELTA_INTERSECTION)
    
    return 0.0 if inter > 0.5 else 1.0
```

**Misbehavior detected when:**
- Two vehicles claim positions that would physically overlap

### 9. Sudden Appearance Check

>[!NOTE]
> Wasn't used in the evaluation of VeReMi NextGen and the comparison with VeReMi Extension

**Purpose:** Detect vehicles that suddenly appear within communication range.

**Inputs:**
- `receiver_pos`, `receiver_pos_conf`
- `sender_pos`, `sender_pos_conf`

**Precondition:** Only checked when sender is new OR not seen for > MAX_SA_TIME seconds.

**CaTCH Implementation:**
```python
def sudden_appearance_check(self, receiver_pos, receiver_pos_conf,
                            sender_pos, sender_pos_conf):
    distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
    
    # Detection zone radius including receiver uncertainty
    r2 = self.params.MAX_SA_RANGE + receiver_pos_conf.x
    
    # No sender uncertainty: simple threshold
    if sender_pos_conf.x <= 0:
        return 0.0 if distance < r2 else 1.0
    
    # Calculate what fraction of sender's uncertainty circle
    # falls OUTSIDE the sudden appearance detection zone
    overlap_area = self.mdm_lib.calculate_circle_circle_intersection(
        sender_pos_conf.x, r2, distance)
    
    sender_area = np.pi * sender_pos_conf.x ** 2
    factor = 1 - overlap_area / sender_area
    
    return factor
```

**Legacy Implementation:**
```python
def sudden_appearance_check(self, sender_pos, receiver_pos):
    distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
    return 0.0 if distance < self.params.MAX_SA_RANGE else 1.0
```

**Misbehavior detected when:**
- A vehicle appears inside the detection zone without being tracked approaching

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
