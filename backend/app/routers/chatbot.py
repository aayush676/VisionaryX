from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.ml.chatbot_engine import generate_reply
from app.models.user import ChatbotMode, UserInDB
from app.services.digital_twin_service import recompute_digital_twin
from app.services.memory_service import build_memory_context

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    mode: ChatbotMode | None = None


class ChatResponse(BaseModel):
    reply: str
    mode: ChatbotMode
    twin_state: str


@router.get("/modes")
async def list_modes():
    return [m.value for m in ChatbotMode]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    mode = payload.mode or user.preferences.default_chatbot_mode

    twin = await recompute_digital_twin(db, user.id)
    memory_context = await build_memory_context(db, user.id, limit=5)

    goal_cursor = db[Collections.GOALS].find({"user_id": user.id, "status": "active"}).sort("created_at", -1).limit(5)
    active_goal_titles = [doc["title"] async for doc in goal_cursor]

    reply = generate_reply(
        message=payload.message,
        mode=mode.value,
        twin_state=twin.state.value,
        memory_context=memory_context,
        active_goal_titles=active_goal_titles,
    )

    return ChatResponse(reply=reply, mode=mode, twin_state=twin.state.value)
