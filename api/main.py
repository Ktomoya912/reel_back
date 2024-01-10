import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api import routers
from api.db import Session


def initialize():
    env_file = Path(".env")
    env_file.touch(exist_ok=True)
    load_dotenv(dotenv_path=env_file)
    if os.getenv("SECRET_KEY") is None:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"SECRET_KEY={secrets.token_hex(32)}\n")
        raise Exception("SECRET_KEYを設定しました。再起動を行ってください。")


def create_app():
    initialize()
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOW_ORIGINS", "*"),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        response = Response("Internal server error", status_code=500)
        try:
            request.state.db = Session()
            response = await call_next(request)
        finally:
            request.state.db.close()
        return response

    app.include_router(routers.router)

    @app.get("/hello")
    def hello():
        return {"message": "hello world!"}

    return app
