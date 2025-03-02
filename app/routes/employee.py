from decimal import Decimal, InvalidOperation
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    send_file,
)
from app.utils.auth_utils import role_required
from app import db
from datetime import datetime
from app.queries.employee_queries import employee_queries
import io

employee_bp = Blueprint("employee", __name__)


@employee_bp.route("/dashboard")
@role_required(["employee"])
def dashboard():
    """Employee dashboard page."""

    employee_info = db.execute_query(
        employee_queries["employee_query"], (session["citizen_id"],)
    )
    citizen_count = db.execute_query(employee_queries["citizen_count_query"])[0][0]
    cert_count = db.execute_query(employee_queries["cert_count_query"])[0][0]
    scheme_count = db.execute_query(employee_queries["scheme_count_query"])[0][0]

    return render_template(
        "employee/dashboard.html",
        employee=employee_info[0] if employee_info else None,
        citizen_count=citizen_count,
        cert_count=cert_count,
        scheme_count=scheme_count,
    )


@employee_bp.route("/certificates")
@role_required(["employee"])
def certificates():
    """View and manage citizens."""

    citizens_list = db.execute_query(employee_queries["citizens_query"])
    return render_template("employee/certificates.html", citizens=citizens_list)


@employee_bp.route("/citizen/<aadhaar>")
@role_required(["employee"])
def view_citizen(aadhaar):
    """View citizen details."""

    citizen = db.execute_query(employee_queries["citizen_one_query"], (aadhaar,))

    if not citizen:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))

    father = False
    mother = False

    if citizen[0][-1] is not None:
        father = db.execute_query(
            employee_queries["citizen_parent_query"], (citizen[0][-1],)
        )

    if citizen[0][-2] is not None:
        mother = db.execute_query(
            employee_queries["citizen_parent_query"], (citizen[0][-2],)
        )

    children = db.execute_query(
        employee_queries["citizen_children_query"], (citizen[0][0], citizen[0][0])
    )

    family_income = db.execute_query(
        employee_queries["citizen_family_income_query"], (citizen[0][-3],)
    )[0][0]

    certificates = db.execute_query(employee_queries["citizen_cert_query"], (aadhaar,))

    # Group certificates by category
    certificates_by_category = {}
    for cert in certificates:
        category = cert[0]
        if category not in certificates_by_category:
            certificates_by_category[category] = []
        certificates_by_category[category].append(
            {
                "category": cert[0],
                "name": cert[1],
                "date_issued": cert[2],
                "has_file": cert[3],
            }
        )

    return render_template(
        "employee/view_citizen.html",
        citizen=citizen[0],
        certificates_by_category=certificates_by_category,
        father=father and father[0],
        mother=mother and mother[0],
        children=children,
        family_income=family_income,
    )


@employee_bp.route("/citizen/<aadhaar>/update", methods=["POST"])
@role_required(["employee"])
def update_citizen(aadhaar):
    """Update a citizen's information in the database."""

    try:
        name = request.form.get("name")
        dob_str = request.form.get("dob")
        gender = request.form.get("gender")
        income_str = request.form.get("income")
        occupation = request.form.get("occupation")
        phone = request.form.get("phone")
        household_addr = request.form.get("householdid")

        # Validate required fields
        if not name:
            flash("Name is required", "error")
            return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format", "error")
                return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        income = None
        if income_str:
            try:
                income = Decimal(income_str)
                if income < 0:
                    raise ValueError("Income cannot be negative")
            except (ValueError, InvalidOperation):
                flash("Invalid income value", "error")
                return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        if not household_addr:
            flash("Household address is required", "error")
            return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        cursor = db.connection.cursor()

        cursor.execute(
            employee_queries["update_citizen_query"],
            (name, dob, gender, income, occupation, phone, aadhaar),
        )

        if household_addr:
            cursor.execute(
                employee_queries["update_household_query"],
                (household_addr, aadhaar),
            )

        db.connection.commit()
        cursor.close()

        flash("Citizen information updated successfully", "success")
        return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

    except Exception as e:
        db.connection.rollback()
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))


