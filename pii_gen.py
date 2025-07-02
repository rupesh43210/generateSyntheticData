#!/usr/bin/env python3
"""
Enhanced PII Generator CLI with flexible database configuration
"""

import click
import logging
import sys
import time
import os
from pathlib import Path
from typing import Optional
import yaml
import json

from src.core.models import GenerationConfig, DataQualityProfile
from src.core.performance import PerformanceOptimizer
from src.core.database_config import DatabaseConfig
from src.generators.person_generator import PersonGenerator
from src.db.azure_sql import EnhancedAzureSQLDatabase


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Generation configuration file path')
@click.option('--db-config', type=click.Path(exists=True), help='Database configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, db_config, verbose):
    """Enhanced PII data generator with flexible database configuration"""
    ctx.ensure_object(dict)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load generation configuration
    if config:
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                ctx.obj['config'] = yaml.safe_load(f)
            else:
                ctx.obj['config'] = json.load(f)
    else:
        ctx.obj['config'] = {}
    
    # Load database configuration
    if db_config:
        ctx.obj['db_config'] = DatabaseConfig.from_yaml(db_config)
    else:
        # Try to load from environment or use defaults
        ctx.obj['db_config'] = DatabaseConfig.from_env()


@cli.command()
@click.option('--server', help='Database server hostname')
@click.option('--database', help='Database name')
@click.option('--username', help='Database username')
@click.option('--password', help='Database password', hide_input=True)
@click.option('--port', default=1433, help='Database port (default: 1433)')
@click.option('--connection-string', help='Complete connection string')
@click.option('--schema', default='dbo', help='Database schema (default: dbo)')
@click.pass_context
def test_connection(ctx, server, database, username, password, port, connection_string, schema):
    """Test database connection"""
    
    # Create database config from parameters
    db_config = ctx.obj.get('db_config', DatabaseConfig())
    
    if connection_string:
        db_config.database.connection_method = 'connection_string'
        db_config.database.connection_string = connection_string
    elif server and database and username and password:
        db_config.database.connection_method = 'individual_params'
        db_config.database.server = server
        db_config.database.database = database
        db_config.database.username = username
        db_config.database.password = password
        db_config.database.port = port
    
    db_config.schema_config.name = schema
    
    # Test connection
    db = EnhancedAzureSQLDatabase(db_config)
    
    click.echo("Testing database connection...")
    if db.test_connection():
        click.echo("✅ Database connection successful!")
        
        # Show connection details (without password)
        click.echo(f"Server: {db_config.database.server}")
        click.echo(f"Database: {db_config.database.database}")
        click.echo(f"Schema: {db_config.schema.name}")
    else:
        click.echo("❌ Database connection failed!")
        sys.exit(1)


@cli.command()
@click.option('--server', help='Database server hostname')
@click.option('--database', help='Database name')
@click.option('--username', help='Database username')
@click.option('--password', help='Database password', hide_input=True)
@click.option('--port', default=1433, help='Database port (default: 1433)')
@click.option('--connection-string', help='Complete connection string')
@click.option('--schema', default='dbo', help='Database schema (default: dbo)')
@click.option('--table-behavior', default='create_if_not_exists',
              type=click.Choice(['create_if_not_exists', 'drop_and_create', 'append_only']),
              help='Table creation behavior')
@click.option('--table-prefix', default='', help='Table name prefix')
@click.pass_context
def setup_schema(ctx, server, database, username, password, port, connection_string, 
                schema, table_behavior, table_prefix):
    """Setup database schema with flexible options"""
    
    # Create database config from parameters
    db_config = ctx.obj.get('db_config', DatabaseConfig())
    
    if connection_string:
        db_config.database.connection_method = 'connection_string'
        db_config.database.connection_string = connection_string
    elif server and database and username and password:
        db_config.database.connection_method = 'individual_params'
        db_config.database.server = server
        db_config.database.database = database
        db_config.database.username = username
        db_config.database.password = password
        db_config.database.port = port
    
    db_config.schema_config.name = schema
    db_config.schema.table_behavior = table_behavior
    db_config.schema.table_prefix = table_prefix
    
    # Setup schema
    db = EnhancedAzureSQLDatabase(db_config)
    
    click.echo(f"Setting up database schema with behavior: {table_behavior}")
    if table_prefix:
        click.echo(f"Using table prefix: {table_prefix}")
    
    if db.setup_schema():
        click.echo("✅ Database schema setup completed successfully!")
    else:
        click.echo("❌ Database schema setup failed!")
        sys.exit(1)


@cli.command()
@click.option('--records', '-n', default=1000, help='Number of records to generate')
@click.option('--threads', '-t', default=4, help='Number of threads to use')
@click.option('--batch-size', '-b', default=1000, help='Batch size for processing')
@click.option('--output', '-o', type=click.Path(), help='Output file path (CSV/JSON)')
@click.option('--server', help='Database server hostname')
@click.option('--database', help='Database name')
@click.option('--username', help='Database username')
@click.option('--password', help='Database password', hide_input=True)
@click.option('--port', default=1433, help='Database port (default: 1433)')
@click.option('--connection-string', help='Complete connection string')
@click.option('--schema', default='dbo', help='Database schema (default: dbo)')
@click.option('--table-behavior', default='create_if_not_exists',
              type=click.Choice(['create_if_not_exists', 'drop_and_create', 'append_only']),
              help='Table creation behavior')
@click.option('--table-prefix', default='', help='Table name prefix')
@click.option('--insert-mode', default='append',
              type=click.Choice(['append', 'skip_duplicates']),
              help='Data insertion mode')
@click.option('--variability-profile', default='realistic', 
              type=click.Choice(['minimal', 'realistic', 'messy', 'extreme']),
              help='Data quality variability profile')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--families', type=int, help='Number of family clusters to generate')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating data')
