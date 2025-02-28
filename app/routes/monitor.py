from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required, hash_password
from app import db

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/dashboard')
@role_required(['monitor'])
def dashboard():
    """Monitor dashboard page."""
    # Get monitor information
    monitor_query = """
        SELECT MonitorID, Name
        FROM Monitors
        WHERE MonitorID = %s
    """
    monitor_info = db.execute_query(monitor_query, (session['monitor_id'],))
    
    # Count statistics
    citizen_count = db.execute_query("SELECT COUNT(*) FROM Citizen")[0][0]
    employee_count = db.execute_query('SELECT COUNT(*) FROM EmployeeCitizens')[0][0]
    scheme_count = db.execute_query("SELECT COUNT(*) FROM Schemes")[0][0]
    land_count = db.execute_query("SELECT COUNT(*) FROM Land")[0][0]
    
    return render_template(
        'monitor/dashboard.html',
        monitor=monitor_info[0] if monitor_info else None,
        citizen_count=citizen_count,
        employee_count=employee_count,
        scheme_count=scheme_count,
        land_count=land_count
    )

@monitor_bp.route('/citizens')
@role_required(['monitor'])
def citizens():
    """View citizens data."""
    # Get all citizens with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Count total citizens for pagination
    total_count = db.execute_query(
        "SELECT COUNT(*) FROM Citizen"
    )[0][0]
    
    # Get citizens with household info
    citizens_query = """
        SELECT c.Aadhaar, c.Name, c.Gender, c.Income, c.Occupation, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        ORDER BY c.Name
        LIMIT %s OFFSET %s
    """
    citizens_list = db.execute_query(citizens_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'monitor/citizens.html',
        citizens=citizens_list,
        current_page=page,
        total_pages=total_pages
    )

@monitor_bp.route('/citizen/<aadhaar>')
@role_required(['monitor'])
def view_citizen(aadhaar):
    """View citizen details."""
    # Get citizen details
    citizen_query = """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Income, c.Occupation, 
               c.Phone, h.Address, h.HouseholdID
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        WHERE c.Aadhaar = %s
    """
    citizen = db.execute_query(citizen_query, (aadhaar,))
    
    if not citizen:
        flash('Citizen not found', 'error')
        return redirect(url_for('monitor.citizens'))
    
    # Get certificates
    cert_query = """
        SELECT CertificateID, Type, DateIssued
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY DateIssued DESC
    """
    certificates = db.execute_query(cert_query, (aadhaar,))
    
    # Get land records
    land_query = """
        SELECT LandID, Size, Location
        FROM Land
        WHERE OwnerID = %s
    """
    land_records = db.execute_query(land_query, (aadhaar,))
    
    # Get schemes
    schemes_query = """
        SELECT se.EnrollmentID, s.Description, se.Date
        FROM SchemeEnrollment se
        JOIN Schemes s ON se.SchemeID = s.SchemeID
        WHERE se.CitizenID = %s
        ORDER BY se.Date DESC
    """
    schemes = db.execute_query(schemes_query, (aadhaar,))
    
    # Get education details
    education_query = """
        SELECT a.SchoolID, s.Name as SchoolName, a.Qualification, a."Pass Date"
        FROM AttendsSchool a
        JOIN Schools s ON a.SchoolID = s.SchoolID
        WHERE a.CitizenID = %s
    """
    education = db.execute_query(education_query, (aadhaar,))
    
    # Check if citizen is an employee
    employee_query = """
        SELECT ec.EmployeeID, ec.StartDate, ec.TermDuration
        FROM EmployeeCitizens ec
        WHERE ec.CitizenID = %s
    """
    employee = db.execute_query(employee_query, (aadhaar,))
    
    return render_template(
        'monitor/view_citizen.html',
        citizen=citizen[0],
        certificates=certificates,
        land_records=land_records,
        schemes=schemes,
        education=education,
        is_employee=len(employee) > 0,
        employee=employee[0] if employee else None
    )

