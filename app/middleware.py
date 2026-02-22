import time
import logging
import json
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import settings

# Configure JSON logger
logger = logging.getLogger("sprintsync")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

# In-memory metrics store
metrics = {
    "http_requests_total": 0,
    "errors_total": 0,
    "ai_suggest_calls_total": 0,
    "total_latency_ms": 0,
    "routes": {},
}


def extract_user_id(request: Request) -> str:
    try:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return "anonymous"
        token = auth.split(" ")[1]
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload.get("sub", "anonymous")
    except JWTError:
        return "anonymous"


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t1 = time.perf_counter()
        user_id = extract_user_id(request)
        status_code = 500

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as exc:
            metrics["errors_total"] += 1
            logger.exception(
                json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "method": request.method,
                    "path": request.url.path,
                    "user_id": user_id,
                    "status_code": 500,
                    "error": str(exc),
                })
            )
            raise

        finally:
            latency_ms = round((time.perf_counter() - t1) * 1000, 2)
            route_key = f"{request.method} {request.url.path}"

            # Update metrics
            metrics["http_requests_total"] += 1
            metrics["total_latency_ms"] += latency_ms
            metrics["routes"][route_key] = (
                metrics["routes"].get(route_key, 0) + 1
            )
            if request.url.path == "/ai/suggest":
                metrics["ai_suggest_calls_total"] += 1
            if status_code >= 500:
                metrics["errors_total"] += 1

            # Emit structured log
            logger.info(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "status_code": status_code,
                "latency_ms": latency_ms,
            }))