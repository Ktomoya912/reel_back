from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EventTimeBase(BaseModel):
    start_time: datetime = Field(..., example="2023-12-31 23:59:59", description="開始日時")
    end_time: datetime = Field(..., example="2023-12-31 23:59:59", description="終了日時")


class EventTimeCreate(EventTimeBase):
    pass


class EventTime(EventTimeBase):
    id: int

    class Config:
        orm_mode = True


class EventTagBase(BaseModel):
    name: str = Field(
        ...,
        example="タグ名",
        description="タグ名",
        min_length=1,
        max_length=20,
    )


class EventTagCreate(EventTagBase):
    pass


class EventTag(EventTagBase):
    id: int

    class Config:
        orm_mode = True


class EventReviewBase(BaseModel):
    title: str = Field(
        ...,
        example="タイトル",
        description="タイトル",
        min_length=1,
        max_length=20,
    )
    review: str = Field(
        ...,
        example="レビュー",
        description="レビュー",
        min_length=1,
        max_length=1000,
    )
    review_point: int = Field(
        ...,
        example=5,
        description="レビューポイント",
        ge=1,
        le=5,
    )


class EventReviewCreate(EventReviewBase):
    pass


class EventReview(EventReviewBase):
    id: int

    class Config:
        orm_mode = True


class EventListView(BaseModel):
    id: int
    name: str = Field(
        ...,
        example="イベント名",
        description="イベント名",
        min_length=5,
        max_length=100,
    )
    period: datetime = Field(..., example="2023-12-31 23:59:59", description="掲載終了日時")


class EventDetail(EventListView):
    postal_code: str = Field(
        ...,
        example="782-8502",
        description="郵便番号",
        min_length=7,
        max_length=8,
    )
    prefecture: str = Field(
        ...,
        example="高知県",
        description="都道府県",
        max_length=5,
    )
    city: str = Field(
        ...,
        example="香美市",
        description="市区町村",
        max_length=20,
    )
    address: str = Field(
        ...,
        example="土佐山田町宮ノ口185",
        description="番地",
        max_length=100,
    )
    phone_number: str = Field(
        ...,
        example="0887-53-1111",
        description="電話番号",
        min_length=10,
        max_length=13,
    )
    email: str = Field(
        ...,
        example="sample@ugs.ac.jp",
        description="メールアドレス",
        max_length=100,
    )
    homepage: Optional[str] = Field(
        "",
        example="https://kochi-tech.ac.jp/",
        description="ホームページ",
    )
    participation_fee: str = Field(
        ...,
        example="無料",
        description="参加費",
    )
    capacity: int = Field(
        ...,
        example=100,
        description="定員",
    )
    # additional_message: str = Field(
    #     ...,
    #     example="",
    #     description="追加メッセージ",
    #     max_length=100,
    # )
    description: str = Field(
        ...,
        example="",
        description="説明",
        max_length=1000,
    )
    tags: Optional[List[EventTag]] = Field(
        [],
        example=[],
        description="タグ",
    )
    event_times: List[EventTime] = Field(
        [],
        example=[
            {"start_time": "2023-12-31 23:59:59", "end_time": "2023-12-31 23:59:59"}
        ],
        description="イベント時間",
    )
    reviews: Optional[List[EventReview]] = Field(
        [],
        example=[],
        description="レビュー",
    )


class EventCreate(EventDetail):
    tags: Optional[List[EventTagCreate]] = Field(
        ...,
        example=[],
        description="タグ",
    )
    event_times: List[EventTimeCreate] = Field(
        ...,
        example=[
            {"start_time": "2023-12-31 23:59:59", "end_time": "2023-12-31 23:59:59"}
        ],
        description="イベント時間",
    )

    class Config:
        orm_mode = True


class BaseImpression(BaseModel):
    age_u_20: int
    age_24: int
    age_29: int
    age_34: int
    age_39: int
    age_u_40: int


class EventImpression(BaseModel):
    female: BaseImpression
    male: BaseImpression
    other: BaseImpression
