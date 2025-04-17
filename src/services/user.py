from xata.client import XataClient  # Use Xata client for database interactions
# Removed SQLAlchemy-related imports
xata = XataClient()

async def get_user(telegram_id: int):
    try:
        return await xata.table("users").filter({"id": telegram_id}).get_first()
    except Exception as e:
        capture_exception(e)
        return None

async def register_user(telegram_id: int, name: str):
    user = await get_user(telegram_id)
    if not user:
        return await xata.table("users").create({"id": telegram_id, "name": name, "role": "passenger"})
    else:
        return await xata.table("users").update(telegram_id, {"name": name})

async def switch_role(user_id: str, new_role: str):
    return await xata.table("users").update(user_id, {"role": new_role})

def get_telegram_handler(user_id: str):
    user = xata.db.users.get(user_id)
    return user["telegram_id"] if user else None
