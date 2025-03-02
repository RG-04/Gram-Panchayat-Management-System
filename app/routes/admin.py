from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from app import db
from app.queries.admin_queries import admin_queries

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def admin_required(f):
    """Decorator to require admin login for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session or not session["admin_logged_in"]:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Admin login page."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Admin login successful", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid admin credentials", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    """Admin logout."""
    session.pop("admin_logged_in", None)
    flash("Admin logged out", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin dashboard page."""

    # Get all table names
    tables = db.execute_query(admin_queries["tables_query"])

    # Get all columns for each table
    table_columns = {}
    for table in tables:
        table_name = table[0]

        columns = db.execute_query(admin_queries["columns_query"], (table_name,))
        table_columns[table_name] = columns

    return render_template(
        "admin/dashboard.html", tables=tables, table_columns=table_columns
    )


@admin_bp.route("/execute", methods=["POST"])
@admin_required
def execute_query():
    """Execute a SQL query."""
    query = request.form.get("query", "")

    if not query.strip():
        flash("Query cannot be empty", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        is_select = query.strip().upper().startswith("SELECT")

        result = db.execute_query(query, fetch=is_select)

        if is_select:
            # If it's a SELECT query, get column names
            if result:
                column_names = []

                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute(query)
                column_names = [desc[0] for desc in cursor.description]
                cursor.close()

                flash("Query executed successfully", "success")
                return render_template(
                    "admin/execute_result.html",
                    query=query,
                    result=result,
                    column_names=column_names,
                    is_select=True,
                )
            else:
                flash("Query executed successfully, but returned no rows", "success")
                return render_template(
                    "admin/execute_result.html",
                    query=query,
                    result=[],
                    column_names=[],
                    is_select=True,
                )
        else:
            # For non-SELECT queries
            flash("Query executed successfully", "success")
            return render_template(
                "admin/execute_result.html",
                query=query,
                result=None,
                column_names=None,
                is_select=False,
            )
    except Exception as e:
        flash(f"Error executing query: {str(e)}", "error")
        return render_template(
            "admin/execute_result.html", query=query, error=str(e), is_select=None
        )


@admin_bp.route("/users")
@admin_required
def manage_users():
    """User management page."""

    # Get all citizens
    citizens_result = db.execute_query(admin_queries["citizens_query"])

    citizens = []
    for row in citizens_result:
        citizens.append(
            {
                "aadhaar": row[0],
                "name": row[1],
                "phone": row[2],
                "user_id": row[3],
                "is_registered": row[3] > 0,
            }
        )

    # Get all employees
    employees_result = db.execute_query(admin_queries["employees_query"])

    employees = []
    for row in employees_result:
        employees.append(
            {
                "aadhaar": row[0],
                "name": row[1],
                "role": row[2],
                "user_id": row[3],
                "is_registered": row[3] > 0,
            }
        )

    # Get all monitors
    monitors_result = db.execute_query(admin_queries["monitors_query"])

    monitors = []
    for row in monitors_result:
        monitors.append(
            {
                "id": row[0],
                "name": row[1],
                "user_id": row[2],
                "is_registered": row[2] > 0,
            }
        )

    return render_template(
        "admin/user_management.html",
        citizens=citizens,
        employees=employees,
        monitors=monitors,
    )


@admin_bp.route("/users/register", methods=["POST"])
@admin_required
def register_user():
    """Register a new user."""
    user_type = request.form.get("user_type")
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    password = request.form.get("password")

    # Validate inputs
    if not user_type or not user_id or not username or not password:
        flash("All fields are required", "error")
        return redirect(url_for("admin.manage_users"))

    # Check if username already exists
    check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
    count = db.execute_query(check_query, (username,))[0][0]

    if count > 0:
        flash(f'Username "{username}" already exists', "error")
        return redirect(url_for("admin.manage_users"))

    try:
        from app.utils.auth_utils import hash_password

        password_hash, salt = hash_password(password)

        # Insert new user
        if user_type == "citizen":
            auth_role = "citizen"
            db.execute_query(
                admin_queries["citizen_insert_query"],
                (user_id, username, password_hash, auth_role, salt),
                fetch=False,
            )

        elif user_type == "employee":
            auth_role = "employee"
            db.execute_query(
                admin_queries["employee_insert_query"],
                (user_id, username, password_hash, auth_role, salt),
                fetch=False,
            )

        elif user_type == "monitor":
            auth_role = "monitor"
            db.execute_query(
                admin_queries["monitor_insert_query"],
                (user_id, username, password_hash, auth_role, salt),
                fetch=False,
            )

        flash(f'User "{username}" registered successfully', "success")
    except Exception as e:
        flash(f"Error registering user: {str(e)}", "error")

    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/deregister/<int:user_id>")
@admin_required
def deregister_user(user_id):
    """Deregister a user."""

    try:
        username_query = "SELECT username FROM users WHERE UserID = %s"
        username_result = db.execute_query(username_query, (user_id,))

        if not username_result:
            flash("User not found", "error")
            return redirect(url_for("admin.manage_users"))

        username = username_result[0][0]

        # Delete the user
        delete_query = "DELETE FROM users WHERE UserID = %s"
        db.execute_query(delete_query, (user_id,), fetch=False)

        flash(f'User "{username}" deregistered successfully', "success")
    except Exception as e:
        flash(f"Error deregistering user: {str(e)}", "error")

    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/reset-password/<int:user_id>")
@admin_required
def reset_password(user_id):
    """Reset a user's password to a default value."""

    try:
        username_query = "SELECT username FROM users WHERE UserID = %s"
        username_result = db.execute_query(username_query, (user_id,))

        if not username_result:
            flash("User not found", "error")
            return redirect(url_for("admin.manage_users"))

        username = username_result[0][0]

        # Default password
        default_password = "Password@123"

        from app.utils.auth_utils import hash_password

        password_hash, salt = hash_password(default_password)

        # Update the user's password
        update_query = "UPDATE users SET password = %s, salt = %s WHERE UserID = %s"
        db.execute_query(update_query, (password_hash, salt, user_id), fetch=False)

        flash(f'Password for "{username}" reset to "{default_password}"', "success")
    except Exception as e:
        flash(f"Error resetting password: {str(e)}", "error")

    return redirect(url_for("admin.manage_users"))
