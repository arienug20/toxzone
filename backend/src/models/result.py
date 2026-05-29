"""Result SQLAlchemy models - SQLite compatible"""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class EPZResultDB(Base):
    """EPZ calculation results"""

    __tablename__ = "epz_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(36), ForeignKey("emergency_scenarios.id", ondelete="CASCADE"), nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)

    model_used = Column(String(50), nullable=False)
    computation_time_ms = Column(Integer)

    erpg1_downwind_m = Column(Float)
    erpg2_downwind_m = Column(Float)
    erpg3_downwind_m = Column(Float)
    idlh_downwind_m = Column(Float)
    aegl1_60min_downwind_m = Column(Float)
    aegl2_60min_downwind_m = Column(Float)
    aegl3_60min_downwind_m = Column(Float)

    erpg1_area_km2 = Column(Float)
    erpg2_area_km2 = Column(Float)
    erpg3_area_km2 = Column(Float)
    total_affected_area_km2 = Column(Float)

    estimated_affected_population = Column(Integer)
    population_by_zone = Column(Text)  # JSON
    affected_vulnerable_facilities = Column(Text)  # JSON

    evacuation_time_min = Column(Float)
    shelter_in_place_recommended = Column(Boolean)

    wind_direction_deg = Column(Float)
    stability_class = Column(String(5))
    concentration_grid = Column(Text)  # JSON
    contour_geojson = Column(Text)  # JSON
    wind_rose_geojson = Column(Text)  # JSON

    scenario = relationship("EmergencyScenario", back_populates="results")


class Export(Base):
    """Saved map exports"""

    __tablename__ = "exports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("epz_results.id", ondelete="CASCADE"), nullable=False)
    format = Column(String(20), nullable=False)
    content_type = Column(String(100))
    file_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
