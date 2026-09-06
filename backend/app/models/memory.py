from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class MemoryEventType(str, Enum):
    GOAL_CREATED = "goal_created"
    GOAL_COMPLETED = "goal_completed"
    GOAL_ABANDONED = "goal_abandoned"
    STREAK_BROKEN = "streak_broken"
    MILESTONE_REACHED = "milestone_reached"
    EMOTIONAL_PATTERN = "emotional_pattern"
    BURNOUT_WARNING = "burnout_warning"
    SIMULATION_RUN = "simulation_run"


class AIMemoryInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    event_type: MemoryEventType
    summary: str
    related_goal_id: PyObjectId | None = None
    importance: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
