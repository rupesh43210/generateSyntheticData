#!/usr/bin/env python3
"""Test creating a fresh model definition"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# Import all profile classes
from src.generators.medical_generator import MedicalProfile
from src.generators.vehicle_generator import VehicleProfile  
from src.generators.education_generator import EducationProfile
from src.generators.social_generator import OnlinePresence
from src.generators.biometric_generator import PhysicalProfile
from src.generators.lifestyle_generator import LifestyleProfile
from src.generators.travel_generator import TravelProfile
from src.generators.financial_transactions_generator import FinancialProfile as EnhancedFinancialProfile
from src.generators.communication_generator import CommunicationProfile

# Import base types
from src.core.models import Gender, Address, PhoneNumber, EmailAddress, Employment, FinancialProfile

class FreshPerson(BaseModel):
    """Fresh Person model with explicit field definitions"""
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
    
    # Original profiles that were working
    medical_profile: Optional[MedicalProfile] = Field(default=None)
    vehicle_profile: Optional[VehicleProfile] = Field(default=None)
    education_profile: Optional[EducationProfile] = Field(default=None)
    online_presence: Optional[OnlinePresence] = Field(default=None)
    physical_profile: Optional[PhysicalProfile] = Field(default=None)
    lifestyle_profile: Optional[LifestyleProfile] = Field(default=None)
    
    # New enhanced profiles
    travel_profile: Optional[TravelProfile] = Field(default=None)
    enhanced_financial_profile: Optional[EnhancedFinancialProfile] = Field(default=None)
    communication_profile: Optional[CommunicationProfile] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True

# Test the fresh model
print("Testing fresh model...")

try:
    # Test basic creation
    person = FreshPerson(
        first_name='Test',
        last_name='User',
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE
    )
    print("✅ Basic fresh person creation works")
    
    # Test with new profiles
    from src.generators.travel_generator import TravelGenerator
    from src.generators.financial_transactions_generator import FinancialTransactionsGenerator
    from src.generators.communication_generator import CommunicationGenerator
    
    travel_gen = TravelGenerator()
    travel_profile = travel_gen.generate_travel_profile(30, 50000, 'average')
    
    financial_gen = FinancialTransactionsGenerator()
    financial_profile = financial_gen.generate_financial_profile(30, 50000, 700, 'average')
    
    comm_gen = CommunicationGenerator()
    comm_profile = comm_gen.generate_communication_profile(30, 'Software Engineer', 'average', 'San Francisco, CA')
    
    person_with_profiles = FreshPerson(
        first_name='Test',
        last_name='User',
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        travel_profile=travel_profile,
        enhanced_financial_profile=financial_profile,
        communication_profile=comm_profile
    )
    print("✅ Fresh person with all new profiles works!")
    
    print(f"Travel trips: {person_with_profiles.travel_profile.total_trips}")
    print(f"Net worth: ${person_with_profiles.enhanced_financial_profile.net_worth}")
    print(f"Contacts: {person_with_profiles.communication_profile.total_contacts}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()