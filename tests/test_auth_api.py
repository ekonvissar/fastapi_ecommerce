from tests.conftest import auth_headers, login_user, register_user


def test_get_cart_without_token_returns_401(client):
    response = client.get("/cart/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_cart_with_valid_token_returns_empty_cart(client):
    register_response = register_user(client)
    assert register_response.status_code == 201
    user = register_response.json()

    response = client.get(
        "/cart/", headers=auth_headers(user["email"], user["id"], user["role"])
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user["id"]
    assert data["items"] == []
    assert data["total_quantity"] == 0


def test_create_product_as_buyer_returns_403(client):
    register_response = register_user(client, email="buyer@test.com", role="buyer")
    user = register_response.json()
    response = client.post(
        "/products/",
        headers=auth_headers(user["email"], user["id"], user["role"]),
        data={
            "name": "Phone",
            "price": "99.99",
            "stock": "5",
            "category_id": "1",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only sellers can perform this action"


def test_login_returns_access_token(client):
    register_user(client, email="login@test.com", password="password123")

    response = login_user(client, email="login@test.com", password="password123")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    register_user(client, email="login@test.com", password="password123")

    response = login_user(client, email="login@test.com", password="wrong")

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_then_access_cart(client):
    register_response = register_user(
        client, email="login@test.com", password="password123"
    )
    user = register_response.json()

    login_response = login_user(client, email="login@test.com", password="password123")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    cart_response = client.get(
        "/cart/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert cart_response.status_code == 200
    assert cart_response.json()["user_id"] == user["id"]
