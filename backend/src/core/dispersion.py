"""Core dispersion models for toxic gas release calculations"""

import math
from typing import Tuple, Optional, List
import numpy as np
from dataclasses import dataclass


@dataclass
class DispersionCoefficients:
    """Pasquill-Gifford dispersion coefficients"""
    sigma_y: float  # Crosswind dispersion coefficient (m)
    sigma_z: float  # Vertical dispersion coefficient (m)


class GaussianPlumeModel:
    """
    Pasquill-Gifford Gaussian Plume Model for atmospheric dispersion.

    Formula:
    C(x,y,z) = Q / (π * u * σy * σz) *
               exp(-y² / (2*σy²)) *
               [exp(-(z-H)² / (2*σz²)) + exp(-(z+H)² / (2*σz²))]

    Where:
    - C = concentration (g/m³ or ppm)
    - Q = emission rate (g/s)
    - u = wind speed (m/s)
    - σy, σz = dispersion coefficients (m)
    - H = effective release height (m)
    - x, y, z = receptor coordinates (m)
    """

    # Pasquill-Gifford σ coefficients (Briggs formulas for open country)
    SIGMA_COEFFS = {
        # Format: (a, b, c, d) for σ = a*x^b for x < c, σ = a*x^b for x >= c
        # σy coefficients
        'A': {'a': 0.22, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
        'B': {'a': 0.16, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
        'C': {'a': 0.11, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
        'D': {'a': 0.08, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
        'E': {'a': 0.06, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
        'F': {'a': 0.04, 'b': 0.0001, 'c': 0.0, 'd': 0.0},
    }

    # Simplified Pasquill-Gifford curves (Turner, 1970)
    SIGMA_Y_PARAMS = {
        'A': {'a': 0.443, 'b': 0.947},
        'B': {'a': 0.283, 'b': 0.896},
        'C': {'a': 0.200, 'b': 0.882},
        'D': {'a': 0.141, 'b': 0.876},
        'E': {'a': 0.105, 'b': 0.803},
        'F': {'a': 0.071, 'b': 0.798},
    }

    SIGMA_Z_PARAMS = {
        'A': {'a': 0.127, 'b': 0.944},
        'B': {'a': 0.110, 'b': 0.920},
        'C': {'a': 0.092, 'b': 0.853},
        'D': {'a': 0.075, 'b': 0.803},
        'E': {'a': 0.061, 'b': 0.702},
        'F': {'a': 0.048, 'b': 0.645},
    }

    @classmethod
    def _calculate_sigma_y(cls, x: float, stability: str) -> float:
        """Calculate crosswind dispersion coefficient σy"""
        params = cls.SIGMA_Y_PARAMS.get(stability, cls.SIGMA_Y_PARAMS['D'])
        return params['a'] * (x ** params['b'])

    @classmethod
    def _calculate_sigma_z(cls, x: float, stability: str) -> float:
        """Calculate vertical dispersion coefficient σz"""
        params = cls.SIGMA_Z_PARAMS.get(stability, cls.SIGMA_Z_PARAMS['D'])
        return params['a'] * (x ** params['b'])

    @classmethod
    def calculate_concentration(
        cls,
        x: float,
        y: float,
        z: float,
        Q: float,
        u: float,
        H: float,
        stability: str,
    ) -> float:
        """
        Calculate concentration at receptor point.

        Args:
            x: Downwind distance (m)
            y: Crosswind distance (m)
            z: Height above ground (m)
            Q: Emission rate (g/s)
            u: Wind speed at release height (m/s)
            H: Effective release height (m)
            stability: Pasquill-Gifford stability class (A-F)

        Returns:
            Concentration (g/m³)
        """
        if x <= 0:
            return 0.0
        if u <= 0:
            return 0.0

        sigma_y = cls._calculate_sigma_y(x, stability)
        sigma_z = cls._calculate_sigma_z(x, stability)

        # Gaussian plume equation with ground reflection
        term1 = Q / (2 * math.pi * u * sigma_y * sigma_z)

        # Crosswind term
        term2 = math.exp(-(y ** 2) / (2 * sigma_y ** 2))

        # Vertical term with ground reflection
        term3 = math.exp(-((z - H) ** 2) / (2 * sigma_z ** 2)) + \
                math.exp(-((z + H) ** 2) / (2 * sigma_z ** 2))

        return term1 * term2 * term3

    @classmethod
    def calculate_downwind_distance(
        cls,
        threshold: float,
        Q: float,
        u: float,
        H: float,
        stability: str,
        max_distance: float = 10000.0,
        tolerance: float = 1.0,
    ) -> Optional[float]:
        """
        Calculate downwind distance to threshold concentration (centerline).

        Uses bisection method to find x where C(x, 0, 0) = threshold.

        Args:
            threshold: Target concentration (g/m³)
            Q: Emission rate (g/s)
            u: Wind speed (m/s)
            H: Release height (m)
            stability: Stability class (A-F)
            max_distance: Maximum search distance (m)
            tolerance: Solution tolerance (m)

        Returns:
            Downwind distance to threshold (m), or None if not found
        """
        if threshold <= 0:
            return None

        # Check concentration at max_distance
        c_max = cls.calculate_concentration(max_distance, 0, 0, Q, u, H, stability)
        if c_max > threshold:
            return None  # Threshold not reached within max_distance

        # Bisection search
        low = 0.0
        high = max_distance

        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            c_mid = cls.calculate_concentration(mid, 0, 0, Q, u, H, stability)

            if abs(c_mid - threshold) < threshold * 0.01:  # 1% tolerance
                return mid

            if c_mid > threshold:
                low = mid
            else:
                high = mid

            if high - low < tolerance:
                return (low + high) / 2

        return None

    @classmethod
    def compute_concentration_grid(
        cls,
        Q: float,
        u: float,
        H: float,
        stability: str,
        grid_extent: Tuple[float, float, float, float],
        resolution: float = 5.0,
        wind_direction_deg: float = 0.0,
    ) -> Tuple[np.ndarray, dict]:
        """
        Compute 2D concentration grid.

        Args:
            Q: Emission rate (g/s)
            u: Wind speed (m/s)
            H: Release height (m)
            stability: Stability class (A-F)
            grid_extent: (x_min, x_max, y_min, y_max) in meters
            resolution: Grid spacing (m)
            wind_direction_deg: Wind direction (degrees from north, clockwise)

        Returns:
            Tuple of (concentration_grid, metadata)
        """
        x_min, x_max, y_min, y_max = grid_extent

        # Create coordinate arrays
        x_coords = np.arange(x_min, x_max + resolution, resolution)
        y_coords = np.arange(y_min, y_max + resolution, resolution)
        X, Y = np.meshgrid(x_coords, y_coords)

        # Rotate coordinates to align with wind direction
        wind_rad = math.radians(wind_direction_deg)
        X_rot = X * math.sin(wind_rad) + Y * math.cos(wind_rad)
        Y_rot = X * math.cos(wind_rad) - Y * math.sin(wind_rad)

        # Initialize concentration grid (ground level z=0)
        C = np.zeros_like(X)

        # Calculate concentration at each point (vectorized where possible)
        # Note: Full vectorization would require rewriting concentration calc
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                x = X_rot[i, j]
                y = Y_rot[i, j]
                if x > 0:  # Only downwind
                    C[i, j] = cls.calculate_concentration(x, y, 0, Q, u, H, stability)

        metadata = {
            'grid_extent': grid_extent,
            'resolution': resolution,
            'x_coords': x_coords.tolist(),
            'y_coords': y_coords.tolist(),
            'wind_direction_deg': wind_direction_deg,
            'source_location': (0, 0),
        }

        return C, metadata


class HeavyGasModel:
    """
    Simplified heavy gas dispersion model (Britter-McQuaid).

    For gases denser than air (gas_density_ratio > 1.15), gravity-driven
    spreading dominates near the source until passive dispersion takes over.
    """

    @classmethod
    def calculate_transition_distance(
        cls,
        volume: float,
        density_ratio: float,
        wind_speed: float,
    ) -> float:
        """
        Calculate distance where passive dispersion begins to dominate.

        Simplified criterion based on densimetric Froude number.

        Args:
            volume: Release volume (m³)
            density_ratio: Gas density / air density
            wind_speed: Wind speed (m/s)

        Returns:
            Transition distance (m)
        """
        if density_ratio <= 1.0:
            return 0.0

        # Simplified Britter-McQuaid criterion
        # When Fr > 2, passive dispersion dominates
        g = 9.81  # m/s²

        # Characteristic length scale
        L = (volume / math.pi) ** (1/3)

        # Densimetric Froude number at distance x: Fr = u / sqrt(g * (ρg/ρa - 1) * h)
        # Transition when Fr ~ 1-2

        # Approximate transition distance
        delta_rho_ratio = density_ratio - 1.0
        if delta_rho_ratio <= 0.01:
            return 0.0

        x_transition = 10 * L * (delta_rho_ratio) ** (-0.5)

        return min(x_transition, 1000.0)  # Cap at 1km for safety

    @classmethod
    def calculate_concentration(
        cls,
        distance: float,
        volume: float,
        density_ratio: float,
        wind_speed: float,
        stability: str = 'D',
    ) -> float:
        """
        Calculate concentration using simplified heavy gas model.

        Near source: gravity spreading with 1/r decay
        Far source: transitions to Gaussian dispersion

        Args:
            distance: Distance from source (m)
            volume: Initial release volume (m³)
            density_ratio: Gas density / air density
            wind_speed: Wind speed (m/s)
            stability: Stability class for passive phase

        Returns:
            Concentration (dimensionless, relative to initial)
        """
        if density_ratio <= 1.0 or distance <= 0:
            # Light gas - use Gaussian instead
            return 0.0

        x_transition = cls.calculate_transition_distance(volume, density_ratio, wind_speed)

        if distance < x_transition:
            # Gravity-driven phase
            # Concentration decays as 1/r² in near field
            L = (volume / math.pi) ** (1/3)
            C = 1.0 / (1.0 + (distance / L) ** 2)
        else:
            # Transition to passive dispersion
            # Use Gaussian with effective source
            sigma_y = GaussianPlumeModel._calculate_sigma_y(distance, stability)
            C = 1.0 / (sigma_y * distance * wind_speed)

        return max(C, 0.0)

    @classmethod
    def calculate_downwind_distance(
        cls,
        threshold: float,
        volume: float,
        density_ratio: float,
        wind_speed: float,
        stability: str = 'D',
        max_distance: float = 5000.0,
    ) -> Optional[float]:
        """
        Calculate downwind distance to threshold.

        Args:
            threshold: Target concentration (dimensionless)
            volume: Release volume (m³)
            density_ratio: Gas density / air density
            wind_speed: Wind speed (m/s)
            stability: Stability class
            max_distance: Maximum search distance (m)

        Returns:
            Downwind distance (m), or None if not found
        """
        if threshold <= 0:
            return None

        # Bisection search
        low = 0.0
        high = max_distance

        for _ in range(100):
            mid = (low + high) / 2
            c_mid = cls.calculate_concentration(mid, volume, density_ratio, wind_speed, stability)

            if abs(c_mid - threshold) < threshold * 0.01:
                return mid

            if c_mid > threshold:
                low = mid
            else:
                high = mid

            if high - low < 1.0:
                return (low + high) / 2

        return None


class ModelSelector:
    """Select appropriate dispersion model based on release characteristics"""

    @staticmethod
    def select_model(
        gas_density_ratio: float,
        release_rate: float,
        release_type: str,
        override: Optional[str] = None,
    ) -> str:
        """
        Select dispersion model.

        Args:
            gas_density_ratio: Gas density / air density
            release_rate: Release rate (kg/s)
            release_type: Release type (continuous, instantaneous, etc.)
            override: User-specified model override

        Returns:
            Model name ('gaussian' or 'heavy_gas')
        """
        if override:
            return override

        # Heavy gas criteria
        is_heavy = gas_density_ratio > 1.15
        is_high_rate = release_rate > 10.0  # kg/s threshold

        if is_heavy and is_high_rate:
            return 'heavy_gas'

        return 'gaussian'

    @staticmethod
    def get_model_parameters(model: str) -> dict:
        """Get parameters for selected model"""
        params = {
            'gaussian': {
                'name': 'Gaussian Plume Model',
                'description': 'Pasquill-Gifford atmospheric dispersion',
                'applicability': 'Most gases, neutral and unstable conditions',
            },
            'heavy_gas': {
                'name': 'Heavy Gas Model',
                'description': 'Britter-McQuaid gravity-driven dispersion',
                'applicability': 'Gases denser than air, high release rates',
            },
        }
        return params.get(model, params['gaussian'])