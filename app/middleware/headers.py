from fastapi import Request
from fastapi.responses import Response


async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    script_src = "'self' https://cdn.jsdelivr.net"
    style_src = "'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net"
    img_src = "'self' data: https://fastapi.tiangolo.com"
    if request.url.path in ("/docs", "/redoc"):
        script_src += " 'unsafe-inline'"
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src {script_src}; "
        f"style-src {style_src}; "
        f"img-src {img_src}; "
        f"font-src 'self' https://fonts.gstatic.com; "
        f"base-uri 'self'; "
        f"form-action 'self'"
    )
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
