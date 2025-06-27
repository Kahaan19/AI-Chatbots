from pydantic import BaseModel
from typing import Optional

class DomainBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str

class DomainCreate(DomainBase):
    pass

class Domain(DomainBase):
    id: int
    
    class Config:
        from_attributes = True