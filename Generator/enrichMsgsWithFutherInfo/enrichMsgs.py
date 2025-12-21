import json
import traci
import sys
import math
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


def get_nearest_edge_neighbors(x: float, y: float, radius: float = 100):
    try:
        edges = traci.simulation.getNeighboringEdges(x, y, radius)
        if edges:
            edges_sorted = sorted(edges, key=lambda e: e[1])
            return edges_sorted[0][0]
    except:
        return None


def get_distance_to_nearest_road(x: float, y: float) -> float:
    try:
        edge_id = None
        lane_pos = None
        lane_index = None

        try:
            edge_id, lane_pos, lane_index = traci.simulation.convertRoad(x, y)
        except:
            pass

        if edge_id is None:
            try:
                edges = traci.simulation.getNeighboringEdges(x, y, 500)
                if edges:
                    edge_id = edges[0][0]
                    edge_shape = traci.edge.getShape(edge_id)
                    min_dist = float('inf')
                    for i, point in enumerate(edge_shape):
                        dist = traci.simulation.getDistance2D(x, y, point[0], point[1])
                        if dist < min_dist:
                            min_dist = dist
                            if i == 0:
                                lane_pos = 0
                            elif i == len(edge_shape) - 1:
                                lane_pos = traci.edge.getLength(edge_id)
                            else:
                                lane_pos = (i / (len(edge_shape) - 1)) * traci.edge.getLength(edge_id)
                    lane_index = 0
            except Exception as e:
                print(f"Fallback fehlgeschlagen für Position ({x}, {y}): {e}")
                return 0

        if edge_id is None:
            return 0

        num_lanes = traci.edge.getLaneNumber(edge_id)
        lane_id = f"{edge_id}_{lane_index}"
        lane_length = traci.lane.getLength(lane_id)
        lane_pos = max(0, min(lane_pos, lane_length))
        heading = traci.edge.getAngle(edge_id, lane_pos)

        center_x, center_y = traci.simulation.convert2D(edge_id, lane_pos, lane_index)

        total_offset = 0
        for i in range(lane_index, num_lanes):
            lane_width = traci.lane.getWidth(f"{edge_id}_{i}")
            if i > lane_index:
                total_offset += lane_width
            else:
                total_offset += lane_width / 2

        new_heading = (heading - 90) % 360
        heading_rad = math.radians(new_heading)
        right_angle = heading_rad

        mittle_edge_x = center_x + math.sin(right_angle) * total_offset
        mittle_edge_y = center_y + math.cos(right_angle) * total_offset
        right_lat, right_lon = traci.simulation.convertGeo(mittle_edge_x, mittle_edge_y)

        distance_mittle = traci.simulation.getDistance2D(mittle_edge_x, mittle_edge_y, x, y) * -1
        total_width = sum(traci.lane.getWidth(f"{edge_id}_{i}") for i in range(num_lanes))
        distance_edge = distance_mittle + total_width

        return distance_edge

    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 0


def parse_position(pos_string) -> Tuple[float, float, float]:
    if isinstance(pos_string, str):
        parts = pos_string.split(',')
    else:
        parts = pos_string
    return float(parts[0]), float(parts[1]), float(parts[2])


def reconstruct_nested(row):
    return {
        'rcvTime': row['rcvTime'],
        'sendTime': row['sendTime'],
        'sender_id': row['sender_id'],
        'sender_alias': row['sender_alias'],
        'messageID': row['messageID'],
        'attacker': row['attacker'],
        'receiver': {
            'pos': row['receiver_pos'],
            'pos_noise': row['receiver_pos_noise'],
            'spd': row['receiver_spd'],
            'spd_noise': row['receiver_spd_noise'],
            'acl': row['receiver_acl'],
            'acl_noise': row['receiver_acl_noise'],
            'hed': row['receiver_hed'],
            'hed_noise': row['receiver_hed_noise'],
            'driversProfile': row['receiver_driversProfile']
        },
        'sender': {
            'pos': row['sender_pos'],
            'pos_noise': row['sender_pos_noise'],
            'spd': row['sender_spd'],
            'spd_noise': row['sender_spd_noise'],
            'acl': row['sender_acl'],
            'acl_noise': row['sender_acl_noise'],
            'hed': row['sender_hed'],
            'hed_noise': row['sender_hed_noise'],
            'driversProfile': row['sender_driversProfile'],
            'distance_to_road_edge': row['distance_to_nearest_road_edge'],
        }
    }


