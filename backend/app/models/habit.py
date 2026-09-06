from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class HabitLogCreate(BaseModel):
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    study_hours: float = Field(default=0, ge=0, le=24)
    sleep_hours: float = Field(default=0, ge=0, le=24)
    screen_time_hours: float = Field(default=0, ge=0, le=24)
    fitness_minutes: float = Field(default=0, ge=0)
    productivity_score: float = Field(default=0, ge=0, le=100)
    focus_score: float = Field(default=0, ge=0, le=100)
    mood: str = "neutral"
    notes: str = ""


class HabitLogInDB(HabitLogCreate):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
