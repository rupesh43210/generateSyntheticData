# PII Generator Examples

This document provides comprehensive examples of using the PII Generator for various scenarios.

## Basic Usage Examples

### 1. Generate Simple Dataset
```bash
# Generate 1,000 basic records
python pii_gen.py generate --records 1000 --output simple_data.csv
```

### 2. High-Performance Generation
```bash
# Generate 10 million records with maximum performance
python pii_gen.py generate \
  --records 10000000 \
  --threads 8 \
  --batch-size 10000 \
  --variability-profile minimal \
  --output large_dataset.csv
```

### 3. Realistic Test Data
```bash
# Generate realistic messy data for QA testing
python pii_gen.py generate \
  --records 50000 \
  --variability-profile messy \
  --families 1000 \
  --output qa_test_data.csv
```

## Azure SQL Database Examples

### 1. Complete Database Setup
```bash
# Step 1: Create the schema
python pii_gen.py create-schema \
  --connection-string "Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-db;Uid=your-user;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;"

# Step 2: Generate and insert data
python pii_gen.py generate \
  --records 1000000 \
  --threads 8 \
  --batch-size 5000 \
  --connection-string "Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-db;Uid=your-user;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;" \
  --variability-profile realistic

# Step 3: Validate data quality
python pii_gen.py validate \
  --connection-string "Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-db;Uid=your-user;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;"
```

### 2. Streaming to Database
```bash
# Stream 5,000 records per second for 2 hours
python pii_gen.py stream \
  --rate 5000 \
  --duration 7200 \
  --connection-string "your-connection-string" \
  --batch-size 10000
```

## Configuration Examples

### 1. Custom Configuration File
```yaml
# custom_config.yaml
data_quality_profile:
  missing_data_rate: 0.08    # 8% missing data
  typo_rate: 0.03           # 3% typos
  duplicate_rate: 0.002     # 0.2% duplicates
  outlier_rate: 0.015       # 1.5% outliers
  inconsistency_rate: 0.05  # 5% format inconsistencies

# Performance settings optimized for your hardware
num_threads: 12
batch_size: 15000

# Enable all advanced features
enable_relationships: true
enable_temporal_patterns: true
enable_geographic_clustering: true
enable_financial_correlations: true

# Custom geographic distribution (e.g., focus on West Coast)
geographic_distribution:
  CA: 0.40    # California - 40%
  WA: 0.15    # Washington - 15%
  OR: 0.10    # Oregon - 10%
  NV: 0.08    # Nevada - 8%
  AZ: 0.12    # Arizona - 12%
  Other: 0.15 # Rest of US - 15%

# Industry distribution for tech hub
industry_distribution:
  Technology: 0.35
  Finance: 0.15
  Healthcare: 0.10
  Education: 0.08
  Retail: 0.08
  Manufacturing: 0.05
  Other: 0.19

# Contact preferences
min_addresses_per_person: 1
max_addresses_per_person: 4
min_phones_per_person: 1
max_phones_per_person: 3
min_emails_per_person: 1
max_emails_per_person: 2
```

```bash
# Use the custom configuration
python pii_gen.py generate --config custom_config.yaml --records 500000
```

### 2. High-Volume Production Config
```yaml
# production_config.yaml
data_quality_profile:
  missing_data_rate: 0.04
  typo_rate: 0.015
  duplicate_rate: 0.0008
  outlier_rate: 0.008
  inconsistency_rate: 0.025

# Optimized for maximum throughput
num_threads: 16
batch_size: 20000

# Simplified for performance
enable_relationships: false
enable_temporal_patterns: true
enable_geographic_clustering: false
enable_financial_correlations: true

# Minimal complexity
min_addresses_per_person: 1
max_addresses_per_person: 2
min_phones_per_person: 1
max_phones_per_person: 1
min_emails_per_person: 1
max_emails_per_person: 1
min_jobs_per_person: 1
max_jobs_per_person: 3
```

## Specialized Use Cases

### 1. Financial Fraud Detection Dataset
```bash
# Generate dataset optimized for fraud detection patterns
python pii_gen.py generate \
  --records 2000000 \
  --variability-profile extreme \
  --threads 8 \
  --seed 12345 \
  --families 50000 \
  --config fraud_detection_config.yaml
```

