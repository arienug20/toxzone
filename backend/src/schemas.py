"""Pydantic schemas for API requests/responses"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Chemical Schemas
# ============================================

class ChemicalBase(BaseModel):
    """Base chemical schema"""
    name: str = Field(..., description="Chemical name")
    synonyms: Optional[List[str]] = None
    formula: Optional[str] = None
    molecular_weight: float = Field(..., gt=0, description="Molecular weight (g/mol)")
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


class ChemicalThresholds(BaseModel):
    """Exposure thresholds"""
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


class ChemicalCreate(ChemicalBase, ChemicalThresholds):
    """Schema for creating a chemical"""
    cas_number: str = Field(..., description="CAS registry number")
    data_sources: Optional[List[str]] = None
    notes: Optional[str] = None


class ChemicalUpdate(ChemicalBase, ChemicalThresholds):
    """Schema for updating a chemical"""
    data_sources: Optional[List[str]] = None
    notes: Optional[str] = None


class Chemical(ChemicalCreate):
    """Full chemical schema"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., alias="cas_number")
    is_heavier_than_air: bool
    last_updated: datetime

    class Config:
        populate_by_name = True


class ChemicalListItem(BaseModel):
    """Lightweight chemical for list views"""
    model_config = ConfigDict(from_attributes=True)

    cas_number: str
    name: str
    formula: Optional[str] = None
    state_at_ambient: Optional[str] = None
    hazard_class: Optional[str] = None


class ChemicalSearchResponse(BaseModel):
    """Response for chemical search"""
    chemicals: List[ChemicalListItem]
    total: int
    page: int
    page_size: int


# ============================================
# Facility Schemas
# ============================================

class FacilityBase(BaseModel):
    """Base facility schema"""
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
    emergency_contact_name_2: Optional[str] = None
    emergency_contact_phone_2: Optional[str] = None


class FacilityCreate(FacilityBase):
    """Schema for creating a facility"""
    pass


class FacilityUpdate(FacilityBase):
    """Schema for updating a facility"""
    pass


class Facility(FacilityCreate):
    """Full facility schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class FacilityListItem(BaseModel):
    """Lightweight facility for list views"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    facility_type: Optional[str] = None
    city: Optional[str] = None
    latitude: float
    longitude: float


class FacilityChemicalBase(BaseModel):
    """Base facility chemical schema"""
    chemical_cas: str
    max_inventory_kg: float = Field(..., gt=0)
    typical_quantity_kg: Optional[float] = None
    storage_condition: Optional[str] = None
    containment_type: Optional[str] = None
    storage_location_desc: Optional[str] = None


class FacilityChemicalCreate(FacilityChemicalBase):
    """Schema for adding chemical to facility"""
    pass


class FacilityChemical(FacilityChemicalCreate):
    """Full facility chemical schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    facility_id: UUID
    chemical: Optional[ChemicalListItem] = None
    last_updated: datetime


class VulnerableFacilityBase(BaseModel):
    """Base vulnerable facility schema"""
    name: str
    type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    estimated_occupancy: Optional[int] = None
    distance_m: Optional[float] = None
    bearing_deg: Optional[float] = None
    notes: Optional[str] = None


class VulnerableFacilityCreate(VulnerableFacilityBase):
    """Schema for creating vulnerable facility"""
    pass


class VulnerableFacility(VulnerableFacilityCreate):
    """Full vulnerable facility schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    facility_id: UUID


# ============================================
# Scenario Schemas
# ============================================

class WeatherPresetBase(BaseModel):
    """Base weather preset schema"""
    name: str
    stability_class: str = Field(..., pattern="^[A-F]$")
    wind_speed_ms: float = Field(..., gt=0)
    wind_direction_deg: float = Field(default=0, ge=0, lt=360)
    temperature_c: float = 25
    humidity_percent: float = Field(default=50, ge=0, le=100)
    surface_roughness_m: float = Field(default=0.03, gt=0)
    inversion_height_m: Optional[float] = None


