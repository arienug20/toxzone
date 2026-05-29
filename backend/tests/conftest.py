"""Test fixtures and conftest for ToxZone tests"""

import sys
from pathlib import Path

# Add backend root to path so we can `import src.*`
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.chemical import Chemical
from src.models.facility import Facility, FacilityChemical, VulnerableFacility
from src.models.scenario import EmergencyScenario, WeatherPreset
from src.models.result import EPZResultDB


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_chemicals(db_session):
    chemicals = [
        Chemical(
            cas_number="7664-41-7", name="Ammonia", formula="NH3", molecular_weight=17.031,
            boiling_point_c=-33.34, gas_density_kg_m3=0.73, gas_density_ratio=0.597,
            state_at_ambient="gas", is_heavier_than_air=False,
            hazard_class="2.3 (Toxic Gas)", un_number="UN1005",
            erpg_1_ppm=25.0, erpg_2_ppm=200.0, erpg_3_ppm=1000.0,
            idlh_ppm=300.0, pel_ppm=50.0,
            aegl_1_10min_ppm=30.0, aegl_1_60min_ppm=10.0,
            aegl_2_10min_ppm=560.0, aegl_2_60min_ppm=160.0,
            aegl_3_10min_ppm=2200.0, aegl_3_60min_ppm=1100.0,
            lel_percent=15.0, uel_percent=28.0,
        ),
        Chemical(
            cas_number="7782-50-5", name="Chlorine", formula="Cl2", molecular_weight=70.906,
            boiling_point_c=-34.0, gas_density_kg_m3=2.95, gas_density_ratio=2.41,
            state_at_ambient="gas", is_heavier_than_air=True,
            hazard_class="2.3 (Toxic Gas)", un_number="UN1017",
            erpg_1_ppm=1.0, erpg_2_ppm=3.0, erpg_3_ppm=20.0,
            idlh_ppm=10.0, pel_ppm=1.0, tlv_twa_ppm=0.5,
            aegl_1_10min_ppm=0.5, aegl_1_60min_ppm=0.5,
            aegl_2_10min_ppm=2.0, aegl_2_60min_ppm=1.0,
            aegl_3_10min_ppm=10.0, aegl_3_60min_ppm=5.0,
        ),
        Chemical(
            cas_number="7647-01-0", name="Hydrogen Chloride", formula="HCl", molecular_weight=36.461,
            boiling_point_c=-85.05, gas_density_kg_m3=1.49, gas_density_ratio=1.22,
            state_at_ambient="gas", is_heavier_than_air=True,
            hazard_class="8 (Corrosive)", un_number="UN1050",
            erpg_1_ppm=3.0, erpg_2_ppm=20.0, erpg_3_ppm=100.0,
            idlh_ppm=50.0, pel_ppm=5.0,
        ),
        Chemical(
            cas_number="71-43-2", name="Benzene", formula="C6H6", molecular_weight=78.114,
            boiling_point_c=80.1, liquid_density_kg_m3=876.5, vapor_pressure_kpa=10.0,
            gas_density_ratio=2.7, state_at_ambient="liquid", is_heavier_than_air=True,
            hazard_class="3 (Flammable Liquid)", un_number="UN1114",
            erpg_1_ppm=50.0, erpg_2_ppm=150.0, erpg_3_ppm=1000.0,
            idlh_ppm=500.0, pel_ppm=1.0, lel_percent=1.2, uel_percent=7.8,
        ),
        Chemical(
            cas_number="630-08-0", name="Carbon Monoxide", formula="CO", molecular_weight=28.01,
            boiling_point_c=-191.5, gas_density_kg_m3=1.15, gas_density_ratio=0.94,
            state_at_ambient="gas", is_heavier_than_air=False,
            hazard_class="2.3 (Toxic Gas)", un_number="UN1016",
            erpg_1_ppm=50.0, erpg_2_ppm=200.0, erpg_3_ppm=1000.0,
            idlh_ppm=1200.0, pel_ppm=50.0, lel_percent=12.5, uel_percent=74.0,
        ),
        Chemical(
            cas_number="7783-06-4", name="Hydrogen Sulfide", formula="H2S", molecular_weight=34.08,
            boiling_point_c=-60.0, gas_density_kg_m3=1.36, gas_density_ratio=1.17,
            state_at_ambient="gas", is_heavier_than_air=True,
            hazard_class="2.3 (Toxic Gas)", un_number="UN1053",
            erpg_1_ppm=0.1, erpg_2_ppm=30.0, erpg_3_ppm=100.0,
            idlh_ppm=50.0, pel_ppm=20.0, lel_percent=4.3, uel_percent=46.0,
        ),
    ]
    for c in chemicals:
        db_session.add(c)
    db_session.commit()
    return chemicals
