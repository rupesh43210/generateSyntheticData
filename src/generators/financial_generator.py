import random
import math
from typing import Dict, Optional, Tuple
from datetime import datetime, date, timedelta
import numpy as np

from src.core.constants import CREDIT_SCORE_DISTRIBUTION, INCOME_BY_AGE_RANGE
from src.core.variability import VariabilityEngine
from src.core.models import FinancialProfile


class FinancialGenerator:
    """Generator for financial data with realistic correlations and distributions"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Credit score factors and weights
        self.credit_factors = {
            "payment_history": 0.35,
            "credit_utilization": 0.30,
            "credit_history_length": 0.15,
            "credit_mix": 0.10,
            "new_credit": 0.10
        }
        
        # Income correlation factors
        self.income_multipliers = {
            "Technology": 1.3,
            "Finance": 1.4,
            "Healthcare": 1.2,
            "Education": 0.8,
            "Retail": 0.7,
            "Manufacturing": 0.9,
            "Construction": 0.95,
            "Real Estate": 1.1,
            "Hospitality": 0.6,
            "Transportation": 0.85,
            "Energy": 1.15,
            "Telecommunications": 1.1,
            "Media": 0.9,
            "Entertainment": 0.8,
            "Government": 0.95,
            "Non-Profit": 0.7,
            "Consulting": 1.25,
            "Legal": 1.35,
            "Insurance": 1.05,
            "Agriculture": 0.75
        }
        
        # Geographic cost of living adjustments
        self.location_multipliers = {
            "CA": 1.3,  # California
            "NY": 1.25,  # New York
            "WA": 1.15,  # Washington
            "MA": 1.2,  # Massachusetts
            "IL": 1.1,  # Illinois
            "TX": 0.95,  # Texas
            "FL": 0.9,  # Florida
            "OH": 0.85,  # Ohio
            "MI": 0.85,  # Michigan
            "GA": 0.9,  # Georgia
            "NC": 0.9,  # North Carolina
            "PA": 0.95,  # Pennsylvania
        }
        
    def _calculate_credit_score_from_factors(self, age: int, income: float,
                                           employment_stable: bool = True) -> int:
        """Calculate credit score based on multiple factors"""
        base_score = 650
        
        # Age factor (credit history length)
        if age < 21:
            age_factor = -50
        elif age < 25:
            age_factor = -20
        elif age < 30:
            age_factor = 0
        elif age < 40:
            age_factor = 20
        elif age < 50:
            age_factor = 30
        else:
            age_factor = 25
        
        # Income factor
        if income < 20000:
            income_factor = -40
        elif income < 40000:
            income_factor = -20
        elif income < 60000:
            income_factor = 0
        elif income < 100000:
            income_factor = 20
        elif income < 150000:
            income_factor = 30
        else:
            income_factor = 40
        
        # Employment stability
        employment_factor = 20 if employment_stable else -30
        
        # Random variation
        random_factor = random.normalvariate(0, 30)
        
        # Calculate final score
        score = base_score + age_factor + income_factor + employment_factor + random_factor
        
        # Apply distribution bias
        for min_score, max_score, probability in CREDIT_SCORE_DISTRIBUTION:
            if random.random() < probability:
                # Bias towards this range
                range_mid = (min_score + max_score) / 2
                score = 0.7 * score + 0.3 * range_mid
                break
        
        # Ensure within valid range
        return max(300, min(850, int(score)))
    
    def generate_income(self, age: int, industry: str, state: str,
                       job_level: str = "mid") -> float:
        """Generate income with correlations to age, industry, and location"""
        # Base income by age
        base_income = 35000  # Default
        for age_range, income_range in INCOME_BY_AGE_RANGE.items():
            if age_range[0] <= age <= age_range[1]:
                base_income = random.uniform(income_range[0], income_range[1])
                break
        
        # Industry adjustment
        industry_mult = self.income_multipliers.get(industry, 1.0)
        
        # Location adjustment
        location_mult = self.location_multipliers.get(state, 1.0)
        
        # Job level adjustment
        level_multipliers = {
            "entry": 0.7,
            "mid": 1.0,
            "senior": 1.5,
            "executive": 2.5
        }
        level_mult = level_multipliers.get(job_level, 1.0)
        
        # Calculate final income
        income = base_income * industry_mult * location_mult * level_mult
        
        # Add some randomness
        income *= random.uniform(0.8, 1.2)
        
        # Round to realistic values
        if income < 50000:
            income = round(income / 1000) * 1000
        elif income < 100000:
            income = round(income / 2500) * 2500
        else:
            income = round(income / 5000) * 5000
        
        # Apply outliers
        if self.variability:
            income = self.variability.create_outlier(income, 'income')
        
        return float(max(0, income))
    
    def generate_debt_profile(self, income: float, age: int,
                            credit_score: int) -> Dict[str, float]:
        """Generate realistic debt profile"""
        # Debt-to-income ratio based on credit score
        if credit_score >= 740:
            max_dti = 0.35
        elif credit_score >= 670:
            max_dti = 0.45
        elif credit_score >= 580:
            max_dti = 0.55
        else:
            max_dti = 0.65
        
        # Base DTI with randomness
        base_dti = random.uniform(0.1, max_dti)
        
        # Age adjustments (younger people tend to have more debt)
        if age < 30:
            base_dti *= 1.2
        elif age > 50:
            base_dti *= 0.8
        
        total_debt = income * base_dti
        
        # Distribute debt across categories
        debt_distribution = {
            "mortgage": 0.0,
            "auto_loans": 0.0,
            "student_loans": 0.0,
            "credit_cards": 0.0,
            "other_debt": 0.0
        }
        
        # Mortgage (more likely for older people)
        if age > 25 and random.random() < 0.6:
            mortgage_amount = income * random.uniform(1.5, 3.5)
            debt_distribution["mortgage"] = mortgage_amount
        
        # Auto loans
        if random.random() < 0.7:
            auto_amount = random.uniform(5000, min(35000, income * 0.5))
            debt_distribution["auto_loans"] = auto_amount
        
        # Student loans (more likely for younger people)
        if age < 40 and random.random() < 0.4:
            student_amount = random.uniform(10000, min(80000, income * 1.5))
            debt_distribution["student_loans"] = student_amount
        
        # Credit cards
        if random.random() < 0.85:
            cc_amount = random.uniform(500, min(20000, income * 0.3))
            debt_distribution["credit_cards"] = cc_amount
        
        # Other debt
        if random.random() < 0.3:
            other_amount = random.uniform(1000, min(15000, income * 0.2))
            debt_distribution["other_debt"] = other_amount
        
        return debt_distribution
    
    def generate_credit_accounts(self, age: int, credit_score: int) -> Dict[str, any]:
        """Generate credit account information"""
        # Number of accounts correlates with age and score
        if age < 21:
            num_accounts = random.randint(0, 3)
        elif age < 30:
            num_accounts = random.randint(2, 8)
        elif age < 50:
            num_accounts = random.randint(5, 15)
        else:
            num_accounts = random.randint(4, 12)
        
        # Adjust based on credit score
        if credit_score < 580:
            num_accounts = max(1, num_accounts - 2)
        elif credit_score > 740:
            num_accounts += random.randint(1, 3)
        
        # Oldest account age
        max_account_age = min(age - 18, 40)  # Can't have accounts before 18
        if max_account_age > 0:
            oldest_account_age = random.uniform(1, max_account_age)
        else:
            oldest_account_age = 0
        
        # Recent inquiries (affects credit score)
        if credit_score < 650:
            recent_inquiries = random.randint(2, 8)
        else:
            recent_inquiries = random.randint(0, 3)
        
        return {
            "number_of_accounts": num_accounts,
            "oldest_account_age_years": oldest_account_age,
            "recent_inquiries": recent_inquiries
        }
    
    def calculate_credit_utilization(self, debt_profile: Dict[str, float],
                                   credit_score: int) -> Tuple[float, float]:
        """Calculate credit utilization and available credit"""
        cc_debt = debt_profile.get("credit_cards", 0)
        
        # Available credit based on score
        if credit_score >= 740:
            available_credit = cc_debt / random.uniform(0.1, 0.3)  # Low utilization
        elif credit_score >= 670:
            available_credit = cc_debt / random.uniform(0.2, 0.5)  # Moderate utilization
        else:
            available_credit = cc_debt / random.uniform(0.5, 0.9)  # High utilization
        
        # Ensure minimum credit limit
        available_credit = max(available_credit, 1000)
        
        # Calculate utilization rate
        if available_credit > 0:
            utilization_rate = cc_debt / available_credit
        else:
            utilization_rate = 0
        
        return available_credit, min(utilization_rate, 1.0)
    
    def generate_financial_profile(self, age: int, income: float,
                                 industry: str, state: str,
                                 employment_stable: bool = True) -> FinancialProfile:
        """Generate complete financial profile with all correlations"""
        # Generate credit score
        credit_score = self._calculate_credit_score_from_factors(age, income, employment_stable)
        
        # Apply variability to credit score
        if self.variability:
            credit_score = int(self.variability.create_outlier(credit_score, 'credit_score'))
            # Ensure credit score stays within valid range (300-850)
            credit_score = max(300, min(850, credit_score))
        
        # Generate debt profile
        debt_profile = self.generate_debt_profile(income, age, credit_score)
        total_debt = sum(debt_profile.values())
        
        # Calculate debt-to-income ratio
        debt_to_income_ratio = total_debt / income if income > 0 else 0
        # Ensure DTI stays within model constraints (max 10.0)
        debt_to_income_ratio = min(debt_to_income_ratio, 10.0)
        
        # Generate account information
        account_info = self.generate_credit_accounts(age, credit_score)
        
        # Calculate credit utilization
        available_credit, utilization_rate = self.calculate_credit_utilization(
            debt_profile, credit_score
        )
        
        # Apply seasonal patterns to income if requested
        annual_income = income
        if self.variability and self.variability.should_apply(0.1):
            # Some variation in reported income
            annual_income = self.variability.add_noise_to_numeric(income, 0.05)
        
        return FinancialProfile(
            credit_score=credit_score,
            annual_income=annual_income,
            debt_to_income_ratio=debt_to_income_ratio,
            number_of_accounts=account_info["number_of_accounts"],
            oldest_account_age_years=account_info["oldest_account_age_years"],
            recent_inquiries=account_info["recent_inquiries"],
            total_debt=total_debt,
            available_credit=available_credit,
            utilization_rate=utilization_rate
        )
    
    def apply_benford_law(self, values: list, digit_position: int = 1) -> list:
        """Apply Benford's Law to financial data for realism"""
        if not values or digit_position < 1:
            return values
        
        # Benford's Law probabilities for first digit
        benford_probs = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097,
            5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
        
        adjusted_values = []
        for value in values:
            if value > 0:
                # Get the specified digit
                str_value = str(int(value))
                if len(str_value) >= digit_position:
                    # Apply Benford's Law with some randomness
                    if random.random() < 0.7:  # 70% follow Benford's Law
                        first_digit = int(np.random.choice(
                            list(benford_probs.keys()),
                            p=list(benford_probs.values())
                        ))
                        # Replace first digit
                        new_value = str(first_digit) + str_value[1:]
                        adjusted_values.append(float(new_value))
                    else:
                        adjusted_values.append(value)
                else:
                    adjusted_values.append(value)
            else:
                adjusted_values.append(value)
        
        return adjusted_values