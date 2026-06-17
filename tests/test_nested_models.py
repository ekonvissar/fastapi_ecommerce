from tests.conftest import (
    auth_headers,
    create_category,
    create_product,
    register_seller,
    register_user,
)


def _seller_setup(client):
    seller = register_seller(client).json()
    headers = auth_headers(seller["email"], seller["id"], seller["role"])
    category_id = create_category(client).json()["id"]
    return seller, headers, category_id


def test_product_response_includes_category(client):
    _, seller_headers, category_id = _seller_setup(client)

    response = create_product(client, seller_headers, category_id, name="iPhone")

    assert response.status_code == 201
    product = response.json()
    assert product["category_id"] == category_id
    assert product["category"] == {"id": category_id, "name": "Phones"}

    get_response = client.get(f"/products/{product['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["category"]["name"] == "Phones"


def test_review_response_includes_user(client):
    buyer = register_user(client, email="buyer@test.com").json()
    buyer_headers = auth_headers(buyer["email"], buyer["id"], buyer["role"])
    _, seller_headers, category_id = _seller_setup(client)
    product_id = create_product(client, seller_headers, category_id).json()["id"]

    response = client.post(
        "/reviews/",
        headers=buyer_headers,
        json={"product_id": product_id, "comment": "Great phone", "grade": 5},
    )

    assert response.status_code == 201
    review = response.json()
    assert review["user_id"] == buyer["id"]
    assert review["user"] == {"id": buyer["id"], "email": buyer["email"]}
    assert review["product"] == {"id": product_id, "name": "Phone"}


def test_get_all_reviews_includes_user_and_product(client):
    buyer = register_user(client, email="buyer@test.com").json()
    buyer_headers = auth_headers(buyer["email"], buyer["id"], buyer["role"])
    _, seller_headers, category_id = _seller_setup(client)
    product_id = create_product(
        client, seller_headers, category_id, name="Galaxy"
    ).json()["id"]

    client.post(
        "/reviews/",
        headers=buyer_headers,
        json={"product_id": product_id, "comment": "Nice", "grade": 4},
    )

    response = client.get("/reviews/")
    assert response.status_code == 200
    review = response.json()[0]
    assert review["user"]["email"] == buyer["email"]
    assert review["product"] == {"id": product_id, "name": "Galaxy"}


def test_cart_item_includes_product_with_category(client):
    buyer = register_user(client, email="buyer@test.com").json()
    buyer_headers = auth_headers(buyer["email"], buyer["id"], buyer["role"])
    _, seller_headers, category_id = _seller_setup(client)
    product_id = create_product(client, seller_headers, category_id).json()["id"]

    client.post(
        "/cart/items/",
        headers=buyer_headers,
        json={"product_id": product_id, "quantity": 2},
    )

    response = client.get("/cart/", headers=buyer_headers)
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["product"]["category"] == {"id": category_id, "name": "Phones"}
    assert item["product"]["name"] == "Phone"


def test_order_item_includes_product_snapshot(client):
    buyer = register_user(client, email="buyer@test.com").json()
    buyer_headers = auth_headers(buyer["email"], buyer["id"], buyer["role"])
    _, seller_headers, category_id = _seller_setup(client)
    product_id = create_product(
        client, seller_headers, category_id, name="Pixel", stock="5"
    ).json()["id"]

    client.post(
        "/cart/items/",
        headers=buyer_headers,
        json={"product_id": product_id, "quantity": 1},
    )

    order_response = client.post("/orders/checkout", headers=buyer_headers)
    assert order_response.status_code == 201
    order = order_response.json()
    snapshot = order["items"][0]["product"]
    assert snapshot == {"id": product_id, "name": "Pixel", "image_url": None}
    assert "stock" not in snapshot
    assert "price" not in snapshot
