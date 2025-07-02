# Project Structure

```
generateSyntheticData/
│
├── src/                        # Source code
│   ├── core/                   # Core functionality
│   │   ├── constants.py        # Application constants
│   │   ├── database_config.py  # Database configuration
│   │   ├── error_handling.py   # Error handling utilities
│   │   ├── models.py          # Pydantic data models
│   │   ├── performance.py     # Performance optimization
│   │   ├── progress_tracker.py # Progress tracking
│   │   ├── validation.py      # Data validation
│   │   └── variability.py     # Data variability settings
│   │
│   ├── db/                    # Database operations
│   │   └── azure_sql.py       # Azure SQL/SQL Server interface
│   │
│   └── generators/            # Data generators
│       ├── person_generator.py     # Main person generator
│       ├── name_generator.py       # Name generation
│       ├── address_generator.py    # Address generation
│       ├── contact_generator.py    # Phone/email generation
│       ├── employment_generator.py # Employment data
│       ├── financial_generator.py  # Financial profiles
│       ├── medical_generator.py    # Medical records
│       └── ...                     # Other generators
│
├── templates/                 # Web UI templates
│   └── index.html            # Main web interface
│
├── configs/                   # Configuration files
│   ├── database_config.yaml  # Database settings
│   ├── realistic_config.yaml # Realistic data profile
│   └── high_performance_config.yaml
│
├── scripts/                   # Utility scripts
│   └── init-db.sql           # Database initialization
│
├── tests/                     # Unit tests
│   └── test_generators.py    # Generator tests
│
├── test_scripts/             # Development test scripts
│   ├── test_generation.py
│   ├── test_web_app.py
│   └── ...
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md      # System architecture
│   ├── DATABASE_SETUP_GUIDE.md
│   ├── DOCKER_README.md     # Docker instructions
│   └── ...
│
├── output/                   # Generated data output (git ignored)
├── logs/                     # Application logs (git ignored)
│
├── pii_gen.py               # CLI entry point
├── web_app.py               # Web interface entry point
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation
├── setup.sh                 # Automated setup script
├── verify_setup.sh          # Setup verification
├── test_docker.sh           # Docker testing
│
├── Dockerfile               # Full Docker image (with SQL drivers)
├── Dockerfile.lite          # Lightweight Docker image
├── docker-compose.yml       # Full stack composition
├── docker-compose.lite.yml  # Lightweight composition
├── docker-compose.override.yml # Development override
├── docker-entrypoint.sh     # Container entry point
│
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── README.md               # Main documentation
└── PROJECT_STRUCTURE.md    # This file
```

## Key Directories

- **`src/`** - All source code, organized by functionality
- **`configs/`** - YAML configuration files for different scenarios
- **`docs/`** - Detailed documentation
- **`test_scripts/`** - Development and testing scripts
- **`templates/`** - Web UI templates

## Entry Points

1. **CLI**: `python pii_gen.py` - Command-line interface
2. **Web**: `python web_app.py` - Web interface on port 5001
3. **Docker**: Various docker-compose files for different deployment scenarios

## Generated/Runtime Directories (Git Ignored)

- **`output/`** - Generated CSV/JSON files
- **`logs/`** - Application logs
- **`venv/`** - Python virtual environment
- **`__pycache__/`** - Python bytecode cache