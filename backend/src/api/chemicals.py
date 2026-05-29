"""API package"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional

from ..database import get_db
from ..models.chemical import Chemical
from ..schemas import (
    Chemical,
    ChemicalCreate,
    ChemicalUpdate,
    ChemicalListItem,
    ChemicalSearchResponse,
    MessageResponse,
)

router = APIRouter()


@router.get("/", response_model=List[ChemicalListItem])
async def list_chemicals(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    hazard_class: Optional[str] = Query(None, description="Filter by hazard class"),
    state: Optional[str] = Query(None, description="Filter by state (solid/liquid/gas)"),
    heavier_than_air: Optional[bool] = Query(None, description="Filter by heavier-than-air"),
    db: AsyncSession = Depends(get_db),
):
    """List chemicals with optional filters"""
    query = select(Chemical)

    # Apply filters
    if hazard_class:
        query = query.where(Chemical.hazard_class == hazard_class)
    if state:
        query = query.where(Chemical.state_at_ambient == state)
    if heavier_than_air is not None:
        query = query.where(Chemical.is_heavier_than_air == heavier_than_air)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    chemicals = result.scalars().all()

    return [
        ChemicalListItem(
            cas_number=c.cas_number,
            name=c.name,
            formula=c.formula,
            state_at_ambient=c.state_at_ambient,
            hazard_class=c.hazard_class,
        )
        for c in chemicals
    ]


@router.get("/search", response_model=ChemicalSearchResponse)
async def search_chemicals(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """Search chemicals by name, synonyms, CAS, or formula"""
    skip = (page - 1) * page_size

    # Build search query (ILIKE for case-insensitive partial match)
    search_pattern = f"%{q}%"
    query = select(Chemical).where(
        or_(
            Chemical.name.ilike(search_pattern),
            Chemical.cas_number.ilike(search_pattern),
            Chemical.formula.ilike(search_pattern),
        )
    )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset(skip).limit(page_size)
    result = await db.execute(query)
    chemicals = result.scalars().all()

    items = [
        ChemicalListItem(
            cas_number=c.cas_number,
            name=c.name,
            formula=c.formula,
            state_at_ambient=c.state_at_ambient,
            hazard_class=c.hazard_class,
        )
        for c in chemicals
    ]

    return ChemicalSearchResponse(
        chemicals=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{cas_number}", response_model=Chemical)
async def get_chemical(
    cas_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Get chemical by CAS number"""
    query = select(Chemical).where(Chemical.cas_number == cas_number)
    result = await db.execute(query)
    chemical = result.scalar_one_or_none()

    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    return Chemical(
        cas_number=chemical.cas_number,
        name=chemical.name,
        synonyms=chemical.synonyms,
        formula=chemical.formula,
        molecular_weight=chemical.molecular_weight,
        boiling_point_c=chemical.boiling_point_c,
        melting_point_c=chemical.melting_point_c,
        liquid_density_kg_m3=chemical.liquid_density_kg_m3,
        gas_density_kg_m3=chemical.gas_density_kg_m3,
        vapor_pressure_kpa=chemical.vapor_pressure_kpa,
        state_at_ambient=chemical.state_at_ambient,
        gas_density_ratio=chemical.gas_density_ratio,
        is_heavier_than_air=chemical.is_heavier_than_air,
        solubility_g_l=chemical.solubility_g_l,
        lel_percent=chemical.lel_percent,
        uel_percent=chemical.uel_percent,
        hazard_class=chemical.hazard_class,
        un_number=chemical.un_number,
        ghs_pictograms=chemical.ghs_pictograms,
        risk_phrases=chemical.risk_phrases,
        first_aid=chemical.first_aid,
        fire_fighting=chemical.fire_fighting,
        ppe_requirements=chemical.ppe_requirements,
        erpg_1_ppm=chemical.erpg_1_ppm,
        erpg_1_mg_m3=chemical.erpg_1_mg_m3,
        erpg_2_ppm=chemical.erpg_2_ppm,
        erpg_2_mg_m3=chemical.erpg_2_mg_m3,
        erpg_3_ppm=chemical.erpg_3_ppm,
        erpg_3_mg_m3=chemical.erpg_3_mg_m3,
        idlh_ppm=chemical.idlh_ppm,
        idlh_mg_m3=chemical.idlh_mg_m3,
        aegl_1_10min_ppm=chemical.aegl_1_10min_ppm,
        aegl_1_30min_ppm=chemical.aegl_1_30min_ppm,
        aegl_1_60min_ppm=chemical.aegl_1_60min_ppm,
        aegl_1_4hr_ppm=chemical.aegl_1_4hr_ppm,
        aegl_2_10min_ppm=chemical.aegl_2_10min_ppm,
        aegl_2_30min_ppm=chemical.aegl_2_30min_ppm,
        aegl_2_60min_ppm=chemical.aegl_2_60min_ppm,
        aegl_2_4hr_ppm=chemical.aegl_2_4hr_ppm,
        aegl_3_10min_ppm=chemical.aegl_3_10min_ppm,
        aegl_3_30min_ppm=chemical.aegl_3_30min_ppm,
        aegl_3_60min_ppm=chemical.aegl_3_60min_ppm,
        aegl_3_4hr_ppm=chemical.aegl_3_4hr_ppm,
        lc50_ppm=chemical.lc50_ppm,
        pel_ppm=chemical.pel_ppm,
        rel_ppm=chemical.rel_ppm,
        tlv_twa_ppm=chemical.tlv_twa_ppm,
        tlv_stel_ppm=chemical.tlv_stel_ppm,
        stel_ppm=chemical.stel_ppm,
        weel_ppm=chemical.weel_ppm,
        data_sources=chemical.data_sources,
        notes=chemical.notes,
        last_updated=chemical.last_updated,
    )


