#!/usr/bin/env python3
"""
PII Generator CLI - High-performance synthetic PII data generator
"""

import click
import logging
import sys
import time
from pathlib import Path
from typing import Optional
import yaml
import json

from src.core.models import GenerationConfig, DataQualityProfile
from src.core.performance import PerformanceOptimizer
from src.generators.person_generator import PersonGenerator
from src.db.azure_sql import AzureSQLDatabase


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """High-performance synthetic PII data generator for Azure SQL Database"""
    ctx.ensure_object(dict)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    if config:
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                ctx.obj['config'] = yaml.safe_load(f)
            else:
                ctx.obj['config'] = json.load(f)
    else:
        ctx.obj['config'] = {}


@cli.command()
@click.option('--records', '-n', default=1000, help='Number of records to generate')
@click.option('--threads', '-t', default=4, help='Number of threads to use')
@click.option('--batch-size', '-b', default=1000, help='Batch size for processing')
@click.option('--output', '-o', type=click.Path(), help='Output file path (CSV/JSON)')
@click.option('--connection-string', help='Azure SQL connection string')
@click.option('--variability-profile', default='realistic', 
              type=click.Choice(['minimal', 'realistic', 'messy', 'extreme']),
              help='Data quality variability profile')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--families', type=int, help='Number of family clusters to generate')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating data')
@click.pass_context
def generate(ctx, records, threads, batch_size, output, connection_string, 
            variability_profile, seed, families, dry_run):
    """Generate synthetic PII data"""
    
    if dry_run:
        click.echo(f"Would generate {records:,} records with:")
        click.echo(f"  Threads: {threads}")
        click.echo(f"  Batch size: {batch_size}")
        click.echo(f"  Variability profile: {variability_profile}")
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
    
    # Output data
    if output:
        click.echo(f"Writing to {output}...")
        write_output(all_people, output)
    
    # Insert to database
    if connection_string:
        click.echo("Inserting to Azure SQL Database...")
        db = AzureSQLDatabase(connection_string)
        
        # Create schema if needed
        if click.confirm("Create database schema?"):
            db.create_schema()
        
        success = db.bulk_insert_people(all_people, batch_size)
        if success:
            click.echo("Successfully inserted to database")
            
            # Validate data quality
            stats = db.validate_data_quality()
            click.echo("Data quality statistics:")
            for key, value in stats.items():
                click.echo(f"  {key}: {value}")
        else:
            click.echo("Failed to insert to database", err=True)


@cli.command()
@click.option('--rate', default=1000, help='Records per second to generate')
@click.option('--duration', default=3600, help='Duration in seconds')
@click.option('--connection-string', required=True, help='Azure SQL connection string')
@click.option('--batch-size', '-b', default=1000, help='Batch size for inserts')
@click.pass_context
def stream(ctx, rate, duration, connection_string, batch_size):
    """Stream generation directly to Azure SQL"""
    
    config = GenerationConfig(
        num_records=rate * duration,  # Estimate
        batch_size=batch_size
    )
    
    # Merge with file config if provided
    if ctx.obj.get('config'):
        config_dict = config.dict()
        config_dict.update(ctx.obj['config'])
        config = GenerationConfig(**config_dict)
    
    click.echo(f"Streaming {rate} records/second for {duration} seconds to Azure SQL...")
    
    # Initialize components
    person_gen = PersonGenerator(config)
    performance_opt = PerformanceOptimizer(config)
    db = AzureSQLDatabase(connection_string)
    
    # Stream generation
    total_inserted = 0
    person_stream = performance_opt.stream_generate(
        person_gen.generate_person, rate, duration
    )
    
    total_inserted = db.stream_insert(person_stream, batch_size)
    
    click.echo(f"Streamed {total_inserted:,} records to database")


@cli.command()
@click.option('--connection-string', required=True, help='Azure SQL connection string')
@click.option('--schema', default='dbo', help='Database schema name')
def create_schema(connection_string, schema):
    """Create database schema for PII data"""
    
    db = AzureSQLDatabase(connection_string, schema)
    
    click.echo(f"Creating schema '{schema}' in Azure SQL Database...")
    
    if db.create_schema():
        click.echo("Schema created successfully")
    else:
        click.echo("Failed to create schema", err=True)
        sys.exit(1)


@cli.command()
@click.option('--connection-string', required=True, help='Azure SQL connection string')
@click.option('--schema', default='dbo', help='Database schema name')
def validate(connection_string, schema):
    """Validate data quality in database"""
    
    db = AzureSQLDatabase(connection_string, schema)
    
    click.echo("Validating data quality...")
    
    stats = db.validate_data_quality()
    
    click.echo("Data Quality Report:")
    click.echo("=" * 50)
    
    for key, value in stats.items():
        if isinstance(value, float):
            click.echo(f"{key}: {value:.2f}")
        else:
            click.echo(f"{key}: {value:,}")


@cli.command()
@click.option('--profile', default='realistic',
              type=click.Choice(['minimal', 'realistic', 'messy', 'extreme']),
              help='Variability profile to generate')
@click.option('--output', '-o', type=click.Path(), default='config.yaml',
              help='Output configuration file')
def create_config(profile, output):
    """Create configuration file with specified profile"""
    
    profiles = {
        'minimal': {
            'data_quality_profile': {
                'missing_data_rate': 0.01,
                'typo_rate': 0.005,
                'duplicate_rate': 0.0001,
                'outlier_rate': 0.001,
                'inconsistency_rate': 0.01
            },
            'num_threads': 2,
            'batch_size': 500
        },
        'realistic': {
            'data_quality_profile': {
                'missing_data_rate': 0.05,
                'typo_rate': 0.02,
                'duplicate_rate': 0.001,
                'outlier_rate': 0.01,
                'inconsistency_rate': 0.03
            },
            'num_threads': 4,
            'batch_size': 1000,
            'enable_relationships': True,
            'enable_temporal_patterns': True,
            'enable_geographic_clustering': True,
            'enable_financial_correlations': True
        },
        'messy': {
            'data_quality_profile': {
                'missing_data_rate': 0.15,
                'typo_rate': 0.05,
                'duplicate_rate': 0.005,
                'outlier_rate': 0.03,
                'inconsistency_rate': 0.08
            },
            'num_threads': 6,
            'batch_size': 2000
        },
        'extreme': {
            'data_quality_profile': {
                'missing_data_rate': 0.25,
                'typo_rate': 0.10,
                'duplicate_rate': 0.01,
                'outlier_rate': 0.05,
                'inconsistency_rate': 0.15
            },
            'num_threads': 8,
            'batch_size': 5000
        }
    }
    
    config = profiles[profile]
    
    with open(output, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    click.echo(f"Configuration file created: {output}")


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
            'gender': person.gender.value,
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