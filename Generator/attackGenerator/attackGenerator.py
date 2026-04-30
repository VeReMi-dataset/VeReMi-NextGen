import argparse
import json
import traci
import math
from typing import Tuple
import pandas as pd
import random
import numpy as np
from pathlib import Path

ATTACK_RATIO = 0.2

parser = argparse.ArgumentParser(description="Sortiere ein JSON-Array nach sendTime.")
parser.add_argument("input_folder", help="Pfad zu den Eingabedateien")
parser.add_argument("misbehavior", help="Fehlverhalten angeben")
parser.add_argument("sumoConf", help="Pfad zum .sumocfg vom Szenario")
args = parser.parse_args()

input_folder = Path(args.input_folder)
sumo_config = args.sumoConf

misbehaviorOptions = [
    "timeDelayAttack",
    "constantPositionOffset",
    "randomPositionOffset",
    "positionMirroring",
    "constantSpeedOffset",
    "randomSpeedOffset",
    "zeroSpeedReport",
    "suddenStop",
    "suddenConstantSpeed",
    "reversedHeading",
    "feignedBraking",
    "accelerationMultiplication",
    "dosAttack",
    "trafficCongestionSybil",
    "dataReplay",
    "mixAll",
    "mixThree"
]

available_misbehaviors = [
    "timeDelayAttack",
    "constantPositionOffset",
    "randomPositionOffset",
    "positionMirroring",
    "constantSpeedOffset",
    "randomSpeedOffset",
    "zeroSpeedReport",
    "suddenStop",
    "suddenConstantSpeed",
    "reversedHeading",
    "feignedBraking",
    "accelerationMultiplication",
    "dosAttack",
    "trafficCongestionSybil",
    "dataReplay"
]

three_misbehaviors = [
    "constantPositionOffset",
    "randomSpeedOffset",
    "suddenStop",
]




###### support methods #######

def get_distance(pos1: str, pos2: str):
    p1 = np.array(pos1.split(','), dtype=np.float64)
    p2 = np.array(pos2.split(','), dtype=np.float64)
    return np.linalg.norm(p2 - p1)


def zufalls_float_mit_intervallen(pos_min, pos_max, neg_min, neg_max):
    intervall = random.choice(['positiv', 'negativ'])
    if intervall == 'positiv':
        return random.uniform(pos_min, pos_max)
    else:
        return random.uniform(neg_min, neg_max)


def reconstruct_nested(row):
    return {
        'rcvTime': row['rcvTime'],
        'sendTime': row['sendTime'],
        'sender_id': row['sender_id'],
        'sender_alias': row['sender_alias'],
        'messageID': row['messageID'],
        'attacker': row['attacker'],
        'receiver': {
            'pos': f"{row['receiver_pos_lat']},{row['receiver_pos_lon']},{row['receiver_pos_alt']}",
            'pos_noise': f"{row['receiver_pos_lat_noise']},{row['receiver_pos_lon_noise']},{row['receiver_pos_alt_noise']}",
            'spd': row['receiver_spd'],
            'spd_noise': row['receiver_spd_noise'],
            'acl': row['receiver_acl'],
            'acl_noise': row['receiver_acl_noise'],
            'hed': row['receiver_hed'],
            'hed_noise': row['receiver_hed_noise'],
            'driversProfile': row['receiver_driversProfile']
        },
        'sender': {
            'pos': f"{row['sender_pos_lat']},{row['sender_pos_lon']},{row['sender_pos_alt']}",
            'pos_noise': f"{row['sender_pos_lat_noise']},{row['sender_pos_lon_noise']},{row['sender_pos_alt_noise']}",
            'spd': row['sender_spd'],
            'spd_noise': row['sender_spd_noise'],
            'acl': row['sender_acl'],
            'acl_noise': row['sender_acl_noise'],
            'hed': row['sender_hed'],
            'hed_noise': row['sender_hed_noise'],
            'driversProfile': row['sender_driversProfile']
        }
    }


def get_distance_to_nearest_road(x: float, y: float, x_with_error: float, y_with_error: float) -> float:
    try:

        edge_id = None
        lane_pos = None
        lane_index = None

        try:
            edge_id, lane_pos, lane_index = traci.simulation.convertRoad(x, y)
        except:
            pass

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

        offset_to_other_side = (num_lanes * 3.2) / 2

        distance_mittle = traci.simulation.getDistance2D(mittle_edge_x, mittle_edge_y, x_with_error, y_with_error)
        return distance_mittle + offset_to_other_side

    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 0


def parse_position(pos_string: str) -> Tuple[float, float, float]:
    parts = pos_string.split(',')
    return float(parts[0]), float(parts[1]), float(parts[2])


def start_sumo():
    sumo_binary = "sumo"
    traci.start([sumo_binary, "-c", sumo_config, "--no-step-log", "true"])


def stop_sumo():
    traci.close()


