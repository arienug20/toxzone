"""Population impact estimator"""

import math
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class PopulationResult:
    """Population estimation result"""
    total_affected: int
    by_zone: Dict[str, int]
    density_per_km2: float


class PopulationEstimator:
    """Estimate population affected by EPZ zones"""

    def __init__(self, default_density: float = 1000.0):
        """
        Args:
            default_density: Default population density (people/km²)
        """
        self.default_density = default_density

    def estimate_from_area(self, area_km2: float, density: Optional[float] = None) -> int:
        """Estimate population from area and density"""
        d = density or self.default_density
        return max(1, int(area_km2 * d))

    def estimate_from_zones(self, zones: Dict[str, Optional[float]]) -> Dict[str, Any]:
        """
        Estimate population for multiple zones.

        Args:
            zones: Dict mapping zone name to area_km2 (or None)

        Returns:
            Dict with total and per-zone estimates
        """
        by_zone = {}
        total = 0

        # Sort zones by severity (ERPG-3 first, then ERPG-2, then ERPG-1)
        severity_order = ['erpg_3', 'idlh', 'erpg_2', 'erpg_1',
                          'aegl_3_60min', 'aegl_2_60min', 'aegl_1_60min']
        sorted_zones = sorted(
            [(k, v) for k, v in zones.items() if v is not None],
            key=lambda x: severity_order.index(x[0]) if x[0] in severity_order else 99
        )

        cumulative_area = 0.0
        for zone_name, area_km2 in sorted_zones:
            if area_km2 and area_km2 > 0:
                # Subtract inner zones to avoid double-counting
                marginal_area = max(0, area_km2 - cumulative_area)
                pop = self.estimate_from_area(marginal_area)
                by_zone[zone_name] = pop
                total += pop
                cumulative_area = area_km2

        return {
            "total_affected": total,
            "by_zone": by_zone,
            "density_per_km2": self.default_density,
        }

    def time_of_day_factor(self, hour: int, land_use: str = "industrial") -> float:
        """
        Adjustment factor for time of day.

        Args:
            hour: Hour of day (0-23)
            land_use: Land use type

        Returns:
            Multiplier for population density
        """
        if land_use == "residential":
            # Higher at night, lower during day
            if 8 <= hour <= 17:
                return 0.4  # People at work/school
            else:
                return 1.2  # People at home
        elif land_use == "commercial":
            if 8 <= hour <= 20:
                return 1.3
            else:
                return 0.2
        elif land_use == "industrial":
            if 7 <= hour <= 17:
                return 1.0
            else:
                return 0.3
        else:  # rural
            return 1.0

    def estimate_evacuation_time(
        self,
        population: int,
        max_distance_m: float,
        road_density: str = "normal",
    ) -> float:
        """
        Estimate evacuation time in minutes.

        Args:
            population: Number of people to evacuate
            max_distance_m: Maximum evacuation distance (m)
            road_density: Road density category (sparse, normal, dense)

        Returns:
            Estimated evacuation time (minutes)
        """
        # Mobilization time (minutes)
        mobilization = 15.0

        # Travel time
        # Average evacuation speed depends on congestion
        base_speed_ms = 8.0  # ~30 km/h base speed

        # Congestion factor based on population and road density
        congestion = {
            'sparse': 3.0,
            'normal': 2.0,
            'dense': 1.5,
        }.get(road_density, 2.0)

        # More people = more congestion
        pop_factor = 1.0 + (population / 10000) * 0.5

        effective_speed = base_speed_ms / (congestion * pop_factor)
        travel_time_min = (max_distance_m / effective_speed) / 60.0

        return mobilization + travel_time_min
