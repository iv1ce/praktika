import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import inspect, text

from app.config import BASE_DIR
from app.database import Base, engine
from app.limiter import limiter
from app.routes import auth, users, tasks
from app.middleware.audit import audit_middleware
from app.middleware.headers import security_headers_middleware

logger = logging.getLogger("uvicorn.error")


def _migrate():
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("users")}
    is_pg = "postgresql" in str(engine.url)
    additions = {
        "failed_login_attempts": "INTEGER DEFAULT 0",
        "locked_until": "TIMESTAMP" if is_pg else "DATETIME",
        "last_activity": "TIMESTAMP" if is_pg else "DATETIME",
    }
    for col, dtype in additions.items():
        if col not in columns:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {dtype}"))
                conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _migrate()
    yield


app = FastAPI(
    title="Secure Platform API",
    description="Защищённая веб-платформа с REST API и ролевой моделью доступа",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.middleware("http")(audit_middleware)
app.middleware("http")(security_headers_middleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
