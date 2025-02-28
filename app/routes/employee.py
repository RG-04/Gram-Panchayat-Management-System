from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required
from app import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime

employee_bp = Blueprint("employee", __name__)


@employee_bp.route("/dashboard")
@role_required(["employee"])
def dashboard():
    """Employee dashboard page."""
    # Get employee information
    employee_query = """
        SELECT ec.EmployeeID, c.Aadhaar, c.Name, c.Phone, 
               ec.StartDate, ec.TermDuration
        FROM EmployeeCitizens ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        WHERE ec.CitizenID = %s
    """
    employee_info = db.execute_query(employee_query, (session["citizen_id"],))

    # Count total citizens
    citizen_count_query = """
        SELECT COUNT(*) FROM Citizen
    """
    citizen_count = db.execute_query(citizen_count_query)[0][0]

    # Count certificates issued
    cert_count_query = """
        SELECT COUNT(*) FROM Certificates
    """
    cert_count = db.execute_query(cert_count_query)[0][0]

    # Count scheme enrollments
    scheme_count_query = """
        SELECT COUNT(*) FROM SchemeEnrollment
    """
    scheme_count = db.execute_query(scheme_count_query)[0][0]

    # Get current date for footer
    current_date = datetime.now().strftime("%d %B %Y")

    return render_template(
        "employee/dashboard.html",
        employee=employee_info[0] if employee_info else None,
        citizen_count=citizen_count,
        cert_count=cert_count,
        scheme_count=scheme_count,
        current_date=current_date,
    )


@employee_bp.route("/certificates")
@role_required(["employee"])
def certificates():
    """View and manage citizens."""
    # Get all citizens
    citizens_query = """
        SELECT c.Aadhaar, c.Name, c.Gender, c.DOB, c.Phone, c.Income,
               c.Occupation, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        ORDER BY c.Name
    """
    citizens_list = db.execute_query(citizens_query)

    return render_template("employee/certificates.html", citizens=citizens_list)


@employee_bp.route("/citizen/<aadhaar>")
@role_required(["employee"])
def view_citizen(aadhaar):
    """View citizen details."""
    # Get citizen details
    citizen_query = """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Income, c.Occupation, 
               c.Phone, h.Address, h.HouseholdID, c.MotherID, c.FatherID
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        WHERE c.Aadhaar = %s
    """
    citizen = db.execute_query(citizen_query, (aadhaar,))

    if not citizen:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))
    
    father = False
    mother = False

    parent_query = """
        SELECT c.Aadhaar, c.Name
        FROM Citizen c
        WHERE c.Aadhaar = %s
    """

    if citizen[0][-1] is not None:
        father = db.execute_query(parent_query, (citizen[0][-1],))

    if citizen[0][-2] is not None:
        mother = db.execute_query(parent_query, (citizen[0][-2],))

    print(str(citizen[0][-1]), str(citizen[0][-2]))

    children_query = """
        SELECT c.Aadhaar, c.Name
        FROM Citizen c
        WHERE c.MotherID = %s OR c.FatherID = %s
    """
    children = db.execute_query(children_query, (citizen[0][0], citizen[0][0]))

    print(children)

    family_income_query = """
        SELECT SUM(c.Income) as FamilyIncome
        FROM Citizen c
        WHERE HouseholdID = %s
    """

    family_income = db.execute_query(family_income_query, (citizen[0][-3],))[0][0]
    print(family_income)

    # Get citizen certificates
    cert_query = """
        SELECT Category, Name, DateIssued, 
               CASE WHEN File IS NOT NULL THEN true ELSE false END as has_file
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY Category, DateIssued DESC
    """
    certificates = db.execute_query(cert_query, (aadhaar,))

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
    """
    Update a citizen's information in the database.

    Args:
        aadhaar: The Aadhaar number of the citizen to update

    Returns:
        Redirects to the citizen view page with success or error message
    """
    try:
        # Get form data
        name = request.form.get("name")
        dob_str = request.form.get("dob")
        gender = request.form.get("gender")
        income_str = request.form.get("income")
        occupation = request.form.get("occupation")
        phone = request.form.get("phone")
        household_id_str = request.form.get("householdid")

        # Validate required fields
        if not name:
            flash("Name is required", "error")
            return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        # Convert and validate date
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format", "error")
                return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        # Convert and validate income
        income = None
        if income_str:
            try:
                income = Decimal(income_str)
                if income < 0:
                    raise ValueError("Income cannot be negative")
            except (ValueError, InvalidOperation):
                flash("Invalid income value", "error")
                return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        # Convert and validate household ID
        household_id = None
        if household_id_str:
            try:
                household_id = int(household_id_str)

                # Check if household exists
                cursor = db.connection.cursor()
                cursor.execute(
                    "SELECT HouseholdID FROM Households WHERE HouseholdID = %s",
                    (household_id,),
                )
                household_exists = cursor.fetchone()
                cursor.close()

                if not household_exists:
                    flash("Household ID does not exist", "error")
                    return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

            except ValueError:
                flash("Invalid Household ID", "error")
                return redirect(url_for("employee.view_citizen", aadhaar=aadhaar))

        # Update citizen information
        cursor = db.connection.cursor()
        cursor.execute(
            """
            UPDATE Citizen
            SET Name = %s, DOB = %s, Gender = %s, Income = %s, 
                Occupation = %s, Phone = %s, HouseholdID = %s
            WHERE Aadhaar = %s
        """,
            (name, dob, gender, income, occupation, phone, household_id, aadhaar),
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
    # Get citizen name
    name_query = """
        SELECT Name FROM Citizen WHERE Aadhaar = %s
    """
    citizen_name = db.execute_query(name_query, (aadhaar,))

    if not citizen_name:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))

    # Get citizen certificates
    cert_query = """
        SELECT Category, Name, DateIssued, 
               CASE WHEN File IS NOT NULL THEN true ELSE false END as has_file
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY Category, DateIssued DESC
    """
    certificates = db.execute_query(cert_query, (aadhaar,))

    # Get list of certificate categories for the form
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
    cert_query = """
        SELECT Category, Name, CitizenID, DateIssued, File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """
    certificate = db.execute_query(cert_query, (category, name, aadhaar))

    if not certificate:
        flash("Certificate not found", "error")
        return redirect(url_for("employee.citizen_certificates", aadhaar=aadhaar))

    # Get citizen name
    name_query = """
        SELECT Name FROM Citizen WHERE Aadhaar = %s
    """
    citizen_name = db.execute_query(name_query, (aadhaar,))

    return render_template(
        "employee/view_certificate.html",
        certificate=certificate[0],
        citizen_name=citizen_name[0][0] if citizen_name else "Unknown",
    )


