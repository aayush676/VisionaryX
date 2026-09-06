from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.models.user import UserInDB, UserPublic, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.patch("/me", response_model=UserPublic, response_model_by_alias=False)
async def update_me(
    payload: UserUpdate,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if "preferences" in updates and updates["preferences"] is not None:
        updates["preferences"] = payload.preferences.model_dump()
    updates["updated_at"] = datetime.now(timezone.utc)

    await db[Collections.USERS].update_one({"_id": user.id}, {"$set": updates})
    doc = await db[Collections.USERS].find_one({"_id": user.id})
    return UserPublic(**doc)
