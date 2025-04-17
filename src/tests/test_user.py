import pytest
from src.services.user import register_user, switch_role, get_user, delete_user
test_user_telegram_id = "12345"
test_user_name = "Test User"

def test_switch_role():
    register_user(telegram_id=test_user_telegram_id, name=test_user_name)
    resp = switch_role(telegram_id=test_user_telegram_id, new_role="driver")
    assert resp.status_code, f"Error: {resp}"
    user = get_user(test_user_telegram_id)
    assert user['role'] == "driver", f"User role should be 'driver', but got {user['role']}"


def test_get_user():
    register_user(telegram_id=test_user_telegram_id, name=test_user_name)
    user = get_user(telegram_id=test_user_telegram_id)
    assert user is not None
    assert len(user) > 0, "User should exist in the database"
    assert user['telegram_id'] == test_user_telegram_id, f"Telegram ID should match {user}"
    assert user['name'] == test_user_name, f"Name should match {user}"

def test_delete_user():
    user = register_user(telegram_id=test_user_telegram_id, name=test_user_name)
    resp = delete_user(telegram_id=test_user_telegram_id)
    assert resp.status_code, f"Error: {resp}"
    user = get_user(test_user_telegram_id)
    assert len(user) == 0, f"User should not exist in the database after deletion, but {user}"
