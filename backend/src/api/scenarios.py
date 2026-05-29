"""Scenario management API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime

from ..database import get_db
from ..models.scenario import EmergencyScenario, WeatherPreset
from ..models.facility import Facility
from ..models.chemical import Chemical
from ..models.result import EPZResult as DBEPZResult
from ..schemas import (
    Scenario,
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioListItem,
    WeatherPreset as WeatherPresetSchema,
    WeatherPresetCreate,
    EPZResult as EPZResultSchema,
    EPZZone,
    MessageResponse,
)

router = APIRouter()


# Weather Presets Routes


@router.get("/weather-presets", response_model=List[WeatherPresetSchema])
async def list_weather_presets(
    db: AsyncSession = Depends(get_db),
):
    """List all weather presets"""
    query = select(WeatherPreset).order_by(WeatherPreset.name)
    result = await db.execute(query)
    presets = result.scalars().all()

    return [
        WeatherPresetSchema(
            id=p.id,
            name=p.name,
            stability_class=p.stability_class,
            wind_speed_ms=p.wind_speed_ms,
            wind_direction_deg=p.wind_direction_deg,
            temperature_c=p.temperature_c,
            humidity_percent=p.humidity_percent,
            surface_roughness_m=p.surface_roughness_m,
            inversion_height_m=p.inversion_height_m,
            is_builtin=p.is_builtin,
        )
        for p in presets
    ]


@router.post("/weather-presets", response_model=WeatherPresetSchema, status_code=201)
async def create_weather_preset(
    preset: WeatherPresetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a custom weather preset"""
    db_preset = WeatherPreset(**preset.model_dump(), is_builtin=False)
    db.add(db_preset)
    await db.commit()
    await db.refresh(db_preset)

    return WeatherPresetSchema(
        id=db_preset.id,
        name=db_preset.name,
        stability_class=db_preset.stability_class,
        wind_speed_ms=db_preset.wind_speed_ms,
        wind_direction_deg=db_preset.wind_direction_deg,
        temperature_c=db_preset.temperature_c,
        humidity_percent=db_preset.humidity_percent,
        surface_roughness_m=db_preset.surface_roughness_m,
        inversion_height_m=db_preset.inversion_height_m,
        is_builtin=db_preset.is_builtin,
    )


# Scenario Routes


