import pytest
from src.services.user import register_user, switch_role, get_user
from src.database.db import SessionLocal
from src.models.models import User

@pytest.fixture
def session():
    session = SessionLocal()
    yield session
    session.close()

def test_register_user(session):
    telegram_id = "12345"
    name = "Test User"
    user = register_user(telegram_id=telegram_id, name=name, session=session)
    assert user.telegram_id == telegram_id
    assert user.name == name
    assert user.role == "passenger"

def test_switch_role(session):
    telegram_id = "12345"
    name = "Test User"
    user = register_user(telegram_id=telegram_id, name=name, session=session)
    updated_user = switch_role(user_id=user.id, new_role="driver", session=session)
    assert updated_user.role == "driver"

def test_get_user(session):
    telegram_id = "12345"
    name = "Test User"
    register_user(telegram_id=telegram_id, name=name, session=session)
    user = get_user(telegram_id=telegram_id, session=session)
    assert user is not None
    assert user.telegram_id == telegram_id
    assert user.name == name
