from xata.client import XataClient  # Use Xata client for database interactions
from src.services.user import get_telegram_handler  # Ensure correct relative import
from src.utils.template_renderer import render_template  # Ensure correct relative import
from sentry_sdk import capture_exception
from datetime import datetime

xata = XataClient()

async def create_trip(driver_id: str, seats: int, pickup_points: list):
    """
    Create a new trip in the database.
    """
    try:
        trip_data = {
            "driver_id": driver_id,
            "status": "active",
            "seats": seats,
            "pickup_points": pickup_points,
            "created_at": datetime.utcnow().isoformat(),
        }
        trip = await xata.table("trips").create(trip_data)
        return trip["id"]
    except Exception as e:
        capture_exception(e)
        return None

async def list_trips():
    """
    List all trips from the database.
    """
    try:
        trips = await xata.table("trips").get_all()
        return [
            {
                "id": trip["id"],
                "driver_id": trip["driver_id"],
                "status": trip["status"],
                "seats": trip.get("seats", "Unknown"),
            }
            for trip in trips
        ]
    except Exception as e:
        capture_exception(e)
        return []

async def get_trip(trip_id: str):
    """
    Retrieve details of a specific trip by ID.
    """
    try:
        trip = await xata.table("trips").read(trip_id)
        if trip:
            trip_details = {
                "id": trip["id"],
                "driver_id": trip["driver_id"],
                "status": trip["status"],
                "created_at": trip["created_at"],
                "pickup_points": trip.get("pickup_points", []),
                "driver_handler": await get_telegram_handler(trip["driver_id"]),
            }
            # Example template rendering
            template = "Trip {id} by Driver {driver_handler} is {status}. Created at {created_at}."
            trip_details["rendered"] = render_template(template, trip_details)
            return trip_details
        return None
    except Exception as e:
        capture_exception(e)
        return None

