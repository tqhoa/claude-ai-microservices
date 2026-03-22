import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.role import RoleResponse


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(
        min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    roles: list[RoleResponse] = []


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserAdminUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserList(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    size: int
