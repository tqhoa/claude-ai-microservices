import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_permission
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.services.acl_service import ACLService

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get(
    "/",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("permissions.manage"))],
)
async def list_permissions(
    session: AsyncSession = Depends(get_db),
) -> list[Permission]:
    service = ACLService(session)
    return await service.list_permissions()


@router.post(
    "/",
    response_model=PermissionResponse,
    status_code=201,
    dependencies=[Depends(require_permission("permissions.manage"))],
)
async def create_permission(
    data: PermissionCreate, session: AsyncSession = Depends(get_db)
) -> Permission:
    service = ACLService(session)
    return await service.create_permission(data)


@router.delete(
    "/{permission_id}",
    status_code=204,
    dependencies=[Depends(require_permission("permissions.manage"))],
)
async def delete_permission(
    permission_id: uuid.UUID, session: AsyncSession = Depends(get_db)
) -> None:
    service = ACLService(session)
    await service.delete_permission(permission_id)
