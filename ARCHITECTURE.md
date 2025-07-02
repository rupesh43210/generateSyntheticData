# PII Generator Architecture

This document describes the architecture, design decisions, and technical implementation of the PII Generator.

## Overview

The PII Generator is designed as a high-performance, modular system that can generate millions of synthetic PII records with realistic variability and statistical accuracy. The architecture prioritizes scalability, maintainability, and extensibility.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Configuration  │    │   Validation    │
│   pii_gen.py    │    │   YAML/JSON     │    │    Testing      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────────────────────────────────────────────────────┐
│                    Core Orchestration                           │
│  ┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ PersonGenerator│  │ PerformanceOpt  │  │ VariabilityEng  │   │
│  └───────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────────────────────────────────────────────────────┐
│                 Component Generators                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │NameGen      │ │AddressGen   │ │ContactGen   │ │Financial │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Employment   │ │Relationships│ │Temporal     │ │Geographic│  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────────────────────────────────────────────────────┐
│                  Data Models & Constants                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │ Pydantic    │ │ Enums       │ │ Name Data   │ │Geographic│  │
│  │ Models      │ │ & Types     │ │ Constants   │ │ Data     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────────────────────────────────────────────────────┐
│                    Output Layer                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │ Azure SQL   │ │ CSV Export  │ │ JSON Export │ │ Streaming│  │
│  │ Database    │ │             │ │             │ │ Output   │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Layer (`pii_gen.py`)

The command-line interface built with Click provides multiple commands:

- **generate**: Main data generation command
- **stream**: Continuous streaming generation  
- **create-schema**: Database schema creation
- **validate**: Data quality validation
- **create-config**: Configuration file generation

**Design Decisions:**
- Click for robust CLI with subcommands
- Rich for enhanced terminal output
- Configuration file support (YAML/JSON)
- Dry-run capabilities for testing

### 2. Core Models (`src/core/models.py`)

Pydantic models define the data structures with validation:

```python
class Person(BaseModel):
    person_id: str
    ssn: Optional[str]
    first_name: str
    # ... other fields
    addresses: List[Address]
    phone_numbers: List[PhoneNumber]
    # ... related data
```

**Design Decisions:**
- Pydantic for runtime validation and serialization
- Optional fields for realistic missing data
- Strong typing throughout
- Nested relationships for complex data

### 3. Variability Engine (`src/core/variability.py`)

Introduces realistic data quality issues:

```python
class VariabilityEngine:
    def introduce_typo(self, text: str) -> str
    def make_missing(self, value: Any) -> Optional[Any]
    def vary_format(self, value: str, value_type: str) -> str
    def create_outlier(self, value: Any, value_type: str) -> Any
```