```yaml
# fraud_detection_config.yaml
data_quality_profile:
  missing_data_rate: 0.12    # Higher missing data
  typo_rate: 0.06           # More typos
  duplicate_rate: 0.008     # More duplicates
  outlier_rate: 0.04        # More outliers
  inconsistency_rate: 0.10  # More inconsistencies

enable_relationships: true   # Important for fraud patterns
enable_financial_correlations: true

# Generate suspicious patterns
geographic_distribution:
  FL: 0.25    # Florida - known for fraud
  CA: 0.20    # California
  TX: 0.15    # Texas
  NY: 0.15    # New York
  Other: 0.25
```

### 2. Healthcare Analytics Dataset
```bash
# Generate healthcare-focused dataset
python pii_gen.py generate \
  --records 1500000 \
  --variability-profile realistic \
  --config healthcare_config.yaml
```

```yaml
# healthcare_config.yaml
data_quality_profile:
  missing_data_rate: 0.06    # HIPAA considerations
  typo_rate: 0.02
  duplicate_rate: 0.001
  outlier_rate: 0.01
  inconsistency_rate: 0.03

# Healthcare industry focus
industry_distribution:
  Healthcare: 0.45
  Insurance: 0.15
  Technology: 0.10
  Government: 0.08
  Education: 0.07
  Other: 0.15

# Age distribution skewed older for healthcare
# (This would require custom age distribution implementation)
```

### 3. E-commerce Customer Dataset
```bash
# Generate e-commerce customer data
python pii_gen.py generate \
  --records 5000000 \
  --variability-profile messy \
  --families 100000 \
  --config ecommerce_config.yaml
```

```yaml
# ecommerce_config.yaml
data_quality_profile:
  missing_data_rate: 0.10    # Customers often don't fill all fields
  typo_rate: 0.04           # Common in user-entered data
  duplicate_rate: 0.003     # Multiple accounts
  outlier_rate: 0.02
  inconsistency_rate: 0.08

# Multiple addresses common for shipping
min_addresses_per_person: 1
max_addresses_per_person: 5  # Home, work, billing, shipping

# Multiple contact methods
min_emails_per_person: 1
max_emails_per_person: 3
min_phones_per_person: 1
max_phones_per_person: 2

# Consumer-focused industries
industry_distribution:
  Retail: 0.25
  Technology: 0.15
  Healthcare: 0.12
  Education: 0.10
  Finance: 0.08
  Manufacturing: 0.08
  Other: 0.22
```

## Performance Optimization Examples

### 1. Memory-Constrained Environment
```bash
# Generate large dataset with limited memory
python pii_gen.py generate \
  --records 50000000 \
  --threads 4 \
  --batch-size 1000 \
  --variability-profile minimal \
  --config memory_optimized.yaml
```

```yaml
# memory_optimized.yaml
num_threads: 4
batch_size: 1000

# Minimal features to reduce memory usage
enable_relationships: false
enable_temporal_patterns: false
enable_geographic_clustering: false
enable_financial_correlations: false

# Simplified data
min_addresses_per_person: 1
max_addresses_per_person: 1
min_phones_per_person: 1
max_phones_per_person: 1
min_emails_per_person: 1
max_emails_per_person: 1
min_jobs_per_person: 0
max_jobs_per_person: 1
```

### 2. CPU-Optimized Generation
```bash
# Maximize CPU utilization
python pii_gen.py generate \
  --records 10000000 \
  --threads 16 \
  --batch-size 25000 \
  --variability-profile realistic
```

### 3. Database Insert Optimization
```bash
# Optimize for Azure SQL insert performance
python pii_gen.py generate \
  --records 20000000 \
  --threads 8 \
  --batch-size 50000 \
  --connection-string "your-connection-string" \
  --variability-profile minimal
```

## Integration Examples

### 1. Python Script Integration
```python
# custom_generator.py
from src.core.models import GenerationConfig, DataQualityProfile
from src.generators.person_generator import PersonGenerator
from src.core.performance import PerformanceOptimizer

def generate_custom_dataset():
    # Custom configuration
    config = GenerationConfig(
        num_records=100000,
        batch_size=5000,
        num_threads=6,
        seed=42,
        data_quality_profile=DataQualityProfile(
            missing_data_rate=0.07,
            typo_rate=0.03,
            duplicate_rate=0.002,
            outlier_rate=0.015,
            inconsistency_rate=0.04
        ),
        enable_relationships=True,
        enable_financial_correlations=True
    )
    
    # Generate data
    generator = PersonGenerator(config)
    optimizer = PerformanceOptimizer(config)
    
    all_people = []
    for batch in optimizer.generate_parallel(
        generator.generate_person, 
        config.num_records, 
        config.batch_size, 
        config.num_threads
    ):
        all_people.extend(batch)
        print(f"Generated {len(all_people)} records so far...")
    
    return all_people

if __name__ == "__main__":
    people = generate_custom_dataset()
    print(f"Generated {len(people)} total records")
```

