import pytest
import random
from datetime import date, datetime
from typing import List

from src.core.models import GenerationConfig, DataQualityProfile, Gender
from src.core.variability import VariabilityEngine
from src.generators.name_generator import NameGenerator
from src.generators.address_generator import AddressGenerator
from src.generators.contact_generator import ContactGenerator
from src.generators.financial_generator import FinancialGenerator
from src.generators.employment_generator import EmploymentGenerator
from src.generators.person_generator import PersonGenerator


class TestNameGenerator:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.05,
            'typo_rate': 0.02,
            'duplicate_rate': 0.001,
            'outlier_rate': 0.01,
            'inconsistency_rate': 0.03
        })
        self.generator = NameGenerator(self.variability)
    
    def test_generate_first_name(self):
        # Test male name generation
        male_name = self.generator.generate_first_name("M")
        assert isinstance(male_name, str)
        assert len(male_name) > 0
        
        # Test female name generation
        female_name = self.generator.generate_first_name("F")
        assert isinstance(female_name, str)
        assert len(female_name) > 0
        
        # Test with birth year
        period_name = self.generator.generate_first_name("M", 1990)
        assert isinstance(period_name, str)
        assert len(period_name) > 0
    
    def test_generate_full_name(self):
        birth_date = date(1990, 5, 15)
        name_data = self.generator.generate_full_name("M", birth_date)
        
        assert "first_name" in name_data
        assert "last_name" in name_data
        assert isinstance(name_data["first_name"], str)
        assert isinstance(name_data["last_name"], str)
        assert len(name_data["first_name"]) > 0
        assert len(name_data["last_name"]) > 0
    
    def test_nickname_generation(self):
        # Test with known names that have nicknames
        nickname = self.generator.generate_nickname("Robert", 1.0)  # 100% chance
        assert nickname is None or isinstance(nickname, str)
        
        nickname = self.generator.generate_nickname("Elizabeth", 1.0)
        assert nickname is None or isinstance(nickname, str)


class TestAddressGenerator:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.05,
            'typo_rate': 0.02,
            'duplicate_rate': 0.001,
            'outlier_rate': 0.01,
            'inconsistency_rate': 0.03
        })
        self.generator = AddressGenerator(self.variability)
    
    def test_generate_standard_address(self):
        addr_data = self.generator.generate_standard_address()
        
        assert "street_1" in addr_data
        assert "city" in addr_data
        assert "state" in addr_data
        assert "zip_code" in addr_data
        
        assert isinstance(addr_data["street_1"], str)
        assert isinstance(addr_data["city"], str)
        assert isinstance(addr_data["state"], str)
        assert isinstance(addr_data["zip_code"], str)
        
        assert len(addr_data["street_1"]) > 0
        assert len(addr_data["city"]) > 0
        assert len(addr_data["state"]) > 0
        assert len(addr_data["zip_code"]) > 0
    
    def test_generate_po_box(self):
        addr_data = self.generator.generate_po_box()
        
        assert "PO Box" in addr_data["street_1"] or "P.O. Box" in addr_data["street_1"]
        assert addr_data["street_2"] is None
    
    def test_generate_address_history(self):
        addresses = self.generator.generate_address_history(3)
        
        assert len(addresses) >= 1
        assert len(addresses) <= 3
        
        # Should have at least one current address
        current_addresses = [a for a in addresses if a.address_type == "current"]
        assert len(current_addresses) >= 1


