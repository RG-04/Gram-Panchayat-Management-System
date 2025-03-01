from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file
import io
from app import db
from app.utils.auth_utils import role_required
from app.queries.citizen_queries import citizen_queries

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/dashboard')
@role_required(['citizen'])
def dashboard():
    """Citizen dashboard page."""
    return render_template('citizen/dashboard.html')

@citizen_bp.route('/statistics')
@role_required(['citizen'])
def statistics():
    """Display statistics based on category."""
    category = request.args.get('category', 'education')
    
    # Validate category
    valid_categories = ['education', 'health', 'agriculture', 'demographic']
    if category not in valid_categories:
        category = 'education'  # Default to education if invalid
    
    # Based on the category, fetch different statistics
    if category == 'education':
        schools = db.execute_query(citizen_queries['school_query'])
        literacy_rate = db.execute_query(citizen_queries['literacy_query'])[0][0]
        male_literacy_rate, female_literacy_rate = db.execute_query(citizen_queries['gender_literacy_query'])
        male_literacy_rate, female_literacy_rate = male_literacy_rate[0], female_literacy_rate[0]
        education_stats = {
            'total_schools': len(schools),
            'curr_students': sum([school[2] for school in schools]),
            'schools': [{'name': school[1], 'current_students': school[2], 'total_students': school[3]} for school in schools],
            'literacy_rate': literacy_rate,
            'male_literacy_rate': male_literacy_rate,            
            'female_literacy_rate': female_literacy_rate,
        }
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Education Statistics',
            stats=education_stats
        )
    
    elif category == 'health':
        hospitals = db.execute_query(citizen_queries['hospital_query'])
        vaccination_stats = db.execute_query(citizen_queries['vaccination_query'])
        health_stats = {
            'total_hospitals': len(hospitals),
            'total_beds': sum([hospital[3] for hospital in hospitals]),
            'hospitals': [{'name': hospital[1], 'beds': hospital[3], 'address': hospital[2]} for hospital in hospitals],
            'vaccination_stats': [
                {
                    'Disease': stat[0],
                    'VaccinatedCitizens': stat[1],
                    'VaccinationRate': stat[3]
                } for stat in vaccination_stats
            ]
        }
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Health Statistics',
            stats=health_stats
        )
    
    elif category == 'agriculture':
        # Execute queries
        total_land = db.execute_query(citizen_queries['total_land_query'])[0][0] or 0
        agricultural_area = db.execute_query(citizen_queries['agricultural_area_query'])[0][0] or 0
        agricultural_percentage = db.execute_query(citizen_queries['agricultural_percentage_query'])[0][0] or 0
        organic_percentage = db.execute_query(citizen_queries['organic_percentage_query'])[0][0] or 0
        crop_types = [row[0] for row in db.execute_query(citizen_queries['crop_types_query'])]        
        crops_result = db.execute_query(citizen_queries['crops_detail_query'])
        crops = []
        for row in crops_result:
            crops.append({
                'id': row[0],
                'name': row[1],
                'type': row[2] or 'Uncategorized',
                'area': round(row[3], 2),
                'yield': round(row[4], 2),
                'yield_per_hectare': round(row[5], 2),
                'organic': row[6]
            })
        
        # Get top crops for pie chart
        top_crops = db.execute_query(citizen_queries['top_crops_query'])
        crop_pie_data = {
            'labels': [row[0] for row in top_crops],
            'values': [float(row[1]) for row in top_crops]
        }
        
        # If we have less than 3 crops, we don't need an "Others" category
        if len(crops) <= 3:
            pass
        else:
            # Calculate "Others" category
            other_area = float(agricultural_area) - sum(crop_pie_data['values'])
            if other_area > 0:
                crop_pie_data['labels'].append('Others')
                crop_pie_data['values'].append(float(other_area))
    
        
        # Build agriculture statistics dictionary
        agriculture_stats = {
            'total_land_area': round(total_land, 2),
            'agricultural_area': round(agricultural_area, 2),
            'agricultural_percentage': agricultural_percentage,
            'organic_percentage': organic_percentage,
            'irrigated_area': round(float(agricultural_area) * 0.6, 2),  # Placeholder - replace with actual query
            'crop_types': crop_types,
            'crops': crops,
            'crop_pie_data': crop_pie_data,
            'main_crops': [crop['name'] for crop in crops[:5]],
        }
        
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Agriculture Statistics',
            stats=agriculture_stats
        )
    elif category == 'demographic':
        # Execute queries
        total_population = db.execute_query(citizen_queries['population_query'])[0][0]
        gender_distribution = db.execute_query(citizen_queries['gender_distribution_query'])
        sex_ratio = db.execute_query(citizen_queries['sex_ratio_query'])[0][0] or 0
        age_distribution = db.execute_query(citizen_queries['age_distribution_query'])
        literacy_rate = db.execute_query(citizen_queries['literacy_query'])[0][0] or 0
        birth_rate = db.execute_query(citizen_queries['birth_rate_query'])[0][0] or 0
        death_rate = db.execute_query(citizen_queries['death_rate_query'])[0][0] or 0
        household_stats = db.execute_query(citizen_queries['household_query'])
        occupation_stats = db.execute_query(citizen_queries['occupation_query'])
        income_distribution = db.execute_query(citizen_queries['income_distribution_query'])
        
        print(occupation_stats)

        # Format data for population pyramid
        age_groups = [row[0] for row in age_distribution]
        male_counts = [-int(row[1]) for row in age_distribution]  # Negative for left side of pyramid
        female_counts = [int(row[2]) for row in age_distribution]
        
        # Format data for gender pie chart
        gender_labels = [str(row[0]) for row in gender_distribution] 
        gender_values = [int(row[1]) for row in gender_distribution]
        
        print(gender_labels, gender_values)

        # Format data for occupation pie chart
        occupation_labels = [row[0] for row in occupation_stats]
        occupation_values = [row[1] for row in occupation_stats]
        
        print(occupation_labels, occupation_values)
        
        # Format data for income distribution chart
        income_labels = [row[0] for row in income_distribution]
        income_values = [row[1] for row in income_distribution]
        
        # Prepare demographic statistics
        total_households = household_stats[0][0] if household_stats else 0
        avg_household_size = household_stats[0][1] if household_stats else 0
        largest_household_size = household_stats[0][2] if household_stats else 0
        
        demographic_stats = {
            'total_population': total_population,
            'gender_distribution': {
                'labels': gender_labels,
                'values': gender_values
            },
            'sex_ratio': sex_ratio,
            'population_pyramid': {
                'age_groups': age_groups,
                'male_counts': male_counts,
                'female_counts': female_counts
            },
            'literacy_rate': literacy_rate,
            'birth_rate': birth_rate,
            'death_rate': death_rate,
            'household_stats': {
                'total_households': total_households,
                'avg_household_size': avg_household_size,
                'largest_household_size': largest_household_size
            },
            'occupation_distribution': {
                'labels': occupation_labels,
                'values': occupation_values
            },
            'income_distribution': {
                'labels': income_labels,
                'values': income_values
            }
        }
        
        return render_template(
            'citizen/statistics.html',
            category=category,
            category_title='Demographic Statistics',
            stats=demographic_stats
        )
    

