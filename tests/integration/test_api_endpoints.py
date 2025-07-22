import uuid
import requests

from app.models.user import User


def _register_and_login(base_url: str, user_data: dict) -> dict:
    """Helper to register a user and return the login token data."""
    reg_resp = requests.post(f"{base_url}/auth/register", json=user_data)
    assert reg_resp.status_code == 201, reg_resp.text
    login_payload = {"username": user_data["username"], "password": user_data["password"]}
    login_resp = requests.post(f"{base_url}/auth/login", json=login_payload)
    assert login_resp.status_code == 200, login_resp.text
    return login_resp.json()


def test_register_login_persists_user(fastapi_server, db_session):
    base_url = fastapi_server.rstrip("/")
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test{uuid.uuid4()}@example.com",
        "username": f"user_{uuid.uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    token_data = _register_and_login(base_url, user_data)

    db_user = db_session.query(User).filter_by(username=user_data["username"]).first()
    assert db_user is not None
    assert token_data["user_id"] == str(db_user.id)


def test_create_calculation_invalid_type(fastapi_server):
    base_url = fastapi_server.rstrip("/")
    user_data = {
        "first_name": "Calc",
        "last_name": "InvalidType",
        "email": f"calc.invalid{uuid.uuid4()}@example.com",
        "username": f"calc_invalid_{uuid.uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    token_data = _register_and_login(base_url, user_data)
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    payload = {"type": "modulus", "inputs": [1, 2], "user_id": "ignored"}
    resp = requests.post(f"{base_url}/calculations", json=payload, headers=headers)
    assert resp.status_code == 422 or resp.status_code == 400


def test_create_calculation_divide_by_zero(fastapi_server):
    base_url = fastapi_server.rstrip("/")
    user_data = {
        "first_name": "Calc",
        "last_name": "DivZero",
        "email": f"calc.divzero{uuid.uuid4()}@example.com",
        "username": f"calc_divzero_{uuid.uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    token_data = _register_and_login(base_url, user_data)
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    payload = {"type": "division", "inputs": [10, 0], "user_id": "ignored"}
    resp = requests.post(f"{base_url}/calculations", json=payload, headers=headers)
    assert resp.status_code == 400