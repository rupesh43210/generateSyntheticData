#!/usr/bin/env python3
"""Test script to diagnose model issues"""

# Test the model creation step by step
print("Testing model creation...")

try:
    # Import base modules
    from src.core.models import Person, Gender
    from datetime import date
    
    print("✅ Basic imports work")
    
    # Try to create a basic person
    person = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE
    )
    print("✅ Basic Person creation works")
    
    # Now try importing the new generators
    from src.generators.travel_generator import TravelGenerator, TravelProfile
    print("✅ Travel generator import works")
    
    # Generate a travel profile
    travel_gen = TravelGenerator()
    travel_profile = travel_gen.generate_travel_profile(30, 50000, 'average')
    print("✅ Travel profile generation works")
    
    # Now try to create a person with the travel profile
    print(f"Travel profile type: {type(travel_profile)}")
    print(f"Is instance of TravelProfile: {isinstance(travel_profile, TravelProfile)}")
    
    # Check the Person model fields
    print("Person model fields:")
    for field_name, field_info in Person.model_fields.items():
        if 'profile' in field_name:
            print(f"  {field_name}: {field_info}")
    
    # Try creating person with travel profile
    person_with_travel = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        travel_profile=travel_profile
    )
    print("✅ Person with travel profile creation works")
    
    # Try the person generator
    from src.generators.person_generator import PersonGenerator
    from src.core.models import GenerationConfig
    
    config = GenerationConfig(num_records=1, batch_size=1, num_threads=1)
    generator = PersonGenerator(config)
    
    print("Testing full person generation...")
    full_person = generator.generate_person()
    print(f"✅ Full person generated: {full_person.first_name} {full_person.last_name}")
    
    # Check if new profiles are there
    if full_person.travel_profile:
        print(f"✅ Travel profile exists: {full_person.travel_profile.total_trips} trips")
    else:
        print("❌ No travel profile generated")
        
    if full_person.enhanced_financial_profile:
        print(f"✅ Enhanced financial profile exists: net worth ${full_person.enhanced_financial_profile.net_worth}")
    else:
        print("❌ No enhanced financial profile generated")
        
    if full_person.communication_profile:
        print(f"✅ Communication profile exists: {full_person.communication_profile.total_contacts} contacts")
    else:
        print("❌ No communication profile generated")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()