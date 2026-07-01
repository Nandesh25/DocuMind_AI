from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.interfaces.i_user_repository import IUserRepository
from app.schemas.user_schema import PasswordChange, UserUpdate


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self._users = user_repo

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        user.full_name = data.full_name
        return await self._users.add(user)

    async def change_password(self, user: User, data: PasswordChange) -> None:
        if not verify_password(data.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect.")
        if verify_password(data.new_password, user.password_hash):
            raise ValidationError("New password must differ from the current one.")
        user.password_hash = hash_password(data.new_password)
        await self._users.add(user)
