from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class Horizon(str, Enum):
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    TWELVE_MONTHS = "12m"


class SimulationOutputs(BaseModel):
    career_readiness: float = 0        # 0-100
    burnout_risk: float = 0            # 0-100
    goal_achievement_probability: float = 0  # 0-100
    learning_growth: float = 0         # 0-100
    productivity_forecast: float = 0   # 0-100


class TimelinePoint(BaseModel):
    label: str          # e.g. "Week 1", "Month 2"
    productivity: float
    burnout_risk: float
    growth: float


class BehaviorAdjustments(BaseModel):
    """Deltas applied on top of current habits for a What-If run."""
    study_hours_delta: float = 0
    sleep_hours_delta: float = 0
    screen_time_delta: float = 0
    fitness_minutes_delta: float = 0
    consistency_delta: float = 0


class SimulationRequest(BaseModel):
    horizon: Horizon = Horizon.THREE_MONTHS
    adjustments: BehaviorAdjustments | None = None  # None => baseline simulation


class SimulationInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    horizon: Horizon
    is_what_if: bool = False
    adjustments: BehaviorAdjustments | None = None
    outputs: SimulationOutputs
    timeline: list[TimelinePoint] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifePathCompareRequest(BaseModel):
    horizon: Horizon = Horizon.SIX_MONTHS
    paths: list[BehaviorAdjustments] = Field(min_length=2, max_length=4)
    labels: list[str] | None = None
