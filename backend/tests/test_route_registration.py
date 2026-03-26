from app.main import app


def test_core_route_modules_are_registered():
    paths = {route.path for route in app.routes}

    assert "/api/novels" in paths
    assert "/api/config" in paths
    assert "/api/writing/chapter" in paths
    assert "/api/learning/works" in paths
    assert "/api/agents/status" in paths
    assert "/api/health" in paths
    assert "/api/ai/templates" in paths
    assert "/api/auto/create" in paths
    assert "/api/schools" in paths


def test_split_route_modules_preserve_existing_endpoints():
    endpoint_names = {getattr(route, "name", None) for route in app.routes}

    assert "list_novels" in endpoint_names
    assert "get_config" in endpoint_names
    assert "create_writing_chapter" in endpoint_names
    assert "list_analyzed_works" in endpoint_names
    assert "get_agents_status" in endpoint_names
    assert "list_templates" in endpoint_names
    assert "auto_create_novel" in endpoint_names
    assert "list_schools" in endpoint_names
