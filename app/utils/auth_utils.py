import hashlib
import os
from flask import session, redirect, url_for
from functools import wraps
from app.queries.auth_queries import auth_queries
from app import db


def hash_password(password, salt=None):
    """
    Hash a password using SHA-256 with a salt.
    """

    if salt is None:
        salt = os.urandom(32).hex()

    pw_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    return pw_hash, salt


def verify_password(password, stored_hash, salt):
    """Verify a password against a stored hash and salt."""

    pw_hash, _ = hash_password(password, salt)
    return pw_hash == stored_hash


def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    """

    result = db.execute_query(auth_queries["user_query"], (username,))

    if result and len(result) > 0:
        user_id, db_username, stored_hash, salt, role, citizen_id, monitor_id, name = (
            result[0]
        )

        if verify_password(password, stored_hash, salt):
            # Check if user is an employee
            is_employee = False
            if citizen_id:
                employee_result = db.execute_query(
                    auth_queries["employee_query"], (citizen_id,)
                )
                is_employee = len(employee_result) > 0

            return {
                "id": user_id,
                "username": db_username,
                "role": role,
                "citizen_id": citizen_id,
                "monitor_id": monitor_id,
                "name": name,
                "is_employee": is_employee,
            }

    return None


def login_required(f):
    """Decorator to require login for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(roles):
    """Decorator to require specific role(s) for a route."""

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if session.get("role") not in roles:
                return redirect(url_for("auth.unauthorized"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_current_user():
    """Get the current logged-in user data."""

    if "user_id" not in session:
        return None

    result = db.execute_query(auth_queries["curr_user_query"], (session["user_id"],))

    if result and len(result) > 0:
        user_id, username, role, citizen_id, monitor_id, name = result[0]

        # Check if user is an employee if they are a citizen
        is_employee = False
        if citizen_id:
            employee_result = db.execute_query(
                auth_queries["employee_query"], (citizen_id,)
            )
            is_employee = len(employee_result) > 0

        return {
            "id": user_id,
            "username": username,
            "role": role,
            "citizen_id": citizen_id,
            "monitor_id": monitor_id,
            "name": name,
            "is_employee": is_employee,
        }

    return None
