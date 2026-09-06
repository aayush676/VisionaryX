"""Analytics Dashboard.

Rolls the Digital Twin + burnout model + goal predictions up into a single
daily AnalyticsSnapshot per user so the dashboard can render trend charts
without recomputing everything from raw habit logs on every request.
"""
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.ml.burnout_model import predict_burnout_risk
from app.services.digital_twin_service import recompute_digital_twin
from app.services.simulation_service import estimate_goal_achievement_probability


def _day_bounds(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


async def record_daily_snapshot(db: AsyncIOMotorDatabase, user_id: ObjectId) -> dict:
    twin = await recompute_digital_twin(db, user_id)
    metrics = twin.metrics

    burnout_score = predict_burnout_risk(
        sleep_hours=metrics.sleep_hours,
        screen_time_hours=metrics.screen_time,
        study_hours=metrics.study_hours,
        consistency=metrics.consistency,
        fitness_minutes=metrics.fitness * 0.6,
    )
    goal_probability = await estimate_goal_achievement_probability(db, user_id, metrics.consistency)
    growth_index = min(100.0, metrics.consistency * 0.5 + metrics.study_hours * 3)
    career_readiness = min(100.0, (
        metrics.productivity * 0.35 + goal_probability * 0.25 + (100 - burnout_score) * 0.2 + growth_index * 0.2
    ))

    today = _day_bounds(datetime.now(timezone.utc))
    snapshot = {
        "user_id": user_id,
        "date": today,
        "productivity_score": metrics.productivity,
        "focus_score": metrics.focus,
        "consistency_score": metrics.consistency,
        "burnout_score": burnout_score,
        "growth_index": round(growth_index, 1),
        "career_readiness": round(career_readiness, 1),
    }

    await db[Collections.ANALYTICS].update_one(
        {"user_id": user_id, "date": today},
        {"$set": snapshot},
        upsert=True,
    )
    return snapshot


async def get_analytics_history(db: AsyncIOMotorDatabase, user_id: ObjectId, days: int = 30) -> list[dict]:
    cursor = db[Collections.ANALYTICS].find({"user_id": user_id}).sort("date", 1).limit(days)
    return [doc async for doc in cursor]
