import pytest
from core.auth import get_password_hash, verify_password, create_access_token
from jose import jwt
from core.config import settings

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_jwt_token_creation():
    data = {"sub": "test_user"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "test_user"
    assert "exp" in payload
