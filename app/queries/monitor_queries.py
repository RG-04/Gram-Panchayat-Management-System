monitor_queries = {
    # 1. Get average school income
    'avg_school_income': """
        SELECT AVG(Income) 
        FROM Schools
    """,

    # 2. Get total school capacity
    'total_school_capacity': """
        SELECT SUM(Capacity) 
        FROM Schools
    """,

    # 3. Get total number of enrolled students
    'total_enrolled_students': """
        SELECT COUNT(DISTINCT CitizenID) 
        FROM AttendsSchool
    """,

    # 4. Get gender distribution of students
    'gender_distribution': """
        SELECT c.Gender, COUNT(DISTINCT a.CitizenID) 
        FROM AttendsSchool a
        JOIN Citizen c ON a.CitizenID = c.Aadhaar
        GROUP BY c.Gender
    """,

    # 5. Get school income distribution
    'income_distribution': """
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
    'school_utilization': """
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
}
