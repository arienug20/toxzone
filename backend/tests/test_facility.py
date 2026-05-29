"""Tests for Facility management - minimum 5 test cases"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models.facility import Facility, FacilityChemical, VulnerableFacility
from src.models.chemical import Chemical


@pytest.fixture
def fac_db():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    Session = sessionmaker(bind=eng)
    session = Session()

    chem = Chemical(
        cas_number="7664-41-7", name="Ammonia", formula="NH3",
        molecular_weight=17.031, gas_density_ratio=0.597,
        state_at_ambient="gas", is_heavier_than_air=False,
    )
    session.add(chem)
    session.commit()
    yield session
    session.close()


class TestFacility:

    def test_create_facility(self, fac_db):
        fac = Facility(
            name="PT Test Plant", facility_type="refinery",
            latitude=-6.2, longitude=106.8, city="Jakarta",
            country="Indonesia", land_use="industrial",
        )
        fac_db.add(fac)
        fac_db.commit()

        result = fac_db.execute(select(Facility)).scalar_one()
        assert result.name == "PT Test Plant"
        assert result.latitude == -6.2

    def test_facility_auto_uuid(self, fac_db):
        fac = Facility(name="Test", latitude=-6.2, longitude=106.8)
        fac_db.add(fac)
        fac_db.commit()

        result = fac_db.execute(select(Facility)).scalar_one()
        assert len(result.id) == 36
        assert "-" in result.id

    def test_add_chemical_to_facility(self, fac_db):
        fac = Facility(name="Test Plant", latitude=-6.2, longitude=106.8)
        fac_db.add(fac)
        fac_db.commit()

        fc = FacilityChemical(
            facility_id=fac.id, chemical_cas="7664-41-7",
            max_inventory_kg=50000.0, typical_quantity_kg=30000.0,
            storage_condition="pressurized", containment_type="above_ground_tank",
        )
        fac_db.add(fc)
        fac_db.commit()

        result = fac_db.execute(select(FacilityChemical)).scalar_one()
        assert result.max_inventory_kg == 50000.0

    def test_vulnerable_facility_creation(self, fac_db):
        fac = Facility(name="Plant", latitude=-6.2, longitude=106.8)
        fac_db.add(fac)
        fac_db.commit()

        vf = VulnerableFacility(
            facility_id=fac.id, name="SDN 01 Elementary",
            type="school", latitude=-6.201, longitude=106.801,
            estimated_occupancy=300, distance_m=150.0, bearing_deg=45.0,
        )
        fac_db.add(vf)
        fac_db.commit()

        result = fac_db.execute(select(VulnerableFacility)).scalar_one()
        assert result.name == "SDN 01 Elementary"
        assert result.type == "school"

    def test_cascade_delete_facility(self, fac_db):
        fac = Facility(name="Test", latitude=-6.2, longitude=106.8)
        fac_db.add(fac)
        fac_db.flush()

        fc = FacilityChemical(
            facility_id=fac.id, chemical_cas="7664-41-7",
            max_inventory_kg=1000.0,
        )
        fac_db.add(fc)
        fac_db.commit()

        fac_db.delete(fac)
        fac_db.commit()

        remaining = fac_db.execute(select(FacilityChemical)).scalar_one_or_none()
        assert remaining is None

    def test_facility_list_filter_by_type(self, fac_db):
        fac1 = Facility(name="Refinery A", facility_type="refinery", latitude=-6.2, longitude=106.8)
        fac2 = Facility(name="Warehouse B", facility_type="warehouse", latitude=-7.0, longitude=110.0)
        fac_db.add_all([fac1, fac2])
        fac_db.commit()

        refineries = fac_db.execute(
            select(Facility).where(Facility.facility_type == "refinery")
        ).scalars().all()
        assert len(refineries) == 1
        assert refineries[0].name == "Refinery A"