class TestContactGenerator:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.05,
            'typo_rate': 0.02,
            'duplicate_rate': 0.001,
            'outlier_rate': 0.01,
            'inconsistency_rate': 0.03
        })
        self.generator = ContactGenerator(self.variability)
    
    def test_generate_phone_number(self):
        phone = self.generator.generate_phone_number("CA", "mobile")
        
        assert isinstance(phone.area_code, str)
        assert isinstance(phone.number, str)
        assert len(phone.area_code) == 3
        assert len(phone.number) == 7
        assert phone.country_code == "+1"
        assert phone.phone_type == "mobile"
    
    def test_generate_email_address(self):
        email = self.generator.generate_email_address("John", "Doe", "personal")
        
        assert isinstance(email.email, str)
        assert "@" in email.email
        assert "." in email.email
        assert email.email_type == "personal"
    
    def test_generate_contact_set(self):
        phones, emails = self.generator.generate_contact_set(
            "John", "Doe", "CA", 1990, "Tech Corp", "Technology", 2, 2
        )
        
        assert len(phones) <= 2
        assert len(emails) <= 2
        
        if phones:
            primary_phones = [p for p in phones if p.is_primary]
            assert len(primary_phones) <= 1
        
        if emails:
            primary_emails = [e for e in emails if e.is_primary]
            assert len(primary_emails) <= 1


class TestFinancialGenerator:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.05,
            'typo_rate': 0.02,
            'duplicate_rate': 0.001,
            'outlier_rate': 0.01,
            'inconsistency_rate': 0.03
        })
        self.generator = FinancialGenerator(self.variability)
    
    def test_generate_income(self):
        income = self.generator.generate_income(30, "Technology", "CA", "mid")
        
        assert isinstance(income, float)
        assert income >= 0
        assert income <= 1000000  # Reasonable upper bound
    
    def test_generate_financial_profile(self):
        profile = self.generator.generate_financial_profile(
            age=35, income=75000, industry="Technology", state="CA"
        )
        
        assert 300 <= profile.credit_score <= 850
        assert profile.annual_income > 0
        assert 0 <= profile.debt_to_income_ratio <= 10
        assert profile.number_of_accounts >= 0
        assert profile.oldest_account_age_years >= 0
        assert profile.recent_inquiries >= 0
        assert 0 <= profile.utilization_rate <= 1.0
    
    def test_credit_score_correlation(self):
        # Higher income should generally correlate with higher credit scores
        scores = []
        for income in [30000, 60000, 100000, 150000]:
            profile = self.generator.generate_financial_profile(
                age=35, income=income, industry="Technology", state="CA"
            )
            scores.append(profile.credit_score)
        
        # Not a strict test due to randomness, but generally should trend upward
        assert len(set(scores)) > 1  # Should have variation


class TestEmploymentGenerator:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.05,
            'typo_rate': 0.02,
            'duplicate_rate': 0.001,
            'outlier_rate': 0.01,
            'inconsistency_rate': 0.03
        })
        self.generator = EmploymentGenerator(self.variability)
    
    def test_generate_employment(self):
        employment = self.generator.generate_employment(
            industry="Technology",
            start_date=date(2020, 1, 1),
            age_at_start=25,
            is_current=True
        )
        
        assert isinstance(employment.employer_name, str)
        assert isinstance(employment.job_title, str)
        assert isinstance(employment.industry, str)
        assert employment.industry == "Technology"
        assert employment.is_current is True
    
    def test_generate_employment_history(self):
        history = self.generator.generate_employment_history(
            current_age=35,
            industries=["Technology", "Finance"],
            base_salary=75000
        )
        
        assert isinstance(history, list)
        
        if history:
            # Check if sorted by start date (newest first)
            for i in range(len(history) - 1):
                assert history[i].start_date >= history[i + 1].start_date
            
            # Should have at most one current job
            current_jobs = [e for e in history if e.is_current]
            assert len(current_jobs) <= 1


class TestPersonGenerator:
    def setup_method(self):
        config = GenerationConfig(
            num_records=10,
            batch_size=5,
            num_threads=1,
            data_quality_profile=DataQualityProfile()
        )
        self.generator = PersonGenerator(config)
    
    def test_generate_person(self):
        person = self.generator.generate_person()
        
        # Basic fields
        assert isinstance(person.person_id, str)
        assert isinstance(person.first_name, str)
        assert isinstance(person.last_name, str)
        assert isinstance(person.date_of_birth, date)
        assert isinstance(person.gender, str)
        assert person.gender in [g.value for g in Gender]
        
        # Required fields
        assert len(person.first_name) > 0
        assert len(person.last_name) > 0
        
        # Collections
        assert isinstance(person.addresses, list)
        assert isinstance(person.phone_numbers, list)
        assert isinstance(person.email_addresses, list)
        assert isinstance(person.employment_history, list)
        
        # Should have at least one address
        assert len(person.addresses) >= 1
    
    def test_generate_family_clusters(self):
        families = self.generator.create_family_clusters(2)
        
        assert len(families) == 2
        
        for family in families:
            assert len(family) >= 1  # At least head of household
            
            # Check family relationships
            if len(family) > 1:
                head = family[0]
                for member in family[1:]:
                    # Should share some characteristics (last name, address, etc.)
                    pass  # Specific relationship tests would go here


