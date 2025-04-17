from sentry_sdk import capture_exception  # Import Sentry's exception capture function
from xata.client import XataClient  # Ensure Xata client is imported
from httpx import Timeout  # Import Timeout for setting request timeouts

xata = XataClient()  # Initialize Xata client with a 5-second timeout

async def get_full_status():
    try:
        users = await xata.table("users").get_all()
        trips = await xata.table("trips").get_all()
        pickup_points = await xata.table("pickup_points").get_all()

        status = "Database Status:\n\n"
        status += "Users:\n" + "\n".join([f"ID: {user['id']}, Name: {user['name']}, Role: {user['role']}" for user in users]) + "\n\n"
        status += "Trips:\n" + "\n".join([f"ID: {trip['id']}, Driver ID: {trip['driver_id']}, Status: {trip['status']}" for trip in trips]) + "\n\n"
        status += "Pickup Points:\n" + "\n".join([f"ID: {point['id']}, Trip ID: {point['trip_id']}, Address: {point['address']}, Time: {point['time']}" for point in pickup_points])

        return status
    except Exception as e:
        capture_exception(e)  # Send exception details to Sentry
        raise

