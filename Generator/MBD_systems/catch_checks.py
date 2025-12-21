from data_structures import Coord, Parameters
from mdm_lib import MDMLib
import numpy as np

np.seterr(all='warn', over='raise')

class CatchChecks:
    def __init__(self, params: Parameters):
        self.params = params
        self.mdm_lib = MDMLib()

    def range_plausibility_check(self, receiver_pos: Coord, receiver_pos_conf: Coord,
                                 sender_pos: Coord, sender_pos_conf: Coord) -> float:
        distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)

        factor = self.mdm_lib.circle_circle_factor(
            distance, sender_pos_conf.x, receiver_pos_conf.x,
            self.params.MAX_PLAUSIBLE_RANGE
        )

        return factor

    def position_plausibility_check(self, sender_pos_conf: Coord, sender_speed: float,
                                    sender_speed_conf: float, distance: float):
        speed = sender_speed - sender_speed_conf
        if speed < 0:
            speed = 0

        if speed <= self.params.MAX_NON_ROUTE_SPEED and distance <= 0:
            return 1

        radius = self.mdm_lib.convert_list_to_float(sender_pos_conf)
        circle_area = np.pi * radius * radius
        min_allowed = self.params.MAX_PLAUSIBLE_DIST_NEGATIVE

        if radius <= 0.0:
            return 1.0 if distance >= min_allowed else 0.0
        elif distance + radius <= min_allowed:
            return 0.0
        elif distance - radius >= min_allowed:
            return 1
        elif distance > min_allowed > distance - radius:
            d = abs(min_allowed - distance)
            seg = self.mdm_lib.berechne_kreisabschnitts_flaeche(radius, d)
            inside_area = circle_area - seg
            factor = inside_area / circle_area
            return max(0.0, min(1.0, factor))
        elif distance < min_allowed < distance + radius:
            d = abs(min_allowed - distance)
            seg = self.mdm_lib.berechne_kreisabschnitts_flaeche(radius, d)
            inside_area = seg
            factor = inside_area / circle_area
            return max(0.0, min(1.0, factor))
        else:
            return 1

    def speed_plausibility_check(self, speed: float, speed_conf: float) -> float:

        if (abs(speed) + abs(speed_conf) / 2) < self.params.MAX_PLAUSIBLE_SPEED:
            return 1.0
        elif (abs(speed) - abs(speed_conf) / 2) > self.params.MAX_PLAUSIBLE_SPEED:
            return 0.0
        else:
            factor = (abs(speed_conf) / 2 + (self.params.MAX_PLAUSIBLE_SPEED - abs(speed))) / abs(
                speed_conf)
            return factor

    def position_consistency_check(self, cur_pos: Coord, cur_pos_conf: Coord,
                                   old_pos: Coord, old_pos_conf: Coord, time_delta: float) -> float:
        time_delta = np.float64(time_delta)
        cur_conf_x = np.float64(cur_pos_conf.x)
        old_conf_x = np.float64(old_pos_conf.x)
        distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
        max_range = np.float64(self.params.MAX_PLAUSIBLE_SPEED) * time_delta
        factor = self.mdm_lib.circle_circle_factor(
            distance, cur_conf_x, old_conf_x, max_range
        )
        return factor

    def speed_consistency_check(self, cur_speed: float, cur_speed_conf: float, old_speed: float, old_speed_conf: float,
                                delta_time: float):
        speed_delta = cur_speed - old_speed
        factor = 1
        if speed_delta > 0:
            factor = self.mdm_lib.segment_segment_factor(speed_delta, cur_speed_conf, old_speed_conf,
                                                         self.params.MAX_PLAUSIBLE_ACCEL * delta_time)
        else:
            factor = self.mdm_lib.segment_segment_factor(abs(speed_delta), cur_speed_conf, old_speed_conf,
                                                         self.params.MAX_PLAUSIBLE_DECEL * delta_time)

        return factor

    def position_speed_consistency_check(self, cur_pos: Coord, cur_pos_conf: Coord, old_pos: Coord, old_pos_conf: Coord,
                                         cur_speed: float, cur_speed_conf: float, old_speed: float,
                                         old_speed_conf: float,
                                         delta_time: float):
        cur_speed = np.float64(cur_speed)
        old_speed = np.float64(old_speed)
        cur_speed_conf = np.float64(cur_speed_conf)
        old_speed_conf = np.float64(old_speed_conf)
        delta_time = np.float64(delta_time)
        if delta_time < np.float64(self.params.MAX_TIME_DELTA):

            if max(cur_speed, old_speed) < np.float64(1.0):
                distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
                max_possible_dist = max(cur_speed, old_speed) * delta_time
                if distance - (cur_pos_conf.x + old_pos_conf.x) <= max_possible_dist:
                    return 1.0

            distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
            cur_speed_test_1 = np.float64(cur_speed + cur_speed_conf)
            old_speed_test_1 = np.float64(old_speed - old_speed_conf)
            cur_speed_test_2 = np.float64(cur_speed - cur_speed_conf)
            old_speed_test_2 = np.float64(old_speed + old_speed_conf)

            if cur_speed_test_2 < old_speed_test_2:
                cur_speed_test_2 = (cur_speed + old_speed) / 2
                old_speed_test_2 = (cur_speed + old_speed) / 2

            min_speed = min(cur_speed, old_speed)
            addon_mgt_range = self.params.MAX_MGT_RNG_DOWN + 0.3571 * min_speed - 0.01694 * min_speed * min_speed

            if addon_mgt_range < 0:
                addon_mgt_range = 0

            min_distance_1, max_distance_1 = \
                self.mdm_lib.calculate_max_min_dist(cur_speed_test_1, old_speed_test_1, delta_time,
                                                    self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)

            factor_min_1 = 1 - self.mdm_lib.circle_circle_factor(distance, cur_pos_conf.x, old_pos_conf.x,
                                                                 min_distance_1)
            factor_max_1 = self.mdm_lib.one_sided_circle_segment_factor(distance, cur_pos_conf.x, old_pos_conf.x,
                                                                        max_distance_1 + self.params.MAX_MGT_RNG_UP)

            min_distance_2, max_distance_2 = \
                self.mdm_lib.calculate_max_min_dist(cur_speed_test_2, old_speed_test_2, delta_time,
                                                    self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)
            factor_min_2 = self.mdm_lib.one_sided_circle_segment_factor_minimum(
                distance, cur_pos_conf.x, old_pos_conf.x, min_distance_2 - addon_mgt_range)
            factor_max_2 = self.mdm_lib.one_sided_circle_segment_factor(distance, cur_pos_conf.x, old_pos_conf.x,
                                                                        max_distance_2 + self.params.MAX_MGT_RNG_UP)

            min_distance_0, max_distance_0 = \
                self.mdm_lib.calculate_max_min_dist(cur_speed, old_speed, delta_time,
                                                    self.params.MAX_PLAUSIBLE_ACCEL, self.params.MAX_PLAUSIBLE_DECEL)

            factor_min_0 = self.mdm_lib.one_sided_circle_segment_factor_minimum(
                distance, cur_pos_conf.x, old_pos_conf.x, min_distance_0 - addon_mgt_range)
            factor_max_0 = self.mdm_lib.one_sided_circle_segment_factor(distance, cur_pos_conf.x, old_pos_conf.x,
                                                                        max_distance_0 + self.params.MAX_MGT_RNG_UP)

            factor_min = (factor_min_1 + factor_min_0 + factor_min_2) / 3
            factor_max = (factor_max_0 + factor_max_1 + factor_max_2) / 3

            return min(factor_min, factor_max)
        else:
            return 1.0

    def position_heading_consistency_check(self, cur_heading: float, cur_heading_conf: float, old_pos: Coord,
                                           old_pos_conf: Coord, cur_pos: Coord, cur_pos_conf: Coord, delta_time: float,
                                           cur_speed: float, cur_speed_conf: float):
        if delta_time < self.params.POS_HEADING_TIME:
            distance = self.mdm_lib.calculate_distance(cur_pos, old_pos)
            if distance < 1:
                return 1


            if cur_speed - cur_speed_conf < 1:
                return 1

            relative_pos = Coord(np.float64(cur_pos.x - old_pos.x), np.float64(cur_pos.y - old_pos.y), np.float64(cur_pos.z - old_pos.z))
            position_angle = self.mdm_lib.calculate_heading_angle(relative_pos)


            angle_delta = abs(cur_heading - position_angle)
            if angle_delta > 180:
                angle_delta = 360 - angle_delta

            angle_low = angle_delta - cur_heading_conf
            if angle_low < 0:
                angle_low = 0

            angle_high = angle_delta + cur_heading_conf
            if angle_high > 180:
                angle_high = 180

            x_low = distance * np.cos(angle_low * np.pi / 180)

            cur_factor_low = 1
            if cur_pos_conf.x == 0:
                if angle_low <= self.params.MAX_HEADING_CHANGE:
                    cur_factor_low = 1
                else:
                    cur_factor_low = 0
            else:
                cur_factor_low = self.mdm_lib.calculate_circle_segment(cur_pos_conf.x, cur_pos_conf.x + x_low) / \
                                 (np.pi * cur_pos_conf.x * cur_pos_conf.x)

            old_factor_low = 1
            if old_pos_conf.x == 0:
                if angle_low <= self.params.MAX_HEADING_CHANGE:
                    old_factor_low = 1
                else:
                    old_factor_low = 0
            else:
                old_factor_low = 1 - self.mdm_lib.calculate_circle_segment(old_pos_conf.x, old_pos_conf.x - x_low) / \
                                 (np.pi * old_pos_conf.x * old_pos_conf.x)

            x_high = distance * np.cos(angle_high * np.pi / 180)

            cur_factor_high = 1
            if cur_pos_conf.x == 0:
                if angle_high <= self.params.MAX_HEADING_CHANGE:
                    cur_factor_high = 1
                else:
                    cur_factor_high = 0
            else:
                cur_factor_high = self.mdm_lib.calculate_circle_segment(cur_pos_conf.x, cur_pos_conf.x + x_high) / \
                                  (np.pi * cur_pos_conf.x * cur_pos_conf.x)

            old_factor_high = 1
            if old_pos_conf.x == 0:
                if angle_high <= self.params.MAX_HEADING_CHANGE:
                    old_factor_high = 1
                else:
                    old_factor_high = 0
            else:
                old_factor_high = 1 - self.mdm_lib.calculate_circle_segment(old_pos_conf.x, old_pos_conf.x - x_high) / \
                                  (np.pi * old_pos_conf.x * old_pos_conf.x)

            factor = (cur_factor_low + old_factor_low + cur_factor_high + old_factor_high) / 4

            return factor
        else:
            return 1

    def intersection_check(self, pos_1: Coord, pos_1_conf: Coord,
                           pos_2: Coord, pos_2_conf: Coord,
                           heading_1: float, heading_2: float,
                           size: Coord, delta_time: float):

        delta_time = np.float64(delta_time)
        heading_1 = np.float64(heading_1)
        heading_2 = np.float64(heading_2)

        origin_x = np.float64(min(pos_1.x, pos_2.x))
        origin_y = np.float64(min(pos_1.y, pos_2.y))

        pos_1_norm = Coord(
            x=np.float64(pos_1.x - origin_x),
            y=np.float64(pos_1.y - origin_y),
            z=np.float64(pos_1.z)
        )

        pos_2_norm = Coord(
            x=np.float64(pos_2.x - origin_x),
            y=np.float64(pos_2.y - origin_y),
            z=np.float64(pos_2.z)
        )

        factor = self.mdm_lib.ellipse_ellipse_intersection_factor(
            pos_1_norm, pos_1_conf, pos_2_norm, pos_2_conf,
            heading_1, heading_2, size, size
        )

        time_factor = (np.float64(self.params.MAX_DELTA_INTERSECTION) - delta_time) / \
                      np.float64(self.params.MAX_DELTA_INTERSECTION)

        factor = np.float64(1.01) - factor * time_factor

        return np.float64(max(0.0, min(1.0, factor)))

    def sudden_appearance_check(self, receiver_pos: Coord, receiver_pos_conf: Coord,
                                sender_pos: Coord, sender_pos_conf: Coord) -> float:
        distance = self.mdm_lib.calculate_distance(sender_pos, receiver_pos)

        r2 = self.params.MAX_SA_RANGE + receiver_pos_conf.x

        if sender_pos_conf.x <= 0:
            return 0.0 if distance < r2 else 1.0
        else:
            area = self.mdm_lib.calculate_circle_circle_intersection(
                sender_pos_conf.x, r2, distance
            )
            factor = 1 - area / (np.pi * sender_pos_conf.x * sender_pos_conf.x)
            return factor