class TestDataQuality:
    def setup_method(self):
        self.variability = VariabilityEngine({
            'missing_data_rate': 0.1,  # 10% for easier testing
            'typo_rate': 0.1,
            'duplicate_rate': 0.01,
            'outlier_rate': 0.1,
            'inconsistency_rate': 0.1
        })
    
    def test_missing_data_rate(self):
        # Test missing data generation
        values = ["test"] * 1000
        missing_count = sum(1 for _ in range(1000) if self.variability.make_missing("test") is None)
        
        # Should be approximately 10% (with some tolerance for randomness)
        missing_rate = missing_count / 1000
        assert 0.05 <= missing_rate <= 0.15
    
    def test_typo_introduction(self):
        # Test typo introduction
        original = "Street"
        typos = [self.variability.introduce_typo(original) for _ in range(1000)]
        modified_count = sum(1 for typo in typos if typo != original)
        
        # Should have some typos
        assert modified_count > 0
    
    def test_format_variations(self):
        # Test format variations
        phone = "1234567890"
        variations = [self.variability.vary_format(phone, 'phone') for _ in range(100)]
        
        # Should have some variations
        unique_formats = len(set(variations))
        assert unique_formats > 1


def test_statistical_distributions():
    """Test that generated data follows expected statistical patterns"""
    config = GenerationConfig(
        num_records=1000,
        batch_size=100,
        num_threads=1,
        data_quality_profile=DataQualityProfile(
            missing_data_rate=0.01,  # Low for statistical testing
            typo_rate=0.01,
            duplicate_rate=0.001,
            outlier_rate=0.01,
            inconsistency_rate=0.01
        )
    )
    
    generator = PersonGenerator(config)
    people = [generator.generate_person() for _ in range(100)]
    
    # Test age distribution
    ages = [(datetime.now().date() - p.date_of_birth).days // 365 for p in people]
    assert min(ages) >= 18  # Minimum working age
    assert max(ages) <= 100  # Reasonable maximum
    
    # Test gender distribution (should be roughly balanced)
    genders = [p.gender for p in people]
    male_count = sum(1 for g in genders if g == Gender.MALE)
    female_count = sum(1 for g in genders if g == Gender.FEMALE)
    
    # Should be roughly balanced (within 30% of each other)
    ratio = min(male_count, female_count) / max(male_count, female_count)
    assert ratio >= 0.7
    
    # Test financial correlations
    financial_people = [p for p in people if p.financial_profile]
    if financial_people:
        # Credit scores should follow realistic distribution
        credit_scores = [p.financial_profile.credit_score for p in financial_people]
        assert all(300 <= score <= 850 for score in credit_scores)
        
        # Higher incomes should generally correlate with higher credit scores
        income_credit_pairs = [(p.financial_profile.annual_income, p.financial_profile.credit_score) 
                              for p in financial_people]
        
        # Sort by income and check if credit scores generally increase
        sorted_pairs = sorted(income_credit_pairs, key=lambda x: x[0])
        
        # Check correlation (simple test)
        if len(sorted_pairs) >= 10:
            low_income_scores = [score for income, score in sorted_pairs[:len(sorted_pairs)//2]]
            high_income_scores = [score for income, score in sorted_pairs[len(sorted_pairs)//2:]]
            
            # High income group should have higher average credit score
            assert sum(high_income_scores) / len(high_income_scores) >= sum(low_income_scores) / len(low_income_scores) - 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])