import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Point to the disposable test database BEFORE importing the app
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/image_metadata_test_db"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("AWS_REGION", "ap-south-1")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket-not-real")

from app.main import app
from app.database import Base, engine
from app.dependencies import get_db

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """Creates fresh tables before each test, drops them after. Keeps tests isolated from each other."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)