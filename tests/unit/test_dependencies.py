"""Tests for the JWT authentication dependency."""

import pytest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from com.aibert.dosw.dependencies import get_current_user


async def test_valid_token_returns_user_dict():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-tok")
    with patch(
        "com.aibert.dosw.dependencies.jwt.decode",
        return_value={"sub": "user-123", "name": "Test"},
    ):
        result = get_current_user(credentials)
    assert result["user_id"] == "user-123"
    assert result["token"] == "valid-tok"
    assert result["payload"]["sub"] == "user-123"


async def test_missing_sub_raises_401():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok")
    with patch(
        "com.aibert.dosw.dependencies.jwt.decode",
        return_value={"email": "user@example.com"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
    assert exc_info.value.status_code == 401
    assert "missing 'sub' claim" in exc_info.value.detail


async def test_jwt_error_raises_401():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-tok")
    with patch(
        "com.aibert.dosw.dependencies.jwt.decode", side_effect=JWTError("expired")
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


async def test_jwt_error_includes_www_authenticate_header():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad")
    with patch(
        "com.aibert.dosw.dependencies.jwt.decode", side_effect=JWTError("expired")
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
