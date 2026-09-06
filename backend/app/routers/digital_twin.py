from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user, get_db
from app.models.user import DigitalTwinSnapshot, UserInDB
from app.services.digital_twin_service import recompute_digital_twin

router = APIRouter(prefix="/api/digital-twin", tags=["digital-twin"])


@router.get("", response_model=DigitalTwinSnapshot)
async def get_digital_twin(user: UserInDB = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    return await recompute_digital_twin(db, user.id)
