import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        # Force certifi's up-to-date CA bundle. Some cloud hosts (Render's
        # Python build included) ship an outdated/mismatched system CA store
        # that fails TLS negotiation against MongoDB Atlas with a bare
        # "TLSV1_ALERT_INTERNAL_ERROR" rather than a clear certificate error.
        _client = AsyncIOMotorClient(
            settings.mongo_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongo_db_name]


async def close_database_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


# Collection name constants keep routers/services from hardcoding strings.
class Collections:
    USERS = "users"
    GOALS = "goals"
    HABIT_LOGS = "habit_logs"
    JOURNALS = "journals"
    SIMULATIONS = "simulations"
    NOTIFICATIONS = "notifications"
    AI_MEMORY = "ai_memory"
    ANALYTICS = "analytics"
    FUTURE_PREDICTIONS = "future_predictions"


async def ensure_indexes() -> None:
    db = get_database()
    await db[Collections.USERS].create_index("email", unique=True)
    await db[Collections.GOALS].create_index("user_id")
    await db[Collections.HABIT_LOGS].create_index([("user_id", 1), ("date", -1)])
    await db[Collections.JOURNALS].create_index([("user_id", 1), ("created_at", -1)])
    await db[Collections.SIMULATIONS].create_index([("user_id", 1), ("created_at", -1)])
    await db[Collections.NOTIFICATIONS].create_index([("user_id", 1), ("created_at", -1)])
    await db[Collections.AI_MEMORY].create_index([("user_id", 1), ("event_type", 1)])
    await db[Collections.ANALYTICS].create_index([("user_id", 1), ("date", -1)])
    await db[Collections.FUTURE_PREDICTIONS].create_index([("user_id", 1), ("horizon", 1), ("created_at", -1)])
