"""SQLAlchemy models for ToxZone"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Chemical(Base):
    """Chemical database with properties and exposure thresholds"""

    __tablename__ = "chemicals"

    cas_number = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    synonyms = Column(ARRAY(String))
    formula = Column(String(100))
    molecular_weight = Column(Float, nullable=False)
    boiling_point_c = Column(Float)
    melting_point_c = Column(Float)
    liquid_density_kg_m3 = Column(Float)
    gas_density_kg_m3 = Column(Float)
    vapor_pressure_kpa = Column(Float)
    state_at_ambient = Column(String(20))  # solid/liquid/gas
    gas_density_ratio = Column(Float)  # vs air (1.0 = same as air)
    is_heavier_than_air = Column(Boolean, nullable=False, default=False)
    solubility_g_l = Column(Float)
    lel_percent = Column(Float)
    uel_percent = Column(Float)
    hazard_class = Column(String(100))
    un_number = Column(String(20))
    ghs_pictograms = Column(ARRAY(String))
    risk_phrases = Column(ARRAY(String))
    first_aid = Column(Text)
    fire_fighting = Column(Text)
    ppe_requirements = Column(Text)

    # Exposure Thresholds (ppm unless noted)
    erpg_1_ppm = Column(Float)
    erpg_1_mg_m3 = Column(Float)
    erpg_2_ppm = Column(Float)
    erpg_2_mg_m3 = Column(Float)
    erpg_3_ppm = Column(Float)
    erpg_3_mg_m3 = Column(Float)
    idlh_ppm = Column(Float)
    idlh_mg_m3 = Column(Float)

    # AEGL values (ppm) — 4 time frames each for 3 severity levels
    aegl_1_10min_ppm = Column(Float)
    aegl_1_30min_ppm = Column(Float)
    aegl_1_60min_ppm = Column(Float)
    aegl_1_4hr_ppm = Column(Float)
    aegl_2_10min_ppm = Column(Float)
    aegl_2_30min_ppm = Column(Float)
    aegl_2_60min_ppm = Column(Float)
    aegl_2_4hr_ppm = Column(Float)
    aegl_3_10min_ppm = Column(Float)
    aegl_3_30min_ppm = Column(Float)
    aegl_3_60min_ppm = Column(Float)
    aegl_3_4hr_ppm = Column(Float)

    # Lethality
    lc50_ppm = Column(Float)

    # Occupational Limits (ppm)
    pel_ppm = Column(Float)
    rel_ppm = Column(Float)
    tlv_twa_ppm = Column(Float)
    tlv_stel_ppm = Column(Float)
    stel_ppm = Column(Float)
    weel_ppm = Column(Float)

    # Metadata
    data_sources = Column(ARRAY(String))
    last_updated = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    # Relationships
    facility_chemicals = relationship("FacilityChemical", back_populates="chemical")
    scenarios = relationship("EmergencyScenario", back_populates="chemical")

    __table_args__ = (
        CheckConstraint("gas_density_ratio > 0", name="check_gas_density_ratio_positive"),
    )


class Facility(Base):
    """Industrial facility information"""

    __tablename__ = "facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255))
    facility_type = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float)
    address = Column(Text)
    city = Column(String(100))
    province = Column(String(100))
    country = Column(String(100), default="Indonesia")
    land_use = Column(String(50), default="industrial")
    default_pop_density = Column(Float, default=1000)
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    emergency_contact_name_2 = Column(String(255))
    emergency_contact_phone_2 = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chemicals = relationship("FacilityChemical", back_populates="facility", cascade="all, delete-orphan")
    scenarios = relationship("EmergencyScenario", back_populates="facility", cascade="all, delete-orphan")
    vulnerable_facilities = relationship("VulnerableFacility", back_populates="facility", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="check_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="check_longitude_range"),
        Index("idx_facilities_location", "latitude", "longitude"),
    )


class FacilityChemical(Base):
    """Chemical inventory at a facility"""

    __tablename__ = "facility_chemicals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    chemical_cas = Column(String(20), ForeignKey("chemicals.cas_number"), nullable=False)
    max_inventory_kg = Column(Float, nullable=False)
    typical_quantity_kg = Column(Float)
    storage_condition = Column(String(50))  # ambient, refrigerated, pressurized, cryogenic
    containment_type = Column(String(50))  # above_ground_tank, underground_tank, cylinder, drum, ibc, pipeline, railcar, isotainer
    storage_location_desc = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="chemicals")
    chemical = relationship("Chemical", back_populates="facility_chemicals")

    __table_args__ = (
        CheckConstraint("max_inventory_kg > 0", name="check_max_inventory_positive"),
    )


class WeatherPreset(Base):
    """Weather configuration presets"""

    __tablename__ = "weather_presets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    stability_class = Column(String(5), nullable=False)  # A-F
    wind_speed_ms = Column(Float, nullable=False)
    wind_direction_deg = Column(Float, default=0)
    temperature_c = Column(Float, default=25)
    humidity_percent = Column(Float, default=50)
    surface_roughness_m = Column(Float, default=0.03)
    inversion_height_m = Column(Float)
    is_builtin = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint("stability_class IN ('A','B','C','D','E','F')", name="check_stability_class"),
    )


class EmergencyScenario(Base):
    """Emergency release scenarios"""

    __tablename__ = "emergency_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    chemical_cas = Column(String(20), ForeignKey("chemicals.cas_number"), nullable=False)

    # Release parameters
    scenario_type = Column(String(50), nullable=False)  # continuous, instantaneous, time_varying, pool_evaporation, catastrophic
    release_rate_kg_s = Column(Float)
    total_release_kg = Column(Float)
    duration_s = Column(Float)
    release_height_m = Column(Float, default=0)
    release_direction = Column(String(20), default="horizontal")
    pool_area_m2 = Column(Float)
    hole_diameter_m = Column(Float)
    discharge_coefficient = Column(Float, default=0.61)

    # Mitigation
    secondary_containment = Column(Boolean, default=False)
    bund_area_m2 = Column(Float)
    water_spray = Column(Boolean, default=False)
    mitigation_factor = Column(Float, default=1.0)

    # Weather
    weather_preset_id = Column(UUID(as_uuid=True), ForeignKey("weather_presets.id"))
    stability_class = Column(String(5))
    wind_speed_ms = Column(Float)
    wind_direction_deg = Column(Float)
    temperature_c = Column(Float, default=25)
    humidity_percent = Column(Float, default=50)
    surface_roughness_m = Column(Float, default=0.03)

    # Scenario classification
    scenario_category = Column(String(50))  # worst_case, alternative, what_if, regulatory

    # Computation
    model_override = Column(String(50))  # gaussian, heavy_gas, auto
    grid_resolution_m = Column(Float, default=5)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="scenarios")
    chemical = relationship("Chemical", back_populates="scenarios")
    results = relationship("EPZResult", back_populates="scenario", cascade="all, delete-orphan")


class EPZResult(Base):
    """EPZ calculation results"""

    __tablename__ = "epz_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("emergency_scenarios.id", ondelete="CASCADE"), nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)

    # Model info
    model_used = Column(String(50), nullable=False)
    computation_time_ms = Column(Integer)

    # Zone radii (meters)
    erpg1_downwind_m = Column(Float)
    erpg2_downwind_m = Column(Float)
    erpg3_downwind_m = Column(Float)
    idlh_downwind_m = Column(Float)
    aegl1_60min_downwind_m = Column(Float)
    aegl2_60min_downwind_m = Column(Float)
    aegl3_60min_downwind_m = Column(Float)

    # Zone areas (km²)
    erpg1_area_km2 = Column(Float)
    erpg2_area_km2 = Column(Float)
    erpg3_area_km2 = Column(Float)
    total_affected_area_km2 = Column(Float)

    # Population impact
    estimated_affected_population = Column(Integer)
    population_by_zone = Column(JSON)  # {"erpg1": N, "erpg2": N, "erpg3": N}
    affected_vulnerable_facilities = Column(JSON)

    # Evacuation
    evacuation_time_min = Column(Float)
    shelter_in_place_recommended = Column(Boolean)

    # Geodata
    wind_direction_deg = Column(Float)
    stability_class = Column(String(5))
    concentration_grid = Column(JSON)  # serialized 2D array with metadata
    contour_geojson = Column(JSON)  # GeoJSON FeatureCollection
    wind_rose_geojson = Column(JSON)

    # Relationships
    scenario = relationship("EmergencyScenario", back_populates="results")


class VulnerableFacility(Base):
    """Vulnerable facilities near industrial sites"""

    __tablename__ = "vulnerable_facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # school, hospital, nursing_home, residential, daycare, mosque, church, market
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    estimated_occupancy = Column(Integer)
    distance_m = Column(Float)
    bearing_deg = Column(Float)
    notes = Column(Text)

    # Relationships
    facility = relationship("Facility", back_populates="vulnerable_facilities")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="check_vuln_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="check_vuln_longitude_range"),
    )


class Export(Base):
    """Saved map exports"""

    __tablename__ = "exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("epz_results.id", ondelete="CASCADE"), nullable=False)
    format = Column(String(20), nullable=False)  # kml, geojson, pdf, png
    content_type = Column(String(100))
    file_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)