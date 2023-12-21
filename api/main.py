import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers import auth, notice, user

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(notice.router)


def initialize():
    env_file = Path(".env")
    env_file.touch(exist_ok=True)
    load_dotenv(dotenv_path=env_file)
    if os.getenv("SECRET_KEY") is None:
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(f"SECRET_KEY={secrets.token_hex(32)}\n")
        load_dotenv(dotenv_path=env_file)


initialize()


@app.get("/hello")
def hello():
    return {"message": "hello world!"}
