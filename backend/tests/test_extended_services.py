import pytest


@pytest.mark.asyncio
async def test_agent_routes_delegate_to_agent_service(client, monkeypatch):
    from app.api import agent_routes

    class StubAgentService:
        def get_agents_status(self):
            return {"agents": [{"id": "editor"}], "total": 1, "timestamp": "now"}

    monkeypatch.setattr(agent_routes, "get_agent_service", lambda: StubAgentService())
    response = await client.get("/api/agents/status")
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1


@pytest.mark.asyncio
async def test_ai_routes_delegate_to_ai_service(client, monkeypatch):
    from app.api import ai_routes

    class StubAIService:
        def list_templates(self):
            return {"core": [{"id": "tpl-1"}]}

    monkeypatch.setattr(ai_routes, "get_ai_service", lambda: StubAIService())
    response = await client.get("/api/ai/templates")
    body = response.json()
    assert body["success"] is True
    assert body["data"]["core"][0]["id"] == "tpl-1"


@pytest.mark.asyncio
async def test_auto_routes_delegate_to_auto_service(client, monkeypatch):
    from app.api import auto_routes

    class StubAutoService:
        async def create_novel(self, data):
            return {"status": "success", "novel_id": "n-1", "blueprint": {}, "first_chapter": {}}

    monkeypatch.setattr(auto_routes, "get_auto_service", lambda: StubAutoService())
    response = await client.post("/api/auto/create", json={"title": "测试书"})
    body = response.json()
    assert body["success"] is True
    assert body["data"]["novel_id"] == "n-1"


@pytest.mark.asyncio
async def test_school_routes_delegate_to_school_service(client, monkeypatch):
    from app.api import school_routes

    class StubSchoolService:
        def list_schools(self, category=None):
            return {"schools": [{"id": "s1"}], "total": 1}

    monkeypatch.setattr(school_routes, "get_school_service", lambda: StubSchoolService())
    response = await client.get("/api/schools")
    body = response.json()
    assert body["success"] is True
    assert body["data"]["schools"][0]["id"] == "s1"
