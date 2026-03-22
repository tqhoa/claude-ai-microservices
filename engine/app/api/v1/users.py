import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_permission
from app.models.user import User
from app.schemas.role import RoleAssign
from app.schemas.user import UserAdminUpdate, UserList, UserResponse, UserUpdate
from app.services.acl_service import ACLService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> User:
    service = UserService(session)
    return await service.update_profile(user.id, data)


@router.get(
    "/",
    response_model=UserList,
    dependencies=[Depends(require_permission("users.read"))],
)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> dict:
    service = UserService(session)
    items, total = await service.list_users(page, size)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users.read"))],
)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> User:
    service = UserService(session)
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users.update"))],
)
async def admin_update_user(
    user_id: uuid.UUID,
    data: UserAdminUpdate,
    session: AsyncSession = Depends(get_db),
) -> User:
    service = UserService(session)
    return await service.admin_update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[Depends(require_permission("users.delete"))],
)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = UserService(session)
    await service.delete_user(user_id)


@router.put(
    "/{user_id}/roles",
    status_code=204,
    dependencies=[Depends(require_permission("roles.manage"))],
)
async def assign_roles(
    user_id: uuid.UUID,
    data: RoleAssign,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = ACLService(session)
    await service.assign_roles_to_user(user_id, data.role_ids)
