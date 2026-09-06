from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user, get_db
from app.models.user import UserInDB
from app.services.memory_service import get_recent_memories

router = APIRouter(prefix="/api/memory", tags=["memory"])


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc["user_id"] = str(doc["user_id"])
    if doc.get("related_goal_id"):
        doc["related_goal_id"] = str(doc["related_goal_id"])
    return doc


@router.get("")
async def list_memory(
    limit: int = 30,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    memories = await get_recent_memories(db, user.id, limit=limit)
    return [_serialize(doc) for doc in memories]
