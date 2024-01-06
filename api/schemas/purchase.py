from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from .event import EventCreate
from .job import JobCreate
from .plan import PurchaseCreate


class __Article(BaseModel):
    purchase: PurchaseCreate

    class Config:
        orm_mode = True


class JobArticleCreate(__Article):
    job: JobCreate


class EventArticleCreate(__Article):
    event: EventCreate
