monitor_queries = {
    # Education Advanced Statistics Queries
    "avg_school_income": """
        SELECT AVG(Income) 
        FROM Schools
    """,
    "total_school_capacity": """
        SELECT SUM(Capacity) 
        FROM Schools
    """,
    "total_enrolled_students": """
        SELECT COUNT(DISTINCT CitizenID) 
        FROM AttendsSchool
    """,
    "gender_distribution": """
        SELECT c.Gender, COUNT(DISTINCT a.CitizenID) 
        FROM AttendsSchool a
        JOIN Citizen c ON a.CitizenID = c.Aadhaar
        GROUP BY c.Gender
    """,
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
    "school_finances": """
        SELECT 
            Name,
            AnnualIncome,
            AnnualExpenditure,
            BudgetYear
        FROM Schools natural join SchoolAccount
        ORDER BY Name
    """,
    # Health advanced statistics queries
    "hospital_finances": """
        SELECT 
            Name,
            AnnualIncome,
            AnnualExpenditure,
            BudgetYear
        FROM Hospitals natural join HospitalAccount
        ORDER BY Name
    """,
    "total_doctors": """
        SELECT COUNT(*) 
        FROM Citizen
        WHERE Occupation = 'Doctor'
    """,
    "total_nurses": """
        SELECT COUNT(*) 
        FROM Citizen
        WHERE Occupation = 'Nurse'
    """,
    "health_schemes": """
        SELECT 
            s.SchemeID,
            s.Name,
            s.Description,
            COUNT(se.CitizenID) AS enrolled_citizens,
            s.AllocatedBudget
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        WHERE s.Type = 'Health' OR s.Type = 'Healthcare'
        GROUP BY s.SchemeID, s.Name, s.Description
        ORDER BY enrolled_citizens DESC
    """,
    # Agriculture advanced statistics queries
    "irrigation_methods": """
        SELECT 
            IrrigationMethod,
            COUNT(*) as usage_count
        FROM LandCrop
        GROUP BY IrrigationMethod
        ORDER BY usage_count DESC
    """,
    "water_usage_by_crop": """
        SELECT 
            c.Name as crop_name,
            SUM(lc.Area) as total_area,
            SUM(lc.WaterUsage * lc.Area) as total_water_usage
        FROM LandCrop lc
        JOIN Crop c ON lc.CropID = c.CropID
        GROUP BY c.Name
        ORDER BY total_water_usage DESC
    """,
    # Demographic advanced statistics queries
    "migration_status": """
        SELECT 
            MigrationStatus,
            COUNT(*) as citizen_count
        FROM Citizen
        WHERE MigrationStatus IS NOT NULL
        GROUP BY MigrationStatus
        ORDER BY citizen_count DESC
    """,
    "residence_duration": """
        SELECT 
            CASE
                WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ResidenceSince) < 1 THEN 'Less than 1 year'
                WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ResidenceSince) BETWEEN 1 AND 5 THEN '1-5 years'
                WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ResidenceSince) BETWEEN 6 AND 10 THEN '6-10 years'
                WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM ResidenceSince) BETWEEN 11 AND 20 THEN '11-20 years'
                ELSE 'More than 20 years'
            END as residence_duration,
            COUNT(*) as citizen_count
        FROM Citizen
        WHERE ResidenceSince IS NOT NULL
        GROUP BY residence_duration
        ORDER BY 
            CASE residence_duration
                WHEN 'Less than 1 year' THEN 1
                WHEN '1-5 years' THEN 2
                WHEN '6-10 years' THEN 3
                WHEN '11-20 years' THEN 4
                ELSE 5
            END
    """,
    # Scheme advanced statistics queries
    "scheme_budget_allocation": """
        SELECT 
            Name as scheme_name,
            AllocatedBudget,
            TargetBeneficiaries,
            COALESCE(se.NumBeneficieries, 0) as total_enrollments,
            COALESCE(se.ReceivedBenefits, 0) as total_benefits
        FROM Schemes as s
        LEFT JOIN (SELECT SchemeID, COUNT(*) as NumBeneficieries, SUM(COALESCE(BenefitsReceived, 0)) as ReceivedBenefits FROM SchemeEnrollment GROUP BY SchemeID) as se ON s.SchemeID = se.SchemeID
        ORDER BY AllocatedBudget DESC
    """,
    "scheme_enrollment_stats": """
        SELECT 
            s.Name as scheme_name,
            COUNT(CASE WHEN se.EnrollmentStatus = 'Active' THEN 1 ELSE 0 END) as active_enrollments,
            COUNT(CASE WHEN se.EnrollmentStatus = 'Inactive' THEN 1 ELSE 0 END) as inactive_enrollments,
            COUNT(CASE WHEN se.EnrollmentStatus = 'Pending' THEN 1 ELSE 0 END) as pending_enrollments,
            COALESCE(SUM(se.BenefitsReceived), 0) as total_benefits
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        GROUP BY s.Name
        ORDER BY s.Name
    """,
    "scheme_beneficiary_demographics": """
        SELECT 
            s.Name as scheme_name,
            c.Gender,
            COUNT(se.CitizenID) as count,
            AVG(c.Income) as avg_income
        FROM SchemeEnrollment se
        JOIN Schemes s ON se.SchemeID = s.SchemeID
        JOIN Citizen c ON se.CitizenID = c.Aadhaar
        WHERE se.EnrollmentStatus = 'Active'
        GROUP BY s.Name, c.Gender
        ORDER BY s.Name, c.Gender
    """,
    # Environmental data queries
    "environmental_summary_2025": """
        SELECT 
            ROUND(AVG(AirQuality), 2) as avg_air_quality,
            ROUND(AVG(RainfallAmount), 2) as avg_rainfall,
            ROUND(AVG(GroundwaterLevel), 2) as avg_groundwater,
            ROUND(AVG(ForestCover), 2) as avg_forest_cover
        FROM EnvironmentalData
        WHERE EXTRACT(YEAR FROM TimeFrame) = 2025
    """,
    "aqi_monthly_trends": """
        SELECT 
            EXTRACT(YEAR FROM TimeFrame) as year,
            EXTRACT(MONTH FROM TimeFrame) as month,
            TO_CHAR(TimeFrame, 'Month') as month_name,
            ROUND(AVG(AirQuality), 2) as avg_aqi
        FROM EnvironmentalData
        GROUP BY EXTRACT(YEAR FROM TimeFrame), EXTRACT(MONTH FROM TimeFrame), TO_CHAR(TimeFrame, 'Month')
        ORDER BY year, month
    """,
    "rainfall_monthly_trends": """
        SELECT 
            EXTRACT(YEAR FROM TimeFrame) as year,
            EXTRACT(MONTH FROM TimeFrame) as month,
            TO_CHAR(TimeFrame, 'Month') as month_name,
            ROUND(AVG(RainfallAmount), 2) as avg_rainfall
        FROM EnvironmentalData
        GROUP BY EXTRACT(YEAR FROM TimeFrame), EXTRACT(MONTH FROM TimeFrame), TO_CHAR(TimeFrame, 'Month')
        ORDER BY year, month
    """,
}
