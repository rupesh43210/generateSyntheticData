import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import uuid
import logging

from src.core.models import Person, Gender, GenerationConfig, rebuild_person_model
from src.core.variability import VariabilityEngine
from .name_generator import NameGenerator
from .address_generator import AddressGenerator
from .contact_generator import ContactGenerator
from .financial_generator import FinancialGenerator
from .employment_generator import EmploymentGenerator
from .medical_generator import MedicalGenerator
from .vehicle_generator import VehicleGenerator
from .education_generator import EducationGenerator
from .social_generator import SocialMediaGenerator
from .biometric_generator import BiometricGenerator
from .lifestyle_generator import LifestyleGenerator
from .travel_generator import TravelGenerator, TravelProfile
from .financial_transactions_generator import FinancialTransactionsGenerator, FinancialProfile as EnhancedFinancialProfile
from .communication_generator import CommunicationGenerator, CommunicationProfile


class PersonGenerator:
    """Main generator that combines all components to create complete person records"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        
        # Initialize variability engine
        self.variability = VariabilityEngine({
            'missing_data_rate': config.data_quality_profile.missing_data_rate,
            'typo_rate': config.data_quality_profile.typo_rate,
            'duplicate_rate': config.data_quality_profile.duplicate_rate,
            'outlier_rate': config.data_quality_profile.outlier_rate,
            'inconsistency_rate': config.data_quality_profile.inconsistency_rate
        })
        
        # Initialize component generators
        self.name_gen = NameGenerator(self.variability)
        self.address_gen = AddressGenerator(self.variability)
        self.contact_gen = ContactGenerator(self.variability)
        self.financial_gen = FinancialGenerator(self.variability)
        self.employment_gen = EmploymentGenerator(self.variability)
        
        # Initialize new comprehensive generators
        self.medical_gen = MedicalGenerator(self.variability)
        self.vehicle_gen = VehicleGenerator(self.variability)
        self.education_gen = EducationGenerator(self.variability)
        self.social_gen = SocialMediaGenerator(self.variability)
        self.biometric_gen = BiometricGenerator(self.variability)
        self.lifestyle_gen = LifestyleGenerator(self.variability)
        self.travel_gen = TravelGenerator()
        self.financial_transactions_gen = FinancialTransactionsGenerator()
        self.communication_gen = CommunicationGenerator()
        
        # Set random seed if provided
        if config.seed:
            random.seed(config.seed)
        
        # Rebuild Person model to resolve forward references
        success = rebuild_person_model()
        if not success:
            logging.warning("Person model rebuild failed - new profiles may not work")
        
        # Track generated data for relationships
        self.generated_people = []
        self.family_groups = []
        self.same_address_groups = []
        
    def _generate_birth_date(self) -> date:
        """Generate realistic birth date with age distribution"""
        # Age distribution (simplified US demographics)
        age_distribution = [
            (18, 24, 0.09),
            (25, 34, 0.14),
            (35, 44, 0.13),
            (45, 54, 0.13),
            (55, 64, 0.13),
            (65, 74, 0.10),
            (75, 84, 0.06),
            (85, 95, 0.02)
        ]
        
        # Select age range
        ranges = [(a[0], a[1]) for a in age_distribution]
        weights = [a[2] for a in age_distribution]
        age_range = random.choices(ranges, weights=weights)[0]
        
        # Generate specific age
        age = random.randint(age_range[0], age_range[1])
        
        # Calculate birth date
        today = date.today()
        
        # Generate a birth date that ensures the person is at least 'age' years old
        # by making sure their birthday has already passed this year
        birth_year = today.year - age - 1  # Start with previous year
        
        # Random month and day
        birth_month = random.randint(1, 12)
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:
            # February - check for leap year
            if birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        
        birth_day = random.randint(1, max_day)
        birth_date = date(birth_year, birth_month, birth_day)
        
        # If the birthday has already passed this year, we can add a year to birth_year
        if (birth_month < today.month) or (birth_month == today.month and birth_day <= today.day):
            birth_date = date(birth_year + 1, birth_month, birth_day)
        
        return birth_date
    
    def _generate_ssn(self) -> str:
        """Generate SSN with realistic patterns"""
        # SSN format: AAA-GG-SSSS
        # AAA: Area number (001-665, 667-899)
        # GG: Group number (01-99)
        # SSSS: Serial number (0001-9999)
        
        # Invalid area numbers
        invalid_areas = [666] + list(range(900, 1000))
        
        area = random.randint(1, 899)
        while area in invalid_areas:
            area = random.randint(1, 899)
        
        group = random.randint(1, 99)
        serial = random.randint(1, 9999)
        
        ssn = f"{area:03d}-{group:02d}-{serial:04d}"
        
        # Apply variations
        if self.variability:
            ssn = self.variability.vary_format(ssn, 'ssn')
        
        return ssn
    
    def _select_gender(self) -> Gender:
        """Select gender with realistic distribution"""
        # Roughly 50/50 with small percentage other/unknown
        rand = random.random()
        if rand < 0.495:
            return Gender.MALE
        elif rand < 0.99:
            return Gender.FEMALE
        elif rand < 0.995:
            return Gender.OTHER
        else:
            return Gender.UNKNOWN
    
    def _select_industries(self) -> List[str]:
        """Select industries for person's career"""
        from src.core.constants import INDUSTRIES
        
        # Most people work in 1-3 industries over career
        num_industries = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        
        # Apply geographic clustering if enabled
        if self.config.enable_geographic_clustering and self.config.industry_distribution:
            # Use configured distribution
            industries = list(self.config.industry_distribution.keys())
            weights = list(self.config.industry_distribution.values())
            selected = random.choices(industries, weights=weights, k=num_industries)
        else:
            selected = random.sample(INDUSTRIES, num_industries)
        
        return selected
    
    def generate_person(self) -> Person:
        """Generate a complete person record"""
        # Basic demographics
        birth_date = self._generate_birth_date()
        gender = self._select_gender()
        age = (date.today() - birth_date).days // 365
        
        # Generate name
        name_data = self.name_gen.generate_full_name(gender.value, birth_date)
        
        # Generate SSN
        ssn = self._generate_ssn() if random.random() > self.variability.missing_data_rate else None
        
        # Generate addresses
        num_addresses = random.randint(
            self.config.min_addresses_per_person,
            self.config.max_addresses_per_person
        )
        addresses = self.address_gen.generate_address_history(num_addresses)
        
        # Get current state for other generators
        current_address = next((a for a in addresses if a.address_type == "current"), addresses[0])
        current_state = current_address.state
        
        # Select industries for career
        industries = self._select_industries()
        
        # Generate employment history
        if age >= 18:
            # Base salary estimation
            base_salary = self.financial_gen.generate_income(
                age, industries[0], current_state, "mid"
            )
            
            employment_history = self.employment_gen.generate_employment_history(
                age, industries, base_salary
            )
            
            # Add contractor periods
            employment_history = self.employment_gen.add_contractor_periods(employment_history)
            
            # Check if currently employed
            is_employed = any(e.is_current for e in employment_history)
            current_employer = next((e.employer_name for e in employment_history if e.is_current), None)
            current_industry = next((e.industry for e in employment_history if e.is_current), industries[0])
        else:
            employment_history = []
            is_employed = False
            current_employer = None
            current_industry = None
            base_salary = 0
        
        # Generate contact information
        num_phones = random.randint(
            self.config.min_phones_per_person,
            self.config.max_phones_per_person
        )
        num_emails = random.randint(
            self.config.min_emails_per_person,
            self.config.max_emails_per_person
        )
        
        phones, emails = self.contact_gen.generate_contact_set(
            name_data["first_name"],
            name_data["last_name"],
            current_state,
            birth_date.year,
            current_employer,
            current_industry,
            num_phones,
            num_emails
        )
        
        # Generate financial profile
        financial_profile = None
        if age >= 18 and self.config.enable_financial_correlations:
            financial_profile = self.financial_gen.generate_financial_profile(
                age,
                base_salary,
                current_industry or industries[0],
                current_state,
                is_employed
            )
        
        # Generate comprehensive new profiles
        # Physical/biometric profile (always generated)
        physical_profile = self.biometric_gen.generate_physical_profile(
            gender.value, age, ethnicity="Caucasian"  # Could be made more dynamic
        )
        
        # Medical profile (generated for adults)
        medical_profile = None
        if age >= 18:
            # Generate emergency contact
            emergency_contact = (
                f"{random.choice(['Jane', 'John', 'Mary', 'Michael', 'Sarah', 'David'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
                "Spouse" if random.random() < 0.6 else random.choice(["Parent", "Sibling", "Friend"]),
                f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            )
            
            medical_profile = self.medical_gen.generate_medical_profile(
                age, gender.value, 
                physical_profile.physical_characteristics.height_cm,
                physical_profile.physical_characteristics.weight_kg,
                emergency_contact
            )
        
        # Education profile (always generated)
        education_profile = self.education_gen.generate_education_profile(
            age, base_salary or 0
        )
        
        # Vehicle profile (generated for adults)
        vehicle_profile = None
        if age >= 16:
            full_name = f"{name_data['first_name']} {name_data['last_name']}"
            vehicle_profile = self.vehicle_gen.generate_vehicle_profile(
                age, base_salary or 0, current_state, full_name
            )
        
        # Online presence (generated for most people)
        online_presence = None
        if age >= 13:  # Most people 13+ have some online presence
            interests = []
            if employment_history:
                interests.append(employment_history[0].industry.lower())
            online_presence = self.social_gen.generate_online_presence(
                name_data["first_name"], name_data["last_name"], age,
                birth_date.year, employment_history[0].job_title if employment_history else "Student",
                current_address.city + ", " + current_address.state,
                base_salary or 0, interests
            )
        
        # Lifestyle profile (always generated)
        current_profession = employment_history[0].job_title if employment_history else "Student"
        lifestyle_profile = self.lifestyle_gen.generate_lifestyle_profile(
            age, base_salary or 0, current_profession
        )
        
        # Travel profile (generated for adults)
        travel_profile = None
        if age >= 18:
            travel_profile = self.travel_gen.generate_travel_profile(
                age, base_salary or 0, lifestyle_profile.lifestyle_category.value
            )
        
        # Enhanced financial profile (generated for adults)
        enhanced_financial_profile = None
        if age >= 18:
            credit_score = financial_profile.credit_score if financial_profile else random.randint(600, 750)
            enhanced_financial_profile = self.financial_transactions_gen.generate_financial_profile(
                age, base_salary or 0, credit_score, lifestyle_profile.lifestyle_category.value
            )
        
        # Communication profile (generated for most people)
        communication_profile = None
        if age >= 13:
            occupation = current_profession if current_profession != "Student" else "Student"
            location = f"{current_address.city}, {current_address.state}"
            communication_profile = self.communication_gen.generate_communication_profile(
                age, occupation, lifestyle_profile.lifestyle_category.value, location
            )
        
        # Create person object
        person = Person(
            ssn=ssn,
            first_name=name_data["first_name"],
            middle_name=name_data["middle_name"],
            last_name=name_data["last_name"],
            suffix=name_data["suffix"],
            prefix=name_data["prefix"],
            nickname=name_data["nickname"],
            maiden_name=name_data["maiden_name"],
            date_of_birth=birth_date,
            gender=gender,
            addresses=addresses,
            phone_numbers=phones,
            email_addresses=emails,
            employment_history=employment_history,
            financial_profile=financial_profile,
            medical_profile=medical_profile,
            vehicle_profile=vehicle_profile,
            education_profile=education_profile,
            online_presence=online_presence,
            physical_profile=physical_profile,
            lifestyle_profile=lifestyle_profile,
            travel_profile=travel_profile,
            enhanced_financial_profile=enhanced_financial_profile,
            communication_profile=communication_profile
        )
        
        # Track for relationships
        self.generated_people.append(person)
        
        return person
    
    def generate_related_people(self, base_person: Person, 
                              relationship_type: str,
                              count: int = 1) -> List[Person]:
        """Generate people related to a base person"""
        related_people = []
        
        for _ in range(count):
            if relationship_type == "spouse":
                related = self._generate_spouse(base_person)
            elif relationship_type == "child":
                related = self._generate_child(base_person)
            elif relationship_type == "sibling":
                related = self._generate_sibling(base_person)
            elif relationship_type == "roommate":
                related = self._generate_roommate(base_person)
            else:
                # Default to unrelated person
                related = self.generate_person()
            
            related_people.append(related)
        
        return related_people
    
    def _generate_spouse(self, base_person: Person) -> Person:
        """Generate spouse with shared characteristics"""
        # Similar age (within 5 years usually)
        base_age = (date.today() - base_person.date_of_birth).days // 365
        age_diff = random.randint(-5, 5)
        spouse_age = max(18, base_age + age_diff)
        
        # Generate spouse
        spouse = self.generate_person()
        
        # Adjust age
        spouse.date_of_birth = date.today() - timedelta(days=spouse_age * 365 + random.randint(0, 364))
        
        # Often share last name
        if random.random() < 0.7:
            spouse.last_name = base_person.last_name
        
        # Share current address
        if base_person.addresses:
            current_addr = next((a for a in base_person.addresses if a.address_type == "current"), None)
            if current_addr:
                spouse_addr = current_addr.model_copy()
                spouse_addr.address_id = str(uuid.uuid4())
                spouse.addresses = [spouse_addr] + spouse.addresses[1:]
        
        return spouse
    
    def _generate_child(self, base_person: Person) -> Person:
        """Generate child with inherited characteristics"""
        # Calculate child's age based on parent's age
        parent_age = (date.today() - base_person.date_of_birth).days // 365
        max_child_age = max(0, parent_age - 18)  # Parent at least 18 when child born
        
        if max_child_age < 18:
            return self.generate_person()  # Parent too young to have adult children
        
        child_age = random.randint(18, min(max_child_age, 40))
        
        # Generate child
        child = self.generate_person()
        
        # Adjust age
        child.date_of_birth = date.today() - timedelta(days=child_age * 365 + random.randint(0, 364))
        
        # Inherit last name
        child.last_name = base_person.last_name
        
        # Share address if child is still relatively young (18-25)
        if child_age <= 25 and random.random() < 0.8:
            if base_person.addresses:
                current_addr = next((a for a in base_person.addresses if a.address_type == "current"), None)
                if current_addr:
                    child_addr = current_addr.model_copy()
                    child_addr.address_id = str(uuid.uuid4())
                    child.addresses = [child_addr] + child.addresses[1:]
        
        return child
    
    def _generate_sibling(self, base_person: Person) -> Person:
        """Generate sibling with shared characteristics"""
        # Similar age (within 10 years)
        base_age = (date.today() - base_person.date_of_birth).days // 365
        age_diff = random.randint(-10, 10)
        sibling_age = max(18, base_age + age_diff)
        
        # Generate sibling
        sibling = self.generate_person()
        
        # Adjust age
        sibling.date_of_birth = date.today() - timedelta(days=sibling_age * 365 + random.randint(0, 364))
        
        # Same last name
        sibling.last_name = base_person.last_name
        
        # Might share childhood address (previous)
        if random.random() < 0.6 and base_person.addresses:
            prev_addr = next((a for a in base_person.addresses if a.address_type == "previous"), None)
            if prev_addr:
                sibling_addr = prev_addr.model_copy()
                sibling_addr.address_id = str(uuid.uuid4())
                sibling.addresses.append(sibling_addr)
        
        return sibling
    
    def _generate_roommate(self, base_person: Person) -> Person:
        """Generate roommate sharing current address"""
        # Similar age (within 10 years)
        base_age = (date.today() - base_person.date_of_birth).days // 365
        age_diff = random.randint(-10, 10)
        roommate_age = max(18, base_age + age_diff)
        
        # Generate roommate
        roommate = self.generate_person()
        
        # Adjust age
        roommate.date_of_birth = date.today() - timedelta(days=roommate_age * 365 + random.randint(0, 364))
        
        # Share current address
        if base_person.addresses:
            current_addr = next((a for a in base_person.addresses if a.address_type == "current"), None)
            if current_addr:
                roommate_addr = current_addr.model_copy()
                roommate_addr.address_id = str(uuid.uuid4())
                roommate.addresses = [roommate_addr] + roommate.addresses[1:]
        
        return roommate
    
    def create_family_clusters(self, num_families: int) -> List[List[Person]]:
        """Create realistic family clusters"""
        families = []
        
        for _ in range(num_families):
            # Generate head of household
            head = self.generate_person()
            family = [head]
            
            # Add spouse (70% chance)
            if random.random() < 0.7:
                spouse = self._generate_spouse(head)
                family.append(spouse)
            
            # Add children (based on age)
            head_age = (date.today() - head.date_of_birth).days // 365
            if head_age > 25:
                num_children = random.choices([0, 1, 2, 3, 4], weights=[0.2, 0.3, 0.35, 0.1, 0.05])[0]
                for _ in range(num_children):
                    child = self._generate_child(head)
                    family.append(child)
            
            families.append(family)
            self.family_groups.append(family)
        
        return families