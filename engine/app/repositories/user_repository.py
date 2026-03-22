import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        stmt = select(User).where(
            (User.email == identifier) | (User.username == identifier)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(
        self, page: int = 1, size: int = 20
    ) -> tuple[list[User], int]:
        offset = (page - 1) * size
        count_stmt = select(func.count()).select_from(User)
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(User).offset(offset).limit(size).order_by(User.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def update(self, user: User) -> User:
        await self._session.flush()
        return user

    async def delete(self, user: User) -> None:
        await self._session.delete(user)
