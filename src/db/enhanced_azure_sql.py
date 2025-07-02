"""Enhanced Azure SQL Database operations with flexible configuration"""

import pyodbc
import pandas as pd
from typing import List, Optional, Dict, Any, Iterator
import logging
from contextlib import contextmanager
import time
from dataclasses import asdict
import json
from datetime import datetime, date

from src.core.models import Person, Address, PhoneNumber, EmailAddress, Employment, FinancialProfile
from src.core.database_config import DatabaseConfig


class EnhancedAzureSQLDatabase:
    """Enhanced Azure SQL Database operations with flexible configuration"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_string = config.database.get_connection_string()
        self.schema = config.schema.name
        self.logger = logging.getLogger(__name__)
        
        # SQL Server bulk insert settings
        self.bulk_options = {
            'fast_executemany': True,
            'autocommit': False
        }
        
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string, **self.bulk_options)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.logger.info("Database connection successful")
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def setup_schema(self) -> bool:
        """Setup database schema based on configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if self.config.schema.table_behavior == 'drop_and_create':
                    self._drop_all_tables(cursor)
                    self._create_all_tables(cursor)
                elif self.config.schema.table_behavior == 'create_if_not_exists':
                    self._create_tables_if_not_exist(cursor)
                elif self.config.schema.table_behavior == 'append_only':
                    # Just verify tables exist
                    if not self._verify_tables_exist(cursor):
                        self.logger.error("Tables don't exist and table_behavior is 'append_only'")
                        return False
                
                # Create indexes if tables were created
                if self.config.schema.table_behavior in ['drop_and_create', 'create_if_not_exists']:
                    self._create_indexes(cursor)
                
                conn.commit()
                self.logger.info("Database schema setup completed successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error setting up schema: {e}")
                conn.rollback()
                return False
    
    def _verify_tables_exist(self, cursor) -> bool:
        """Verify all required tables exist"""
        for table_name, enabled in self.config.schema.tables.items():
            if enabled:
                full_table_name = self.config.get_table_name(table_name)
                cursor.execute(f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                """, self.schema, full_table_name)
                
                if cursor.fetchone()[0] == 0:
                    self.logger.error(f"Required table {full_table_name} does not exist")
                    return False
        return True
    
    def _create_tables_if_not_exist(self, cursor):
        """Create tables only if they don't exist"""
        tables = self._get_table_definitions()
        
        for table_name, table_sql in tables.items():
            if self.config.schema.tables.get(table_name.replace(self.config.schema.table_prefix, ''), True):
                # Check if table exists
                cursor.execute(f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                """, self.schema, table_name)
                
                if cursor.fetchone()[0] == 0:
                    self.logger.info(f"Creating table: {table_name}")
                    cursor.execute(table_sql)
                else:
                    self.logger.info(f"Table {table_name} already exists, skipping creation")
    
    def _drop_all_tables(self, cursor):
        """Drop all tables (in correct order due to foreign keys)"""
        tables_to_drop = [
            'financial_profiles',
            'employment_history', 
            'email_addresses',
            'phone_numbers',
            'addresses',
            'people'
        ]
        
        for table_name in tables_to_drop:
            if self.config.schema.tables.get(table_name, True):
                full_table_name = self.config.get_table_name(table_name)
                cursor.execute(f"IF OBJECT_ID('{self.schema}.{full_table_name}', 'U') IS NOT NULL DROP TABLE {self.schema}.{full_table_name}")
                self.logger.info(f"Dropped table: {full_table_name}")
    
    def _create_all_tables(self, cursor):
        """Create all enabled tables"""
        tables = self._get_table_definitions()
        
        for table_name, table_sql in tables.items():
            base_name = table_name.replace(self.config.schema.table_prefix, '')
            if self.config.schema.tables.get(base_name, True):
                self.logger.info(f"Creating table: {table_name}")
                cursor.execute(table_sql)
    
    def _create_indexes(self, cursor):
        """Create indexes for performance"""
        indexes = self._get_index_definitions()
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                self.logger.warning(f"Failed to create index: {e}")
    
    def bulk_insert_people(self, people: List[Person], batch_size: Optional[int] = None) -> bool:
        """Bulk insert people and all related data"""
        batch_size = batch_size or self.config.data_insertion.batch_size
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Process in batches
                for i in range(0, len(people), batch_size):
                    batch = people[i:i + batch_size]
                    
                    if self.config.data_insertion.mode == 'skip_duplicates':
                        batch = self._filter_duplicates(cursor, batch)
                    
                    if batch:  # Only insert if there are records to insert
                        self._insert_people_batch(cursor, batch)
                        
                        # Commit every batch
                        conn.commit()
                        self.logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error in bulk insert: {e}")
                conn.rollback()
                return False
    
    def _filter_duplicates(self, cursor, people: List[Person]) -> List[Person]:
        """Filter out duplicate people based on configured key columns"""
        if not self.config.data_insertion.duplicate_key_columns.get('people'):
            return people
        
        key_columns = self.config.data_insertion.duplicate_key_columns['people']
        table_name = self.config.get_table_name('people')
        
        filtered_people = []
        
        for person in people:
            # Build WHERE clause for duplicate check
            where_conditions = []
            values = []
            
            for col in key_columns:
                if col == 'ssn':
                    where_conditions.append(f"{col} = ?")
                    values.append(person.ssn)
            
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.{table_name} WHERE {where_clause}", values)
                
                if cursor.fetchone()[0] == 0:
                    filtered_people.append(person)
                else:
                    self.logger.debug(f"Skipping duplicate person: {person.person_id}")
        
        return filtered_people
    
    def _insert_people_batch(self, cursor, people: List[Person]):
        """Insert a batch of people and related data"""
        # Prepare data for bulk insert
        people_data = []
        addresses_data = []
        phones_data = []
        emails_data = []
        employment_data = []
        financial_data = []
        
        for person in people:
            # Person data
            people_data.append(self._person_to_tuple(person))
            
            # Addresses
            if self.config.schema.tables.get('addresses', True):
                for address in person.addresses:
                    addresses_data.append(self._address_to_tuple(address, person.person_id))
            
            # Phone numbers
            if self.config.schema.tables.get('phone_numbers', True):
                for phone in person.phone_numbers:
                    phones_data.append(self._phone_to_tuple(phone, person.person_id))
            
            # Email addresses
            if self.config.schema.tables.get('email_addresses', True):
                for email in person.email_addresses:
                    emails_data.append(self._email_to_tuple(email, person.person_id))
            
            # Employment history
            if self.config.schema.tables.get('employment_history', True):
                for employment in person.employment_history:
                    employment_data.append(self._employment_to_tuple(employment, person.person_id))
            
            # Financial profile
            if self.config.schema.tables.get('financial_profiles', True) and person.financial_profile:
                financial_data.append(self._financial_to_tuple(person.financial_profile, person.person_id))
        
        # Bulk insert each table
        if self.config.schema.tables.get('people', True):
            self._bulk_insert_table(cursor, 'people', people_data, self._get_people_columns())
        
        if addresses_data and self.config.schema.tables.get('addresses', True):
            self._bulk_insert_table(cursor, 'addresses', addresses_data, self._get_addresses_columns())
        
        if phones_data and self.config.schema.tables.get('phone_numbers', True):
            self._bulk_insert_table(cursor, 'phone_numbers', phones_data, self._get_phones_columns())
        
        if emails_data and self.config.schema.tables.get('email_addresses', True):
            self._bulk_insert_table(cursor, 'email_addresses', emails_data, self._get_emails_columns())
        
        if employment_data and self.config.schema.tables.get('employment_history', True):
            self._bulk_insert_table(cursor, 'employment_history', employment_data, self._get_employment_columns())
        
        if financial_data and self.config.schema.tables.get('financial_profiles', True):
            self._bulk_insert_table(cursor, 'financial_profiles', financial_data, self._get_financial_columns())
    
    def _bulk_insert_table(self, cursor, table_name: str, data: List[tuple], columns: List[str]):
        """Perform bulk insert for a specific table"""
        if not data:
            return
        
        full_table_name = self.config.get_table_name(table_name)
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT INTO {self.schema}.{full_table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.executemany(sql, data)
    
    # Data conversion methods (same as original)
    def _person_to_tuple(self, person: Person) -> tuple:
        """Convert Person to tuple for bulk insert"""
        return (
            person.person_id,
            person.ssn,
            person.first_name,
            person.middle_name,
            person.last_name,
            person.suffix,
            person.prefix,
            person.nickname,
            person.maiden_name,
            person.date_of_birth,
            person.gender.value,
            person.created_at,
            person.updated_at
        )
    
    def _address_to_tuple(self, address: Address, person_id: str) -> tuple:
        """Convert Address to tuple for bulk insert"""
        return (
            address.address_id,
            person_id,
            address.address_type.value,
            address.street_1,
            address.street_2,
            address.city,
            address.state,
            address.zip_code,
            address.country,
            address.is_valid,
            address.effective_date,
            address.end_date
        )
    
    def _phone_to_tuple(self, phone: PhoneNumber, person_id: str) -> tuple:
        """Convert PhoneNumber to tuple for bulk insert"""
        return (
            phone.phone_id,
            person_id,
            phone.phone_type,
            phone.country_code,
            phone.area_code,
            phone.number,
            phone.extension,
            phone.is_primary,
            phone.is_valid,
            phone.do_not_call
        )
    
    def _email_to_tuple(self, email: EmailAddress, person_id: str) -> tuple:
        """Convert EmailAddress to tuple for bulk insert"""
        return (
            email.email_id,
            person_id,
            email.email,
            email.email_type,
            email.is_primary,
            email.is_valid,
            email.is_bounced,
            email.domain
        )
    
    def _employment_to_tuple(self, employment: Employment, person_id: str) -> tuple:
        """Convert Employment to tuple for bulk insert"""
        return (
            employment.employment_id,
            person_id,
            employment.employer_name,
            employment.job_title,
            employment.department,
            employment.industry,
            employment.employment_status.value,
            employment.start_date,
            employment.end_date,
            employment.salary,
            employment.is_current
        )
    
    def _financial_to_tuple(self, financial: FinancialProfile, person_id: str) -> tuple:
        """Convert FinancialProfile to tuple for bulk insert"""
        return (
            person_id,
            financial.credit_score,
            financial.annual_income,
            financial.debt_to_income_ratio,
            financial.number_of_accounts,
            financial.oldest_account_age_years,
            financial.recent_inquiries,
            financial.total_debt,
            financial.available_credit,
            financial.utilization_rate
        )
    
    def _get_table_definitions(self) -> Dict[str, str]:
        """Get SQL table definitions with configured table names"""
        tables = {}
        
        if self.config.schema.tables.get('people', True):
            tables[self.config.get_table_name('people')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('people')} (
                    person_id NVARCHAR(50) PRIMARY KEY,
                    ssn NVARCHAR(15),
                    first_name NVARCHAR(100) NOT NULL,
                    middle_name NVARCHAR(100),
                    last_name NVARCHAR(100) NOT NULL,
                    suffix NVARCHAR(20),
                    prefix NVARCHAR(20),
                    nickname NVARCHAR(100),
                    maiden_name NVARCHAR(100),
                    date_of_birth DATE NOT NULL,
                    gender CHAR(1) NOT NULL,
                    created_at DATETIME2 DEFAULT GETUTCDATE(),
                    updated_at DATETIME2 DEFAULT GETUTCDATE()
                )
            """
        
        if self.config.schema.tables.get('addresses', True):
            tables[self.config.get_table_name('addresses')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('addresses')} (
                    address_id NVARCHAR(50) PRIMARY KEY,
                    person_id NVARCHAR(50) NOT NULL,
                    address_type NVARCHAR(20) NOT NULL,
                    street_1 NVARCHAR(200) NOT NULL,
                    street_2 NVARCHAR(200),
                    city NVARCHAR(100) NOT NULL,
                    state NVARCHAR(10) NOT NULL,
                    zip_code NVARCHAR(20) NOT NULL,
                    country NVARCHAR(50) DEFAULT 'USA',
                    is_valid BIT DEFAULT 1,
                    effective_date DATE NOT NULL,
                    end_date DATE,
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.{self.config.get_table_name('people')}(person_id)
                )
            """
        
        if self.config.schema.tables.get('phone_numbers', True):
            tables[self.config.get_table_name('phone_numbers')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('phone_numbers')} (
                    phone_id NVARCHAR(50) PRIMARY KEY,
                    person_id NVARCHAR(50) NOT NULL,
                    phone_type NVARCHAR(20) NOT NULL,
                    country_code NVARCHAR(5) DEFAULT '+1',
                    area_code NVARCHAR(5) NOT NULL,
                    number NVARCHAR(20) NOT NULL,
                    extension NVARCHAR(10),
                    is_primary BIT DEFAULT 0,
                    is_valid BIT DEFAULT 1,
                    do_not_call BIT DEFAULT 0,
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.{self.config.get_table_name('people')}(person_id)
                )
            """
        
        if self.config.schema.tables.get('email_addresses', True):
            tables[self.config.get_table_name('email_addresses')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('email_addresses')} (
                    email_id NVARCHAR(50) PRIMARY KEY,
                    person_id NVARCHAR(50) NOT NULL,
                    email NVARCHAR(255) NOT NULL,
                    email_type NVARCHAR(20) NOT NULL,
                    is_primary BIT DEFAULT 0,
                    is_valid BIT DEFAULT 1,
                    is_bounced BIT DEFAULT 0,
                    domain NVARCHAR(100),
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.{self.config.get_table_name('people')}(person_id)
                )
            """
        
        if self.config.schema.tables.get('employment_history', True):
            tables[self.config.get_table_name('employment_history')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('employment_history')} (
                    employment_id NVARCHAR(50) PRIMARY KEY,
                    person_id NVARCHAR(50) NOT NULL,
                    employer_name NVARCHAR(200) NOT NULL,
                    job_title NVARCHAR(200) NOT NULL,
                    department NVARCHAR(100),
                    industry NVARCHAR(100) NOT NULL,
                    employment_status NVARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    salary DECIMAL(12,2),
                    is_current BIT DEFAULT 0,
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.{self.config.get_table_name('people')}(person_id)
                )
            """
        
        if self.config.schema.tables.get('financial_profiles', True):
            tables[self.config.get_table_name('financial_profiles')] = f"""
                CREATE TABLE {self.schema}.{self.config.get_table_name('financial_profiles')} (
                    person_id NVARCHAR(50) PRIMARY KEY,
                    credit_score INT NOT NULL,
                    annual_income DECIMAL(12,2) NOT NULL,
                    debt_to_income_ratio DECIMAL(5,4) NOT NULL,
                    number_of_accounts INT NOT NULL,
                    oldest_account_age_years DECIMAL(5,2) NOT NULL,
                    recent_inquiries INT NOT NULL,
                    total_debt DECIMAL(12,2) NOT NULL,
                    available_credit DECIMAL(12,2) NOT NULL,
                    utilization_rate DECIMAL(5,4) NOT NULL,
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.{self.config.get_table_name('people')}(person_id)
                )
            """
        
        return tables
    
    def _get_index_definitions(self) -> List[str]:
        """Get index definitions for performance"""
        indexes = []
        
        if self.config.schema.tables.get('people', True):
            people_table = self.config.get_table_name('people')
            indexes.extend([
                f"CREATE INDEX IX_{people_table}_dob ON {self.schema}.{people_table}(date_of_birth)",
                f"CREATE INDEX IX_{people_table}_last_name ON {self.schema}.{people_table}(last_name)",
                f"CREATE INDEX IX_{people_table}_ssn ON {self.schema}.{people_table}(ssn)",
            ])
        
        if self.config.schema.tables.get('addresses', True):
            addresses_table = self.config.get_table_name('addresses')
            indexes.extend([
                f"CREATE INDEX IX_{addresses_table}_person_id ON {self.schema}.{addresses_table}(person_id)",
                f"CREATE INDEX IX_{addresses_table}_zip ON {self.schema}.{addresses_table}(zip_code)",
                f"CREATE INDEX IX_{addresses_table}_city_state ON {self.schema}.{addresses_table}(city, state)",
            ])
        
        # Add other index definitions as needed...
        
        return indexes
    
    # Column definitions (same as original)
    def _get_people_columns(self) -> List[str]:
        return ['person_id', 'ssn', 'first_name', 'middle_name', 'last_name', 'suffix', 
                'prefix', 'nickname', 'maiden_name', 'date_of_birth', 'gender', 
                'created_at', 'updated_at']
    
    def _get_addresses_columns(self) -> List[str]:
        return ['address_id', 'person_id', 'address_type', 'street_1', 'street_2', 
                'city', 'state', 'zip_code', 'country', 'is_valid', 'effective_date', 'end_date']
    
    def _get_phones_columns(self) -> List[str]:
        return ['phone_id', 'person_id', 'phone_type', 'country_code', 'area_code', 
                'number', 'extension', 'is_primary', 'is_valid', 'do_not_call']
    
    def _get_emails_columns(self) -> List[str]:
        return ['email_id', 'person_id', 'email', 'email_type', 'is_primary', 
                'is_valid', 'is_bounced', 'domain']
    
    def _get_employment_columns(self) -> List[str]:
        return ['employment_id', 'person_id', 'employer_name', 'job_title', 'department', 
                'industry', 'employment_status', 'start_date', 'end_date', 'salary', 'is_current']
    
    def _get_financial_columns(self) -> List[str]:
        return ['person_id', 'credit_score', 'annual_income', 'debt_to_income_ratio', 
                'number_of_accounts', 'oldest_account_age_years', 'recent_inquiries', 
                'total_debt', 'available_credit', 'utilization_rate']