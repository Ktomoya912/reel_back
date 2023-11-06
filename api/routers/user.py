from fastapi import APIRouter
from typing import List

import api.schemas.user as user_schema

router = APIRouter()


@router.get("/users", response_model=List[user_schema.User])
def get_users():
    return [
        user_schema.User(
            id=1,
            name="user1",
            password="password1",
            email="example@email.com",
            gender="男",
            birthday="1990-01-01",
        )
    ]


@router.post("/users", response_model=user_schema.UserCreateResponse)
def create_user(user_id: int, user_body: user_schema.UserCreate):
    return user_schema.UserCreateResponse(id=user_id, **user_body.dict())


@router.put("/users/{user_id}", response_model=user_schema.UserCreateResponse)
def update_user(user_body: user_schema.UserCreate):
    return user_schema.UserCreateResponse(id=1, **user_body.dict())


@router.delete("/users/{user_id}")
def delete_user():
    pass
