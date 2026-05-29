"""Result SQLAlchemy models"""

from typing import Optional
from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...database import Base


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


class Export(Base):
    """Saved map exports"""

    __tablename__ = "exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("epz_results.id", ondelete="CASCADE"), nullable=False)
    format = Column(String(20), nullable=False)  # kml, geojson, pdf, png
    content_type = Column(String(100))
    file_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)