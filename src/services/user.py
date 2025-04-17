from xata.client import XataClient  # Use Xata client for database interactions
from sentry_sdk import capture_exception
from httpx import Timeout  # Import Timeout for setting request timeouts

xata = XataClient()  # Initialize Xata client with a 5-second timeout

def get_user(telegram_id: int):
    resp = xata.data().query("users", {
        "columns": ["name", "role", "telegram_id"], # the columns we want returned
        "filter": { "telegram_id": telegram_id } # optional filters to apply
    })
    # assert resp.is_success(), f"Error: {resp}"
    # assert len(resp['records']) > 0, f"Error: {resp}"
    # print(resp)
    if len(resp['records']) == 0:
        return []
    else:
        return resp['records'][0]  # Return the first user found

def register_user(telegram_id: int, name: str):
    user = get_user(telegram_id)
    if len(user) > 0:
        return user
    else:
        # Insert record to table "Avengers" and let Xata generate a record Id
        record = {
            "telegram_id": telegram_id,
            "name": name,
            "role": "passenger"
        }
        resp = xata.records().insert("users", record)
        # print(resp)

        # assert resp.is_success(), f"Error: {resp}"
        return resp

def switch_role(telegram_id: int, new_role: str):
    user = get_user(telegram_id)
    record = {
        "telegram_id": user['telegram_id'],
        "name": user['name'],
        "role": new_role
    }
    record_id = user['id']
    resp = xata.records().update("users", record_id, payload=record)
    #resp = xata.records().update("users", telegram_id, {"role": "driver"})
    # print(resp)
    return resp

def delete_user(telegram_id: int):
    user = get_user(telegram_id)
    record_id = user['id']
    resp = xata.records().delete("users", record_id)
    # assert resp.is_success(), f"Error: {resp}"
    return resp