class WeatherPresetCreate(WeatherPresetBase):
    """Schema for creating weather preset"""
    pass


class WeatherPreset(WeatherPresetCreate):
    """Full weather preset schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_builtin: bool


class ScenarioBase(BaseModel):
    """Base scenario schema"""
    name: str
    chemical_cas: str
    facility_id: UUID

    # Release parameters
    scenario_type: str  # continuous, instantaneous, time_varying, pool_evaporation, catastrophic
    release_rate_kg_s: Optional[float] = Field(None, gt=0)
    total_release_kg: Optional[float] = Field(None, gt=0)
    duration_s: Optional[float] = Field(None, gt=0)
    release_height_m: float = 0
    release_direction: str = "horizontal"
    pool_area_m2: Optional[float] = Field(None, gt=0)
    hole_diameter_m: Optional[float] = Field(None, gt=0)
    discharge_coefficient: float = Field(default=0.61, gt=0, le=1)

    # Mitigation
    secondary_containment: bool = False
    bund_area_m2: Optional[float] = Field(None, gt=0)
    water_spray: bool = False
    mitigation_factor: float = Field(default=1.0, gt=0)

    # Weather
    weather_preset_id: Optional[UUID] = None
    stability_class: Optional[str] = Field(None, pattern="^[A-F]$")
    wind_speed_ms: Optional[float] = Field(None, gt=0)
    wind_direction_deg: Optional[float] = Field(None, ge=0, lt=360)
    temperature_c: float = 25
    humidity_percent: float = Field(default=50, ge=0, le=100)
    surface_roughness_m: float = Field(default=0.03, gt=0)

    # Scenario classification
    scenario_category: Optional[str] = None

    # Computation
    model_override: Optional[str] = None
    grid_resolution_m: float = Field(default=5, gt=0)


class ScenarioCreate(ScenarioBase):
    """Schema for creating scenario"""
    pass


class ScenarioUpdate(ScenarioBase):
    """Schema for updating scenario"""
    pass


class Scenario(ScenarioCreate):
    """Full scenario schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    facility: Optional[FacilityListItem] = None
    chemical: Optional[ChemicalListItem] = None


# ============================================
# EPZ Result Schemas
# ============================================

class EPZZone(BaseModel):
    """Single EPZ zone"""
    threshold_name: str
    threshold_value_ppm: Optional[float] = None
    downwind_distance_m: Optional[float] = None
    crosswind_width_m: Optional[float] = None
    area_km2: Optional[float] = None
    affected_population: Optional[int] = None


class EPZResultCreate(BaseModel):
    """Schema for creating EPZ result (computed)"""
    scenario_id: UUID


class EPZResult(BaseModel):
    """Full EPZ result schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    computed_at: datetime

    model_used: str
    computation_time_ms: Optional[int] = None

    # Zones
    zones: List[EPZZone] = []
    total_affected_area_km2: Optional[float] = None
    estimated_affected_population: Optional[int] = None
    population_by_zone: Optional[Dict[str, int]] = None
    affected_vulnerable_facilities: Optional[List[Dict[str, Any]]] = None

    # Evacuation
    evacuation_time_min: Optional[float] = None
    shelter_in_place_recommended: Optional[bool] = None

    # Geodata
    wind_direction_deg: Optional[float] = None
    stability_class: Optional[str] = None
    contour_geojson: Optional[Dict[str, Any]] = None
    wind_rose_geojson: Optional[Dict[str, Any]] = None


class CalculationRequest(BaseModel):
    """Request to calculate EPZ"""
    scenario: ScenarioCreate
    use_wind_rose: bool = False
    wind_rose_step_deg: int = 15


class CalculationResponse(BaseModel):
    """Response from EPZ calculation"""
    result: EPZResult
    warnings: Optional[List[str]] = None


# ============================================
# Common Schemas
# ============================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int