**Design Decisions:**
- Configurable rates for different quality issues
- Type-specific variations (phone formats, date formats)
- Statistical realism (Benford's Law, normal distributions)
- Reproducible with seed control

### 4. Performance Optimizer (`src/core/performance.py`)

Handles high-performance generation:

```python
class PerformanceOptimizer:
    def generate_parallel(self, generator_func, total_records, batch_size, num_processes)
    def stream_generate(self, generator_func, rate_per_second, duration_seconds)
    def generate_chunked(self, generator_func, total_records, chunk_size)
```

**Design Decisions:**
- Multiprocessing for CPU-bound tasks
- Streaming for memory efficiency
- Configurable batch sizes
- Progress tracking with tqdm

## Component Generators

### Name Generator (`src/generators/name_generator.py`)

Generates culturally diverse names with temporal accuracy:

**Features:**
- Period-appropriate names by birth year
- Cultural/ethnic name distributions
- Nickname generation
- Name variations and suffixes
- Family relationship naming

**Data Sources:**
- US Census name popularity data
- Cultural name databases
- Historical naming trends

### Address Generator (`src/generators/address_generator.py`)

Creates realistic address data:

**Features:**
- Real city/state/zip combinations
- Multiple address types (current, previous, billing)
- Address format variations
- Geographic clustering
- Military and PO Box addresses

**Data Sources:**
- USPS city/state/zip data
- Population density information
- Address format standards

### Contact Generator (`src/generators/contact_generator.py`)

Generates phone and email data:

**Features:**
- Valid area codes by state
- Multiple phone formats
- Realistic email patterns
- Domain distribution by type
- Contact validation states

**Algorithms:**
- Phone number validation rules
- Email domain weighting
- Format variation patterns

### Financial Generator (`src/generators/financial_generator.py`)

Creates correlated financial profiles:

**Features:**
- Credit score distributions
- Income correlations by age/industry/location
- Debt profile generation
- Account history simulation
- Statistical compliance (Benford's Law)

**Correlations:**
- Age → Income → Credit Score
- Industry → Salary multipliers
- Location → Cost of living adjustments
- Employment stability → Credit factors

### Employment Generator (`src/generators/employment_generator.py`)

Builds realistic employment histories:

**Features:**
- Career progression patterns
- Industry-specific job titles
- Seasonal hiring patterns
- Employment gaps and overlaps
- Salary progression over time

**Temporal Patterns:**
- Age-based career stages
- Industry migration patterns
- Economic cycle effects
- Promotion timelines

## Data Models

### Person Model Hierarchy

```
Person
├── Basic Demographics (name, age, gender, SSN)
├── Addresses[]
│   ├── Current Address
│   ├── Previous Addresses
│   ├── Billing Address
│   └── Shipping Address
├── Phone Numbers[]
│   ├── Mobile
│   ├── Home
│   └── Work
├── Email Addresses[]
│   ├── Personal
│   └── Work
├── Employment History[]
│   ├── Current Job
│   └── Previous Jobs
└── Financial Profile
    ├── Credit Information
    ├── Income Data
    └── Debt Profile
```

### Database Schema Design

The Azure SQL schema is optimized for analytics and performance:

**Normalization Strategy:**
- Person as central entity
- Related data in separate tables
- Foreign key relationships
- Optimized indexes for common queries

**Performance Considerations:**
- Bulk insert optimization
- Columnstore indexes for analytics
- Partitioning by date fields
- Compression for storage efficiency

## Performance Architecture

### Multiprocessing Strategy

```python
# Process allocation
processes = min(num_threads, cpu_count)
records_per_process = total_records // processes

# Work distribution
work_items = [(start_idx, count, batch_size, process_id) 
              for process in range(processes)]

# Parallel execution with imap_unordered
with Pool(processes=processes) as pool:
    for batch in pool.imap_unordered(generate_batch, work_items):
        yield batch
```

**Design Decisions:**
- Process-based parallelism for CPU-bound tasks
- Batch processing to minimize IPC overhead
- Memory management per process
- Fault tolerance with process isolation

### Memory Management

**Strategies:**
- Streaming generation to prevent memory buildup
- Configurable batch sizes based on available memory
- Generator patterns for lazy evaluation
- Memory monitoring and alerts

**Memory Optimization:**
```python
@contextmanager
def memory_monitor(threshold_mb=2000):
    def check_memory():
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        return current_memory < threshold_mb
    yield check_memory
```

### Database Performance

**Bulk Insert Optimization:**
- SQL Server fast_executemany
- Optimized batch sizes (1K-50K records)
- Transaction management
- Connection pooling

**Insert Strategy:**
```python
# Prepare bulk data
people_data = [person_to_tuple(p) for p in batch]
addresses_data = [addr_to_tuple(a, p.id) for p in batch for a in p.addresses]

# Bulk insert with executemany
cursor.executemany(people_sql, people_data)
cursor.executemany(addresses_sql, addresses_data)
```

## Extensibility Architecture

### Plugin System Design

The architecture supports extensibility through:

**1. Generator Interfaces:**
```python
class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, **kwargs) -> Any:
        pass
```

**2. Custom Variability Rules:**
```python
class CustomVariabilityEngine(VariabilityEngine):
    def custom_industry_patterns(self, value, industry):
        # Industry-specific data quality patterns
        pass
```

**3. Output Format Extensions:**
```python
class CustomOutputHandler:
    def write_parquet(self, data: List[Person], path: str):
        # Custom output format
        pass
```

### Configuration System

**Hierarchical Configuration:**
```yaml
# Base configuration
base_config.yaml

# Environment-specific overrides  
production_config.yaml:
  inherits: base_config.yaml
  overrides:
    num_threads: 16
    batch_size: 50000
```

**Runtime Configuration:**
- CLI argument precedence
- Environment variable support
- Configuration validation
- Hot reloading capabilities

## Quality Assurance

### Testing Strategy

**1. Unit Tests:**
- Individual generator testing
- Statistical validation
- Data quality verification
- Performance benchmarks

**2. Integration Tests:**
- End-to-end generation workflows
- Database integration testing
- Configuration validation
- CLI interface testing

**3. Performance Tests:**
- Load testing with large datasets
- Memory usage validation
- Database performance testing
- Concurrent generation testing

### Statistical Validation

**Distribution Testing:**
```python
def test_age_distribution():
    ages = [calculate_age(p.date_of_birth) for p in sample]
    
    # Chi-square test against census data
    chi2, p_value = stats.chisquare(observed_counts, expected_counts)
    assert p_value > 0.05  # Accept if statistically similar
```

**Correlation Testing:**
```python
def test_income_credit_correlation():
    data = [(p.financial.income, p.financial.credit_score) for p in sample]
    correlation, p_value = stats.pearsonr(*zip(*data))
    assert correlation > 0.3  # Positive correlation expected
```

## Security Considerations

### Data Protection

**1. No Real PII:**
- All data is synthetically generated
- No connection to real individuals
- Deterministic generation with seeds

**2. Database Security:**
- Connection string encryption
- SQL injection prevention
- Access control integration

**3. Data Retention:**
- Configurable data lifecycle
- Secure deletion capabilities
- Audit trail generation

### Privacy by Design

**Principles:**
- Synthetic data only
- No reverse engineering possible
- Configurable anonymization levels
- GDPR/CCPA compliance ready

## Monitoring and Observability

### Metrics Collection

**Performance Metrics:**
- Records generated per second
- Memory usage patterns
- Database insert rates
- Error rates and types

**Quality Metrics:**
- Data completeness rates
- Statistical distribution validation
- Correlation coefficient tracking
- Outlier detection rates

### Logging Strategy

**Structured Logging:**
```python
logger.info("Generation completed", extra={
    "records_generated": count,
    "duration_seconds": elapsed,
    "rate_per_second": rate,
    "memory_used_mb": memory_usage,
    "configuration": config_hash
})
```

**Log Levels:**
- DEBUG: Detailed generation steps
- INFO: Progress and completion
- WARN: Data quality issues
- ERROR: Generation failures

## Future Architecture Considerations

### Scalability Enhancements

**1. Distributed Generation:**
- Kubernetes deployment support
- Message queue integration
- Distributed coordination

**2. Cloud-Native Features:**
- Azure Functions integration
- Event-driven architecture
- Auto-scaling capabilities

**3. Real-Time Generation:**
- WebSocket streaming
- Real-time quality monitoring
- Dynamic configuration updates

### Advanced Features

**1. Machine Learning Integration:**
- Pattern learning from real data
- Anomaly detection in generated data
- Adaptive quality improvement

**2. Advanced Analytics:**
- Data lineage tracking
- Synthetic data validation
- Quality score calculation

**3. Integration Ecosystem:**
- REST API endpoints
- GraphQL interface
- Webhook notifications

This architecture provides a solid foundation for high-performance, scalable synthetic data generation while maintaining flexibility for future enhancements and integrations.