@citizen_bp.route('/profile')
@role_required(['citizen', 'employee'])
def profile():
    """User profile page."""
    citizen_id = session['citizen_id']
    
    profile = db.execute_query(citizen_queries['profile_details_query'], (citizen_id,))
    user = db.execute_query(citizen_queries['user_query'], (citizen_id,))
    certificates = db.execute_query(citizen_queries['cert_query'], (citizen_id,))
    
    certificates_by_category = {}
    for cert in certificates:
        category = cert[0]
        if category not in certificates_by_category:
            certificates_by_category[category] = []
        certificates_by_category[category].append({
            'category': cert[0],
            'name': cert[1],
            'date_issued': cert[2]
        })

    return render_template(
        'citizen/profile.html',
        profile=profile[0] if profile else None,
        user=user[0] if user else None,
        certificates_by_category=certificates_by_category
    )

@citizen_bp.route('/certificate/<category>/<name>')
@role_required(['citizen', 'employee'])
def view_certificate(category, name):
    """View a specific certificate."""
    certificate = db.execute_query(citizen_queries['cert_details_query'], (category, name, session['citizen_id']))
    
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('citizen.profile'))
    
    return render_template(
        'citizen/view_certificate.html', 
        certificate=certificate[0]
    )

@citizen_bp.route('/certificate/<category>/<name>/file')
@role_required(['citizen','employee'])
def certificate_file(category, name):
    """Get the certificate file."""
    result = db.execute_query(citizen_queries['cert_file_query'], (category, name, session['citizen_id']))
    
    if not result or not result[0][0]:
        flash('Certificate file not found', 'error')
        return redirect(url_for('citizen.view_certificate', category=category, name=name))
    
    # Convert BYTEA data to bytes
    file_data = result[0][0]
    
    # Create a file-like object from the bytes
    file_stream = io.BytesIO(file_data)
    
    # Return the PDF file
    return send_file(
        file_stream,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f"{category}_{name}_certificate.pdf"
    )

@citizen_bp.route('/schemes')
@role_required(['citizen'])
def schemes():
    # Execute queries
    schemes_result = db.execute_query(citizen_queries['schemes_query'], (session['citizen_id'],))
    scheme_types_result = db.execute_query(citizen_queries['scheme_types_query'])
    type_count_result = db.execute_query(citizen_queries['type_count_query'])
    
    # Process the results
    schemes = []
    for row in schemes_result:
        schemes.append({
            'id': row[0],
            'name': row[1],
            'type': row[2] or 'Uncategorized',
            'description': row[3],
            'enrollments': row[4],
            'enrolled': row[5]
        })
    
    scheme_types = [row[0] for row in scheme_types_result]
    
    scheme_type_counts = {row[0]: row[1] for row in type_count_result}
    if 'Uncategorized' not in scheme_type_counts:
        uncategorized_count = db.execute_query(
            "SELECT COUNT(*) FROM Schemes WHERE Type IS NULL;"
        )[0][0]
        if uncategorized_count > 0:
            scheme_type_counts['Uncategorized'] = uncategorized_count
    
    return render_template(
        'citizen/schemes.html',
        schemes=schemes,
        scheme_types=scheme_types,
        scheme_type_counts=scheme_type_counts,
    )

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

@citizen_bp.route('/panchayat_employees')
@role_required(['citizen', 'monitor'])
def panchayat_employees():
    """View list of panchayat employees, their roles, and contact details."""
    # Get list of all employees with their details
    
    employees = db.execute_query(citizen_queries['employees_query'])
    
    # Group employees by role for better organization
    employees_by_role = {}
    for emp in employees:
        role = emp[2]
        if role not in employees_by_role:
            employees_by_role[role] = []
        employees_by_role[role].append({
            'name': emp[0],
            'phone': emp[1],
            'role': role,
        })
    
    return render_template(
        'citizen/panchayat_employees.html',
        employees=employees,
        employees_by_role=employees_by_role
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
        query = 'SELECT password, salt FROM users WHERE UserID = %s'
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
        return redirect(url_for('citizen.profile'))
    
    return render_template('citizen/update_password.html')