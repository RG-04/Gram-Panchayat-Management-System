import os
import psycopg2

# Global connection variable
connection = None
db_config = None


def init_db(app):
    """Initialize the database configuration."""
    global db_config

    # Store the database configuration
    db_config = {
        "host": app.config["DB_HOST"],
        "database": app.config["DB_NAME"],
        "user": app.config["DB_USER"],
        "password": app.config["DB_PASSWORD"],
        "port": app.config["DB_PORT"],
    }

    print("Database configuration initialized successfully")


def get_connection():
    """Get the database connection, creating it if necessary."""
    global connection

    try:
        # Check if connection is closed or None
        if connection is None or connection.closed:
            connection = psycopg2.connect(**db_config)
            print("New database connection established")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise e

    return connection


def execute_query(query, params=None, fetch=True):
    """Execute a query and optionally fetch results."""
    conn = get_connection()
    cursor = None
    results = None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        if fetch:
            results = cursor.fetchall()

        conn.commit()
        return results
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()


def execute_many(query, params_list):
    """Execute a query with multiple parameter sets."""
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()


def close_connection():
    """Close the database connection."""
    global connection

    if connection is not None and not connection.closed:
        connection.close()
        connection = None
        print("Database connection closed")