def worker_process_batch(json_files: List[str], sumo_config: str, worker_id: int):
    """Worker verarbeitet mehrere JSON-Dateien mit einer SUMO-Instanz"""
    results = []
    port = 8873 + worker_id

    try:
        # SUMO einmal starten
        sumo_binary = "sumo"
        traci.start([sumo_binary, "-c", sumo_config, "--no-step-log", "true"],
                    port=port, label=str(port))

        # Alle zugewiesenen Dateien verarbeiten
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    messages = json.load(f)

                df = pd.json_normalize(messages, sep='_')
                df['distance_to_nearest_road_edge'] = np.nan

                for i, row in df.iterrows():
                    pos_string = row.get('sender_pos', '')
                    if pos_string:
                        x, y, z = parse_position(pos_string)
                        distanz = get_distance_to_nearest_road(x, y)
                        df.at[i, 'distance_to_nearest_road_edge'] = distanz

                messages_with_distance = df.apply(reconstruct_nested, axis=1).tolist()

                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(messages_with_distance, f, indent=2)

                results.append({'status': 'ok', 'file': json_file})

            except Exception as e:
                results.append({'status': 'error', 'file': json_file, 'error': str(e)})

    finally:
        traci.close()

    return results


def main():
    if len(sys.argv) < 3:
        print("Verwendung: py enrichMsgs_multithreading <messages_folder> <sumo_config.sumocfg> [--workers N]")
        sys.exit(1)

    input_folder = Path(sys.argv[1])
    sumo_config = sys.argv[2]

    # Optionale Worker-Anzahl
    max_workers = os.cpu_count() or 4
    if len(sys.argv) > 4 and sys.argv[3] == '--workers':
        max_workers = int(sys.argv[4])

    # Sammle alle JSON-Dateien
    json_files = list(input_folder.glob('*.json'))
    total_files = len(json_files)

    if total_files == 0:
        print("Keine JSON-Dateien gefunden!")
        sys.exit(1)

    print(f"Starting processing with {max_workers} workers...", file=sys.stderr)
    count = 0
    errors = []

    # Dateien auf Worker aufteilen
    chunk_size = max(1, total_files // max_workers)
    chunks = [json_files[i:i + chunk_size] for i in range(0, total_files, chunk_size)]

    with ProcessPoolExecutor(max_workers=min(max_workers, len(chunks))) as executor:
        futures = []

        for worker_id, chunk in enumerate(chunks):
            f = executor.submit(worker_process_batch,
                                [str(f) for f in chunk],
                                sumo_config,
                                worker_id)
            futures.append(f)

        # Ergebnisse sammeln
        for future in as_completed(futures):
            try:
                for result in future.result():
                    count += 1
                    if result['status'] == 'ok':
                        print(f"Processed file {count}/{total_files}: {Path(result['file']).name}")
                    else:
                        print(f"[ERROR] {Path(result['file']).name}: {result.get('error')}", file=sys.stderr)
                        errors.append((Path(result['file']).name, result.get('error')))
            except Exception as e:
                print(f"[ERROR] Worker failed: {e}", file=sys.stderr)

    # Zusammenfassung
    if errors:
        print(f"\n{len(errors)} Dateien mit Fehlern:", file=sys.stderr)
        for file, error in errors:
            print(f"  - {file}: {error}", file=sys.stderr)
    else:
        print(f"\nAlle {total_files} Dateien erfolgreich verarbeitet!")


if __name__ == "__main__":
    main()