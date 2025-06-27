from sqlalchemy.orm import Session
from app.models.domain import Domain
from app.schemas.domain import DomainCreate
from typing import List, Optional

class DomainService:
    @staticmethod
    def get_all_domains(db: Session) -> List[Domain]:
        return db.query(Domain).all()
    
    @staticmethod
    def get_domain_by_id(db: Session, domain_id: int) -> Optional[Domain]:
        return db.query(Domain).filter(Domain.id == domain_id).first()
    
    @staticmethod
    def get_domain_by_name(db: Session, name: str) -> Optional[Domain]:
        return db.query(Domain).filter(Domain.name == name).first()
    
    @staticmethod
    def create_domain(db: Session, domain: DomainCreate) -> Domain:
        db_domain = Domain(**domain.dict())
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
        return db_domain