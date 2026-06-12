import pytest

from tests.conftest import create_category


def test_get_categories_empty(client):
    response = client.get("/categories/")

    assert response.status_code == 200
    assert response.json() == []


def test_category_response_includes_parent(client):
    parent_response = create_category(client, name="Electronics")
    parent_id = parent_response.json()["id"]

    child_response = create_category(client, name="Phones", parent_id=parent_id)

    assert child_response.status_code == 201
    child = child_response.json()
    assert child["parent_id"] == parent_id
    assert child["parent"] == {"id": parent_id, "name": "Electronics"}


def test_create_and_get_categories(client):
    create_response = client.post(
        "/categories/",
        json={"name": "Phones", "parent_id": None},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Phones"
    assert created["is_active"] is True

    list_responses = client.get("/categories/")
    assert list_responses.status_code == 200
    categories = list_responses.json()
    assert len(categories) == 1
    assert categories[0]["name"] == "Phones"


@pytest.mark.parametrize("invalid_name", ["", "a", "ab"])
def test_create_category_invalid_name_returns_422(client, invalid_name):
    response = client.post(
        "/categories/",
        json={"name": invalid_name, "parent_id": None},
    )
    assert response.status_code == 422


def test_create_category_with_invalid_parent_returns_400(client):
    response = client.post(
        "/categories/",
        json={"name": "Phones", "parent_id": 999},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Parent category not found"


def test_update_category(client):
    create_response = create_category(client, name="Phones")
    category_id = create_response.json()["id"]
    update_response = client.put(
        f"/categories/{category_id}",
        json={"name": "Gadgets", "parent_id": None},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Gadgets"
    list_response = client.get("/categories/")
    assert list_response.json()[0]["name"] == "Gadgets"


def test_delete_category_hides_it_from_list(client):
    create_response = create_category(client, name="Phones")
    category_id = create_response.json()["id"]
    delete_response = client.delete(f"/categories/{category_id}")
    assert delete_response.status_code == 200
    list_response = client.get("/categories/")
    assert list_response.json() == []


def test_update_missing_category_returns_404(client):
    response = client.put(
        "/categories/999",
        json={"name": "Ghost", "parent_id": None},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_missing_category_returns_404(client):
    response = client.delete("/categories/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
