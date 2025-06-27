from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.domain import Domain, DomainCreate
from app.services.domain_service import DomainService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/domains", tags=["domains"])

@router.get("/", response_model=List[Domain])
def get_domains(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available domains"""
    return DomainService.get_all_domains(db)

@router.get("/{domain_id}", response_model=Domain)
def get_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific domain by ID"""
    domain = DomainService.get_domain_by_id(db, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain