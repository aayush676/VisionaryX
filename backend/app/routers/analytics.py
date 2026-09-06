from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user, get_db
from app.models.user import UserInDB
from app.services.analytics_service import get_analytics_history, record_daily_snapshot

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc["user_id"] = str(doc["user_id"])
    return doc


@router.post("/snapshot")
async def create_snapshot(user: UserInDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    return await record_daily_snapshot(db, user.id)


@router.get("/history")
async def analytics_history(
    days: int = Query(default=30, ge=1, le=365),
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    docs = await get_analytics_history(db, user.id, days=days)
    return [_serialize(doc) for doc in docs]
