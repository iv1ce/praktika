import logging
from datetime import datetime, timezone

from fastapi import Request

from app.services.auth import decode_access_token

logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

_handler = logging.FileHandler("audit.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))

if not logger.handlers:
    logger.addHandler(_handler)


async def audit_middleware(request: Request, call_next):
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ")
        payload = decode_access_token(token)
        user_id = payload.get("sub", "anonymous") if payload else "invalid_token"
    else:
        user_id = "anonymous"

    request.state.user_id = user_id
    ip = request.client.host if request.client else "unknown"

    response = await call_next(request)

    logger.info(
        f"USER={user_id} "
        f"IP={ip} "
        f"METHOD={request.method} "
        f"PATH={request.url.path} "
        f"STATUS={response.status_code}"
    )
    return response
