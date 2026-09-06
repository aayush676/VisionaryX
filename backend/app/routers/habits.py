from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.models.habit import HabitLogCreate, HabitLogInDB
from app.models.user import UserInDB

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.post("", response_model=HabitLogInDB, response_model_by_alias=False, status_code=201)
async def log_habit(
    payload: HabitLogCreate,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = payload.model_dump()
    doc["user_id"] = user.id
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db[Collections.HABIT_LOGS].insert_one(doc)
    doc["_id"] = result.inserted_id
    return HabitLogInDB(**doc)


@router.get("", response_model=list[HabitLogInDB], response_model_by_alias=False)
async def list_habits(
    days: int = Query(default=30, ge=1, le=365),
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = db[Collections.HABIT_LOGS].find({"user_id": user.id, "date": {"$gte": since}}).sort("date", -1)
    return [HabitLogInDB(**doc) async for doc in cursor]
