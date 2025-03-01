admin_queries = {
    # Database Management Queries
    "tables_query": """
        SELECT 
            table_name 
        FROM 
            information_schema.tables 
        WHERE 
            table_schema = 'public'
        ORDER BY 
            table_name
    """,
    "columns_query": """
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default
        FROM 
            information_schema.columns 
        WHERE 
            table_schema = 'public' 
            AND table_name = %s
        ORDER BY 
            ordinal_position
    """,
    # Users Management Queries
    "citizens_query": """
        SELECT c.Aadhaar, c.Name, c.Phone, COALESCE(u.UserID, 0) as UserID
        FROM Citizen c
        LEFT JOIN users u ON c.Aadhaar = u.CitizenID
        WHERE c.Aadhaar NOT IN (
            SELECT ec.CitizenID 
            FROM EmployeeCitizens ec
        )
        ORDER BY c.Name
    """,
    "employees_query": """
        SELECT c.Aadhaar, c.Name, ec.Role, COALESCE(u.UserID, 0) as UserID
        FROM EmployeeCitizens ec
        JOIN Citizen c ON ec.CitizenID = c.Aadhaar
        LEFT JOIN users u ON c.Aadhaar = u.CitizenID
        ORDER BY c.Name
    """,
    "monitors_query": """
        SELECT m.MonitorID, m.Name, COALESCE(u.UserID, 0) as UserID
        FROM Monitors m
        LEFT JOIN users u ON m.MonitorID = u.MonitorID
        ORDER BY m.Name
    """,
    "citizen_insert_query": """
        INSERT INTO users (CitizenID, MonitorID, username, password, auth, salt)
        VALUES (%s, NULL, %s, %s, %s, %s)
    """,
    "employee_insert_query": """
        INSERT INTO users (CitizenID, MonitorID, username, password, auth, salt)
        VALUES (%s, NULL, %s, %s, %s, %s)
    """,
    "monitor_insert_query": """
        INSERT INTO users (CitizenID, MonitorID, username, password, auth, salt)
        VALUES (NULL, %s, %s, %s, %s, %s)
    """,
}
