import json
import os
from threading import Lock
from typing import List, Dict, Any, Optional

# Define base path to database file (relative to workspace root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "users.json")

# Simple thread lock to prevent concurrent write issues during parallel API calls
_db_lock = Lock()


def init_db() -> None:
    """
    Initializes the database folder and JSON file if they do not exist.
    """
    with _db_lock:
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR, exist_ok=True)
        if not os.path.exists(DB_PATH):
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)


def load_users() -> List[Dict[str, Any]]:
    """
    Loads all users from the JSON database file.
    """
    init_db()
    with _db_lock:
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def save_users(users: List[Dict[str, Any]]) -> None:
    """
    Saves the list of users back to the JSON database file.
    """
    init_db()
    with _db_lock:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Queries a user by their email address. Case-insensitive.
    """
    users = load_users()
    email_lower = email.lower()
    for user in users:
        if user.get("email", "").lower() == email_lower:
            return user
    return None


def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserts a new user record into the JSON database.
    """
    users = load_users()
    users.append(user_data)
    save_users(users)
    return user_data
