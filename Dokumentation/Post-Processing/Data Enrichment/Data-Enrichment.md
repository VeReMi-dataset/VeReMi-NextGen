# Data Enrichment

Enriches V2X messages with additional information from SUMO.

## Function

Calculates the **distance to the nearest road edge** (`distance_to_road_edge`) for each message. This information is essential for the **Position Plausibility Check**.

## Usage

```bash
python enrichMsgs.py <messages_folder> <sumo_config.sumocfg> [--workers N]
```

**Example:**
```bash
python enrichMsgs.py ./traces ./scenario.sumocfg --workers 8
```

## Algorithm

1. Extract position (x,y) from message
2. Via TraCI: Find nearest road edge (`edge_id`)
3. Calculate road center (considering all lanes)
4. Calculate distance from position to road edge



## TraCI Functions

| Function | Usage |
|----------|-------|
| `traci.simulation.convertRoad(x, y)` | Position → Edge/Lane |
| `traci.edge.getShape(edge_id)` | Edge geometry |
| `traci.lane.getWidth(lane_id)` | Lane width |
| `traci.edge.getAngle(edge_id, pos)` | Heading direction |
| `traci.simulation.convert2D(...)` | Edge position → Coordinates |
| `traci.simulation.getDistance2D(...)` | Calculate distance |

## Parallelization

- Starts N SUMO instances on different ports (8873 + worker_id)
- Each worker processes a chunk of JSON files
- One SUMO instance per worker (avoids reconnects)

```python
chunk_size = total_files // max_workers
# Worker 0: Files 0-99
# Worker 1: Files 100-199
# ...
```

## Output

Modifies JSON files in-place. Adds:

```json
{
  "sender": {
    "distance_to_road_edge": 3.5,
    ...
  }
}
```

## Error Handling

- Fallback when `convertRoad` fails: `getNeighboringEdges` within 500m radius
- On complete failure: `distance = 0`
- Failed files are logged