@monitor_bp.route('/employees')
@role_required(['monitor'])
def employees():
    """View employees data."""
    # Get all employees with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Count total employees for pagination
    total_count = db.execute_query(
        'SELECT COUNT(*) FROM EmployeeCitizens'
    )[0][0]
    
    # Get employees with citizen info
    employees_query = """
        SELECT ec.EmployeeID, ec.CitizenID, c.Name, ec.StartDate, 
               ec.TermDuration, c.Phone
        FROM EmployeeCitizens ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        ORDER BY ec.StartDate DESC
        LIMIT %s OFFSET %s
    """
    employees_list = db.execute_query(employees_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'monitor/employees.html',
        employees=employees_list,
        current_page=page,
        total_pages=total_pages
    )

@monitor_bp.route('/schemes')
@role_required(['monitor'])
def schemes():
    """View schemes data."""
    # Get all schemes with enrollment counts
    schemes_query = """
        SELECT s.SchemeID, s.Description, COUNT(se.EnrollmentID) as enrollment_count
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        GROUP BY s.SchemeID, s.Description
        ORDER BY s.SchemeID
    """
    schemes = db.execute_query(schemes_query)
    
    return render_template('monitor/schemes.html', schemes=schemes)

@monitor_bp.route('/scheme_enrollments/<int:scheme_id>')
@role_required(['monitor'])
def scheme_enrollments(scheme_id):
    """View enrollments for a specific scheme."""
    # Get scheme details
    scheme_query = """
        SELECT SchemeID, Description
        FROM Schemes
        WHERE SchemeID = %s
    """
    scheme = db.execute_query(scheme_query, (scheme_id,))
    
    if not scheme:
        flash('Scheme not found', 'error')
        return redirect(url_for('monitor.schemes'))
    
    # Get enrollments
    enrollments_query = """
        SELECT se.EnrollmentID, se.CitizenID, c.Name, se.Date, c.Income
        FROM SchemeEnrollment se
        JOIN Citizen c ON se.CitizenID = c.Aadhaar
        WHERE se.SchemeID = %s
        ORDER BY se.Date DESC
    """
    enrollments = db.execute_query(enrollments_query, (scheme_id,))
    
    return render_template(
        'monitor/scheme_enrollments.html',
        scheme=scheme[0],
        enrollments=enrollments
    )

@monitor_bp.route('/land_records')
@role_required(['monitor'])
def land_records():
    """View land records."""
    # Get land records with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Count total land records for pagination
    total_count = db.execute_query(
        "SELECT COUNT(*) FROM Land"
    )[0][0]
    
    # Get land records with owner info
    land_query = """
        SELECT l.LandID, l.Size, l.Location, l.OwnerID, c.Name
        FROM Land l
        JOIN Citizen c ON l.OwnerID = c.Aadhaar
        ORDER BY l.LandID
        LIMIT %s OFFSET %s
    """
    land_records = db.execute_query(land_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'monitor/land_records.html',
        land_records=land_records,
        current_page=page,
        total_pages=total_pages
    )

@monitor_bp.route('/schools')
@role_required(['monitor'])
def schools():
    """View schools data."""
    # Get all schools with student counts
    schools_query = """
        SELECT s.SchoolID, s.Name, s.Capacity, COUNT(a.AttendanceID) as student_count
        FROM Schools s
        LEFT JOIN AttendsSchool a ON s.SchoolID = a.SchoolID
        GROUP BY s.SchoolID, s.Name, s.Capacity
        ORDER BY s.Name
    """
    schools = db.execute_query(schools_query)
    
    return render_template('monitor/schools.html', schools=schools)

@monitor_bp.route('/school_students/<int:school_id>')
@role_required(['monitor'])
def school_students(school_id):
    """View students for a specific school."""
    # Get school details
    school_query = """
        SELECT SchoolID, Name, Capacity
        FROM Schools
        WHERE SchoolID = %s
    """
    school = db.execute_query(school_query, (school_id,))
    
    if not school:
        flash('School not found', 'error')
        return redirect(url_for('monitor.schools'))
    
    # Get students
    students_query = """
        SELECT a.AttendanceID, a.CitizenID, c.Name, a.Qualification, a."Pass Date"
        FROM AttendsSchool a
        JOIN Citizen c ON a.CitizenID = c.Aadhaar
        WHERE a.SchoolID = %s
        ORDER BY a."Pass Date" DESC
    """
    students = db.execute_query(students_query, (school_id,))
    
    return render_template(
        'monitor/school_students.html',
        school=school[0],
        students=students
    )

