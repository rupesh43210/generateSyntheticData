import random
import string
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import math

from src.core.constants import (
    COMMON_FIRST_NAMES, ETHNIC_FIRST_NAMES, COMMON_LAST_NAMES,
    HYPHENATED_LAST_NAMES, NAME_PREFIXES, NAME_SUFFIXES
)
from src.core.variability import VariabilityEngine


class NameGenerator:
    """Advanced name generator with cultural diversity and realistic variations"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Name popularity by decade (simplified)
        self.name_popularity_by_decade = {
            1940: ["Robert", "James", "John", "William", "Richard", "Mary", "Patricia", "Barbara", "Betty", "Shirley"],
            1950: ["James", "Robert", "John", "Michael", "David", "Mary", "Linda", "Patricia", "Susan", "Deborah"],
            1960: ["Michael", "David", "John", "James", "Robert", "Lisa", "Mary", "Susan", "Karen", "Kimberly"],
            1970: ["Michael", "Christopher", "Jason", "David", "James", "Jennifer", "Amy", "Melissa", "Michelle", "Kimberly"],
            1980: ["Michael", "Christopher", "Matthew", "Joshua", "David", "Jessica", "Jennifer", "Amanda", "Ashley", "Sarah"],
            1990: ["Michael", "Christopher", "Matthew", "Joshua", "Jacob", "Jessica", "Ashley", "Emily", "Sarah", "Samantha"],
            2000: ["Jacob", "Michael", "Joshua", "Matthew", "Daniel", "Emily", "Emma", "Madison", "Abigail", "Olivia"],
            2010: ["Jacob", "Mason", "Noah", "William", "Liam", "Sophia", "Emma", "Olivia", "Isabella", "Ava"]
        }
        
        # Cultural distribution (can be configured)
        self.cultural_weights = {
            "anglo": 0.60,
            "hispanic": 0.18,
            "african": 0.13,
            "asian": 0.06,
            "other": 0.03
        }
        
        # Nickname mappings
        self.nicknames = {
            "Robert": ["Bob", "Bobby", "Rob", "Robbie"],
            "William": ["Will", "Bill", "Billy", "Liam"],
            "James": ["Jim", "Jimmy", "Jamie"],
            "John": ["Johnny", "Jack"],
            "Michael": ["Mike", "Mickey"],
            "Richard": ["Rick", "Dick", "Rich"],
            "Joseph": ["Joe", "Joey"],
            "Thomas": ["Tom", "Tommy"],
            "Charles": ["Charlie", "Chuck", "Chas"],
            "Christopher": ["Chris", "Kit"],
            "Daniel": ["Dan", "Danny"],
            "Matthew": ["Matt", "Matty"],
            "Anthony": ["Tony"],
            "Donald": ["Don", "Donnie"],
            "Kenneth": ["Ken", "Kenny"],
            "Steven": ["Steve"],
            "Edward": ["Ed", "Eddie"],
            "Andrew": ["Andy", "Drew"],
            "Timothy": ["Tim", "Timmy"],
            "Elizabeth": ["Liz", "Beth", "Betty", "Eliza", "Lizzie"],
            "Patricia": ["Pat", "Patty", "Trish"],
            "Jennifer": ["Jen", "Jenny"],
            "Margaret": ["Maggie", "Meg", "Peggy"],
            "Katherine": ["Kate", "Katie", "Kathy", "Kit"],
            "Deborah": ["Deb", "Debbie"],
            "Jessica": ["Jess", "Jessie"],
            "Rebecca": ["Becca", "Becky"],
            "Stephanie": ["Steph", "Stevie"],
            "Christine": ["Chris", "Christie"],
            "Samantha": ["Sam", "Sammy"]
        }
        
    def _select_cultural_background(self) -> str:
        """Select cultural background based on weights"""
        return random.choices(
            list(self.cultural_weights.keys()),
            weights=list(self.cultural_weights.values())
        )[0]
    
    def _get_names_for_birth_year(self, birth_year: int, gender: str) -> List[str]:
        """Get period-appropriate names based on birth year"""
        decade = (birth_year // 10) * 10
        
        # Find closest decade
        available_decades = list(self.name_popularity_by_decade.keys())
        closest_decade = min(available_decades, key=lambda x: abs(x - decade))
        
        popular_names = self.name_popularity_by_decade.get(closest_decade, [])
        
        if gender == "M":
            return [n for n in popular_names if n in COMMON_FIRST_NAMES["M"]]
        else:
            return [n for n in popular_names if n in COMMON_FIRST_NAMES["F"]]
    
    def generate_first_name(self, gender: str, birth_year: Optional[int] = None,
                          cultural_background: Optional[str] = None) -> str:
        """Generate culturally appropriate first name"""
        if not cultural_background:
            cultural_background = self._select_cultural_background()
        
        # Use period-appropriate names if birth year provided
        if birth_year and random.random() < 0.7:  # 70% chance of period-appropriate name
            period_names = self._get_names_for_birth_year(birth_year, gender)
            if period_names:
                return random.choice(period_names)
        
        # Select from cultural name pools
        if cultural_background in ["hispanic", "asian", "african"] and cultural_background in ETHNIC_FIRST_NAMES:
            if random.random() < 0.8:  # 80% chance of ethnic name for non-anglo
                ethnic_names = ETHNIC_FIRST_NAMES[cultural_background].get(gender, [])
                if ethnic_names:
                    return random.choice(ethnic_names)
        
        # Fall back to common names
        # Handle Other/Unknown genders by randomly choosing from M/F
        if gender in ['O', 'U']:
            gender = random.choice(['M', 'F'])
        return random.choice(COMMON_FIRST_NAMES[gender])
    
    def generate_middle_name(self, gender: str, has_middle: float = 0.85) -> Optional[str]:
        """Generate middle name or initial"""
        if random.random() > has_middle:
            return None
            
        # Sometimes use just initial
        if random.random() < 0.15:
            return random.choice(string.ascii_uppercase) + "."
        
        # Sometimes use family name as middle name
        if random.random() < 0.1:
            return random.choice(COMMON_LAST_NAMES)
        
        # Regular middle name
        # Handle Other/Unknown genders by randomly choosing from M/F
        if gender in ['O', 'U']:
            gender = random.choice(['M', 'F'])
        return random.choice(COMMON_FIRST_NAMES[gender])
    
    def generate_last_name(self, cultural_background: Optional[str] = None,
                         is_hyphenated: float = 0.02) -> str:
        """Generate last name with possible hyphenation"""
        if random.random() < is_hyphenated:
            # Hyphenated last name
            name_pair = random.choice(HYPHENATED_LAST_NAMES)
            return f"{name_pair[0]}-{name_pair[1]}"
        
        # Cultural last names could be added here
        # For now, use common last names
        return random.choice(COMMON_LAST_NAMES)
    
    def generate_prefix(self, age: int, gender: str, has_prefix: float = 0.05) -> Optional[str]:
        """Generate name prefix based on age and gender"""
        if random.random() > has_prefix:
            return None
            
        professional_prefixes = ["Dr.", "Prof."]
        military_prefixes = ["Capt.", "Lt.", "Col.", "Gen."]
        civil_prefixes = ["Hon.", "Rev.", "Sen.", "Rep."]
        
        # Age-based logic
        if age < 30:
            return None  # Young people less likely to have prefixes
        elif age < 40 and random.random() < 0.3:
            return random.choice(professional_prefixes)
        elif age >= 40:
            prefix_pool = professional_prefixes + military_prefixes + civil_prefixes
            return random.choice(prefix_pool)
        
        # Gender-based traditional prefixes
        if gender == "F":
            return random.choice(["Ms.", "Mrs.", "Miss"])
        else:
            return "Mr."
    
    def generate_suffix(self, has_suffix: float = 0.08) -> Optional[str]:
        """Generate name suffix"""
        if random.random() > has_suffix:
            return None
            
        # Generational suffixes more common
        if random.random() < 0.6:
            return random.choice(["Jr.", "Sr.", "II", "III", "IV"])
        else:
            # Professional suffixes
            return random.choice(["PhD", "MD", "JD", "CPA", "MBA", "RN", "DDS", "DVM", "Esq."])
    
    def generate_nickname(self, first_name: str, use_nickname: float = 0.15) -> Optional[str]:
        """Generate nickname based on first name"""
        if random.random() > use_nickname:
            return None
            
        if first_name in self.nicknames:
            return random.choice(self.nicknames[first_name])
        
        # Generic nickname patterns
        if len(first_name) > 4:
            return first_name[:3] + "y"  # Bobby, Jimmy, etc.
        
        return None
    
    def generate_full_name(self, gender: str, birth_date: date,
                         include_maiden: bool = False) -> Dict[str, Optional[str]]:
        """Generate complete name with all components"""
        birth_year = birth_date.year
        age = (datetime.now().date() - birth_date).days // 365
        
        cultural_background = self._select_cultural_background()
        
        # Generate name components
        first_name = self.generate_first_name(gender, birth_year, cultural_background)
        middle_name = self.generate_middle_name(gender)
        last_name = self.generate_last_name(cultural_background)
        prefix = self.generate_prefix(age, gender)
        suffix = self.generate_suffix()
        nickname = self.generate_nickname(first_name)
        
        # Maiden name for some females
        maiden_name = None
        if include_maiden and gender == "F" and age > 25 and random.random() < 0.3:
            maiden_name = self.generate_last_name()
        
        # Apply variability if engine provided
        if self.variability:
            first_name = self.variability.introduce_typo(first_name) if random.random() < 0.02 else first_name
            last_name = self.variability.introduce_typo(last_name) if random.random() < 0.02 else last_name
            
            # Format variations
            if random.random() < 0.05:
                first_name = self.variability.vary_format(first_name, 'name')
            if random.random() < 0.05:
                last_name = self.variability.vary_format(last_name, 'name')
        
        return {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "prefix": prefix,
            "suffix": suffix,
            "nickname": nickname,
            "maiden_name": maiden_name,
            "cultural_background": cultural_background
        }
    
    def generate_related_name(self, base_name: Dict[str, Optional[str]], 
                            relationship: str) -> Dict[str, Optional[str]]:
        """Generate related names (family members)"""
        new_name = base_name.copy()
        
        if relationship in ["spouse", "sibling"]:
            # Same last name (usually)
            if random.random() < 0.9:
                new_name["last_name"] = base_name["last_name"]
            
            # Different first name
            gender = random.choice(["M", "F"])
            new_name["first_name"] = self.generate_first_name(
                gender, 
                cultural_background=base_name.get("cultural_background")
            )
            new_name["middle_name"] = self.generate_middle_name(gender)
            
        elif relationship == "child":
            # Same last name
            new_name["last_name"] = base_name["last_name"]
            
            # Sometimes use parent's name as middle name
            if random.random() < 0.15:
                new_name["middle_name"] = base_name["first_name"]
            
            # Might have Jr./III suffix
            if base_name.get("suffix") in ["Jr.", "II", "III"]:
                suffix_map = {"Jr.": "III", "II": "III", "III": "IV"}
                new_name["suffix"] = suffix_map.get(base_name["suffix"], None)
        
        return new_name