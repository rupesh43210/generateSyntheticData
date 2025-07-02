#!/usr/bin/env python3
"""Debug Person creation step by step"""

from src.generators.person_generator import PersonGenerator
from src.core.models import GenerationConfig, Person, Gender
from datetime import date

print('Debugging Person creation...')

try:
    config = GenerationConfig(num_records=1, batch_size=1, num_threads=1)
    generator = PersonGenerator(config)
    
    # Generate all the profiles separately first
    print('Generating individual profiles...')
    
    # Basic demographics (this should work)
    birth_date = date(1990, 1, 1)
    gender = Gender.MALE
    
    print('Testing basic Person creation...')
    basic_person = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=birth_date,
        gender=gender
    )
    print('✅ Basic Person creation works')
    
    # Now test with each profile type individually
    print('Testing with medical profile...')
    medical_profile = generator.medical_gen.generate_medical_profile(
        30, 'M', 180, 75, ('John Doe', 'Spouse', '555-1234')
    )
    print(f'Medical profile type: {type(medical_profile)}')
    
    person_with_medical = Person(
        first_name='Test',
        last_name='User', 
        date_of_birth=birth_date,
        gender=gender,
        medical_profile=medical_profile
    )
    print('✅ Person with medical profile works')
    
    # Test with travel profile
    print('Testing with travel profile...')
    travel_profile = generator.travel_gen.generate_travel_profile(30, 50000, 'average')
    print(f'Travel profile type: {type(travel_profile)}')
    
    person_with_travel = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=birth_date,
        gender=gender,
        travel_profile=travel_profile
    )
    print('✅ Person with travel profile works')
    
    # Test with all new profiles
    print('Testing with all new profiles...')
    financial_profile = generator.financial_transactions_gen.generate_financial_profile(30, 50000, 700, 'average')
    communication_profile = generator.communication_gen.generate_communication_profile(30, 'Software Engineer', 'average', 'San Francisco, CA')
    
    print(f'Financial profile type: {type(financial_profile)}')
    print(f'Communication profile type: {type(communication_profile)}')
    
    person_with_all_new = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=birth_date,
        gender=gender,
        travel_profile=travel_profile,
        enhanced_financial_profile=financial_profile,
        communication_profile=communication_profile
    )
    print('✅ Person with all new profiles works!')
    
except Exception as e:
    print(f'❌ Error at step: {e}')
    import traceback
    traceback.print_exc()