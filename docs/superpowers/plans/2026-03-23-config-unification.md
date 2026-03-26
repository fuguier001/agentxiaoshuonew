# Configuration Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify runtime configuration so the backend, workflow executor, health checks, and frontend config APIs all read and write the same source of truth without exposing plaintext API keys.

**Architecture:** Keep `.env` for infrastructure/runtime environment only, and move all business/runtime LLM provider settings to SQLite via a new `config_service` abstraction. Existing code that reads `ConfigManager`, `ConfigDatabase`, or raw JSON config must be redirected through the service so one path controls validation, masking, default provider resolution, and runtime reads.

**Tech Stack:** Python, FastAPI, SQLite, Pydantic, pytest

---

## File Structure Map

### Create
- `backend/app/services/__init__.py` - service package marker
- `backend/app/services/config_service.py` - single source of truth for provider config, masking, validation, and project config reads/writes
- `backend/tests/test_config_service.py` - unit tests for config service behavior
- `backend/tests/test_config_api.py` - integration-style tests for `/api/config` behavior and secret masking

### Modify
- `backend/app/config.py` - reduce responsibility to environment/system settings only; stop owning runtime LLM provider source of truth
- `backend/app/config_db.py` - normalize DB reads/writes and add helpers needed by service layer
- `backend/app/api/routes.py` - switch `/config`, `/llm/test`, and `/llm/validate` to `config_service`
- `backend/app/workflow_executor.py` - load active provider config from `config_service`
- `backend/app/utils/llm_client.py` - stop loading provider config from JSON file; accept provider config from service
- `backend/app/main.py` - startup logging should use unified config summary instead of stale JSON/config manager paths
- `backend/app/api/health.py` - health checks that mention provider/default config must read from unified service
- `README.md` - document the new config model
- `frontend/src/views/ProjectConfig.vue` - adapt config UI to masked keys and non-destructive save semantics
- `frontend/src/api/client.js` - keep config payload/response handling aligned with new API shape

### Optional cleanup after green
- `backend/config/llm_providers.json` - keep as deprecated template only, or remove runtime references after migration is complete

---

## Behavioral decisions that must be implemented

1. **Runtime source of truth**
   - SQLite is the only runtime source for provider/project config.
   - `.env` remains only for infrastructure/system settings.

2. **Legacy migration behavior**
   - If SQLite has no providers but legacy JSON exists, migrate JSON -> SQLite once at startup/service init.
   - If both exist, SQLite wins.
   - After migration, mark JSON as deprecated/template-only.

3. **Masked secret save semantics**
   - `GET /api/config` must never return plaintext API keys.
   - `api_key: ""` in save payload means **unchanged** if `has_api_key` is already true.
   - Explicit key deletion must use a deliberate flag such as `clear_api_key: true`.

4. **Failure behavior**
   - If default provider is missing, disabled, or incomplete, `get_active_provider_config()` returns a structured failure result or raises one typed domain error consistently.
   - Workflow, health, and test-connection endpoints must surface that same failure in a consistent response shape.

5. **Atomic writes**
   - Saving default provider, providers, and project config must be one transaction; partial writes must roll back.

6. **Service access pattern**
   - `get_config_service()` lives in `backend/app/services/config_service.py` as the singleton/factory entrypoint.
   - FastAPI routes, startup hooks, workflow execution, and health checks all import that single function.

---

### Task 1: Lock the target behavior with tests

**Files:**
- Create: `backend/tests/test_config_service.py`
- Create: `backend/tests/test_config_api.py`

- [ ] **Step 1: Write the failing test for masked config reads**

```python
def test_get_config_masks_api_keys(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "sk-secret-12345678",
                "base_url": "https://example.com",
                "model": "deepseek-v3"
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    result = service.get_runtime_config(mask_secrets=True)

    assert result["providers"]["eggfans"]["api_key"] == ""
    assert result["providers"]["eggfans"]["has_api_key"] is True
    assert result["providers"]["eggfans"]["masked_api_key"].endswith("5678")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_get_config_masks_api_keys -v`

