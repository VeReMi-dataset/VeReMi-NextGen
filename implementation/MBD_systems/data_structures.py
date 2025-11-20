from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class Coord:
    x: np.float64 = np.float64(0.0)
    y: np.float64 = np.float64(0.0)
    z: np.float64 = np.float64(0.0)

    def __post_init__(self):
        self.x = np.float64(self.x)
        self.y = np.float64(self.y)
        self.z = np.float64(self.z)

    def to_array(self):
        return np.array([self.x, self.y, self.z], dtype=np.float64)


@dataclass
class VehicleData:
    pos: Coord = field(default_factory=lambda: Coord(0, 0, 0))
    pos_noise: Coord = field(default_factory=lambda: Coord(0, 0, 0))
    spd: float = 0
    spd_noise: float = 0
    acl: float = 0
    acl_noise: float = 0
    hed: float = 0
    hed_noise: float = 0
    distance_to_road_edge: float = 0
    driversProfile: str = "None"


@dataclass
class Message:
    rcvTime: int = 0
    sendTime: int = 0
    sender_id: str = 0
    sender_alias: int = 0
    messageID: int = 0
    attacker: int = 0
    prediction: int = 0
    receiver: VehicleData = field(default_factory=VehicleData)
    sender: VehicleData = field(default_factory=VehicleData)


@dataclass
class Parameters:
    # RANGE & DISTANCE PARAMETER
    MAX_PLAUSIBLE_RANGE: float = 418.13997683369433  # mpr
    MAX_SA_RANGE: float = 150.0  # msar
    MAX_PLAUSIBLE_DIST_NEGATIVE: float = -4.498043609151968  # mpdn

    # GESCHWINDIGKEIT & BESCHLEUNIGUNG
    MAX_PLAUSIBLE_SPEED: float = 62.329252544679385  # mps
    MAX_PLAUSIBLE_ACCEL: float = 5.418563530162665  # mpa
    MAX_PLAUSIBLE_DECEL: float = 5.005295111839574  # mpd

    # HEADING & INTERSECTION
    MAX_HEADING_CHANGE: float = 76.23960198184574  # mhc
    MAX_DELTA_INTERSECTION: float = 4.297205392054125  # mdi

    # ZEIT-PARAMETER
    MAX_TIME_DELTA: float = 4.7243132992341765  # mtd
    POS_HEADING_TIME: float = 0.39809268515981683  # pht
    MAX_MGT_RNG_UP: float =  0.7063553998663573  # mmru
    MAX_MGT_RNG_DOWN: float = 1.0299180161460522  # mmrd
    MAX_SA_TIME: float = 2.1  # msat

    # ROUTE & SCHWELLWERTE
    MAX_NON_ROUTE_SPEED: float =  0.6798715937399384  # mnrs


class Mapper:

    @staticmethod
    def row_to_message(row: pd.Series) -> Message:
        receiver = VehicleData(
            pos=Coord(x=row['receiver_pos_lat'], y=row['receiver_pos_lon'], z=row['receiver_pos_alt']),
            pos_noise=Coord(x=row['receiver_pos_lat_noise'], y=row['receiver_pos_lon_noise'],
                            z=row['receiver_pos_alt_noise']),
            spd=row['receiver_spd'],
            spd_noise=row['receiver_spd_noise'],
            acl=row['receiver_acl'],
            acl_noise=row['receiver_acl_noise'],
            hed=row['receiver_hed'],
            hed_noise=row['receiver_hed_noise'],
            distance_to_road_edge=0.0,
            driversProfile=row['receiver_driversProfile']
        )

        sender = VehicleData(
            pos=Coord(x=row['sender_pos_lat'], y=row['sender_pos_lon'], z=row['sender_pos_alt']),
            pos_noise=Coord(x=row['sender_pos_lat_noise'], y=row['sender_pos_lon_noise'],
                            z=row['sender_pos_alt_noise']),
            spd=row['sender_spd'],
            spd_noise=row['sender_spd_noise'],
            acl=row['sender_acl'],
            acl_noise=row['sender_acl_noise'],
            hed=row['sender_hed'],
            hed_noise=row['sender_hed_noise'],
            distance_to_road_edge=row['sender_distance_to_road_edge'],
            driversProfile=row['sender_driversProfile']
        )

        return Message(
            rcvTime=int(row['rcvTime']),
            sendTime=int(row['sendTime']),
            sender_id=row['sender_id'],
            sender_alias=int(row['sender_alias']),
            messageID=int(row['messageID']),
            attacker=int(row['attacker']),
            prediction=0,
            receiver=receiver,
            sender=sender
        )

    @staticmethod
    def row_to_json(row: pd.Series):
        return {
            'rcvTime': row['rcvTime'],
            'sendTime': row['sendTime'],
            'sender_id': row['sender_id'],
            'sender_alias': row['sender_alias'],
            'messageID': row['messageID'],
            'attacker': row['attacker'],
            'prediction': row['prediction'],
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
                'driversProfile': row['sender_driversProfile'],
                'distance_to_road_edge': row['sender_distance_to_road_edge']
            },
            'check': {
                'range_plausibility_check': row.get('check_range_plausibility', -1),
                'position_plausibility_check': row.get('check_position_plausibility_check', -1),
                'speed_plausibility_check': row.get('check_speed_plausibility_check', -1),
                'position_consistency_check': row.get('check_position_consistency_check', -1),
                'speed_consistency_check': row.get('check_speed_consistency_check', -1),
                'position_speed_consistency_check': row.get('check_position_speed_consistency_check', -1),
                'position_heading_consistency_check': row.get('check_position_heading_consistency_check', -1),
                'intersection_check': row.get('check_intersection_check', -1),
                'sudden_appearance_check': row.get('check_sudden_appearance_check', -1)
            }
        }
