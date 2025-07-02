import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import string

from src.core.constants import (
    STREET_TYPES, STREET_NAMES, APARTMENT_PREFIXES, CITY_STATE_ZIP_DATA
)
from src.core.variability import VariabilityEngine
from src.core.models import Address, AddressType


class AddressGenerator:
    """Advanced address generator with real geographic data and variations"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Build city lookup for performance
        self.cities_by_state = {}
        self.zip_by_city = {}
        for city, state, zips in CITY_STATE_ZIP_DATA:
            if state not in self.cities_by_state:
                self.cities_by_state[state] = []
            self.cities_by_state[state].append((city, zips))
            self.zip_by_city[f"{city},{state}"] = zips
        
        # Address patterns
        self.rural_indicators = ["Rural Route", "RR", "HC", "Highway Contract Route"]
        self.military_bases = [
            ("Fort Bragg", "NC", ["28307", "28308", "28310"]),
            ("Fort Hood", "TX", ["76544", "76545"]),
            ("Joint Base Lewis-McChord", "WA", ["98433", "98438"]),
            ("Camp Pendleton", "CA", ["92055", "92057", "92058"]),
            ("Fort Campbell", "KY", ["42223"]),
            ("Fort Benning", "GA", ["31905"]),
            ("Fort Carson", "CO", ["80913"])
        ]
        
        # PO Box patterns
        self.po_box_formats = [
            "PO Box {num}",
            "P.O. Box {num}"
        ]
        
        # International address formats (simplified)
        self.international_formats = {
            "UK": {
                "cities": ["London", "Manchester", "Birmingham", "Leeds", "Liverpool"],
                "postcodes": ["SW1A", "EC1A", "M1", "B1", "LS1", "L1"],
                "format": "{street}, {city}, {postcode}, United Kingdom"
            },
            "Canada": {
                "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
                "provinces": ["ON", "BC", "QC", "AB", "ON"],
                "format": "{street}, {city}, {province} {postal}, Canada"
            }
        }
    
    def _generate_street_number(self) -> str:
        """Generate realistic street numbers"""
        # Most addresses are in reasonable ranges
        if random.random() < 0.7:
            return str(random.randint(1, 999))
        elif random.random() < 0.9:
            return str(random.randint(1000, 9999))
        else:
            # Some addresses have letters or are very high
            if random.random() < 0.5:
                return str(random.randint(10000, 99999))
            else:
                return f"{random.randint(1, 999)}{random.choice(['A', 'B', 'C', '1/2'])}"
    
    def _generate_street_name(self) -> Tuple[str, str]:
        """Generate street name and type"""
        name = random.choice(STREET_NAMES)
        
        # Sometimes use numbered streets
        if random.random() < 0.15:
            number = random.randint(1, 200)
            ordinal = self._get_ordinal(number)
            name = ordinal
        
        # Select street type with realistic distribution
        street_type = random.choice(STREET_TYPES)
        
        # Sometimes use directional prefixes/suffixes
        if random.random() < 0.1:
            direction = random.choice(["N", "S", "E", "W", "NE", "NW", "SE", "SW"])
            if random.random() < 0.5:
                name = f"{direction} {name}"
            else:
                name = f"{name} {direction}"
        
        return name, street_type
    
    def _get_ordinal(self, num: int) -> str:
        """Convert number to ordinal (1st, 2nd, etc.)"""
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
        return f"{num}{suffix}"
    
    def _generate_apartment(self, include_apt: float = 0.3) -> Optional[str]:
        """Generate apartment/suite/unit information"""
        if random.random() > include_apt:
            return None
        
        prefix = random.choice(APARTMENT_PREFIXES)
        
        # Different apartment numbering schemes
        if random.random() < 0.4:
            # Just number
            number = random.randint(1, 999)
        elif random.random() < 0.7:
            # Letter + number
            letter = random.choice(string.ascii_uppercase)
            number = f"{letter}{random.randint(1, 99)}"
        else:
            # Floor + unit
            floor = random.randint(1, 50)
            unit = random.randint(1, 20)
            number = f"{floor}{unit:02d}"
        
        # Format variations
        if self.variability and self.variability.should_apply(0.1):
            formats = [
                f"{prefix} {number}",
                f"{prefix}. {number}",
                f"{prefix} #{number}",
                f", {prefix} {number}",
                f" - {prefix} {number}"
            ]
            return random.choice(formats)
        
        return f"{prefix} {number}"
    
    def generate_po_box(self) -> Dict[str, str]:
        """Generate PO Box address"""
        box_format = random.choice(self.po_box_formats)
        box_number = random.randint(1, 99999)
        
        city, state, zips = random.choice(CITY_STATE_ZIP_DATA)
        zip_code = random.choice(zips) + f"{random.randint(0, 9999):04d}"
        
        return {
            "street_1": box_format.format(num=box_number),
            "street_2": None,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
    
    def generate_rural_address(self) -> Dict[str, str]:
        """Generate rural route address"""
        rural_type = random.choice(self.rural_indicators)
        route_number = random.randint(1, 20)
        box_number = random.randint(1, 9999)
        
        # Rural areas - pick smaller cities/towns
        city, state, zips = random.choice(CITY_STATE_ZIP_DATA[-20:])  # Last entries tend to be smaller
        zip_code = random.choice(zips) + f"{random.randint(0, 9999):04d}"
        
        street_1 = f"{rural_type} {route_number} Box {box_number}"
        
        return {
            "street_1": street_1,
            "street_2": None,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
    
    def generate_military_address(self) -> Dict[str, str]:
        """Generate military base address"""
        base_name, state, zips = random.choice(self.military_bases)
        unit_types = ["Unit", "PSC", "CMR", "APO", "FPO"]
        unit_type = random.choice(unit_types)
        unit_number = random.randint(1000, 9999)
        
        street_1 = f"{unit_type} {unit_number}"
        street_2 = f"{base_name}"
        
        if unit_type in ["APO", "FPO"]:
            # Military overseas addresses
            state = random.choice(["AE", "AP", "AA"])  # Armed forces codes
            zip_code = f"{random.randint(9000, 9999):05d}"
        else:
            zip_code = random.choice(zips)
        
        return {
            "street_1": street_1,
            "street_2": street_2,
            "city": base_name.split()[0],  # First word of base name
            "state": state,
            "zip_code": zip_code
        }
    
    def generate_standard_address(self, city_state_zip: Optional[Tuple] = None) -> Dict[str, str]:
        """Generate standard residential/commercial address"""
        if not city_state_zip:
            city, state, zips = random.choice(CITY_STATE_ZIP_DATA)
        else:
            city, state, zips = city_state_zip
        
        # Generate street address
        street_num = self._generate_street_number()
        street_name, street_type = self._generate_street_name()
        street_1 = f"{street_num} {street_name} {street_type}"
        
        # Maybe add apartment
        apt = self._generate_apartment()
        street_2 = apt
        
        # Generate ZIP+4
        zip_base = random.choice(zips)
        zip_plus4 = f"{random.randint(0, 9999):04d}"
        zip_code = f"{zip_base}{zip_plus4}"
        
        # Apply variations
        if self.variability:
            # Street type variations
            if self.variability.should_apply(0.1):
                street_1 = self.variability.vary_format(street_1, 'address')
            
            # Missing ZIP+4
            if self.variability.should_apply(0.3):
                zip_code = zip_base
            
            # Typos
            if self.variability.should_apply(0.02):
                street_1 = self.variability.introduce_typo(street_1)
            if self.variability.should_apply(0.02):
                city = self.variability.introduce_typo(city)
        
        return {
            "street_1": street_1,
            "street_2": street_2,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
    
    def generate_address(self, address_type: AddressType = AddressType.CURRENT,
                       previous_addresses: Optional[List[Address]] = None) -> Address:
        """Generate complete address with specified type"""
        # Determine address style
        style_weights = {
            "standard": 0.85,
            "po_box": 0.08,
            "rural": 0.04,
            "military": 0.03
        }
        
        style = random.choices(
            list(style_weights.keys()),
            weights=list(style_weights.values())
        )[0]
        
        # Generate based on style
        if style == "po_box":
            addr_data = self.generate_po_box()
        elif style == "rural":
            addr_data = self.generate_rural_address()
        elif style == "military":
            addr_data = self.generate_military_address()
        else:
            # For previous addresses, maybe use same city
            if previous_addresses and random.random() < 0.3:
                prev_addr = random.choice(previous_addresses)
                city_state_zip = None
                for c, s, z in CITY_STATE_ZIP_DATA:
                    if c == prev_addr.city and s == prev_addr.state:
                        city_state_zip = (c, s, z)
                        break
                addr_data = self.generate_standard_address(city_state_zip)
            else:
                addr_data = self.generate_standard_address()
        
        # Set dates
        if address_type == AddressType.CURRENT:
            effective_date = date.today() - timedelta(days=random.randint(30, 1825))  # 1 month to 5 years
            end_date = None
        else:
            # Previous address
            years_ago = random.randint(2, 15)
            days_ago = years_ago * 365 + random.randint(0, 30)  # Add some randomness
            effective_date = date.today() - timedelta(days=days_ago)
            duration_days = random.randint(365, 365 * 5)
            end_date = effective_date + timedelta(days=duration_days)
        
        # Apply data quality issues
        is_valid = True
        if self.variability:
            # Some addresses might be invalid
            if self.variability.should_apply(0.02):
                is_valid = False
            
            # Partial addresses
            if self.variability.should_apply(0.03):
                if random.random() < 0.5 and addr_data["street_2"]:
                    addr_data["street_2"] = None  # Missing apartment
                elif random.random() < 0.3:
                    addr_data["zip_code"] = addr_data["zip_code"][:5]  # Missing +4
        
        return Address(
            address_type=address_type,
            street_1=addr_data["street_1"],
            street_2=addr_data.get("street_2"),
            city=addr_data["city"],
            state=addr_data["state"],
            zip_code=addr_data["zip_code"],
            country="USA",
            is_valid=is_valid,
            effective_date=effective_date,
            end_date=end_date
        )
    
    def generate_address_history(self, num_addresses: int = 3) -> List[Address]:
        """Generate realistic address history for a person"""
        addresses = []
        
        # Current address
        current = self.generate_address(AddressType.CURRENT)
        addresses.append(current)
        
        # Determine if we should include a billing address
        include_billing = random.random() < 0.7 and num_addresses > 1
        
        # Calculate how many previous addresses to generate
        num_previous = num_addresses - 1
        if include_billing:
            num_previous = max(0, num_addresses - 2)  # Reserve one slot for billing
        
        # Previous addresses
        for i in range(num_previous):
            prev = self.generate_address(AddressType.PREVIOUS, addresses)
            addresses.append(prev)
        
        # Add billing address if we have room
        if include_billing and len(addresses) < num_addresses:
            if random.random() < 0.8:
                # Same as current
                billing = current.model_copy()
                billing.address_type = AddressType.BILLING
                billing.address_id = str(random.randint(1000000, 9999999))
            else:
                billing = self.generate_address(AddressType.BILLING)
            addresses.append(billing)
        
        return addresses