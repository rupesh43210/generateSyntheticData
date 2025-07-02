# Database Setup Guide

## Overview

The enhanced PII generator now supports flexible database configuration with multiple ways to specify connection parameters and control table behavior to avoid overwriting existing data.

## Connection Methods

### Method 1: Command Line Parameters (Recommended for testing)

```bash
# Test connection
python pii_gen_enhanced.py test-connection \
  --server localhost \
  --database TestDatabase \
  --username sa \
  --password "YourPassword123!" \
  --port 1433

# Setup schema (creates tables if they don't exist)
python pii_gen_enhanced.py setup-schema \
  --server localhost \
  --database TestDatabase \
  --username sa \
  --password "YourPassword123!" \
  --table-behavior create_if_not_exists \
  --table-prefix pii_

# Generate and insert data
python pii_gen_enhanced.py generate \
  --records 1000 \
  --server localhost \
  --database TestDatabase \
  --username sa \
  --password "YourPassword123!" \
  --table-behavior create_if_not_exists \
  --table-prefix pii_ \
  --insert-mode append
```

### Method 2: Configuration File (Recommended for production)

1. Create database configuration file:
```bash
python pii_gen_enhanced.py create-db-config --output my_db_config.yaml
```

2. Edit `my_db_config.yaml` with your database details:
```yaml
database:
  connection_method: 'individual_params'
  server: 'your-server.database.windows.net'
  database: 'your-database-name'
  username: 'your-username'
  password: 'your-password'
  port: 1433
  driver: 'ODBC Driver 18 for SQL Server'

schema:
  name: 'dbo'
  table_behavior: 'create_if_not_exists'  # Won't overwrite existing tables
  table_prefix: 'pii_'  # Tables will be named pii_people, pii_addresses, etc.

data_insertion:
  mode: 'append'  # Always append data, never overwrite
  batch_size: 1000
```

3. Use the configuration file:
```bash
# Test connection
python pii_gen_enhanced.py --db-config my_db_config.yaml test-connection

# Setup schema
python pii_gen_enhanced.py --db-config my_db_config.yaml setup-schema

# Generate data
python pii_gen_enhanced.py --db-config my_db_config.yaml generate --records 5000
```

### Method 3: Environment Variables

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your database details:
```bash
DB_SERVER=localhost
DB_DATABASE=TestDatabase
DB_USERNAME=sa
DB_PASSWORD=YourPassword123!
DB_TABLE_BEHAVIOR=create_if_not_exists
DB_TABLE_PREFIX=pii_
DB_INSERT_MODE=append
```

3. Run commands (they'll automatically pick up environment variables):
```bash
python pii_gen_enhanced.py test-connection
python pii_gen_enhanced.py setup-schema
python pii_gen_enhanced.py generate --records 1000
```

### Method 4: Connection String

For complex connection scenarios:
```bash
python pii_gen_enhanced.py generate \
  --connection-string "Driver={ODBC Driver 18 for SQL Server};Server=localhost,1433;Database=TestDatabase;Uid=sa;Pwd=YourPassword123!;Encrypt=yes;TrustServerCertificate=yes;" \
  --records 1000 \
  --table-behavior create_if_not_exists \
  --insert-mode append
```

## Table Behavior Options

### `create_if_not_exists` (Recommended)
- Creates tables only if they don't exist
- **Safe**: Won't overwrite existing data
- Perfect for appending new data to existing tables

### `append_only`
- Assumes tables already exist
- Will fail if tables don't exist
- **Safest**: Guaranteed no table modifications

### `drop_and_create`
- **Dangerous**: Drops all existing tables and recreates them
- **All existing data will be lost**
- Only use for fresh database setup

## Data Insertion Modes

### `append` (Default)
- Always appends new records
- No duplicate checking
- **Fastest option**

### `skip_duplicates`
- Checks for duplicates before inserting
- Based on configurable key columns (SSN, email, phone, etc.)
- **Slower but prevents duplicates**

## Examples

### Safe Production Setup

```bash
# 1. Test connection first
python pii_gen_enhanced.py test-connection \
  --server myserver.database.windows.net \
  --database ProductionDB \
  --username myuser \
  --password "SecurePass123!"

# 2. Setup schema safely (won't overwrite)
python pii_gen_enhanced.py setup-schema \
  --server myserver.database.windows.net \
  --database ProductionDB \
  --username myuser \
  --password "SecurePass123!" \
  --table-behavior create_if_not_exists \
  --table-prefix test_pii_

# 3. Generate test data
python pii_gen_enhanced.py generate \
  --records 10000 \
  --server myserver.database.windows.net \
  --database ProductionDB \
  --username myuser \
  --password "SecurePass123!" \
  --table-behavior append_only \
  --table-prefix test_pii_ \
  --insert-mode skip_duplicates \
  --batch-size 500
```

### Azure SQL Database

```bash
python pii_gen_enhanced.py generate \
  --server myserver.database.windows.net \
  --database MyAzureDB \
  --username admin@myserver \
  --password "AzurePass123!" \
  --port 1433 \
  --records 50000 \
  --table-behavior create_if_not_exists \
  --table-prefix synthetic_ \
  --insert-mode append \
  --threads 8 \
  --batch-size 2000
```

### Local SQL Server

```bash
python pii_gen_enhanced.py generate \
  --server localhost \
  --database TestDB \
  --username sa \
  --password "LocalPass123!" \
  --records 5000 \
  --table-behavior create_if_not_exists \
  --table-prefix dev_pii_ \
  --insert-mode append
```

## Generated Tables

With prefix `pii_`, the following tables will be created:

- `pii_people` - Main person records
- `pii_addresses` - Address history
- `pii_phone_numbers` - Phone numbers
- `pii_email_addresses` - Email addresses
- `pii_employment_history` - Job history
- `pii_financial_profiles` - Financial information

## Configuration Tips

1. **Always test connection first** before generating large datasets
2. **Use table prefixes** to avoid conflicts with existing tables
3. **Start with small record counts** to verify everything works
4. **Use `create_if_not_exists`** for safety in production
5. **Use configuration files** for complex setups
6. **Set appropriate batch sizes** based on your database performance

## Troubleshooting

### Connection Issues
```bash
# Test basic connectivity
python pii_gen_enhanced.py test-connection --server localhost --database TestDB --username sa --password "YourPass"
```

### Driver Issues
- Install ODBC Driver 18 for SQL Server
- For older systems, use "ODBC Driver 17 for SQL Server"

### Permission Issues
- Ensure user has CREATE TABLE permissions for schema setup
- Ensure user has INSERT permissions for data generation

### Performance Issues
- Reduce batch size for slower databases
- Increase batch size for faster databases
- Adjust thread count based on database capacity