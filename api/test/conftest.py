import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import Base
from app.deps import get_db
from app.main import app as fastapi_app
from app.models import Pet, User, Clinic, Appointment
from datetime import datetime, timedelta, timezone


@pytest.fixture(scope="session")
def engine():
    url = get_settings().test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    eng = create_engine(url)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def db(engine):
    """A session wrapped in a transaction that is rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """A TestClient whose get_db yields the rolled-back test session."""

    def override_get_db():
        yield db

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def make_user(db):
    """Create a user inside the test transaction and return it."""

    def _make(email: str, role: str = "owner") -> User:
        user = User(email=email, name=email.split("@")[0], role=role)
        db.add(user)
        db.flush()
        return user

    return _make


@pytest.fixture
def make_pet(db):
    """Create a pet owned by the given user, inside the test transaction."""

    def _make(owner: User, name: str = "TestPet") -> Pet:
        pet = Pet(owner_id=owner.id, name=name, species="dog")
        db.add(pet)
        db.flush()
        return pet

    return _make



@pytest.fixture
def booked(db, make_user, make_pet):
    """Alice owns a pet and has one scheduled appointment. Returns the pieces."""
    alice = make_user("alice@test.test")
    ben = make_user("ben@test.test")
    pet = make_pet(alice, "Milo")

    clinic = Clinic(owner_id=alice.id, name="Test Clinic")
    db.add(clinic)
    db.flush()

    appt = Appointment(
        pet_id=pet.id,
        clinic_id=clinic.id,
        start_time=datetime.now(timezone.utc) + timedelta(days=3),
        status="scheduled",
    )
    db.add(appt)
    db.flush()

    return {"alice": alice, "ben": ben, "appt": appt}