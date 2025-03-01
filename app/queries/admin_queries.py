admin_queries={
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
}