def get_vehicle_offset(msg):
    pos_string = msg.get('sender_pos', '')
    if pos_string:
        x, y, z = parse_position(pos_string)
        x_error, y_error, z_error = parse_position(msg.get('sender_pos_noise', ''))
        distance = get_distance_to_nearest_road(x - x_error, y - y_error, x, y)
    else:
        distance = None

    return distance


def constant_position_offset(msg: pd.Series):
    msg['sender_pos_lat'] += misbehavior_config[msg['sender_id']]["offset_lat"]
    msg['sender_pos_lon'] += misbehavior_config[msg['sender_id']]["offset_lon"]
    msg['attacker'] = 1
    return msg


def time_delay_attack(msg: pd.Series):
    msg['sendTime'] += misbehavior_config[msg['sender_id']]['timeDelay']
    msg['rcvTime'] += misbehavior_config[msg['sender_id']]['timeDelay']
    msg['attacker'] = 1
    return msg


def random_position_offset(msg: pd.Series):
    global messages_lookup

    if msg['messageID'] in messages_lookup:
        attack_msg = messages_lookup[msg['messageID']].copy()
        attack_msg['receiver_pos'] = msg['receiver_pos']
        attack_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        attack_msg['receiver_spd'] = msg['receiver_spd']
        attack_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        attack_msg['receiver_acl'] = msg['receiver_acl']
        attack_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        attack_msg['receiver_hed'] = msg['receiver_hed']
        attack_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        attack_msg['receiver_driversProfile'] = msg['receiver_driversProfile']
        return attack_msg

    msg['sender_pos_lat'] += zufalls_float_mit_intervallen(20, 70, -70, -20)
    msg['sender_pos_lon'] += zufalls_float_mit_intervallen(20, 70, -70, -20)
    msg['attacker'] = 1
    messages_lookup[msg['messageID']] = msg.copy()
    return msg


def position_mirroring(msg: pd.Series):
    offset = get_vehicle_offset(msg)
    new_heading = (msg['sender_hed'] - 90) % 360
    heading_rad = math.radians(new_heading)
    msg['sender_pos_lat'] += math.sin(heading_rad) * offset
    msg['sender_pos_lon'] += math.cos(heading_rad) * offset
    msg['attacker'] = 1
    return msg


def constant_speed_offset(msg: pd.Series):
    msg['sender_spd'] += misbehavior_config[msg['sender_id']]["speedOffset"]
    msg['attacker'] = 1
    return msg


def random_speed_offset(msg: pd.Series):
    global messages_lookup

    if msg['messageID'] in messages_lookup:
        attack_msg = messages_lookup[msg['messageID']].copy()
        attack_msg['receiver_pos'] = msg['receiver_pos']
        attack_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        attack_msg['receiver_spd'] = msg['receiver_spd']
        attack_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        attack_msg['receiver_acl'] = msg['receiver_acl']
        attack_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        attack_msg['receiver_hed'] = msg['receiver_hed']
        attack_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        attack_msg['receiver_driversProfile'] = msg['receiver_driversProfile']
        return attack_msg

    msg['sender_spd'] += zufalls_float_mit_intervallen(1, 7, -7, -1)
    msg['attacker'] = 1
    messages_lookup[msg['messageID']] = msg.copy()
    return msg


def zero_speed_report(msg: pd.Series):
    global sender_lookup
    correct_msg = msg.copy()
    msg['sender_spd'] = 0
    if correct_msg['sender_spd'] > 1 and msg['sender_id'] in sender_lookup and get_distance(
            sender_lookup[msg['sender_id']]['sender_pos'], msg['sender_pos']) > 1.0:
        msg['attacker'] = 1
    elif correct_msg['sender_spd'] > 1 and msg['sender_id'] not in sender_lookup:
        msg['attacker'] = 1
    sender_lookup[msg['sender_id']] = correct_msg.copy()
    return msg


def sudden_stop(msg: pd.Series):
    random_number = random.uniform(0, 1)
    if misbehavior_config[msg['sender_id']]["msg"] is not None and misbehavior_config[msg['sender_id']]["stop_time"] < \
            msg['sendTime']:
        attack_msg = misbehavior_config[msg['sender_id']]["msg"].copy()
        attack_msg["sender_alias"] = msg['sender_alias']
        attack_msg['rcvTime'] = msg['rcvTime']
        attack_msg['sendTime'] = msg['sendTime']
        attack_msg['sender_id'] = msg['sender_id']
        attack_msg['messageID'] = msg['messageID']
        attack_msg['receiver_pos'] = msg['receiver_pos']
        attack_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        attack_msg['receiver_spd'] = msg['receiver_spd']
        attack_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        attack_msg['receiver_acl'] = msg['receiver_acl']
        attack_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        attack_msg['receiver_hed'] = msg['receiver_hed']
        attack_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        attack_msg['receiver_driversProfile'] = msg['receiver_driversProfile']
        if msg['sender_spd'] > 1 or get_distance(msg['sender_pos'], attack_msg['sender_pos']) >= 20:
            attack_msg['attacker'] = 1
        return attack_msg

    if misbehavior_config[msg['sender_id']]['stop_time'] is None and misbehavior_config[msg['sender_id']][
        "suddenStop"] > random_number:
        attacker = msg['sender_spd'] > 1 and msg['sender_acl'] >= 0
        msg['sender_spd'] = 0
        msg['sender_acl'] = 0
        misbehavior_config[msg['sender_id']]["msg"] = msg.copy()
        misbehavior_config[msg['sender_id']]['stop_time'] = msg['sendTime']
        attack_msg = misbehavior_config[msg['sender_id']]["msg"].copy()
        attack_msg["sender_alias"] = msg['sender_alias']
        if attacker:
            attack_msg['attacker'] = 1
        attack_msg['receiver_pos'] = msg['receiver_pos']
        attack_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        attack_msg['receiver_spd'] = msg['receiver_spd']
        attack_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        attack_msg['receiver_acl'] = msg['receiver_acl']
        attack_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        attack_msg['receiver_hed'] = msg['receiver_hed']
        attack_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        attack_msg['receiver_driversProfile'] = msg['receiver_driversProfile']
        return attack_msg

    return msg


