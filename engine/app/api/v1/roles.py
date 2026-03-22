import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_permission
from app.models.role import Role
from app.schemas.permission import PermissionAssign
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.acl_service import ACLService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get(
    "/",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def list_roles(session: AsyncSession = Depends(get_db)) -> list[Role]:
    service = ACLService(session)
    return await service.list_roles()


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=201,
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def create_role(
    data: RoleCreate, session: AsyncSession = Depends(get_db)
) -> Role:
    service = ACLService(session)
    return await service.create_role(data)


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def update_role(
    role_id: uuid.UUID, data: RoleUpdate, session: AsyncSession = Depends(get_db)
) -> Role:
    service = ACLService(session)
    return await service.update_role(role_id, data)


@router.delete(
    "/{role_id}",
    status_code=204,
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def delete_role(
    role_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    service = ACLService(session)
    await service.delete_role(role_id)


@router.put(
    "/{role_id}/permissions",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def assign_permissions(
    role_id: uuid.UUID,
    data: PermissionAssign,
    session: AsyncSession = Depends(get_db),
) -> Role:
    service = ACLService(session)
    return await service.assign_permissions_to_role(role_id, data.permission_ids)
