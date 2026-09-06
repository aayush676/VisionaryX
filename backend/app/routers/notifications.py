from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.models.notification import NotificationInDB
from app.models.user import UserInDB

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationInDB], response_model_by_alias=False)
async def list_notifications(
    unread_only: bool = False,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    query: dict = {"user_id": user.id}
    if unread_only:
        query["is_read"] = False
    cursor = db[Collections.NOTIFICATIONS].find(query).sort("created_at", -1).limit(50)
    return [NotificationInDB(**doc) async for doc in cursor]


@router.patch("/{notification_id}/read", response_model=NotificationInDB, response_model_by_alias=False)
async def mark_read(
    notification_id: str,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid notification id")

    doc = await db[Collections.NOTIFICATIONS].find_one({"_id": ObjectId(notification_id), "user_id": user.id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    await db[Collections.NOTIFICATIONS].update_one({"_id": doc["_id"]}, {"$set": {"is_read": True}})
    doc["is_read"] = True
    return NotificationInDB(**doc)


@router.patch("/read-all")
async def mark_all_read(user: UserInDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await db[Collections.NOTIFICATIONS].update_many(
        {"user_id": user.id, "is_read": False}, {"$set": {"is_read": True}}
    )
    return {"updated": result.modified_count}
