from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister, session: AsyncSession = Depends(get_db)
) -> User:
    service = AuthService(session)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin, session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(session)
    return await service.login(data.username, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: TokenRefresh, session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(session)
    return await service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
