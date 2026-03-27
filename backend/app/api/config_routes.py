from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import json
import logging

from app.services.config_service import get_config_service
from app.api.responses import error_response, success_response
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["配置管理"])


@router.get("/config")
async def get_config():
    try:
        return success_response(get_config_service().get_runtime_config(mask_secrets=True))
    except Exception as e:
        logger.error(f"获取配置失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(config_data: Dict[str, Any]):
    try:
        logger.info(f"收到配置数据：{json.dumps(config_data, ensure_ascii=False)[:1000]}")
        data = get_config_service().save_runtime_config(
            default_provider=config_data.get("default_provider", ""),
            providers=config_data.get("providers", {}),
            project_config=config_data.get("project_config", {}),
        )
        return success_response(data, "配置已保存到数据库，下次访问会自动加载")
    except Exception as e:
        logger.error(f"更新配置失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/test")
async def test_llm_connection(data: Dict[str, Any]):
    try:
        provider = data.get("provider")
        if not provider:
            return error_response("未指定提供商", code="LLM_PROVIDER_REQUIRED", status_code=400)
        provider_config = get_config_service().get_provider_config(provider, mask_secrets=False)
        if not provider_config or not provider_config.get("api_key"):
            return error_response("提供商未配置或缺少 API Key", code="LLM_PROVIDER_NOT_CONFIGURED", status_code=400)

        # 与 workflow_executor._call_llm 保持一致，避免测试连接和实际创作请求格式不一致
        base_url = provider_config.get("base_url", "").rstrip("/")
        api_key = provider_config.get("api_key", "")
        model = provider_config.get("model", "")
        timeout = provider_config.get("timeout", 60)
        # 使用配置中的 endpoint，如果没有则默认使用 /v1/chat/completions
        endpoint = provider_config.get("endpoint", "/v1/chat/completions")
        if not endpoint:
            endpoint = "/v1/chat/completions"

        logger.info(f"测试连接 - provider: {provider}, base_url: {base_url}, endpoint: {endpoint}")

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello, just a connection test."}
            ],
            "max_tokens": 32,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}{endpoint}",
                headers=headers,
                json=payload,
            )

        if response.status_code == 200:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            return success_response({
                "status": "success",
                "message": "连接正常",
                "sample_response": content[:100] + "..." if len(content) > 100 else content,
            })

        return error_response(
            f"上游接口返回 {response.status_code}: {response.text[:200]}",
            code="LLM_TEST_FAILED",
            status_code=400,
        )
    except Exception as e:
        logger.error(f"测试 LLM 连接失败：{e}")
        return error_response(str(e), code="LLM_TEST_FAILED", status_code=500)


@router.post("/llm/validate")
async def validate_llm_config(config: Dict[str, Any]):
    try:
        provider = config.get("provider") or config.get("name") or "provider"
        payload = config.get("config", config)
        result = get_config_service().validate_provider_payload(provider, payload)
        if result.get("valid"):
            return success_response(result)
        return error_response(result.get("error", "配置验证失败"), code="LLM_CONFIG_INVALID", details=result.get("errors"), status_code=400)
    except Exception as e:
        logger.error(f"验证 LLM 配置失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
