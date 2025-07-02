# PII Generator - High-Performance Synthetic Data Generator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Azure SQL](https://img.shields.io/badge/Azure%20SQL-Compatible-orange)](https://azure.microsoft.com/en-us/products/azure-sql/database/)

A high-performance Python application for generating massive amounts of realistic synthetic Personally Identifiable Information (PII) data. Perfect for testing data systems, developing privacy-preserving applications, and seeding databases with realistic test data.

## 🚀 Key Features

- **High Performance**: Generate 1 million+ records in under 5 minutes
- **Realistic Data**: Culturally diverse names, addresses, and demographics with real-world distributions
- **Comprehensive Profiles**: 30+ data types including employment, financial, medical, and social information
- **Data Quality**: Configurable error rates, duplicates, and inconsistencies to mimic real-world data
- **Multiple Interfaces**: Command-line tool, web UI, and Python API
- **Database Integration**: Direct Azure SQL/SQL Server integration with batch optimization
- **Streaming Mode**: Continuous data generation for real-time testing scenarios
- **Memory Efficient**: Process unlimited records with < 2GB memory usage

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Docker Setup](#docker-setup)
  - [Traditional Setup](#traditional-setup)
- [Usage](#-usage)
- [Data Types](#-data-types)
- [Configuration](#-configuration)
- [Performance](#-performance)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## 🏃 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/rupesh43210/generateSyntheticData.git
cd generateSyntheticData
docker-compose up -d

# Visit http://localhost:5001
```

### Traditional Setup
```bash
# One-line setup
curl -sSL https://raw.githubusercontent.com/rupesh43210/generateSyntheticData/main/setup.sh | bash

# Generate data via CLI
python pii_gen.py generate -n 1000 -o sample_data.csv

# Or use web interface
python web_app.py
# Visit http://localhost:5001
```

## 💻 Installation

### Docker Setup

The easiest way to get started is with Docker:

```bash
# Clone the repository
git clone https://github.com/rupesh43210/generateSyntheticData.git
cd generateSyntheticData

# Start all services (includes SQL Server)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f pii-generator
```

For detailed Docker instructions, see [DOCKER_README.md](DOCKER_README.md).

### Traditional Setup

#### Prerequisites

- Python 3.8 or higher
- SQL Server ODBC Driver 17 or 18 (for database features)
- 4GB RAM minimum (8GB recommended for large datasets)
- 10GB free disk space

#### Automated Setup

```bash
# Clone the repository
git clone https://github.com/rupesh43210/generateSyntheticData.git
cd generateSyntheticData

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup (Optional)

For Azure SQL Database:

1. Create an Azure SQL Database instance
2. Configure firewall rules to allow your IP
3. Update `.env` with connection details:

```bash
DB_SERVER=yourserver.database.windows.net
DB_DATABASE=yourdatabase
DB_USERNAME=yourusername
DB_PASSWORD=yourpassword
```

## 📖 Usage

### Command Line Interface

```bash
# Generate data to CSV
python pii_gen.py generate -n 10000 -o data.csv

# Generate with different quality profiles
python pii_gen.py generate -n 5000 --variability-profile messy -o messy_data.csv

# Test database connection
python pii_gen.py test-connection --server myserver --database mydb

# Create database schema
python pii_gen.py setup-schema
```

### Web Interface

```bash
# Standard web UI
python web_app.py

# Enhanced web UI with advanced features
python web_app_enhanced.py
```

Navigate to `http://localhost:5001` to access the interface.

### Python API

```python
from src.generators.person_generator import PersonGenerator

# Create generator
generator = PersonGenerator()

# Generate single person
person = generator.generate_person()
print(f"Name: {person.name.full_name}")
print(f"SSN: {person.ssn}")

# Generate batch
people = generator.generate_batch(1000)

# Export to CSV
generator.export_to_csv(people, "output.csv")
```

## 📊 Data Types

The generator creates comprehensive person profiles with the following data:

### Basic Information
- **Names**: First, middle, last, suffixes, nicknames
- **Demographics**: DOB, gender, ethnicity, nationality
- **Identifiers**: SSN, driver's license, passport number
- **Contact**: Multiple phone numbers, emails, addresses

### Extended Profile
- **Employment**: Job history, salary progression, skills
- **Financial**: Credit scores, bank accounts, income, debt
- **Medical**: Conditions, medications, allergies, insurance
- **Education**: Degrees, institutions, GPAs
- **Family**: Relationships, emergency contacts
- **Digital**: Social media, online accounts, devices
- **Lifestyle**: Hobbies, preferences, memberships
- **Travel**: History, frequent flyer numbers
- **Vehicles**: Ownership history, registration

### Data Quality Features
- **Typos**: Configurable error rates in names and addresses
- **Missing Data**: Realistic null patterns
- **Duplicates**: Intentional fuzzy duplicates
- **Inconsistencies**: Mismatched data across fields
- **Historical Data**: Address and employment history

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Database Connection
DB_SERVER=localhost
DB_DATABASE=TestDatabase
DB_USERNAME=sa
DB_PASSWORD=YourStrongPassword123!
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server

# Schema Settings
DB_SCHEMA=dbo
DB_TABLE_PREFIX=pii_
DB_TABLE_BEHAVIOR=create_if_not_exists

# Performance Settings
BATCH_SIZE=5000
MAX_WORKERS=8
MEMORY_LIMIT_MB=2048

# Data Quality
ERROR_RATE=0.02
DUPLICATE_RATE=0.05
NULL_RATE=0.10
```

### Configuration Files

Create custom configurations in YAML format:

```yaml
# configs/custom_config.yaml
generation:
  error_rates:
    typo_rate: 0.03
    missing_data_rate: 0.08
    duplicate_rate: 0.02
  
  demographics:
    age_distribution:
      18-25: 0.15
      26-35: 0.25
      36-45: 0.22
      46-55: 0.18
      56-65: 0.12
      65+: 0.08
    
    ethnicity_distribution:
      white: 0.60
      hispanic: 0.18
      black: 0.13
      asian: 0.06
      other: 0.03

performance:
  batch_size: 10000
  max_workers: 16
  streaming_rate: 1000
```

## 🚄 Performance

### Benchmarks

| Records | Time | Memory | CPU Cores |
|---------|------|---------|-----------|
| 10K | 3s | 150MB | 4 |
| 100K | 28s | 500MB | 8 |
| 1M | 4m 45s | 1.8GB | 16 |
| 10M | 48m | 2GB | 16 |

### Optimization Tips

1. **Batch Size**: Increase `BATCH_SIZE` for better throughput
2. **Workers**: Set `MAX_WORKERS` to CPU cores - 2
3. **Database**: Use bulk insert mode for large datasets
4. **Memory**: Enable streaming mode for unlimited datasets

## 🧹 Recent Updates (July 2025)

The project has been significantly cleaned up and simplified:
- **Consolidated codebase**: Removed duplicate implementations
- **Simplified Docker**: Single Dockerfile and docker-compose.yml
- **Organized structure**: Documentation in `docs/`, tests in `test_scripts/`
- **Improved imports**: Fixed all module references
- **Better defaults**: Works out-of-the-box with file output

## 🏗️ Architecture

```
├── src/
│   ├── core/               # Core models and utilities
│   │   ├── models.py       # Pydantic data models
│   │   ├── constants.py    # Configuration constants
│   │   └── validation.py   # Data validation
│   ├── generators/         # Data generators
│   │   ├── person_generator.py
│   │   ├── address_generator.py
│   │   ├── employment_generator.py
│   │   └── ...
│   └── db/                 # Database operations
│       ├── azure_sql.py    # SQL Server integration
│       └── bulk_insert.py  # Optimized bulk operations
├── configs/                # Configuration files
├── templates/              # Web UI templates
└── tests/                  # Test suite
```

## 🔧 API Documentation

### PersonGenerator

```python
class PersonGenerator:
    def __init__(self, config: Optional[Dict] = None):
        """Initialize generator with optional configuration."""
    
    def generate_person(self) -> Person:
        """Generate a single person with full profile."""
    
    def generate_batch(self, count: int) -> List[Person]:
        """Generate multiple people efficiently."""
    
    def stream_people(self, rate: int) -> Iterator[Person]:
        """Stream people at specified rate per second."""
```

### Database Manager

```python
class AzureSQLManager:
    def create_schema(self, force: bool = False):
        """Create database schema for all person tables."""
    
    def insert_batch(self, people: List[Person], batch_size: int = 5000):
        """Efficiently insert people in batches."""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics and row counts."""
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection (Optional)**
   - The app works without a database - it generates CSV/JSON files by default
   - For SQL Server support, install ODBC drivers:
   ```bash
   # Linux
   sudo apt-get install unixodbc msodbcsql18
   
   # macOS  
   brew install unixodbc msodbcsql18
   
   # Windows
   # Download from Microsoft website
   ```

2. **Memory Issues**
   - Enable streaming mode: `--stream`
   - Reduce batch size: `--batch-size 1000`
   - Increase system swap space

3. **Database Connection Failed**
   - Check firewall rules
   - Verify credentials in `.env`
   - Test with `sqlcmd` or Azure Data Studio

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Fork the repository
# Create your feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m 'Add some amazing feature'

# Push to the branch
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Faker](https://github.com/joke2k/faker) for base data generation
- Optimized for [Azure SQL Database](https://azure.microsoft.com/en-us/products/azure-sql/database/)
- UI powered by [Flask](https://flask.palletsprojects.com/)

## 📞 Support

- **Documentation**: [Wiki](https://github.com/rupesh43210/generateSyntheticData/wiki)
- **Issues**: [GitHub Issues](https://github.com/rupesh43210/generateSyntheticData/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rupesh43210/generateSyntheticData/discussions)

---

Made with ❤️ for the data engineering community