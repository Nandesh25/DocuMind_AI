from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings
from app.core.constants import TokenType
from app.core.exceptions import UnauthorizedError

# bcrypt only considers the first 72 bytes of a password.
_BCRYPT_MAX_BYTES = 72


@dataclass(frozen=True)
class TokenClaims:
    """Decoded token claims."""

    subject: UUID
    jti: str
    expires_at: datetime


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8")[:_BCRYPT_MAX_BYTES], hashed.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def _create_token(subject: UUID, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "type": token_type.value,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: UUID) -> str:
    return _create_token(
        subject,
        TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: UUID) -> str:
    return _create_token(
        subject,
        TokenType.REFRESH,
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def decode_claims(token: str, expected_type: TokenType) -> TokenClaims:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if payload.get("type") != expected_type.value:
        raise UnauthorizedError("Invalid token type")

    subject = payload.get("sub")
    jti = payload.get("jti")
    exp = payload.get("exp")
    if subject is None or jti is None or exp is None:
        raise UnauthorizedError("Malformed token")
    try:
        return TokenClaims(
            subject=UUID(subject),
            jti=str(jti),
            expires_at=datetime.fromtimestamp(int(exp), tz=UTC),
        )
    except (ValueError, TypeError) as exc:
        raise UnauthorizedError("Malformed token subject") from exc


def decode_token(token: str, expected_type: TokenType) -> UUID:
    """Convenience helper returning only the subject (user id)."""
    return decode_claims(token, expected_type).subject

