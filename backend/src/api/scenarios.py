"""Scenario API routes - sync SQLite"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from ..database import get_db
from ..models.scenario import EmergencyScenario, WeatherPreset
from ..models.facility import Facility
from ..models.chemical import Chemical
from ..schemas import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioListItem,
    ScenarioDetail,
    WeatherPresetCreate,
    WeatherPresetDetail,
    MessageResponse,
)

router = APIRouter()


@router.get("/", response_model=List[ScenarioListItem])
def list_scenarios(
    facility_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = select(EmergencyScenario)
    if facility_id:
        query = query.where(EmergencyScenario.facility_id == facility_id)
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    scenarios = result.scalars().all()
    items = []
    for s in scenarios:
        items.append(ScenarioListItem(
            id=s.id, name=s.name, facility_id=s.facility_id,
            chemical_cas=s.chemical_cas, scenario_type=s.scenario_type,
            scenario_category=s.scenario_category, created_at=s.created_at,
        ))
    return items


@router.get("/{scenario_id}", response_model=ScenarioDetail)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(EmergencyScenario).where(EmergencyScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioDetail.model_validate(scenario)


@router.post("/", response_model=ScenarioDetail, status_code=201)
def create_scenario(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    fac = db.execute(select(Facility).where(Facility.id == scenario.facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    chem = db.execute(select(Chemical).where(Chemical.cas_number == scenario.chemical_cas)).scalar_one_or_none()
    if not chem:
        raise HTTPException(status_code=404, detail="Chemical not found")
    db_scenario = EmergencyScenario(**scenario.model_dump())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return ScenarioDetail.model_validate(db_scenario)


@router.put("/{scenario_id}", response_model=ScenarioDetail)
def update_scenario(scenario_id: str, scenario: ScenarioUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(EmergencyScenario).where(EmergencyScenario.id == scenario_id))
    db_scenario = result.scalar_one_or_none()
    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    update_data = scenario.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_scenario, field, value)
    db.commit()
    db.refresh(db_scenario)
    return ScenarioDetail.model_validate(db_scenario)


@router.delete("/{scenario_id}", response_model=MessageResponse)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(EmergencyScenario).where(EmergencyScenario.id == scenario_id))
    db_scenario = result.scalar_one_or_none()
    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(db_scenario)
    db.commit()
    return MessageResponse(message=f"Scenario {scenario_id} deleted successfully")


# Weather Presets

@router.get("/weather-presets/", response_model=List[WeatherPresetDetail])
def list_weather_presets(db: Session = Depends(get_db)):
    result = db.execute(select(WeatherPreset))
    return [WeatherPresetDetail.model_validate(wp) for wp in result.scalars().all()]


@router.post("/weather-presets/", response_model=WeatherPresetDetail, status_code=201)
def create_weather_preset(preset: WeatherPresetCreate, db: Session = Depends(get_db)):
    db_preset = WeatherPreset(**preset.model_dump())
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return WeatherPresetDetail.model_validate(db_preset)
