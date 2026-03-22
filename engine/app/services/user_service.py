import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DuplicateError, NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAdminUpdate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("user")
        return user

    async def list_users(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[User], int]:
        return await self._repo.list_users(page, size)

    async def update_profile(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        if data.email is not None and data.email != user.email:
            existing = await self._repo.get_by_email(data.email)
            if existing:
                raise DuplicateError(
                    code="EMAIL_EXISTS", message="Email already in use"
                )
            user.email = data.email
        if data.full_name is not None:
            user.full_name = data.full_name
        return await self._repo.update(user)

    async def admin_update_user(
        self, user_id: uuid.UUID, data: UserAdminUpdate
    ) -> User:
        user = await self.get_user(user_id)
        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if field == "email" and value != user.email:
                existing = await self._repo.get_by_email(value)
                if existing:
                    raise DuplicateError(
                        code="EMAIL_EXISTS", message="Email already in use"
                    )
            setattr(user, field, value)
        return await self._repo.update(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)
        await self._repo.delete(user)