@monitor_bp.route('/report')
@role_required(['monitor'])
def report():
    """Generate and view reports."""
    # Get statistics for reports
    
    # Citizen statistics by gender
    gender_stats_query = """
        SELECT Gender, COUNT(*) as count
        FROM Citizen
        WHERE Gender IS NOT NULL
        GROUP BY Gender
    """
    gender_stats = db.execute_query(gender_stats_query)
    
    # Income distribution
    income_stats_query = """
        SELECT 
            CASE 
                WHEN Income < 100000 THEN 'Below 1 Lakh'
                WHEN Income BETWEEN 100000 AND 300000 THEN '1-3 Lakhs'
                WHEN Income BETWEEN 300001 AND 500000 THEN '3-5 Lakhs'
                WHEN Income > 500000 THEN 'Above 5 Lakhs'
            END as income_range,
            COUNT(*) as count
        FROM Citizen
        WHERE Income IS NOT NULL
        GROUP BY income_range
        ORDER BY 
            CASE income_range
                WHEN 'Below 1 Lakh' THEN 1
                WHEN '1-3 Lakhs' THEN 2
                WHEN '3-5 Lakhs' THEN 3
                WHEN 'Above 5 Lakhs' THEN 4
            END
    """
    income_stats = db.execute_query(income_stats_query)
    
    # Occupation distribution (top 5)
    occupation_stats_query = """
        SELECT Occupation, COUNT(*) as count
        FROM Citizen
        WHERE Occupation IS NOT NULL
        GROUP BY Occupation
        ORDER BY count DESC
        LIMIT 5
    """
    occupation_stats = db.execute_query(occupation_stats_query)
    
    # Scheme enrollment counts
    scheme_stats_query = """
        SELECT s.Description, COUNT(se.EnrollmentID) as count
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        GROUP BY s.SchemeID, s.Description
        ORDER BY count DESC
    """
    scheme_stats = db.execute_query(scheme_stats_query)
    
    return render_template(
        'monitor/report.html',
        gender_stats=gender_stats,
        income_stats=income_stats,
        occupation_stats=occupation_stats,
        scheme_stats=scheme_stats
    )

@monitor_bp.route('/profile')
@role_required(['monitor'])
def profile():
    """Monitor profile page."""
    # Get monitor profile data
    query = """
        SELECT MonitorID, Name
        FROM Monitors
        WHERE MonitorID = %s
    """
    profile = db.execute_query(query, (session['monitor_id'],))
    
    # Get user account data
    user_query = """
        SELECT username, auth
        FROM users
        WHERE MonitorID = %s
    """
    user = db.execute_query(user_query, (session['monitor_id'],))
    
    return render_template(
        'monitor/profile.html',
        profile=profile[0] if profile else None,
        user=user[0] if user else None
    )

@monitor_bp.route('/update_password', methods=['GET', 'POST'])
@role_required(['monitor'])
def update_password():
    """Update password page."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('monitor/update_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('monitor/update_password.html')
        
        # Verify current password
        from app.utils.auth_utils import verify_password, hash_password
        
        # Get current password hash and salt
        query = 'SELECT password, salt FROM users WHERE UserID = %s'
        result = db.execute_query(query, (session['user_id'],))
        
        if not result:
            flash('User not found', 'error')
            return redirect(url_for('auth.logout'))
        
        stored_hash, salt = result[0]
        
        if not verify_password(current_password, stored_hash, salt):
            flash('Current password is incorrect', 'error')
            return render_template('monitor/update_password.html')
        
        # Update password
        new_hash, new_salt = hash_password(new_password)
        
        update_query = """
            UPDATE users
            SET password = %s, salt = %s
            WHERE UserID = %s
        """
        db.execute_query(
            update_query,
            (new_hash, new_salt, session['user_id']),
            fetch=False
        )
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('monitor.profile'))
    
    return render_template('monitor/update_password.html')