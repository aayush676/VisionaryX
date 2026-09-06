"""AI Memory System.

Long-term memory persisted in MongoDB so the Future Self Chatbot (and the
dashboard) can reference specific past events instead of only reacting to
the current snapshot -- e.g. "You abandoned this goal 3 weeks ago."
"""
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.models.memory import MemoryEventType

STALE_GOAL_DAYS = 14


async def record_memory(
    db: AsyncIOMotorDatabase,
    user_id: ObjectId,
    event_type: MemoryEventType,
    summary: str,
    related_goal_id: ObjectId | None = None,
    importance: int = 1,
) -> None:
    await db[Collections.AI_MEMORY].insert_one({
        "user_id": user_id,
        "event_type": event_type.value,
        "summary": summary,
        "related_goal_id": related_goal_id,
        "importance": importance,
        "created_at": datetime.now(timezone.utc),
    })


async def get_recent_memories(db: AsyncIOMotorDatabase, user_id: ObjectId, limit: int = 20) -> list[dict]:
    cursor = (
        db[Collections.AI_MEMORY]
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [doc async for doc in cursor]


async def detect_stale_goals(db: AsyncIOMotorDatabase, user_id: ObjectId) -> list[dict]:
    """Find active goals with no progress update in STALE_GOAL_DAYS and log a
    memory event for any that haven't already been flagged."""
    threshold = datetime.now(timezone.utc) - timedelta(days=STALE_GOAL_DAYS)
    cursor = db[Collections.GOALS].find({
        "user_id": user_id,
        "status": "active",
        "$or": [
            {"last_progress_at": {"$lt": threshold}},
            {"last_progress_at": None, "created_at": {"$lt": threshold}},
        ],
    })
    stale_goals = [doc async for doc in cursor]

    for goal in stale_goals:
        already_flagged = await db[Collections.AI_MEMORY].find_one({
            "user_id": user_id,
            "event_type": MemoryEventType.STREAK_BROKEN.value,
            "related_goal_id": goal["_id"],
            "created_at": {"$gte": threshold},
        })
        if not already_flagged:
            days_stale = (datetime.now(timezone.utc) - (goal.get("last_progress_at") or goal["created_at"])).days
            await record_memory(
                db, user_id, MemoryEventType.STREAK_BROKEN,
                summary=f'No progress on "{goal["title"]}" for {days_stale} days.',
                related_goal_id=goal["_id"],
                importance=3,
            )
    return stale_goals


async def build_memory_context(db: AsyncIOMotorDatabase, user_id: ObjectId, limit: int = 8) -> list[str]:
    """Human-readable summaries for the chatbot prompt/template layer."""
    await detect_stale_goals(db, user_id)
    memories = await get_recent_memories(db, user_id, limit=limit)
    return [m["summary"] for m in memories]
