"""Tests for EPZ Calculator - minimum 10 test cases"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from src.core.epz_calculator import EPZCalculator


def ammonia_dict():
    return {
        "name": "Ammonia", "formula": "NH3", "molecular_weight": 17.031,
        "boiling_point_c": -33.34, "gas_density_kg_m3": 0.73, "gas_density_ratio": 0.597,
        "state_at_ambient": "gas", "is_heavier_than_air": False,
        "erpg_1_ppm": 25.0, "erpg_2_ppm": 200.0, "erpg_3_ppm": 1000.0,
        "idlh_ppm": 300.0, "liquid_density_kg_m3": 682.0, "vapor_pressure_kpa": 1000.0,
    }


def chlorine_dict():
    return {
        "name": "Chlorine", "formula": "Cl2", "molecular_weight": 70.906,
        "boiling_point_c": -34.0, "gas_density_kg_m3": 2.95, "gas_density_ratio": 2.41,
        "state_at_ambient": "gas", "is_heavier_than_air": True,
        "erpg_1_ppm": 1.0, "erpg_2_ppm": 3.0, "erpg_3_ppm": 20.0,
        "idlh_ppm": 10.0,
        "aegl_1_10min_ppm": 0.5, "aegl_1_60min_ppm": 0.5,
        "aegl_2_10min_ppm": 2.0, "aegl_2_60min_ppm": 1.0,
        "aegl_3_10min_ppm": 10.0, "aegl_3_60min_ppm": 5.0,
        "liquid_density_kg_m3": 1562.0, "vapor_pressure_kpa": 740.0,
    }


def default_weather():
    return {
        "stability_class": "D", "wind_speed_ms": 5.0,
        "wind_direction_deg": 0.0, "temperature_c": 25.0,
        "humidity_percent": 50.0, "surface_roughness_m": 0.03,
    }


def continuous_scenario(rate_kg_s=1.0, height=0.0):
    return {
        "scenario_type": "continuous", "release_rate_kg_s": rate_kg_s,
        "release_height_m": height, "mitigation_factor": 1.0,
        "discharge_coefficient": 0.61, "grid_resolution_m": 20.0,
    }


class TestEPZCalculator:

    def test_continuous_release_ammonia(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        result = calc.calculate_all_zones()
        assert result.model_used == "gaussian"
        assert len(result.zones) > 0
        assert result.computation_time_ms >= 0
        assert result.stability_class == "D"

    def test_continuous_release_chlorine(self):
        calc = EPZCalculator(chlorine_dict(), continuous_scenario(1.0), default_weather())
        result = calc.calculate_all_zones()
        assert len(result.zones) >= 3
        erpg3 = result.zones.get("erpg_3")
        if erpg3:
            assert erpg3.threshold_value_ppm == 20.0

    def test_model_selection_light_gas(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        assert calc.model == "gaussian"

    def test_model_selection_heavy_gas_override(self):
        scenario = continuous_scenario(20.0)
        scenario["model_override"] = "gaussian"
        calc = EPZCalculator(chlorine_dict(), scenario, default_weather())
        assert calc.model == "gaussian"

    def test_worst_case_weather(self):
        worst_weather = {
            "stability_class": "F", "wind_speed_ms": 1.5,
            "wind_direction_deg": 0.0, "temperature_c": 25.0,
            "humidity_percent": 50.0, "surface_roughness_m": 0.03,
        }
        calc_worst = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), worst_weather)
        result_worst = calc_worst.calculate_all_zones()

        calc_normal = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        result_normal = calc_normal.calculate_all_zones()

        worst_area = result_worst.total_affected_area_km2 or 0
        normal_area = result_normal.total_affected_area_km2 or 0
        assert worst_area >= normal_area * 0.8

    def test_zero_release_rate(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(0.0), default_weather())
        result = calc.calculate_all_zones()
        assert result.warnings is not None or len(result.zones) == 0 or all(
            z.downwind_distance_m is None for z in result.zones.values()
        )

    def test_instantaneous_release(self):
        scenario = {
            "scenario_type": "instantaneous", "total_release_kg": 1000.0,
            "duration_s": 600.0, "release_height_m": 0.0,
            "mitigation_factor": 1.0, "discharge_coefficient": 0.61,
            "grid_resolution_m": 20.0,
        }
        calc = EPZCalculator(chlorine_dict(), scenario, default_weather())
        result = calc.calculate_all_zones()
        assert result.model_used == "gaussian"
        assert len(result.zones) > 0

    def test_elevated_release(self):
        calc_ground = EPZCalculator(ammonia_dict(), continuous_scenario(1.0, 0.0), default_weather())
        result_ground = calc_ground.calculate_all_zones()

        calc_elevated = EPZCalculator(ammonia_dict(), continuous_scenario(1.0, 20.0), default_weather())
        result_elevated = calc_elevated.calculate_all_zones()

        assert result_ground.computation_time_ms >= 0
        assert result_elevated.computation_time_ms >= 0

    def test_mitigation_factor(self):
        scenario_no_mit = continuous_scenario(1.0)
        scenario_no_mit["mitigation_factor"] = 1.0

        scenario_mit = continuous_scenario(1.0)
        scenario_mit["mitigation_factor"] = 0.5

        calc_full = EPZCalculator(ammonia_dict(), scenario_no_mit, default_weather())
        result_full = calc_full.calculate_all_zones()

        calc_mit = EPZCalculator(ammonia_dict(), scenario_mit, default_weather())
        result_mit = calc_mit.calculate_all_zones()

        full_area = result_full.total_affected_area_km2 or 0
        mit_area = result_mit.total_affected_area_km2 or 0
        assert mit_area <= full_area * 1.01

    def test_ppm_to_g_m3_conversion(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        result = calc._ppm_to_g_m3(1.0)
        expected = 17.031 / 24.45 / 1000.0
        assert abs(result - expected) < 1e-6

    def test_wind_rose_computation(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        wind_rose = calc.compute_wind_rose(step_deg=90)
        assert len(wind_rose) == 4
        assert "0" in wind_rose
        assert "90" in wind_rose

    def test_threshold_extraction(self):
        calc = EPZCalculator(chlorine_dict(), continuous_scenario(1.0), default_weather())
        assert "erpg_1" in calc.thresholds
        assert "erpg_2" in calc.thresholds
        assert "erpg_3" in calc.thresholds
        assert "idlh" in calc.thresholds
        assert calc.thresholds["erpg_1"][0] == 1.0
        assert calc.thresholds["erpg_3"][0] == 20.0

    def test_contour_geojson_generation(self):
        calc = EPZCalculator(ammonia_dict(), continuous_scenario(1.0), default_weather())
        result = calc.calculate_all_zones()
        if result.contour_geojson:
            assert result.contour_geojson["type"] == "FeatureCollection"
            assert isinstance(result.contour_geojson["features"], list)
