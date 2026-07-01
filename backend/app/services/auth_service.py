from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_claims,
    hash_password,
    verify_password,
)
from app.config.settings import settings
from app.core.constants import TokenType
from app.models.user import User
from app.repositories.interfaces.i_token_repository import ITokenRepository
from app.repositories.interfaces.i_user_repository import IUserRepository
from app.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    def __init__(self, user_repo: IUserRepository, token_repo: ITokenRepository):
        self._users = user_repo
        self._tokens = token_repo

    async def register(self, data: RegisterRequest) -> User:
        existing = await self._users.get_by_email(data.email)
        if existing:
            raise ConflictError("An account with this email already exists.")
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
        )
        return await self._users.add(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise ForbiddenError("This account is inactive.")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        claims = decode_claims(refresh_token, TokenType.REFRESH)
        if await self._tokens.is_revoked(claims.jti):
            raise UnauthorizedError("Refresh token has been revoked.")

        user = await self._users.get_by_id(claims.subject)
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid refresh token.")

        # Rotate: revoke the presented refresh token, then issue a new pair.
        await self._tokens.revoke(claims.jti, claims.expires_at)
        return self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        """Invalidate the presented refresh token (best-effort)."""
        try:
            claims = decode_claims(refresh_token, TokenType.REFRESH)
        except UnauthorizedError:
            return
        await self._tokens.revoke(claims.jti, claims.expires_at)

    def _issue_tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