@click.pass_context
def generate(ctx, records, threads, batch_size, output, server, database, username, password, port,
            connection_string, schema, table_behavior, table_prefix, insert_mode, 
            variability_profile, seed, families, dry_run):
    """Generate synthetic PII data with enhanced configuration"""
    
    if dry_run:
        click.echo(f"Would generate {records:,} records with:")
        click.echo(f"  Threads: {threads}")
        click.echo(f"  Batch size: {batch_size}")
        click.echo(f"  Variability profile: {variability_profile}")
        click.echo(f"  Table behavior: {table_behavior}")
        click.echo(f"  Insert mode: {insert_mode}")
        if table_prefix:
            click.echo(f"  Table prefix: {table_prefix}")
        if families:
            click.echo(f"  Family clusters: {families}")
        return
    
    # Create data quality profile
    variability_profiles = {
        'minimal': DataQualityProfile(
            missing_data_rate=0.01,
            typo_rate=0.005,
            duplicate_rate=0.0001,
            outlier_rate=0.001,
            inconsistency_rate=0.01
        ),
        'realistic': DataQualityProfile(
            missing_data_rate=0.05,
            typo_rate=0.02,
            duplicate_rate=0.001,
            outlier_rate=0.01,
            inconsistency_rate=0.03
        ),
        'messy': DataQualityProfile(
            missing_data_rate=0.15,
            typo_rate=0.05,
            duplicate_rate=0.005,
            outlier_rate=0.03,
            inconsistency_rate=0.08
        ),
        'extreme': DataQualityProfile(
            missing_data_rate=0.25,
            typo_rate=0.10,
            duplicate_rate=0.01,
            outlier_rate=0.05,
            inconsistency_rate=0.15
        )
    }
    
    # Create generation config
    config = GenerationConfig(
        num_records=records,
        batch_size=batch_size,
        num_threads=threads,
        seed=seed,
        data_quality_profile=variability_profiles[variability_profile]
    )
    
    # Merge with file config if provided
    if ctx.obj.get('config'):
        config_dict = config.dict()
        config_dict.update(ctx.obj['config'])
        config = GenerationConfig(**config_dict)
    
    click.echo(f"Starting generation of {records:,} records...")
    start_time = time.time()
    
    # Initialize generators
    person_gen = PersonGenerator(config)
    performance_opt = PerformanceOptimizer(config)
    
    # Generate families or individual records
    if families:
        click.echo(f"Generating {families} family clusters...")
        family_clusters = person_gen.create_family_clusters(families)
        all_people = [person for family in family_clusters for person in family]
        
        # Generate additional individual records if needed
        remaining = records - len(all_people)
        if remaining > 0:
            click.echo(f"Generating {remaining} additional individual records...")
            for batch in performance_opt.generate_parallel(
                person_gen.generate_person, remaining, batch_size, threads
            ):
                all_people.extend(batch)
    else:
        # Generate individual records
        all_people = []
        for batch in performance_opt.generate_parallel(
            person_gen.generate_person, records, batch_size, threads
        ):
            all_people.extend(batch)
    
    elapsed = time.time() - start_time
    rate = len(all_people) / elapsed if elapsed > 0 else 0
    
    click.echo(f"Generated {len(all_people):,} records in {elapsed:.2f} seconds ({rate:.0f} records/sec)")
    
    # Output data to file
    if output:
        click.echo(f"Writing to {output}...")
        write_output(all_people, output)
    
    # Insert to database
    if any([server, database, username, password, connection_string]):
        # Create database config from parameters
        db_config = ctx.obj.get('db_config', DatabaseConfig())
        
        if connection_string:
            db_config.database.connection_method = 'connection_string'
            db_config.database.connection_string = connection_string
        elif server and database and username and password:
            db_config.database.connection_method = 'individual_params'
            db_config.database.server = server
            db_config.database.database = database
            db_config.database.username = username
            db_config.database.password = password
            db_config.database.port = port
        
        db_config.schema_config.name = schema
        db_config.schema.table_behavior = table_behavior
        db_config.schema.table_prefix = table_prefix
        db_config.data_insertion.mode = insert_mode
        db_config.data_insertion.batch_size = batch_size
        
        click.echo("Setting up database schema...")
        db = EnhancedAzureSQLDatabase(db_config)
        
        if db.setup_schema():
            click.echo("Inserting data to database...")
            success = db.bulk_insert_people(all_people, batch_size)
            
            if success:
                click.echo("✅ Successfully inserted data to database")
            else:
                click.echo("❌ Failed to insert data to database", err=True)
        else:
            click.echo("❌ Failed to setup database schema", err=True)


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='database_config.yaml',
              help='Output configuration file')
