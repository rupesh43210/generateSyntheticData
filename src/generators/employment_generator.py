import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import math

from src.core.constants import JOB_TITLES_BY_LEVEL, INDUSTRIES, COMPANY_NAMES
from src.core.variability import VariabilityEngine
from src.core.models import Employment, EmploymentStatus


class EmploymentGenerator:
    """Generator for employment data with temporal patterns and career progression"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Industry-specific job titles
        self.industry_job_titles = {
            "Technology": {
                "entry": ["Junior Developer", "QA Analyst", "IT Support Specialist", "Data Entry Clerk"],
                "mid": ["Software Engineer", "Systems Analyst", "DevOps Engineer", "Product Manager"],
                "senior": ["Senior Software Engineer", "Tech Lead", "Solutions Architect", "Engineering Manager"],
                "executive": ["CTO", "VP of Engineering", "Chief Information Officer", "Director of Technology"]
            },
            "Healthcare": {
                "entry": ["Medical Assistant", "Pharmacy Technician", "Nursing Aide", "Receptionist"],
                "mid": ["Registered Nurse", "Physical Therapist", "Lab Technician", "Medical Coder"],
                "senior": ["Nurse Practitioner", "Department Manager", "Senior Therapist", "Clinical Coordinator"],
                "executive": ["Chief Medical Officer", "Hospital Administrator", "VP of Clinical Services"]
            },
            "Finance": {
                "entry": ["Junior Analyst", "Bank Teller", "Loan Processor", "Accounting Clerk"],
                "mid": ["Financial Analyst", "Account Manager", "Risk Analyst", "Senior Accountant"],
                "senior": ["Portfolio Manager", "Senior Financial Advisor", "Finance Director", "VP of Finance"],
                "executive": ["CFO", "Chief Investment Officer", "Managing Director", "Partner"]
            }
        }
        
        # Department mappings
        self.departments_by_industry = {
            "Technology": ["Engineering", "Product", "QA", "DevOps", "IT", "Support", "Research"],
            "Healthcare": ["Clinical", "Nursing", "Laboratory", "Pharmacy", "Administration", "Emergency"],
            "Finance": ["Trading", "Risk Management", "Accounting", "Audit", "Investment Banking", "Wealth Management"],
            "Default": ["Operations", "Sales", "Marketing", "Human Resources", "Administration", "Customer Service"]
        }
        
        # Seasonal hiring patterns
        self.seasonal_patterns = {
            "Retail": {1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2, 7: 1.2, 8: 1.1, 9: 1.0, 10: 1.2, 11: 1.5, 12: 1.8},
            "Education": {1: 1.2, 2: 1.0, 3: 0.9, 4: 0.8, 5: 0.7, 6: 0.6, 7: 0.7, 8: 1.5, 9: 1.4, 10: 1.0, 11: 0.9, 12: 0.8},
            "Construction": {1: 0.6, 2: 0.7, 3: 0.9, 4: 1.2, 5: 1.4, 6: 1.5, 7: 1.5, 8: 1.4, 9: 1.2, 10: 1.0, 11: 0.8, 12: 0.6},
            "Default": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0}
        }
        
        # Career progression patterns
        self.avg_tenure_by_age = {
            (18, 25): (0.5, 2.0),   # Young workers change jobs frequently
            (26, 35): (1.5, 4.0),   # Early career
            (36, 45): (3.0, 7.0),   # Mid career
            (46, 55): (5.0, 12.0),  # Late career
            (56, 99): (7.0, 20.0)   # Near retirement
        }
        
    def _get_job_level(self, age: int, years_experience: int) -> str:
        """Determine job level based on age and experience"""
        if years_experience < 2 or age < 25:
            return "entry"
        elif years_experience < 5 or age < 30:
            return random.choice(["entry", "mid"]) if years_experience < 3 else "mid"
        elif years_experience < 10 or age < 40:
            return random.choice(["mid", "senior"])
        elif years_experience < 15:
            return "senior"
        else:
            return random.choice(["senior", "executive"]) if age > 45 else "senior"
    
    def _generate_company_name(self, industry: str) -> str:
        """Generate or select company name"""
        if random.random() < 0.7:
            # Use predefined company names
            return random.choice(COMPANY_NAMES)
        else:
            # Generate industry-specific company name
            prefixes = ["Global", "Premier", "Advanced", "Strategic", "Innovative", "Digital", "United", "National"]
            suffixes = {
                "Technology": ["Tech", "Systems", "Solutions", "Software", "Digital", "Labs"],
                "Healthcare": ["Health", "Medical", "Care", "Clinic", "Wellness", "Therapeutics"],
                "Finance": ["Financial", "Capital", "Investments", "Securities", "Bank", "Advisors"],
                "Default": ["Group", "Corporation", "Enterprises", "Industries", "Partners", "Associates"]
            }
            
            prefix = random.choice(prefixes)
            suffix_list = suffixes.get(industry, suffixes["Default"])
            suffix = random.choice(suffix_list)
            
            return f"{prefix} {suffix}"
    
    def _get_department(self, industry: str, job_title: str) -> str:
        """Get appropriate department based on industry and job title"""
        departments = self.departments_by_industry.get(industry, self.departments_by_industry["Default"])
        
        # Match department to job title
        if "Engineer" in job_title or "Developer" in job_title:
            return "Engineering" if "Engineering" in departments else departments[0]
        elif "Manager" in job_title or "Director" in job_title:
            return "Management"
        elif "Analyst" in job_title:
            return "Analytics" if "Analytics" in departments else departments[0]
        
        return random.choice(departments)
    
    def _calculate_tenure(self, age: int, is_current: bool = False) -> float:
        """Calculate realistic job tenure based on age"""
        # Find appropriate age range
        tenure_range = (1.0, 3.0)  # Default
        for age_range, tenure in self.avg_tenure_by_age.items():
            if age_range[0] <= age <= age_range[1]:
                tenure_range = tenure
                break
        
        # Generate tenure with some randomness
        min_tenure, max_tenure = tenure_range
        
        if is_current:
            # Current job might have shorter tenure
            tenure = random.uniform(0.5, min(max_tenure, 10.0))
        else:
            tenure = random.uniform(min_tenure, max_tenure)
        
        # Add some outliers
        if random.random() < 0.1:
            # 10% chance of unusually long tenure
            tenure *= random.uniform(1.5, 2.5)
        elif random.random() < 0.15:
            # 15% chance of short tenure
            tenure *= random.uniform(0.3, 0.7)
        
        return tenure
    
    def generate_employment(self, industry: str, start_date: date,
                          age_at_start: int, is_current: bool = False,
                          previous_salary: Optional[float] = None) -> Employment:
        """Generate single employment record"""
        # Calculate experience at start
        years_experience = max(0, age_at_start - 22)  # Assume start working at 22
        
        # Determine job level
        job_level = self._get_job_level(age_at_start, years_experience)
        
        # Get job title
        if industry in self.industry_job_titles:
            titles = self.industry_job_titles[industry][job_level]
        else:
            titles = JOB_TITLES_BY_LEVEL[job_level]
        
        job_title = random.choice(titles)
        
        # Generate company name
        company_name = self._generate_company_name(industry)
        
        # Get department
        department = self._get_department(industry, job_title)
        
        # Employment status
        if is_current:
            if random.random() < 0.85:
                status = EmploymentStatus.FULL_TIME
            else:
                status = random.choice([EmploymentStatus.PART_TIME, EmploymentStatus.CONTRACT])
        else:
            # Historical employment usually full-time
            status = EmploymentStatus.FULL_TIME if random.random() < 0.9 else EmploymentStatus.CONTRACT
        
        # Calculate tenure and end date
        tenure_years = self._calculate_tenure(age_at_start, is_current)
        
        if is_current:
            end_date = None
        else:
            end_date = start_date + timedelta(days=int(tenure_years * 365))
        
        # Calculate salary with progression
        base_salary = previous_salary * random.uniform(1.05, 1.25) if previous_salary else None
        
        # Apply variability
        if self.variability:
            # Typos in company name
            if self.variability.should_apply(0.02):
                company_name = self.variability.introduce_typo(company_name)
            
            # Missing department
            if self.variability.should_apply(0.1):
                department = None
        
        return Employment(
            employer_name=company_name,
            job_title=job_title,
            department=department,
            industry=industry,
            employment_status=status,
            start_date=start_date,
            end_date=end_date,
            salary=base_salary,
            is_current=is_current
        )
    
    def generate_employment_history(self, current_age: int, industries: List[str],
                                  base_salary: float) -> List[Employment]:
        """Generate complete employment history with gaps and overlaps"""
        employment_history = []
        
        # Determine starting age (education completion)
        if random.random() < 0.6:
            start_age = 22  # Bachelor's degree
        elif random.random() < 0.8:
            start_age = 24  # Master's degree
        elif random.random() < 0.9:
            start_age = 18  # High school
        else:
            start_age = 27  # PhD
        
        if current_age < start_age:
            return []  # Still in education
        
        # Start from current and work backwards
        current_date = date.today()
        age = current_age
        current_salary = base_salary
        
        # Current employment
        if random.random() < 0.85:  # 85% currently employed
            # Apply seasonal patterns
            industry = random.choice(industries)
            hire_month = self._apply_seasonal_hiring(industry)
            
            # Random start date for current job
            years_at_current = random.uniform(0.5, min(5.0, current_age - start_age))
            start_date = current_date - timedelta(days=int(years_at_current * 365))
            # Safely replace month, handling day overflow
            try:
                start_date = start_date.replace(month=hire_month)
            except ValueError:
                # Handle case where day doesn't exist in target month
                import calendar
                max_day = calendar.monthrange(start_date.year, hire_month)[1]
                start_date = start_date.replace(month=hire_month, day=min(start_date.day, max_day))
            
            current_job = self.generate_employment(
                industry=industry,
                start_date=start_date,
                age_at_start=int(age - years_at_current),
                is_current=True,
                previous_salary=current_salary
            )
            current_job.salary = current_salary
            employment_history.append(current_job)
            
            # Move to previous job
            current_date = start_date
            age -= years_at_current
            current_salary = current_salary * random.uniform(0.75, 0.95)  # Previous salary was lower
        
        # Generate previous employment
        while age > start_age and len(employment_history) < 10:  # Max 10 jobs
            # Employment gap (unemployment, education, etc.)
            if random.random() < 0.15:  # 15% chance of gap
                gap_months = random.randint(1, 12)
                current_date -= timedelta(days=gap_months * 30)
                age -= gap_months / 12
                continue
            
            # Calculate job duration
            tenure = self._calculate_tenure(int(age))
            if age - tenure < start_age:
                tenure = age - start_age
            
            if tenure <= 0:
                break
            
            # Job end date (with possible overlap for contracting)
            end_date = current_date
            if random.random() < 0.05:  # 5% overlap (contracting)
                end_date += timedelta(days=random.randint(30, 180))
            
            start_date = end_date - timedelta(days=int(tenure * 365))
            
            # Apply seasonal hiring
            industry = random.choice(industries)
            hire_month = self._apply_seasonal_hiring(industry)
            # Safely replace month, handling day overflow
            try:
                start_date = start_date.replace(month=hire_month)
            except ValueError:
                # Handle case where day doesn't exist in target month
                import calendar
                max_day = calendar.monthrange(start_date.year, hire_month)[1]
                start_date = start_date.replace(month=hire_month, day=min(start_date.day, max_day))
            
            # Generate employment
            job = self.generate_employment(
                industry=industry,
                start_date=start_date,
                age_at_start=int(age - tenure),
                is_current=False,
                previous_salary=current_salary
            )
            job.salary = current_salary
            employment_history.append(job)
            
            # Prepare for next iteration
            current_date = start_date - timedelta(days=random.randint(0, 90))  # Gap between jobs
            age -= tenure
            current_salary = current_salary * random.uniform(0.75, 0.95)
        
        # Sort by start date (newest first)
        employment_history.sort(key=lambda x: x.start_date, reverse=True)
        
        return employment_history
    
    def _apply_seasonal_hiring(self, industry: str) -> int:
        """Apply seasonal hiring patterns to determine hire month"""
        patterns = self.seasonal_patterns.get(industry, self.seasonal_patterns["Default"])
        
        # Weighted random selection of month
        months = list(patterns.keys())
        weights = list(patterns.values())
        
        return random.choices(months, weights=weights)[0]
    
    def add_contractor_periods(self, employment_history: List[Employment]) -> List[Employment]:
        """Add contractor/freelance periods to employment history"""
        if not employment_history or random.random() > 0.2:  # 20% have contractor periods
            return employment_history
        
        # Find gaps in employment
        gaps = []
        for i in range(len(employment_history) - 1):
            current_job = employment_history[i]
            next_job = employment_history[i + 1]
            
            if current_job.end_date and next_job.start_date:
                gap_days = (next_job.start_date - current_job.end_date).days
                if gap_days > 60:  # At least 2 months gap
                    gaps.append((current_job.end_date, next_job.start_date, i + 1))
        
        # Fill some gaps with contractor work
        new_jobs = []
        for end_date, start_date, insert_idx in gaps:
            if random.random() < 0.5:  # 50% chance to fill gap
                contract_start = end_date + timedelta(days=random.randint(15, 45))
                contract_end = start_date - timedelta(days=random.randint(15, 45))
                
                if contract_end > contract_start:
                    contract_job = Employment(
                        employer_name="Freelance/Contract",
                        job_title=f"Contract {random.choice(['Consultant', 'Specialist', 'Analyst'])}",
                        department=None,
                        industry=employment_history[insert_idx - 1].industry,
                        employment_status=EmploymentStatus.CONTRACT,
                        start_date=contract_start,
                        end_date=contract_end,
                        salary=None,  # Often not disclosed for contract work
                        is_current=False
                    )
                    new_jobs.append((insert_idx, contract_job))
        
        # Insert contract jobs
        for idx, job in reversed(new_jobs):
            employment_history.insert(idx, job)
        
        return employment_history