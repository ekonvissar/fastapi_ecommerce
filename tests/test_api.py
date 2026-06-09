def test_openapi_schema(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "FastAPI интеренет-магазин"
    assert "paths" in data
