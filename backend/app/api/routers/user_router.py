from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, UserServiceDep
from app.schemas.user_schema import PasswordChange, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate, current_user: CurrentUser, service: UserServiceDep
) -> UserResponse:
    user = await service.update_profile(current_user, data)
    return UserResponse.model_validate(user)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChange, current_user: CurrentUser, service: UserServiceDep
) -> None:
    await service.change_password(current_user, data)
    return None
