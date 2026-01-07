# Data Enrichment

Calculates the **distance to the nearest road edge** (`distance_to_road_edge`) for each message. This information is essential for the **Position Plausibility Check**.

## Algorithm

1. Get position of the nearest lane
   ![](../../Resources/distance-Step1.pdf)
2. Get Heading of the lane
   ![](../../Resources/distance-Step2.pdf)
3. Calculate road center (considering all lanes)
   ![](../../Resources/distance-Step3.pdf)
4. Calculate distance from position to road center
   ![](../../Resources/distance-Step4.pdf)
5. Calculate the total width of the street (one direction)
   ![](../../Resources/distance-Step5.pdf)
6. Add total width to the distance from the car to the middle
   ![](../../Resources/distance-Step6.pdf)

## TraCI Functions

| Function                              | Usage                       |
|---------------------------------------|-----------------------------|
| `traci.simulation.convertRoad(x, y)`  | Position → Edge/Lane        |
| `traci.edge.getShape(edge_id)`        | Edge geometry               |
| `traci.lane.getWidth(lane_id)`        | Lane width                  |
| `traci.edge.getAngle(edge_id, pos)`   | Heading direction           |
| `traci.simulation.convert2D(...)`     | Edge position → Coordinates |
| `traci.simulation.getDistance2D(...)` | Calculate distance          |

## Parallelization

- Starts N SUMO instances on different ports (8873 + worker_id)
- Each worker processes a chunk of JSON files
- One SUMO instance per worker (avoids reconnects)

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