def sudden_stop_speed(msg: pd.Series):
    random_number = random.uniform(0, 1)

    if misbehavior_config[msg['sender_id']]["saved_speed"] is not None and misbehavior_config[msg['sender_id']][
        "speed_freeze_time"] < msg['sendTime']:
        attacker = msg['sender_spd'] - misbehavior_config[msg['sender_id']]["saved_speed"] > 1
        msg['sender_spd'] = misbehavior_config[msg['sender_id']]["saved_speed"]
        if attacker:
            msg['attacker'] = 1
        return msg

    if misbehavior_config[msg['sender_id']]["speed_freeze_time"] is None and misbehavior_config[msg['sender_id']][
        "suddenConstantSpeed"] > random_number:
        misbehavior_config[msg['sender_id']]["saved_speed"] = msg['sender_spd']
        misbehavior_config[msg['sender_id']]["speed_freeze_time"] = msg['sendTime']
        return msg

    return msg


def reversed_heading(msg: pd.Series):
    global sender_lookup
    correct_msg = msg.copy()
    msg['sender_hed'] = (msg['sender_hed'] + 180) % 360
    if msg['sender_spd'] > 1 and msg['sender_id'] in sender_lookup and get_distance(
            sender_lookup[msg['sender_id']]['sender_pos'], msg['sender_pos']) > 1.0:
        msg['attacker'] = 1
    elif msg['sender_spd'] > 1 and msg['sender_id'] not in sender_lookup:
        msg['attacker'] = 1
    sender_lookup[msg['sender_id']] = correct_msg.copy()
    return msg


def feigned_braking(msg: pd.Series):
    original_acl = msg['sender_acl']
    if original_acl > 0:
        msg['sender_acl'] *= -1 * misbehavior_config[msg['sender_id']]["feigned_braking"]
        if original_acl > 0.25:
            msg['attacker'] = 1
    return msg


def acl_multiplication(msg: pd.Series):
    original_acl = msg['sender_acl']
    msg['sender_acl'] *= misbehavior_config[msg['sender_id']]["accelerationMult"]
    if original_acl > 0.5 or original_acl < -0.5:
        msg['attacker'] = 1
    return msg


def dos_attack(msg: pd.Series):
    msg['attacker'] = 1
    global df_attack
    amount = misbehavior_config[msg['sender_id']]["amount"]
    frequency = round(500000000 / misbehavior_config[msg['sender_id']]["amount"])
    i_values = np.arange(2000000, 2000000 + amount)
    u_values = np.arange(1, amount)
    new_sendTimes = msg['sendTime'] + frequency * u_values
    new_rcvTimes = msg['rcvTime'] + frequency * u_values
    new_messageIDs = msg['messageID'] + i_values
    new_data = []
    for i, (sendTime, rcvTime, messageID) in enumerate(zip(new_sendTimes, new_rcvTimes, new_messageIDs)):
        new_row = msg.copy()
        new_row['sendTime'] = sendTime
        new_row['rcvTime'] = rcvTime
        new_row['messageID'] = messageID
        new_row['attacker'] = 1
        new_data.append(new_row)

    df_attack = pd.concat([df_attack, pd.DataFrame(new_data)], ignore_index=True)
    return msg


