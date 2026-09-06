from typing import Annotated, Any

from bson import ObjectId
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema


def _validate_object_id(value: Any) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError("Invalid ObjectId")


# Drop-in type for Mongo's `_id` (and any foreign-key style reference) that
# accepts either a str or ObjectId on the way in and always serializes to str.
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(_validate_object_id),
    PlainSerializer(lambda oid: str(oid), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
