from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str


class Tag(TagBase):
    id: int
    jobs: Optional[list] = Field(
        [],
        example=[],
        description="求人",
    )
    events: Optional[list] = Field(
        [],
        example=[],
        description="イベント",
    )

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    pass


class TagCreateResponse(TagCreate):
    id: int

    class Config:
        orm_mode = True
