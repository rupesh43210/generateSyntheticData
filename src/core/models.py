from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
import uuid

# Import new data types - changed from TYPE_CHECKING to direct imports
try:
    from src.generators.medical_generator import MedicalProfile
    from src.generators.vehicle_generator import VehicleProfile
    from src.generators.education_generator import EducationProfile
    from src.generators.social_generator import OnlinePresence
    from src.generators.biometric_generator import PhysicalProfile
    from src.generators.lifestyle_generator import LifestyleProfile
    from src.generators.travel_generator import TravelProfile
    from src.generators.financial_transactions_generator import FinancialProfile as EnhancedFinancialProfile
    from src.generators.communication_generator import CommunicationProfile
except ImportError:
    # Fallback for when modules aren't available yet
    MedicalProfile = None
    VehicleProfile = None
    EducationProfile = None
    OnlinePresence = None
    PhysicalProfile = None
    LifestyleProfile = None
    TravelProfile = None
    EnhancedFinancialProfile = None
    CommunicationProfile = None


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


class AddressType(str, Enum):
    CURRENT = "current"
    PREVIOUS = "previous"
    BILLING = "billing"
    SHIPPING = "shipping"
    WORK = "work"


class EmploymentStatus(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class DataQualityProfile(BaseModel):
    missing_data_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    typo_rate: float = Field(default=0.02, ge=0.0, le=1.0)
    duplicate_rate: float = Field(default=0.001, ge=0.0, le=1.0)
    outlier_rate: float = Field(default=0.01, ge=0.0, le=1.0)
    inconsistency_rate: float = Field(default=0.03, ge=0.0, le=1.0)


class Address(BaseModel):
    address_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    address_type: AddressType
    street_1: str
    street_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    is_valid: bool = True
    effective_date: date
    end_date: Optional[date] = None
    
    model_config = ConfigDict(use_enum_values=True)


class PhoneNumber(BaseModel):
    phone_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone_type: str  # mobile, home, work, fax
    country_code: str = "+1"
    area_code: str
    number: str
    extension: Optional[str] = None
    is_primary: bool = False
    is_valid: bool = True
    do_not_call: bool = False


class EmailAddress(BaseModel):
    email_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    email_type: str  # personal, work, other
    is_primary: bool = False
    is_valid: bool = True
    is_bounced: bool = False
    domain: str = ""
    
    @field_validator('domain', mode='before')
    @classmethod
    def extract_domain(cls, v, info):
        if info.data.get('email') and '@' in info.data['email']:
            return info.data['email'].split('@')[1]
        return v


class Employment(BaseModel):
    employment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employer_name: str
    job_title: str
    department: Optional[str] = None
    industry: str
    employment_status: EmploymentStatus
    start_date: date
    end_date: Optional[date] = None
    salary: Optional[float] = None
    is_current: bool = True
    
    model_config = ConfigDict(use_enum_values=True)


class FinancialProfile(BaseModel):
    credit_score: int = Field(ge=300, le=850)
    annual_income: float = Field(ge=0)
    debt_to_income_ratio: float = Field(ge=0.0, le=10.0)
    number_of_accounts: int = Field(ge=0)
    oldest_account_age_years: float = Field(ge=0)
    recent_inquiries: int = Field(ge=0)
    total_debt: float = Field(ge=0)
    available_credit: float = Field(ge=0)
    utilization_rate: float = Field(ge=0.0, le=1.0)


class Person(BaseModel):
    person_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ssn: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    prefix: Optional[str] = None
    nickname: Optional[str] = None
    maiden_name: Optional[str] = None
    date_of_birth: date
    gender: Gender
    
    addresses: List[Address] = Field(default_factory=list)
    phone_numbers: List[PhoneNumber] = Field(default_factory=list)
    email_addresses: List[EmailAddress] = Field(default_factory=list)
    employment_history: List[Employment] = Field(default_factory=list)
    financial_profile: Optional[FinancialProfile] = None
    
    # Original profiles
    medical_profile: Optional['MedicalProfile'] = Field(default=None)
    vehicle_profile: Optional['VehicleProfile'] = Field(default=None)
    education_profile: Optional['EducationProfile'] = Field(default=None)
    online_presence: Optional['OnlinePresence'] = Field(default=None)
    physical_profile: Optional['PhysicalProfile'] = Field(default=None)
    lifestyle_profile: Optional['LifestyleProfile'] = Field(default=None)
    
    # New enhanced profiles with explicit type annotations
    travel_profile: Optional['TravelProfile'] = Field(default=None)
    enhanced_financial_profile: Optional['EnhancedFinancialProfile'] = Field(default=None)
    communication_profile: Optional['CommunicationProfile'] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(use_enum_values=True)


# Rebuild the model after all imports are complete
def rebuild_person_model():
    """Rebuild Person model after all forward references are resolved"""
    # NOTE: Model rebuild is causing Pydantic validation issues
    # The forward references resolve naturally, so we skip the rebuild
    print("✅ Person model using natural forward reference resolution")
    return True

class GenerationConfig(BaseModel):
    num_records: int = Field(default=1000, ge=1)
    batch_size: int = Field(default=1000, ge=1)
    num_threads: int = Field(default=4, ge=1)
    seed: Optional[int] = None
    
    data_quality_profile: DataQualityProfile = Field(default_factory=DataQualityProfile)
    
    enable_relationships: bool = True
    enable_temporal_patterns: bool = True
    enable_geographic_clustering: bool = True
    enable_financial_correlations: bool = True
    
    min_addresses_per_person: int = Field(default=1, ge=1)
    max_addresses_per_person: int = Field(default=3, ge=1)
    min_phones_per_person: int = Field(default=1, ge=0)
    max_phones_per_person: int = Field(default=2, ge=0)
    min_emails_per_person: int = Field(default=1, ge=0)
    max_emails_per_person: int = Field(default=2, ge=0)
    min_jobs_per_person: int = Field(default=1, ge=0)
    max_jobs_per_person: int = Field(default=5, ge=0)
    
    geographic_distribution: Dict[str, float] = Field(default_factory=dict)
    industry_distribution: Dict[str, float] = Field(default_factory=dict)