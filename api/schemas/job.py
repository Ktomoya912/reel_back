from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

import api.schemas.tag as tag_schema
import api.schemas.user as user_schema
from api.utils import get_jst_now

sample_date = get_jst_now() + timedelta(days=1)
start_time = sample_date.strftime("%Y-%m-%d %H:%M:%S")
end_time = (sample_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


class JobTimeBase(BaseModel):
    start_time: datetime = Field(..., example=start_time, description="開始日時")
    end_time: datetime = Field(..., example=end_time, description="終了日時")


class JobTimeCreate(JobTimeBase):
    pass


class JobTime(JobTimeBase):
    id: int

    class Config:
        orm_mode = True


class JobReviewBase(BaseModel):
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


class JobReviewCreate(JobReviewBase):
    pass


class JobReview(JobReviewBase):
    id: int
    user: user_schema.User

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    name: str
    image_url: Optional[str] = Field(
        None,
        example="https://example.com",
        description="画像URL",
    )

    @field_serializer("image_url")
    def str_image_url(self, v: str):
        return str(v)


class JobCreate(JobBase):
    salary: str = Field(
        ...,
        example="時給1000円",
        description="給与",
        min_length=1,
    )
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
    description: str = Field(
        ...,
        example="説明",
        description="説明",
        min_length=1,
    )
    is_one_day: bool = Field(
        ...,
        example=True,
        description="1日のみ",
    )
    additional_message: str = Field(
        ...,
        example="追加メッセージ",
        description="追加メッセージ",
        min_length=1,
    )
    tags: Optional[list[tag_schema.TagCreate]]
    job_times: list[JobTimeCreate]

    class Config:
        orm_mode = True


class JobCreateResponse(JobCreate):
    id: int = Field(..., example=1, description="求人ID")


class JobListView(JobCreate):
    id: int = Field(..., example=1, description="求人ID")
    status: Optional[str] = Field(..., example="1", description="イベントステータス")
    job_times: List[JobTime]
    tags: Optional[List[tag_schema.Tag]]


class Job(JobListView):
    reviews: Optional[List[JobReview]]
    is_favorite: bool = Field(..., example=True, description="お気に入り登録済みかどうか")
    author: user_schema.User
