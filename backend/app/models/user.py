from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.common import PyObjectId


class ChatbotMode(str, Enum):
    MENTOR = "mentor"
    FRIEND = "friend"
    STRICT = "strict"
    GROWTH = "growth"


class TwinState(str, Enum):
    BURNOUT = "burnout"
    DISTRACTED = "distracted"
    NOMINAL = "nominal"
    FOCUSED = "focused"
    ELITE_PERFORMER = "elite_performer"


class UserPreferences(BaseModel):
    theme: str = "dark-neon"
    notifications_enabled: bool = True
    default_chatbot_mode: ChatbotMode = ChatbotMode.MENTOR


class DigitalTwinMetrics(BaseModel):
    study_hours: float = 0
    sleep_hours: float = 0
    productivity: float = 0        # 0-100
    focus: float = 0               # 0-100
    fitness: float = 0             # 0-100
    screen_time: float = 0         # hours/day
    consistency: float = 0         # 0-100
    emotional_state: float = 50    # 0 (very negative) - 100 (very positive)


class DigitalTwinSnapshot(BaseModel):
    state: TwinState = TwinState.NOMINAL
    metrics: DigitalTwinMetrics = Field(default_factory=DigitalTwinMetrics)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


class VerifyEmailRequest(BaseModel):
    token: str


class UserUpdate(BaseModel):
    name: str | None = None
    preferences: UserPreferences | None = None


class UserInDB(UserBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    password_hash: str
    role: str = "user"
    is_email_verified: bool = False
    verification_token: str | None = None
    reset_token: str | None = None
    reset_token_expires_at: datetime | None = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    digital_twin: DigitalTwinSnapshot = Field(default_factory=DigitalTwinSnapshot)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPublic(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: PyObjectId = Field(alias="_id")
    name: str
    email: EmailStr
    role: str
    is_email_verified: bool
    preferences: UserPreferences
    digital_twin: DigitalTwinSnapshot
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
