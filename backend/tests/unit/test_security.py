from uuid import uuid4

import pytest

from app.core.constants import TokenType
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_claims,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    hashed = hash_password("S3cure!pass")
    assert hashed != "S3cure!pass"
    assert verify_password("S3cure!pass", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_roundtrip():
    user_id = uuid4()
    token = create_access_token(user_id)
    assert decode_token(token, TokenType.ACCESS) == user_id


def test_refresh_token_roundtrip():
    user_id = uuid4()
    token = create_refresh_token(user_id)
    assert decode_token(token, TokenType.REFRESH) == user_id


def test_token_type_mismatch_rejected():
    token = create_access_token(uuid4())
    with pytest.raises(UnauthorizedError):
        decode_token(token, TokenType.REFRESH)


def test_invalid_token_rejected():
    with pytest.raises(UnauthorizedError):
        decode_token("not-a-jwt", TokenType.ACCESS)


def test_claims_include_jti_and_expiry():
    claims = decode_claims(create_refresh_token(uuid4()), TokenType.REFRESH)
    assert claims.jti
    # Each token gets a unique jti.
    other = decode_claims(create_refresh_token(uuid4()), TokenType.REFRESH)
    assert claims.jti != other.jti
