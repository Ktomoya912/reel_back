from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings, extra="allow"):
    SECRET_KEY: str
    PREFIX: str = "/api/v1"
    IS_PRODUCT: bool = False
    MAIL_PASSWORD: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class DevelopConfig(BaseConfig):
    MAIL_SENDER: EmailStr


class ProductConfig(BaseConfig):
    MAIL_SENDER: EmailStr
    IS_PRODUCT: bool = True


class TestConfig(BaseConfig):
    SECRET_KEY: str = "this1is2test3secret4key5"
