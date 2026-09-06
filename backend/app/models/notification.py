from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ACHIEVEMENT = "achievement"
    REMINDER = "reminder"


class NotificationInDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
