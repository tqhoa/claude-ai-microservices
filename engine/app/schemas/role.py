import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.permission import PermissionResponse


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None
    is_default: bool = False
    permission_ids: list[uuid.UUID] = []


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None
    is_default: bool | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_default: bool
    created_at: datetime
    permissions: list[PermissionResponse] = []


class RoleAssign(BaseModel):
    role_ids: list[uuid.UUID]
