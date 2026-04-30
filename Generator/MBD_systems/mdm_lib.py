import logging
import math
import sys

import numpy as np
from typing import Tuple, List, Optional
from data_structures import Coord, Message
from shapely.geometry import Point
from shapely.affinity import scale, rotate

np.seterr(all='warn', over='raise')


class MDMLib:

    @staticmethod
    def ns_to_seconds(nanoseconds: int) -> float:
        return nanoseconds / 1e9

    @staticmethod
    def calculate_distance(pos1: Coord, pos2: Coord) -> float:
        return np.float64(math.hypot(pos1.x - pos2.x, pos1.y - pos2.y))

    @staticmethod
    def safe_acos(x: float) -> float:
        return np.arccos(np.clip(x, -1.0, 1.0))

    @staticmethod
    def calculate_heading_angle(heading: Coord) -> float:
        angle = np.arctan2(heading.x, heading.y) * 180 / np.pi
        if angle < 0:
            angle += 360
        return angle

    @staticmethod
    def calculate_circle_segment(radius: float, int_distance: float) -> float:
        if radius <= 0 or int_distance <= 0:
            return 0
        if int_distance > 2 * radius:
            return np.pi * radius * radius

        if radius > int_distance:
            area = radius * radius * MDMLib.safe_acos((radius - int_distance) / radius)
            area -= (radius - int_distance) * np.sqrt(2 * radius * int_distance - int_distance * int_distance)
        else:
            int_distance_temp = 2 * radius - int_distance
            area = radius * radius * MDMLib.safe_acos((radius - int_distance_temp) / radius)
            area -= (radius - int_distance_temp) * np.sqrt(
                2 * radius * int_distance_temp - int_distance_temp * int_distance_temp)
            area = np.pi * radius * radius - area

        return area

    @staticmethod
    def calculate_circle_circle_intersection(r0: float, r1: float, d: float) -> float:
        r0 = np.float64(r0)
        r1 = np.float64(r1)
        d = np.float64(d)

        if r0 <= 0 or r1 <= 0:
            return np.float64(0)

        rr0 = r0 * r0
        rr1 = r1 * r1
        dd = d * d

        if d > r1 + r0:
            return np.float64(0)
        elif d <= abs(r0 - r1) and r0 >= r1:
            return np.pi * rr1
        elif d <= abs(r0 - r1) and r0 < r1:
            return np.pi * rr0
        else:
            arg1 = (rr0 + dd - rr1) / (np.float64(2) * r0 * d)
            arg2 = (rr1 + dd - rr0) / (np.float64(2) * r1 * d)

            phi = np.float64(2) * MDMLib.safe_acos(arg1)
            theta = np.float64(2) * MDMLib.safe_acos(arg2)

            area1 = np.float64(0.5) * theta * rr1 - np.float64(0.5) * rr1 * np.sin(theta)
            area2 = np.float64(0.5) * phi * rr0 - np.float64(0.5) * rr0 * np.sin(phi)

            return area1 + area2

    @staticmethod
    def circle_circle_factor(d: float, r1: float, r2: float, range_val: float) -> float:
        d = np.float64(d)
        r1 = np.float64(r1)
        r2 = np.float64(r2)
        range_val = np.float64(range_val)

        d1, d2 = np.float64(0), np.float64(0)

        if d > 0:
            # Use of float64 for all calculations
            r1_sq = r1 * r1
            r2_sq = r2 * r2
            d_sq = d * d

            d1 = (r1_sq + d_sq - r2_sq) / (np.float64(2) * d)
            d2 = (r2_sq + d_sq - r1_sq) / (np.float64(2) * d)

            half_range = range_val / np.float64(2)

            if (d1 + r1) < half_range and (d2 + r2) > half_range:
                shift = half_range - (d1 + r1)
                d2 = d2 - shift
                d1 = d1 + shift

            if (d2 + r2) < half_range and (d1 + r1) > half_range:
                shift = half_range - (d2 + r2)
                d1 = d1 - shift
                d2 = d2 + shift


        if r1 <= 0 and r2 <= 0:
            return np.float64(1.0) if range_val >= d else np.float64(0.0)
        elif r1 <= 0:
            if range_val / 2 >= d1:
                area2 = MDMLib.calculate_circle_circle_intersection(r2, range_val / 2, d2)
                return area2 / (np.pi * r2 * r2)
            return 0
        elif r2 <= 0:
            if range_val / 2 >= d2:
                area1 = MDMLib.calculate_circle_circle_intersection(r1, range_val / 2, d1)
                return area1 / (np.pi * r1 * r1)
            return 0
        else:
            area1 = MDMLib.calculate_circle_circle_intersection(r1, range_val / 2, d1)
            area2 = MDMLib.calculate_circle_circle_intersection(r2, range_val / 2, d2)
            return (area1 + area2) / (np.pi * r1 * r1 + np.pi * r2 * r2)

    @staticmethod
    def calculate_max_min_dist(cur_speed: float, old_speed: float, time: float,
                               max_accel: float, max_decel: float) -> Tuple[
        float, float]:

        cur_speed = max(0.0, float(cur_speed))
        old_speed = max(0.0, float(old_speed))

        avg_speed = (cur_speed + old_speed) / 2
        base_distance = avg_speed * time

        delta_v = abs(cur_speed - old_speed)
        required_accel = delta_v / time

        if required_accel < 1.0:
            variation_factor = 0.02
        elif required_accel < 2.5:
            variation_factor = 0.03 + (required_accel - 1.0) * 0.02
        elif required_accel < 5.0:
            variation_factor = 0.05 + (required_accel - 2.5) * 0.02
        else:
            variation_factor = 0.10

        speed_factor = 1.0
        if avg_speed > 30:
            speed_factor = 0.7
        elif avg_speed > 20:
            speed_factor = 0.85

        if cur_speed > old_speed:
            theoretical_max_extra = 0.25 * max_accel * time * time
            theoretical_min_less = 0.25 * max_decel * time * time
        else:
            theoretical_max_extra = 0.25 * max_accel * time * time
            theoretical_min_less = 0.25 * max_decel * time * time

        max_variation = min(
            base_distance * variation_factor * speed_factor,
            theoretical_max_extra
        )
        min_variation = min(
            base_distance * variation_factor * speed_factor,
            theoretical_min_less
        )

        min_distance = base_distance - min_variation
        max_distance = base_distance + max_variation

        min_distance = max(0, min_distance)

        if delta_v < 1.0:
            min_distance = max(min_distance, base_distance - 1.0)
            max_distance = min(max_distance, base_distance + 1.0)
        elif delta_v < 3.0:
            min_distance = max(min_distance, base_distance - 2.0)
            max_distance = min(max_distance, base_distance + 2.0)

        return min_distance, max_distance

    @staticmethod
    def rect_rect_factor(pos1: Coord, pos2: Coord,
                         heading1: float, heading2: float,
                         size1: Coord, size2: Coord) -> float:

        h1_rad = np.radians(heading1)
        h2_rad = np.radians(heading2)

        half_width1 = size1.x / 2
        half_length1 = size1.y / 2

        cos1, sin1 = np.cos(h1_rad), np.sin(h1_rad)
        corners1 = [
            [pos1.x + cos1 * half_width1 - sin1 * half_length1,
             pos1.y + sin1 * half_width1 + cos1 * half_length1],
            [pos1.x - cos1 * half_width1 - sin1 * half_length1,
             pos1.y - sin1 * half_width1 + cos1 * half_length1],
            [pos1.x - cos1 * half_width1 + sin1 * half_length1,
             pos1.y - sin1 * half_width1 - cos1 * half_length1],
            [pos1.x + cos1 * half_width1 + sin1 * half_length1,
             pos1.y + sin1 * half_width1 - cos1 * half_length1]
        ]

        half_width2 = size2.x / 2
        half_length2 = size2.y / 2

        cos2, sin2 = np.cos(h2_rad), np.sin(h2_rad)
        corners2 = [
            [pos2.x + cos2 * half_width2 - sin2 * half_length2,
             pos2.y + sin2 * half_width2 + cos2 * half_length2],
            [pos2.x - cos2 * half_width2 - sin2 * half_length2,
             pos2.y - sin2 * half_width2 + cos2 * half_length2],
            [pos2.x - cos2 * half_width2 + sin2 * half_length2,
             pos2.y - sin2 * half_width2 - cos2 * half_length2],
            [pos2.x + cos2 * half_width2 + sin2 * half_length2,
             pos2.y + sin2 * half_width2 - cos2 * half_length2]
        ]

        distance = np.linalg.norm(np.array([pos1.x, pos1.y]) - np.array([pos2.x, pos2.y]))
        max_diagonal1 = np.sqrt(size1.x ** 2 + size1.y ** 2) / 2
        max_diagonal2 = np.sqrt(size2.x ** 2 + size2.y ** 2) / 2

        if distance > max_diagonal1 + max_diagonal2:
            return 0.0

        if distance < (max_diagonal1 + max_diagonal2) * 0.5:
            overlap_estimate = 1.0 - (distance / (max_diagonal1 + max_diagonal2))

            # Consider size ratio
            area1 = size1.x * size1.y
            area2 = size2.x * size2.y
            min_area = min(area1, area2)
            max_area = max(area1, area2)
            size_factor = min_area / max_area

            # Combine factors
            intersection_factor = overlap_estimate * size_factor
            return min(1.0, intersection_factor)

        return 0.0

    @staticmethod
    def berechne_kreisabschnitts_flaeche(radius: float, d: float) -> float:
        radius = np.float64(radius)
        d = np.float64(d)

        if d >= radius:
            return np.float64(0.0)

        theta = MDMLib.safe_acos(d / radius)
        sektor_flaeche = radius * radius * theta
        dreieck_flaeche = d * np.sqrt(radius * radius - d * d)

        return np.float64(sektor_flaeche - dreieck_flaeche)

    @staticmethod
    def convert_list_to_float(value: Coord) -> float:
        return np.linalg.norm(np.array([value.x, value.y, value.z]))

    @staticmethod
    def segment_segment_factor(d: float, r1: float, r2: float, total_range: float) -> float:
        d = np.float64(d)
        r1 = np.float64(r1)
        r2 = np.float64(r2)
        total_range = np.float64(total_range)
        d1 = np.float64(0.0)
        d2 = np.float64(0.0)
        if d > 0:
            d1 = (r1 * r1 + d * d - r2 * r2) / (np.float64(2) * d)
            d2 = (r2 * r2 + d * d - r1 * r1) / (np.float64(2) * d)

            half_range = total_range / 2.0
            if (d1 + r1) < half_range and (d2 + r2) > half_range:
                shift = half_range - (d1 + r1)
                d1 += shift
                d2 -= shift
            if (d2 + r2) < half_range and (d1 + r1) > half_range:
                shift = half_range - (d2 + r2)
                d2 += shift
                d1 -= shift

        overlap1 = 0.0
        overlap2 = 0.0

        half_range = total_range / 2.0
        addon = 0.0
        diff1 = d1 - half_range
        if diff1 < r1:
            if diff1 > -r1:
                addon = -(d1 - r1)
                overlap1 = half_range + addon
            else:
                overlap1 = 2 * r1

        diff2 = d2 - half_range
        if diff2 < r2:
            if diff2 > -r2:
                addon = -(d2 - r2)
                overlap2 = half_range + addon
            else:
                overlap2 = 2 * r2

        if r1 == 0.0 and r2 == 0.0:
            return 0.0 if d > total_range else 1.0

        factor = (overlap1 + overlap2) / (2 * r1 + 2 * r2)
        return factor

    @staticmethod
    def one_sided_circle_segment_factor_minimum(distance: float, r1: float, r2: float,
                                                min_required: float) -> float:
        distance = np.float64(distance)
        r1 = np.float64(r1)
        r2 = np.float64(r2)
        min_required = np.float64(min_required)

        if distance < 0:
            return 0.0

        if distance - r1 - r2 >= min_required:
            return 1.0

        if distance + r1 + r2 <= min_required:
            return 0.0

        if r1 <= 0 and r2 <= 0:
            return 1.0 if distance >= min_required else 0.0

        elif r1 <= 0:
            if distance >= min_required - r2:
                overlap = min(1.0, (distance + r2 - min_required) / (2 * r2))
                return max(0.0, overlap)
            else:
                return 0.0

        elif r2 <= 0:
            if distance >= min_required - r1:
                overlap = min(1.0, (distance + r1 - min_required) / (2 * r1))
                return max(0.0, overlap)
            else:
                return 0.0

        else:
            min_possible = distance - r1 - r2
            max_possible = distance + r1 + r2

            if min_possible >= min_required:
                return 1.0
            elif max_possible <= min_required:
                return 0.0
            else:
                if min_required <= min_possible:
                    return 1.0
                elif min_required >= max_possible:
                    return 0.0
                else:
                    ok_range = max_possible - min_required
                    total_range = max_possible - min_possible

                    if total_range > 0:
                        base_factor = ok_range / total_range

                        if distance > 0:
                            d1 = (r1 * r1 + distance * distance - r2 * r2) / (2 * distance)
                            d2 = distance - d1

                            distance_factor = (distance - min_required) / (r1 + r2)

                            if distance_factor > 0:
                                weight = min(1.0, 0.5 + distance_factor)
                            else:
                                weight = max(0.0, 0.5 + distance_factor)

                            return base_factor * weight
                        else:
                            return base_factor
                    else:
                        return 0.5

    @staticmethod
    def one_sided_circle_segment_factor(d: float, r1: float, r2: float, total_range: float) -> float:
        if d < 0:
            return 1.0

        if total_range > d + r1 + r2:
            return 1.0
        elif total_range < d - r1 - r2:
            return 0.0
        else:
            d1 = 0.0
            d2 = 0.0
            if d > 0:
                d1 = (r1 ** 2 + d ** 2 - r2 ** 2) / (2 * d)
                d2 = (r2 ** 2 + d ** 2 - r1 ** 2) / (2 * d)

                half_range = total_range / 2.0
                if (d1 + r1) < half_range and (d2 + r2) > half_range:
                    shift = half_range - (d1 + r1)
                    d1 += shift
                    d2 -= shift
                if (d2 + r2) < half_range and (d1 + r1) > half_range:
                    shift = half_range - (d2 + r2)
                    d2 += shift
                    d1 -= shift

            if r1 <= 0 and r2 <= 0:
                return 1.0 if total_range >= d else 0.0

            elif r1 <= 0:
                if total_range / 2.0 >= d1:
                    int_d2 = total_range / 2.0 - (d2 - r2)
                    area2 = MDMLib.calculate_circle_segment(r2, int_d2)
                    return area2 / (np.pi * r2 ** 2)
                else:
                    return 0.0

            elif r2 <= 0:
                if total_range / 2.0 >= d2:
                    int_d1 = total_range / 2.0 - (d1 - r1)
                    area1 = MDMLib.calculate_circle_segment(r1, int_d1)
                    return area1 / (np.pi * r1 ** 2)
                else:
                    return 0.0

            else:
                int_d1 = total_range / 2.0 - (d1 - r1)
                int_d2 = total_range / 2.0 - (d2 - r2)

                area1 = MDMLib.calculate_circle_segment(r1, int_d1)
                area2 = MDMLib.calculate_circle_segment(r2, int_d2)

                total_area = np.pi * r1 ** 2 + np.pi * r2 ** 2
                return (area1 + area2) / total_area

    @staticmethod
    def gaussian_sum(x: float, sig: float) -> float:
        x = x / sig

        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911

        sign = 1
        if x < 0:
            sign = -1
        x = abs(x) / np.sqrt(2.0)

        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t + a3) * t + a2) * t + a1)
                   * t * np.exp(-x * x))

        return 0.5 * (1.0 + sign * y)

    @staticmethod
    def bounded_gaussian_sum(x1: float, x2: float, sig: float) -> float:
        return MDMLib.gaussian_sum(x2, sig) - MDMLib.gaussian_sum(x1, sig)

    @staticmethod
    def importance_factor(r1, r2, d):
        r1 = np.float64(r1)
        r2 = np.float64(r2)
        d = np.float64(d)

        overlap = r2 + r1 - d

        if d < np.float64(1e-10):
            return np.float64(0)

        if overlap < 0:
            return np.float64(0)

        s1 = e1 = s2 = e2 = np.float64(0)

        if r2 > r1:
            if overlap < 2 * r1:
                s1 = -r1
                e1 = -r1 + overlap

                s2 = -r2
                e2 = -r2 + overlap
            else:
                s1 = -r1
                e1 = r1
                s2 = -(d + r1)
                e2 = -(d - r1)
        else:
            if overlap < 2 * r2:
                s2 = -r2
                e2 = -r2 + overlap

                s1 = -r1
                e1 = -r1 + overlap
            else:
                s2 = -r2
                e2 = r2

                s1 = -(d + r2)
                e1 = -(d - r2)

        sig1 = r1 / np.float64(3)
        sig2 = r2 / np.float64(3)

        if s1 == -r1:
            if e1 == r1:
                factor1 = 1
            else:
                factor1 = MDMLib.gaussian_sum(e1, sig1)
        else:
            factor1 = MDMLib.bounded_gaussian_sum(s1, e1, sig1)

        if s2 == -r2:
            if e2 == r2:
                factor2 = 1
            else:
                factor2 = MDMLib.gaussian_sum(e2, sig2)
        else:
            factor2 = MDMLib.bounded_gaussian_sum(s2, e2, sig2)

        # Normieren
        factor1 /= ((e1 - s1) / (2 * r1))
        factor2 /= ((e2 - s2) / (2 * r2))

        return (2 * (factor1 * factor2) / (factor1 + factor2)) / d

    @staticmethod
    def ellipse_int_area(cx1, cy1, w1, h1, r1, cx2, cy2, w2, h2, r2):
        from shapely.geometry import Point
        from shapely.affinity import scale, rotate, translate

        cx1, cy1 = np.float64(cx1), np.float64(cy1)
        cx2, cy2 = np.float64(cx2), np.float64(cy2)
        w1, h1 = np.float64(w1), np.float64(h1)
        w2, h2 = np.float64(w2), np.float64(h2)
        r1, r2 = np.float64(r1), np.float64(r2)

        offset_x = np.float64(min(cx1, cx2))
        offset_y = np.float64(min(cy1, cy2))

        rel_cx1 = cx1 - offset_x
        rel_cy1 = cy1 - offset_y
        rel_cx2 = cx2 - offset_x
        rel_cy2 = cy2 - offset_y

        try:
            ellipse1 = Point(0, 0).buffer(1)
            ellipse1 = scale(ellipse1, xfact=w1 / 2, yfact=h1 / 2)
            ellipse1 = rotate(ellipse1, r1, use_radians=False)
            ellipse1 = translate(ellipse1, xoff=rel_cx1, yoff=rel_cy1)

            ellipse2 = Point(0, 0).buffer(1)
            ellipse2 = scale(ellipse2, xfact=w2 / 2, yfact=h2 / 2)
            ellipse2 = rotate(ellipse2, r2, use_radians=False)
            ellipse2 = translate(ellipse2, xoff=rel_cx2, yoff=rel_cy2)

            intersection = ellipse1.intersection(ellipse2)

            return np.float64(intersection.area)

        except Exception as e:
            print(f"Shapely calculation failed, using circle approximation: {e}")

            avg_r1 = np.float64((w1 + h1) / 4)
            avg_r2 = np.float64((w2 + h2) / 4)
            dist = np.float64(math.hypot(rel_cx1 - rel_cx2, rel_cy1 - rel_cy2))

            return MDMLib.calculate_circle_circle_intersection(avg_r1, avg_r2, dist)

    @staticmethod
    def ellipse_ellipse_intersection_factor(
            pos1: Coord, pos_conf1: Coord, pos2: Coord, pos_conf2: Coord,
            heading1: float, heading2: float,
            size1: Coord, size2: Coord
    ) -> float:

        heading1 = np.float64(heading1)
        heading2 = np.float64(heading2)

        dx1 = np.float64(size1.x + pos_conf1.x * 2)
        dy1 = np.float64(size1.y + pos_conf1.x * 2)
        dx2 = np.float64(size2.x + pos_conf2.x * 2)
        dy2 = np.float64(size2.y + pos_conf2.x * 2)

        heading1 = np.float64(int(heading1 / 0.01) * 0.01)
        heading2 = np.float64(int(heading2 / 0.01) * 0.01)

        distance = np.float64(math.hypot(
            pos1.x - pos2.x,
            pos1.y - pos2.y
        ))

        max_diagonal1 = np.sqrt(dx1 ** 2 + dy1 ** 2) / np.float64(2)
        max_diagonal2 = np.sqrt(dx2 ** 2 + dy2 ** 2) / np.float64(2)

        if distance > max_diagonal1 + max_diagonal2:
            return np.float64(0.0)

        try:
            int_area = MDMLib.ellipse_int_area(
                np.float64(pos1.x), np.float64(pos1.y),
                dx1, dy1, heading1,
                np.float64(pos2.x), np.float64(pos2.y),
                dx2, dy2, heading2
            )
        except Exception as e:
            print(f"Warning: Ellipse intersection calculation failed: {e}")
            return np.float64(0.0)

        area1 = np.pi * (dx1 / np.float64(2)) * (dy1 / np.float64(2))
        area2 = np.pi * (dx2 / np.float64(2)) * (dy2 / np.float64(2))

        # Prevent division by zero
        union_area = area1 + area2 - int_area
        if union_area <= 0:
            return np.float64(0.0)

        area_factor = int_area / union_area

        # Calculate Importance Factor
        distance = distance + np.float64(0.0001) if distance == 0 else distance

        # Calculate the angle between the centers
        centers_angle = MDMLib.calculate_heading_angle(
            Coord(
                x=np.float64(pos2.x - pos1.x),
                y=np.float64(pos2.y - pos1.y)
            )
        )

        # Convert radians mit float64
        c1 = np.deg2rad(centers_angle)
        h1 = np.deg2rad(heading1)
        h2 = np.deg2rad(heading2)

        # Calculate angle differences
        diff_angle1 = np.arctan2(np.sin(h1 - c1), np.cos(h1 - c1))
        diff_angle2 = np.arctan2(np.sin(h2 - c1), np.cos(h2 - c1))

        # Normalize angles
        if diff_angle1 > np.pi / 2:
            diff_angle1 -= np.pi
        if diff_angle1 < -np.pi / 2:
            diff_angle1 += np.pi
        if diff_angle2 > np.pi / 2:
            diff_angle2 -= np.pi
        if diff_angle2 < -np.pi / 2:
            diff_angle2 += np.pi

        # Calculate importance radii
        imp_r1 = (dx1 / np.float64(2)) * np.sin(diff_angle1) + \
                 (dy1 / np.float64(2)) * np.cos(diff_angle1)
        imp_r2 = (dx2 / np.float64(2)) * np.sin(diff_angle2) + \
                 (dy2 / np.float64(2)) * np.cos(diff_angle2)

        # Importance factor with float64
        imp_factor = MDMLib.importance_factor(
            np.float64(imp_r1),
            np.float64(imp_r2),
            distance
        )

        # Combine factors
        factor1 = imp_factor * area_factor
        factor2 = area_factor

        return np.float64(min(factor1, factor2))
