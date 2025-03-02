from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required
from app import db
from app.queries.monitor_queries import monitor_queries

monitor_bp = Blueprint("monitor", __name__)


@monitor_bp.route("/dashboard")
@role_required(["monitor"])
def dashboard():
    """Display the monitor dashboard - redirects to citizen dashboard with monitor role."""
    return redirect(url_for("citizen.dashboard"))


@monitor_bp.route("/advanced_stats")
@role_required(["monitor"])
def advanced_stats():
    """Display advanced statistics based on category."""

    category = request.args.get("category", "education")

    # Validate category
    valid_categories = ["education", "health", "agriculture", "demographic", "schemes", "environment"]
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

    elif category == "schemes":
        stats = get_advanced_scheme_stats()
        category_title = "Advanced Scheme Analysis"

    elif category == "environment":
        stats = get_environmental_stats()
        category_title = "Environmental Statistics"

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

        # 5. Get finance data
        finance_data = db.execute_query(monitor_queries["school_finances"])
        stats["school_finances"] = [
            {
                "name": row[0],
                "income": row[1],
                "expenditure": row[2],
                "budget_year": row[3],
                "surplus": row[1] - row[2],
            }
            for row in finance_data
        ]

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
    """Fetch advanced health statistics using db queries."""

    stats = {}

    try:
        # Get hospital financial data
        finance_data = db.execute_query(monitor_queries["hospital_finances"])
        stats["hospital_finances"] = [
            {
                "name": row[0],
                "income": row[1],
                "expenditure": row[2],
                "budget_year": row[3],
                "profit_margin": (
                    round((row[1] - row[2]) / row[1] * 100, 1) if row[1] > 0 else 0
                ),
            }
            for row in finance_data
        ]

        total_doctors = db.execute_query(monitor_queries["total_doctors"])[0][0]
        total_nurses = db.execute_query(monitor_queries["total_nurses"])[0][0]
        total_population = db.execute_query("SELECT COUNT(*) FROM Citizen")[0][0]

        stats["total_doctors"] = total_doctors
        stats["total_nurses"] = total_nurses
        stats["doctor_citizen_ratio"] = (
            f"1:{round(total_population / total_doctors)}"
            if total_doctors > 0
            else "N/A"
        )
        stats["nurse_citizen_ratio"] = (
            f"1:{round(total_population / total_nurses)}" if total_nurses > 0 else "N/A"
        )

        health_schemes = db.execute_query(monitor_queries["health_schemes"])
        print(health_schemes)
        stats["health_schemes"] = []
        for scheme in health_schemes:
            stats["health_schemes"].append(
                {
                    "name": scheme[1],
                    "description": scheme[2],
                    "enrolled_citizens": scheme[3],
                    "budget": scheme[4],
                    "enrollment_rate": (
                        round((scheme[3] / total_population) * 100, 1)
                        if total_population > 0
                        else 0
                    ),
                }
            )

        # Calculate summary statistics
        total_income = sum(
            hospital["income"] for hospital in stats["hospital_finances"]
        )
        total_expenditure = sum(
            hospital["expenditure"] for hospital in stats["hospital_finances"]
        )

        stats["total_income"] = total_income
        stats["total_expenditure"] = total_expenditure
        stats["overall_margin"] = (
            round((total_income - total_expenditure) / total_income * 100, 1)
            if total_income > 0
            else 0
        )

        # Get vaccination coverage statistics (reuse query from citizen stats)
        vaccination_data = db.execute_query(monitor_queries["vaccination_stats"])
        stats["vaccination_stats"] = [
            {
                "Disease": row[0],
                "VaccinatedCitizens": row[1],
                "TotalAdults": row[2],
                "VaccinationRate": (
                    round((row[1] / row[2]) * 100, 1) if row[2] > 0 else 0
                ),
            }
            for row in vaccination_data
        ]

    except Exception as e:
        print(f"Database error in health stats: {e}")

    return stats


def get_advanced_agriculture_stats():
    """Fetch advanced agriculture statistics using db queries."""

    stats = {}

    try:
        # Get irrigation method statistics
        irrigation_data = db.execute_query(monitor_queries["irrigation_methods"])
        stats["irrigation_methods"] = {
            "labels": [row[0] for row in irrigation_data],
            "values": [row[1] for row in irrigation_data],
        }

        # Get water usage by crop
        water_usage_data = db.execute_query(monitor_queries["water_usage_by_crop"])
        stats["water_usage"] = [
            {
                "crop_name": row[0],
                "total_area": row[1],
                "total_water_usage": row[2],
                "water_per_acre": round(row[2] / row[1], 1) if row[1] > 0 else 0,
            }
            for row in water_usage_data
        ]

    except Exception as e:
        print(f"Database error in agriculture stats: {e}")

    return stats


