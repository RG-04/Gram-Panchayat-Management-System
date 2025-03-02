employee_queries = {
    # Dashboard Queries
    "employee_query": """
        SELECT ec.EmployeeID, c.Aadhaar, c.Name, c.Phone, 
               ec.StartDate, ec.TermDuration, ec.Role
        FROM EmployeeCitizens ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        WHERE ec.CitizenID = %s
    """,
    "citizen_count_query": """
        SELECT COUNT(*) FROM Citizen
    """,
    "cert_count_query": """
        SELECT COUNT(*) FROM Certificates
    """,
    "scheme_count_query": """
        SELECT COUNT(*) FROM SchemeEnrollment
    """,
    # Citizens Queries
    "citizens_query": """
        SELECT c.Aadhaar, c.Name, c.Gender, c.DOB, c.Phone, c.Income,
               c.Occupation, h.Address
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        ORDER BY c.Name
    """,
    "citizen_one_query": """
        SELECT c.Aadhaar, c.Name, c.DOB, c.Gender, c.Income, c.Occupation, 
               c.Phone, h.Address, h.HouseholdID, c.MotherID, c.FatherID
        FROM Citizen c
        LEFT JOIN Households h ON c.HouseholdID = h.HouseholdID
        WHERE c.Aadhaar = %s
    """,
    "citizen_parent_query": """
        SELECT c.Aadhaar, c.Name
        FROM Citizen c
        WHERE c.Aadhaar = %s
    """,
    "citizen_children_query": """
        SELECT c.Aadhaar, c.Name
        FROM Citizen c
        WHERE c.MotherID = %s OR c.FatherID = %s
    """,
    "citizen_family_income_query": """
        SELECT Income as FamilyIncome
        FROM Households
        WHERE HouseholdID = %s
    """,
    "citizen_cert_query": """
        SELECT Category, Name, DateIssued, 
               CASE WHEN File IS NOT NULL THEN true ELSE false END as has_file
        FROM Certificates
        WHERE CitizenID = %s
        ORDER BY Category, DateIssued DESC
    """,
    "update_citizen_query": """
        UPDATE Citizen
        SET Name = %s, DOB = %s, Gender = %s, Income = %s, 
            Occupation = %s, Phone = %s
        WHERE Aadhaar = %s
    """,
    "update_household_query": """
        UPDATE Households
        SET Address = %s
        WHERE HouseholdID = (SELECT HouseholdID FROM Citizen WHERE Aadhaar = %s)
    """,
    # Citizen Certificate Queries
    "specific_cert_query": """
        SELECT Category, Name, CitizenID, DateIssued, File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """,
    "cert_file_query": """
        SELECT File
        FROM Certificates
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """,
    "update_cert_query": """
        UPDATE Certificates
        SET File = %s
        WHERE Category = %s AND Name = %s AND CitizenID = %s
    """,
    # Schemes
    "schemes_query": """
        SELECT s.SchemeID, s.Name, s.Type, s.Description, 
            COUNT(se.CitizenID) AS EnrollmentCount
        FROM Schemes s
        LEFT JOIN SchemeEnrollment se ON s.SchemeID = se.SchemeID
        GROUP BY s.SchemeID, s.Name, s.Type, s.Description
        ORDER BY s.Name;
    """,
    "scheme_insert_query": """
        INSERT INTO Schemes (Name, Type, Description, AllocatedBudget, TargetBeneficiaries)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING SchemeID;
    """,
    "scheme_update_query": """
        UPDATE Schemes
        SET Name = %s, Type = %s, Description = %s
        WHERE SchemeID = %s;
    """,
    "scheme_delete_query": """
        DELETE FROM Schemes WHERE SchemeID = %s;
    """,
    # Assets & Surveys Queries
    "assets_query": """
        SELECT a.asset_id, a.Name, a.Type, a.InstallationDate, 
               a.LastSurveyedDate, a.Location,
               (CURRENT_DATE - COALESCE(a.LastSurveyedDate, a.InstallationDate)) as days_since_last_survey
        FROM assets a
        ORDER BY days_since_last_survey DESC
    """,
    "asset_details_query": """
        SELECT asset_id, Name, Type, InstallationDate, LastSurveyedDate, Location
        FROM assets
        WHERE asset_id = %s
    """,
    "surveys_query": """
        SELECT asu.SurveyDate, asu.SurveyData, 
               c.Name as SurveyorName
        FROM AssetSurveys asu
        JOIN EmployeeCitizens ec ON asu.SurveyorID = ec.EmployeeID
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        WHERE asu.asset_id = %s
        ORDER BY asu.SurveyDate DESC
    """,
    "survey_insert_query": """
        INSERT INTO AssetSurveys (asset_id, SurveyDate, SurveyorID, SurveyData)
        VALUES (%s, CURRENT_DATE, %s, %s)
        ON CONFLICT (asset_id, SurveyDate) 
        DO UPDATE SET SurveyorID = %s, SurveyData = %s
    """,
    "asset_insert_query": """
        INSERT INTO assets (Name, Type, InstallationDate, Location)
        VALUES (%s, %s, %s, %s)
        RETURNING asset_id
    """,
}
