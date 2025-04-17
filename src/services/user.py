from xata.client import XataClient  # Use Xata client for database interactions
# Removed SQLAlchemy-related imports
xata = XataClient()

def get_user(telegram_id: int):
    try:
        return xata.db.users.filter({"telegram_id": telegram_id}).get_first()
    except Exception as e:
        capture_exception(e)
        return None

def register_user(telegram_id: int, name: str):
    user = get_user(telegram_id)
    if not user:
        return xata.db.users.create({"telegram_id": telegram_id, "name": name, "role": "passenger"})
    else:
        return xata.db.users.update(user["id"], {"name": name})

def switch_role(user_id: str, new_role: str):
    return xata.db.users.update(user_id, {"role": new_role})

def get_telegram_handler(user_id: str):
    user = xata.db.users.get(user_id)
    return user["telegram_id"] if user else None