@employee_bp.route("/citizen/<aadhaar>/certificates")
@role_required(["employee"])
def citizen_certificates(aadhaar):
    """View and manage citizen certificates."""

    citizen_name = db.execute_query(
        employee_queries["citizen_by_aadhaar_query"], (aadhaar,)
    )

    if not citizen_name:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))

    certificates = db.execute_query(employee_queries["citizen_cert_query"], (aadhaar,))

    categories = set([cert[0] for cert in certificates])
    if not categories:
        # Default categories if none exist yet
        categories = ["Identity", "Education", "Property", "Income", "Other"]

    return render_template(
        "employee/citizen_certificates.html",
        citizen_id=aadhaar,
        citizen_name=citizen_name[0][0],
        certificates=certificates,
        categories=sorted(categories),
    )


@employee_bp.route("/citizen/<aadhaar>/certificate/<category>/<name>")
@role_required(["employee"])
def view_certificate(aadhaar, category, name):
    """View a specific certificate."""

    certificate = db.execute_query(
        employee_queries["specific_cert_query"], (category, name, aadhaar)
    )
    if not certificate:
        flash("Certificate not found", "error")
        return redirect(url_for("employee.citizen_certificates", aadhaar=aadhaar))

    citizen_name = db.execute_query(
        employee_queries["citizen_by_aadhaar_query"], (aadhaar,)
    )

    return render_template(
        "employee/view_certificate.html",
        certificate=certificate[0],
        citizen_name=citizen_name[0][0] if citizen_name else "Unknown",
    )


@employee_bp.route("/citizen/<aadhaar>/certificate/file/<category>/<name>")
@role_required(["employee"])
def certificate_file(aadhaar, category, name):
    """Get the certificate file."""

    result = db.execute_query(
        employee_queries["cert_file_query"], (category, name, aadhaar)
    )

    if not result or not result[0][0]:
        flash("Certificate file not found", "error")
        return redirect(
            url_for(
                "employee.view_certificate",
                aadhaar=aadhaar,
                category=category,
                name=name,
            )
        )

    # Create a file-like object from the bytes
    file_data = result[0][0]
    file_stream = io.BytesIO(file_data)

    return send_file(
        file_stream,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"{category}_{name}_certificate.pdf",
    )


@employee_bp.route(
    "/citizen/<aadhaar>/certificate/<category>/<name>/update", methods=["POST"]
)
@role_required(["employee"])
def update_certificate_file(aadhaar, category, name):
    """Update the certificate file."""

    certificate_file = request.files.get("certificate_file")

    if not certificate_file or not certificate_file.filename:
        flash("No file provided", "error")
        return redirect(
            url_for(
                "employee.view_certificate",
                aadhaar=aadhaar,
                category=category,
                name=name,
            )
        )

    file_data = certificate_file.read()

    # Update certificate with file
    db.execute_query(
        employee_queries["update_cert_query"],
        (file_data, category, name, aadhaar),
        fetch=False,
    )

    flash("Certificate file uploaded successfully", "success")
    return redirect(
        url_for(
            "employee.view_certificate", aadhaar=aadhaar, category=category, name=name
        )
    )


