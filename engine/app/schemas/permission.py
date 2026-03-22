import uuid

from pydantic import BaseModel, ConfigDict, Field


class PermissionCreate(BaseModel):
    codename: str = Field(
        min_length=3, max_length=100, pattern=r"^[a-z_]+\.[a-z_]+$"
    )
    description: str | None = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    codename: str
    description: str | None


class PermissionAssign(BaseModel):
    permission_ids: list[uuid.UUID]
