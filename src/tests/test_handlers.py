import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User as TelegramUser, Message
from telegram.ext import ContextTypes
from src.services.user import register_user, switch_role, get_user
from src.services.trip import create_trip, get_trip

@pytest.fixture
def mock_update():
    user = TelegramUser(id=12345, first_name="Test", is_bot=False)
    message = MagicMock(spec=Message)
    message.reply_text = AsyncMock()
    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = message
    return update

@pytest.fixture
def mock_context():
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)

@patch("src.services.user.register_user")
async def test_start(mock_register_user, mock_update, mock_context):
    await start(mock_update, mock_context)
    mock_register_user.assert_called_once_with(telegram_id=12345, name="Test")
    mock_update.message.reply_text.assert_called_once_with("Welcome, Test! You have been registered as a passenger.")

@patch("src.services.user.get_user")
@patch("src.services.user.switch_role")
async def test_switch_role_command(mock_switch_role, mock_get_user, mock_update, mock_context):
    mock_get_user.return_value = MagicMock(id=1, role="passenger")
    await switch_role_command(mock_update, mock_context)
    mock_switch_role.assert_called_once_with(1, "driver")
    mock_update.message.reply_text.assert_called_once_with("Your role has been switched to driver.")

@patch("src.services.user.get_user")
async def test_switch_role_command_no_user(mock_get_user, mock_update, mock_context):
    mock_get_user.return_value = None
    await switch_role_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("You need to register first using /start.")

@patch("src.services.user.get_user")
@patch("src.services.trip.create_trip")
async def test_create_trip_command(mock_create_trip, mock_get_user, mock_update, mock_context):
    mock_get_user.return_value = MagicMock(id=1, role="driver")
    mock_create_trip.return_value = 101
    await create_trip_command(mock_update, mock_context)
    mock_create_trip.assert_called_once_with(driver_id=1, seats=4, pickup_points=["Point A", "Point B"])
    mock_update.message.reply_text.assert_called_once_with("Trip created successfully with ID: 101.")

@patch("src.services.user.get_user")
async def test_create_trip_command_not_driver(mock_get_user, mock_update, mock_context):
    mock_get_user.return_value = MagicMock(id=1, role="passenger")
    await create_trip_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Only drivers can create trips. Switch to driver role using /switch_role.")

@patch("src.services.trip.get_trip")
async def test_get_trip_command(mock_get_trip, mock_update, mock_context):
    mock_update.message.text = "/get_trip 101"
    mock_context.args = ["101"]
    mock_get_trip.return_value = MagicMock(id=101, driver_id=1, status="active")
    await get_trip_command(mock_update, mock_context)
    mock_get_trip.assert_called_once_with(101)
    mock_update.message.reply_text.assert_called_once_with("Trip ID: 101, Driver ID: 1, Status: active")

async def test_get_trip_command_no_args(mock_update, mock_context):
    mock_context.args = []
    await get_trip_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Please provide a trip ID. Usage: /get_trip <trip_id>")

@patch("src.services.trip.get_trip")
async def test_get_trip_command_not_found(mock_get_trip, mock_update, mock_context):
    mock_context.args = ["101"]
    mock_get_trip.return_value = None
    await get_trip_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Trip not found.")
