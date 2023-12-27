from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.cruds.message as message_crud
import api.schemas.user as user_schema
from api.db import get_db

from .auth import get_current_user

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("/notifications")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_user),
):
    job_messages = await message_crud.get_messages(db, current_user.id, "J")
    event_messages = await message_crud.get_messages(db, current_user.id, "E")
    return [
        event_messages,
        job_messages,
    ]
