from sentry_sdk import capture_exception  # Import Sentry's exception capture function

def get_full_status():
    try:
        status = "Database Status:\n\n"
        status += "Users:\n" + "\n".join([f"ID: {user.id}, Name: {user.name}, Role: {user.role}" for user in users]) + "\n\n"
        status += "Trips:\n" + "\n".join([f"ID: {trip.id}, Driver ID: {trip.driver_id}, Status: {trip.status}, State: {trip.state}" for trip in trips]) + "\n\n"
        status += "Pickup Points:\n" + "\n".join([f"ID: {point.id}, Trip ID: {point.trip_id}, Address: {point.address}, Time: {point.time}" for point in pickup_points])

        return status
    except Exception as e:
        capture_exception(e)  # Send exception details to Sentry
        raise

