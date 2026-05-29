"""Scenario SQLAlchemy models"""

from typing import Optional
from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...database import Base


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