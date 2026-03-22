import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DuplicateError, NotFoundError
from app.models.permission import Permission
from app.models.role import Role
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.permission import PermissionCreate
from app.schemas.role import RoleCreate, RoleUpdate


class ACLService:
    def __init__(self, session: AsyncSession) -> None:
        self._role_repo = RoleRepository(session)
        self._perm_repo = PermissionRepository(session)
        self._user_repo = UserRepository(session)

    # --- Roles ---

    async def create_role(self, data: RoleCreate) -> Role:
        if await self._role_repo.get_by_name(data.name):
            raise DuplicateError(
                code="ROLE_EXISTS", message=f"Role '{data.name}' already exists"
            )
        role = Role(
            name=data.name, description=data.description, is_default=data.is_default
        )
        role = await self._role_repo.create(role)
        if data.permission_ids:
            perms = await self._perm_repo.get_by_ids(data.permission_ids)
            role.permissions.extend(perms)
        return role

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate) -> Role:
        role = await self._role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError("role")
        update_fields = data.model_dump(exclude_unset=True)
        if "name" in update_fields:
            existing = await self._role_repo.get_by_name(update_fields["name"])
            if existing and existing.id != role_id:
                raise DuplicateError(
                    code="ROLE_EXISTS", message="Role name already in use"
                )
        for field, value in update_fields.items():
            setattr(role, field, value)
        return await self._role_repo.update(role)

    async def delete_role(self, role_id: uuid.UUID) -> None:
        role = await self._role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError("role")
        await self._role_repo.delete(role)

    async def list_roles(self) -> list[Role]:
        return await self._role_repo.list_all()

    async def assign_roles_to_user(
        self, user_id: uuid.UUID, role_ids: list[uuid.UUID]
    ) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("user")
        roles = [await self._role_repo.get_by_id(rid) for rid in role_ids]
        user.roles = [r for r in roles if r is not None]

    async def assign_permissions_to_role(
        self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
    ) -> Role:
        role = await self._role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError("role")
        perms = await self._perm_repo.get_by_ids(permission_ids)
        role.permissions = perms
        return role

    # --- Permissions ---

    async def create_permission(self, data: PermissionCreate) -> Permission:
        if await self._perm_repo.get_by_codename(data.codename):
            raise DuplicateError(
                code="PERMISSION_EXISTS",
                message=f"Permission '{data.codename}' already exists",
            )
        perm = Permission(codename=data.codename, description=data.description)
        return await self._perm_repo.create(perm)

    async def list_permissions(self) -> list[Permission]:
        return await self._perm_repo.list_all()

    async def delete_permission(self, perm_id: uuid.UUID) -> None:
        perm = await self._perm_repo.get_by_id(perm_id)
        if not perm:
            raise NotFoundError("permission")
        await self._perm_repo.delete(perm)
