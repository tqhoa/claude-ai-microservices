import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, perm_id: uuid.UUID) -> Permission | None:
        return await self._session.get(Permission, perm_id)

    async def get_by_codename(self, codename: str) -> Permission | None:
        stmt = select(Permission).where(Permission.codename == codename)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Permission]:
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.codename)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, perm: Permission) -> Permission:
        self._session.add(perm)
        await self._session.flush()
        return perm

    async def delete(self, perm: Permission) -> None:
        await self._session.delete(perm)
