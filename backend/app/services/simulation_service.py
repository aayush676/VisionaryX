"""Future Simulation Engine + What-If Engine.

Projects probable future outcomes (career readiness, burnout risk, goal
achievement probability, learning growth, productivity) from a user's
current Digital Twin metrics and recent analytics history. A What-If run
applies behavior deltas (more study, less screen time, better sleep, ...) on
top of the same engine so baseline vs. adjusted futures are directly
comparable.

This is explicitly a *simulation*, not a prophecy: outputs are probabilistic
estimates from a transparent, tunable formula + lightweight ML, not a claim
about what will actually happen.
"""
from datetime import datetime, timezone

import numpy as np
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.ml.burnout_model import predict_burnout_risk
from app.ml.forecasting import project_forward
from app.ml.goal_prediction import predict_goal_success_probability
from app.models.simulation import BehaviorAdjustments, Horizon, SimulationOutputs, TimelinePoint
from app.models.user import DigitalTwinMetrics
from app.services.digital_twin_service import recompute_digital_twin

HORIZON_CONFIG: dict[Horizon, dict] = {
    Horizon.ONE_MONTH: {"points": 4, "unit": "Week"},
    Horizon.THREE_MONTHS: {"points": 3, "unit": "Month"},
    Horizon.SIX_MONTHS: {"points": 6, "unit": "Month"},
    Horizon.TWELVE_MONTHS: {"points": 12, "unit": "Month"},
}


def _productivity_shift(adjustments: BehaviorAdjustments | None) -> float:
    if not adjustments:
        return 0.0
    return (
        adjustments.study_hours_delta * 3.0
        - adjustments.screen_time_delta * 2.0
        + adjustments.sleep_hours_delta * 2.0
        + adjustments.consistency_delta * 0.5
    )


def _growth_shift(adjustments: BehaviorAdjustments | None) -> float:
    if not adjustments:
        return 0.0
    return adjustments.study_hours_delta * 4.0 + adjustments.consistency_delta * 0.3


def _adjusted_metrics(metrics: DigitalTwinMetrics, adjustments: BehaviorAdjustments | None) -> dict:
    if not adjustments:
        return {
            "sleep_hours": metrics.sleep_hours,
            "screen_time_hours": metrics.screen_time,
            "study_hours": metrics.study_hours,
            "consistency": metrics.consistency,
            "fitness_minutes": metrics.fitness * 0.6,
        }
    return {
        "sleep_hours": max(0.0, metrics.sleep_hours + adjustments.sleep_hours_delta),
        "screen_time_hours": max(0.0, metrics.screen_time + adjustments.screen_time_delta),
        "study_hours": max(0.0, metrics.study_hours + adjustments.study_hours_delta),
        "consistency": float(np.clip(metrics.consistency + adjustments.consistency_delta, 0, 100)),
        "fitness_minutes": max(0.0, metrics.fitness * 0.6 + adjustments.fitness_minutes_delta),
    }


async def _analytics_history(db: AsyncIOMotorDatabase, user_id: ObjectId, field: str, limit: int = 30) -> list[float]:
    cursor = db[Collections.ANALYTICS].find({"user_id": user_id}).sort("date", 1).limit(limit)
    docs = [doc async for doc in cursor]
    return [doc.get(field, 0.0) for doc in docs]


async def estimate_goal_achievement_probability(db: AsyncIOMotorDatabase, user_id: ObjectId, consistency: float) -> float:
    cursor = db[Collections.GOALS].find({"user_id": user_id, "status": "active"})
    goals = [doc async for doc in cursor]
    if not goals:
        return round(float(np.clip(consistency * 0.7 + 20, 0, 100)), 1)

    now = datetime.now(timezone.utc)
    probs = []
    for goal in goals:
        target_date = goal.get("target_date")
        days_remaining = (target_date - now).days if target_date else 90
        streak_days = min(30.0, (consistency / 100) * 30)
        probs.append(predict_goal_success_probability(
            progress=goal.get("progress", 0),
            days_remaining=max(days_remaining, 1),
            consistency=consistency,
            streak_days=streak_days,
        ))
    return round(float(np.mean(probs)), 1)


async def compute_simulation(
    db: AsyncIOMotorDatabase,
    user_id: ObjectId,
    horizon: Horizon,
    adjustments: BehaviorAdjustments | None = None,
) -> tuple[SimulationOutputs, list[TimelinePoint]]:
    twin = await recompute_digital_twin(db, user_id)
    metrics = twin.metrics
    config = HORIZON_CONFIG[horizon]
    points = config["points"]
    unit = config["unit"]

    productivity_history = await _analytics_history(db, user_id, "productivity_score") or [metrics.productivity] * 5
    growth_history = await _analytics_history(db, user_id, "growth_index") or [
        float(np.clip(metrics.consistency * 0.5 + metrics.study_hours * 3, 0, 100))
    ] * 5

    baseline_productivity = project_forward(productivity_history, points)
    baseline_growth = project_forward(growth_history, points)

    prod_shift = _productivity_shift(adjustments)
    growth_shift = _growth_shift(adjustments)
    fractions = np.linspace(1 / points, 1.0, points)  # ramps the behavior-change effect in over time

    productivity_timeline = [
        float(np.clip(val + prod_shift * frac, 0, 100)) for val, frac in zip(baseline_productivity, fractions)
    ]
    growth_timeline = [
        float(np.clip(val + growth_shift * frac, 0, 100)) for val, frac in zip(baseline_growth, fractions)
    ]

    baseline_burnout = predict_burnout_risk(**_adjusted_metrics(metrics, None))
    adjusted_burnout = predict_burnout_risk(**_adjusted_metrics(metrics, adjustments))
    burnout_timeline = list(np.linspace(baseline_burnout, adjusted_burnout, points))

    adjusted = _adjusted_metrics(metrics, adjustments)
    goal_probability = await estimate_goal_achievement_probability(db, user_id, adjusted["consistency"])

    final_productivity = productivity_timeline[-1]
    final_growth = growth_timeline[-1]
    final_burnout = burnout_timeline[-1]

    career_readiness = float(np.clip(
        final_productivity * 0.35 + goal_probability * 0.25 + (100 - final_burnout) * 0.2 + final_growth * 0.2,
        0, 100,
    ))

    outputs = SimulationOutputs(
        career_readiness=round(career_readiness, 1),
        burnout_risk=round(final_burnout, 1),
        goal_achievement_probability=goal_probability,
        learning_growth=round(final_growth, 1),
        productivity_forecast=round(final_productivity, 1),
    )

    timeline = [
        TimelinePoint(
            label=f"{unit} {i + 1}",
            productivity=round(productivity_timeline[i], 1),
            burnout_risk=round(burnout_timeline[i], 1),
            growth=round(growth_timeline[i], 1),
        )
        for i in range(points)
    ]

    return outputs, timeline


async def run_and_store_simulation(
    db: AsyncIOMotorDatabase,
    user_id: ObjectId,
    horizon: Horizon,
    adjustments: BehaviorAdjustments | None = None,
) -> dict:
    outputs, timeline = await compute_simulation(db, user_id, horizon, adjustments)
    doc = {
        "user_id": user_id,
        "horizon": horizon.value,
        "is_what_if": adjustments is not None,
        "adjustments": adjustments.model_dump() if adjustments else None,
        "outputs": outputs.model_dump(),
        "timeline": [t.model_dump() for t in timeline],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db[Collections.SIMULATIONS].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc
