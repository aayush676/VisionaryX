from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class AnalyticsSnapshot(BaseModel):
    productivity_score: float = 0
    focus_score: float = 0
    consistency_score: float = 0
    burnout_score: float = 0
    growth_index: float = 0
    career_readiness: float = 0


class AnalyticsInDB(AnalyticsSnapshot):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FuturePredictionInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    horizon: str
    model_version: str = "heuristic-v1"
    predictions: dict[str, float]
    confidence: float = 0.7
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
