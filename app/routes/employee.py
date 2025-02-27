from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required, hash_password
from app import db

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/dashboard')
@role_required(['employee'])
def dashboard():
    """Employee dashboard page."""
    # Get employee information
    employee_query = """
        SELECT ec.EmployeeID, c.Aadhaar, c.Name, c.Phone, 
               ec."Start Date", ec."Term-Duration"
        FROM "Employee-Citizens" ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        WHERE ec.CitizenID = %s
    """
    employee_info = db.execute_query(employee_query, (session['citizen_id'],))
    
    # Count certificates issued
    cert_count_query = """
        SELECT COUNT(*) FROM Certificates
    """
    cert_count = db.execute_query(cert_count_query)[0][0]
    
    # Count scheme enrollments
    scheme_count_query = """
        SELECT COUNT(*) FROM "Scheme-Enrollment"
    """
    scheme_count = db.execute_query(scheme_count_query)[0][0]
    
    # Count citizens
    citizen_count_query = """
        SELECT COUNT(*) FROM Citizen
    """
    citizen_count = db.execute_query(citizen_count_query)[0][0]
    
    return render_template(
        'employee/dashboard.html',
        employee=employee_info[0] if employee_info else None,
        cert_count=cert_count,
        scheme_count=scheme_count,
        citizen_count=citizen_count
    )

@employee_bp.route('/citizens')
@role_required(['employee'])
def citizens():
    """View and manage citizens."""
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
        SELECT c.Aadhaar, c.Name, c.Gender, c.Phone, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        ORDER BY c.Name
        LIMIT %s OFFSET %s
    """
    citizens_list = db.execute_query(citizens_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'employee/citizens.html',
        citizens=citizens_list,
        current_page=page,
        total_pages=total_pages
    )

@employee_bp.route('/citizen/<aadhaar>')
@role_required(['employee'])
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
        return redirect(url_for('employee.citizens'))
    
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
        FROM "Scheme-Enrollment" se
        JOIN Schemes s ON se.SchemeID = s.SchemeID
        WHERE se.CitizenID = %s
        ORDER BY se.Date DESC
    """
    schemes = db.execute_query(schemes_query, (aadhaar,))
    
    # Get education details
    education_query = """
        SELECT a.SchoolID, s.Name as SchoolName, a.Qualification, a."Pass Date"
        FROM "Attends-School" a
        JOIN Schools s ON a.SchoolID = s.SchoolID
        WHERE a.CitizenID = %s
    """
    education = db.execute_query(education_query, (aadhaar,))
    
    # Check if citizen has user account
    user_query = """
        SELECT UserID, username, auth
        FROM "User"
        WHERE CitizenID = %s
    """
    user = db.execute_query(user_query, (aadhaar,))
    
    return render_template(
        'employee/view_citizen.html',
        citizen=citizen[0],
        certificates=certificates,
        land_records=land_records,
        schemes=schemes,
        education=education,
        user=user[0] if user else None
    )