@employee_bp.route("/citizen/<aadhaar>/upload_certificate", methods=["GET", "POST"])
@role_required(["employee"])
def upload_certificate(aadhaar):
    """Upload a new certificate for a citizen."""

    citizen_name = db.execute_query(
        employee_queries["citizen_by_aadhaar_query"], (aadhaar,)
    )

    if not citizen_name:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))

    # Get existing certificate categories
    existing_categories = db.execute_query(
        employee_queries["certificate_categories_query"]
    )

    categories = [cat[0] for cat in existing_categories]
    if not categories:
        # Default categories if none exist yet
        categories = ["Identity", "Education", "Property", "Income", "Other"]

    if request.method == "POST":
        category = request.form.get("category")
        custom_category = request.form.get("custom_category")
        name = request.form.get("name")
        date_issued = request.form.get("date_issued")
        certificate_file = request.files.get("certificate_file")

        # Validate input
        if not category or not name or not date_issued:
            flash("Category, name, and issue date are required", "error")
            return render_template(
                "employee/upload_certificate.html",
                citizen_id=aadhaar,
                citizen_name=citizen_name[0][0],
                categories=categories,
            )

        if category == "Other" and custom_category:
            category = custom_category

        count = db.execute_query(
            employee_queries["specific_cert_count_query"], (category, name, aadhaar)
        )[0][0]

        if count > 0:
            flash(
                "A certificate with this category and name already exists for this citizen",
                "error",
            )
            return render_template(
                "employee/upload_certificate.html",
                citizen_id=aadhaar,
                citizen_name=citizen_name[0][0],
                categories=categories,
            )

        file_data = None
        if certificate_file and certificate_file.filename:
            file_data = certificate_file.read()

        if file_data:
            db.execute_query(
                employee_queries["insert_certificate_with_file_query"],
                (category, name, aadhaar, date_issued, file_data),
                fetch=False,
            )
        else:
            db.execute_query(
                employee_queries["insert_certificate_query"],
                (category, name, aadhaar, date_issued),
                fetch=False,
            )

        flash("Certificate added successfully", "success")
        return redirect(url_for("employee.citizen_certificates", aadhaar=aadhaar))

    return render_template(
        "employee/upload_certificate.html",
        citizen_id=aadhaar,
        citizen_name=citizen_name[0][0],
        categories=categories,
    )


@employee_bp.route("/schemes")
@role_required(["employee"])
def schemes():
    """Manage government schemes page."""

    schemes_result = db.execute_query(employee_queries["schemes_query"])
    scheme_types_result = db.execute_query(employee_queries["scheme_types_query"])
    total_enrollments_result = db.execute_query(
        employee_queries["scheme_enrollment_count_query"]
    )

    schemes = []
    for row in schemes_result:
        schemes.append(
            {
                "id": row[0],
                "name": row[1],
                "type": row[2] or "Uncategorized",
                "description": row[3],
                "enrollments": row[4],
            }
        )

    scheme_types = [row[0] for row in scheme_types_result]
    if "Uncategorized" not in scheme_types and any(
        scheme["type"] == "Uncategorized" for scheme in schemes
    ):
        scheme_types.append("Uncategorized")

    total_enrollments = (
        total_enrollments_result[0][0] if total_enrollments_result else 0
    )

    return render_template(
        "employee/manage_schemes.html",
        schemes=schemes,
        scheme_types=scheme_types,
        total_schemes=len(schemes),
        total_enrollments=total_enrollments,
    )


@employee_bp.route("/schemes/add", methods=["POST"])
@role_required(["employee"])
def add_scheme():
    """Add a new scheme."""

    name = request.form.get("name")
    type_value = request.form.get("type")

    # Check if a new type is being added
    if type_value == "new":
        type_value = request.form.get("new_type")

    description = request.form.get("description")

    # Validate inputs
    if not name or not description:
        flash("Scheme name and description are required", "error")
        return redirect(url_for("employee.schemes"))

    try:
        result = db.execute_query(
            employee_queries["scheme_insert_query"], (name, type_value, description)
        )
        scheme_id = result[0][0] if result else None

        if scheme_id:
            flash(f"Scheme '{name}' added successfully", "success")
        else:
            flash("Failed to add scheme", "error")

    except Exception as e:
        flash(f"Error adding scheme: {str(e)}", "error")

    return redirect(url_for("employee.schemes"))


@employee_bp.route("/schemes/update", methods=["POST"])
@role_required(["employee"])
def update_scheme():
    """Update an existing scheme."""

    scheme_id = request.form.get("scheme_id")
    name = request.form.get("name")
    type_value = request.form.get("type")

    # Check if a new type is being added
    if type_value == "new":
        type_value = request.form.get("new_type")

    description = request.form.get("description")

    # Validate inputs
    if not scheme_id or not name or not description:
        flash("Scheme ID, name, and description are required", "error")
        return redirect(url_for("employee.schemes"))

    try:
        db.execute_query(
            employee_queries["scheme_update_query"],
            (name, type_value, description, scheme_id),
            fetch=False,
        )
        flash(f"Scheme '{name}' updated successfully", "success")
    except Exception as e:
        flash(f"Error updating scheme: {str(e)}", "error")

    return redirect(url_for("employee.schemes"))


