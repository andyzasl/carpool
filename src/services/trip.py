from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.models import Trip, PickupPoint  # Ensure correct relative import
from src.services.user import with_session, get_telegram_handler  # Ensure correct relative import
from src.utils.template_renderer import render_template  # Ensure correct relative import

@with_session
def create_trip(session: Session, driver_id: int, seats: int, pickup_points: list):
    trip = Trip(driver_id=driver_id, status="active")
    session.add(trip)
    session.flush()  # Ensure trip ID is generated before adding pickup points

    for point in pickup_points:
        pickup_point = PickupPoint(trip_id=trip.id, address=point["address"], time=point["time"])
        session.add(pickup_point)

    return trip.id

@with_session
def list_trips(session: Session):
    trips = session.query(Trip).all()
    return [
        {"id": trip.id, "driver_id": trip.driver_id, "status": trip.status}
        for trip in trips
    ]

@with_session
def get_trip(session: Session, trip_id: int):
    trip = session.query(Trip).filter_by(id=trip_id).first()
    if trip:
        pickup_points = session.query(PickupPoint).filter_by(trip_id=trip.id).all()
        trip_details = {
            "id": trip.id,
            "driver_id": trip.driver_id,
            "status": trip.status,
            "state": trip.state,
            "created_at": trip.created_at,
            "pickup_points": [
                {"id": point.id, "address": point.address, "time": point.time}
                for point in pickup_points
            ],
            "driver_handler": get_telegram_handler(trip.driver_id),  # Add driver handler
        }
        # Example template rendering
        template = "Trip {id} by Driver {driver_handler} is {status}. Created at {created_at}."
        trip_details["rendered"] = render_template(template, trip_details)
        return trip_details
    return None

@with_session
def close_expired_trips(session: Session):
    expired_trips = session.query(Trip).filter(
        Trip.status == "active",
        Trip.created_at < datetime.utcnow() - timedelta(days=1)  # Example: 1-day expiration
    ).all()
    for trip in expired_trips:
        trip.status = "closed"

