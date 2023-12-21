from typing import Optional

from pydantic import BaseModel, Field

from .user import Company


class JobBase(BaseModel):
    title: str
    salary: int = Field(
        ...,
        example=1000,
        description="給与",
    )
    working_hours: str = Field(
        ...,
        example="10:00~19:00",
        description="勤務時間",
    )
    working_location: str = Field(
        ...,
        example="東京都",
        description="勤務地",
    )
    description: str = Field(
        ...,
        example="◯◯の開発をお願いします。",
        description="仕事内容",
    )
    is_one_day: bool = Field(
        False,
        example=True,
        description="1日のみかどうか",
    )
    period: str = Field(
        ...,
        example="2週間",
        description="期間",
    )
    additional_message: str = Field(
        ...,
        example="初心者歓迎！",
        description="追加メッセージ",
    )


class Job(JobBase):
    id: int
    company: Optional[Company] = None
    tags: Optional[list] = Field(
        [],
        example=[],
        description="タグ",
    )
    bookmark_users: Optional[list] = Field(
        [],
        example=[],
        description="ブックマークしたユーザー",
    )
    reviews: Optional[list] = Field(
        [],
        example=[],
        description="レビュー",
    )
    applicants: Optional[list] = Field(
        [],
        example=[],
        description="応募者",
    )
    watch_users: Optional[list] = Field(
        [],
        example=[],
        description="閲覧したユーザー",
    )
    created_at: Optional[str] = Field(
        None,
        example="2021-01-01 00:00:00",
        description="作成日時",
    )
    updated_at: Optional[str] = Field(
        None,
        example="2021-01-01 00:00:00",
        description="更新日時",
    )

    class Config:
        orm_mode = True


class JobCreate(JobBase):
    pass


class JobCreateResponse(JobCreate):
    id: int

    class Config:
        orm_mode = True
