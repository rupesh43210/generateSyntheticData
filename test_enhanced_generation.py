#!/usr/bin/env python3
"""Test enhanced person generation directly"""

print('Testing enhanced person generation...')

# Test the full pipeline
from src.generators.person_generator import PersonGenerator
from src.core.models import GenerationConfig

try:
    config = GenerationConfig(num_records=1, batch_size=1, num_threads=1)
    generator = PersonGenerator(config)
    
    print('Generating person...')
    person = generator.generate_person()
    print(f'✅ Generated: {person.first_name} {person.last_name}')
    
    # Check new profiles
    new_profiles = []
    if person.travel_profile:
        new_profiles.append(f'travel({person.travel_profile.total_trips} trips)')
    if person.enhanced_financial_profile:
        new_profiles.append(f'financial(${person.enhanced_financial_profile.net_worth:,.0f} net worth)')
    if person.communication_profile:
        new_profiles.append(f'communication({person.communication_profile.total_contacts} contacts)')
    
    if new_profiles:
        print(f'✅ Enhanced profiles: {" | ".join(new_profiles)}')
    else:
        print('❌ No enhanced profiles generated')
        
    # Test JSON serialization
    print('Testing JSON serialization...')
    if hasattr(person, 'model_dump'):
        person_dict = person.model_dump()
    else:
        person_dict = person.dict()
    
    print('✅ JSON serialization works')
    
except Exception as e:
    print(f'❌ Error in generation: {e}')
    import traceback
    traceback.print_exc()