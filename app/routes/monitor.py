from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required
from app import db
from app.queries.monitor_queries import monitor_queries

monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.route("/advanced_stats")
@role_required(["monitor"])
def advanced_stats():
    """Display advanced statistics based on category."""

    category = request.args.get("category", "education")

    # Validate category
    valid_categories = ["education", "health", "agriculture", "demographic"]
    if category not in valid_categories:
        flash(f"Invalid category: {category}", "danger")
        return redirect(url_for("citizen.dashboard"))

    # Fetch statistics based on the selected category
    if category == "education":
        stats = get_advanced_education_stats()
        category_title = "Advanced Education Statistics"

    elif category == "health":
        stats = get_advanced_health_stats()
        category_title = "Advanced Health Statistics"

    elif category == "agriculture":
        stats = get_advanced_agriculture_stats()
        category_title = "Advanced Agriculture Statistics"

    elif category == "demographic":
        stats = get_advanced_demographic_stats()
        category_title = "Advanced Demographic Statistics"

    return render_template(
        "monitor/advanced_stats.html",
        category=category,
        category_title=category_title,
        stats=stats,
        role="monitor",
    )


def get_advanced_education_stats():
    """Fetch advanced education statistics using db queries."""

    stats = {}

    try:
        # 1. Get average school income
        avg_income = db.execute_query(monitor_queries["avg_school_income"])[0][0]
        stats["avg_school_income"] = avg_income or 0

        # 2. Get total capacity and total enrolled students
        total_capacity = db.execute_query(monitor_queries["total_school_capacity"])[0][
            0
        ]
        stats["total_capacity"] = total_capacity or 0

        total_students = db.execute_query(monitor_queries["total_enrolled_students"])[
            0
        ][0]
        stats["total_students"] = total_students or 0

        # 3. Calculate capacity utilization
        stats["capacity_utilization"] = (
            round((total_students / total_capacity) * 100, 1)
            if total_capacity > 0
            else 0
        )

        # 4. Get gender distribution of students
        gender_data = db.execute_query(monitor_queries["gender_distribution"])
        stats["gender_distribution"] = {
            "labels": [row[0] for row in gender_data],
            "values": [row[1] for row in gender_data],
        }

        # 6. Get school capacity utilization details
        utilization_data = db.execute_query(monitor_queries["school_utilization"])
        stats["school_utilization"] = [
            {
                "name": row[1],
                "capacity": row[2],
                "enrolled": row[3],
                "utilization_pct": (
                    round((row[3] / row[2]) * 100, 1) if row[2] > 0 else 0
                ),
            }
            for row in utilization_data
        ]

    except Exception as e:
        print(f"Database error: {e}")

    return stats


def get_advanced_health_stats():
    """Fetch advanced health statistics using db queries (To be implemented)."""
    stats = {}

    try:
        db_res = db.execute_query(monitor_queries["total_doctors"])
        stats["total_doctors"] = 0
        if db_res and db_res[0]:
            stats["total_doctors"] = db_res[0][0]

        # 2. Get total nurses
        db_res = db.execute_query(monitor_queries["total_nurses"])
        stats["total_nurses"] = 0
        if db_res and db_res[0]:
            stats["total_nurses"] = db_res[0][0]

        # 3. Get total citizens for ratio calculations
        db_res = db.execute_query("SELECT COUNT(*) FROM Citizen")
        total_citizens = 1000
        if db_res and db_res[0]:
            total_citizens = db_res[0][0]

        # Calculate doctor:citizen ratio (1:X format)
        if stats["total_doctors"] > 0 and total_citizens > 0:
            stats["doctor_citizen_ratio"] = (
                f"1:{round(total_citizens / stats['total_doctors'])}"
            )
        else:
            stats["doctor_citizen_ratio"] = "N/A"

        # Calculate nurse:citizen ratio (1:X format)
        if stats["total_nurses"] > 0 and total_citizens > 0:
            stats["nurse_citizen_ratio"] = (
                f"1:{round(total_citizens / stats['total_nurses'])}"
            )
        else:
            stats["nurse_citizen_ratio"] = "N/A"

        # 5. Get health welfare schemes

        health_schemes_data = db.execute_query(monitor_queries["health_schemes"])

        health_schemes = []

        for scheme in health_schemes_data:
            # Calculate enrollment rate as percentage of total citizens
            enrollment_rate = (
                round((scheme[3] / total_citizens) * 100, 1)
                if total_citizens > 0
                else 0
            )

            health_schemes.append(
                {
                    "name": scheme[1],
                    "description": scheme[2],
                    "enrolled_citizens": scheme[3],
                    "enrollment_rate": enrollment_rate,
                }
            )

        stats["health_schemes"] = health_schemes

    except Exception as e:
        print(f"Database error: {e}")

    return stats


def get_advanced_agriculture_stats():
    """Fetch advanced agriculture statistics using db queries (To be implemented)."""
    return {}


def get_advanced_demographic_stats():
    """Fetch advanced demographic statistics using db queries (To be implemented)."""
    return {}
