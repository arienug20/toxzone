"""Tests for Chemical Service - minimum 5 test cases"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
import json
from sqlalchemy import select
from src.models.chemical import Chemical


class TestChemicalService:

    def test_create_chemical(self, db_session):
        chem = Chemical(
            cas_number="7664-41-7", name="Ammonia", formula="NH3",
            molecular_weight=17.031, gas_density_ratio=0.597,
            state_at_ambient="gas", is_heavier_than_air=False,
            erpg_1_ppm=25.0, erpg_2_ppm=200.0, erpg_3_ppm=1000.0,
            idlh_ppm=300.0,
        )
        db_session.add(chem)
        db_session.commit()

        result = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "7664-41-7")
        ).scalar_one()
        assert result.name == "Ammonia"
        assert result.molecular_weight == 17.031

    def test_query_chemical_by_name(self, db_session, sample_chemicals):
        results = db_session.execute(
            select(Chemical).where(Chemical.name.ilike("%Chlor%"))
        ).scalars().all()
        assert len(results) >= 1
        assert any(c.name == "Chlorine" for c in results)

    def test_heavier_than_air_flag(self, db_session, sample_chemicals):
        chlorine = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "7782-50-5")
        ).scalar_one()
        assert chlorine.is_heavier_than_air is True

        ammonia = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "7664-41-7")
        ).scalar_one()
        assert ammonia.is_heavier_than_air is False

    def test_update_chemical(self, db_session, sample_chemicals):
        chem = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "7664-41-7")
        ).scalar_one()
        chem.notes = "Updated test note"
        db_session.commit()

        updated = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "7664-41-7")
        ).scalar_one()
        assert updated.notes == "Updated test note"

    def test_delete_chemical(self, db_session, sample_chemicals):
        chem = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "630-08-0")
        ).scalar_one()
        db_session.delete(chem)
        db_session.commit()

        result = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "630-08-0")
        ).scalar_one_or_none()
        assert result is None

    def test_json_synonyms(self, db_session):
        chem = Chemical(
            cas_number="9999-99-9", name="Test Chemical",
            molecular_weight=50.0,
            synonyms=json.dumps(["Alias 1", "Alias 2"]),
        )
        db_session.add(chem)
        db_session.commit()

        result = db_session.execute(
            select(Chemical).where(Chemical.cas_number == "9999-99-9")
        ).scalar_one()
        assert result.get_synonyms_list() == ["Alias 1", "Alias 2"]

    def test_all_sample_chemicals_have_thresholds(self, db_session, sample_chemicals):
        for chem in sample_chemicals:
            has_threshold = any([
                chem.erpg_1_ppm, chem.erpg_2_ppm, chem.erpg_3_ppm, chem.idlh_ppm
            ])
            assert has_threshold, f"{chem.name} has no thresholds"