def traffic_congestion_sybil(msg: pd.Series):
    global df_attack
    global messages_lookup

    if msg['messageID'] not in messages_lookup:
        amount = misbehavior_config[msg['sender_id']]["amount"]
        frequency = misbehavior_config[msg['sender_id']]["frequency"]

        i_values = np.arange(2000000, 2000000 + amount)
        new_sendTimes = msg['sendTime'] + frequency * i_values
        new_rcvTimes = msg['rcvTime'] + frequency * i_values
        new_messageIDs = msg['messageID'] + i_values

        new_data = []
        for i, (sendTime, rcvTime, messageID) in enumerate(zip(new_sendTimes, new_rcvTimes, new_messageIDs)):
            new_row = msg.copy()
            new_row['sendTime'] = sendTime
            new_row['rcvTime'] = rcvTime
            new_row['messageID'] = messageID
            new_row['sender_id'] = 'veh_' + str(random.randint(1000000, 9000000))
            new_row['sender_alias'] = random.randint(1111111111, 9999999999)
            heading_rad = math.radians(msg['sender_hed'])
            lateral_offset = zufalls_float_mit_intervallen(2, 3, -3, -2)
            new_row['sender_pos_lat'] += -math.sin(heading_rad) * lateral_offset
            new_row['sender_pos_lon'] += math.cos(heading_rad) * lateral_offset
            longitudinal_offset = zufalls_float_mit_intervallen(5, 6, -6, -5)
            new_row['sender_pos_lat'] += math.cos(heading_rad) * (longitudinal_offset * math.ceil(i / 2))
            new_row['sender_pos_lon'] += math.sin(heading_rad) * (longitudinal_offset * math.ceil(i / 2))
            new_row['attacker'] = 1
            new_row['sender_pos_lat'] = new_row['sender_pos_lat'] + random.uniform(-2, 2)
            new_row['sender_pos_lon'] = new_row['sender_pos_lon'] + random.uniform(-2, 2)
            new_row['sender_pos_lat_noise'] = new_row['sender_pos_lat_noise'] + new_row[
                'sender_pos_lat_noise'] * random.uniform(-0.10, 0.10)
            new_row['sender_pos_lon_noise'] = new_row['sender_pos_lon_noise'] + new_row[
                'sender_pos_lon_noise'] * random.uniform(-0.10, 0.10)
            new_row['sender_spd'] = msg['sender_spd'] + msg['sender_spd'] * random.uniform(-0.05, 0.05)
            new_row['sender_spd_noise'] = msg['sender_spd_noise'] + msg['sender_spd_noise'] * random.uniform(-0.10,
                                                                                                             0.10)
            new_row['sender_acl'] = msg['sender_acl'] + msg['sender_acl'] * random.uniform(-0.05, 0.05)
            new_row['sender_acl_noise'] = msg['sender_acl_noise'] + msg['sender_acl_noise'] * random.uniform(-0.10,
                                                                                                             0.10)
            new_row['sender_hed'] = msg['sender_hed'] + msg['sender_hed'] * random.uniform(-0.01, 0.01)
            new_row['sender_hed_noise'] = msg['sender_hed_noise'] + msg['sender_hed_noise'] * random.uniform(-0.10,
                                                                                                             0.10)
            new_data.append(new_row)
        messages_lookup[msg['messageID']] = new_data
    else:
        new_data = [row.copy() for row in messages_lookup[msg['messageID']]]

    for new_msg in new_data:
        new_msg['receiver_pos'] = msg['receiver_pos']
        new_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        new_msg['receiver_spd'] = msg['receiver_spd']
        new_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        new_msg['receiver_acl'] = msg['receiver_acl']
        new_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        new_msg['receiver_hed'] = msg['receiver_hed']
        new_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        new_msg['receiver_driversProfile'] = msg['receiver_driversProfile']

    df_attack = pd.concat([df_attack, pd.DataFrame(new_data)], ignore_index=True)
    return msg


def implement_data_replay_attack():
    global df_all
    df_all.sort_values(by='sendTime', ascending=True, inplace=True)
    df_all.loc[df_all['sender_id'].isin(attackerIDs)] = df_all.loc[df_all['sender_id'].isin(attackerIDs)] \
        .apply(data_replay_attack, axis=1)


def data_replay_attack(msg: pd.Series):
    global df_all
    detected_messages = df_all[
        (df_all['rcvTime'] <= msg['rcvTime']) &
        (df_all['rcvTime'] >= msg['rcvTime'] - 5000000000) &
        (((df_all['sender_pos_lat'] - msg['sender_pos_lat']) ** 2 +
          (df_all['sender_pos_lon'] - msg['sender_pos_lon']) ** 2) < 400 ** 2) &
        (df_all['sender_id'] != msg['sender_id'])
        ]
    if len(detected_messages) == 0:
        return msg
    config = misbehavior_config[msg['sender_id']]
    if config["replay_seq"] < config["max_replay_seq"]:
        attack_msgs = detected_messages.loc[(detected_messages['sender_alias'].isin([config["saved_alias"]])) &
                                            (detected_messages['rcvTime'] > config["saved_rcv_time"])].sort_values(
            by='sendTime', ascending=True)
        if len(attack_msgs) > 0:
            attack_msg = attack_msgs.iloc[0].copy()
            config["saved_rcv_time"] = attack_msg['rcvTime']
            config["replay_seq"] += 1
            attack_msg["sender_alias"] = msg['sender_alias']
            attack_msg["attacker"] = 1
            attack_msg["rcvTime"] = msg['rcvTime']
            attack_msg["sendTime"] = msg['sendTime']
            attack_msg["sender_id"] = msg['sender_id']
            attack_msg["messageID"] = msg['messageID']
            return attack_msg
    available_aliases = detected_messages[~detected_messages['sender_alias'].isin([config["saved_alias"]])]
    if len(available_aliases) == 0:
        return msg
    new_alias = available_aliases['sender_alias'].sample().iloc[0]
    attack_msg = \
        detected_messages[detected_messages['sender_alias'] == new_alias].sort_values(by='sendTime',
                                                                                      ascending=True).iloc[0].copy()
    config["replay_seq"] = 0
    config["saved_alias"] = attack_msg['sender_alias']
    config["saved_rcv_time"] = attack_msg['rcvTime']
    attack_msg["sender_alias"] = msg['sender_alias']
    attack_msg['attacker'] = 1
    attack_msg["rcvTime"] = msg['rcvTime']
    attack_msg["sendTime"] = msg['sendTime']
    attack_msg["sender_id"] = msg['sender_id']
    attack_msg["messageID"] = msg['messageID']
    return attack_msg