@router.post("/", response_model=Chemical, status_code=201)
async def create_chemical(
    chemical: ChemicalCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chemical"""
    # Check if CAS number already exists
    existing = await db.execute(
        select(Chemical).where(Chemical.cas_number == chemical.cas_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Chemical with this CAS number already exists")

    # Create chemical
    db_chemical = Chemical(
        cas_number=chemical.cas_number,
        name=chemical.name,
        synonyms=chemical.synonyms,
        formula=chemical.formula,
        molecular_weight=chemical.molecular_weight,
        boiling_point_c=chemical.boiling_point_c,
        melting_point_c=chemical.melting_point_c,
        liquid_density_kg_m3=chemical.liquid_density_kg_m3,
        gas_density_kg_m3=chemical.gas_density_kg_m3,
        vapor_pressure_kpa=chemical.vapor_pressure_kpa,
        state_at_ambient=chemical.state_at_ambient,
        gas_density_ratio=chemical.gas_density_ratio,
        is_heavier_than_air=(chemical.gas_density_ratio or 0) > 1.0,
        solubility_g_l=chemical.solubility_g_l,
        lel_percent=chemical.lel_percent,
        uel_percent=chemical.uel_percent,
        hazard_class=chemical.hazard_class,
        un_number=chemical.un_number,
        ghs_pictograms=chemical.ghs_pictograms,
        risk_phrases=chemical.risk_phrases,
        first_aid=chemical.first_aid,
        fire_fighting=chemical.fire_fighting,
        ppe_requirements=chemical.ppe_requirements,
        erpg_1_ppm=chemical.erpg_1_ppm,
        erpg_1_mg_m3=chemical.erpg_1_mg_m3,
        erpg_2_ppm=chemical.erpg_2_ppm,
        erpg_2_mg_m3=chemical.erpg_2_mg_m3,
        erpg_3_ppm=chemical.erpg_3_ppm,
        erpg_3_mg_m3=chemical.erpg_3_mg_m3,
        idlh_ppm=chemical.idlh_ppm,
        idlh_mg_m3=chemical.idlh_mg_m3,
        aegl_1_10min_ppm=chemical.aegl_1_10min_ppm,
        aegl_1_30min_ppm=chemical.aegl_1_30min_ppm,
        aegl_1_60min_ppm=chemical.aegl_1_60min_ppm,
        aegl_1_4hr_ppm=chemical.aegl_1_4hr_ppm,
        aegl_2_10min_ppm=chemical.aegl_2_10min_ppm,
        aegl_2_30min_ppm=chemical.aegl_2_30min_ppm,
        aegl_2_60min_ppm=chemical.aegl_2_60min_ppm,
        aegl_2_4hr_ppm=chemical.aegl_2_4hr_ppm,
        aegl_3_10min_ppm=chemical.aegl_3_10min_ppm,
        aegl_3_30min_ppm=chemical.aegl_3_30min_ppm,
        aegl_3_60min_ppm=chemical.aegl_3_60min_ppm,
        aegl_3_4hr_ppm=chemical.aegl_3_4hr_ppm,
        lc50_ppm=chemical.lc50_ppm,
        pel_ppm=chemical.pel_ppm,
        rel_ppm=chemical.rel_ppm,
        tlv_twa_ppm=chemical.tlv_twa_ppm,
        tlv_stel_ppm=chemical.tlv_stel_ppm,
        stel_ppm=chemical.stel_ppm,
        weel_ppm=chemical.weel_ppm,
        data_sources=chemical.data_sources,
        notes=chemical.notes,
    )

    db.add(db_chemical)
    await db.commit()
    await db.refresh(db_chemical)

    # Return using schema
    chemical_dict = {
        "cas_number": db_chemical.cas_number,
        "name": db_chemical.name,
        "synonyms": db_chemical.synonyms,
        "formula": db_chemical.formula,
        "molecular_weight": db_chemical.molecular_weight,
        "boiling_point_c": db_chemical.boiling_point_c,
        "melting_point_c": db_chemical.melting_point_c,
        "liquid_density_kg_m3": db_chemical.liquid_density_kg_m3,
        "gas_density_kg_m3": db_chemical.gas_density_kg_m3,
        "vapor_pressure_kpa": db_chemical.vapor_pressure_kpa,
        "state_at_ambient": db_chemical.state_at_ambient,
        "gas_density_ratio": db_chemical.gas_density_ratio,
        "is_heavier_than_air": db_chemical.is_heavier_than_air,
        "solubility_g_l": db_chemical.solubility_g_l,
        "lel_percent": db_chemical.lel_percent,
        "uel_percent": db_chemical.uel_percent,
        "hazard_class": db_chemical.hazard_class,
        "un_number": db_chemical.un_number,
        "ghs_pictograms": db_chemical.ghs_pictograms,
        "risk_phrases": db_chemical.risk_phrases,
        "first_aid": db_chemical.first_aid,
        "fire_fighting": db_chemical.fire_fighting,
        "ppe_requirements": db_chemical.ppe_requirements,
        "erpg_1_ppm": db_chemical.erpg_1_ppm,
        "erpg_1_mg_m3": db_chemical.erpg_1_mg_m3,
        "erpg_2_ppm": db_chemical.erpg_2_ppm,
        "erpg_2_mg_m3": db_chemical.erpg_2_mg_m3,
        "erpg_3_ppm": db_chemical.erpg_3_ppm,
        "erpg_3_mg_m3": db_chemical.erpg_3_mg_m3,
        "idlh_ppm": db_chemical.idlh_ppm,
        "idlh_mg_m3": db_chemical.idlh_mg_m3,
        "aegl_1_10min_ppm": db_chemical.aegl_1_10min_ppm,
        "aegl_1_30min_ppm": db_chemical.aegl_1_30min_ppm,
        "aegl_1_60min_ppm": db_chemical.aegl_1_60min_ppm,
        "aegl_1_4hr_ppm": db_chemical.aegl_1_4hr_ppm,
        "aegl_2_10min_ppm": db_chemical.aegl_2_10min_ppm,
        "aegl_2_30min_ppm": db_chemical.aegl_2_30min_ppm,
        "aegl_2_60min_ppm": db_chemical.aegl_2_60min_ppm,
        "aegl_2_4hr_ppm": db_chemical.aegl_2_4hr_ppm,
        "aegl_3_10min_ppm": db_chemical.aegl_3_10min_ppm,
        "aegl_3_30min_ppm": db_chemical.aegl_3_30min_ppm,
        "aegl_3_60min_ppm": db_chemical.aegl_3_60min_ppm,
        "aegl_3_4hr_ppm": db_chemical.aegl_3_4hr_ppm,
        "lc50_ppm": db_chemical.lc50_ppm,
        "pel_ppm": db_chemical.pel_ppm,
        "rel_ppm": db_chemical.rel_ppm,
        "tlv_twa_ppm": db_chemical.tlv_twa_ppm,
        "tlv_stel_ppm": db_chemical.tlv_stel_ppm,
        "stel_ppm": db_chemical.stel_ppm,
        "weel_ppm": db_chemical.weel_ppm,
        "data_sources": db_chemical.data_sources,
        "notes": db_chemical.notes,
        "last_updated": db_chemical.last_updated,
    }

    return Chemical(**chemical_dict)


@router.put("/{cas_number}", response_model=Chemical)
async def update_chemical(
    cas_number: str,
    chemical: ChemicalUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update chemical"""
    query = select(Chemical).where(Chemical.cas_number == cas_number)
    result = await db.execute(query)
    db_chemical = result.scalar_one_or_none()

    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    # Update fields
    update_data = chemical.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chemical, field, value)

    # Recalculate is_heavier_than_air if gas_density_ratio changed
    if 'gas_density_ratio' in update_data:
        db_chemical.is_heavier_than_air = (db_chemical.gas_density_ratio or 0) > 1.0

    await db.commit()
    await db.refresh(db_chemical)

    # Return updated chemical
    return await get_chemical(cas_number, db)


@router.delete("/{cas_number}", response_model=MessageResponse)
async def delete_chemical(
    cas_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete chemical"""
    query = select(Chemical).where(Chemical.cas_number == cas_number)
    result = await db.execute(query)
    db_chemical = result.scalar_one_or_none()

    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    await db.delete(db_chemical)
    await db.commit()

    return MessageResponse(message=f"Chemical {cas_number} deleted successfully")