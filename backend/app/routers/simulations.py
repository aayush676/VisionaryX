from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.models.memory import MemoryEventType
from app.models.simulation import LifePathCompareRequest, SimulationRequest
from app.models.user import UserInDB
from app.services.life_path_service import compare_life_paths
from app.services.memory_service import record_memory
from app.services.simulation_service import run_and_store_simulation

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc["user_id"] = str(doc["user_id"])
    return doc


@router.post("/run")
async def run_simulation(
    payload: SimulationRequest,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await run_and_store_simulation(db, user.id, payload.horizon, payload.adjustments)
    if payload.adjustments is None:
        await record_memory(
            db, user.id, MemoryEventType.SIMULATION_RUN,
            f"Ran a {payload.horizon.value} future simulation.", importance=1,
        )
    return _serialize(doc)


@router.post("/what-if")
async def run_what_if(
    payload: SimulationRequest,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if payload.adjustments is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="adjustments are required for a what-if run")

    baseline = await run_and_store_simulation(db, user.id, payload.horizon, adjustments=None)
    adjusted = await run_and_store_simulation(db, user.id, payload.horizon, adjustments=payload.adjustments)

    await record_memory(
        db, user.id, MemoryEventType.SIMULATION_RUN,
        f"Ran a What-If simulation over {payload.horizon.value}.", importance=2,
    )

    return {"baseline": _serialize(baseline), "what_if": _serialize(adjusted)}


@router.post("/compare-life-paths")
async def compare_paths(
    payload: LifePathCompareRequest,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    results = await compare_life_paths(db, user.id, payload.horizon, payload.paths, payload.labels)
    return {"horizon": payload.horizon.value, "paths": results}


@router.get("")
async def list_simulations(
    limit: int = 20,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db[Collections.SIMULATIONS].find({"user_id": user.id}).sort("created_at", -1).limit(limit)
    return [_serialize(doc) async for doc in cursor]
