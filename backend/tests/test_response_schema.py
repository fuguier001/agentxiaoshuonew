import pytest


@pytest.mark.asyncio
async def test_success_response_contains_success_boolean(client):
    response = await client.get("/api/novels")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["status"] == "success"
    assert "data" in body


@pytest.mark.asyncio
async def test_http_error_response_uses_structured_error_shape(client):
    response = await client.get("/api/novels/non-existent-id")
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert body["status"] == "error"
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]


@pytest.mark.asyncio
async def test_llm_test_error_response_uses_same_error_shape(client):
    response = await client.post("/api/llm/test", json={})
    body = response.json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["status"] == "error"
    assert body["error"]["message"]