@employee_bp.route('/add_citizen', methods=['GET', 'POST'])
@role_required(['employee'])
def add_citizen():
    """Add a new citizen."""
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar')
        name = request.form.get('name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        income = request.form.get('income')
        occupation = request.form.get('occupation')
        phone = request.form.get('phone')
        
        # Get or create household
        household_id = request.form.get('household_id')
        address = request.form.get('address')
        
        if not household_id and address:
            # Create new household
            household_query = """
                INSERT INTO Households (Address)
                VALUES (%s)
                RETURNING HouseholdID
            """
            household_id = db.execute_query(household_query, (address,))[0][0]
        
        # Insert new citizen
        citizen_query = """
            INSERT INTO Citizen (Aadhaar, Name, DOB, Gender, Income, 
                                Occupation, Phone, HouseholdID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_query(
            citizen_query,
            (aadhaar, name, dob, gender, income, occupation, phone, household_id),
            fetch=False
        )
        
        flash('Citizen added successfully', 'success')
        return redirect(url_for('employee.view_citizen', aadhaar=aadhaar))
    
    # Get all households for dropdown
    households_query = """
        SELECT HouseholdID, Address
        FROM Households
        ORDER BY Address
    """
    households = db.execute_query(households_query)
    
    return render_template('employee/add_citizen.html', households=households)

@employee_bp.route('/edit_citizen/<aadhaar>', methods=['GET', 'POST'])
@role_required(['employee'])
def edit_citizen(aadhaar):
    """Edit citizen details."""
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        income = request.form.get('income')
        occupation = request.form.get('occupation')
        phone = request.form.get('phone')
        household_id = request.form.get('household_id')
        
        # Update citizen
        update_query = """
            UPDATE Citizen
            SET Name = %s, DOB = %s, Gender = %s, Income = %s,
                Occupation = %s, Phone = %s, HouseholdID = %s
            WHERE Aadhaar = %s
        """
        db.execute_query(
            update_query,
            (name, dob, gender, income, occupation, phone, household_id, aadhaar),
            fetch=False
        )
        
        flash('Citizen updated successfully', 'success')
        return redirect(url_for('employee.view_citizen', aadhaar=aadhaar))
    
    # Get citizen details
    citizen_query = """
        SELECT Aadhaar, Name, DOB, Gender, Income, Occupation, 
               Phone, HouseholdID
        FROM Citizen
        WHERE Aadhaar = %s
    """
    citizen = db.execute_query(citizen_query, (aadhaar,))
    
    if not citizen:
        flash('Citizen not found', 'error')
        return redirect(url_for('employee.citizens'))
    
    # Get all households for dropdown
    households_query = """
        SELECT HouseholdID, Address
        FROM Households
        ORDER BY Address
    """
    households = db.execute_query(households_query)
    
    return render_template(
        'employee/edit_citizen.html',
        citizen=citizen[0],
        households=households
    )

@employee_bp.route('/create_user/<aadhaar>', methods=['GET', 'POST'])
@role_required(['employee'])
def create_user(aadhaar):
    """Create user account for a citizen."""
    # Check if user already exists
    check_query = """
        SELECT COUNT(*) FROM "User"
        WHERE CitizenID = %s
    """
    count = db.execute_query(check_query, (aadhaar,))[0][0]
    
    if count > 0:
        flash('User account already exists for this citizen', 'error')
        return redirect(url_for('employee.view_citizen', aadhaar=aadhaar))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('employee/create_user.html', aadhaar=aadhaar)
        
        # Check if username already exists
        username_check = """
            SELECT COUNT(*) FROM "User"
            WHERE username = %s
        """
        username_count = db.execute_query(username_check, (username,))[0][0]
        
        if username_count > 0:
            flash('Username already exists', 'error')
            return render_template('employee/create_user.html', aadhaar=aadhaar)
        
        # Hash password
        pw_hash, salt = hash_password(password)
        
        # Create user
        insert_query = """
            INSERT INTO "User" (CitizenID, MonitorID, username, password, auth, salt)
            VALUES (%s, NULL, %s, %s, 'citizen', %s)
        """
        db.execute_query(
            insert_query,
            (aadhaar, username, pw_hash, salt),
            fetch=False
        )
        
        flash('User account created successfully', 'success')
        return redirect(url_for('employee.view_citizen', aadhaar=aadhaar))
    
    # Get citizen name for display
    name_query = """
        SELECT Name FROM Citizen
        WHERE Aadhaar = %s
    """
    name = db.execute_query(name_query, (aadhaar,))[0][0]
    
    return render_template('employee/create_user.html', aadhaar=aadhaar, name=name)

@employee_bp.route('/certificates')
@role_required(['employee'])
def certificates():
    """Manage certificates."""
    # Get certificates with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Count total certificates for pagination
    total_count = db.execute_query(
        "SELECT COUNT(*) FROM Certificates"
    )[0][0]
    
    # Get certificates with citizen info
    cert_query = """
        SELECT c.CertificateID, c.Type, c.DateIssued, c.CitizenID, cit.Name
        FROM Certificates c
        JOIN Citizen cit ON c.CitizenID = cit.Aadhaar
        ORDER BY c.DateIssued DESC
        LIMIT %s OFFSET %s
    """
    certificates = db.execute_query(cert_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'employee/certificates.html',
        certificates=certificates,
        current_page=page,
        total_pages=total_pages
    )

@employee_bp.route('/issue_certificate', methods=['GET', 'POST'])
@role_required(['employee'])
def issue_certificate():
    """Issue a new certificate."""
    if request.method == 'POST':
        citizen_id = request.form.get('citizen_id')
        cert_type = request.form.get('type')
        date_issued = request.form.get('date_issued')
        
        # Validate input
        if not citizen_id or not cert_type or not date_issued:
            flash('All fields are required', 'error')
            
            # Get citizens for dropdown
            citizens_query = """
                SELECT Aadhaar, Name
                FROM Citizen
                ORDER BY Name
            """
            citizens = db.execute_query(citizens_query)
            
            return render_template('employee/issue_certificate.html', citizens=citizens)
        
        # Insert certificate
        cert_query = """
            INSERT INTO Certificates (Type, CitizenID, DateIssued)
            VALUES (%s, %s, %s)
            RETURNING CertificateID
        """
        cert_id = db.execute_query(cert_query, (cert_type, citizen_id, date_issued))[0][0]
        
        flash('Certificate issued successfully', 'success')
        return redirect(url_for('employee.certificates'))
    
    # Get citizens for dropdown
    citizens_query = """
        SELECT Aadhaar, Name
        FROM Citizen
        ORDER BY Name
    """
    citizens = db.execute_query(citizens_query)
    
    return render_template('employee/issue_certificate.html', citizens=citizens)

@employee_bp.route('/land_records')
@role_required(['employee'])
def land_records():
    """Manage land records."""
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
        'employee/land_records.html',
        land_records=land_records,
        current_page=page,
        total_pages=total_pages
    )

@employee_bp.route('/add_land', methods=['GET', 'POST'])
@role_required(['employee'])
def add_land():
    """Add a new land record."""
    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        size = request.form.get('size')
        location = request.form.get('location')
        
        # Validate input
        if not owner_id or not size or not location:
            flash('All fields are required', 'error')
            
            # Get citizens for dropdown
            citizens_query = """
                SELECT Aadhaar, Name
                FROM Citizen
                ORDER BY Name
            """
            citizens = db.execute_query(citizens_query)
            
            return render_template('employee/add_land.html', citizens=citizens)
        
        # Insert land record
        land_query = """
            INSERT INTO Land (OwnerID, Size, Location)
            VALUES (%s, %s, %s)
            RETURNING LandID
        """
        land_id = db.execute_query(land_query, (owner_id, size, location))[0][0]
        
        flash('Land record added successfully', 'success')
        return redirect(url_for('employee.land_records'))
    
    # Get citizens for dropdown
    citizens_query = """
        SELECT Aadhaar, Name
        FROM Citizen
        ORDER BY Name
    """
    citizens = db.execute_query(citizens_query)
    
    return render_template('employee/add_land.html', citizens=citizens)

@employee_bp.route('/schemes')
@role_required(['employee'])
def schemes():
    """Manage schemes."""
    # Get all schemes
    schemes_query = """
        SELECT s.SchemeID, s.Description, COUNT(se.EnrollmentID) as enrollment_count
        FROM Schemes s
        LEFT JOIN "Scheme-Enrollment" se ON s.SchemeID = se.SchemeID
        GROUP BY s.SchemeID, s.Description
        ORDER BY s.SchemeID
    """
    schemes = db.execute_query(schemes_query)
    
    return render_template('employee/schemes.html', schemes=schemes)

@employee_bp.route('/scheme_enrollments/<int:scheme_id>')
@role_required(['employee'])
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
        return redirect(url_for('employee.schemes'))
    
    # Get enrollments
    enrollments_query = """
        SELECT se.EnrollmentID, se.CitizenID, c.Name, se.Date
        FROM "Scheme-Enrollment" se
        JOIN Citizen c ON se.CitizenID = c.Aadhaar
        WHERE se.SchemeID = %s
        ORDER BY se.Date DESC
    """
    enrollments = db.execute_query(enrollments_query, (scheme_id,))
    
    return render_template(
        'employee/scheme_enrollments.html',
        scheme=scheme[0],
        enrollments=enrollments
    )

@employee_bp.route('/profile')
@role_required(['employee'])
def profile():
    """User profile page."""
    # Get employee profile data
    query = """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Phone, 
               ec."Start Date", ec."Term-Duration"
        FROM Citizen c
        JOIN "Employee-Citizens" ec ON c.Aadhaar = ec.CitizenID
        WHERE c.Aadhaar = %s
    """
    profile = db.execute_query(query, (session['citizen_id'],))
    
    # Get user account data
    user_query = """
        SELECT username, auth
        FROM "User"
        WHERE CitizenID = %s
    """
    user = db.execute_query(user_query, (session['citizen_id'],))
    
    return render_template(
        'employee/profile.html',
        profile=profile[0] if profile else None,
        user=user[0] if user else None
    )

@employee_bp.route('/update_password', methods=['GET', 'POST'])
@role_required(['employee'])
def update_password():
    """Update password page."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('employee/update_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('employee/update_password.html')
        
        # Verify current password
        from app.utils.auth_utils import verify_password, hash_password
        
        # Get current password hash and salt
        query = 'SELECT password, salt FROM "User" WHERE UserID = %s'
        result = db.execute_query(query, (session['user_id'],))
        
        if not result:
            flash('User not found', 'error')
            return redirect(url_for('auth.logout'))
        
        stored_hash, salt = result[0]
        
        if not verify_password(current_password, stored_hash, salt):
            flash('Current password is incorrect', 'error')
            return render_template('employee/update_password.html')
        
        # Update password
        new_hash, new_salt = hash_password(new_password)
        
        update_query = """
            UPDATE "User"
            SET password = %s, salt = %s
            WHERE UserID = %s
        """
        db.execute_query(
            update_query,
            (new_hash, new_salt, session['user_id']),
            fetch=False
        )
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('employee.profile'))
    
    return render_template('employee/update_password.html')

