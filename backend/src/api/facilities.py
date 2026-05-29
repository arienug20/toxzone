"""Facility management API routes - sync SQLite"""

import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional

from ..database import get_db
from ..models.facility import Facility, FacilityChemical, VulnerableFacility
from ..models.chemical import Chemical
from ..schemas import (
    FacilityCreate,
    FacilityUpdate,
    FacilityListItem,
    FacilityDetail,
    FacilityChemicalCreate,
    FacilityChemicalDetail,
    VulnerableFacilityCreate,
    VulnerableFacilityDetail,
    MessageResponse,
)

router = APIRouter()


@router.get("/", response_model=List[FacilityListItem])
def list_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    facility_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = select(Facility)
    if facility_type:
        query = query.where(Facility.facility_type == facility_type)
    if city:
        query = query.where(Facility.city.ilike(f"%{city}%"))
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    facilities = result.scalars().all()
    return [FacilityListItem(
        id=f.id, name=f.name, facility_type=f.facility_type,
        city=f.city, latitude=f.latitude, longitude=f.longitude
    ) for f in facilities]


@router.get("/{facility_id}", response_model=FacilityDetail)
def get_facility(facility_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return FacilityDetail.model_validate(facility)


@router.post("/", response_model=FacilityDetail, status_code=201)
def create_facility(facility: FacilityCreate, db: Session = Depends(get_db)):
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return FacilityDetail.model_validate(db_facility)


@router.put("/{facility_id}", response_model=FacilityDetail)
def update_facility(facility_id: str, facility: FacilityUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Facility).where(Facility.id == facility_id))
    db_facility = result.scalar_one_or_none()
    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    update_data = facility.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_facility, field, value)
    db.commit()
    db.refresh(db_facility)
    return FacilityDetail.model_validate(db_facility)


@router.delete("/{facility_id}", response_model=MessageResponse)
def delete_facility(facility_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(Facility).where(Facility.id == facility_id))
    db_facility = result.scalar_one_or_none()
    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    db.delete(db_facility)
    db.commit()
    return MessageResponse(message=f"Facility {facility_id} deleted successfully")


# Facility Chemical Inventory

@router.get("/{facility_id}/chemicals", response_model=List[FacilityChemicalDetail])
def list_facility_chemicals(facility_id: str, db: Session = Depends(get_db)):
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    result = db.execute(select(FacilityChemical).where(FacilityChemical.facility_id == facility_id))
    return [FacilityChemicalDetail.model_validate(fc) for fc in result.scalars().all()]


@router.post("/{facility_id}/chemicals", response_model=FacilityChemicalDetail, status_code=201)
def add_facility_chemical(facility_id: str, chemical: FacilityChemicalCreate, db: Session = Depends(get_db)):
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    chem = db.execute(select(Chemical).where(Chemical.cas_number == chemical.chemical_cas)).scalar_one_or_none()
    if not chem:
        raise HTTPException(status_code=404, detail="Chemical not found")
    db_fc = FacilityChemical(facility_id=facility_id, **chemical.model_dump())
    db.add(db_fc)
    db.commit()
    db.refresh(db_fc)
    return FacilityChemicalDetail.model_validate(db_fc)


@router.delete("/{facility_id}/chemicals/{chemical_id}", response_model=MessageResponse)
def remove_facility_chemical(facility_id: str, chemical_id: str, db: Session = Depends(get_db)):
    result = db.execute(select(FacilityChemical).where(
        FacilityChemical.id == chemical_id, FacilityChemical.facility_id == facility_id
    ))
    db_fc = result.scalar_one_or_none()
    if not db_fc:
        raise HTTPException(status_code=404, detail="Facility chemical not found")
    db.delete(db_fc)
    db.commit()
    return MessageResponse(message="Chemical removed from facility inventory")


# Vulnerable Facilities

@router.get("/{facility_id}/vulnerable", response_model=List[VulnerableFacilityDetail])
def list_vulnerable_facilities(facility_id: str, db: Session = Depends(get_db)):
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    result = db.execute(select(VulnerableFacility).where(VulnerableFacility.facility_id == facility_id))
    return [VulnerableFacilityDetail.model_validate(vf) for vf in result.scalars().all()]


@router.post("/{facility_id}/vulnerable", response_model=VulnerableFacilityDetail, status_code=201)
def add_vulnerable_facility(facility_id: str, vuln: VulnerableFacilityCreate, db: Session = Depends(get_db)):
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")

    lat1, lon1 = math.radians(fac.latitude), math.radians(fac.longitude)
    lat2, lon2 = math.radians(vuln.latitude), math.radians(vuln.longitude)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    distance_m = 2 * 6371000 * math.asin(math.sqrt(a))
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    db_vf = VulnerableFacility(
        facility_id=facility_id, name=vuln.name, type=vuln.type,
        latitude=vuln.latitude, longitude=vuln.longitude,
        estimated_occupancy=vuln.estimated_occupancy,
        distance_m=distance_m, bearing_deg=bearing, notes=vuln.notes,
    )
    db.add(db_vf)
    db.commit()
    db.refresh(db_vf)
    return VulnerableFacilityDetail.model_validate(db_vf)