Expected: FAIL because `ConfigService` does not exist yet.

- [ ] **Step 3: Write the failing test for workflow/runtime reads**

```python
def test_get_active_provider_returns_db_backed_runtime_provider(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "sk-live-value",
                "base_url": "https://example.com",
                "model": "deepseek-v3"
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    provider = service.get_active_provider_config()

    assert provider["name"] == "eggfans"
    assert provider["api_key"] == "sk-live-value"
    assert provider["model"] == "deepseek-v3"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_get_active_provider_returns_db_backed_runtime_provider -v`

Expected: FAIL because active provider resolution is still split across modules.

- [ ] **Step 5: Write the failing API test for `/api/config`**

```python
def test_get_config_api_never_returns_plaintext_api_key(client, seeded_config_db):
    response = client.get("/api/config")
    body = response.json()

    assert response.status_code == 200
    assert body["data"]["providers"]["eggfans"]["api_key"] == ""
    assert body["data"]["providers"]["eggfans"]["has_api_key"] is True
    assert "sk-" not in str(body)
```
```

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest backend/tests/test_config_api.py::test_get_config_api_never_returns_plaintext_api_key -v`

Expected: FAIL because current `/api/config` returns plaintext `api_key`.

- [ ] **Step 7: Write the failing test for masked-key save semantics**

```python
def test_save_runtime_config_keeps_existing_key_when_api_key_is_blank(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "sk-existing-9999",
                "base_url": "https://example.com",
                "model": "m1"
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "",
                "base_url": "https://example.com/v2",
                "model": "m2",
                "has_api_key": True,
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    provider = service.get_active_provider_config()
    assert provider["api_key"] == "sk-existing-9999"
    assert provider["base_url"] == "https://example.com/v2"
    assert provider["model"] == "m2"
```

- [ ] **Step 8: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_save_runtime_config_keeps_existing_key_when_api_key_is_blank -v`

Expected: FAIL because blank-key preservation is not implemented.

- [ ] **Step 9: Write the failing migration test**

```python
def test_service_migrates_legacy_json_when_database_is_empty(tmp_path):
    legacy_json = tmp_path / "llm_providers.json"
    legacy_json.write_text(
        json.dumps({
            "default_provider": "eggfans",
            "providers": {
                "eggfans": {
                    "api_key": "sk-legacy",
                    "base_url": "https://example.com",
                    "model": "m1",
                    "enabled": True
                }
            }
        }),
        encoding="utf-8"
    )

    service = ConfigService(db_path=tmp_path / "config.db", legacy_json_path=legacy_json)
    provider = service.get_active_provider_config()

    assert provider["api_key"] == "sk-legacy"
    assert service.get_runtime_config(mask_secrets=True)["default_provider"] == "eggfans"
```

- [ ] **Step 10: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_service_migrates_legacy_json_when_database_is_empty -v`

Expected: FAIL because no migration path exists yet.

- [ ] **Step 11: Write the failing frontend-impact API test**

```python
def test_get_config_api_returns_mask_metadata_for_frontend(client, seeded_config_db):
    body = client.get("/api/config").json()
    provider = body["data"]["providers"]["eggfans"]

    assert "has_api_key" in provider
    assert "masked_api_key" in provider
    assert provider["api_key"] == ""
```
```

- [ ] **Step 12: Run test to verify it fails**

Run: `pytest backend/tests/test_config_api.py::test_get_config_api_returns_mask_metadata_for_frontend -v`

Expected: FAIL because current response shape lacks mask metadata.

- [ ] **Step 13: Write the failing `/api/llm/test` config-error test**

```python
def test_llm_test_endpoint_returns_structured_config_error_when_provider_is_invalid(client, seeded_empty_config_db):
    response = client.post("/api/llm/test", json={"provider": "eggfans"})
    body = response.json()

    assert response.status_code in (200, 400, 422)
    assert body["status"] == "error"
    assert body["data"]["status"] == "error"
    assert "sk-" not in str(body)
