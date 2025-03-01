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
    valid_categories = ['education', 'health', 'agriculture', 'demographic']
    if category not in valid_categories:
        category = 'education'  # Default to education if invalid
    
    # Based on the category, fetch different statistics
    if category == 'education':
        school_query = """
        SELECT schoolid, s.name,
        SUM(CASE WHEN a.PassDate IS NULL THEN 1 ELSE 0 END) AS current_students,
        COUNT(*) AS total_students
        FROM schools s NATURAL JOIN attendsschool a
        JOIN citizen c ON a.citizenid = c.aadhaar
        GROUP BY schoolid
        ORDER BY schoolid;
        """

        literacy_query = """
        SELECT ROUND((COUNT(DISTINCT a.CitizenID) * 100.0) / COUNT(DISTINCT c.Aadhaar), 2) AS LiteracyRate
        FROM Citizen c
        LEFT JOIN AttendsSchool a
        ON c.Aadhaar = a.CitizenID;
        """

        gender_literacy_query = """
        SELECT ROUND((COUNT(DISTINCT a.CitizenID) * 100.0) / COUNT(DISTINCT c.Aadhaar), 2) AS LiteracyRate
        FROM Citizen c
        LEFT JOIN AttendsSchool a
        ON c.Aadhaar = a.CitizenID
        GROUP BY c.Gender;
        """

        schools = db.execute_query(school_query)
        literacy_rate = db.execute_query(literacy_query)[0][0]
        male_literacy_rate, female_literacy_rate = db.execute_query(gender_literacy_query)
        male_literacy_rate, female_literacy_rate = male_literacy_rate[0],female_literacy_rate[0]
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
        # Example health statistics
        hospital_query = """
        SELECT * FROM Hospitals
        ORDER BY HospitalID;
        """
        vaccination_query="""
        WITH TotalCitizens AS ( SELECT COUNT(DISTINCT Aadhaar) AS Total FROM Citizen )
        SELECT 
            cert.Name AS Disease,
            COUNT(DISTINCT cert.CitizenID) AS VaccinatedCitizens,
            (SELECT Total FROM TotalCitizens) AS TotalCitizens,
            ROUND((COUNT(DISTINCT cert.CitizenID) * 100.0) / (SELECT Total FROM TotalCitizens), 2) AS VaccinationRate
        FROM Certificates cert
        WHERE cert.Category = 'Vaccination'AND cert.Name IS NOT NULL
        GROUP BY cert.Name
        ORDER BY VaccinationRate DESC;
        """
        hospitals = db.execute_query(hospital_query)
        vaccination_stats = db.execute_query(vaccination_query)
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

        total_land_query = """
        SELECT SUM(Size) FROM Land;
        """
        
        agricultural_area_query = """
        SELECT SUM(Area) FROM LandCrop;
        """
        
        agricultural_percentage_query = """
        SELECT ROUND(((SELECT SUM(Area) FROM LandCrop)/(SELECT SUM(Size) FROM Land))*100, 2) AS AgriPercentage; 
        """
        
        organic_percentage_query = """
        SELECT ROUND(((SELECT SUM(Area) FROM LandCrop WHERE isOrganic = TRUE)/(SELECT SUM(Area) FROM LandCrop))*100, 2) AS OrganicPercentage;
        """
        
        crop_types_query = """
        SELECT DISTINCT Type FROM Crop WHERE Type IS NOT NULL;
        """
        
        crops_detail_query = """
        SELECT c.CropID, c.Name, c.Type, SUM(lc.Area) AS TotalArea, 
               SUM(lc.AnnualYield) AS TotalYield,
               ROUND(SUM(lc.AnnualYield)/SUM(lc.Area), 2) AS YieldPerHectare,
               CASE WHEN COUNT(lc.isOrganic) = SUM(CASE WHEN lc.isOrganic THEN 1 ELSE 0 END) THEN TRUE ELSE FALSE END AS IsOrganic
        FROM Crop c
        JOIN LandCrop lc ON c.CropID = lc.CropID
        GROUP BY c.CropID, c.Name, c.Type
        ORDER BY TotalArea DESC;
        """
        
        top_crops_query = """
        SELECT c.Name, SUM(lc.Area) AS TotalArea
        FROM Crop c
        JOIN LandCrop lc ON c.CropID = lc.CropID
        GROUP BY c.CropID, c.Name
        ORDER BY TotalArea DESC
        LIMIT 3;
        """
        
        # Execute queries
        total_land = db.execute_query(total_land_query)[0][0] or 0
        agricultural_area = db.execute_query(agricultural_area_query)[0][0] or 0
        agricultural_percentage = db.execute_query(agricultural_percentage_query)[0][0] or 0
        organic_percentage = db.execute_query(organic_percentage_query)[0][0] or 0
        crop_types = [row[0] for row in db.execute_query(crop_types_query)]
        
        # Get crops details
        crops_result = db.execute_query(crops_detail_query)
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
        top_crops = db.execute_query(top_crops_query)
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
        # Total population query
        population_query = """
        SELECT COUNT(*) AS TotalPopulation FROM Citizen;
        """
        
        # Gender distribution query
        gender_distribution_query = """
        SELECT Gender, COUNT(*) AS Count
        FROM Citizen
        WHERE Gender IS NOT NULL
        GROUP BY Gender
        ORDER BY Gender;
        """
        
        # Sex ratio query (females per 1000 males)
        sex_ratio_query = """
        SELECT 
            ROUND((COUNT(CASE WHEN Gender = 'Female' THEN 1 END) * 1000.0) / 
            NULLIF(COUNT(CASE WHEN Gender = 'Male' THEN 1 END), 0), 2) AS SexRatio
        FROM Citizen
        WHERE Gender IN ('Male', 'Female');
        """
        
        # Age group distribution for population pyramid
        age_distribution_query = """
        WITH AgeGroups AS (
            SELECT 
                Gender,
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 5 THEN '0-4'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 10 THEN '5-9'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 15 THEN '10-14'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 20 THEN '15-19'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 25 THEN '20-24'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 30 THEN '25-29'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 35 THEN '30-34'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 40 THEN '35-39'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 45 THEN '40-44'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 50 THEN '45-49'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 55 THEN '50-54'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 60 THEN '55-59'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 65 THEN '60-64'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 70 THEN '65-69'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 75 THEN '70-74'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 80 THEN '75-79'
                    ELSE '80+' 
                END AS AgeGroup,
                COUNT(*) AS Count
            FROM Citizen
            WHERE DOB IS NOT NULL AND Gender IN ('Male', 'Female')
            GROUP BY Gender, AgeGroup
        )
        SELECT AgeGroup, 
            SUM(CASE WHEN Gender = 'Male' THEN Count ELSE 0 END) AS MaleCount,
            SUM(CASE WHEN Gender = 'Female' THEN Count ELSE 0 END) AS FemaleCount
        FROM AgeGroups
        GROUP BY AgeGroup
        ORDER BY 
            CASE 
                WHEN AgeGroup = '0-4' THEN 1
                WHEN AgeGroup = '5-9' THEN 2
                WHEN AgeGroup = '10-14' THEN 3
                WHEN AgeGroup = '15-19' THEN 4
                WHEN AgeGroup = '20-24' THEN 5
                WHEN AgeGroup = '25-29' THEN 6
                WHEN AgeGroup = '30-34' THEN 7
                WHEN AgeGroup = '35-39' THEN 8
                WHEN AgeGroup = '40-44' THEN 9
                WHEN AgeGroup = '45-49' THEN 10
                WHEN AgeGroup = '50-54' THEN 11
                WHEN AgeGroup = '55-59' THEN 12
                WHEN AgeGroup = '60-64' THEN 13
                WHEN AgeGroup = '65-69' THEN 14
                WHEN AgeGroup = '70-74' THEN 15
                WHEN AgeGroup = '75-79' THEN 16
                WHEN AgeGroup = '80+' THEN 17
            END;
        """
        
        # Literacy rate query (we reuse the one from education section)
        literacy_query = """
        SELECT ROUND((COUNT(DISTINCT a.CitizenID) * 100.0) / COUNT(DISTINCT c.Aadhaar), 2) AS LiteracyRate
        FROM Citizen c
        LEFT JOIN AttendsSchool a
        ON c.Aadhaar = a.CitizenID;
        """
        
        # Birth rate (births in last year per 1000 population)
        birth_rate_query = """
        WITH Births AS (
            SELECT COUNT(*) AS BirthCount 
            FROM Citizen 
            WHERE EXTRACT(YEAR FROM AGE(CURRENT_DATE, DOB)) < 1
        ),
        TotalPop AS (
            SELECT COUNT(*) AS Total FROM Citizen
        )
        SELECT ROUND((BirthCount * 1000.0) / NULLIF(Total, 0), 2) AS BirthRate
        FROM Births, TotalPop;
        """
        
        # Death certificates in the last year (approximate death rate)
        death_rate_query = """
        WITH Deaths AS (
            SELECT COUNT(*) AS DeathCount 
            FROM Certificates 
            WHERE Category = 'Death Certificate' 
            AND DateIssued >= CURRENT_DATE - INTERVAL '1 year'
        ),
        TotalPop AS (
            SELECT COUNT(*) AS Total FROM Citizen
        )
        SELECT ROUND((DeathCount * 1000.0) / NULLIF(Total, 0), 2) AS DeathRate
        FROM Deaths, TotalPop;
        """
        
        # Household statistics
        household_query = """
        SELECT 
            COUNT(DISTINCT HouseholdSizes.HouseholdID) AS TotalHouseholds,
            ROUND(COUNT(Citizen.Aadhaar) * 1.0 / COUNT(DISTINCT HouseholdSizes.HouseholdID), 2) AS AvgHouseholdSize,
            MAX(HouseholdCount) AS LargestHouseholdSize
        FROM (
            SELECT HouseholdID, COUNT(*) AS HouseholdCount
            FROM Citizen
            WHERE HouseholdID IS NOT NULL
            GROUP BY HouseholdID
        ) AS HouseholdSizes, Citizen
        WHERE Citizen.HouseholdID IS NOT NULL;
        """
        
        # Occupation distribution (top 5)
        occupation_query = """
        SELECT Occupation, COUNT(*) AS Count
        FROM Citizen
        WHERE Occupation IS NOT NULL
        GROUP BY Occupation
        ORDER BY Count DESC
        LIMIT 5;
        """
        
        # Income distribution
        income_distribution_query = """
        SELECT * 
        FROM (
            SELECT 
                CASE 
                    WHEN Income < 50000 THEN 'Below 50K'
                    WHEN Income < 100000 THEN '50K-1L'
                    WHEN Income < 300000 THEN '1L-3L'
                    WHEN Income < 500000 THEN '3L-5L'
                    WHEN Income < 1000000 THEN '5L-10L'
                    ELSE 'Above 10L'
                END AS IncomeGroup,
                COUNT(*) AS Count
            FROM Citizen
            WHERE Income IS NOT NULL
            GROUP BY IncomeGroup
        ) AS income_data
        ORDER BY 
            CASE 
                WHEN IncomeGroup = 'Below 50K' THEN 1
                WHEN IncomeGroup = '50K-1L' THEN 2
                WHEN IncomeGroup = '1L-3L' THEN 3
                WHEN IncomeGroup = '3L-5L' THEN 4
                WHEN IncomeGroup = '5L-10L' THEN 5
                WHEN IncomeGroup = 'Above 10L' THEN 6
            END;
        """
        
        # Execute queries
        total_population = db.execute_query(population_query)[0][0]
        gender_distribution = db.execute_query(gender_distribution_query)
        sex_ratio = db.execute_query(sex_ratio_query)[0][0] or 0
        age_distribution = db.execute_query(age_distribution_query)
        literacy_rate = db.execute_query(literacy_query)[0][0] or 0
        birth_rate = db.execute_query(birth_rate_query)[0][0] or 0
        death_rate = db.execute_query(death_rate_query)[0][0] or 0
        household_stats = db.execute_query(household_query)
        occupation_stats = db.execute_query(occupation_query)
        income_distribution = db.execute_query(income_distribution_query)
        
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
        FROM users
        WHERE CitizenID = %s
    """
    user = db.execute_query(user_query, (session['citizen_id'],))
    
    # Get certificates
    cert_query = """
        SELECT Category, Name, DateIssued
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY Category, DateIssued DESC
    """
    certificates = db.execute_query(cert_query, (session['citizen_id'],))
    
    # Group certificates by category
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
@role_required(['citizen'])
def view_certificate(category, name):
    """View a specific certificate."""
    cert_query = """
        SELECT Category, Name, CitizenID, DateIssued, File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """
    certificate = db.execute_query(cert_query, (category, name, session['citizen_id']))
    
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('citizen.profile'))
    
    return render_template(
        'citizen/view_certificate.html', 
        certificate=certificate[0]
    )

@citizen_bp.route('/certificate/<category>/<name>/file')
@role_required(['citizen'])
def certificate_file(category, name):
    """Get the certificate file."""
    from flask import send_file, Response
    import io
    
    cert_query = """
        SELECT File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """
    result = db.execute_query(cert_query, (category, name, session['citizen_id']))
    
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

    citizen_id = session['citizen_id']

    # SQL query to get all schemes with enrollment count
    schemes_query = """
    SELECT s.SchemeID, s.Name, s.Type, s.Description, 
           COUNT(se.CitizenID) AS EnrollmentCount,
           (SELECT COUNT(*) FROM SchemeEnrollment WHERE CitizenID = %s AND SchemeID = s.SchemeID) AS Enrolled
    FROM Schemes s
    LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
    GROUP BY s.SchemeID, s.Name, s.Type, s.Description
    ORDER BY s.Name;
    """
    
    # SQL query to get unique scheme types
    scheme_types_query = """
    SELECT DISTINCT Type FROM Schemes WHERE Type IS NOT NULL ORDER BY Type;
    """
    
    # SQL query to count schemes by type
    type_count_query = """
    SELECT Type, COUNT(*) FROM Schemes 
    WHERE Type IS NOT NULL 
    GROUP BY Type 
    ORDER BY COUNT(*) DESC;
    """
    
    # Execute queries
    schemes_result = db.execute_query(schemes_query, (citizen_id,))
    scheme_types_result = db.execute_query(scheme_types_query)
    type_count_result = db.execute_query(type_count_query)
    
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