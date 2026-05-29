"""EPZ calculation API routes"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import Dict, Any

from ..database import get_db
from ..models.scenario import EmergencyScenario
from ..models.chemical import Chemical
from ..models.facility import Facility
from ..models.result import EPZResult as DBEPZResult
from ..schemas import (
    CalculationRequest,
    CalculationResponse,
    EPZResult as EPZResultSchema,
    EPZZone,
)
from ..core import EPZCalculator

router = APIRouter()


async def _get_scenario_data(scenario_id: uuid.UUID, db: AsyncSession) -> tuple:
    """Fetch scenario, chemical, and weather data"""
    # Get scenario
    scenario_query = select(EmergencyScenario).where(EmergencyScenario.id == scenario_id)
    scenario_result = await db.execute(scenario_query)
    scenario = scenario_result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get chemical
    chemical_query = select(Chemical).where(Chemical.cas_number == scenario.chemical_cas)
    chemical_result = await db.execute(chemical_query)
    chemical = chemical_result.scalar_one_or_none()

    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Build weather dict
    weather = {
        'stability_class': scenario.stability_class or 'D',
        'wind_speed_ms': scenario.wind_speed_ms or 5.0,
        'wind_direction_deg': scenario.wind_direction_deg or 0.0,
        'temperature_c': scenario.temperature_c or 25.0,
        'humidity_percent': scenario.humidity_percent or 50.0,
        'surface_roughness_m': scenario.surface_roughness_m or 0.03,
    }

    # Build chemical dict
    chemical_dict = {
        'cas_number': chemical.cas_number,
        'name': chemical.name,
        'molecular_weight': chemical.molecular_weight,
        'gas_density_ratio': chemical.gas_density_ratio or 1.0,
        'is_heavier_than_air': chemical.is_heavier_than_air,
        'liquid_density_kg_m3': chemical.liquid_density_kg_m3,
        'vapor_pressure_kpa': chemical.vapor_pressure_kpa,
        'erpg_1_ppm': chemical.erpg_1_ppm,
        'erpg_2_ppm': chemical.erpg_2_ppm,
        'erpg_3_ppm': chemical.erpg_3_ppm,
        'idlh_ppm': chemical.idlh_ppm,
        'aegl_1_60min_ppm': chemical.aegl_1_60min_ppm,
        'aegl_2_60min_ppm': chemical.aegl_2_60min_ppm,
        'aegl_3_60min_ppm': chemical.aegl_3_60min_ppm,
    }

    # Build scenario dict
    scenario_dict = {
        'scenario_type': scenario.scenario_type,
        'release_rate_kg_s': scenario.release_rate_kg_s,
        'total_release_kg': scenario.total_release_kg,
        'duration_s': scenario.duration_s,
        'release_height_m': scenario.release_height_m,
        'release_direction': scenario.release_direction,
        'pool_area_m2': scenario.pool_area_m2,
        'hole_diameter_m': scenario.hole_diameter_m,
        'discharge_coefficient': scenario.discharge_coefficient,
        'mitigation_factor': scenario.mitigation_factor,
        'model_override': scenario.model_override,
        'grid_resolution_m': scenario.grid_resolution_m,
    }

    return scenario_dict, chemical_dict, weather


def _build_zones_list(epz_result) -> list:
    """Build zones list from EPZ calculator result"""
    zones = []

    zone_key_map = {
        'erpg_3': 'ERPG-3',
        'erpg_2': 'ERPG-2',
        'erpg_1': 'ERPG-1',
        'idlh': 'IDLH',
        'aegl_3_60min': 'AEGL-3 (60min)',
        'aegl_2_60min': 'AEGL-2 (60min)',
        'aegl_1_60min': 'AEGL-1 (60min)',
    }

    for zone_key, zone_info in epz_result.zones.items():
        display_name = zone_key_map.get(zone_key, zone_key)

        zones.append(
            EPZZone(
                threshold_name=display_name,
                threshold_value_ppm=zone_info.threshold_value_ppm,
                threshold_value_mg_m3=zone_info.threshold_value_mg_m3,
                downwind_distance_m=zone_info.downwind_distance_m,
                crosswind_width_m=zone_info.crosswind_width_m,
                area_km2=zone_info.area_km2,
                affected_population=None,  # Will be calculated separately
            )
        )

    return zones


def _save_calculation_result(
    scenario_id: uuid.UUID,
    epz_result,
    db: AsyncSession
):
    """Save calculation result to database (synchronous for background task)"""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Note: This is a simplified approach. In production, use a proper
    # task queue like Celery or background task handler.

    # For now, we'll skip background saving and save synchronously
    # This is a limitation of the current implementation


@router.post("/scenario/{scenario_id}", response_model=CalculationResponse)
async def calculate_epz(
    scenario_id: uuid.UUID,
    use_wind_rose: bool = False,
    wind_rose_step_deg: int = 15,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate EPZ for a scenario.

    Performs dispersion modeling and computes all applicable threshold zones.
    """
    # Fetch data
    scenario_dict, chemical_dict, weather = await _get_scenario_data(scenario_id, db)

    # Create calculator
    calculator = EPZCalculator(
        chemical=chemical_dict,
        scenario=scenario_dict,
        weather=weather,
    )

    # Calculate zones
    epz_result = calculator.calculate_all_zones()

    # Build zones list
    zones = _build_zones_list(epz_result)

    # Prepare response
    response_result = EPZResultSchema(
        id=None,  # Will be set after saving
        scenario_id=scenario_id,
        computed_at=None,  # Will be set after saving
        model_used=epz_result.model_used,
        computation_time_ms=epz_result.computation_time_ms,
        zones=zones,
        total_affected_area_km2=epz_result.total_affected_area_km2,
        estimated_affected_population=None,  # Population module not yet implemented
        population_by_zone=None,
        affected_vulnerable_facilities=None,
        evacuation_time_min=None,  # Evacuation module not yet implemented
        shelter_in_place_recommended=None,
        wind_direction_deg=epz_result.wind_direction_deg,
        stability_class=epz_result.stability_class,
        contour_geojson=epz_result.contour_geojson,
        wind_rose_geojson=epz_result.wind_rose_geojson,
    )

    # Save result to database
    db_result = DBEPZResult(
        scenario_id=scenario_id,
        model_used=epz_result.model_used,
        computation_time_ms=int(epz_result.computation_time_ms),
        wind_direction_deg=epz_result.wind_direction_deg,
        stability_class=epz_result.stability_class,
        total_affected_area_km2=epz_result.total_affected_area_km2,
        concentration_grid=epz_result.concentration_grid,
        contour_geojson=epz_result.contour_geojson,
        wind_rose_geojson=None,  # Not calculated by default
    )

    # Map zone results to database fields
    zone_field_map = {
        'erpg_3': ('erpg3_downwind_m', 'erpg3_area_km2'),
        'erpg_2': ('erpg2_downwind_m', 'erpg2_area_km2'),
        'erpg_1': ('erpg1_downwind_m', 'erpg1_area_km2'),
        'idlh': ('idlh_downwind_m', None),
        'aegl_3_60min': ('aegl3_60min_downwind_m', None),
        'aegl_2_60min': ('aegl2_60min_downwind_m', None),
        'aegl_1_60min': ('aegl1_60min_downwind_m', None),
    }

    for zone_key, (dist_field, area_field) in zone_field_map.items():
        if zone_key in epz_result.zones:
            zone = epz_result.zones[zone_key]
            if dist_field and zone.downwind_distance_m:
                setattr(db_result, dist_field, zone.downwind_distance_m)
            if area_field and zone.area_km2:
                setattr(db_result, area_field, zone.area_km2)

    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)

    # Update response with saved data
    response_result.id = db_result.id
    response_result.computed_at = db_result.computed_at

    # Wind rose calculation (optional)
    wind_rose_data = None
    if use_wind_rose:
        wind_rose_data = calculator.compute_wind_rose(step_deg=wind_rose_step_deg)
        # Save wind rose data to result
        db_result.wind_rose_geojson = wind_rose_data
        await db.commit()

    return CalculationResponse(
        result=response_result,
        warnings=epz_result.warnings,
    )


@router.post("/scenario/{scenario_id}/wind-rose")
async def calculate_wind_rose(
    scenario_id: uuid.UUID,
    step_deg: int = 15,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate wind rose analysis (EPZ for all wind directions).

    Useful for identifying worst-case wind directions.
    """
    # Fetch data
    scenario_dict, chemical_dict, weather = await _get_scenario_data(scenario_id, db)

    # Create calculator
    calculator = EPZCalculator(
        chemical=chemical_dict,
        scenario=scenario_dict,
        weather=weather,
    )

    # Calculate wind rose
    wind_rose_result = calculator.compute_wind_rose(step_deg=step_deg)

    # Return results
    return {
        "scenario_id": str(scenario_id),
        "step_deg": step_deg,
        "results": wind_rose_result,
    }