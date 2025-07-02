#!/usr/bin/env python3
"""Test without model rebuild"""

print('Testing person generation WITHOUT model rebuild...')

# Import everything but don't rebuild
from src.core.models import Person, Gender, GenerationConfig
from datetime import date

try:
    # Try direct Person creation first
    print('Testing direct Person creation...')
    person = Person(
        first_name='Test',
        last_name='User',
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE
    )
    print(f'✅ Direct Person creation works: {person.first_name} {person.last_name}')
    
    # Now try with PersonGenerator but skip the rebuild
    print('Testing PersonGenerator without rebuild...')
    from src.generators.person_generator import PersonGenerator
    
    # Patch the rebuild function to do nothing
    import src.core.models
    original_rebuild = src.core.models.rebuild_person_model
    src.core.models.rebuild_person_model = lambda: True
    
    config = GenerationConfig(num_records=1, batch_size=1, num_threads=1)
    generator = PersonGenerator(config)
    
    # Restore original function
    src.core.models.rebuild_person_model = original_rebuild
    
    print('Generating person...')
    person = generator.generate_person()
    print(f'✅ PersonGenerator works: {person.first_name} {person.last_name}')
    
    # Check new profiles
    if person.travel_profile:
        print(f'✅ Travel profile: {person.travel_profile.total_trips} trips')
    if person.enhanced_financial_profile:
        print(f'✅ Financial profile: ${person.enhanced_financial_profile.net_worth:,.0f}')
    if person.communication_profile:
        print(f'✅ Communication profile: {person.communication_profile.total_contacts} contacts')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()