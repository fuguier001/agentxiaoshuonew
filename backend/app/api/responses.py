from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.exceptions import NovelAgentException


def success_response(data: Any = None, message: str = "", status: str = "success") -> Dict[str, Any]:
    payload = {
        "success": True,
        "status": status,
        "data": data,
    }
    if message:
        payload["message"] = message
    return payload


def error_response(message: str, code: str = "HTTP_ERROR", details: Optional[Any] = None, status_code: int = 400) -> JSONResponse:
    body: Dict[str, Any] = {
        "success": False,
        "status": "error",
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict) and "success" in detail and "status" in detail:
            return JSONResponse(status_code=exc.status_code, content=detail)
        if isinstance(detail, dict):
            message = detail.get("message", "请求失败")
            code = detail.get("code", f"HTTP_{exc.status_code}")
            details = detail.get("details")
        else:
            message = str(detail)
            code = f"HTTP_{exc.status_code}"
            details = None
        return error_response(message=message, code=code, details=details, status_code=exc.status_code)

    @app.exception_handler(NovelAgentException)
    async def novel_agent_exception_handler(request: Request, exc: NovelAgentException):
        return error_response(message=exc.message, code=exc.code, details=exc.details, status_code=400)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return error_response(message=str(exc), code="INTERNAL_ERROR", status_code=500)
