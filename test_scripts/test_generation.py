#!/usr/bin/env python3
"""Test script for person generation"""

# Import all model classes to ensure they're loaded before rebuilding
from src.generators.medical_generator import MedicalProfile
from src.generators.vehicle_generator import VehicleProfile  
from src.generators.education_generator import EducationProfile
from src.generators.social_generator import OnlinePresence
from src.generators.biometric_generator import PhysicalProfile
from src.generators.lifestyle_generator import LifestyleProfile

from src.core.models import GenerationConfig, DataQualityProfile, Person
from src.core.performance import PerformanceOptimizer
from src.generators.person_generator import PersonGenerator

# Rebuild Person model after all imports
Person.model_rebuild()

def test_generation():
    """Test basic person generation"""
    config = GenerationConfig(
        num_records=3, 
        batch_size=3, 
        num_threads=1, 
        data_quality_profile=DataQualityProfile()
    )
    
    gen = PersonGenerator(config)
    
    try:
        person = gen.generate_person()
        print("✓ Generated person successfully!")
        print(f"  Name: {person.first_name} {person.last_name}")
        print(f"  Age: {2024 - person.date_of_birth.year}")
        print(f"  Gender: {person.gender}")
        if person.physical_profile:
            print(f"  Height: {person.physical_profile.physical_characteristics.height_ft_in}")
        if person.medical_profile:
            print(f"  Blood Type: {person.medical_profile.blood_type}")
        return True
    except Exception as e:
        print(f"✗ Error generating person: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generation()
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed!")