def insert_data_replay(msg: pd.Series):
    global df_all

    if msg['messageID'] in df_all['messageID'].values and df_all[df_all['messageID'] == msg['messageID']].iloc[0][
        'attacker'] == 1:
        attack_msg = df_all[df_all['messageID'] == msg['messageID']].iloc[0].copy()
        attack_msg['receiver_pos'] = msg['receiver_pos']
        attack_msg['receiver_pos_noise'] = msg['receiver_pos_noise']
        attack_msg['receiver_spd'] = msg['receiver_spd']
        attack_msg['receiver_spd_noise'] = msg['receiver_spd_noise']
        attack_msg['receiver_acl'] = msg['receiver_acl']
        attack_msg['receiver_acl_noise'] = msg['receiver_acl_noise']
        attack_msg['receiver_hed'] = msg['receiver_hed']
        attack_msg['receiver_hed_noise'] = msg['receiver_hed_noise']
        attack_msg['receiver_driversProfile'] = msg['receiver_driversProfile']
        return attack_msg
    else:
        return msg


def mixed_dispatcher(msg: pd.Series):
    assigned_misbehavior = misbehavior_config[msg['sender_id']].get("assigned_misbehavior")

    if not assigned_misbehavior:
        return msg

    misbehavior_functions = {
        "constantPositionOffset": constant_position_offset,
        "timeDelayAttack": time_delay_attack,
        "randomPositionOffset": random_position_offset,
        "positionMirroring": position_mirroring,
        "constantSpeedOffset": constant_speed_offset,
        "randomSpeedOffset": random_speed_offset,
        "zeroSpeedReport": zero_speed_report,
        "suddenStop": sudden_stop,
        "suddenConstantSpeed": sudden_stop_speed,
        "reversedHeading": reversed_heading,
        "feignedBraking": feigned_braking,
        "accelerationMultiplication": acl_multiplication,
        "dosAttack": dos_attack,
        "trafficCongestionSybil": traffic_congestion_sybil,
        "dataReplay": insert_data_replay
    }

    if assigned_misbehavior in misbehavior_functions:
        return misbehavior_functions[assigned_misbehavior](msg)

    return msg


