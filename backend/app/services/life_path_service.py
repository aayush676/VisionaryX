"""Life Path Comparison.

Runs the same Future Simulation Engine across 2-4 candidate behavior paths
(e.g. "Consistent Routine" vs "Inconsistent Routine") and returns them
side by side so the frontend can render a direct comparison.
"""
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.simulation import BehaviorAdjustments, Horizon
from app.services.simulation_service import compute_simulation


async def compare_life_paths(
    db: AsyncIOMotorDatabase,
    user_id: ObjectId,
    horizon: Horizon,
    paths: list[BehaviorAdjustments],
    labels: list[str] | None = None,
) -> list[dict]:
    results = []
    for i, adjustments in enumerate(paths):
        outputs, timeline = await compute_simulation(db, user_id, horizon, adjustments)
        label = labels[i] if labels and i < len(labels) else f"Path {chr(65 + i)}"
        results.append({
            "label": label,
            "adjustments": adjustments.model_dump(),
            "outputs": outputs.model_dump(),
            "timeline": [t.model_dump() for t in timeline],
        })
    return results
