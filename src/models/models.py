from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False)
    state = Column(String, default="active")  # New column for trip state
    created_at = Column(DateTime, default=datetime.utcnow)  # Track creation time


class PickupPoint(Base):
    __tablename__ = "pickup_points"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    address = Column(String, nullable=False)
    time = Column(String, nullable=False)  # Time as a string for simplicity