@employee_bp.route("/schemes/delete", methods=["POST"])
@role_required(["employee"])
def delete_scheme():
    """Delete a scheme and all associated enrollments and forms."""

    scheme_id = request.form.get("scheme_id")

    if not scheme_id:
        flash("Scheme ID is required", "error")
        return redirect(url_for("employee.schemes"))

    try:

        result1 = db.execute_query(employee_queries["scheme_name_query"], (scheme_id))
        scheme_name = result1[0][0] if result1 else None

        print(scheme_name)

        if not scheme_name:
            flash("Scheme not found", "error")
            return redirect(url_for("employee.schemes"))

        db.execute_query(
            employee_queries["scheme_delete_query"], (scheme_id), fetch=False
        )

        flash(f"Scheme '{scheme_name}' deleted successfully", "success")

    except Exception as e:
        flash(f"Error deleting scheme: {str(e)}", "error")

    return redirect(url_for("employee.schemes"))


@employee_bp.route("/assets")
@role_required(["employee"])
def assets():
    """View all assets and their details."""

    assets_list = db.execute_query(employee_queries["assets_query"])

    return render_template("employee/assets.html", assets=assets_list)


@employee_bp.route("/asset/<int:asset_id>")
@role_required(["employee"])
def view_asset(asset_id):
    """View a specific asset and its survey history."""

    asset = db.execute_query(employee_queries["asset_details_query"], (asset_id,))

    if not asset:
        flash("Asset not found", "error")
        return redirect(url_for("employee.assets"))

    surveys = db.execute_query(employee_queries["surveys_query"], (asset_id,))

    return render_template(
        "employee/view_asset.html",
        asset=asset[0],
        surveys=surveys,
        current_date=datetime.now().date(),
    )


@employee_bp.route("/asset/<int:asset_id>/survey", methods=["GET", "POST"])
@role_required(["employee"])
def survey_asset(asset_id):
    """Survey an asset."""

    asset = db.execute_query(employee_queries["asset_details_query"], (asset_id,))

    if not asset:
        flash("Asset not found", "error")
        return redirect(url_for("employee.assets"))

    employee = db.execute_query(
        employee_queries["get_employee_query"], (session["citizen_id"],)
    )

    if not employee:
        flash("Employee record not found", "error")
        return redirect(url_for("employee.assets"))

    employee_id = employee[0][0]

    if request.method == "POST":
        condition = request.form.get("condition")
        issues = request.form.get("issues")
        maintenance_needed = request.form.get("maintenance_needed", "No")
        comments = request.form.get("comments", "")

        survey_data = f"Condition: {condition}; Issues: {issues}; Maintenance Needed: {maintenance_needed}; Comments: {comments}"

        db.execute_query(
            employee_queries["survey_insert_query"],
            (asset_id, employee_id, survey_data, employee_id, survey_data),
            fetch=False,
        )

        flash("Asset survey submitted successfully", "success")
        return redirect(url_for("employee.view_asset", asset_id=asset_id))

    return render_template("employee/survey_asset.html", asset=asset[0])


@employee_bp.route("/add_asset", methods=["GET", "POST"])
@role_required(["employee"])
def add_asset():
    """Add a new asset."""

    if request.method == "POST":
        name = request.form.get("name")
        asset_type = request.form.get("type")
        installation_date = request.form.get("installation_date")
        location = request.form.get("location")

        # Validate required fields
        if not name or not asset_type or not installation_date:
            flash("Name, type, and installation date are required", "error")
            return render_template("employee/add_asset.html")

        asset_id = db.execute_query(
            employee_queries["asset_insert_query"],
            (name, asset_type, installation_date, location),
        )[0][0]

        flash("Asset added successfully", "success")
        return redirect(url_for("employee.view_asset", asset_id=asset_id))

    return render_template("employee/add_asset.html")
