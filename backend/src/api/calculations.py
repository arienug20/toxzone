"""Calculation API routes - sync SQLite"""

import json
import math
import time as time_mod
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from ..models.scenario import EmergencyScenario
from ..models.chemical import Chemical
from ..models.facility import Facility
from ..models.result import EPZResultDB
from ..core.epz_calculator import EPZCalculator
from ..core.population_estimator import PopulationEstimator
from ..schemas import (
    CalculationRequest,
    CalculationResponse,
    EPZZoneResult,
    EPZResultDetail,
    MessageResponse,
)

router = APIRouter()


@router.post("/compute", response_model=CalculationResponse)
def compute_epz(request: CalculationRequest, db: Session = Depends(get_db)):
    """Compute EPZ for a scenario"""
    # Get chemical
    result = db.execute(select(Chemical).where(Chemical.cas_number == request.chemical_cas))
    chemical = result.scalar_one_or_none()
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Build chemical dict
    chemical_dict = {}
    for col in chemical.__table__.columns:
        val = getattr(chemical, col.name)
        if col.name in ('synonyms', 'data_sources', 'ghs_pictograms', 'risk_phrases') and val:
            try:
                val = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                val = []
        chemical_dict[col.name] = val

    # Build scenario dict
    scenario_dict = {
        'scenario_type': request.scenario_type,
        'release_rate_kg_s': request.release_rate_kg_s,
        'total_release_kg': request.total_release_kg,
        'duration_s': request.duration_s,
        'release_height_m': request.release_height_m or 0.0,
        'release_direction': request.release_direction or 'horizontal',
        'pool_area_m2': request.pool_area_m2,
        'hole_diameter_m': request.hole_diameter_m,
        'discharge_coefficient': request.discharge_coefficient or 0.61,
        'mitigation_factor': request.mitigation_factor or 1.0,
        'model_override': request.model_override,
        'grid_resolution_m': request.grid_resolution_m or 5.0,
        'bund_area_m2': request.bund_area_m2,
    }

    # Build weather dict
    weather_dict = {
        'stability_class': request.stability_class or 'D',
        'wind_speed_ms': request.wind_speed_ms or 5.0,
        'wind_direction_deg': request.wind_direction_deg or 0.0,
        'temperature_c': request.temperature_c or 25.0,
        'humidity_percent': request.humidity_percent or 50.0,
        'surface_roughness_m': request.surface_roughness_m or 0.03,
    }

    # Calculate EPZ
    calculator = EPZCalculator(chemical_dict, scenario_dict, weather_dict)
    epz_result = calculator.calculate_all_zones()

    # Build zones for response
    zones = []
    for key, zone in epz_result.zones.items():
        zones.append(EPZZoneResult(
            threshold_name=zone.threshold_name,
            threshold_value_ppm=zone.threshold_value_ppm,
            threshold_value_mg_m3=zone.threshold_value_mg_m3,
            downwind_distance_m=zone.downwind_distance_m,
            crosswind_width_m=zone.crosswind_width_m,
            area_km2=zone.area_km2,
        ))

    # Population estimate if facility provided
    pop_est = None
    if request.facility_id:
        fac_result = db.execute(select(Facility).where(Facility.id == request.facility_id))
        facility = fac_result.scalar_one_or_none()
        if facility:
            estimator = PopulationEstimator(default_density=facility.default_pop_density)
            pop_est = estimator.estimate_from_zones(
                {k: z.area_km2 for k, z in epz_result.zones.items() if z.area_km2}
            )

    result_detail = EPZResultDetail(
        model_used=epz_result.model_used,
        model_description=epz_result.model_description,
        computation_time_ms=epz_result.computation_time_ms,
        wind_direction_deg=epz_result.wind_direction_deg,
        stability_class=epz_result.stability_class,
        total_affected_area_km2=epz_result.total_affected_area_km2,
        zones=zones,
        population_estimate=pop_est,
        contour_geojson=epz_result.contour_geojson,
        warnings=epz_result.warnings,
    )

    # Save result if scenario_id provided
    if request.scenario_id:
        db_result = EPZResultDB(
            scenario_id=request.scenario_id,
            model_used=epz_result.model_used,
            computation_time_ms=int(epz_result.computation_time_ms),
            total_affected_area_km2=epz_result.total_affected_area_km2,
            wind_direction_deg=epz_result.wind_direction_deg,
            stability_class=epz_result.stability_class,
        )
        # Set zone distances
        for key, zone in epz_result.zones.items():
            col_map = {
                'erpg_1': 'erpg1_downwind_m',
                'erpg_2': 'erpg2_downwind_m',
                'erpg_3': 'erpg3_downwind_m',
                'idlh': 'idlh_downwind_m',
            }
            if key in col_map and zone.downwind_distance_m:
                setattr(db_result, col_map[key], zone.downwind_distance_m)

        if epz_result.contour_geojson:
            db_result.contour_geojson = json.dumps(epz_result.contour_geojson)

        db.add(db_result)
        db.commit()

    return CalculationResponse(result=result_detail, warnings=epz_result.warnings)


@router.post("/wind-rose")
def compute_wind_rose(
    request: CalculationRequest,
    step_deg: int = 15,
    db: Session = Depends(get_db),
):
    """Compute EPZ for multiple wind directions"""
    result = db.execute(select(Chemical).where(Chemical.cas_number == request.chemical_cas))
    chemical = result.scalar_one_or_none()
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    chemical_dict = {}
    for col in chemical.__table__.columns:
        val = getattr(chemical, col.name)
        if col.name in ('synonyms', 'data_sources', 'ghs_pictograms', 'risk_phrases') and val:
            try:
                val = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                val = []
        chemical_dict[col.name] = val

    scenario_dict = {
        'scenario_type': request.scenario_type,
        'release_rate_kg_s': request.release_rate_kg_s,
        'total_release_kg': request.total_release_kg,
        'duration_s': request.duration_s,
        'release_height_m': request.release_height_m or 0.0,
        'mitigation_factor': request.mitigation_factor or 1.0,
        'model_override': request.model_override,
        'grid_resolution_m': request.grid_resolution_m or 5.0,
        'bund_area_m2': request.bund_area_m2,
        'discharge_coefficient': request.discharge_coefficient or 0.61,
        'release_direction': request.release_direction or 'horizontal',
        'pool_area_m2': request.pool_area_m2,
        'hole_diameter_m': request.hole_diameter_m,
    }

    weather_dict = {
        'stability_class': request.stability_class or 'D',
        'wind_speed_ms': request.wind_speed_ms or 5.0,
        'temperature_c': request.temperature_c or 25.0,
        'humidity_percent': request.humidity_percent or 50.0,
        'surface_roughness_m': request.surface_roughness_m or 0.03,
    }

    calculator = EPZCalculator(chemical_dict, scenario_dict, weather_dict)
    wind_rose = calculator.compute_wind_rose(step_deg=step_deg)

    return {"wind_rose": wind_rose}
