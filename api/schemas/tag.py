from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(
        ...,
        example="タグ名",
        description="タグ名",
        min_length=1,
        max_length=20,
    )


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    pass


class TagCreateResponse(TagCreate):
    id: int

    class Config:
        orm_mode = True
