"""Database configuration management"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import yaml
import os


class ConnectionOptions(BaseModel):
    """Database connection options"""
    Encrypt: str = 'yes'
    TrustServerCertificate: str = 'no'
    Connection_Timeout: int = 30


class DatabaseConnection(BaseModel):
    """Database connection configuration"""
    connection_method: str = Field(default='individual_params', 
                                 description="'connection_string' or 'individual_params'")
    
    # Individual parameters
    server: Optional[str] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    port: int = 1433
    driver: str = 'ODBC Driver 18 for SQL Server'
    connection_options: ConnectionOptions = Field(default_factory=ConnectionOptions)
    
    # Direct connection string
    connection_string: Optional[str] = None
    
    def get_connection_string(self) -> str:
        """Generate connection string from configuration"""
        if self.connection_method == 'connection_string' and self.connection_string:
            return self.connection_string
        
        if self.connection_method == 'individual_params':
            if not all([self.server, self.database, self.username, self.password]):
                raise ValueError("Server, database, username, and password are required for individual_params method")
            
            # Build connection string
            conn_str = f"Driver={{{self.driver}}};Server={self.server},{self.port};Database={self.database};Uid={self.username};Pwd={self.password};"
            
            # Add connection options
            for key, value in self.connection_options.dict().items():
                conn_str += f"{key}={value};"
            
            return conn_str
        
        raise ValueError(f"Invalid connection_method: {self.connection_method}")


class SchemaConfig(BaseModel):
    """Schema configuration"""
    name: str = 'dbo'
    table_behavior: str = Field(default='create_if_not_exists',
                               description="'create_if_not_exists', 'drop_and_create', 'append_only'")
    table_prefix: str = ''
    
    tables: Dict[str, bool] = Field(default_factory=lambda: {
        'people': True,
        'addresses': True,
        'phone_numbers': True,
        'email_addresses': True,
        'employment_history': True,
        'financial_profiles': True
    })


class DataInsertionConfig(BaseModel):
    """Data insertion configuration"""
    mode: str = Field(default='append', description="'append', 'upsert', 'skip_duplicates'")
    batch_size: int = 1000
    duplicate_key_columns: Dict[str, list] = Field(default_factory=lambda: {
        'people': ['ssn'],
        'addresses': ['person_id', 'address_type', 'street_1', 'city', 'state', 'zip_code'],
        'phone_numbers': ['area_code', 'number'],
        'email_addresses': ['email']
    })


class DatabaseConfig(BaseModel):
    """Complete database configuration"""
    database: DatabaseConnection = Field(default_factory=DatabaseConnection)
    schema: SchemaConfig = Field(default_factory=SchemaConfig)
    data_insertion: DataInsertionConfig = Field(default_factory=DataInsertionConfig)
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'DatabaseConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Database connection from environment
        if os.getenv('DB_SERVER'):
            config.database.server = os.getenv('DB_SERVER')
        if os.getenv('DB_DATABASE'):
            config.database.database = os.getenv('DB_DATABASE')
        if os.getenv('DB_USERNAME'):
            config.database.username = os.getenv('DB_USERNAME')
        if os.getenv('DB_PASSWORD'):
            config.database.password = os.getenv('DB_PASSWORD')
        if os.getenv('DB_PORT'):
            config.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_CONNECTION_STRING'):
            config.database.connection_string = os.getenv('DB_CONNECTION_STRING')
            config.database.connection_method = 'connection_string'
        
        # Schema configuration
        if os.getenv('DB_SCHEMA'):
            config.schema.name = os.getenv('DB_SCHEMA')
        if os.getenv('DB_TABLE_BEHAVIOR'):
            config.schema.table_behavior = os.getenv('DB_TABLE_BEHAVIOR')
        if os.getenv('DB_TABLE_PREFIX'):
            config.schema.table_prefix = os.getenv('DB_TABLE_PREFIX')
        
        # Data insertion configuration
        if os.getenv('DB_INSERT_MODE'):
            config.data_insertion.mode = os.getenv('DB_INSERT_MODE')
        if os.getenv('DB_BATCH_SIZE'):
            config.data_insertion.batch_size = int(os.getenv('DB_BATCH_SIZE'))
        
        return config
    
    def get_table_name(self, base_name: str) -> str:
        """Get full table name with prefix"""
        return f"{self.schema.table_prefix}{base_name}"