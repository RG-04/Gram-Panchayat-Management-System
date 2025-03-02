from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import authenticate_user
from app import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    """Landing page / redirects to login page."""
    if "user_id" in session:
        # Redirect based on user role
        if session["role"] == "citizen":
            return redirect(url_for("citizen.dashboard"))
        elif session["role"] == "employee":
            return redirect(url_for("employee.dashboard"))
        elif session["role"] == "monitor":
            return redirect(url_for("monitor.dashboard"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "GET" and "user_id" in session:
        return redirect(url_for("auth.index"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Both username and password are required."
        else:
            user = authenticate_user(username, password)

            if user:
                # Set session data
                session.permanent = True
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["name"] = user["name"]

                if user["citizen_id"]:
                    session["citizen_id"] = user["citizen_id"]

                if user["monitor_id"]:
                    session["monitor_id"] = user["monitor_id"]

                # Redirect based on user role
                if user["role"] == "citizen":
                    return redirect(url_for("citizen.dashboard"))
                elif user["role"] == "employee":
                    return redirect(url_for("employee.dashboard"))
                elif user["role"] == "monitor":
                    return redirect(url_for("monitor.dashboard"))
            else:
                error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/unauthorized")
def unauthorized():
    """Unauthorized access page."""
    return render_template("unauthorized.html")
