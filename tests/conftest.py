import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.task import Task
from app.services.auth import hash_password, create_access_token

TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Disable rate limiting in tests
from app.limiter import limiter
limiter.enabled = False


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_token(client):
    client.post("/api/auth/register", json={
        "username": "testuser", "email": "user@test.com", "password": "password123"
    })
    r = client.post("/api/auth/login", json={
        "username": "testuser", "password": "password123"
    })
    return r.json()["access_token"]


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_token(db):
    admin = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass123"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    return token


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def second_user_token(client):
    client.post("/api/auth/register", json={
        "username": "second", "email": "second@test.com", "password": "password123"
    })
    r = client.post("/api/auth/login", json={
        "username": "second", "password": "password123"
    })
    return r.json()["access_token"]


@pytest.fixture
def second_user_headers(second_user_token):
    return {"Authorization": f"Bearer {second_user_token}"}
