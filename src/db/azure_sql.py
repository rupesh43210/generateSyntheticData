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


class AzureSQLDatabase:
    """Azure SQL Database operations with bulk insert optimization"""
    
    def __init__(self, connection_string: str, schema: str = "dbo"):
        self.connection_string = connection_string
        self.schema = schema
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
    
    def create_schema(self) -> bool:
        """Create database schema for PII data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            tables = self._get_table_definitions()
            
            try:
                for table_name, table_sql in tables.items():
                    self.logger.info(f"Creating table: {table_name}")
                    cursor.execute(f"IF OBJECT_ID('{self.schema}.{table_name}', 'U') IS NOT NULL DROP TABLE {self.schema}.{table_name}")
                    cursor.execute(table_sql)
                
                # Create indexes
                indexes = self._get_index_definitions()
                for index_sql in indexes:
                    cursor.execute(index_sql)
                
                conn.commit()
                self.logger.info("Database schema created successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error creating schema: {e}")
                conn.rollback()
                return False
    
    def bulk_insert_people(self, people: List[Person], batch_size: int = 1000) -> bool:
        """Bulk insert people and all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Process in batches
                for i in range(0, len(people), batch_size):
                    batch = people[i:i + batch_size]
                    self._insert_people_batch(cursor, batch)
                    
                    # Commit every batch
                    conn.commit()
                    self.logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error in bulk insert: {e}")
                conn.rollback()
                return False
    
    def bulk_insert_dataframe(self, df: pd.DataFrame, table_name: str, 
                            batch_size: int = 10000) -> bool:
        """Bulk insert from pandas DataFrame using SQL Server bulk copy"""
        try:
            with self.get_connection() as conn:
                # Use pandas to_sql with fast_executemany
                df.to_sql(
                    name=table_name,
                    con=conn,
                    schema=self.schema,
                    if_exists='append',
                    index=False,
                    chunksize=batch_size,
                    method='multi'
                )
                conn.commit()
                self.logger.info(f"Bulk inserted {len(df)} records to {table_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error in DataFrame bulk insert: {e}")
            return False
    
    def stream_insert(self, person_iterator: Iterator[Person], 
                     batch_size: int = 1000) -> int:
        """Stream insert with batching for memory efficiency"""
        total_inserted = 0
        batch = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                for person in person_iterator:
                    batch.append(person)
                    
                    if len(batch) >= batch_size:
                        self._insert_people_batch(cursor, batch)
                        conn.commit()
                        total_inserted += len(batch)
                        batch = []
                        
                        self.logger.info(f"Stream inserted {total_inserted} records")
                
                # Insert remaining batch
                if batch:
                    self._insert_people_batch(cursor, batch)
                    conn.commit()
                    total_inserted += len(batch)
                
                return total_inserted
                
            except Exception as e:
                self.logger.error(f"Error in stream insert: {e}")
                conn.rollback()
                return total_inserted
    
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
            for address in person.addresses:
                addresses_data.append(self._address_to_tuple(address, person.person_id))
            
            # Phone numbers
            for phone in person.phone_numbers:
                phones_data.append(self._phone_to_tuple(phone, person.person_id))
            
            # Email addresses
            for email in person.email_addresses:
                emails_data.append(self._email_to_tuple(email, person.person_id))
            
            # Employment history
            for employment in person.employment_history:
                employment_data.append(self._employment_to_tuple(employment, person.person_id))
            
            # Financial profile
            if person.financial_profile:
                financial_data.append(self._financial_to_tuple(person.financial_profile, person.person_id))
        
        # Bulk insert each table
        self._bulk_insert_table(cursor, 'people', people_data, self._get_people_columns())
        
        if addresses_data:
            self._bulk_insert_table(cursor, 'addresses', addresses_data, self._get_addresses_columns())
        
        if phones_data:
            self._bulk_insert_table(cursor, 'phone_numbers', phones_data, self._get_phones_columns())
        
        if emails_data:
            self._bulk_insert_table(cursor, 'email_addresses', emails_data, self._get_emails_columns())
        
        if employment_data:
            self._bulk_insert_table(cursor, 'employment_history', employment_data, self._get_employment_columns())
        
        if financial_data:
            self._bulk_insert_table(cursor, 'financial_profiles', financial_data, self._get_financial_columns())
    
    def _bulk_insert_table(self, cursor, table_name: str, data: List[tuple], columns: List[str]):
        """Perform bulk insert for a specific table"""
        if not data:
            return
        
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT INTO {self.schema}.{table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.executemany(sql, data)
    
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
        """Get SQL table definitions"""
        return {
            'people': f"""
                CREATE TABLE {self.schema}.people (
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
            """,
            'addresses': f"""
                CREATE TABLE {self.schema}.addresses (
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
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.people(person_id)
                )
            """,
            'phone_numbers': f"""
                CREATE TABLE {self.schema}.phone_numbers (
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
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.people(person_id)
                )
            """,
            'email_addresses': f"""
                CREATE TABLE {self.schema}.email_addresses (
                    email_id NVARCHAR(50) PRIMARY KEY,
                    person_id NVARCHAR(50) NOT NULL,
                    email NVARCHAR(255) NOT NULL,
                    email_type NVARCHAR(20) NOT NULL,
                    is_primary BIT DEFAULT 0,
                    is_valid BIT DEFAULT 1,
                    is_bounced BIT DEFAULT 0,
                    domain NVARCHAR(100),
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.people(person_id)
                )
            """,
            'employment_history': f"""
                CREATE TABLE {self.schema}.employment_history (
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
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.people(person_id)
                )
            """,
            'financial_profiles': f"""
                CREATE TABLE {self.schema}.financial_profiles (
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
                    FOREIGN KEY (person_id) REFERENCES {self.schema}.people(person_id)
                )
            """
        }
    
    def _get_index_definitions(self) -> List[str]:
        """Get index definitions for performance"""
        return [
            f"CREATE INDEX IX_people_dob ON {self.schema}.people(date_of_birth)",
            f"CREATE INDEX IX_people_last_name ON {self.schema}.people(last_name)",
            f"CREATE INDEX IX_people_ssn ON {self.schema}.people(ssn)",
            f"CREATE INDEX IX_addresses_person_id ON {self.schema}.addresses(person_id)",
            f"CREATE INDEX IX_addresses_zip ON {self.schema}.addresses(zip_code)",
            f"CREATE INDEX IX_addresses_city_state ON {self.schema}.addresses(city, state)",
            f"CREATE INDEX IX_phones_person_id ON {self.schema}.phone_numbers(person_id)",
            f"CREATE INDEX IX_emails_person_id ON {self.schema}.email_addresses(person_id)",
            f"CREATE INDEX IX_emails_domain ON {self.schema}.email_addresses(domain)",
            f"CREATE INDEX IX_employment_person_id ON {self.schema}.employment_history(person_id)",
            f"CREATE INDEX IX_employment_employer ON {self.schema}.employment_history(employer_name)",
            f"CREATE INDEX IX_financial_credit_score ON {self.schema}.financial_profiles(credit_score)"
        ]
    
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
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality and return statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.people")
            stats['total_people'] = cursor.fetchone()[0]
            
            # Missing data analysis
            cursor.execute(f"""
                SELECT 
                    SUM(CASE WHEN ssn IS NULL THEN 1 ELSE 0 END) as missing_ssn,
                    SUM(CASE WHEN middle_name IS NULL THEN 1 ELSE 0 END) as missing_middle_name,
                    COUNT(*) as total
                FROM {self.schema}.people
            """)
            row = cursor.fetchone()
            stats['missing_ssn_pct'] = (row[0] / row[2]) * 100 if row[2] > 0 else 0
            stats['missing_middle_name_pct'] = (row[1] / row[2]) * 100 if row[2] > 0 else 0
            
            # Age distribution
            cursor.execute(f"""
                SELECT 
                    AVG(DATEDIFF(year, date_of_birth, GETDATE())) as avg_age,
                    MIN(DATEDIFF(year, date_of_birth, GETDATE())) as min_age,
                    MAX(DATEDIFF(year, date_of_birth, GETDATE())) as max_age
                FROM {self.schema}.people
            """)
            row = cursor.fetchone()
            stats['avg_age'] = row[0]
            stats['min_age'] = row[1]
            stats['max_age'] = row[2]
            
            return stats