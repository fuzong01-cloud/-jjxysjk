import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./data/test_touyan.db"
os.environ["APP_SECRET_KEY"] = "test-secret"
os.environ["ADMIN_PASSWORD"] = "TestPass123!"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


@pytest.fixture
def authenticated_client(client):
    response = client.post("/login", data={"username": "admin", "password": "TestPass123!"})
    assert response.status_code == 200
    return client
