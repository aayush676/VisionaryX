"""Digital Twin Engine.

Recomputes the user's Digital Twin (a live snapshot of study/sleep/
productivity/focus/fitness/screen-time/consistency/emotional-state) from
their recent habit logs and journal entries, classifies it into one of five
states, and persists the snapshot onto the user document so the frontend can
render it without recomputing on every page load.
"""
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.ml.burnout_model import predict_burnout_risk
from app.models.user import DigitalTwinMetrics, DigitalTwinSnapshot, TwinState

LOOKBACK_DAYS = 14


def classify_twin_state(metrics: DigitalTwinMetrics, burnout_risk: float) -> TwinState:
    composite = (metrics.productivity + metrics.focus + metrics.consistency) / 3

    if burnout_risk >= 70:
        return TwinState.BURNOUT
    if metrics.focus < 40 and metrics.consistency < 40:
        return TwinState.DISTRACTED
    if composite >= 80 and metrics.consistency >= 75:
        return TwinState.ELITE_PERFORMER
    if composite >= 60:
        return TwinState.FOCUSED
    return TwinState.NOMINAL


async def _aggregate_recent_habits(db: AsyncIOMotorDatabase, user_id: ObjectId) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    cursor = db[Collections.HABIT_LOGS].find({"user_id": user_id, "date": {"$gte": since}})
    logs = [doc async for doc in cursor]

    if not logs:
        return {
            "study_hours": 0, "sleep_hours": 0, "screen_time": 0,
            "productivity": 0, "focus": 0, "fitness": 0, "consistency": 0,
        }

    n = len(logs)
    avg_study = sum(l.get("study_hours", 0) for l in logs) / n
    avg_sleep = sum(l.get("sleep_hours", 0) for l in logs) / n
    avg_screen = sum(l.get("screen_time_hours", 0) for l in logs) / n
    avg_productivity = sum(l.get("productivity_score", 0) for l in logs) / n
    avg_focus = sum(l.get("focus_score", 0) for l in logs) / n
    avg_fitness_minutes = sum(l.get("fitness_minutes", 0) for l in logs) / n

    # Consistency: fraction of the lookback window that actually has a log,
    # capped at 100.
    consistency = min(100.0, (n / LOOKBACK_DAYS) * 100)

    # Normalize fitness minutes/day onto a 0-100 scale (60+ min/day = 100).
    fitness_score = min(100.0, (avg_fitness_minutes / 60) * 100)

    return {
        "study_hours": round(avg_study, 1),
        "sleep_hours": round(avg_sleep, 1),
        "screen_time": round(avg_screen, 1),
        "productivity": round(avg_productivity, 1),
        "focus": round(avg_focus, 1),
        "fitness": round(fitness_score, 1),
        "consistency": round(consistency, 1),
    }


async def _average_emotional_state(db: AsyncIOMotorDatabase, user_id: ObjectId) -> float:
    since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    cursor = db[Collections.JOURNALS].find({"user_id": user_id, "created_at": {"$gte": since}})
    entries = [doc async for doc in cursor]
    if not entries:
        return 50.0
    # sentiment_score is -1..1 -> map onto 0..100.
    avg_sentiment = sum(e.get("sentiment_score", 0) for e in entries) / len(entries)
    return round((avg_sentiment + 1) * 50, 1)


async def recompute_digital_twin(db: AsyncIOMotorDatabase, user_id: ObjectId) -> DigitalTwinSnapshot:
    habit_stats = await _aggregate_recent_habits(db, user_id)
    emotional_state = await _average_emotional_state(db, user_id)

    metrics = DigitalTwinMetrics(**habit_stats, emotional_state=emotional_state)
    burnout_risk = predict_burnout_risk(
        sleep_hours=metrics.sleep_hours,
        screen_time_hours=metrics.screen_time,
        study_hours=metrics.study_hours,
        consistency=metrics.consistency,
        fitness_minutes=habit_stats["fitness"] * 0.6,  # approx back to minutes/day
    )
    state = classify_twin_state(metrics, burnout_risk)

    snapshot = DigitalTwinSnapshot(state=state, metrics=metrics, updated_at=datetime.now(timezone.utc))

    await db[Collections.USERS].update_one(
        {"_id": user_id},
        {"$set": {"digital_twin": snapshot.model_dump(), "updated_at": datetime.now(timezone.utc)}},
    )
    return snapshot