def assign_misbehaviors_to_attackers(attacker_ids, misbehavior_list):
    num_attackers = len(attacker_ids)
    num_misbehaviors = len(misbehavior_list)

    repetitions = (num_attackers // num_misbehaviors) + 1
    misbehavior_assignments = misbehavior_list * repetitions

    random.shuffle(misbehavior_assignments)

    assignments = {}
    for i, attacker_id in enumerate(attacker_ids):
        assignments[attacker_id] = misbehavior_assignments[i]

    return assignments


def process_single_file(json_file):
    global df
    global misbehavior_config
    global df_attack
    global attackerIDs
    global messages_lookup
    global sender_lookup

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if len(data) < 1:
        print(f"Datei {json_file} ist leer, überspringe...")
        return

    df = pd.json_normalize(data, sep='_')
    df['attacker'] = 0

    # Metadaten Felder
    df['rcvTime'] = df['rcvTime'].astype(int)
    df['sendTime'] = df['sendTime'].astype(int)
    df['sender_id'] = df['sender_id'].astype(str)
    df['sender_alias'] = df['sender_alias'].astype(int)
    df['messageID'] = df['messageID'].astype(int)

    # Receiver Felder
    df['receiver_pos'] = df['receiver_pos'].astype(str)
    df['receiver_pos_noise'] = df['receiver_pos_noise'].astype(str)
    df['receiver_spd'] = df['receiver_spd'].astype(float)
    df['receiver_spd_noise'] = df['receiver_spd_noise'].astype(float)
    df['receiver_acl'] = df['receiver_acl'].astype(float)
    df['receiver_acl_noise'] = df['receiver_acl_noise'].astype(float)
    df['receiver_hed'] = df['receiver_hed'].astype(float)
    df['receiver_hed_noise'] = df['receiver_hed_noise'].astype(float)
    df['receiver_driversProfile'] = df['receiver_driversProfile'].astype(str)

    # Sender Felder
    df['sender_pos'] = df['sender_pos'].astype(str)
    df['sender_pos_noise'] = df['sender_pos_noise'].astype(str)
    df['sender_spd'] = df['sender_spd'].astype(float)
    df['sender_spd_noise'] = df['sender_spd_noise'].astype(float)
    df['sender_acl'] = df['sender_acl'].astype(float)
    df['sender_acl_noise'] = df['sender_acl_noise'].astype(float)
    df['sender_hed'] = df['sender_hed'].astype(float)
    df['sender_hed_noise'] = df['sender_hed_noise'].astype(float)
    df['sender_driversProfile'] = df['sender_driversProfile'].astype(str)

    # Split position strings
    df[['receiver_pos_lat', 'receiver_pos_lon', 'receiver_pos_alt']] = df['receiver_pos'].str.split(',',
                                                                                                    expand=True).astype(
        float)
    df[['receiver_pos_lat_noise', 'receiver_pos_lon_noise', 'receiver_pos_alt_noise']] = df[
        'receiver_pos_noise'].str.split(',', expand=True).astype(float)
    df[['sender_pos_lat', 'sender_pos_lon', 'sender_pos_alt']] = df['sender_pos'].str.split(',', expand=True).astype(
        float)
    df[['sender_pos_lat_noise', 'sender_pos_lon_noise', 'sender_pos_alt_noise']] = df['sender_pos_noise'].str.split(',',
                                                                                                                    expand=True).astype(
        float)

    df.sort_values(by='rcvTime', ascending=True, inplace=True)

    df_attack = df.copy()
    # Setup manipulation function
    if args.misbehavior in ["mixAll", "mixThree"]:
        manipulation_function = mixed_dispatcher
    else:
        match args.misbehavior:
            case "constantPositionOffset":
                manipulation_function = constant_position_offset
            case "timeDelayAttack":
                manipulation_function = time_delay_attack
            case "randomPositionOffset":
                manipulation_function = random_position_offset
            case "positionMirroring":
                manipulation_function = position_mirroring
            case "constantSpeedOffset":
                manipulation_function = constant_speed_offset
            case "randomSpeedOffset":
                manipulation_function = random_speed_offset
            case "zeroSpeedReport":
                manipulation_function = zero_speed_report
            case "suddenStop":
                manipulation_function = sudden_stop
            case "suddenConstantSpeed":
                manipulation_function = sudden_stop_speed
            case "reversedHeading":
                manipulation_function = reversed_heading
            case "feignedBraking":
                manipulation_function = feigned_braking
            case "accelerationMultiplication":
                manipulation_function = acl_multiplication
            case "dosAttack":
                manipulation_function = dos_attack
            case "trafficCongestionSybil":
                manipulation_function = traffic_congestion_sybil
            case "dataReplay":
                manipulation_function = insert_data_replay
            case _:
                raise ValueError(f"Missbehavior '{args.misbehavior}' ist nicht gefunden!")

    # Apply misbehavior
    df.loc[df['sender_id'].isin(attackerIDs)] = df.loc[df['sender_id'].isin(attackerIDs)].apply(manipulation_function,
                                                                                                axis=1)

    special_attacks = ["dosAttack", "trafficCongestionSybil"]

    if args.misbehavior in ["mixAll", "mixThree"]:
        assigned_specials = [misbehavior_config[aid].get("assigned_misbehavior")
                             for aid in attackerIDs
                             if misbehavior_config[aid].get("assigned_misbehavior") in special_attacks]
        if assigned_specials:
            new_rows = df_attack[~df_attack['messageID'].isin(df['messageID'])]
            df = pd.concat([df, new_rows], ignore_index=True)
    elif args.misbehavior in special_attacks:
        new_rows = df_attack[~df_attack['messageID'].isin(df['messageID'])]
        df = pd.concat([df, new_rows], ignore_index=True)

    df.sort_values(by='rcvTime', ascending=True, inplace=True)

    # Konvertiere zurück zur verschachtelten Struktur
    nested_data = df.apply(reconstruct_nested, axis=1).tolist()

    # Speichern
    output_file = input_folder.parent / f"{input_folder.name}_{args.misbehavior}" / f"{json_file.name}"
    with open(output_file, 'w') as f:
        json.dump(nested_data, f, indent=4)


def set_up_misbehavior_config():
    if args.misbehavior == "mixAll":
        assignments = assign_misbehaviors_to_attackers(attackerIDs, available_misbehaviors)
        for attacker_id in attackerIDs:
            misbehavior_config[attacker_id]["assigned_misbehavior"] = assignments[attacker_id]
            assigned = assignments[attacker_id]
            if assigned == "constantPositionOffset":
                misbehavior_config[attacker_id]["offset_lat"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
                misbehavior_config[attacker_id]["offset_lon"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
            elif assigned == "timeDelayAttack":
                misbehavior_config[attacker_id]["timeDelay"] = random.randint(2000000000, 4000000000)
            elif assigned == "constantSpeedOffset":
                misbehavior_config[attacker_id]["speedOffset"] = zufalls_float_mit_intervallen(1, 7, -7, -1)
            elif assigned == "suddenStop":
                misbehavior_config[attacker_id]["msg"] = None
                misbehavior_config[attacker_id]["stop_time"] = None
                misbehavior_config[attacker_id]["suddenStop"] = 0.05
            elif assigned == "suddenConstantSpeed":
                misbehavior_config[attacker_id]["saved_speed"] = None
                misbehavior_config[attacker_id]["speed_freeze_time"] = None
                misbehavior_config[attacker_id]["suddenConstantSpeed"] = 0.05
            elif assigned == "feignedBraking":
                misbehavior_config[attacker_id]["feigned_braking"] = random.uniform(2, 4)
            elif assigned == "accelerationMultiplication":
                misbehavior_config[attacker_id]["accelerationMult"] = random.uniform(2, 4)
            elif assigned == "dosAttack":
                misbehavior_config[attacker_id]["amount"] = random.randint(2, 4)
            elif assigned == "trafficCongestionSybil":
                misbehavior_config[attacker_id]["frequency"] = random.randint(1000, 100000)
                misbehavior_config[attacker_id]["amount"] = random.randint(4, 6)
            elif assigned == "dataReplay":
                misbehavior_config[attacker_id]["replay_seq"] = 0
                misbehavior_config[attacker_id]["max_replay_seq"] = random.randint(4, 8)
                misbehavior_config[attacker_id]["saved_alias"] = None
                misbehavior_config[attacker_id]["saved_rcv_time"] = 0

    elif args.misbehavior == "mixThree":
        assignments = assign_misbehaviors_to_attackers(attackerIDs, three_misbehaviors)
        for attacker_id in attackerIDs:
            misbehavior_config[attacker_id]["assigned_misbehavior"] = assignments[attacker_id]
            assigned = assignments[attacker_id]
            if assigned == "constantPositionOffset":
                misbehavior_config[attacker_id]["offset_lat"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
                misbehavior_config[attacker_id]["offset_lon"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
            elif assigned == "randomSpeedOffset":
                pass
            elif assigned == "suddenStop":
                misbehavior_config[attacker_id]["msg"] = None
                misbehavior_config[attacker_id]["stop_time"] = None
                misbehavior_config[attacker_id]["suddenStop"] = 0.05
            elif assigned == "timeDelayAttack":
                misbehavior_config[attacker_id]["timeDelay"] = random.randint(2000000000, 4000000000)

    else:
        match args.misbehavior:
            case "constantPositionOffset":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["offset_lat"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
                    misbehavior_config[attacker_id]["offset_lon"] = zufalls_float_mit_intervallen(20, 70, -70, -20)
            case "timeDelayAttack":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["timeDelay"] = random.randint(2000000000, 4000000000)
            case "constantSpeedOffset":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["speedOffset"] = zufalls_float_mit_intervallen(1, 7, -7, -1)
            case "suddenStop":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["msg"] = None
                    misbehavior_config[attacker_id]["stop_time"] = None
                    misbehavior_config[attacker_id]["suddenStop"] = 0.05
            case "suddenConstantSpeed":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["saved_speed"] = None
                    misbehavior_config[attacker_id]["speed_freeze_time"] = None
                    misbehavior_config[attacker_id]["suddenConstantSpeed"] = 0.05
            case "feignedBraking":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["feigned_braking"] = random.uniform(2, 4)
            case "accelerationMultiplication":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["accelerationMult"] = random.uniform(2, 4)
            case "dosAttack":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["amount"] = random.randint(2, 4)
            case "trafficCongestionSybil":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["frequency"] = random.randint(1000, 100000)
                    misbehavior_config[attacker_id]["amount"] = random.randint(4, 6)
            case "dataReplay":
                for attacker_id in attackerIDs:
                    misbehavior_config[attacker_id]["replay_seq"] = 0
                    misbehavior_config[attacker_id]["max_replay_seq"] = random.randint(4, 8)
                    misbehavior_config[attacker_id]["saved_alias"] = None
                    misbehavior_config[attacker_id]["saved_rcv_time"] = 0


# Main execution
if __name__ == "__main__":
    df_all = pd.DataFrame()
    misbehavior_config = dict()
    messages_lookup = {}
    sender_lookup = {}
    misbehavior_config['ratio'] = ATTACK_RATIO
    output_dir = input_folder.parent / f"{input_folder.name}_{args.misbehavior}"
    output_dir.mkdir(exist_ok=True)

    for json_file in input_folder.glob('*.json'):
        with open(json_file, 'r') as f:
            data = json.load(f)
            df_temp = pd.json_normalize(data, sep='_')
            df_all = pd.concat([df_all, df_temp], ignore_index=True)
    df_all = df_all.drop_duplicates(subset='messageID')

    df_all['attacker'] = 0

    # Metadaten Felder
    df_all['rcvTime'] = df_all['rcvTime'].astype(int)
    df_all['sendTime'] = df_all['sendTime'].astype(int)
    df_all['sender_id'] = df_all['sender_id'].astype(str)
    df_all['sender_alias'] = df_all['sender_alias'].astype(int)
    df_all['messageID'] = df_all['messageID'].astype(int)

    # Receiver Felder
    df_all['receiver_pos'] = df_all['receiver_pos'].astype(str)
    df_all['receiver_pos_noise'] = df_all['receiver_pos_noise'].astype(str)
    df_all['receiver_spd'] = df_all['receiver_spd'].astype(float)
    df_all['receiver_spd_noise'] = df_all['receiver_spd_noise'].astype(float)
    df_all['receiver_acl'] = df_all['receiver_acl'].astype(float)
    df_all['receiver_acl_noise'] = df_all['receiver_acl_noise'].astype(float)
    df_all['receiver_hed'] = df_all['receiver_hed'].astype(float)
    df_all['receiver_hed_noise'] = df_all['receiver_hed_noise'].astype(float)
    df_all['receiver_driversProfile'] = df_all['receiver_driversProfile'].astype(str)

    # Sender Felder
    df_all['sender_pos'] = df_all['sender_pos'].astype(str)
    df_all['sender_pos_noise'] = df_all['sender_pos_noise'].astype(str)
    df_all['sender_spd'] = df_all['sender_spd'].astype(float)
    df_all['sender_spd_noise'] = df_all['sender_spd_noise'].astype(float)
    df_all['sender_acl'] = df_all['sender_acl'].astype(float)
    df_all['sender_acl_noise'] = df_all['sender_acl_noise'].astype(float)
    df_all['sender_hed'] = df_all['sender_hed'].astype(float)
    df_all['sender_hed_noise'] = df_all['sender_hed_noise'].astype(float)
    df_all['sender_driversProfile'] = df_all['sender_driversProfile'].astype(str)

    # Split position strings
    df_all[['receiver_pos_lat', 'receiver_pos_lon', 'receiver_pos_alt']] = df_all['receiver_pos'].str.split(',',
                                                                                                            expand=True).astype(
        float)
    df_all[['receiver_pos_lat_noise', 'receiver_pos_lon_noise', 'receiver_pos_alt_noise']] = df_all[
        'receiver_pos_noise'].str.split(',', expand=True).astype(float)
    df_all[['sender_pos_lat', 'sender_pos_lon', 'sender_pos_alt']] = df_all['sender_pos'].str.split(',',
                                                                                                    expand=True).astype(
        float)
    df_all[['sender_pos_lat_noise', 'sender_pos_lon_noise', 'sender_pos_alt_noise']] = df_all[
        'sender_pos_noise'].str.split(',',
                                      expand=True).astype(
        float)

    attackerIDs = random.sample(df_all['sender_id'].unique().tolist(),
                                int(len(df_all['sender_id'].unique()) * misbehavior_config["ratio"]))

    for attacker_id in attackerIDs:
        misbehavior_config[attacker_id] = {}

    set_up_misbehavior_config()

    if args.misbehavior in ["mixAll", "mixThree"]:
        print(f"\n[INFO] Misbehavior-Zuweisung für {args.misbehavior}:")
        misbehavior_counts = {}
        for attacker_id in attackerIDs:
            assigned = misbehavior_config[attacker_id].get("assigned_misbehavior")
            if assigned:
                misbehavior_counts[assigned] = misbehavior_counts.get(assigned, 0) + 1

        for misbehavior, count in sorted(misbehavior_counts.items()):
            print(f"  - {misbehavior}: {count} Angreifer")
        print()

    if args.misbehavior == "dataReplay":
        implement_data_replay_attack()
    elif args.misbehavior in ["mixAll", "mixThree"]:
        has_data_replay = any(
            misbehavior_config[aid].get("assigned_misbehavior") == "dataReplay"
            for aid in attackerIDs
        )
        if has_data_replay:
            original_attackerIDs = attackerIDs.copy()
            attackerIDs = [aid for aid in attackerIDs
                           if misbehavior_config[aid].get("assigned_misbehavior") == "dataReplay"]
            if attackerIDs:
                implement_data_replay_attack()
            attackerIDs = original_attackerIDs

    needs_sumo = False
    if args.misbehavior == "positionMirroring":
        needs_sumo = True
    elif args.misbehavior in ["mixAll", "mixThree"]:
        for attacker_id in attackerIDs:
            if misbehavior_config[attacker_id].get("assigned_misbehavior") == "positionMirroring":
                needs_sumo = True
                break

    if needs_sumo:
        start_sumo()

    files_to_process = [f for f in input_folder.glob('*.json')
                        if not f.stem.endswith(tuple(misbehaviorOptions))]

    total_files = len(files_to_process)
    count = 0

    for json_file in input_folder.glob('*.json'):
        if not json_file.stem.endswith(tuple(misbehaviorOptions)):
            process_single_file(json_file)
            count += 1
            print(f"Processing misbehavior for file {count}/{total_files}: {json_file.name}")

    if needs_sumo:
        stop_sumo()

    print(f"[OK] Completed processing {total_files} files")
