# ==========================================
# 多 Agent 协作小说系统 - LLM 客户端
# 支持多提供商、配置验证、重试机制
# ==========================================

from typing import Dict, Any, Optional, List
import asyncio
import httpx
import json
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMClient:
    """
    通用 LLM 调用客户端
    支持火山引擎、阿里云、eggfans 等多家提供商
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "./config/llm_providers.json"
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.default_provider: Optional[str] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        
        # 速率限制跟踪
        self.rate_limits: Dict[str, List[datetime]] = {}

    def configure(self, providers: Dict[str, Dict[str, Any]], default_provider: Optional[str] = None):
        """直接注入提供商配置，避免运行时依赖 JSON 文件"""
        self.providers = providers or {}
        self.default_provider = default_provider
        return self
    
    def load_config(self):
        """从 JSON 配置文件加载所有提供商配置"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"LLM 配置文件不存在：{config_file}")
            self._create_empty_config()
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.providers = config.get('providers', {})
            self.default_provider = config.get('default_provider', '')
            
            logger.info(f"加载了 {len(self.providers)} 个 LLM 提供商")
            logger.info(f"默认提供商：{self.default_provider}")
            
        except Exception as e:
            logger.error(f"LLM 配置加载失败：{e}")
            raise
    
    def _create_empty_config(self):
        """创建空配置模板"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        empty_config = {
            "default_provider": "",
            "providers": {}
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(empty_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"创建空 LLM 配置模板：{config_file}")
    
    def validate_provider(self, provider_name: str) -> Dict[str, Any]:
        """
        验证提供商配置
        
        Returns:
            {"valid": True/False, "error": "错误信息", "errors": ["错误列表"]}
        """
        if provider_name not in self.providers:
            return {
                "valid": False,
                "error": f"提供商不存在：{provider_name}"
            }
        
        config = self.providers[provider_name]
        errors = []
        
        # 验证必填字段
        if not config.get('api_key', '').strip():
            errors.append("API Key 不能为空")
        
        base_url = config.get('base_url', '')
        if not base_url.startswith(('http://', 'https://')):
            errors.append("Base URL 格式不正确")
        
        if not config.get('model', '').strip():
            errors.append("模型名称不能为空")
        
        timeout = config.get('timeout', 60)
        if timeout < 1 or timeout > 600:
            errors.append("超时时间必须在 1-600 秒之间")
        
        if errors:
            return {
                "valid": False,
                "error": "配置验证失败",
                "errors": errors
            }
        
        return {
            "valid": True,
            "message": "配置验证通过"
        }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        调用 LLM 生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            provider: 指定提供商（None 则用默认）
            **kwargs: 额外参数（temperature, max_tokens 等）
        
        Returns:
            生成的文本内容
        """
        provider_name = provider or self.default_provider
        
        if not provider_name:
            raise ValueError("未指定默认提供商，请在配置中设置 default_provider")
        
        if provider_name not in self.providers:
            raise ValueError(f"未知的提供商：{provider_name}")
        
        provider_config = self.providers[provider_name]
        
        # 检查速率限制
        await self._check_rate_limit(provider_name, provider_config)
        
        # 构建请求
        request_body = self._build_request_body(
            prompt=prompt,
            system_prompt=system_prompt,
            provider_config=provider_config,
            **kwargs
        )
        
        # 发送请求（带重试）
        return await self._send_with_retry(provider_config, request_body)
    
    def _build_request_body(
        self,
        prompt: str,
        system_prompt: str,
        provider_config: Dict[str, Any],
        **kwargs
    ) -> Dict:
        """根据提供商配置构建请求体"""
        api_format = provider_config.get('api_format', 'openai')
        
        if api_format == 'openai':
            # OpenAI 兼容格式（火山引擎、阿里云百炼等）
            return {
                "model": provider_config.get('model', ''),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            }
        
        elif api_format == 'aliyun':
            # 阿里云 DashScope 格式
            return {
                "model": provider_config.get('model', ''),
                "input": {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": kwargs
            }
        
        elif api_format == 'custom':
            # 完全自定义格式
            template = provider_config.get('request_template', {})
            return self._fill_template(template, {
                "prompt": prompt,
                "system_prompt": system_prompt,
                **kwargs
            })
        
        else:
            # 默认 OpenAI 格式
            return {
                "model": provider_config.get('model', ''),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            }
    
    async def _send_with_retry(
        self,
        provider_config: Dict[str, Any],
        request_body: Dict,
        max_retries: int = 3
    ) -> str:
        """发送请求，带重试机制"""
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        for attempt in range(max_retries):
            try:
                return await self._send_request(provider_config, request_body)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # 速率限制，等待后重试
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    logger.warning(f"速率限制，等待 {retry_after}秒后重试")
                    await asyncio.sleep(retry_after)
                elif e.response.status_code >= 500:
                    # 服务器错误，等待后重试
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"服务器错误，等待 {wait_time}秒后重试")
                    await asyncio.sleep(wait_time)
                else:
                    # 其他错误，不重试
                    raise
        
        raise Exception(f"请求失败，已重试 {max_retries} 次")
    
    async def _send_request(
        self,
        provider_config: Dict[str, Any],
        request_body: Dict
    ) -> str:
        """发送 HTTP 请求并解析响应"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=provider_config.get('timeout', 60)
            )
        
        base_url = provider_config.get('base_url', '')
        endpoint = provider_config.get('endpoint', '/chat/completions')
        url = f"{base_url}{endpoint}"
        
        headers = self._build_headers(provider_config)
        
        response = await self._http_client.post(
            url,
            headers=headers,
            json=request_body
        )
        response.raise_for_status()
        
        # 解析响应
        return self._parse_response(response.json(), provider_config)
    
    def _build_headers(self, provider_config: Dict[str, Any]) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # API Key 认证
        api_key = provider_config.get('api_key', '')
        auth_type = provider_config.get('auth_type', 'bearer')
        
        if auth_type == 'bearer':
            headers["Authorization"] = f"Bearer {api_key}"
        elif auth_type == 'api_key':
            headers["X-API-Key"] = api_key
        elif auth_type == 'custom':
            header_name = provider_config.get('auth_header', 'Authorization')
            headers[header_name] = api_key
        
        # 额外 headers
        extra_headers = provider_config.get('headers', {})
        headers.update(extra_headers)
        
        return headers
    
    def _parse_response(
        self,
        response: Dict,
        provider_config: Dict[str, Any]
    ) -> str:
        """解析响应，提取生成的文本"""
        response_format = provider_config.get('response_format', 'openai')
        
        if response_format == 'openai':
            # OpenAI 格式：choices[0].message.content
            return response["choices"][0]["message"]["content"]
        
        elif response_format == 'aliyun':
            # 阿里云格式：output.choices[0].message.content
            return response["output"]["choices"][0]["message"]["content"]
        
        elif response_format == 'custom':
            # 自定义路径
            path = provider_config.get('response_path', 'choices[0].message.content')
            return self._extract_by_path(response, path)
        
        else:
            return response["choices"][0]["message"]["content"]
    
    def _extract_by_path(self, data: Dict, path: str) -> str:
        """根据路径从嵌套字典中提取值"""
        keys = path.replace('[', '.').replace(']', '').split('.')
        result = data
        for key in keys:
            if key.isdigit():
                result = result[int(key)]
            else:
                result = result[key]
        return result
    
    async def _check_rate_limit(
        self,
        provider_name: str,
        provider_config: Dict[str, Any]
    ):
        """检查速率限制"""
        rate_limit = provider_config.get('rate_limit')
        if not rate_limit:
            return
        
        now = datetime.now()
        if provider_name not in self.rate_limits:
            self.rate_limits[provider_name] = []
        
        # 清理 1 分钟前的记录
        cutoff = now.timestamp() - 60
        self.rate_limits[provider_name] = [
            t for t in self.rate_limits[provider_name]
            if t.timestamp() > cutoff
        ]
        
        # 检查是否超限
        if len(self.rate_limits[provider_name]) >= rate_limit:
            raise Exception(f"提供商 {provider_name} 速率限制：{rate_limit} 请求/分钟")
        
        # 记录本次请求
        self.rate_limits[provider_name].append(now)
    
    async def test_connection(self, provider: str) -> Dict[str, Any]:
        """
        测试 API 连接
        
        Returns:
            {"status": "success/error", "message": "...", "response_time_ms": 123}
        """
        if provider not in self.providers:
            return {
                "status": "error",
                "message": f"未知的提供商：{provider}"
            }
        
        try:
            start_time = datetime.now()
            
            result = await self.generate(
                prompt="Hello, just a test.",
                system_prompt="You are a helpful assistant.",
                provider=provider
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "success",
                "message": "连接正常",
                "response_time_ms": round(response_time, 2),
                "sample_response": result[:100] + "..." if len(result) > 100 else result
            }
        
        except Exception as e:
            logger.error(f"LLM 连接测试失败：{e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_provider_list(self) -> List[Dict[str, Any]]:
        """获取所有已配置的提供商列表"""
        return [
            {
                "name": name,
                "type": config.get("api_format", "openai"),
                "model": config.get("model", ""),
                "base_url": config.get("base_url", ""),
                "enabled": config.get("enabled", True)
            }
            for name, config in self.providers.items()
        ]
    
    async def close(self):
        """关闭 HTTP 客户端"""
        if self._http_client:
            await self._http_client.aclose()


# ========== 全局实例 ==========

_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
        _llm_client.load_config()
    return _llm_client
