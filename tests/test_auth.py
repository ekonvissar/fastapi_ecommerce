from app.auth import hash_password, verify_password
from tests.conftest import login_user, register_user


def test_hash_password():
    password = "example_of_password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_hash_password_produces_different_hashes():
    password = "example_of_password"
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)

    assert hashed1 != hashed2
    assert verify_password(password, hashed1)
    assert verify_password(password, hashed2)


def test_refresh_returns_new_access_token(client):
    register_user(client, email="refresh@test.com", password="password123")
    login_user(client, email="refresh@test.com", password="password123")
    response = client.post("/users/refresh")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_without_cookie_returns_401(client):
    response = client.post("/users/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing refresh token"


def test_logout_returns_ok(client):
    register_user(client, email="logout@test.com", password="password123")
    login_user(client, email="logout@test.com", password="password123")

    response = client.post("/users/logout")

    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out"


def test_refresh_token_reuse_returns_401(client):
    register_user(client, email="reuse@test.com", password="password123")
    login_user(client, email="reuse@test.com", password="password123")

    old_refresh_token = client.cookies.get("refresh_token")
    client.post("/users/refresh")

    client.cookies.clear()
    client.cookies.set("refresh_token", old_refresh_token, path="/users")

    response = client.post("/users/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token reuse detected"
