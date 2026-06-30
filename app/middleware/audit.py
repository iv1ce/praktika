import logging
from datetime import datetime, timezone

from fastapi import Request

logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("audit.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
logger.addHandler(handler)


async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    user_id = getattr(request.state, "user_id", "anonymous")
    logger.info(
        f"USER={user_id} "
        f"METHOD={request.method} "
        f"PATH={request.url.path} "
        f"STATUS={response.status_code}"
    )
    return response
