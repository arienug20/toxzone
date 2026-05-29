"""Pydantic schemas for API requests/responses"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Chemical Schemas
# ============================================

class ChemicalListItem(BaseModel):
    cas_number: str
    name: str
    formula: Optional[str] = None
    state_at_ambient: Optional[str] = None
    hazard_class: Optional[str] = None


class ChemicalCreate(BaseModel):
    cas_number: str
    name: str
    synonyms: Optional[List[str]] = None
    formula: Optional[str] = None
    molecular_weight: float = Field(..., gt=0)
    boiling_point_c: Optional[float] = None
    melting_point_c: Optional[float] = None
    liquid_density_kg_m3: Optional[float] = None
    gas_density_kg_m3: Optional[float] = None
    vapor_pressure_kpa: Optional[float] = None
    state_at_ambient: Optional[str] = None
    gas_density_ratio: Optional[float] = None
    solubility_g_l: Optional[float] = None
    lel_percent: Optional[float] = None
    uel_percent: Optional[float] = None
    hazard_class: Optional[str] = None
    un_number: Optional[str] = None
    ghs_pictograms: Optional[List[str]] = None
    risk_phrases: Optional[List[str]] = None
    first_aid: Optional[str] = None
    fire_fighting: Optional[str] = None
    ppe_requirements: Optional[str] = None
    erpg_1_ppm: Optional[float] = None
    erpg_1_mg_m3: Optional[float] = None
    erpg_2_ppm: Optional[float] = None
    erpg_2_mg_m3: Optional[float] = None
    erpg_3_ppm: Optional[float] = None
    erpg_3_mg_m3: Optional[float] = None
    idlh_ppm: Optional[float] = None
    idlh_mg_m3: Optional[float] = None
    aegl_1_10min_ppm: Optional[float] = None
    aegl_1_30min_ppm: Optional[float] = None
    aegl_1_60min_ppm: Optional[float] = None
    aegl_1_4hr_ppm: Optional[float] = None
    aegl_2_10min_ppm: Optional[float] = None
    aegl_2_30min_ppm: Optional[float] = None
    aegl_2_60min_ppm: Optional[float] = None
    aegl_2_4hr_ppm: Optional[float] = None
    aegl_3_10min_ppm: Optional[float] = None
    aegl_3_30min_ppm: Optional[float] = None
    aegl_3_60min_ppm: Optional[float] = None
    aegl_3_4hr_ppm: Optional[float] = None
    lc50_ppm: Optional[float] = None
    pel_ppm: Optional[float] = None
    rel_ppm: Optional[float] = None
    tlv_twa_ppm: Optional[float] = None
    tlv_stel_ppm: Optional[float] = None
    stel_ppm: Optional[float] = None
    weel_ppm: Optional[float] = None
    data_sources: Optional[List[str]] = None
    notes: Optional[str] = None


class ChemicalUpdate(BaseModel):
    name: Optional[str] = None
    synonyms: Optional[List[str]] = None
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    boiling_point_c: Optional[float] = None
    melting_point_c: Optional[float] = None
    liquid_density_kg_m3: Optional[float] = None
    gas_density_kg_m3: Optional[float] = None
    vapor_pressure_kpa: Optional[float] = None
    state_at_ambient: Optional[str] = None
    gas_density_ratio: Optional[float] = None
    solubility_g_l: Optional[float] = None
    lel_percent: Optional[float] = None
    uel_percent: Optional[float] = None
    hazard_class: Optional[str] = None
    un_number: Optional[str] = None
    ghs_pictograms: Optional[List[str]] = None
    risk_phrases: Optional[List[str]] = None
    first_aid: Optional[str] = None
    fire_fighting: Optional[str] = None
    ppe_requirements: Optional[str] = None
    erpg_1_ppm: Optional[float] = None
    erpg_1_mg_m3: Optional[float] = None
    erpg_2_ppm: Optional[float] = None
    erpg_2_mg_m3: Optional[float] = None
    erpg_3_ppm: Optional[float] = None
    erpg_3_mg_m3: Optional[float] = None
    idlh_ppm: Optional[float] = None
    idlh_mg_m3: Optional[float] = None
    aegl_1_10min_ppm: Optional[float] = None
    aegl_1_30min_ppm: Optional[float] = None
    aegl_1_60min_ppm: Optional[float] = None
    aegl_1_4hr_ppm: Optional[float] = None
    aegl_2_10min_ppm: Optional[float] = None
    aegl_2_30min_ppm: Optional[float] = None
    aegl_2_60min_ppm: Optional[float] = None
    aegl_2_4hr_ppm: Optional[float] = None
    aegl_3_10min_ppm: Optional[float] = None
    aegl_3_30min_ppm: Optional[float] = None
    aegl_3_60min_ppm: Optional[float] = None
    aegl_3_4hr_ppm: Optional[float] = None
    lc50_ppm: Optional[float] = None
    pel_ppm: Optional[float] = None
    rel_ppm: Optional[float] = None
    tlv_twa_ppm: Optional[float] = None
    tlv_stel_ppm: Optional[float] = None
    stel_ppm: Optional[float] = None
    weel_ppm: Optional[float] = None
    data_sources: Optional[List[str]] = None
    notes: Optional[str] = None


class ChemicalDetail(BaseModel):
    cas_number: str
    name: str
    synonyms: Optional[Any] = None
    formula: Optional[str] = None
    molecular_weight: float
    boiling_point_c: Optional[float] = None
    melting_point_c: Optional[float] = None
    liquid_density_kg_m3: Optional[float] = None
    gas_density_kg_m3: Optional[float] = None
    vapor_pressure_kpa: Optional[float] = None
    state_at_ambient: Optional[str] = None
    gas_density_ratio: Optional[float] = None
    is_heavier_than_air: Optional[bool] = None
    solubility_g_l: Optional[float] = None
    lel_percent: Optional[float] = None
    uel_percent: Optional[float] = None
    hazard_class: Optional[str] = None
    un_number: Optional[str] = None
    ghs_pictograms: Optional[Any] = None
    risk_phrases: Optional[Any] = None
    first_aid: Optional[str] = None
    fire_fighting: Optional[str] = None
    ppe_requirements: Optional[str] = None
    erpg_1_ppm: Optional[float] = None
    erpg_1_mg_m3: Optional[float] = None
    erpg_2_ppm: Optional[float] = None
    erpg_2_mg_m3: Optional[float] = None
    erpg_3_ppm: Optional[float] = None
    erpg_3_mg_m3: Optional[float] = None
    idlh_ppm: Optional[float] = None
    idlh_mg_m3: Optional[float] = None
    aegl_1_10min_ppm: Optional[float] = None
    aegl_1_30min_ppm: Optional[float] = None
    aegl_1_60min_ppm: Optional[float] = None
    aegl_1_4hr_ppm: Optional[float] = None
    aegl_2_10min_ppm: Optional[float] = None
    aegl_2_30min_ppm: Optional[float] = None
    aegl_2_60min_ppm: Optional[float] = None
    aegl_2_4hr_ppm: Optional[float] = None
    aegl_3_10min_ppm: Optional[float] = None
    aegl_3_30min_ppm: Optional[float] = None
    aegl_3_60min_ppm: Optional[float] = None
    aegl_3_4hr_ppm: Optional[float] = None
    lc50_ppm: Optional[float] = None
    pel_ppm: Optional[float] = None
    rel_ppm: Optional[float] = None
    tlv_twa_ppm: Optional[float] = None
    tlv_stel_ppm: Optional[float] = None
    stel_ppm: Optional[float] = None
    weel_ppm: Optional[float] = None
    data_sources: Optional[Any] = None
    last_updated: Optional[datetime] = None
    notes: Optional[str] = None


class ChemicalSearchResponse(BaseModel):
    chemicals: List[ChemicalListItem]
    total: int
    page: int
    page_size: int


# ============================================
# Facility Schemas
# ============================================

class FacilityCreate(BaseModel):
    name: str
    owner: Optional[str] = None
    facility_type: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation_m: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: str = "Indonesia"
    land_use: str = "industrial"
    default_pop_density: float = 1000
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class FacilityUpdate(FacilityCreate):
    pass


class FacilityListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    facility_type: Optional[str] = None
    city: Optional[str] = None
    latitude: float
    longitude: float


class FacilityDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    owner: Optional[str] = None
    facility_type: Optional[str] = None
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: str = "Indonesia"
    land_use: str = "industrial"
    default_pop_density: float = 1000
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FacilityChemicalCreate(BaseModel):
    chemical_cas: str
    max_inventory_kg: float = Field(..., gt=0)
    typical_quantity_kg: Optional[float] = None
    storage_condition: Optional[str] = None
    containment_type: Optional[str] = None
    storage_location_desc: Optional[str] = None


class FacilityChemicalDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    facility_id: str
    chemical_cas: str
    max_inventory_kg: float
    typical_quantity_kg: Optional[float] = None
    storage_condition: Optional[str] = None
    containment_type: Optional[str] = None
    storage_location_desc: Optional[str] = None
    last_updated: Optional[datetime] = None


class VulnerableFacilityCreate(BaseModel):
    name: str
    type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    estimated_occupancy: Optional[int] = None
    notes: Optional[str] = None


class VulnerableFacilityDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    facility_id: str
    name: str
    type: str
    latitude: float
    longitude: float
    estimated_occupancy: Optional[int] = None
    distance_m: Optional[float] = None
    bearing_deg: Optional[float] = None
    notes: Optional[str] = None


# ============================================
# Scenario Schemas
# ============================================

class WeatherPresetCreate(BaseModel):
    name: str
    stability_class: str = Field(..., pattern="^[A-F]$")
    wind_speed_ms: float = Field(..., gt=0)
    wind_direction_deg: float = 0
    temperature_c: float = 25
    humidity_percent: float = 50
    surface_roughness_m: float = 0.03
    inversion_height_m: Optional[float] = None


class WeatherPresetDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    stability_class: str
    wind_speed_ms: float
    wind_direction_deg: float = 0
    temperature_c: float = 25
    humidity_percent: float = 50
    surface_roughness_m: float = 0.03
    is_builtin: bool = False


class ScenarioCreate(BaseModel):
    name: str
    chemical_cas: str
    facility_id: str
    scenario_type: str
    release_rate_kg_s: Optional[float] = None
    total_release_kg: Optional[float] = None
    duration_s: Optional[float] = None
    release_height_m: float = 0
    release_direction: str = "horizontal"
    pool_area_m2: Optional[float] = None
    hole_diameter_m: Optional[float] = None
    discharge_coefficient: float = 0.61
    secondary_containment: bool = False
    bund_area_m2: Optional[float] = None
    water_spray: bool = False
    mitigation_factor: float = 1.0
    stability_class: Optional[str] = None
    wind_speed_ms: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    temperature_c: float = 25
    humidity_percent: float = 50
    surface_roughness_m: float = 0.03
    scenario_category: Optional[str] = None
    model_override: Optional[str] = None
    grid_resolution_m: float = 5


class ScenarioUpdate(ScenarioCreate):
    pass


class ScenarioListItem(BaseModel):
    id: str
    name: str
    facility_id: str
    chemical_cas: str
    scenario_type: str
    scenario_category: Optional[str] = None
    created_at: Optional[datetime] = None


class ScenarioDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    facility_id: str
    name: str
    chemical_cas: str
    scenario_type: str
    release_rate_kg_s: Optional[float] = None
    total_release_kg: Optional[float] = None
    duration_s: Optional[float] = None
    release_height_m: float = 0
    release_direction: str = "horizontal"
    pool_area_m2: Optional[float] = None
    hole_diameter_m: Optional[float] = None
    discharge_coefficient: float = 0.61
    secondary_containment: bool = False
    bund_area_m2: Optional[float] = None
    water_spray: bool = False
    mitigation_factor: float = 1.0
    stability_class: Optional[str] = None
    wind_speed_ms: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    temperature_c: float = 25
    humidity_percent: float = 50
    surface_roughness_m: float = 0.03
    scenario_category: Optional[str] = None
    model_override: Optional[str] = None
    grid_resolution_m: float = 5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================
# Calculation Schemas
# ============================================

class CalculationRequest(BaseModel):
    scenario_id: Optional[str] = None
    facility_id: Optional[str] = None
    chemical_cas: str
    scenario_type: str = "continuous"
    release_rate_kg_s: Optional[float] = None
    total_release_kg: Optional[float] = None
    duration_s: Optional[float] = None
    release_height_m: float = 0
    release_direction: str = "horizontal"
    pool_area_m2: Optional[float] = None
    hole_diameter_m: Optional[float] = None
    discharge_coefficient: float = 0.61
    mitigation_factor: float = 1.0
    model_override: Optional[str] = None
    grid_resolution_m: float = 5
    bund_area_m2: Optional[float] = None
    stability_class: Optional[str] = 'D'
    wind_speed_ms: Optional[float] = 5.0
    wind_direction_deg: Optional[float] = 0.0
    temperature_c: float = 25.0
    humidity_percent: float = 50.0
    surface_roughness_m: float = 0.03


class EPZZoneResult(BaseModel):
    threshold_name: str
    threshold_value_ppm: Optional[float] = None
    threshold_value_mg_m3: Optional[float] = None
    downwind_distance_m: Optional[float] = None
    crosswind_width_m: Optional[float] = None
    area_km2: Optional[float] = None


class EPZResultDetail(BaseModel):
    model_used: str
    model_description: str
    computation_time_ms: float
    wind_direction_deg: float
    stability_class: str
    total_affected_area_km2: float
    zones: List[EPZZoneResult] = []
    population_estimate: Optional[Dict[str, Any]] = None
    contour_geojson: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None


class CalculationResponse(BaseModel):
    result: EPZResultDetail
    warnings: Optional[List[str]] = None


class MessageResponse(BaseModel):
    message: str
