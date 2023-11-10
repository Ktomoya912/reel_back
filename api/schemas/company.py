from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    name: str
    postal_code: str
    prefecture: str
    city: str
    address: str
    phone_number: str
    email: str
    homepage: Optional[str] = Field(
        "",
        example="https://example.com",
        description="ホームページ",
    )
    representative: str  # 代表者


class Company(CompanyBase):
    id: int

    class Config:
        orm_mode = True


class CompanyCreate(CompanyBase):
    pass


class CompanyCreateResponse(CompanyCreate):
    id: int

    class Config:
        orm_mode = True
