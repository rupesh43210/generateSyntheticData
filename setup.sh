#!/bin/bash

# PII Generator - Comprehensive Setup Script
# This script sets up the complete environment for the PII Generator project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Main setup function
main() {
    echo "=================================================="
    echo "     PII Generator - Setup Script v1.0"
    echo "=================================================="
    echo ""

    OS=$(detect_os)
    print_status "Detected OS: $OS"

    # Step 1: Check Python version
    print_status "Checking Python version..."
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $PYTHON_VERSION is installed, but version $REQUIRED_VERSION or higher is required."
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION is installed"

    # Step 2: Check for ODBC driver
    print_status "Checking for ODBC drivers..."
    if [[ "$OS" == "linux" ]]; then
        if ! command_exists odbcinst; then
            print_warning "ODBC tools not found. Installing..."
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y unixodbc unixodbc-dev
            elif command_exists yum; then
                sudo yum install -y unixODBC unixODBC-devel
            else
                print_error "Cannot install ODBC tools automatically. Please install unixODBC manually."
                exit 1
            fi
        fi
        
        # Check for SQL Server ODBC driver
        if ! odbcinst -q -d | grep -q "ODBC Driver 1[78] for SQL Server"; then
            print_warning "SQL Server ODBC driver not found. Would you like to install it? (y/n)"
            read -r response
            if [[ "$response" == "y" ]]; then
                # Install Microsoft ODBC driver
                curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
                curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
                sudo apt-get update
                sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
            fi
        fi
    elif [[ "$OS" == "macos" ]]; then
        if ! command_exists brew; then
            print_warning "Homebrew not found. Installing Homebrew is recommended for ODBC driver installation."
            print_status "Visit https://brew.sh for installation instructions."
        else
            if ! brew list unixodbc &>/dev/null; then
                print_status "Installing unixODBC..."
                brew install unixodbc
            fi
            if ! brew list msodbcsql18 &>/dev/null; then
                print_warning "SQL Server ODBC driver not found. Would you like to install it? (y/n)"
                read -r response
                if [[ "$response" == "y" ]]; then
                    brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
                    brew update
                    HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql18
                fi
            fi
        fi
    elif [[ "$OS" == "windows" ]]; then
        print_status "Please ensure ODBC Driver 17 or 18 for SQL Server is installed."
        print_status "Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
    fi

    # Step 3: Create virtual environment
    print_status "Creating Python virtual environment..."
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Would you like to recreate it? (y/n)"
        read -r response
        if [[ "$response" == "y" ]]; then
            rm -rf venv
            python3 -m venv venv
        fi
    else
        python3 -m venv venv
    fi
    print_success "Virtual environment created"

    # Step 4: Activate virtual environment
    print_status "Activating virtual environment..."
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi

    # Step 5: Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip

    # Step 6: Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"

    # Step 7: Install package in development mode
    print_status "Installing PII Generator package..."
    pip install -e .
    print_success "Package installed"

    # Step 8: Create .env file
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your database credentials"
    else
        print_status ".env file already exists"
    fi

    # Step 9: Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p output
    mkdir -p data/cache
    print_success "Directories created"

    # Step 10: Test database connection (optional)
    print_status "Would you like to test the database connection? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        print_status "Testing database connection..."
        python3 -c "
from src.db.azure_sql import AzureSQLManager
import os
from dotenv import load_dotenv

load_dotenv()

try:
    manager = AzureSQLManager(
        server=os.getenv('DB_SERVER', 'localhost'),
        database=os.getenv('DB_DATABASE', 'TestDatabase'),
        username=os.getenv('DB_USERNAME', 'sa'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', '1433'))
    )
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    print('Please check your .env file and database settings.')
"
    fi

    # Step 11: Display next steps
    echo ""
    echo "=================================================="
    echo "              Setup Complete!"
    echo "=================================================="
    echo ""
    print_success "PII Generator has been successfully set up!"
    echo ""
    echo "Next steps:"
    echo "1. Edit the .env file with your database credentials"
    echo "2. Run the CLI tool: python pii_gen.py --help"
    echo "3. Start the web interface: python web_app.py"
    echo "4. Or use the enhanced web interface: python web_app_enhanced.py"
    echo ""
    echo "Quick start examples:"
    echo "  - Generate 1000 records to CSV: python pii_gen.py generate --count 1000 --output data.csv"
    echo "  - Create database schema: python pii_gen.py create-schema"
    echo "  - Stream data to database: python pii_gen.py stream --rate 100"
    echo ""
    print_status "To activate the virtual environment in the future, run:"
    if [[ "$OS" == "windows" ]]; then
        echo "  source venv/Scripts/activate"
    else
        echo "  source venv/bin/activate"
    fi
}

# Run main function
main