@router.get("/", response_model=List[ScenarioListItem])
async def list_scenarios(
    facility_id: Optional[uuid.UUID] = Query(None),
    scenario_category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List scenarios with optional filters"""
    query = select(EmergencyScenario)

    if facility_id:
        query = query.where(EmergencyScenario.facility_id == facility_id)
    if scenario_category:
        query = query.where(EmergencyScenario.scenario_category == scenario_category)

    query = query.order_by(EmergencyScenario.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    scenarios = result.scalars().all()

    # Fetch related data
    response = []
    for s in scenarios:
        # Get facility
        fac_query = select(Facility).where(Facility.id == s.facility_id)
        fac_result = await db.execute(fac_query)
        facility = fac_result.scalar_one_or_none()

        # Get chemical
        chem_query = select(Chemical).where(Chemical.cas_number == s.chemical_cas)
        chem_result = await db.execute(chem_query)
        chemical = chem_result.scalar_one_or_none()

        facility_info = None
        if facility:
            facility_info = {
                "id": facility.id,
                "name": facility.name,
                "city": facility.city,
            }

        chemical_info = None
        if chemical:
            chemical_info = {
                "cas_number": chemical.cas_number,
                "name": chemical.name,
                "formula": chemical.formula,
            }

        response.append(
            ScenarioListItem(
                id=s.id,
                name=s.name,
                facility_id=s.facility_id,
                chemical_cas=s.chemical_cas,
                scenario_type=s.scenario_type,
                scenario_category=s.scenario_category,
                created_at=s.created_at,
                updated_at=s.updated_at,
                facility=facility_info,
                chemical=chemical_info,
            )
        )

    return response


@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get scenario by ID"""
    query = select(EmergencyScenario).where(EmergencyScenario.id == scenario_id)
    result = await db.execute(query)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get facility and chemical info
    fac_query = select(Facility).where(Facility.id == scenario.facility_id)
    fac_result = await db.execute(fac_query)
    facility = fac_result.scalar_one_or_none()

    chem_query = select(Chemical).where(Chemical.cas_number == scenario.chemical_cas)
    chem_result = await db.execute(chem_query)
    chemical = chem_result.scalar_one_or_none()

    facility_info = None
    if facility:
        facility_info = {
            "id": facility.id,
            "name": facility.name,
            "city": facility.city,
        }

    chemical_info = None
    if chemical:
        chemical_info = {
            "cas_number": chemical.cas_number,
            "name": chemical.name,
            "formula": chemical.formula,
        }

    return Scenario(
        id=scenario.id,
        name=scenario.name,
        chemical_cas=scenario.chemical_cas,
        facility_id=scenario.facility_id,
        scenario_type=scenario.scenario_type,
        release_rate_kg_s=scenario.release_rate_kg_s,
        total_release_kg=scenario.total_release_kg,
        duration_s=scenario.duration_s,
        release_height_m=scenario.release_height_m,
        release_direction=scenario.release_direction,
        pool_area_m2=scenario.pool_area_m2,
        hole_diameter_m=scenario.hole_diameter_m,
        discharge_coefficient=scenario.discharge_coefficient,
        secondary_containment=scenario.secondary_containment,
        bund_area_m2=scenario.bund_area_m2,
        water_spray=scenario.water_spray,
        mitigation_factor=scenario.mitigation_factor,
        weather_preset_id=scenario.weather_preset_id,
        stability_class=scenario.stability_class,
        wind_speed_ms=scenario.wind_speed_ms,
        wind_direction_deg=scenario.wind_direction_deg,
        temperature_c=scenario.temperature_c,
        humidity_percent=scenario.humidity_percent,
        surface_roughness_m=scenario.surface_roughness_m,
        scenario_category=scenario.scenario_category,
        model_override=scenario.model_override,
        grid_resolution_m=scenario.grid_resolution_m,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at,
        facility=facility_info,
        chemical=chemical_info,
    )


@router.post("/", response_model=Scenario, status_code=201)
async def create_scenario(
    scenario: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new scenario"""
    # Verify facility exists
    fac_query = select(Facility).where(Facility.id == scenario.facility_id)
    fac_result = await db.execute(fac_query)
    if not fac_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Facility not found")

    # Verify chemical exists
    chem_query = select(Chemical).where(Chemical.cas_number == scenario.chemical_cas)
    chem_result = await db.execute(chem_query)
    if not chem_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chemical not found")

    # If weather preset specified, load preset values
    if scenario.weather_preset_id:
        preset_query = select(WeatherPreset).where(WeatherPreset.id == scenario.weather_preset_id)
        preset_result = await db.execute(preset_query)
        preset = preset_result.scalar_one_or_none()

        if preset:
            # Use preset values if not explicitly provided
            scenario_dict = scenario.model_dump()
            if scenario_dict.get('stability_class') is None:
                scenario_dict['stability_class'] = preset.stability_class
            if scenario_dict.get('wind_speed_ms') is None:
                scenario_dict['wind_speed_ms'] = preset.wind_speed_ms
            if scenario_dict.get('wind_direction_deg') is None:
                scenario_dict['wind_direction_deg'] = preset.wind_direction_deg
            if scenario_dict.get('temperature_c') == 25:  # Default value
                scenario_dict['temperature_c'] = preset.temperature_c
            if scenario_dict.get('humidity_percent') == 50:  # Default value
                scenario_dict['humidity_percent'] = preset.humidity_percent
            if scenario_dict.get('surface_roughness_m') == 0.03:  # Default value
                scenario_dict['surface_roughness_m'] = preset.surface_roughness_m

            scenario_data = scenario_dict
        else:
            scenario_data = scenario.model_dump()
    else:
        scenario_data = scenario.model_dump()

    db_scenario = EmergencyScenario(**scenario_data)
    db.add(db_scenario)
    await db.commit()
    await db.refresh(db_scenario)

    return await get_scenario(db_scenario.id, db)


@router.put("/{scenario_id}", response_model=Scenario)
async def update_scenario(
    scenario_id: uuid.UUID,
    scenario: ScenarioUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update scenario"""
    query = select(EmergencyScenario).where(EmergencyScenario.id == scenario_id)
    result = await db.execute(query)
    db_scenario = result.scalar_one_or_none()

    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    update_data = scenario.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_scenario, field, value)

    db_scenario.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_scenario)

    return await get_scenario(scenario_id, db)


