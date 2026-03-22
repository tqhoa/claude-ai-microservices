import uuid

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import UnauthorizedError
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserRegister
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)

    async def register(self, data: UserRegister) -> User:
        from app.exceptions import DuplicateError

        if await self._user_repo.get_by_email(data.email):
            raise DuplicateError(code="EMAIL_EXISTS", message="Email already registered")
        if await self._user_repo.get_by_username(data.username):
            raise DuplicateError(
                code="USERNAME_EXISTS", message="Username already taken"
            )

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        user = await self._user_repo.create(user)

        default_roles = await self._role_repo.get_default_roles()
        if default_roles:
            user.roles = default_roles
            await self._session.flush()

        await self._session.refresh(user, ["roles"])
        return user

    async def login(self, identifier: str, password: str) -> TokenResponse:
        user = await self._user_repo.get_by_email_or_username(identifier)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(message="Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError(message="Account is disabled")

        access_token, expires_in = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token_str)
        except JWTError:
            raise UnauthorizedError(message="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedError(message="Invalid token type")

        user_id = uuid.UUID(payload["sub"])
        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError(message="User not found or disabled")

        access_token, expires_in = create_access_token(user.id)
        new_refresh = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=expires_in,
        )
