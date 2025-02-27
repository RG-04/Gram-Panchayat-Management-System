from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required
from app import db
from datetime import datetime

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/dashboard')
@role_required(['citizen'])
def dashboard():
    """Citizen dashboard page."""
    # Get current date for footer
    current_date = datetime.now().strftime('%d %B %Y')
    return render_template('citizen/dashboard.html', current_date=current_date)

@citizen_bp.route('/statistics')
@role_required(['citizen'])
def statistics():
    """Display statistics based on category."""
    category = request.args.get('category', 'education')
    
    # Validate category
    valid_categories = ['education', 'health', 'agriculture']
    if category not in valid_categories:
        category = 'education'  # Default to education if invalid
    
    # Based on the category, fetch different statistics
    if category == 'education':
        # Example education statistics
        # In a real application, you would fetch this data from your database
        education_stats = {
            'total_schools': 5,
            'total_students': 1250,
            'literacy_rate': 78.5,
            'schools': [
                {'name': 'Sundarpur Primary School', 'students': 500, 'teachers': 15},
                {'name': 'Chandanagar High School', 'students': 750, 'teachers': 25}
            ]
        }
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Education Statistics',
            stats=education_stats
        )
    
    elif category == 'health':
        # Example health statistics
        health_stats = {
            'total_hospitals': 2,
            'total_beds': 75,
            'vaccination_rate': 85.2,
            'hospitals': [
                {'name': 'Sundarpur Primary Health Center', 'beds': 25, 'doctors': 5},
                {'name': 'Chandanagar General Hospital', 'beds': 50, 'doctors': 12}
            ]
        }
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Health Statistics',
            stats=health_stats
        )
    
    elif category == 'agriculture':
        # Example agriculture statistics
        agriculture_stats = {
            'total_land_area': 3500,
            'irrigated_area': 2200,
            'main_crops': ['Rice', 'Wheat', 'Vegetables'],
            'schemes': [
                {'name': 'Farmers Subsidy Program', 'beneficiaries': 150},
                {'name': 'Irrigation Development Scheme', 'beneficiaries': 85}
            ]
        }
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Agriculture Statistics',
            stats=agriculture_stats
        )

@citizen_bp.route('/profile')
@role_required(['citizen'])
def profile():
    """User profile page."""
    # Get citizen profile data
    query = """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Income, 
               c.Occupation, c.Phone, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
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
        'citizen/profile.html',
        profile=profile[0] if profile else None,
        user=user[0] if user else None
    )

@citizen_bp.route('/certificates')
@role_required(['citizen'])
def certificates():
    """View certificates page."""
    cert_query = """
        SELECT Type, CitizenID, DateIssued
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY DateIssued DESC
    """
    certificates = db.execute_query(cert_query, (session['citizen_id'],))
    
    return render_template('citizen/certificates.html', certificates=certificates)

@citizen_bp.route('/certificate/<certificate_type>')
@role_required(['citizen'])
def view_certificate(certificate_type):
    """View a specific certificate."""
    cert_query = """
        SELECT Type, CitizenID, DateIssued, File
        FROM Certificates
        WHERE Type = %s AND CitizenID = %s
    """
    certificate = db.execute_query(cert_query, (certificate_type, session['citizen_id']))
    
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('citizen.certificates'))
    
    return render_template('citizen/view_certificate.html', certificate=certificate[0])

@citizen_bp.route('/schemes')
@role_required(['citizen'])
def schemes():
    """View and apply for schemes."""
    # Get all available schemes
    all_schemes_query = """
        SELECT s.SchemeID, s.Description, f.Fee,
               CASE WHEN se.CitizenID IS NOT NULL THEN true ELSE false END as enrolled
        FROM Schemes s
        LEFT JOIN Forms f ON s.SchemeID = f.SchemeID
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID AND se.CitizenID = %s
        ORDER BY s.SchemeID
    """
    schemes = db.execute_query(all_schemes_query, (session['citizen_id'],))
    
    # Get citizen's enrolled schemes
    enrolled_query = """
        SELECT se.SchemeID, s.Description, se.Date
        FROM SchemeEnrollment se
        JOIN Schemes s ON se.SchemeID = s.SchemeID
        WHERE se.CitizenID = %s
        ORDER BY se.Date DESC
    """
    enrolled = db.execute_query(enrolled_query, (session['citizen_id'],))
    
    return render_template(
        'citizen/schemes.html',
        schemes=schemes,
        enrolled=enrolled
    )

@citizen_bp.route('/apply_scheme/<int:scheme_id>', methods=['POST'])
@role_required(['citizen'])
def apply_scheme(scheme_id):
    """Apply for a scheme."""
    # Check if already enrolled
    check_query = """
        SELECT COUNT(*) FROM SchemeEnrollment
        WHERE SchemeID = %s AND CitizenID = %s
    """
    count = db.execute_query(check_query, (scheme_id, session['citizen_id']))[0][0]
    
    if count > 0:
        flash('You are already enrolled in this scheme', 'info')
        return redirect(url_for('citizen.schemes'))
    
    # Insert new enrollment
    insert_query = """
        INSERT INTO SchemeEnrollment (SchemeID, CitizenID, Date)
        VALUES (%s, %s, CURRENT_DATE)
    """
    db.execute_query(insert_query, (scheme_id, session['citizen_id']), fetch=False)
    
    flash('Successfully applied for the scheme', 'success')
    return redirect(url_for('citizen.schemes'))

@citizen_bp.route('/education')
@role_required(['citizen'])
def education():
    """View education details."""
    education_query = """
        SELECT a.CitizenID, a.SchoolID, s.Name as SchoolName, 
               a.Qualification, a.PassDate
        FROM AttendsSchool a
        JOIN Schools s ON a.SchoolID = s.SchoolID
        WHERE a.CitizenID = %s
        ORDER BY a.PassDate DESC
    """
    education = db.execute_query(education_query, (session['citizen_id'],))
    
    # Get list of schools for form
    schools_query = "SELECT SchoolID, Name FROM Schools ORDER BY Name"
    schools = db.execute_query(schools_query)
    
    return render_template(
        'citizen/education.html',
        education=education,
        schools=schools
    )

@citizen_bp.route('/update_password', methods=['GET', 'POST'])
@role_required(['citizen'])
def update_password():
    """Update password page."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('citizen/update_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('citizen/update_password.html')
        
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
            return render_template('citizen/update_password.html')
        
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
        return redirect(url_for('citizen.profile'))
    
    return render_template('citizen/update_password.html')