import datetime
from typing import Optional, Union

from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CompanyBase(BaseModel):
    name: str
    postal_code: str
    prefecture: str
    city: str
    address: str
    phone_number: str
    email: EmailStr
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


class MailBase(BaseModel):
    email: EmailStr = Field(
        ...,
        example="my@example.com",
        description="メールアドレス",
    )

    class Config:
        orm_mode = True


class MailBody(MailBase):
    subject: str = Field(
        ...,
        example="subject",
        description="件名",
    )
    body: str = Field(
        ...,
        example="body",
        description="本文",
    )


class UserPasswordChange(BaseModel):
    password: str = Field(
        ...,
        example="password",
        description="パスワード",
        min_length=8,
    )

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(
        ...,
        example="username",
        description="ユーザー名",
        min_length=4,
        max_length=16,
        pattern=r"[\w\-._]+",
    )
    image_url: Optional[str] = Field(
        None,
        example="https://example.com",
        description="画像URL",
    )
    email: EmailStr = Field(
        ...,
        example="my@example.com",
        description="メールアドレス",
    )
    sex: Optional[str] = Field(
        "o",
        example="男",
        description="性别",
        max_length=2,
    )
    birthday: datetime.date
    user_type: str = Field(
        "g",
        example="g",
        description="ユーザータイプ",
        pattern=r"[gca]",
    )

    class Config:
        orm_mode = True


class UserCreate(UserBase, UserPasswordChange):
    pass


class User(UserBase):
    id: int
    company: Optional["Company"]
    is_active: bool


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