### 2. Airflow DAG Integration
```python
# airflow_dag.py
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'pii_data_generation',
    default_args=default_args,
    description='Generate synthetic PII data daily',
    schedule_interval='@daily',
    catchup=False
)

# Generate daily batch
generate_task = BashOperator(
    task_id='generate_pii_data',
    bash_command='''
    cd /opt/pii-generator && 
    python pii_gen.py generate \
      --records 1000000 \
      --threads 8 \
      --batch-size 10000 \
      --connection-string "{{ var.value.azure_sql_connection }}" \
      --variability-profile realistic \
      --config configs/production_config.yaml
    ''',
    dag=dag
)

# Validate data quality
validate_task = BashOperator(
    task_id='validate_data_quality',
    bash_command='''
    cd /opt/pii-generator && 
    python pii_gen.py validate \
      --connection-string "{{ var.value.azure_sql_connection }}"
    ''',
    dag=dag
)

generate_task >> validate_task
```

## Testing Examples

### 1. Unit Testing Custom Generators
```python
# test_custom.py
import pytest
from src.generators.person_generator import PersonGenerator
from src.core.models import GenerationConfig, DataQualityProfile

def test_custom_generation():
    config = GenerationConfig(
        num_records=100,
        data_quality_profile=DataQualityProfile(
            missing_data_rate=0.1,
            typo_rate=0.05
        )
    )
    
    generator = PersonGenerator(config)
    
    # Generate test data
    people = [generator.generate_person() for _ in range(100)]
    
    # Assertions
    assert len(people) == 100
    assert all(person.first_name for person in people)
    assert all(person.last_name for person in people)
    
    # Check data quality
    missing_ssn = sum(1 for p in people if p.ssn is None)
    assert 5 <= missing_ssn <= 15  # Should be around 10%

def test_performance_benchmark():
    """Test that generation meets performance targets"""
    import time
    
    config = GenerationConfig(num_records=10000)
    generator = PersonGenerator(config)
    
    start_time = time.time()
    people = [generator.generate_person() for _ in range(10000)]
    elapsed = time.time() - start_time
    
    rate = len(people) / elapsed
    assert rate > 1000  # Should generate > 1000 records/second
```

### 2. Integration Testing
```bash
# Run integration tests
pytest tests/integration/ -v --connection-string "your-test-db-connection"
```

## Monitoring and Observability

### 1. Performance Monitoring
```bash
# Monitor generation with detailed logging
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)

from src.core.models import GenerationConfig
from src.generators.person_generator import PersonGenerator
from src.core.performance import PerformanceOptimizer

config = GenerationConfig(num_records=50000, num_threads=4)
generator = PersonGenerator(config)
optimizer = PerformanceOptimizer(config)

for batch in optimizer.generate_parallel(generator.generate_person, 50000):
    print(f'Generated batch of {len(batch)} records')
"
```

### 2. Memory Profiling
```bash
# Profile memory usage
pip install memory-profiler
python -m memory_profiler pii_gen.py generate --records 100000 --threads 1
```

### 3. Database Performance Monitoring
```sql
-- Monitor Azure SQL performance during inserts
SELECT 
    r.session_id,
    r.status,
    r.command,
    r.percent_complete,
    r.total_elapsed_time,
    r.estimated_completion_time,
    t.text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id > 50;
```

## Troubleshooting Examples

### 1. Debug Connection Issues
```python
# test_connection.py
import pyodbc

def test_azure_sql_connection():
    connection_string = "your-connection-string"
    
    try:
        conn = pyodbc.connect(connection_string, timeout=30)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Connection successful: {result}")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_azure_sql_connection()
```

### 2. Performance Debugging
```bash
# Debug slow generation
python -m cProfile -o profile.stats pii_gen.py generate --records 10000
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

### 3. Memory Issues
```bash
# Monitor memory usage during generation
watch -n 1 'ps aux | grep python | grep pii_gen'

# Or use memory profiler
mprof run pii_gen.py generate --records 100000
mprof plot
```

These examples cover the most common use cases and should help you get started with the PII Generator for your specific needs.