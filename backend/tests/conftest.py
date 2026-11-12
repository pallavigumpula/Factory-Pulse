import os
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_factorypulse.db"

from backend.app.config import settings
from backend.app.database import Base
from backend.app.models.user import User
from backend.app.utils.security import create_access_token
from backend.data_generator.generator import ManufacturingDataGenerator

test_engine = create_engine("sqlite:///./test_factorypulse.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    generator = ManufacturingDataGenerator(seed=20261022, mode="starter")
    generator.run(db=db, export_dir="data")
    db.close()
    yield TestingSessionLocal

@pytest.fixture
def db(setup_test_db):
    session = setup_test_db()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def admin_user(db):
    return db.query(User).filter(User.username == "admin").first()

@pytest.fixture
def operator_user(db):
    return db.query(User).filter(User.username == "operator1").first()

@pytest.fixture
def maint_user(db):
    return db.query(User).filter(User.username == "maint1").first()

@pytest.fixture
def qc_user(db):
    return db.query(User).filter(User.username == "qc1").first()

@pytest.fixture
def planner_user(db):
    return db.query(User).filter(User.username == "planner1").first()
