auth_queries = {
    "user_query": """
        SELECT u.UserID, u.username, u.password, u.salt, u.auth, u.CitizenID, u.MonitorID, 
               CASE WHEN u.CitizenID IS NOT NULL THEN c.Name 
                    WHEN u.MonitorID IS NOT NULL THEN m.Name
                    ELSE NULL
               END as Name
        FROM users u
        LEFT JOIN Citizen c ON u.CitizenID = c.Aadhaar
        LEFT JOIN Monitors m ON u.MonitorID = m.MonitorID
        WHERE u.username = %s
    """,
    "employee_query": """
        SELECT EmployeeID FROM EmployeeCitizens 
        WHERE CitizenID = %s
    """,
    "curr_user_query": """
        SELECT u.UserID, u.username, u.auth, u.CitizenID, u.MonitorID, 
               CASE WHEN u.CitizenID IS NOT NULL THEN c.Name 
                    WHEN u.MonitorID IS NOT NULL THEN m.Name
                    ELSE NULL
               END as Name
        FROM users u
        LEFT JOIN Citizen c ON u.CitizenID = c.Aadhaar
        LEFT JOIN Monitors m ON u.MonitorID = m.MonitorID
        WHERE u.UserID = %s
    """,
}