@employee_bp.route("/citizen/<aadhaar>/certificate/file/<category>/<name>")
@role_required(["employee"])
def certificate_file(aadhaar, category, name):
    """Get the certificate file."""
    from flask import send_file
    import io

    cert_query = """
        SELECT File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """
    result = db.execute_query(cert_query, (category, name, aadhaar))

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

    # Convert BYTEA data to bytes
    file_data = result[0][0]

    # Create a file-like object from the bytes
    file_stream = io.BytesIO(file_data)

    # Return the PDF file
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

    # Get file data
    file_data = certificate_file.read()

    # Update certificate with file
    update_query = """
        UPDATE Certificates
        SET File = %s
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """
    db.execute_query(update_query, (file_data, category, name, aadhaar), fetch=False)

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
    # Get citizen name
    name_query = """
        SELECT Name FROM Citizen WHERE Aadhaar = %s
    """
    citizen_name = db.execute_query(name_query, (aadhaar,))

    if not citizen_name:
        flash("Citizen not found", "error")
        return redirect(url_for("employee.certificates"))

    # Get existing certificate categories
    categories_query = """
        SELECT DISTINCT Category FROM Certificates ORDER BY Category
    """
    existing_categories = db.execute_query(categories_query)

    # Convert to list of strings
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

        # Use custom category if provided and "Other" is selected
        if category == "Other" and custom_category:
            category = custom_category

        # Check if certificate already exists
        check_query = """
            SELECT COUNT(*) FROM Certificates
            WHERE Category = %s AND Name = %s AND CitizenID = %s
        """
        count = db.execute_query(check_query, (category, name, aadhaar))[0][0]

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

        # Process file if provided
        file_data = None
        if certificate_file and certificate_file.filename:
            # Get file data
            file_data = certificate_file.read()

        # Insert certificate
        if file_data:
            insert_query = """
                INSERT INTO Certificates (Category, Name, CitizenID, DateIssued, File)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_query(
                insert_query,
                (category, name, aadhaar, date_issued, file_data),
                fetch=False,
            )
        else:
            insert_query = """
                INSERT INTO Certificates (Category, Name, CitizenID, DateIssued)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(
                insert_query, (category, name, aadhaar, date_issued), fetch=False
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
    return render_template("employee/schemes.html")
