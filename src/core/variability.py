import random
import string
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

from src.core.constants import TYPO_PATTERNS, COMMON_MISSPELLINGS


class VariabilityEngine:
    """Engine for introducing realistic data quality issues and variations"""
    
    def __init__(self, config: Dict[str, float]):
        self.missing_data_rate = config.get('missing_data_rate', 0.05)
        self.typo_rate = config.get('typo_rate', 0.02)
        self.duplicate_rate = config.get('duplicate_rate', 0.001)
        self.outlier_rate = config.get('outlier_rate', 0.01)
        self.inconsistency_rate = config.get('inconsistency_rate', 0.03)
        
    def should_apply(self, rate: float) -> bool:
        """Determine if a variation should be applied based on rate"""
        return random.random() < rate
    
    def make_missing(self, value: Any, required: bool = False) -> Optional[Any]:
        """Randomly make data missing based on configuration"""
        if required or not self.should_apply(self.missing_data_rate):
            return value
        return None
    
    def introduce_typo(self, text: str) -> str:
        """Introduce realistic typos into text"""
        if not text or not self.should_apply(self.typo_rate):
            return text
        
        typo_type = random.choice(['swap', 'missing', 'double', 'misspell', 'case'])
        
        if typo_type == 'swap' and len(text) > 2:
            # Swap adjacent characters
            pos = random.randint(0, len(text) - 2)
            chars = list(text)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            return ''.join(chars)
            
        elif typo_type == 'missing' and len(text) > 3:
            # Remove a character
            pos = random.randint(1, len(text) - 2)
            return text[:pos] + text[pos + 1:]
            
        elif typo_type == 'double':
            # Double a character
            pos = random.randint(0, len(text) - 1)
            return text[:pos] + text[pos] + text[pos:]
            
        elif typo_type == 'misspell':
            # Use common misspelling patterns
            for word, misspellings in COMMON_MISSPELLINGS.items():
                if word.lower() in text.lower():
                    misspelled = random.choice(misspellings)
                    return re.sub(word, misspelled, text, flags=re.IGNORECASE)
            
            # Use typo patterns
            for correct, typo in TYPO_PATTERNS:
                if correct in text:
                    return text.replace(correct, typo, 1)
                    
        elif typo_type == 'case':
            # Random case changes
            if len(text) > 0:
                pos = random.randint(0, len(text) - 1)
                chars = list(text)
                chars[pos] = chars[pos].swapcase()
                return ''.join(chars)
        
        return text
    
    def vary_format(self, value: str, value_type: str) -> str:
        """Introduce format variations based on value type"""
        if not self.should_apply(self.inconsistency_rate):
            return value
            
        if value_type == 'name':
            variations = [
                lambda x: x.upper(),
                lambda x: x.lower(),
                lambda x: x.title(),
                lambda x: x.replace('-', ' '),
                lambda x: x.replace(' ', '-'),
                lambda x: x[0] + '.' if len(x) > 1 else x  # Initial only
            ]
        elif value_type == 'phone':
            # Different phone formats
            if len(value) >= 10:
                digits = ''.join(c for c in value if c.isdigit())
                if len(digits) >= 10:
                    variations = [
                        lambda x: f"({x[:3]}) {x[3:6]}-{x[6:10]}",
                        lambda x: f"{x[:3]}-{x[3:6]}-{x[6:10]}",
                        lambda x: f"{x[:3]}.{x[3:6]}.{x[6:10]}",
                        lambda x: f"+1{x}",
                        lambda x: f"1-{x[:3]}-{x[3:6]}-{x[6:10]}",
                        lambda x: x  # Just digits
                    ]
                    return random.choice(variations)(digits)
        elif value_type == 'date':
            # Different date formats
            try:
                if isinstance(value, str):
                    dt = datetime.strptime(value, "%Y-%m-%d")
                else:
                    dt = value
                formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y%m%d", "%b %d, %Y", "%d-%b-%Y"]
                return dt.strftime(random.choice(formats))
            except:
                pass
        elif value_type == 'ssn':
            # SSN format variations
            if len(value) >= 9:
                digits = ''.join(c for c in value if c.isdigit())
                if len(digits) >= 9:
                    variations = [
                        lambda x: f"{x[:3]}-{x[3:5]}-{x[5:9]}",
                        lambda x: f"{x[:3]} {x[3:5]} {x[5:9]}",
                        lambda x: x,  # No formatting
                        lambda x: f"***-**-{x[5:9]}",  # Partial masking
                        lambda x: f"{x[:3]}-**-****"  # Partial masking
                    ]
                    return random.choice(variations)(digits)
                    
        return value
    
    def create_outlier(self, value: Any, value_type: str) -> Any:
        """Create outlier values based on type"""
        if not self.should_apply(self.outlier_rate):
            return value
            
        if value_type == 'age':
            # Unrealistic ages
            return random.choice([0, 1, 120, 150, 200, -5])
        elif value_type == 'income':
            # Extreme incomes
            if random.random() < 0.5:
                return random.randint(1000000, 10000000)  # Very high
            else:
                return random.choice([0, 1, -1000])  # Very low or negative
        elif value_type == 'credit_score':
            # Invalid credit scores
            return random.choice([0, 100, 200, 900, 1000, -100])
        elif value_type == 'phone':
            # Invalid phone numbers
            return random.choice(["0000000000", "1111111111", "9999999999", "123456789"])
        elif value_type == 'email':
            # Invalid emails
            return random.choice([
                "notanemail",
                "@example.com",
                "user@",
                "user@@example.com",
                "user@example",
                ""
            ])
            
        return value
    
    def add_noise_to_numeric(self, value: float, noise_percent: float = 0.05) -> float:
        """Add noise to numeric values"""
        if not self.should_apply(self.inconsistency_rate):
            return value
        
        noise = value * noise_percent * (2 * random.random() - 1)
        return value + noise
    
    def create_partial_value(self, value: str, value_type: str) -> str:
        """Create partial/incomplete values"""
        if not value or not self.should_apply(self.missing_data_rate / 2):
            return value
            
        if value_type == 'address':
            # Missing apartment number, incomplete street, etc.
            parts = value.split(',')
            if len(parts) > 1:
                # Remove random part
                parts.pop(random.randint(0, len(parts) - 1))
                return ', '.join(parts)
        elif value_type == 'name':
            # Missing middle name, initial only, etc.
            parts = value.split()
            if len(parts) > 1:
                # Maybe just use initial
                if random.random() < 0.5:
                    idx = random.randint(0, len(parts) - 1)
                    parts[idx] = parts[idx][0] + '.'
                else:
                    # Remove a part
                    parts.pop(random.randint(0, len(parts) - 1))
                return ' '.join(parts)
        elif value_type == 'phone':
            # Partial phone number
            if len(value) > 7:
                return value[:-random.randint(1, 3)]
                
        return value
    
    def create_duplicate_variation(self, value: Any) -> Any:
        """Create slight variations for duplicates"""
        if isinstance(value, str):
            variations = [
                lambda x: x + " ",  # Extra space
                lambda x: " " + x,  # Leading space
                lambda x: x.replace(' ', '  '),  # Double space
                lambda x: self.introduce_typo(x),  # Small typo
                lambda x: self.vary_format(x, 'name')  # Format change
            ]
            return random.choice(variations)(value)
        return value
    
    def apply_temporal_drift(self, value: Any, years_passed: int) -> Any:
        """Apply temporal changes to values over time"""
        if isinstance(value, (int, float)):
            # Numeric drift (e.g., salary increases)
            annual_change = 0.03  # 3% annual change
            multiplier = (1 + annual_change) ** years_passed
            return value * multiplier
        return value