```

- [ ] **Step 14: Run test to verify it fails**

Run: `pytest backend/tests/test_config_api.py::test_llm_test_endpoint_returns_structured_config_error_when_provider_is_invalid -v`

Expected: FAIL because `/api/llm/test` failure behavior is not unified.

- [ ] **Step 15: Write the failing workflow config-error test**

```python
@pytest.mark.asyncio
async def test_workflow_executor_returns_structured_error_when_no_active_provider(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    executor = WritingWorkflowExecutor(config_service=service)

    result = await executor.execute_chapter_workflow(
        novel_id="n1",
        chapter_num=1,
        outline="test",
    )

    assert result["status"] == "error"
    assert "LLM" in result["message"] or "provider" in result["message"]
```

- [ ] **Step 16: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_workflow_executor_returns_structured_error_when_no_active_provider -v`

Expected: FAIL because workflow failure behavior is not yet bound to the unified config contract.

- [ ] **Step 17: Write the failing test for explicit key clearing**

```python
def test_save_runtime_config_can_explicitly_clear_api_key(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "sk-existing-9999",
                "base_url": "https://example.com",
                "model": "m1"
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "",
                "clear_api_key": True,
                "base_url": "https://example.com",
                "model": "m1"
            }
        },
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    provider = service.get_provider_config("eggfans", mask_secrets=False)
    assert provider["api_key"] == ""
```

- [ ] **Step 18: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_save_runtime_config_can_explicitly_clear_api_key -v`

Expected: FAIL because explicit key-clearing behavior is not implemented.

- [ ] **Step 19: Write the failing atomic-write rollback test**

```python
def test_save_runtime_config_rolls_back_on_partial_failure(tmp_path, monkeypatch):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={
            "eggfans": {
                "api_key": "sk-old",
                "base_url": "https://old.example.com",
                "model": "m1"
            }
        },
        project_config={"project_name": "Old", "project_path": "./projects/old"},
    )

    monkeypatch.setattr(service, "_save_project_config", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(RuntimeError):
        service.save_runtime_config(
            default_provider="eggfans",
            providers={
                "eggfans": {
                    "api_key": "sk-new",
                    "base_url": "https://new.example.com",
                    "model": "m2"
                }
            },
            project_config={"project_name": "New", "project_path": "./projects/new"},
        )

    provider = service.get_active_provider_config()
    assert provider["api_key"] == "sk-old"
    assert provider["base_url"] == "https://old.example.com"
```

- [ ] **Step 20: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_save_runtime_config_rolls_back_on_partial_failure -v`

Expected: FAIL because atomic rollback is not implemented.

- [ ] **Step 21: Commit the red tests**

```bash
git add backend/tests/test_config_service.py backend/tests/test_config_api.py
git commit -m "test: define unified config behavior"
```

---

### Task 2: Add a unified configuration service

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/config_service.py`
- Modify: `backend/app/config_db.py`

- [ ] **Step 1: Implement `ConfigService` skeleton**

Add a focused class with methods like:

```python
class ConfigService:
    def __init__(self, db_path: str | Path | None = None): ...
    def get_runtime_config(self, mask_secrets: bool = True) -> dict: ...
    def save_runtime_config(self, default_provider: str, providers: dict, project_config: dict) -> dict: ...
    def get_active_provider_config(self) -> dict | None: ...
    def get_provider_config(self, provider_name: str, mask_secrets: bool = True) -> dict | None: ...
    def validate_provider_payload(self, provider_name: str, payload: dict) -> dict: ...
```

- [ ] **Step 2: Add DB helpers needed by the service**

Add or normalize in `config_db.py`:
- provider row -> normalized dict conversion
- project config fetch/update helpers
- default provider update helper returning success/failure deterministically
- transactional save helper for providers/default/project config

- [ ] **Step 3: Implement secret masking in the service**

Use one masking rule only:
- `api_key` returned to frontend = `""`
- `has_api_key` boolean
- `masked_api_key` like `***5678`

- [ ] **Step 4: Implement active provider resolution**

Rules:
- use DB `default_provider`
- provider must exist and be enabled
- provider must have `api_key`, `base_url`, `model`
- return normalized dict including provider `name`

- [ ] **Step 5: Implement legacy JSON -> SQLite one-time migration**

Behavior:
- if DB has zero providers and legacy JSON exists, import providers/default provider into SQLite
- if DB already has providers, skip migration
- log migration summary without logging raw API keys

- [ ] **Step 6: Implement explicit blank-vs-clear API key semantics**

Rules:
- blank `api_key` + `has_api_key=true` => preserve old key
- `clear_api_key=true` => erase stored key
- blank `api_key` without prior stored key => invalid if provider is enabled and required

- [ ] **Step 7: Implement typed service-level error behavior**

Define one consistent error/return contract for:
- no default provider
- missing provider row
- disabled provider
- incomplete provider config

Use that same behavior in workflow, health, and config/test endpoints.

- [ ] **Step 8: Add explicit singleton/factory access**

In `backend/app/services/config_service.py`, add:

```python
_config_service: ConfigService | None = None

def get_config_service() -> ConfigService:
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service
```

This is the only shared access path for routes, startup, workflow, and health code.

- [ ] **Step 9: Run service tests**

Run: `pytest backend/tests/test_config_service.py -v`

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add backend/app/services/__init__.py backend/app/services/config_service.py backend/app/config_db.py backend/tests/test_config_service.py
git commit -m "feat: add unified config service"
```

---

### Task 3: Reduce `config.py` to environment/system config only

**Files:**
- Modify: `backend/app/config.py`

- [ ] **Step 1: Write the failing test for environment-only responsibility**

Add/extend a test asserting `ConfigManager` no longer claims runtime provider ownership.

```python
def test_config_manager_does_not_expose_runtime_provider_payloads():
    manager = get_config_manager()
    payload = manager.to_dict()
    assert "llm_providers" not in payload or payload["llm_providers"] == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_config_manager_does_not_expose_runtime_provider_payloads -v`

Expected: FAIL because `ConfigManager` currently loads JSON provider config.

- [ ] **Step 3: Remove JSON runtime ownership from `ConfigManager`**

Refactor `config.py` so it owns only:
- env-backed app settings
- memory/system settings derived from env
- secret-key/encryption utilities if still needed later

Stop using:
- `_load_llm_providers()` for runtime reads
- `get_default_provider()` as runtime source of truth
- hash logic based on provider JSON content

- [ ] **Step 4: Keep backward compatibility minimal**

If callers still import `get_config_manager()`, ensure it still works for env/system settings, but does not silently read stale provider JSON.

- [ ] **Step 5: Run tests**

Run: `pytest backend/tests/test_config_service.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/config.py backend/tests/test_config_service.py
git commit -m "refactor: limit config manager to environment settings"
```

---

### Task 4: Move API endpoints to `ConfigService`

**Files:**
- Modify: `backend/app/api/routes.py`
- Test: `backend/tests/test_config_api.py`

- [ ] **Step 1: Refactor `GET /api/config` to use `ConfigService`**

Required behavior:
- return `default_provider`
- return `providers`
- never return raw `api_key`
- return normalized `project_config`

- [ ] **Step 2: Refactor `POST /api/config` to use `ConfigService.save_runtime_config()`**

Required behavior:
- save providers, project config, default provider in one path
- validate payload before saving
- remove fake “also updates JSON backup” behavior unless actually implemented
- do not clear existing keys when masked frontend payload sends blank `api_key`
- support explicit deletion only via dedicated field such as `clear_api_key`

- [ ] **Step 3: Refactor `POST /api/llm/validate` to use shared validation rules**

Validation must come from one place only (`ConfigService.validate_provider_payload`).

- [ ] **Step 4: Refactor `POST /api/llm/test` to read provider config from DB-backed service**

Do not rely on stale in-memory JSON-loaded provider lists.

- [ ] **Step 5: Add non-leak tests for config-related endpoints**

Add tests for:
- `GET /api/config`
- `POST /api/config`
- `POST /api/llm/test`
- validation error payloads

Assertions:
- no plaintext `api_key`
- no raw keys in error messages

- [ ] **Step 6: Run API tests**

Run: `pytest backend/tests/test_config_api.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/routes.py backend/tests/test_config_api.py
git commit -m "refactor: route config endpoints through unified service"
```

---

### Task 5: Move runtime LLM execution to the unified config path

**Files:**
- Modify: `backend/app/workflow_executor.py`
- Modify: `backend/app/utils/llm_client.py`

- [ ] **Step 1: Write the failing test for runtime provider lookup**

Add a test proving workflow/runtime code reads DB-backed active provider config, not JSON file config.

```python
def test_workflow_executor_loads_runtime_provider_settings_from_config_service(tmp_path):
    service = ConfigService(db_path=tmp_path / "config.db")
    service.save_runtime_config(
        default_provider="eggfans",
        providers={"eggfans": {"api_key": "sk-live", "base_url": "https://example.com", "model": "m1"}},
        project_config={"project_name": "Demo", "project_path": "./projects/demo"},
    )

    executor = WritingWorkflowExecutor(config_service=service)

    assert executor.runtime_provider["api_key"] == "sk-live"
    assert executor.runtime_provider["name"] == "eggfans"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_config_service.py::test_workflow_executor_loads_runtime_provider_settings_from_config_service -v`

Expected: FAIL because executor currently reads `config_db` directly and is not service-injected.

- [ ] **Step 3: Refactor `WritingWorkflowExecutor` to accept a config service**

Constructor target:

```python
def __init__(self, config_service: ConfigService | None = None):
    self.config_service = config_service or get_config_service()
    self.runtime_provider = None
    self.llm_client = None
    self._load_llm_config()
```

- [ ] **Step 4: Refactor `LLMClient` to stop owning JSON file config**

Preferred direction:
- `LLMClient` becomes a pure request client
- config payload is passed in explicitly
- any config loading responsibility moves to `ConfigService`

- [ ] **Step 5: Ensure workflow failure behavior is explicit**

If no valid active provider exists, workflow executor must fail with a structured, user-facing config error instead of silent `None` behavior.

- [ ] **Step 6: Run focused tests**

Run: `pytest backend/tests/test_config_service.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/workflow_executor.py backend/app/utils/llm_client.py backend/tests/test_config_service.py
git commit -m "refactor: use unified provider config in runtime workflow"
```

---

### Task 6: Update startup logging and configuration documentation

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/health.py`
- Modify: `README.md`

- [ ] **Step 0: Write the failing health behavior tests**

Add tests covering:

```python
def test_health_reports_ready_when_active_provider_exists(...): ...
def test_health_reports_config_error_when_active_provider_missing(...): ...
def test_health_response_never_leaks_plaintext_api_keys(...): ...
```

Run: `pytest backend/tests/test_config_api.py -k health -v`

Expected: FAIL before the health refactor.

- [ ] **Step 1: Update startup logging**

At startup, log:
- env/system settings from `ConfigManager`
- active provider summary from `ConfigService`

Do not log raw API keys.

- [ ] **Step 2: Update README configuration section**

Document clearly:
- `.env` = infrastructure/runtime environment only
- `/api/config` + SQLite = runtime LLM/provider config
- `backend/config/llm_providers.json` is deprecated or template-only

- [ ] **Step 3: Add manual verification instructions**

Verification checklist in README or plan notes:
- save provider from frontend
- refresh config page
- run `GET /api/config`
- confirm `has_api_key=true`, `api_key=""`
- start backend and verify active provider summary logs

- [ ] **Step 4: Update health checks to read unified config state**

If health currently reports config/provider readiness, it must call `ConfigService` instead of stale config manager/provider JSON logic.

- [ ] **Step 5: Add/extend health verification**

Verification:
- healthy when active provider exists and is complete
- degraded/error when default provider is missing/incomplete
- no plaintext API key in health output

- [ ] **Step 6: Add a non-leak logging guard**

Ensure startup logs and config-related error logs never print raw API keys. Add at least one test or log-capture assertion if test infrastructure allows; otherwise add a manual verification script note and code review checklist item.

- [ ] **Step 7: Commit**

```bash
git add backend/app/main.py backend/app/api/health.py README.md
git commit -m "docs: document unified configuration model"
```

---

### Task 7: Adapt frontend config UI to masked secret behavior

**Files:**
- Modify: `frontend/src/views/ProjectConfig.vue`
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Write the failing frontend-oriented behavior note/test**

If frontend test tooling is unavailable, document a manual failing scenario first:
- load config where key exists
- UI shows “已保存” metadata without receiving raw key
- save non-key fields
- stored key remains unchanged

- [ ] **Step 2: Update `ProjectConfig.vue` loading logic**

UI must use:
- `has_api_key`
- `masked_api_key`
- blank input for hidden secret value

It must stop assuming `provider.api_key` contains the saved secret suffix.

- [ ] **Step 3: Update save payload semantics**

When user leaves API key blank and provider already has a saved key:
- send `has_api_key: true`
- do not overwrite with blank secret

When user explicitly clears key:
- send `clear_api_key: true`

- [ ] **Step 4: Verify test-connection UX still works**

The selected provider test must use the server-side stored key when UI does not send a new secret.

- [ ] **Step 5: Manual verification**

Verify in browser:
- existing key shows as saved/masked
- save without changing key preserves key
- replacing key works
- clearing key is explicit and works

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/ProjectConfig.vue frontend/src/api/client.js
git commit -m "fix: support masked provider secrets in config UI"
```

---

### Task 8: Full verification before handoff

**Files:**
- Test: `backend/tests/test_config_service.py`
- Test: `backend/tests/test_config_api.py`

- [ ] **Step 1: Run focused config tests**

Run: `pytest backend/tests/test_config_service.py backend/tests/test_config_api.py -v`

Expected: all PASS.

- [ ] **Step 2: Run smoke import test**

Run: `python -m py_compile backend/app/config.py backend/app/config_db.py backend/app/api/routes.py backend/app/api/health.py backend/app/workflow_executor.py backend/app/utils/llm_client.py backend/app/main.py`

Expected: no output, exit code 0.

- [ ] **Step 3: Manual API verification**

Run backend, then verify:
- `GET /api/config` returns masked values only
- `POST /api/config` persists values
- `POST /api/llm/validate` uses same validation rules as save path
- workflow executor can load active provider config after save
- health endpoint reflects unified config readiness
- legacy JSON migrates only when DB is empty
- save with blank secret preserves stored key

- [ ] **Step 4: Final commit**

```bash
git add backend/app/config.py backend/app/config_db.py backend/app/api/routes.py backend/app/api/health.py backend/app/workflow_executor.py backend/app/utils/llm_client.py backend/app/main.py backend/app/services/__init__.py backend/app/services/config_service.py frontend/src/views/ProjectConfig.vue frontend/src/api/client.js README.md backend/tests/test_config_service.py backend/tests/test_config_api.py
git commit -m "feat: unify runtime configuration flow"
```

---

## Notes for the implementing engineer

- Do **not** try to unify chapter storage, routing, or Celery in this plan. Stay narrowly focused on configuration.
- Keep secrets masked in any API response, logs, or exceptions.
- Prefer adding a thin migration path instead of deleting old JSON-related code immediately if other modules still import it.
- If you must preserve `llm_providers.json`, treat it as template/export only, not runtime source of truth.
- If existing ad hoc tests conflict with this plan, trust the new focused pytest tests over shell-print “success” scripts.
