"""Source term models for calculating release rates from various failure scenarios"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class DischargeResult:
    """Result from discharge calculation"""
    rate_kg_s: float
    duration_s: Optional[float] = None
    total_mass_kg: Optional[float] = None
    notes: Optional[str] = None


class LiquidDischarge:
    """
    Liquid discharge through hole using Bernoulli equation.

    Q = Cd * A * sqrt(2 * rho * delta_P)
    """

    @staticmethod
    def calculate_rate(
        hole_area_m2: float,
        liquid_density_kg_m3: float,
        pressure_diff_pa: float,
        discharge_coeff: float = 0.61,
    ) -> float:
        """
        Calculate liquid discharge rate.

        Args:
            hole_area_m2: Area of hole (m²)
            liquid_density_kg_m3: Liquid density (kg/m³)
            pressure_diff_pa: Pressure difference (Pa) = rho * g * head
            discharge_coeff: Discharge coefficient (typically 0.6-0.64)

        Returns:
            Discharge rate (kg/s)
        """
        if pressure_diff_pa <= 0 or hole_area_m2 <= 0:
            return 0.0

        rate = discharge_coeff * hole_area_m2 * math.sqrt(2 * liquid_density_kg_m3 * pressure_diff_pa)
        return rate

    @staticmethod
    def calculate_from_tank_level(
        hole_diameter_m: float,
        liquid_density_kg_m3: float,
        liquid_head_m: float,
        discharge_coeff: float = 0.61,
        atmospheric_pressure_pa: float = 101325.0,
    ) -> DischargeResult:
        """
        Calculate discharge from tank with given liquid level.

        Args:
            hole_diameter_m: Diameter of hole (m)
            liquid_density_kg_m3: Liquid density (kg/m³)
            liquid_head_m: Height of liquid above hole (m)
            discharge_coeff: Discharge coefficient
            atmospheric_pressure_pa: Atmospheric pressure (Pa)

        Returns:
            DischargeResult with rate
        """
        g = 9.81  # m/s²
        hole_area = math.pi * (hole_diameter_m / 2) ** 2
        pressure_diff = liquid_density_kg_m3 * g * liquid_head_m

        rate = LiquidDischarge.calculate_rate(
            hole_area, liquid_density_kg_m3, pressure_diff, discharge_coeff
        )

        return DischargeResult(rate_kg_s=rate)


class GasDischarge:
    """
    Gas discharge through hole (choked and subsonic flow).

    Handles both choked (critical) and subsonic flow regimes.
    """

    @staticmethod
    def calculate_rate(
        hole_area_m2: float,
        gas_density_kg_m3: float,
        upstream_pressure_pa: float,
        downstream_pressure_pa: float,
        gamma: float = 1.4,
        discharge_coeff: float = 0.85,
    ) -> DischargeResult:
        """
        Calculate gas discharge rate.

        Args:
            hole_area_m2: Area of hole (m²)
            gas_density_kg_m3: Gas density at upstream conditions (kg/m³)
            upstream_pressure_pa: Upstream pressure (Pa)
            downstream_pressure_pa: Downstream/back pressure (Pa)
            gamma: Heat capacity ratio (Cp/Cv)
            discharge_coeff: Discharge coefficient

        Returns:
            DischargeResult with rate
        """
        if upstream_pressure_pa <= downstream_pressure_pa or hole_area_m2 <= 0:
            return DischargeResult(rate_kg_s=0.0)

        # Pressure ratio
        pressure_ratio = downstream_pressure_pa / upstream_pressure_pa

        # Critical pressure ratio for choked flow
        critical_ratio = (2 / (gamma + 1)) ** (gamma / (gamma - 1))

        gas_constant = 287.0  # J/(kg·K) for air, approximate for other gases
        temperature_k = 298.0  # Assume 25°C

        # Calculate velocity
        if pressure_ratio <= critical_ratio:
            # Choked flow (critical)
            velocity = math.sqrt(
                (2 * gamma / (gamma + 1)) * gas_constant * temperature_k
            )
            notes = "Choked flow"
        else:
            # Subsonic flow
            velocity = math.sqrt(
                (2 * gamma / (gamma - 1)) * gas_constant * temperature_k *
                (1 - pressure_ratio ** ((gamma - 1) / gamma))
            )
            notes = "Subsonic flow"

        rate = discharge_coeff * hole_area_m2 * gas_density_kg_m3 * velocity

        return DischargeResult(rate_kg_s=rate, notes=notes)

    @staticmethod
    def calculate_from_pressure_vessel(
        hole_diameter_m: float,
        gas_density_kg_m3: float,
        vessel_pressure_pa: float,
        back_pressure_pa: float = 101325.0,
        gamma: float = 1.4,
    ) -> DischargeResult:
        """
        Calculate discharge from pressurized gas vessel.

        Args:
            hole_diameter_m: Diameter of hole (m)
            gas_density_kg_m3: Gas density (kg/m³)
            vessel_pressure_pa: Vessel pressure (Pa)
            back_pressure_pa: Ambient/back pressure (Pa)
            gamma: Heat capacity ratio

        Returns:
            DischargeResult with rate
        """
        hole_area = math.pi * (hole_diameter_m / 2) ** 2

        return GasDischarge.calculate_rate(
            hole_area, gas_density_kg_m3, vessel_pressure_pa, back_pressure_pa, gamma
        )


class TwoPhaseFlow:
    """
    Two-phase (flashing liquid) discharge model (HEM/Fauske).

    For liquids released under pressure that flash to vapor.
    """

    @staticmethod
    def calculate_rate(
        hole_area_m2: float,
        liquid_density_kg_m3: float,
        upstream_pressure_pa: float,
        saturation_pressure_pa: float,
        discharge_coeff: float = 0.8,
    ) -> DischargeResult:
        """
        Calculate two-phase discharge rate using homogeneous equilibrium model.

        Args:
            hole_area_m2: Area of hole (m²)
            liquid_density_kg_m3: Liquid density (kg/m³)
            upstream_pressure_pa: Upstream pressure (Pa)
            saturation_pressure_pa: Saturation pressure at ambient (Pa)
            discharge_coeff: Discharge coefficient

        Returns:
            DischargeResult with rate
        """
        if upstream_pressure_pa <= saturation_pressure_pa:
            # No flashing - single phase liquid
            pressure_diff = upstream_pressure_pa - saturation_pressure_pa
            rate = LiquidDischarge.calculate_rate(
                hole_area_m2, liquid_density_kg_m3, pressure_diff, discharge_coeff
            )
            return DischargeResult(rate_kg_s=rate, notes="Single phase liquid")

        # Simplified two-phase model
        # Calculate quality (mass fraction vapor)
        # Assuming constant enthalpy flash

        pressure_ratio = saturation_pressure_pa / upstream_pressure_pa

        # Two-phase density (simplified)
        # Use homogeneous equilibrium model approximation
        two_phase_density = liquid_density_kg_m3 * pressure_ratio ** 0.5

        # Nozzle velocity (simplified)
        g = 9.81
        velocity = math.sqrt(2 * (upstream_pressure_pa - saturation_pressure_pa) / two_phase_density)

        rate = discharge_coeff * hole_area_m2 * two_phase_density * velocity

        return DischargeResult(rate_kg_s=rate, notes="Two-phase flashing flow")


class PoolEvaporation:
    """
    Pool spreading and evaporation model.

    Combines pool spreading dynamics with evaporation rate calculation.
    """

    @staticmethod
    def calculate_spreading_radius(
        volume_m3: float,
        time_s: float,
        liquid_density_kg_m3: float,
        substrate: str = 'concrete',
    ) -> float:
        """
        Calculate pool radius over time using gravity-inertia spreading regime.

        For continuous spreading on flat surface.

        Args:
            volume_m3: Initial liquid volume (m³)
            time_s: Time since release (s)
            liquid_density_kg_m3: Liquid density (kg/m³)
            substrate: Ground substrate (concrete, soil, water)

        Returns:
            Pool radius (m)
        """
        if volume_m3 <= 0 or time_s <= 0:
            return 0.0

        g = 9.81  # m/s²

        # Spreading coefficient based on substrate
        substrate_coeffs = {
            'concrete': 1.5,
            'soil': 1.0,
            'sand': 0.8,
            'water': 2.0,
        }
        alpha = substrate_coeffs.get(substrate, 1.0)

        # Gravity-inertia regime: R = alpha * (g * V^2 / t)^(1/4)
        radius = alpha * ((g * volume_m3 ** 2) / time_s) ** 0.25

        return radius

    @staticmethod
    def calculate_equilibrium_radius(
        volume_m3: float,
        liquid_density_kg_m3: float,
        bund_area_m2: Optional[float] = None,
    ) -> float:
        """
        Calculate equilibrium pool radius (maximum spread).

        Args:
            volume_m3: Liquid volume (m³)
            liquid_density_kg_m3: Liquid density (kg/m³)
            bund_area_m2: Bund/containment area (m²), if present

        Returns:
            Pool radius (m)
        """
        if bund_area_m2:
            # Contained by bund
            radius = math.sqrt(bund_area_m2 / math.pi)
        else:
            # Unconfined spreading to thin film (~1 cm)
            min_depth = 0.01  # m
            area = volume_m3 / min_depth
            radius = math.sqrt(area / math.pi)

        return radius

    @staticmethod
    def calculate_evaporation_rate(
        pool_area_m2: float,
        vapor_pressure_pa: float,
        molecular_weight_g_mol: float,
        wind_speed_ms: float,
        temperature_k: float = 298.15,
    ) -> float:
        """
        Calculate evaporation rate using Mackay & Matsugu correlation.

        E = (M * P_v / (R * T)) * K * A

        Where K is mass transfer coefficient.

        Args:
            pool_area_m2: Pool surface area (m²)
            vapor_pressure_pa: Vapor pressure (Pa)
            molecular_weight_g_mol: Molecular weight (g/mol)
            wind_speed_ms: Wind speed at 10m height (m/s)
            temperature_k: Ambient temperature (K)

        Returns:
            Evaporation rate (kg/s)
        """
        if pool_area_m2 <= 0 or vapor_pressure_pa <= 0:
            return 0.0

        R = 8.314  # J/(mol·K)
        M_kg_mol = molecular_weight_g_mol / 1000.0  # Convert to kg/mol

        # Saturation concentration (kg/m³)
        C_sat = (M_kg_mol * vapor_pressure_pa) / (R * temperature_k)

        # Mass transfer coefficient (Mackay & Matsugu)
        # K = 0.002 * u^0.78 * (M)^-0.475
        # Simplified: K ~ D / L where D is diffusivity
        # Using empirical correlation
        K = 0.00482 * wind_speed_ms ** 0.78 * (molecular_weight_g_mol) ** -0.475

        # Evaporation rate
        rate = K * pool_area_m2 * C_sat

        return rate

    @staticmethod
    def calculate_pool_evaporation(
        volume_m3: float,
        vapor_pressure_pa: float,
        molecular_weight_g_mol: float,
        liquid_density_kg_m3: float,
        wind_speed_ms: float,
        bund_area_m2: Optional[float] = None,
        substrate: str = 'concrete',
        temperature_k: float = 298.15,
    ) -> DischargeResult:
        """
        Calculate pool evaporation from spilled liquid.

        Args:
            volume_m3: Spilled volume (m³)
            vapor_pressure_pa: Vapor pressure (Pa)
            molecular_weight_g_mol: Molecular weight (g/mol)
            liquid_density_kg_m3: Liquid density (kg/m³)
            wind_speed_ms: Wind speed (m/s)
            bund_area_m2: Containment area (m²)
            substrate: Ground substrate
            temperature_k: Temperature (K)

        Returns:
            DischargeResult with evaporation rate and duration
        """
        # Equilibrium pool radius
        radius = PoolEvaporation.calculate_equilibrium_radius(
            volume_m3, liquid_density_kg_m3, bund_area_m2
        )
        pool_area = math.pi * radius ** 2

        # Evaporation rate
        evap_rate = PoolEvaporation.calculate_evaporation_rate(
            pool_area, vapor_pressure_pa, molecular_weight_g_mol,
            wind_speed_ms, temperature_k
        )

        # Time to evaporate
        mass = volume_m3 * liquid_density_kg_m3
        if evap_rate > 0:
            duration = mass / evap_rate
        else:
            duration = float('inf')

        return DischargeResult(
            rate_kg_s=evap_rate,
            duration_s=duration,
            total_mass_kg=mass,
            notes=f"Pool radius: {radius:.1f}m, Area: {pool_area:.1f}m²"
        )


class HoleSizeCalculator:
    """Calculate effective hole area from various damage scenarios"""

    @staticmethod
    def circular_hole(diameter_m: float) -> float:
        """Calculate area of circular hole"""
        return math.pi * (diameter_m / 2) ** 2

    @staticmethod
    def crack_equivalent(length_m: float, width_m: float) -> float:
        """Calculate equivalent area of rectangular crack"""
        return length_m * width_m

    @staticmethod
    def corrosion_hole(
        wall_thickness_m: float,
        corrosion_rate_m_year: float,
        years: float,
        shape: str = 'circular',
    ) -> Tuple[float, str]:
        """
        Estimate hole size from uniform corrosion.

        Args:
            wall_thickness_m: Initial wall thickness (m)
            corrosion_rate_m_year: Corrosion rate (m/year)
            years: Years of corrosion
            shape: Hole shape assumption

        Returns:
            Tuple of (area_m2, description)
        """
        penetration = corrosion_rate_m_year * years

        if penetration >= wall_thickness_m:
            # Full penetration
            diameter = wall_thickness_m * 2  # Assume through-wall
            description = "Full penetration"
        else:
            # Partial penetration - estimate remaining thickness
            # Assume localized pitting creates hole of ~penetration diameter
            diameter = penetration * 2
            description = f"Partial penetration: {penetration*1000:.1f}mm"

        if shape == 'circular':
            area = HoleSizeCalculator.circular_hole(diameter)
        else:
            # Rectangular crack
            length = diameter * 5  # Typical aspect ratio
            width = diameter
            area = length * width
            description += f", rectangular crack {length*1000:.1f}x{width*1000:.1f}mm"

        return area, description

    @staticmethod
    def rupture_equivalent(
        vessel_volume_m3: float,
        vessel_length_m: Optional[float] = None,
        rupture_type: str = 'catastrophic',
    ) -> Tuple[float, str]:
        """
        Estimate effective hole area from vessel rupture.

        Args:
            vessel_volume_m3: Vessel volume (m³)
            vessel_length_m: Vessel length (m), if known
            rupture_type: Type of rupture (catastrophic, partial, tear)

        Returns:
            Tuple of (area_m2, description)
        """
        if rupture_type == 'catastrophic':
            # Full vessel break - assume large opening
            # Approximate as cross-section
            if vessel_length_m:
                diameter = (4 * vessel_volume_m3 / (math.pi * vessel_length_m)) ** 0.5
            else:
                # Assume spherical vessel
                diameter = (6 * vessel_volume_m3 / math.pi) ** (1/3)

            area = HoleSizeCalculator.circular_hole(diameter)
            description = f"Catastrophic failure, approx {diameter:.1f}m diameter opening"

        elif rupture_type == 'partial':
            # Assume 50% of cross-section
            if vessel_length_m:
                diameter = (4 * vessel_volume_m3 / (math.pi * vessel_length_m)) ** 0.5
            else:
                diameter = (6 * vessel_volume_m3 / math.pi) ** (1/3)

            area = 0.5 * HoleSizeCalculator.circular_hole(diameter)
            description = f"Partial rupture, ~50% of {diameter:.1f}m diameter"

        else:  # tear
            # Longitudinal tear - assume rectangular
            if vessel_length_m:
                length = vessel_length_m * 0.3  # 30% of length
                width = 0.1  # 10 cm wide tear
            else:
                diameter = (6 * vessel_volume_m3 / math.pi) ** (1/3)
                length = diameter * 0.5
                width = 0.05

            area = length * width
            description = f"Tear {length*1000:.1f}x{width*1000:.0f}mm"

        return area, description