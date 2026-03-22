import uuid
from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_token

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError(message="Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedError(message="Invalid token type")

    user_id = uuid.UUID(payload["sub"])
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError(message="User not found or disabled")

    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise UnauthorizedError(message="Inactive user")
    return user


def require_permission(codename: str) -> Callable:
    """Dependency factory that checks a specific permission.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permission("users.read"))])
    """

    async def permission_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if user.is_superuser:
            return user
        for role in user.roles:
            for perm in role.permissions:
                if perm.codename == codename:
                    return user
        raise ForbiddenError(message=f"Permission '{codename}' required")

    return permission_checker


def require_any_permission(*codenames: str) -> Callable:
    """Require at least one of the listed permissions."""

    async def permission_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if user.is_superuser:
            return user
        user_perms = {
            perm.codename for role in user.roles for perm in role.permissions
        }
        if user_perms & set(codenames):
            return user
        raise ForbiddenError(message=f"One of permissions {codenames} required")

    return permission_checker
