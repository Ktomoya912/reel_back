from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .user import User


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
    users: Optional[list["User"]] = Field(
        [],
        example=[],
        description="ユーザー情報",
    )

    class Config:
        orm_mode = True


class CompanyCreate(CompanyBase):
    pass


class CompanyCreateResponse(CompanyCreate):
    id: int

    class Config:
        orm_mode = True
