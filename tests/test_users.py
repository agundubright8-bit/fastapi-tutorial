from app import schemas
from uuid import uuid4
import pytest
from app import oauth2
from fastapi import HTTPException


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}


def test_create_user(client):
    email = f"{uuid4()}@example.com" 
    response = client.post("/users/", json={"email": email, "password": "password"})
    new_user = schemas.UserOut(**response.json())
    assert response.status_code == 201
    assert new_user.email == email


def test_login_user(client, test_user):
    response = client.post("/auth/login", data={"username": test_user["email"], "password": "password"})
    assert response.status_code == 200
    token = schemas.Token(**response.json())
    payload = oauth2.verify_access_token(token.access_token, credentials_exception=HTTPException(status_code=401, detail="Could not validate credentials"))
    assert payload.id == test_user["id"]
    assert token.token_type == "bearer"
    assert token.access_token


@pytest.mark.parametrize("email, password, expected_status", [
    ("wrong@example.com", "password", 403),
    ("test@example.com", "wrongpassword", 403),
    (None, "password", 422),
    ("test@example.com", None, 422),
    (None, None, 422)
])


def test_incorrect_login(client, test_user, email, password, expected_status):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert response.status_code == expected_status