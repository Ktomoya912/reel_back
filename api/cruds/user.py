from datetime import timedelta
from typing import Optional, Union
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

from api import models, schemas
from api.utils import get_jst_now

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """パスワードの検証"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(
    db: Session, username: str, password: str
) -> Union[bool, models.User]:
    """ユーザーの認証"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(
    secret_key: str, data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """アクセストークンの生成"""
    to_encode = data.copy()
    if expires_delta:
        expire = get_jst_now() + expires_delta
    else:
        expire = get_jst_now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_company(
    db: Session, company_create: schemas.CompanyCreate
) -> models.Company:
    """会社の作成"""
    tmp = company_create.model_dump()
    company = models.Company(**tmp)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def create_user_company(
    db: Session, user_create: schemas.UserCreateCompany
) -> models.User:
    """ユーザーと会社の作成"""
    tmp = user_create.model_dump()
    tmp["password"] = pwd_context.hash(tmp["password"])
    company = create_company(db, user_create.company)
    tmp["company"] = company
    user = models.User(**tmp)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, user_create: schemas.UserCreate) -> models.User:
    """ユーザーの作成"""
    tmp = user_create.model_dump()
    tmp["password"] = pwd_context.hash(tmp["password"])
    user = models.User(**tmp)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[models.User]:
    """ユーザー一覧の取得"""
    return db.query(models.User).all()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """ユーザー名からユーザー情報を取得"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """メールアドレスからユーザー情報を取得"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """idからユーザー情報を取得"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(
    db: Session, user_create: schemas.UserCreate, original: models.User
) -> models.User:
    update_data = user_create.model_dump(
        exclude_unset=True, exclude={"password", "company"}
    )
    for key, value in update_data.items():
        if (
            key == "username"
            and value != original.username
            and get_user_by_username(db, value)
        ):
            raise HTTPException(status_code=400, detail="Username already registered")
        if key == "email" and value != original.email and get_user_by_email(db, value):
            raise HTTPException(status_code=400, detail="Email already registered")

        setattr(original, key, value)
    db.commit()
    db.refresh(original)
    return original


def update_user_password(
    db: Session, user: models.User, new_password: schemas.UserPasswordChange
) -> models.User:
    user.password = pwd_context.hash(new_password.password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> False:
    db.delete(user)
    db.commit()
    return True
