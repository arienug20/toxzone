"""Facility SQLAlchemy models"""

from typing import Optional
from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...database import Base


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