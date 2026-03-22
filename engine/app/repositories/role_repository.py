import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        return await self._session.get(Role, role_id)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_default_roles(self) -> list[Role]:
        stmt = select(Role).where(Role.is_default.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Role]:
        stmt = select(Role).order_by(Role.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, role: Role) -> Role:
        self._session.add(role)
        await self._session.flush()
        return role

    async def update(self, role: Role) -> Role:
        await self._session.flush()
        return role

    async def delete(self, role: Role) -> None:
        await self._session.delete(role)
