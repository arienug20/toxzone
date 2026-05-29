"""Chemical SQLAlchemy model - SQLite compatible"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
import json

from src.database import Base


class Chemical(Base):
    """Chemical database with properties and exposure thresholds"""

    __tablename__ = "chemicals"

    cas_number = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    synonyms = Column(Text)  # JSON-encoded list
    formula = Column(String(100))
    molecular_weight = Column(Float, nullable=False)
    boiling_point_c = Column(Float)
    melting_point_c = Column(Float)
    liquid_density_kg_m3 = Column(Float)
    gas_density_kg_m3 = Column(Float)
    vapor_pressure_kpa = Column(Float)
    state_at_ambient = Column(String(20))
    gas_density_ratio = Column(Float)
    is_heavier_than_air = Column(Boolean, default=False)
    solubility_g_l = Column(Float)
    lel_percent = Column(Float)
    uel_percent = Column(Float)
    hazard_class = Column(String(100))
    un_number = Column(String(20))
    ghs_pictograms = Column(Text)  # JSON
    risk_phrases = Column(Text)  # JSON
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

    # AEGL values (ppm)
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

    lc50_ppm = Column(Float)

    # Occupational Limits (ppm)
    pel_ppm = Column(Float)
    rel_ppm = Column(Float)
    tlv_twa_ppm = Column(Float)
    tlv_stel_ppm = Column(Float)
    stel_ppm = Column(Float)
    weel_ppm = Column(Float)

    # Metadata
    data_sources = Column(Text)  # JSON
    last_updated = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    # Relationships
    facility_chemicals = relationship("FacilityChemical", back_populates="chemical")
    scenarios = relationship("EmergencyScenario", back_populates="chemical")

    def get_synonyms_list(self) -> list:
        if self.synonyms:
            try:
                return json.loads(self.synonyms)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def set_synonyms_list(self, val):
        self.synonyms = json.dumps(val) if val else None

    def get_data_sources_list(self) -> list:
        if self.data_sources:
            try:
                return json.loads(self.data_sources)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def set_data_sources_list(self, val):
        self.data_sources = json.dumps(val) if val else None
