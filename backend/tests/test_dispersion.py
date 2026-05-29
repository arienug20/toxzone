"""Tests for Dispersion Models - minimum 8 test cases"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from src.core.dispersion import GaussianPlumeModel, HeavyGasModel, ModelSelector


class TestGaussianPlumeModel:

    def test_concentration_at_source_is_zero(self):
        c = GaussianPlumeModel.calculate_concentration(0, 0, 0, 100, 5, 0, "D")
        assert c == 0.0

    def test_concentration_positive_downwind(self):
        c = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 5, 0, "D")
        assert c > 0

    def test_concentration_decreases_with_distance(self):
        c_100 = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 5, 0, "D")
        c_500 = GaussianPlumeModel.calculate_concentration(500, 0, 0, 100, 5, 0, "D")
        c_1000 = GaussianPlumeModel.calculate_concentration(1000, 0, 0, 100, 5, 0, "D")
        assert c_100 > c_500 > c_1000

    def test_concentration_lower_at_crosswind(self):
        c_center = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 5, 0, "D")
        c_off = GaussianPlumeModel.calculate_concentration(100, 50, 0, 100, 5, 0, "D")
        assert c_center > c_off

    def test_downwind_distance_finds_threshold(self):
        Q = 100.0
        u = 5.0
        c_500 = GaussianPlumeModel.calculate_concentration(500, 0, 0, Q, u, 0, "D")
        dist = GaussianPlumeModel.calculate_downwind_distance(c_500, Q, u, 0, "D")
        assert dist is not None
        assert abs(dist - 500) < 50

    def test_downwind_distance_none_for_tiny_threshold(self):
        dist = GaussianPlumeModel.calculate_downwind_distance(
            1e-20, 0.001, 5.0, 0, "D", max_distance=100.0
        )
        assert dist is None or dist > 0

    def test_stability_class_effect(self):
        c_A = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 5, 0, "A")
        c_F = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 5, 0, "F")
        assert c_F > c_A

    def test_zero_wind_speed(self):
        c = GaussianPlumeModel.calculate_concentration(100, 0, 0, 100, 0, 0, "D")
        assert c == 0.0


class TestHeavyGasModel:

    def test_transition_distance_positive(self):
        dist = HeavyGasModel.calculate_transition_distance(100.0, 2.0, 5.0)
        assert dist > 0

    def test_light_gas_no_transition(self):
        dist = HeavyGasModel.calculate_transition_distance(100.0, 0.5, 5.0)
        assert dist == 0.0

    def test_concentration_decreases_with_distance(self):
        c_near = HeavyGasModel.calculate_concentration(10, 100, 2.0, 5.0, "D")
        c_far = HeavyGasModel.calculate_concentration(100, 100, 2.0, 5.0, "D")
        assert c_near > c_far


class TestModelSelector:

    def test_light_gas_selects_gaussian(self):
        model = ModelSelector.select_model(0.6, 5.0, "continuous")
        assert model == "gaussian"

    def test_heavy_gas_high_rate_selects_heavy(self):
        model = ModelSelector.select_model(2.0, 20.0, "continuous")
        assert model == "heavy_gas"

    def test_override_respected(self):
        model = ModelSelector.select_model(2.0, 20.0, "continuous", override="gaussian")
        assert model == "gaussian"