def create_db_config(output):
    """Create database configuration file template"""
    
    # Use the example config we created
    config_path = Path(__file__).parent / 'configs' / 'database_config.yaml'
    
    if config_path.exists():
        # Copy the template
        with open(config_path, 'r') as f:
            content = f.read()
        
        with open(output, 'w') as f:
            f.write(content)
        
        click.echo(f"Database configuration template created: {output}")
        click.echo("Please edit the file with your actual database credentials.")
    else:
        click.echo("Template file not found. Creating basic template...")
        
        # Create basic template
        basic_config = {
            'database': {
                'connection_method': 'individual_params',
                'server': 'your-server.database.windows.net',
                'database': 'your-database-name',
                'username': 'your-username',
                'password': 'your-password',
                'port': 1433,
                'driver': 'ODBC Driver 18 for SQL Server'
            },
            'schema': {
                'name': 'dbo',
                'table_behavior': 'create_if_not_exists',
                'table_prefix': 'pii_'
            },
            'data_insertion': {
                'mode': 'append',
                'batch_size': 1000
            }
        }
        
        with open(output, 'w') as f:
            yaml.dump(basic_config, f, default_flow_style=False)
        
        click.echo(f"Basic database configuration created: {output}")


def write_output(people, output_path):
    """Write people data to output file"""
    import pandas as pd
    
    # Convert to flat format
    records = []
    for person in people:
        # Flatten person data
        record = {
            'person_id': person.person_id,
            'ssn': person.ssn,
            'first_name': person.first_name,
            'middle_name': person.middle_name,
            'last_name': person.last_name,
            'full_name': f"{person.first_name} {person.last_name}",
            'date_of_birth': person.date_of_birth,
            'gender': person.gender if isinstance(person.gender, str) else person.gender.value,
        }
        
        # Current address
        current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
        if current_addr:
            record.update({
                'address': f"{current_addr.street_1}, {current_addr.city}, {current_addr.state} {current_addr.zip_code}",
                'city': current_addr.city,
                'state': current_addr.state,
                'zip_code': current_addr.zip_code
            })
        
        # Primary contact
        primary_phone = next((p for p in person.phone_numbers if p.is_primary), None)
        if primary_phone:
            record['phone'] = f"({primary_phone.area_code}) {primary_phone.number[:3]}-{primary_phone.number[3:]}"
        
        primary_email = next((e for e in person.email_addresses if e.is_primary), None)
        if primary_email:
            record['email'] = primary_email.email
        
        # Current employment
        current_job = next((e for e in person.employment_history if e.is_current), None)
        if current_job:
            record.update({
                'employer': current_job.employer_name,
                'job_title': current_job.job_title,
                'salary': current_job.salary
            })
        
        # Financial
        if person.financial_profile:
            record.update({
                'credit_score': person.financial_profile.credit_score,
                'annual_income': person.financial_profile.annual_income
            })
        
        records.append(record)
    
    # Write to file
    df = pd.DataFrame(records)
    
    if output_path.endswith('.csv'):
        df.to_csv(output_path, index=False)
    elif output_path.endswith('.json'):
        df.to_json(output_path, orient='records', indent=2)
    else:
        # Default to CSV
        df.to_csv(output_path + '.csv', index=False)


if __name__ == '__main__':
    cli()