@employee_bp.route('/add_scheme', methods=['GET', 'POST'])
@role_required(['employee'])
def add_scheme():
    """Add a new scheme."""
    if request.method == 'POST':
        description = request.form.get('description')
        fee = request.form.get('fee')
        
        # Validate input
        if not description:
            flash('Description is required', 'error')
            return render_template('employee/add_scheme.html')
        
        # Insert scheme
        scheme_query = """
            INSERT INTO Schemes (Description)
            VALUES (%s)
            RETURNING SchemeID
        """
        scheme_id = db.execute_query(scheme_query, (description,))[0][0]
        
        # If fee is provided, insert form record
        if fee:
            form_query = """
                INSERT INTO Forms (SchemeID, Fee)
                VALUES (%s, %s)
            """
            db.execute_query(form_query, (scheme_id, fee), fetch=False)
        
        flash('Scheme added successfully', 'success')
        return redirect(url_for('employee.schemes'))
    
    return render_template('employee/add_scheme.html')

@employee_bp.route('/schools')
@role_required(['employee'])
def schools():
    """Manage schools."""
    # Get all schools
    schools_query = """
        SELECT s.SchoolID, s.Name, s.Capacity, COUNT(a.AttendanceID) as student_count
        FROM Schools s
        LEFT JOIN "Attends-School" a ON s.SchoolID = a.SchoolID
        GROUP BY s.SchoolID, s.Name, s.Capacity
        ORDER BY s.Name
    """
    schools = db.execute_query(schools_query)
    
    return render_template('employee/schools.html', schools=schools)

