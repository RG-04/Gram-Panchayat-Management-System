citizen_queries = {
    # Profile queries
    "profile_details_query": """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Income, 
               c.Occupation, c.Phone, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        WHERE c.Aadhaar = %s
    """,
    "user_query": """
        SELECT username, auth
        FROM users
        WHERE CitizenID = %s
    """,
    "cert_query": """
        SELECT Category, Name, DateIssued
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY Category, DateIssued DESC
    """,
    "cert_details_query": """
        SELECT Category, Name, CitizenID, DateIssued, File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """,
    "cert_file_query": """
        SELECT File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """,
    # Statistics queries
    # Education queries
    "school_query": """
        SELECT schoolid, s.name,
        SUM(CASE WHEN a.PassDate IS NULL THEN 1 ELSE 0 END) AS current_students,
        COUNT(*) AS total_students
        FROM schools s NATURAL JOIN attendsschool a
        JOIN citizen c ON a.citizenid = c.aadhaar
        GROUP BY schoolid
        ORDER BY schoolid;
        """,
    "literacy_query": """
        SELECT ROUND((COUNT(DISTINCT a.CitizenID) * 100.0) / COUNT(DISTINCT c.Aadhaar), 2) AS LiteracyRate
        FROM Citizen c
        LEFT JOIN AttendsSchool a
        ON c.Aadhaar = a.CitizenID;
        """,
    "gender_literacy_query": """
        SELECT ROUND((COUNT(DISTINCT a.CitizenID) * 100.0) / COUNT(DISTINCT c.Aadhaar), 2) AS LiteracyRate
        FROM Citizen c
        LEFT JOIN AttendsSchool a
        ON c.Aadhaar = a.CitizenID
        GROUP BY c.Gender;
        """,
    # Health queries
    "hospital_query": """
        SELECT * FROM Hospitals
        ORDER BY HospitalID;
        """,
    "vaccination_query": """
        WITH TotalCitizens AS ( SELECT COUNT(DISTINCT Aadhaar) AS Total FROM Citizen )
        SELECT 
            cert.Name AS Disease,
            COUNT(DISTINCT cert.CitizenID) AS VaccinatedCitizens,
            (SELECT Total FROM TotalCitizens) AS TotalCitizens,
            ROUND((COUNT(DISTINCT cert.CitizenID) * 100.0) / (SELECT Total FROM TotalCitizens), 2) AS VaccinationRate
        FROM Certificates cert
        WHERE cert.Category = 'Vaccination' AND cert.Name IS NOT NULL
        GROUP BY cert.Name
        ORDER BY VaccinationRate DESC;
        """,
    # Agriculture queries
    "total_land_query": """
        SELECT SUM(Size) FROM Land;
        """,
    "agricultural_area_query": """
        SELECT SUM(Area) FROM LandCrop;
        """,
    "agricultural_percentage_query": """
        SELECT ROUND(((SELECT SUM(Area) FROM LandCrop)/(SELECT SUM(Size) FROM Land))*100, 2) AS AgriPercentage; 
        """,
    "organic_percentage_query": """
        SELECT ROUND(((SELECT SUM(Area) FROM LandCrop WHERE isOrganic = TRUE)/(SELECT SUM(Area) FROM LandCrop))*100, 2) AS OrganicPercentage;
        """,
    "crop_types_query": """
        SELECT DISTINCT Type FROM Crop WHERE Type IS NOT NULL;
        """,
    "crops_detail_query": """
        SELECT c.CropID, c.Name, c.Type, SUM(lc.Area) AS TotalArea, 
               SUM(lc.AnnualYield) AS TotalYield,
               ROUND(SUM(lc.AnnualYield)/SUM(lc.Area), 2) AS YieldPerHectare,
               CASE WHEN COUNT(lc.isOrganic) = SUM(CASE WHEN lc.isOrganic THEN 1 ELSE 0 END) THEN TRUE ELSE FALSE END AS IsOrganic
        FROM Crop c
        JOIN LandCrop lc ON c.CropID = lc.CropID
        GROUP BY c.CropID, c.Name, c.Type
        ORDER BY TotalArea DESC;
        """,
    "top_crops_query": """
        SELECT c.Name, SUM(lc.Area) AS TotalArea
        FROM Crop c
        JOIN LandCrop lc ON c.CropID = lc.CropID
        GROUP BY c.CropID, c.Name
        ORDER BY TotalArea DESC
        LIMIT 3;
        """,
    # Demographics queries
    "population_query": """
        SELECT COUNT(*) AS TotalPopulation FROM Citizen;
        """,
    "gender_distribution_query": """
        SELECT Gender, COUNT(*) AS Count
        FROM Citizen
        WHERE Gender IS NOT NULL
        GROUP BY Gender
        ORDER BY Gender;
        """,
    "sex_ratio_query": """
        SELECT 
            ROUND((COUNT(CASE WHEN Gender = 'Female' THEN 1 END) * 1000.0) / 
            NULLIF(COUNT(CASE WHEN Gender = 'Male' THEN 1 END), 0), 2) AS SexRatio
        FROM Citizen
        WHERE Gender IN ('Male', 'Female');
        """,
    "age_distribution_query": """
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
        """,
    "birth_rate_query": """
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
        """,
    "death_rate_query": """
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
        """,
    "household_query": """
        SELECT 
            COUNT(DISTINCT HouseholdSizes.HouseholdID) AS TotalHouseholds,
            ROUND(COUNT(DISTINCT Citizen.Aadhaar) * 1.0 / COUNT(DISTINCT HouseholdSizes.HouseholdID), 2) AS AvgHouseholdSize,
            MAX(HouseholdCount) AS LargestHouseholdSize
        FROM (
            SELECT HouseholdID, COUNT(*) AS HouseholdCount
            FROM Citizen
            WHERE HouseholdID IS NOT NULL
            GROUP BY HouseholdID
        ) AS HouseholdSizes, Citizen
        WHERE Citizen.HouseholdID IS NOT NULL;
        """,
    "occupation_query": """
        SELECT Occupation, COUNT(*) AS Count
        FROM Citizen
        WHERE Occupation IS NOT NULL
        GROUP BY Occupation
        ORDER BY Count DESC
        LIMIT 5;
        """,
    "income_distribution_query": """
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
        """,
    # Scheme queries
    "schemes_query": """
        SELECT s.SchemeID, s.Name, s.Type, s.Description, 
            COUNT(se.CitizenID) AS EnrollmentCount,
            (SELECT COUNT(*) FROM SchemeEnrollment WHERE CitizenID = %s AND SchemeID = s.SchemeID) AS Enrolled
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        GROUP BY s.SchemeID, s.Name, s.Type, s.Description
        ORDER BY s.Name;
    """,
    "scheme_types_query": """
        SELECT DISTINCT Type FROM Schemes WHERE Type IS NOT NULL ORDER BY Type;
    """,
    "type_count_query": """
        SELECT Type, COUNT(*) FROM Schemes 
        WHERE Type IS NOT NULL 
        GROUP BY Type 
        ORDER BY COUNT(*) DESC;
    """,
    # Panchayat queries
    "employees_query": """
        SELECT c.Name, c.Phone, ec.Role
        FROM EmployeeCitizens ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        ORDER BY ec.Role, c.Name
    """,
}
