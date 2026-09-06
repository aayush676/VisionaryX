from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class EmotionScores(BaseModel):
    stress: float = 0
    burnout: float = 0
    focus: float = 0
    happiness: float = 0
    anxiety: float = 0
    motivation: float = 0


class JournalCreate(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class JournalInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    content: str
    sentiment_score: float = 0     # -1 (negative) .. 1 (positive)
    dominant_emotion: str = "neutral"
    emotions: EmotionScores = Field(default_factory=EmotionScores)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
