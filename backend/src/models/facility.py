"""Facility SQLAlchemy models - SQLite compatible"""

from datetime import datetime
import uuid
import json

from sqlalchemy import Column, DateTime, Float, String, Text, Boolean, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Facility(Base):
    """Industrial facility information"""

    __tablename__ = "facilities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
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

    chemicals = relationship("FacilityChemical", back_populates="facility", cascade="all, delete-orphan")
    scenarios = relationship("EmergencyScenario", back_populates="facility", cascade="all, delete-orphan")
    vulnerable_facilities = relationship("VulnerableFacility", back_populates="facility", cascade="all, delete-orphan")


class FacilityChemical(Base):
    """Chemical inventory at a facility"""

    __tablename__ = "facility_chemicals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    chemical_cas = Column(String(20), ForeignKey("chemicals.cas_number"), nullable=False)
    max_inventory_kg = Column(Float, nullable=False)
    typical_quantity_kg = Column(Float)
    storage_condition = Column(String(50))
    containment_type = Column(String(50))
    storage_location_desc = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

    facility = relationship("Facility", back_populates="chemicals")
    chemical = relationship("Chemical", back_populates="facility_chemicals")


class VulnerableFacility(Base):
    """Vulnerable facilities near industrial sites"""

    __tablename__ = "vulnerable_facilities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    facility_id = Column(String(36), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    estimated_occupancy = Column(Integer)
    distance_m = Column(Float)
    bearing_deg = Column(Float)
    notes = Column(Text)

    facility = relationship("Facility", back_populates="vulnerable_facilities")
