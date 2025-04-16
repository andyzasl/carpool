from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base

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


class PickupPoint(Base):
    __tablename__ = "pickup_points"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    address = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Participant(Base):
    __tablename__ = "participants"
    trip_id = Column(Integer, ForeignKey("trips.id"), primary_key=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    pickup_point_id = Column(Integer, ForeignKey("pickup_points.id"))


class TripTemplate(Base):
    __tablename__ = "trip_templates"
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    pickup_points = Column(JSON, nullable=False)
    seats = Column(Integer, nullable=False)