def get_advanced_demographic_stats():
    """Fetch advanced demographic statistics using db queries."""

    stats = {}

    try:
        # Get migration statistics
        migration_data = db.execute_query(monitor_queries["migration_status"])
        stats["migration_status"] = {
            "labels": [row[0] for row in migration_data],
            "values": [row[1] for row in migration_data],
        }

    except Exception as e:
        print(f"Database error in demographic stats: {e}")

    return stats


def get_advanced_scheme_stats():
    """Fetch advanced scheme analysis statistics using db queries."""

    stats = {}

    try:
        # Get scheme budget and utilization
        scheme_budget_data = db.execute_query(
            monitor_queries["scheme_budget_allocation"]
        )
        stats["scheme_budget"] = [
            {
                "scheme_name": row[0],
                "allocated_budget": row[1],
                "target_beneficiaries": row[2],
                "beneficiaries_enrolled": row[4],
                "achievement_rate": row[4] * 100 / row[2] if row[2] > 0 else 0,
                "benefits_received": row[5],
                "budget_year": row[3],
            }
            for row in scheme_budget_data
        ]

        # Get scheme enrollment statistics
        enrollment_data = db.execute_query(monitor_queries["scheme_enrollment_stats"])
        stats["enrollment_stats"] = [
            {
                "scheme_name": row[0],
                "active_enrollments": row[1],
                "inactive_enrollments": row[2],
                "pending_enrollments": row[3],
                "total_enrollments": row[1] + row[2] + row[3],
                "total_benefits": row[4],
            }
            for row in enrollment_data
        ]

        # Calculate target achievement rates
        # for scheme_budget in stats['scheme_budget']:
        #     matching_enrollment = next((e for e in stats['enrollment_stats']
        #                                if e['scheme_name'] == scheme_budget['scheme_name']), None)

        #     if matching_enrollment:
        #         target = scheme_budget['target_beneficiaries']
        #         actual = matching_enrollment['total_enrollments']
        #         scheme_budget['achievement_rate'] = round((actual / target) * 100, 1) if target > 0 else 0

        #         # Calculate cost per beneficiary
        #         budget = scheme_budget['allocated_budget']
        #         scheme_budget['cost_per_beneficiary'] = round(budget / actual, 2) if actual > 0 else 0
        #     else:
        #         scheme_budget['achievement_rate'] = 0
        #         scheme_budget['cost_per_beneficiary'] = 0

    except Exception as e:
        print(f"Database error in scheme stats: {e}")

    return stats


def get_environmental_stats():
    """Fetch environmental statistics using simplified db queries."""
    
    stats = {}
    
    try:
        # Get 2025 environmental summary
        summary_data = db.execute_query(monitor_queries['environmental_summary_2025'])
        if summary_data and len(summary_data) > 0:
            stats['env_summary'] = {
                'avg_air_quality': summary_data[0][0] or 0,
                'avg_rainfall': summary_data[0][1] or 0,
                'avg_groundwater': summary_data[0][2] or 0,
                'avg_forest_cover': summary_data[0][3] or 0
            }
        else:
            stats['env_summary'] = {
                'avg_air_quality': 0,
                'avg_rainfall': 0,
                'avg_groundwater': 0,
                'avg_forest_cover': 0
            }
        
        # Get AQI monthly trends
        aqi_data = db.execute_query(monitor_queries['aqi_monthly_trends'])
        aqi_trends = []
        
        if aqi_data:
            for row in aqi_data:
                aqi_trends.append({
                    'year': int(row[0]),
                    'month': int(row[1]),
                    'month_name': row[2].strip(),
                    'avg_aqi': float(row[3] or 0)
                })
        
        stats['aqi_trends'] = aqi_trends
        
        # Get rainfall monthly trends
        rainfall_data = db.execute_query(monitor_queries['rainfall_monthly_trends'])
        rainfall_trends = []
        
        if rainfall_data:
            for row in rainfall_data:
                rainfall_trends.append({
                    'year': int(row[0]),
                    'month': int(row[1]),
                    'month_name': row[2].strip(),
                    'avg_rainfall': float(row[3] or 0)
                })
        
        stats['rainfall_trends'] = rainfall_trends
        
    except Exception as e:
        print(f"Database error in environmental stats: {e}")
        stats = {}
    
    return stats