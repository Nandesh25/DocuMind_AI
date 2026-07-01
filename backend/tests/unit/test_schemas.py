import pytest
from pydantic import ValidationError

from app.schemas.auth_schema import RegisterRequest, validate_password_strength
from app.schemas.common import PageParams


def test_password_strength_accepts_valid():
    assert validate_password_strength("S3cure!pass") == "S3cure!pass"


@pytest.mark.parametrize(
    "bad",
    ["short1!", "NoDigits!!", "NoSymbol123", "lowercase1!"],
)
def test_password_strength_rejects_weak(bad):
    with pytest.raises(ValueError):
        validate_password_strength(bad)


def test_register_request_valid():
    req = RegisterRequest(
        email="user@corp.com", password="S3cure!pass", full_name="Jane Doe"
    )
    assert req.email == "user@corp.com"


def test_register_request_rejects_weak_password():
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="user@corp.com", password="weak", full_name="Jane Doe"
        )


def test_page_params_offset():
    assert PageParams(page=1, size=20).offset == 0
    assert PageParams(page=3, size=20).offset == 40
