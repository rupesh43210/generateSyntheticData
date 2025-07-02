import random
import string
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

from src.core.constants import AREA_CODES_BY_STATE, EMAIL_DOMAINS
from src.core.variability import VariabilityEngine
from src.core.models import PhoneNumber, EmailAddress


class ContactGenerator:
    """Generator for phone numbers and email addresses with realistic patterns"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Phone patterns
        self.mobile_prefixes = ["201", "202", "203", "204", "205", "206", "207", "208", "209", "210",
                               "212", "213", "214", "215", "216", "217", "218", "219", "220", "223"]
        
        # Invalid phone patterns (for data quality)
        self.invalid_patterns = [
            "0000000000", "1111111111", "2222222222", "3333333333", "4444444444",
            "5555555555", "6666666666", "7777777777", "8888888888", "9999999999",
            "1234567890", "0123456789", "9876543210"
        ]
        
        # Email generation patterns
        self.email_separators = [".", "_", "-", ""]
        self.email_formats = [
            "{first}{sep}{last}",
            "{first}.{last}",
            "{f}{last}",
            "{first}{l}",
            "{last}{first}",
            "{first}{year}",
            "{first}.{last}{year}",
            "{first}{random}"
        ]
        
        # Company email domains by industry
        self.company_domains_by_industry = {
            "Technology": ["tech", "systems", "software", "digital", "data"],
            "Healthcare": ["health", "medical", "care", "clinic", "hospital"],
            "Finance": ["financial", "capital", "invest", "bank", "fund"],
            "Education": ["edu", "academy", "school", "university", "institute"],
            "Retail": ["shop", "store", "mart", "retail", "commerce"],
            "Manufacturing": ["mfg", "industrial", "factory", "production"]
        }
        
    def _get_area_code_for_state(self, state: str) -> str:
        """Get appropriate area code for state"""
        if state in AREA_CODES_BY_STATE:
            return random.choice(AREA_CODES_BY_STATE[state])
        
        # Default to common area codes
        return random.choice(["212", "310", "312", "415", "202", "404", "713", "214"])
    
    def _generate_phone_exchange(self) -> str:
        """Generate middle 3 digits of phone number"""
        # Avoid N11 codes (211, 311, 411, etc.)
        first_digit = random.randint(2, 9)
        second_digit = random.randint(0, 9)
        if second_digit == 1 and first_digit == second_digit:
            second_digit = random.randint(2, 9)
        third_digit = random.randint(0, 9)
        
        return f"{first_digit}{second_digit}{third_digit}"
    
    def _generate_phone_line(self) -> str:
        """Generate last 4 digits of phone number"""
        # Avoid patterns like 0000, 1111, etc.
        digits = f"{random.randint(0, 9999):04d}"
        if len(set(digits)) == 1:  # All same digit
            digits = f"{random.randint(1000, 9999)}"
        return digits
    
    def generate_phone_number(self, state: Optional[str] = None, 
                            phone_type: str = "mobile") -> PhoneNumber:
        """Generate realistic phone number"""
        # Get area code
        if state:
            area_code = self._get_area_code_for_state(state)
        else:
            area_code = random.choice([code for codes in AREA_CODES_BY_STATE.values() for code in codes])
        
        # Generate number parts
        exchange = self._generate_phone_exchange()
        line = self._generate_phone_line()
        
        # Full number
        number = f"{exchange}{line}"
        
        # Extension for work phones
        extension = None
        if phone_type == "work" and random.random() < 0.3:
            extension = str(random.randint(100, 9999))
        
        # Apply variations
        is_valid = True
        do_not_call = random.random() < 0.05  # 5% on DNC list
        
        if self.variability:
            # Invalid numbers
            if self.variability.should_apply(0.02):
                if random.random() < 0.5:
                    # Known invalid pattern
                    full_number = random.choice(self.invalid_patterns)
                    area_code = full_number[:3]
                    number = full_number[3:]
                else:
                    # Invalid area code
                    area_code = random.choice(["000", "111", "999"])
                is_valid = False
            
            # Format variations are handled when displaying
        
        return PhoneNumber(
            phone_type=phone_type,
            country_code="+1",
            area_code=area_code,
            number=number,
            extension=extension,
            is_primary=(phone_type == "mobile"),
            is_valid=is_valid,
            do_not_call=do_not_call
        )
    
    def format_phone_number(self, phone: PhoneNumber) -> str:
        """Format phone number with variations"""
        base_number = f"{phone.area_code}{phone.number}"
        
        formats = [
            f"({phone.area_code}) {phone.number[:3]}-{phone.number[3:]}",
            f"{phone.area_code}-{phone.number[:3]}-{phone.number[3:]}",
            f"{phone.area_code}.{phone.number[:3]}.{phone.number[3:]}",
            f"+1 {phone.area_code} {phone.number[:3]} {phone.number[3:]}",
            f"1-{phone.area_code}-{phone.number[:3]}-{phone.number[3:]}",
            base_number,  # Just digits
            f"+1{base_number}"
        ]
        
        formatted = random.choice(formats)
        
        if phone.extension:
            ext_formats = [" ext. ", " x", " ext ", " #"]
            formatted += random.choice(ext_formats) + phone.extension
        
        # Apply variability
        if self.variability:
            formatted = self.variability.vary_format(formatted, 'phone')
        
        return formatted
    
    def _generate_username(self, first_name: str, last_name: str, 
                         birth_year: Optional[int] = None) -> str:
        """Generate email username"""
        first = first_name.lower().replace(" ", "").replace("-", "")
        last = last_name.lower().replace(" ", "").replace("-", "")
        f_initial = first[0] if first else "x"
        l_initial = last[0] if last else "x"
        
        # Year suffix
        year = ""
        if birth_year and random.random() < 0.3:
            year = str(birth_year)[-2:]  # Last 2 digits
        elif random.random() < 0.2:
            year = str(random.randint(1, 99))
        
        # Random suffix
        random_suffix = ""
        if random.random() < 0.15:
            random_suffix = str(random.randint(1, 999))
        
        # Select format
        format_choice = random.choice(self.email_formats)
        sep = random.choice(self.email_separators)
        
        username = format_choice.format(
            first=first,
            last=last,
            f=f_initial,
            l=l_initial,
            sep=sep,
            year=year,
            random=random_suffix
        )
        
        # Clean up
        username = username.replace("..", ".").replace("__", "_").replace("--", "-")
        username = username.strip("._-")
        
        return username
    
    def _select_email_domain(self, email_type: str, company_name: Optional[str] = None,
                           industry: Optional[str] = None) -> str:
        """Select appropriate email domain"""
        if email_type == "work" and company_name:
            # Generate company domain
            company_clean = company_name.lower()
            company_clean = re.sub(r'[^a-z0-9]', '', company_clean)
            
            if industry and industry in self.company_domains_by_industry:
                suffix = random.choice(self.company_domains_by_industry[industry])
                return f"{company_clean}.com"
            else:
                return f"{company_clean}.com"
        else:
            # Personal email
            domains = EMAIL_DOMAINS["personal"]
            # Weighted selection
            domain_names = [d[0] for d in domains]
            weights = [d[1] for d in domains]
            return random.choices(domain_names, weights=weights)[0]
    
    def generate_email_address(self, first_name: str, last_name: str,
                             email_type: str = "personal",
                             birth_year: Optional[int] = None,
                             company_name: Optional[str] = None,
                             industry: Optional[str] = None) -> EmailAddress:
        """Generate realistic email address"""
        username = self._generate_username(first_name, last_name, birth_year)
        domain = self._select_email_domain(email_type, company_name, industry)
        
        email = f"{username}@{domain}"
        
        # Data quality
        is_valid = True
        is_bounced = False
        
        if self.variability:
            # Invalid emails
            if self.variability.should_apply(0.05):
                if random.random() < 0.3:
                    # Missing @ symbol
                    email = username + domain
                elif random.random() < 0.5:
                    # Double @
                    email = username + "@@" + domain
                elif random.random() < 0.7:
                    # Missing domain
                    email = username + "@"
                else:
                    # Invalid domain
                    email = username + "@" + domain.replace(".com", "")
                is_valid = False
            
            # Bounced emails
            if self.variability.should_apply(0.08):
                is_bounced = True
            
            # Typos
            if self.variability.should_apply(0.02):
                email = self.variability.introduce_typo(email)
        
        return EmailAddress(
            email=email,
            email_type=email_type,
            is_primary=(email_type == "personal"),
            is_valid=is_valid,
            is_bounced=is_bounced,
            domain=domain
        )
    
    def generate_contact_set(self, first_name: str, last_name: str,
                           state: Optional[str] = None,
                           birth_year: Optional[int] = None,
                           company_name: Optional[str] = None,
                           industry: Optional[str] = None,
                           num_phones: int = 2,
                           num_emails: int = 2) -> Tuple[List[PhoneNumber], List[EmailAddress]]:
        """Generate complete contact information set"""
        phones = []
        emails = []
        
        # Generate phones
        phone_types = ["mobile", "home", "work"]
        used_types = []
        
        for i in range(num_phones):
            if i == 0:
                phone_type = "mobile"  # Always have mobile first
            else:
                available_types = [t for t in phone_types if t not in used_types]
                if available_types:
                    phone_type = random.choice(available_types)
                else:
                    phone_type = random.choice(phone_types)
            
            used_types.append(phone_type)
            phone = self.generate_phone_number(state, phone_type)
            phone.is_primary = (i == 0)
            phones.append(phone)
        
        # Generate emails
        email_types = ["personal", "work"] if company_name else ["personal"]
        
        for i in range(num_emails):
            if i == 0:
                email_type = "personal"  # Always have personal first
            else:
                email_type = random.choice(email_types)
            
            email = self.generate_email_address(
                first_name, last_name, email_type,
                birth_year, company_name, industry
            )
            email.is_primary = (i == 0)
            emails.append(email)
        
        return phones, emails