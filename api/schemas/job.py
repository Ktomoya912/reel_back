from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

import api.schemas.tag as tag_schema
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

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    name: str
    image_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com",
        description="画像URL",
    )


class JobListView(JobBase):
    id: int = Field(..., example=1, description="求人ID")
    status: Optional[str] = Field(..., example="1", description="求人ステータス")
    job_times: List[JobTime]


class JobCreate(JobBase):
    salary: str = Field(
        ...,
        example="時給1000円",
        description="給与",
        min_length=1,
    )
    working_location: str = Field(
        ...,
        example="高知県香美市",
        description="勤務地",
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
    image_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com",
        description="画像URL",
    )
    tags: Optional[list[tag_schema.TagCreate]] = Field(
        ...,
        description="タグ",
    )
    job_times: list[JobTimeCreate] = Field(
        ...,
        description="勤務時間",
    )


class Job(JobListView, JobCreate):
    tags: Optional[list[tag_schema.Tag]] = Field(
        ...,
        description="タグ",
    )
    bookmark_users: Optional[list] = Field(
        ...,
        description="ブックマークしたユーザー",
    )
    reviews: Optional[list[JobReview]] = Field(
        ...,
        description="レビュー",
    )

    class Config:
        orm_mode = True
