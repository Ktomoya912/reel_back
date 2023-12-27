import os
import re
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, event, notice, user


class NoEnvironmentError(Exception):
    def __init__(self, message=""):
        self.message = f'環境変数が設定されていません。"{message}"が設定されているか確認してください。'
        super().__init__(self.message)


def initialize():
    env_file = Path(".env")
    env_file.touch(exist_ok=True)
    load_dotenv(dotenv_path=env_file)
    if os.getenv("SECRET_KEY") is None:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"SECRET_KEY={secrets.token_hex(32)}\n")
        load_dotenv(dotenv_path=env_file)
    mail_sender = os.getenv("MAIL_SENDER")
    if not mail_sender:
        raise NoEnvironmentError("MAIL_SENDER")
    elif not re.match(r"[\w\-._]+@[\w\-._]+", mail_sender):
        raise ValueError("MAIL_SENDER")


def create_app(config_name="production"):
    if config_name == "production":
        initialize()
    elif config_name == "test":
        os.environ["SECRET_KEY"] = "test"
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOW_ORIGINS", "*"),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router)
    app.include_router(user.router)
    app.include_router(notice.router)
    app.include_router(event.router)

    @app.get("/hello")
    def hello():
        return {"message": "hello world!"}

    return app