@employee_bp.route('/add_school', methods=['GET', 'POST'])
@role_required(['employee'])
def add_school():
    """Add a new school."""
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity')
        
        # Validate input
        if not name:
            flash('Name is required', 'error')
            return render_template('employee/add_school.html')
        
        # Insert school
        school_query = """
            INSERT INTO Schools (Name, Capacity)
            VALUES (%s, %s)
            RETURNING SchoolID
        """
        school_id = db.execute_query(school_query, (name, capacity))[0][0]
        
        flash('School added successfully', 'success')
        return redirect(url_for('employee.schools'))
    
    return render_template('employee/add_school.html')

@employee_bp.route('/school_students/<int:school_id>')
@role_required(['employee'])
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
        return redirect(url_for('employee.schools'))
    
    # Get students
    students_query = """
        SELECT a.AttendanceID, a.CitizenID, c.Name, a.Qualification, a."Pass Date"
        FROM "Attends-School" a
        JOIN Citizen c ON a.CitizenID = c.Aadhaar
        WHERE a.SchoolID = %s
        ORDER BY a."Pass Date" DESC
    """
    students = db.execute_query(students_query, (school_id,))
    
    return render_template(
        'employee/school_students.html',
        school=school[0],
        students=students
    )

@employee_bp.route('/add_student/<int:school_id>', methods=['GET', 'POST'])
@role_required(['employee'])
def add_student(school_id):
    """Add a student to a school."""
    # Get school details
    school_query = """
        SELECT SchoolID, Name
        FROM Schools
        WHERE SchoolID = %s
    """
    school = db.execute_query(school_query, (school_id,))
    
    if not school:
        flash('School not found', 'error')
        return redirect(url_for('employee.schools'))
    
    if request.method == 'POST':
        citizen_id = request.form.get('citizen_id')
        qualification = request.form.get('qualification')
        pass_date = request.form.get('pass_date')
        
        # Validate input
        if not citizen_id:
            flash('Citizen is required', 'error')
            
            # Get citizens for dropdown
            citizens_query = """
                SELECT Aadhaar, Name
                FROM Citizen
                ORDER BY Name
            """
            citizens = db.execute_query(citizens_query)
            
            return render_template(
                'employee/add_student.html',
                school=school[0],
                citizens=citizens
            )
        
        # Insert school attendance record
        attendance_query = """
            INSERT INTO "Attends-School" (CitizenID, SchoolID, Qualification, "Pass Date")
            VALUES (%s, %s, %s, %s)
        """
        db.execute_query(
            attendance_query,
            (citizen_id, school_id, qualification, pass_date),
            fetch=False
        )
        
        flash('Student added successfully', 'success')
        return redirect(url_for('employee.school_students', school_id=school_id))
    
    # Get citizens for dropdown
    citizens_query = """
        SELECT Aadhaar, Name
        FROM Citizen
        ORDER BY Name
    """
    citizens = db.execute_query(citizens_query)
    
    return render_template(
        'employee/add_student.html',
        school=school[0],
        citizens=citizens
    )