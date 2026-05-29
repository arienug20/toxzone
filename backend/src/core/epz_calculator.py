"""EPZ (Emergency Planning Zone) calculator"""

import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np

from .dispersion import GaussianPlumeModel, HeavyGasModel, ModelSelector
from .source_terms import (
    LiquidDischarge, GasDischarge, TwoPhaseFlow,
    PoolEvaporation, HoleSizeCalculator, DischargeResult
)


@dataclass
class ZoneInfo:
    """Information about a single EPZ zone"""
    threshold_name: str
    threshold_value_ppm: Optional[float]
    threshold_value_mg_m3: Optional[float]
    downwind_distance_m: Optional[float]
    crosswind_width_m: Optional[float]
    area_km2: Optional[float]
    geojson_polygon: Optional[Dict[str, Any]]


@dataclass
class EPZResult:
    """Complete EPZ calculation result"""
    zones: Dict[str, ZoneInfo]
    model_used: str
    model_description: str
    computation_time_ms: float
    wind_direction_deg: float
    stability_class: str
    total_affected_area_km2: float
    concentration_grid: Optional[Dict[str, Any]] = None
    contour_geojson: Optional[Dict[str, Any]] = None
    warnings: List[str] = None


class EPZCalculator:
    """
    Emergency Planning Zone calculator.

    Computes EPZs based on chemical thresholds, release scenarios,
    and weather conditions using dispersion models.
    """

    # Threshold priority (from most severe to least)
    THRESHOLD_PRIORITY = [
        ('erpg_3', 'ERPG-3'),
        ('erpg_2', 'ERPG-2'),
        ('erpg_1', 'ERPG-1'),
        ('idlh', 'IDLH'),
        ('aegl_3_60min', 'AEGL-3 (60min)'),
        ('aegl_2_60min', 'AEGL-2 (60min)'),
        ('aegl_1_60min', 'AEGL-1 (60min)'),
    ]

    def __init__(
        self,
        chemical: Dict[str, Any],
        scenario: Dict[str, Any],
        weather: Dict[str, Any],
    ):
        """
        Initialize EPZ calculator.

        Args:
            chemical: Chemical properties dict
            scenario: Release scenario dict
            weather: Weather conditions dict
        """
        self.chemical = chemical
        self.scenario = scenario
        self.weather = weather

        # Extract key parameters
        self.molecular_weight = chemical.get('molecular_weight', 0)
        self.gas_density_ratio = chemical.get('gas_density_ratio', 1.0)
        self.is_heavier_than_air = chemical.get('is_heavier_than_air', False)

        # Weather parameters
        self.stability_class = weather.get('stability_class', 'D')
        self.wind_speed_ms = weather.get('wind_speed_ms', 5.0)
        self.wind_direction_deg = weather.get('wind_direction_deg', 0.0)
        self.temperature_c = weather.get('temperature_c', 25.0)
        self.humidity_percent = weather.get('humidity_percent', 50.0)
        self.surface_roughness_m = weather.get('surface_roughness_m', 0.03)

        # Scenario parameters
        self.scenario_type = scenario.get('scenario_type', 'continuous')
        self.release_height_m = scenario.get('release_height_m', 0.0)
        self.discharge_coeff = scenario.get('discharge_coefficient', 0.61)
        self.mitigation_factor = scenario.get('mitigation_factor', 1.0)

        # Grid parameters
        self.grid_resolution = scenario.get('grid_resolution_m', 5.0)

        # Select dispersion model
        self.model = ModelSelector.select_model(
            gas_density_ratio=self.gas_density_ratio,
            release_rate=self._get_release_rate(),
            release_type=self.scenario_type,
            override=scenario.get('model_override')
        )
        self.model_params = ModelSelector.get_model_parameters(self.model)

        # Thresholds from chemical
        self.thresholds = self._extract_thresholds()

        self.warnings: List[str] = []

    def _get_release_rate(self) -> float:
        """Get release rate (kg/s) from scenario"""
        return self.scenario.get('release_rate_kg_s', 0.0)

    def _extract_thresholds(self) -> Dict[str, Tuple[float, Optional[float]]]:
        """
        Extract available thresholds from chemical.

        Returns:
            Dict mapping threshold key to (ppm_value, mg_m3_value)
        """
        thresholds = {}

        # ERPG thresholds
        if self.chemical.get('erpg_3_ppm'):
            thresholds['erpg_3'] = (self.chemical['erpg_3_ppm'], self.chemical.get('erpg_3_mg_m3'))
        if self.chemical.get('erpg_2_ppm'):
            thresholds['erpg_2'] = (self.chemical['erpg_2_ppm'], self.chemical.get('erpg_2_mg_m3'))
        if self.chemical.get('erpg_1_ppm'):
            thresholds['erpg_1'] = (self.chemical['erpg_1_ppm'], self.chemical.get('erpg_1_mg_m3'))

        # IDLH
        if self.chemical.get('idlh_ppm'):
            thresholds['idlh'] = (self.chemical['idlh_ppm'], self.chemical.get('idlh_mg_m3'))

        # AEGL 60-minute thresholds
        if self.chemical.get('aegl_3_60min_ppm'):
            thresholds['aegl_3_60min'] = (self.chemical['aegl_3_60min_ppm'], None)
        if self.chemical.get('aegl_2_60min_ppm'):
            thresholds['aegl_2_60min'] = (self.chemical['aegl_2_60min_ppm'], None)
        if self.chemical.get('aegl_1_60min_ppm'):
            thresholds['aegl_1_60min'] = (self.chemical['aegl_1_60min_ppm'], None)

        return thresholds

    def _calculate_emission_rate(self) -> Tuple[float, str]:
        """
        Calculate effective emission rate based on scenario type.

        Returns:
            Tuple of (rate_g_s, notes)
        """
        scenario_type = self.scenario_type
        notes = ""

        if scenario_type == 'continuous':
            rate_kg_s = self.scenario.get('release_rate_kg_s', 0.0)
            rate_g_s = rate_kg_s * 1000.0
            notes = f"Continuous release at {rate_kg_s:.2f} kg/s"

        elif scenario_type == 'instantaneous':
            total_kg = self.scenario.get('total_release_kg', 0.0)
            duration_s = self.scenario.get('duration_s', 600.0)  # Default 10 min
            rate_kg_s = total_kg / duration_s if duration_s > 0 else 0.0
            rate_g_s = rate_kg_s * 1000.0
            notes = f"Instantaneous release: {total_kg:.1f} kg over {duration_s:.0f}s"

        elif scenario_type == 'pool_evaporation':
            volume_m3 = self.scenario.get('total_release_kg', 0.0) / self.chemical.get('liquid_density_kg_m3', 1000.0)
            vapor_pressure_pa = self.chemical.get('vapor_pressure_kpa', 0.0) * 1000.0

            result = PoolEvaporation.calculate_pool_evaporation(
                volume_m3=volume_m3,
                vapor_pressure_pa=vapor_pressure_pa,
                molecular_weight_g_mol=self.molecular_weight,
                liquid_density_kg_m3=self.chemical.get('liquid_density_kg_m3', 1000.0),
                wind_speed_ms=self.wind_speed_ms,
                bund_area_m2=self.scenario.get('bund_area_m2'),
                substrate='concrete',
            )
            rate_g_s = result.rate_kg_s * 1000.0
            notes = result.notes or f"Pool evaporation: {result.rate_kg_s:.3f} kg/s"

        elif scenario_type == 'catastrophic':
            # Full tank rupture - instantaneous release of entire inventory
            total_kg = self.scenario.get('total_release_kg', 0.0)
            duration_s = 60.0  # Assume 1 minute for catastrophic event
            rate_kg_s = total_kg / duration_s
            rate_g_s = rate_kg_s * 1000.0
            notes = f"Catastrophic failure: {total_kg:.1f} kg released in {duration_s}s"

        else:
            rate_g_s = 0.0
            notes = f"Unknown scenario type: {scenario_type}"
            self.warnings.append(notes)

        # Apply mitigation factor
        rate_g_s *= self.mitigation_factor
        if self.mitigation_factor != 1.0:
            notes += f" (mitigation factor: {self.mitigation_factor})"

        return rate_g_s, notes

    def _ppm_to_g_m3(self, ppm: float) -> float:
        """Convert ppm to g/m³ at standard conditions"""
        if self.molecular_weight <= 0:
            return 0.0

        # At 25°C and 1 atm: 1 ppm = (MW / 24.45) mg/m³
        mg_m3 = ppm * self.molecular_weight / 24.45
        return mg_m3 / 1000.0  # Convert to g/m³

    def _calculate_zone(
        self,
        threshold_name: str,
        threshold_ppm: float,
        emission_rate_g_s: float,
    ) -> ZoneInfo:
        """Calculate single zone for given threshold"""
        threshold_g_m3 = self._ppm_to_g_m3(threshold_ppm)

        if self.model == 'gaussian':
            distance_m = GaussianPlumeModel.calculate_downwind_distance(
                threshold=threshold_g_m3,
                Q=emission_rate_g_s,
                u=self.wind_speed_ms,
                H=self.release_height_m,
                stability=self.stability_class,
                max_distance=20000.0,
            )
        else:  # heavy_gas
            # Estimate volume for heavy gas model
            total_kg = self.scenario.get('total_release_kg', emission_rate_g_s * 600.0 / 1000.0)
            density_kg_m3 = self.chemical.get('gas_density_kg_m3', 1.2)
            volume_m3 = total_kg / density_kg_m3 if density_kg_m3 > 0 else 1.0

            # Convert threshold to dimensionless for heavy gas model
            # This is a simplification - proper conversion would require
            # more complex gas dynamics
            threshold_normalized = threshold_ppm / 1e6

            distance_m = HeavyGasModel.calculate_downwind_distance(
                threshold=threshold_normalized,
                volume=volume_m3,
                density_ratio=self.gas_density_ratio,
                wind_speed=self.wind_speed_ms,
                stability=self.stability_class,
                max_distance=10000.0,
            )

        # Calculate crosswind width (assuming Gaussian distribution)
        if distance_m and distance_m > 0:
            sigma_y = GaussianPlumeModel._calculate_sigma_y(distance_m, self.stability_class)
            # Width at threshold is approximately 2.355 * sigma_y (95% of mass)
            width_m = 2.355 * sigma_y * 2

            # Area (simplified as ellipse)
            area_m2 = math.pi * (distance_m / 2) * (width_m / 2)
            area_km2 = area_m2 / 1e6
        else:
            width_m = None
            area_km2 = None

        # Generate simplified GeoJSON polygon
        geojson = None
        if distance_m and distance_m > 0 and width_m:
            geojson = self._generate_zone_geojson(distance_m, width_m, self.wind_direction_deg)

        return ZoneInfo(
            threshold_name=threshold_name,
            threshold_value_ppm=threshold_ppm,
            threshold_value_mg_m3=threshold_ppm * self.molecular_weight / 24.45,
            downwind_distance_m=distance_m,
            crosswind_width_m=width_m,
            area_km2=area_km2,
            geojson_polygon=geojson,
        )

    def _generate_zone_geojson(
        self,
        downwind_m: float,
        crosswind_m: float,
        wind_direction_deg: float,
    ) -> Dict[str, Any]:
        """Generate simplified GeoJSON polygon for zone"""
        # Create ellipse points
        num_points = 32
        points = []

        # Ellipse parameters (semi-major and semi-minor axes)
        a = downwind_m / 2  # Semi-major (downwind)
        b = crosswind_m / 2  # Semi-minor (crosswind)

        # Rotation angle (wind direction from north)
        # Note: wind direction is direction wind is blowing TO
        # So source is at wind_direction + 180 degrees
        wind_rad = math.radians(wind_direction_deg + 180)

        for i in range(num_points):
            theta = 2 * math.pi * i / num_points

            # Ellipse in local coordinates (x=downwind, y=crosswind)
            x_local = a * math.cos(theta)
            y_local = b * math.sin(theta)

            # Rotate and translate (source at origin)
            x_rot = x_local * math.cos(wind_rad) - y_local * math.sin(wind_rad)
            y_rot = x_local * math.sin(wind_rad) + y_local * math.cos(wind_rad)

            # Convert to lat/lon (approximate: 1 degree lat ~ 111km)
            lat_offset = y_rot / 111000.0
            lon_offset = x_rot / (111000.0 * math.cos(math.radians(0.0)))  # Assume equator for simplicity

            points.append([lon_offset, lat_offset])

        # Close polygon
        points.append(points[0])

        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [points]
            },
            "properties": {
                "downwind_distance_m": downwind_m,
                "crosswind_width_m": crosswind_m,
                "wind_direction_deg": wind_direction_deg,
            }
        }

    def calculate_all_zones(self) -> EPZResult:
        """
        Calculate all EPZ zones.

        Returns:
            EPZResult with all zones
        """
        start_time = time.time()

        # Calculate emission rate
        emission_rate_g_s, emission_notes = self._calculate_emission_rate()

        if emission_rate_g_s <= 0:
            self.warnings.append("Emission rate is zero or negative")

        # Calculate each zone
        zones = {}
        total_area_km2 = 0.0

        for threshold_key, threshold_name in self.THRESHOLD_PRIORITY:
            if threshold_key in self.thresholds:
                threshold_ppm, _ = self.thresholds[threshold_key]

                zone = self._calculate_zone(threshold_key, threshold_ppm, emission_rate_g_s)
                zones[threshold_key] = zone

                if zone.area_km2:
                    total_area_km2 = max(total_area_km2, zone.area_km2)

        # Compute concentration grid
        grid_data = None
        if emission_rate_g_s > 0:
            max_distance = max(
                [z.downwind_distance_m for z in zones.values() if z.downwind_distance_m],
                default=1000.0
            )
            grid_extent = (-200, max_distance + 200, -500, 500)

            if self.model == 'gaussian':
                concentration_grid, metadata = GaussianPlumeModel.compute_concentration_grid(
                    Q=emission_rate_g_s,
                    u=self.wind_speed_ms,
                    H=self.release_height_m,
                    stability=self.stability_class,
                    grid_extent=grid_extent,
                    resolution=self.grid_resolution,
                    wind_direction_deg=self.wind_direction_deg,
                )

                grid_data = {
                    'grid': concentration_grid.tolist(),
                    'metadata': metadata,
                }

        # Generate contour GeoJSON
        contour_geojson = self._generate_contour_geojson(zones)

        computation_time = (time.time() - start_time) * 1000.0

        return EPZResult(
            zones=zones,
            model_used=self.model,
            model_description=self.model_params['description'],
            computation_time_ms=computation_time,
            wind_direction_deg=self.wind_direction_deg,
            stability_class=self.stability_class,
            total_affected_area_km2=total_area_km2,
            concentration_grid=grid_data,
            contour_geojson=contour_geojson,
            warnings=self.warnings if self.warnings else None,
        )

    def _generate_contour_geojson(self, zones: Dict[str, ZoneInfo]) -> Dict[str, Any]:
        """Generate GeoJSON FeatureCollection with all zone contours"""
        features = []

        for zone_key, zone in zones.items():
            if zone.geojson_polygon:
                feature = zone.geojson_polygon
                feature['properties']['zone'] = zone_key
                feature['properties']['name'] = zone.threshold_name
                feature['properties']['threshold_ppm'] = zone.threshold_value_ppm
                features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    def compute_wind_rose(self, step_deg: int = 15) -> Dict[str, Any]:
        """
        Compute EPZ for multiple wind directions (wind rose analysis).

        Args:
            step_deg: Angle step for wind direction sweep (degrees)

        Returns:
            Dict with results for each wind direction
        """
        results = {}

        original_wind_dir = self.wind_direction_deg

        for direction in range(0, 360, step_deg):
            self.wind_direction_deg = float(direction)

            result = self.calculate_all_zones()
            results[str(direction)] = {
                'zones': {
                    k: {
                        'downwind_distance_m': v.downwind_distance_m,
                        'area_km2': v.area_km2,
                    }
                    for k, v in result.zones.items()
                },
                'total_area_km2': result.total_affected_area_km2,
            }

        # Restore original wind direction
        self.wind_direction_deg = original_wind_dir

        return results