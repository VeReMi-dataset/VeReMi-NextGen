from data_structures import Coord, Parameters
from mdm_lib import MDMLib


class LegacyChecks:
    def __init__(self, params: Parameters):
        self.params = params
        self.mdm_lib = MDMLib()

    def range_plausibility_check(self, sender_pos: Coord, receiver_pos: Coord) -> float:
        distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
        return 1.0 if distance < self.params.MAX_PLAUSIBLE_RANGE else 0.0

    def position_plausibility_check(self, sender_speed: float, distance_to_road: float) -> float:
        if sender_speed <= self.params.MAX_NON_ROUTE_SPEED:
            return 1.0

        return 1.0 if self.params.MAX_PLAUSIBLE_DIST_POSITIVE >= distance_to_road >=\
                      self.params.MAX_PLAUSIBLE_DIST_NEGATIVE else 0.0

    def speed_plausibility_check(self, speed: float) -> float:
        return 1.0 if abs(speed) < self.params.MAX_PLAUSIBLE_SPEED else 0.0

    def sudden_appearance_check(self, sender_pos: Coord, receiver_pos: Coord) -> float:
        distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)
        return 0.0 if distance < self.params.MAX_SA_RANGE else 1.0

    def position_consistency_check(self, cur_pos: Coord, old_pos: Coord, time_delta: float) -> float:
        distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
        max_distance = self.params.MAX_PLAUSIBLE_SPEED * time_delta
        return 1.0 if distance < max_distance else 0.0

    def speed_consistency_check(self, cur_speed: float, old_speed: float, time_delta: float) -> float:
        speed_delta = cur_speed - old_speed

        if speed_delta > 0:
            max_delta = self.params.MAX_PLAUSIBLE_ACCEL * time_delta
        else:
            max_delta = self.params.MAX_PLAUSIBLE_DECEL * time_delta

        return 1.0 if abs(speed_delta) < max_delta else 0.0

    def position_speed_consistency_check(self, cur_pos: Coord, old_pos: Coord,
                                         cur_speed: float, old_speed: float, time_delta: float) -> float:
        if time_delta >= self.params.MAX_TIME_DELTA:
            return 1.0

        distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)

        min_speed = min(cur_speed, old_speed)
        addon_mgt_range = max(0, self.params.MAX_MGT_RNG_DOWN + 0.3571 * min_speed - 0.01694 * min_speed * min_speed)

        min_dist, max_dist = self.mdm_lib.calculate_max_min_dist(
            cur_speed, old_speed, time_delta,
            self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL,
            self.params.MAX_PLAUSIBLE_SPEED
        )

        delta_min = distance - min_dist + addon_mgt_range
        delta_max = max_dist - distance + self.params.MAX_MGT_RNG_UP

        return 1.0 if (delta_min >= 0 and delta_max >= 0) else 0.0

    def position_heading_consistency_check(self, cur_heading: float, cur_pos: Coord,
                                           old_pos: Coord, time_delta: float, cur_speed: float) -> float:
        if time_delta >= self.params.POS_HEADING_TIME:
            return 1.0

        distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
        if distance < 1 or cur_speed < 1:
            return 1.0

        relative_pos = Coord(cur_pos.x - old_pos.x, cur_pos.y - old_pos.y, cur_pos.z - old_pos.z)
        position_angle = self.mdm_lib.calculate_heading_angle(relative_pos)

        angle_delta = abs(cur_heading - position_angle)
        if angle_delta > 180:
            angle_delta = 360 - angle_delta

        return 1.0 if angle_delta <= self.params.MAX_HEADING_CHANGE else 0.0

    def intersection_check(self, pos_1: Coord, pos_2: Coord, node_size_1: Coord, node_size_2: Coord, heading_1: float,
                           heading_2: float) -> float:
        intersection = self.mdm_lib.rect_rect_factor(pos_1, pos_2, heading_1, heading_2, node_size_1, node_size_2)

        inter = intersection * (
                    (self.params.MAX_DELTA_INTERSECTION - self.params.MAX_TIME_DELTA) / self.params.MAX_DELTA_INTERSECTION)

        return 0.0 if inter > 0.5 else 1.0
