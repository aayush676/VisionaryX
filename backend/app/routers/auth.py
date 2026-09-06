from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.database import Collections
from app.core.deps import get_current_user, get_db
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    hash_password,
    verify_password,
)
from app.models.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenPair,
    UserCreate,
    UserInDB,
    UserLogin,
    UserPublic,
    VerifyEmailRequest,
)
from app.services.email_service import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/signup", response_model=UserPublic, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, payload: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing = await db[Collections.USERS].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    verification_token = generate_secure_token()
    now = datetime.now(timezone.utc)
    doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": "user",
        "is_email_verified": False,
        "verification_token": verification_token,
        "reset_token": None,
        "reset_token_expires_at": None,
        "preferences": {"theme": "dark-neon", "notifications_enabled": True, "default_chatbot_mode": "mentor"},
        "digital_twin": {
            "state": "nominal",
            "metrics": {
                "study_hours": 0, "sleep_hours": 0, "productivity": 0, "focus": 0,
                "fitness": 0, "screen_time": 0, "consistency": 0, "emotional_state": 50,
            },
            "updated_at": now,
        },
        "created_at": now,
        "updated_at": now,
    }
    result = await db[Collections.USERS].insert_one(doc)
    doc["_id"] = result.inserted_id

    send_verification_email(payload.email, verification_token)
    return UserPublic(**doc)


@router.post("/verify-email", response_model=UserPublic, response_model_by_alias=False)
async def verify_email(payload: VerifyEmailRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db[Collections.USERS].find_one({"verification_token": payload.token})
    if not doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    await db[Collections.USERS].update_one(
        {"_id": doc["_id"]},
        {"$set": {"is_email_verified": True, "verification_token": None, "updated_at": datetime.now(timezone.utc)}},
    )
    doc["is_email_verified"] = True
    return UserPublic(**doc)


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
async def login(request: Request, payload: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db[Collections.USERS].find_one({"email": payload.email})
    if not doc or not verify_password(payload.password, doc["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user_id = str(doc["_id"])
    return TokenPair(
        access_token=create_access_token(user_id, doc.get("role", "user")),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_access_token(payload_in: RefreshTokenRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    payload = decode_token(payload_in.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    doc = await db[Collections.USERS].find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenPair(
        access_token=create_access_token(user_id, doc.get("role", "user")),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db[Collections.USERS].find_one({"email": payload.email})
    # Always return a generic response so we don't leak which emails exist.
    if doc:
        reset_token = generate_secure_token()
        await db[Collections.USERS].update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            }},
        )
        send_password_reset_email(payload.email, reset_token)
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db[Collections.USERS].find_one({"reset_token": payload.token})
    if not doc or not doc.get("reset_token_expires_at"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    expires_at = doc["reset_token_expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    await db[Collections.USERS].update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "password_hash": hash_password(payload.new_password),
            "reset_token": None,
            "reset_token_expires_at": None,
            "updated_at": datetime.now(timezone.utc),
        }},
    )
    return {"message": "Password has been reset successfully."}


@router.get("/me", response_model=UserPublic, response_model_by_alias=False)
async def get_me(user: UserInDB = Depends(get_current_user)):
    return UserPublic(**user.model_dump(by_alias=True))
