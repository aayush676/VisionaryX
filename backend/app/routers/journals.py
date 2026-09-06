from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.ml.sentiment import analyze_journal_text
from app.models.journal import JournalCreate, JournalInDB
from app.models.memory import MemoryEventType
from app.models.user import UserInDB
from app.services.memory_service import record_memory

router = APIRouter(prefix="/api/journals", tags=["journals"])

_BURNOUT_MEMORY_THRESHOLD = 60


@router.post("", response_model=JournalInDB, response_model_by_alias=False, status_code=201)
async def create_journal(
    payload: JournalCreate,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    analysis = analyze_journal_text(payload.content)
    doc = {
        "user_id": user.id,
        "content": payload.content,
        "sentiment_score": analysis["sentiment_score"],
        "dominant_emotion": analysis["dominant_emotion"],
        "emotions": analysis["emotions"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db[Collections.JOURNALS].insert_one(doc)
    doc["_id"] = result.inserted_id

    if analysis["emotions"]["burnout"] >= _BURNOUT_MEMORY_THRESHOLD or analysis["emotions"]["stress"] >= _BURNOUT_MEMORY_THRESHOLD:
        await record_memory(
            db, user.id, MemoryEventType.BURNOUT_WARNING,
            "Journal entry showed high stress/burnout signals.", importance=4,
        )

    return JournalInDB(**doc)


@router.get("", response_model=list[JournalInDB], response_model_by_alias=False)
async def list_journals(
    days: int = Query(default=30, ge=1, le=365),
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = db[Collections.JOURNALS].find({"user_id": user.id, "created_at": {"$gte": since}}).sort("created_at", -1)
    return [JournalInDB(**doc) async for doc in cursor]