@router.delete("/{scenario_id}", response_model=MessageResponse)
async def delete_scenario(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete scenario (cascades to results)"""
    query = select(EmergencyScenario).where(EmergencyScenario.id == scenario_id)
    result = await db.execute(query)
    db_scenario = result.scalar_one_or_none()

    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    await db.delete(db_scenario)
    await db.commit()

    return MessageResponse(message=f"Scenario {scenario_id} deleted successfully")


# Scenario Results Routes


@router.get("/{scenario_id}/results", response_model=List[EPZResultSchema])
async def list_scenario_results(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List EPZ calculation results for a scenario"""
    # Verify scenario exists
    scenario_query = select(EmergencyScenario).where(EmergencyScenario.id == scenario_id)
    scenario_result = await db.execute(scenario_query)
    if not scenario_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Scenario not found")

    query = select(DBEPZResult).where(
        DBEPZResult.scenario_id == scenario_id
    ).order_by(DBEPZResult.computed_at.desc())
    result = await db.execute(query)
    db_results = result.scalars().all()

    response = []
    for r in db_results:
        # Build zones list
        zones = []
        zone_mappings = {
            'erpg1': ('ERPG-1', r.erpg1_downwind_m, r.erpg1_area_km2),
            'erpg2': ('ERPG-2', r.erpg2_downwind_m, r.erpg2_area_km2),
            'erpg3': ('ERPG-3', r.erpg3_downwind_m, r.erpg3_area_km2),
            'idlh': ('IDLH', r.idlh_downwind_m, None),
            'aegl1_60min': ('AEGL-1 (60min)', r.aegl1_60min_downwind_m, None),
            'aegl2_60min': ('AEGL-2 (60min)', r.aegl2_60min_downwind_m, None),
            'aegl3_60min': ('AEGL-3 (60min)', r.aegl3_60min_downwind_m, None),
        }

        for zone_key, (name, downwind, area) in zone_mappings.items():
            if downwind is not None:
                zones.append(
                    EPZZone(
                        threshold_name=name,
                        threshold_value_ppm=None,
                        threshold_value_mg_m3=None,
                        downwind_distance_m=downwind,
                        crosswind_width_m=None,
                        area_km2=area,
                        affected_population=None,
                    )
                )

        response.append(
            EPZResultSchema(
                id=r.id,
                scenario_id=r.scenario_id,
                computed_at=r.computed_at,
                model_used=r.model_used,
                computation_time_ms=r.computation_time_ms,
                zones=zones,
                total_affected_area_km2=r.total_affected_area_km2,
                estimated_affected_population=r.estimated_affected_population,
                population_by_zone=r.population_by_zone,
                affected_vulnerable_facilities=r.affected_vulnerable_facilities,
                evacuation_time_min=r.evacuation_time_min,
                shelter_in_place_recommended=r.shelter_in_place_recommended,
                wind_direction_deg=r.wind_direction_deg,
                stability_class=r.stability_class,
                contour_geojson=r.contour_geojson,
                wind_rose_geojson=r.wind_rose_geojson,
            )
        )

    return response


@router.get("/{scenario_id}/results/latest", response_model=EPZResultSchema)
async def get_latest_result(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get latest EPZ calculation result for a scenario"""
    query = select(DBEPZResult).where(
        DBEPZResult.scenario_id == scenario_id
    ).order_by(DBEPZResult.computed_at.desc()).limit(1)
    result = await db.execute(query)
    db_result = result.scalar_one_or_none()

    if not db_result:
        raise HTTPException(status_code=404, detail="No results found for this scenario")

    # Build response (same as list_scenario_results)
    zones = []
    zone_mappings = {
        'erpg1': ('ERPG-1', db_result.erpg1_downwind_m, db_result.erpg1_area_km2),
        'erpg2': ('ERPG-2', db_result.erpg2_downwind_m, db_result.erpg2_area_km2),
        'erpg3': ('ERPG-3', db_result.erpg3_downwind_m, db_result.erpg3_area_km2),
        'idlh': ('IDLH', db_result.idlh_downwind_m, None),
        'aegl1_60min': ('AEGL-1 (60min)', db_result.aegl1_60min_downwind_m, None),
        'aegl2_60min': ('AEGL-2 (60min)', db_result.aegl2_60min_downwind_m, None),
        'aegl3_60min': ('AEGL-3 (60min)', db_result.aegl3_60min_downwind_m, None),
    }

    for zone_key, (name, downwind, area) in zone_mappings.items():
        if downwind is not None:
            zones.append(
                EPZZone(
                    threshold_name=name,
                    threshold_value_ppm=None,
                    threshold_value_mg_m3=None,
                    downwind_distance_m=downwind,
                    crosswind_width_m=None,
                    area_km2=area,
                    affected_population=None,
                )
            )

    return EPZResultSchema(
        id=db_result.id,
        scenario_id=db_result.scenario_id,
        computed_at=db_result.computed_at,
        model_used=db_result.model_used,
        computation_time_ms=db_result.computation_time_ms,
        zones=zones,
        total_affected_area_km2=db_result.total_affected_area_km2,
        estimated_affected_population=db_result.estimated_affected_population,
        population_by_zone=db_result.population_by_zone,
        affected_vulnerable_facilities=db_result.affected_vulnerable_facilities,
        evacuation_time_min=db_result.evacuation_time_min,
        shelter_in_place_recommended=db_result.shelter_in_place_recommended,
        wind_direction_deg=db_result.wind_direction_deg,
        stability_class=db_result.stability_class,
        contour_geojson=db_result.contour_geojson,
        wind_rose_geojson=db_result.wind_rose_geojson,
    )