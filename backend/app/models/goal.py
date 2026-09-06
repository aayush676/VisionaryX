from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


class GoalTask(BaseModel):
    id: str
    title: str
    frequency: str  # "daily" | "weekly" | "monthly"
    is_done: bool = False
    due_date: datetime | None = None


class GoalCreate(BaseModel):
    title: str
    description: str = ""
    category: str = "general"
    target_date: datetime | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: GoalStatus | None = None
    progress: float | None = Field(default=None, ge=0, le=100)


class GoalInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    title: str
    description: str = ""
    category: str = "general"
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0
    target_date: datetime | None = None
    tasks: list[GoalTask] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    last_progress_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
