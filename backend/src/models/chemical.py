"""Chemical SQLAlchemy model"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Float,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from ...database import Base


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