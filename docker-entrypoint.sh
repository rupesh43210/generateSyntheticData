#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    # Skip database check if in file-only mode
    if [ "$OUTPUT_MODE" = "file" ]; then
        echo "Running in file-only mode, skipping database check"
        return 0
    fi
    
    echo "Waiting for database to be ready..."
    until python -c "
from src.db.azure_sql import EnhancedAzureSQLDatabase
from src.core.database_config import DatabaseConfig
import os
import sys

try:
    config = DatabaseConfig.from_env()
    db = EnhancedAzureSQLDatabase(config)
    # Test connection
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "Database is up!"
}

# Function to create database schema
create_schema() {
    # Skip schema creation if in file-only mode
    if [ "$OUTPUT_MODE" = "file" ]; then
        echo "Running in file-only mode, skipping schema creation"
        return 0
    fi
    
    echo "Creating database schema..."
    python pii_gen.py setup-schema || echo "Schema already exists or creation failed"
}

# Main entrypoint logic
case "$1" in
    web)
        wait_for_db
        create_schema
        echo "Starting web application..."
        exec python web_app.py
        ;;
    web-enhanced)
        wait_for_db
        create_schema
        echo "Starting enhanced web application..."
        exec python web_app_enhanced.py
        ;;
    cli)
        wait_for_db
        create_schema
        echo "PII Generator CLI is ready. Run commands like:"
        echo "  docker-compose run pii-cli python pii_gen.py generate --count 1000 --output /app/output/data.csv"
        echo "  docker-compose run pii-cli python pii_gen.py stream --rate 100"
        exec /bin/bash
        ;;
    generate)
        wait_for_db
        create_schema
        shift
        exec python pii_gen.py generate "$@"
        ;;
    stream)
        wait_for_db
        create_schema
        shift
        exec python pii_gen.py stream "$@"
        ;;
    *)
        # Pass through any other commands
        exec "$@"
        ;;
esac