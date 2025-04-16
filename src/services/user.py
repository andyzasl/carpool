from functools import wraps
from sqlalchemy.orm import Session
from src.database.db import SessionLocal  # Ensure correct relative import
from src.models.models import User  # Ensure correct relative import

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session: Session = SessionLocal()
        try:
            kwargs['session'] = session
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    return wrapper

@with_session
def get_user(session: Session, telegram_id: str):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        # Access attributes to ensure they are loaded before the session is closed
        user.id, user.role
        session.expunge(user)  # Detach the instance from the session
    return user

@with_session
def register_user(telegram_id: str, name: str, session: Session = None):
    """
    Register a new user or update the name if the user already exists.

    Args:
        telegram_id (str): Telegram ID of the user.
        name (str): Full name of the user.
        session (Session): SQLAlchemy session (injected by the decorator).

    Returns:
        User: The registered or updated user.
    """
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, name=name, role="passenger")
        session.add(user)
    else:
        user.name = name  # Update name if the user already exists
    return user

@with_session
def switch_role(session: Session, user_id: int, new_role: str):
    """
    Switch the role of a user.

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): ID of the user whose role is to be switched.
        new_role (str): The new role to assign ("driver" or "passenger").

    Returns:
        User: The updated user object.
    """
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.role = new_role
        return user
    else:
        raise ValueError(f"User with ID {user_id} not found.")

@with_session
def get_telegram_handler(session: Session, user_id: int):
    """
    Retrieve the Telegram handler (username) for a user.

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): ID of the user.

    Returns:
        str: The Telegram handler (username) of the user, or None if not found.
    """
    user = session.query(User).filter_by(id=user_id).first()
    return user.telegram_id if user else None

