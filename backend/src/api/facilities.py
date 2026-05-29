"""Facility management API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid

from ..database import get_db
from ..models.facility import Facility, FacilityChemical, VulnerableFacility
from ..models.chemical import Chemical
from ..schemas import (
    Facility,
    FacilityCreate,
    FacilityUpdate,
    FacilityListItem,
    FacilityChemical,
    FacilityChemicalCreate,
    VulnerableFacility,
    VulnerableFacilityCreate,
    MessageResponse,
)

router = APIRouter()


@router.get("/", response_model=List[FacilityListItem])
async def list_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    facility_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List facilities with optional filters"""
    query = select(Facility)

    if facility_type:
        query = query.where(Facility.facility_type == facility_type)
    if city:
        query = query.where(Facility.city.ilike(f"%{city}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    facilities = result.scalars().all()

    return [
        FacilityListItem(
            id=f.id,
            name=f.name,
            facility_type=f.facility_type,
            city=f.city,
            latitude=f.latitude,
            longitude=f.longitude,
        )
        for f in facilities
    ]


@router.get("/{facility_id}", response_model=Facility)
async def get_facility(
    facility_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get facility by ID"""
    query = select(Facility).where(Facility.id == facility_id)
    result = await db.execute(query)
    facility = result.scalar_one_or_none()

    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    return Facility(
        id=facility.id,
        name=facility.name,
        owner=facility.owner,
        facility_type=facility.facility_type,
        latitude=facility.latitude,
        longitude=facility.longitude,
        elevation_m=facility.elevation_m,
        address=facility.address,
        city=facility.city,
        province=facility.province,
        country=facility.country,
        land_use=facility.land_use,
        default_pop_density=facility.default_pop_density,
        emergency_contact_name=facility.emergency_contact_name,
        emergency_contact_phone=facility.emergency_contact_phone,
        emergency_contact_name_2=facility.emergency_contact_name_2,
        emergency_contact_phone_2=facility.emergency_contact_phone_2,
        created_at=facility.created_at,
        updated_at=facility.updated_at,
    )


@router.post("/", response_model=Facility, status_code=201)
async def create_facility(
    facility: FacilityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new facility"""
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    await db.commit()
    await db.refresh(db_facility)

    return Facility(
        id=db_facility.id,
        name=db_facility.name,
        owner=db_facility.owner,
        facility_type=db_facility.facility_type,
        latitude=db_facility.latitude,
        longitude=db_facility.longitude,
        elevation_m=db_facility.elevation_m,
        address=db_facility.address,
        city=db_facility.city,
        province=db_facility.province,
        country=db_facility.country,
        land_use=db_facility.land_use,
        default_pop_density=db_facility.default_pop_density,
        emergency_contact_name=db_facility.emergency_contact_name,
        emergency_contact_phone=db_facility.emergency_contact_phone,
        emergency_contact_name_2=db_facility.emergency_contact_name_2,
        emergency_contact_phone_2=db_facility.emergency_contact_phone_2,
        created_at=db_facility.created_at,
        updated_at=db_facility.updated_at,
    )


@router.put("/{facility_id}", response_model=Facility)
async def update_facility(
    facility_id: uuid.UUID,
    facility: FacilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update facility"""
    query = select(Facility).where(Facility.id == facility_id)
    result = await db.execute(query)
    db_facility = result.scalar_one_or_none()

    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    update_data = facility.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_facility, field, value)

    await db.commit()
    await db.refresh(db_facility)

    return await get_facility(facility_id, db)


@router.delete("/{facility_id}", response_model=MessageResponse)
async def delete_facility(
    facility_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete facility (cascades to chemicals, scenarios, etc.)"""
    query = select(Facility).where(Facility.id == facility_id)
    result = await db.execute(query)
    db_facility = result.scalar_one_or_none()

    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    await db.delete(db_facility)
    await db.commit()

    return MessageResponse(message=f"Facility {facility_id} deleted successfully")


# Facility Chemical Inventory Routes


@router.get("/{facility_id}/chemicals", response_model=List[FacilityChemical])
async def list_facility_chemicals(
    facility_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List chemicals at a facility"""
    # Verify facility exists
    facility_query = select(Facility).where(Facility.id == facility_id)
    facility_result = await db.execute(facility_query)
    if not facility_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Facility not found")

    # Get facility chemicals
    query = (
        select(FacilityChemical)
        .where(FacilityChemical.facility_id == facility_id)
    )
    result = await db.execute(query)
    chemicals = result.scalars().all()

    # Fetch chemical details
    response = []
    for fc in chemicals:
        # Get chemical info
        chem_query = select(Chemical).where(Chemical.cas_number == fc.chemical_cas)
        chem_result = await db.execute(chem_query)
        chemical = chem_result.scalar_one_or_none()

        chemical_info = None
        if chemical:
            chemical_info = {
                "cas_number": chemical.cas_number,
                "name": chemical.name,
                "formula": chemical.formula,
                "state_at_ambient": chemical.state_at_ambient,
                "hazard_class": chemical.hazard_class,
            }

        response.append(
            FacilityChemical(
                id=fc.id,
                facility_id=fc.facility_id,
                chemical_cas=fc.chemical_cas,
                max_inventory_kg=fc.max_inventory_kg,
                typical_quantity_kg=fc.typical_quantity_kg,
                storage_condition=fc.storage_condition,
                containment_type=fc.containment_type,
                storage_location_desc=fc.storage_location_desc,
                last_updated=fc.last_updated,
                chemical=chemical_info,
            )
        )

    return response


@router.post("/{facility_id}/chemicals", response_model=FacilityChemical, status_code=201)
async def add_facility_chemical(
    facility_id: uuid.UUID,
    chemical: FacilityChemicalCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add chemical to facility inventory"""
    # Verify facility exists
    facility_query = select(Facility).where(Facility.id == facility_id)
    facility_result = await db.execute(facility_query)
    if not facility_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Facility not found")

    # Verify chemical exists
    chem_query = select(Chemical).where(Chemical.cas_number == chemical.chemical_cas)
    chem_result = await db.execute(chem_query)
    if not chem_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Check if already exists
    existing_query = select(FacilityChemical).where(
        FacilityChemical.facility_id == facility_id,
        FacilityChemical.chemical_cas == chemical.chemical_cas,
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Chemical already exists in facility inventory"
        )

    # Create facility chemical
    db_fc = FacilityChemical(
        facility_id=facility_id,
        **chemical.model_dump()
    )
    db.add(db_fc)
    await db.commit()
    await db.refresh(db_fc)

    return FacilityChemical(
        id=db_fc.id,
        facility_id=db_fc.facility_id,
        chemical_cas=db_fc.chemical_cas,
        max_inventory_kg=db_fc.max_inventory_kg,
        typical_quantity_kg=db_fc.typical_quantity_kg,
        storage_condition=db_fc.storage_condition,
        containment_type=db_fc.containment_type,
        storage_location_desc=db_fc.storage_location_desc,
        last_updated=db_fc.last_updated,
    )


@router.delete("/{facility_id}/chemicals/{chemical_id}", response_model=MessageResponse)
async def remove_facility_chemical(
    facility_id: uuid.UUID,
    chemical_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove chemical from facility inventory"""
    query = select(FacilityChemical).where(
        FacilityChemical.id == chemical_id,
        FacilityChemical.facility_id == facility_id,
    )
    result = await db.execute(query)
    db_fc = result.scalar_one_or_none()

    if not db_fc:
        raise HTTPException(status_code=404, detail="Facility chemical not found")

    await db.delete(db_fc)
    await db.commit()

    return MessageResponse(message="Chemical removed from facility inventory")


# Vulnerable Facilities Routes


@router.get("/{facility_id}/vulnerable", response_model=List[VulnerableFacility])
async def list_vulnerable_facilities(
    facility_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List vulnerable facilities near a facility"""
    # Verify facility exists
    facility_query = select(Facility).where(Facility.id == facility_id)
    facility_result = await db.execute(facility_query)
    if not facility_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Facility not found")

    query = select(VulnerableFacility).where(
        VulnerableFacility.facility_id == facility_id
    )
    result = await db.execute(query)
    vuln_facilities = result.scalars().all()

    return [
        VulnerableFacility(
            id=vf.id,
            facility_id=vf.facility_id,
            name=vf.name,
            type=vf.type,
            latitude=vf.latitude,
            longitude=vf.longitude,
            estimated_occupancy=vf.estimated_occupancy,
            distance_m=vf.distance_m,
            bearing_deg=vf.bearing_deg,
            notes=vf.notes,
        )
        for vf in vuln_facilities
    ]


@router.post("/{facility_id}/vulnerable", response_model=VulnerableFacility, status_code=201)
async def add_vulnerable_facility(
    facility_id: uuid.UUID,
    vuln_facility: VulnerableFacilityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add vulnerable facility"""
    # Verify parent facility exists
    facility_query = select(Facility).where(Facility.id == facility_id)
    facility_result = await db.execute(facility_query)
    facility = facility_result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    # Calculate distance and bearing
    import math
    lat1 = math.radians(facility.latitude)
    lon1 = math.radians(facility.longitude)
    lat2 = math.radians(vuln_facility.latitude)
    lon2 = math.radians(vuln_facility.longitude)

    # Distance (Haversine formula, simplified)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance_m = c * 6371000

    # Bearing
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360

    db_vf = VulnerableFacility(
        facility_id=facility_id,
        name=vuln_facility.name,
        type=vuln_facility.type,
        latitude=vuln_facility.latitude,
        longitude=vuln_facility.longitude,
        estimated_occupancy=vuln_facility.estimated_occupancy,
        distance_m=distance_m,
        bearing_deg=bearing,
        notes=vuln_facility.notes,
    )
    db.add(db_vf)
    await db.commit()
    await db.refresh(db_vf)

    return VulnerableFacility(
        id=db_vf.id,
        facility_id=db_vf.facility_id,
        name=db_vf.name,
        type=db_vf.type,
        latitude=db_vf.latitude,
        longitude=db_vf.longitude,
        estimated_occupancy=db_vf.estimated_occupancy,
        distance_m=db_vf.distance_m,
        bearing_deg=db_vf.bearing_deg,
        notes=db_vf.notes,
    )