import datetime
from typing import Optional, Union

from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_serializer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    username: str
    password: str
    email: str
    sex: Optional[str] = Field(
        "o",
        example="男",
        description="性别",
        max_length=2,
    )
    birthday: datetime.date
    user_type: str = Field(
        "u",
        example="u",
        description="ユーザータイプ",
    )

    @field_serializer("password")
    def password_hash(self, v: str):
        return pwd_context.hash(v)


class User(UserBase):
    id: int
    company: Optional["Company"]
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


# 法人ユーザー登録用
class UserCreateCompany(UserCreate):
    user_type: str = Field(
        "c",
        example="c",
        description="ユーザータイプ",
    )
    company: CompanyCreate


class UserCreateResponse(UserCreate):
    id: int

    class Config:
        orm_mode = True
