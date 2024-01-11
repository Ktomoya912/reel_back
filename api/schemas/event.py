from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

import api.schemas.tag as tag_schema
import api.schemas.user as user_schema
from api.utils import get_jst_now

sample_date = get_jst_now() + timedelta(days=1)
start_time = sample_date.strftime("%Y-%m-%d %H:%M:%S")
end_time = (sample_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


class EventTimeBase(BaseModel):
    start_time: datetime = Field(..., example=start_time, description="開始日時")
    end_time: datetime = Field(..., example=end_time, description="終了日時")


class EventTimeCreate(EventTimeBase):
    pass


class EventTime(EventTimeBase):
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
    user: user_schema.User

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    name: str = Field(
        ...,
        example="イベント名",
        description="イベント名",
        min_length=5,
        max_length=100,
    )
    image_url: Optional[str] = Field(
        None,
        example="https://example.com",
        description="画像URL",
    )


class EventCreate(EventBase):
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
        description="番地・建物名",
        max_length=100,
    )
    phone_number: str = Field(
        ...,
        example="0887-53-1111",
        description="電話番号",
        min_length=10,
        max_length=13,
    )
    email: EmailStr = Field(
        ...,
        example="sample@ugs.ac.jp",
        description="メールアドレス",
        max_length=100,
    )
    homepage: Optional[str] = Field(
        ...,
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
    additional_message: str = Field(
        ...,
        example="",
        description="追加メッセージ",
        max_length=1000,
    )
    description: str = Field(
        ...,
        example="",
        description="説明",
        max_length=1000,
    )
    caution: str = Field(
        ...,
        example="",
        description="注意事項",
        max_length=1000,
    )
    tags: Optional[List[tag_schema.TagCreate]]
    event_times: List[EventTimeCreate]

    class Config:
        orm_mode = True


class EventCreateResponse(EventCreate):
    id: int = Field(..., example=1, description="イベントID")


class EventListView(EventCreateResponse):
    status: Optional[str] = Field(..., example="1", description="イベントステータス")
    event_times: List[EventTime]
    tags: Optional[List[tag_schema.Tag]]


class Event(EventListView):
    # period: datetime = Field(..., example="2023-12-31 23:59:59", description="掲載終了日時")
    reviews: Optional[List[EventReview]]
    is_favorite: bool = Field(..., example=True, description="お気に入り登録済みかどうか")
    author: user_schema.User


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
