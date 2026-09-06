from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.models.goal import GoalCreate, GoalInDB, GoalStatus, GoalUpdate
from app.models.memory import MemoryEventType
from app.models.user import UserInDB
from app.services.goal_intelligence_service import generate_tasks_for_goal
from app.services.memory_service import record_memory

router = APIRouter(prefix="/api/goals", tags=["goals"])


async def _get_owned_goal(db: AsyncIOMotorDatabase, goal_id: str, user_id: ObjectId) -> dict:
    if not ObjectId.is_valid(goal_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid goal id")
    doc = await db[Collections.GOALS].find_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return doc


@router.post("", response_model=GoalInDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    tasks = generate_tasks_for_goal(payload.title, payload.category, payload.target_date)
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user.id,
        "title": payload.title,
        "description": payload.description,
        "category": payload.category,
        "status": GoalStatus.ACTIVE.value,
        "progress": 0,
        "target_date": payload.target_date,
        "tasks": [t.model_dump() for t in tasks],
        "milestones": [],
        "last_progress_at": None,
        "created_at": now,
        "updated_at": now,
    }
    result = await db[Collections.GOALS].insert_one(doc)
    doc["_id"] = result.inserted_id

    await record_memory(db, user.id, MemoryEventType.GOAL_CREATED, f'Started a new goal: "{payload.title}".',
                         related_goal_id=doc["_id"])
    return GoalInDB(**doc)


@router.get("", response_model=list[GoalInDB], response_model_by_alias=False)
async def list_goals(
    status_filter: GoalStatus | None = None,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    query: dict = {"user_id": user.id}
    if status_filter:
        query["status"] = status_filter.value
    cursor = db[Collections.GOALS].find(query).sort("created_at", -1)
    return [GoalInDB(**doc) async for doc in cursor]


@router.get("/{goal_id}", response_model=GoalInDB, response_model_by_alias=False)
async def get_goal(goal_id: str, user: UserInDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await _get_owned_goal(db, goal_id, user.id)
    return GoalInDB(**doc)


@router.patch("/{goal_id}", response_model=GoalInDB, response_model_by_alias=False)
async def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await _get_owned_goal(db, goal_id, user.id)
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    now = datetime.now(timezone.utc)

    if "progress" in updates:
        updates["last_progress_at"] = now
    if "status" in updates:
        updates["status"] = updates["status"].value if hasattr(updates["status"], "value") else updates["status"]

    updates["updated_at"] = now
    await db[Collections.GOALS].update_one({"_id": doc["_id"]}, {"$set": updates})

    if updates.get("status") == GoalStatus.COMPLETED.value:
        await record_memory(db, user.id, MemoryEventType.GOAL_COMPLETED, f'Completed the goal: "{doc["title"]}".',
                             related_goal_id=doc["_id"], importance=5)
    elif updates.get("status") == GoalStatus.ABANDONED.value:
        await record_memory(db, user.id, MemoryEventType.GOAL_ABANDONED, f'Abandoned the goal: "{doc["title"]}".',
                             related_goal_id=doc["_id"], importance=4)

    updated = await db[Collections.GOALS].find_one({"_id": doc["_id"]})
    return GoalInDB(**updated)


@router.patch("/{goal_id}/tasks/{task_id}", response_model=GoalInDB, response_model_by_alias=False)
async def toggle_task(
    goal_id: str,
    task_id: str,
    is_done: bool,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await _get_owned_goal(db, goal_id, user.id)
    tasks = doc.get("tasks", [])
    if not any(t["id"] == task_id for t in tasks):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    now = datetime.now(timezone.utc)
    await db[Collections.GOALS].update_one(
        {"_id": doc["_id"], "tasks.id": task_id},
        {"$set": {"tasks.$.is_done": is_done, "last_progress_at": now, "updated_at": now}},
    )
    updated = await db[Collections.GOALS].find_one({"_id": doc["_id"]})
    return GoalInDB(**updated)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(goal_id: str, user: UserInDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await _get_owned_goal(db, goal_id, user.id)
    await db[Collections.GOALS].delete_one({"_id": doc["_id"]})
