from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import DATABASE_URL, setup_sentry  # Ensure correct relative import
from src.models.models import Base  # Ensure correct relative import
import os

# Initialize Sentry before database setup
setup_sentry()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database schema
Base.metadata.create_all(bind=engine)

