monitor_queries = {
    # 1. Get average school income
    "avg_school_income": """
        SELECT AVG(Income) 
        FROM Schools
    """,
    # 2. Get total school capacity
    "total_school_capacity": """
        SELECT SUM(Capacity) 
        FROM Schools
    """,
    # 3. Get total number of enrolled students
    "total_enrolled_students": """
        SELECT COUNT(DISTINCT CitizenID) 
        FROM AttendsSchool
    """,
    # 4. Get gender distribution of students
    "gender_distribution": """
        SELECT c.Gender, COUNT(DISTINCT a.CitizenID) 
        FROM AttendsSchool a
        JOIN Citizen c ON a.CitizenID = c.Aadhaar
        GROUP BY c.Gender
    """,
    # 5. Get school income distribution
    "income_distribution": """
        WITH IncomeGroups AS (
            SELECT 
                CASE 
                    WHEN Income < 100000 THEN 'Under ₹1 Lakh'
                    WHEN Income >= 100000 AND Income < 200000 THEN '₹1-2 Lakh'
                    WHEN Income >= 200000 AND Income < 500000 THEN '₹2-5 Lakh'
                    WHEN Income >= 500000 AND Income < 1000000 THEN '₹5-10 Lakh'
                    ELSE 'Above ₹10 Lakh'
                END AS income_range
            FROM Schools
        )
        SELECT income_range, COUNT(*) 
        FROM IncomeGroups
        GROUP BY income_range
        ORDER BY 
            CASE 
                WHEN income_range = 'Under ₹1 Lakh' THEN 1
                WHEN income_range = '₹1-2 Lakh' THEN 2
                WHEN income_range = '₹2-5 Lakh' THEN 3
                WHEN income_range = '₹5-10 Lakh' THEN 4
                ELSE 5
            END
    """,
    # 6. Get school capacity utilization details
    "school_utilization": """
        WITH StudentCounts AS (
            SELECT 
                a.SchoolID,
                COUNT(DISTINCT a.CitizenID) as student_count
            FROM AttendsSchool a
            GROUP BY a.SchoolID
        )
        SELECT 
            s.SchoolID,
            s.Name,
            s.Capacity,
            COALESCE(sc.student_count, 0) 
        FROM Schools s
        LEFT JOIN StudentCounts sc ON s.SchoolID = sc.SchoolID
        ORDER BY s.Name
    """,
    # 7. Get total doctors
    "total_doctors": """
        SELECT COUNT(*) 
        FROM Citizen
        WHERE Occupation = 'Doctor'
    """,
    # 8. Get total nurses
    "total_nurses": """
        SELECT COUNT(*) 
        FROM Citizen
        WHERE Occupation = 'Nurse'
    """,
    # 9. Get personnel distribution for chart
    "personnel_distribution": """
        SELECT 
            CASE 
                WHEN Occupation = 'Doctor' THEN 'Doctors'
                WHEN Occupation = 'Nurse' THEN 'Nurses'
                WHEN Occupation = 'Paramedic' THEN 'Paramedics'
                WHEN Occupation LIKE '%Health%' OR Occupation LIKE '%Medical%' THEN 'Other Healthcare Staff'
                ELSE NULL
            END AS personnel_type,
            COUNT(*) AS count
        FROM Citizen
        WHERE 
            Occupation = 'Doctor' 
            OR Occupation = 'Nurse'
            OR Occupation = 'Paramedic'
            OR Occupation LIKE '%Health%' 
            OR Occupation LIKE '%Medical%'
        GROUP BY personnel_type
        HAVING personnel_type IS NOT NULL
        ORDER BY count DESC
    """,
    # 10. Get health welfare schemes
    "health_schemes": """
        SELECT 
            s.SchemeID,
            s.Name,
            s.Description,
            COUNT(se.CitizenID) AS enrolled_citizens
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        WHERE s.Type = 'Health' OR s.Type = 'Healthcare'
        GROUP BY s.SchemeID, s.Name, s.Description
        ORDER BY enrolled_citizens DESC
    """,
    # 11. Get citizen count for health scheme by month
    "scheme_enrollment_by_month": """
        SELECT 
            TO_CHAR(Date, 'Mon YYYY') AS month,
            COUNT(*) AS enrollments
        FROM SchemeEnrollment
        WHERE 
            SchemeID = %s AND
            Date >= %s AND
            Date <= %s
        GROUP BY month
        ORDER BY MIN(Date)
    """,
}
