from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings, extra="allow"):
    SECRET_KEY: str
    MAIL_SENDER: str = Field(..., pattern=r"[\w\-._]+@[\w\-._]+")
    IS_PRODUCT: bool = False
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class DevelopConfig(BaseConfig):
    pass


class ProductConfig(BaseConfig):
    IS_PRODUCT: bool = True


class TestConfig(BaseConfig):
    SECRET_KEY: str = "this1is2test3secret4key5"
