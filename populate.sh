#!/bin/bash

# Database credentials
DB_HOST="10.5.18.73"
DB_USER="22CS30045"
DB_NAME="22CS30045"
DB_PASSWORD="22CS30045"

# SQL scripts to execute
SQL_SCRIPTS=("create.sql" "seed.sql")

# Run each SQL script using psql
for SCRIPT in "${SQL_SCRIPTS[@]}"; do
    echo "Running $SCRIPT..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$SCRIPT"
    if [ $? -eq 0 ]; then
        echo "$SCRIPT executed successfully!"
    else
        echo "Error executing $SCRIPT"
        exit 1
    fi
done
