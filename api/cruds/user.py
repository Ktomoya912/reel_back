from datetime import datetime, timedelta
from typing import Optional, Union

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

import api.models.company as company_model
import api.models.user as user_model
import api.schemas.user as user_schema

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """パスワードの検証"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(
    db: Session, username: str, password: str
) -> Union[bool, user_model.User]:
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
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_company(
    db: Session, company_create: user_schema.CompanyCreate
) -> company_model.Company:
    """会社の作成"""
    tmp = company_create.model_dump()
    company = company_model.Company(**tmp)
    db.add(company)
    db.commit()

    return company


def create_user_company(
    db: Session, user_create: user_schema.UserCreateCompany
) -> user_model.User:
    """ユーザーと会社の作成"""
    tmp = user_create.model_dump()
    company = create_company(db, user_create.company)
    tmp["company"] = company
    user = user_model.User(**tmp)
    db.add(user)
    db.commit()
    return user


def create_user(db: Session, user_create: user_schema.UserCreate) -> user_model.User:
    """ユーザーの作成"""
    tmp = user_create.model_dump()
    user = user_model.User(**tmp)
    db.add(user)
    db.commit()
    return user


def get_users(db: Session) -> list[user_model.User]:
    """ユーザー一覧の取得"""
    users = db.query(user_model.User).all()
    return users


def get_user_by_username(db: Session, username: str) -> Optional[user_model.User]:
    """ユーザー名からユーザー情報を取得"""
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    return user


def get_user_by_email(db: Session, email: str) -> Optional[user_model.User]:
    """メールアドレスからユーザー情報を取得"""
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    return user


def get_user(db: Session, user_id: int) -> Optional[user_model.User]:
    """idからユーザー情報を取得"""
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    return user


def update_user(
    db: Session, user_create: user_schema.UserCreate, original: user_model.User
) -> user_model.User:
    original.username = user_create.username
    db.commit()
    return original


def update_user_password(
    db: Session, user: user_model.User, password: str
) -> user_model.User:
    user.password = password
    db.commit()
    return user


def delete_user(db: Session, user: user_model.User) -> None:
    db.delete(user)
    db.commit()
