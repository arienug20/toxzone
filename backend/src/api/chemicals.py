"""Chemical API routes - sync SQLite"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from typing import List, Optional

from ..database import get_db
from ..models.chemical import Chemical
from ..schemas import (
    ChemicalCreate,
    ChemicalUpdate,
    ChemicalListItem,
    ChemicalSearchResponse,
    ChemicalDetail,
    MessageResponse,
)

router = APIRouter()


def _chemical_to_list_item(c: Chemical) -> dict:
    return {
        "cas_number": c.cas_number,
        "name": c.name,
        "formula": c.formula,
        "state_at_ambient": c.state_at_ambient,
        "hazard_class": c.hazard_class,
    }


def _chemical_to_detail(c: Chemical) -> dict:
    d = {}
    for col in c.__table__.columns:
        val = getattr(c, col.name)
        if col.name in ('synonyms', 'data_sources', 'ghs_pictograms', 'risk_phrases') and val:
            try:
                val = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                val = []
        d[col.name] = val
    return d


@router.get("/", response_model=List[ChemicalListItem])
def list_chemicals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    hazard_class: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    heavier_than_air: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = select(Chemical)
    if hazard_class:
        query = query.where(Chemical.hazard_class == hazard_class)
    if state:
        query = query.where(Chemical.state_at_ambient == state)
    if heavier_than_air is not None:
        query = query.where(Chemical.is_heavier_than_air == heavier_than_air)
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    chemicals = result.scalars().all()
    return [_chemical_to_list_item(c) for c in chemicals]


@router.get("/search", response_model=ChemicalSearchResponse)
def search_chemicals(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    search_pattern = f"%{q}%"
    query = select(Chemical).where(
        or_(
            Chemical.name.ilike(search_pattern),
            Chemical.cas_number.ilike(search_pattern),
            Chemical.formula.ilike(search_pattern),
        )
    )
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    query = query.offset(skip).limit(page_size)
    result = db.execute(query)
    chemicals = result.scalars().all()
    items = [_chemical_to_list_item(c) for c in chemicals]

    return ChemicalSearchResponse(chemicals=items, total=total, page=page, page_size=page_size)


@router.get("/{cas_number}", response_model=ChemicalDetail)
def get_chemical(cas_number: str, db: Session = Depends(get_db)):
    result = db.execute(select(Chemical).where(Chemical.cas_number == cas_number))
    chemical = result.scalar_one_or_none()
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return _chemical_to_detail(chemical)


@router.post("/", response_model=ChemicalDetail, status_code=201)
def create_chemical(chemical: ChemicalCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(Chemical).where(Chemical.cas_number == chemical.cas_number)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Chemical with this CAS number already exists")

    data = chemical.model_dump()
    # Convert lists to JSON strings
    for key in ('synonyms', 'data_sources', 'ghs_pictograms', 'risk_phrases'):
        if key in data and data[key] is not None:
            data[key] = json.dumps(data[key])

    if data.get('gas_density_ratio') and data['gas_density_ratio'] > 1.0:
        data['is_heavier_than_air'] = True
    else:
        data['is_heavier_than_air'] = False

    db_chemical = Chemical(**data)
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return _chemical_to_detail(db_chemical)


@router.put("/{cas_number}", response_model=ChemicalDetail)
def update_chemical(cas_number: str, chemical: ChemicalUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Chemical).where(Chemical.cas_number == cas_number))
    db_chemical = result.scalar_one_or_none()
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    update_data = chemical.model_dump(exclude_unset=True)
    for key in ('synonyms', 'data_sources', 'ghs_pictograms', 'risk_phrases'):
        if key in update_data and update_data[key] is not None:
            update_data[key] = json.dumps(update_data[key])

    for field, value in update_data.items():
        setattr(db_chemical, field, value)

    if 'gas_density_ratio' in update_data:
        db_chemical.is_heavier_than_air = (db_chemical.gas_density_ratio or 0) > 1.0

    db.commit()
    db.refresh(db_chemical)
    return _chemical_to_detail(db_chemical)


@router.delete("/{cas_number}", response_model=MessageResponse)
def delete_chemical(cas_number: str, db: Session = Depends(get_db)):
    result = db.execute(select(Chemical).where(Chemical.cas_number == cas_number))
    db_chemical = result.scalar_one_or_none()
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    db.delete(db_chemical)
    db.commit()
    return MessageResponse(message=f"Chemical {cas_number} deleted successfully")
