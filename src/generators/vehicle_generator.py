import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import string

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field


class Vehicle(BaseModel):
    vin: str
    year: int
    make: str
    model: str
    trim_level: str
    body_style: str
    engine: str
    transmission: str
    drivetrain: str
    exterior_color: str
    interior_color: str
    fuel_type: str
    mpg_city: int
    mpg_highway: int
    purchase_date: date
    purchase_price: float
    current_mileage: int
    license_plate: str
    registration_state: str
    registration_expiry: date
    is_leased: bool
    lease_monthly_payment: Optional[float] = None
    lease_end_date: Optional[date] = None


class InsurancePolicy(BaseModel):
    policy_number: str
    insurance_company: str
    policy_type: str  # liability, comprehensive, collision, full coverage
    monthly_premium: float
    deductible: int
    coverage_limits: Dict[str, int]
    policy_start_date: date
    policy_end_date: date
    primary_driver: str
    additional_drivers: List[str] = Field(default_factory=list)


class MaintenanceRecord(BaseModel):
    service_date: date
    mileage_at_service: int
    service_type: str
    description: str
    cost: float
    service_provider: str
    next_service_due: Optional[date] = None
    next_service_mileage: Optional[int] = None


class Violation(BaseModel):
    violation_date: date
    violation_type: str
    fine_amount: float
    location: str
    officer_badge: str
    court_date: Optional[date] = None
    points_assessed: int
    paid: bool


class VehicleProfile(BaseModel):
    vehicles: List[Vehicle] = Field(default_factory=list)
    insurance_policies: List[InsurancePolicy] = Field(default_factory=list)
    maintenance_records: List[MaintenanceRecord] = Field(default_factory=list)
    violations: List[Violation] = Field(default_factory=list)
    drivers_license_number: str
    drivers_license_state: str
    drivers_license_class: str
    drivers_license_expiry: date
    drivers_license_issue_date: date
    cdl_endorsements: List[str] = Field(default_factory=list)


class VehicleGenerator:
    """Generator for comprehensive vehicle and automotive data"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Vehicle data by year (more recent years have different popular models)
        self.vehicles_by_year = {
            2024: {
                "Toyota": [
                    ("Camry", ["LE", "SE", "XLE", "XSE", "TRD"], "Sedan"),
                    ("RAV4", ["LE", "XLE", "Adventure", "Limited", "Prime"], "SUV"),
                    ("Corolla", ["L", "LE", "SE", "XLE"], "Sedan"),
                    ("Highlander", ["LE", "XLE", "Limited", "Platinum"], "SUV"),
                    ("Prius", ["LE", "XLE", "Limited"], "Hatchback"),
                    ("Tacoma", ["SR", "SR5", "TRD Sport", "TRD Off-Road", "Limited"], "Truck")
                ],
                "Honda": [
                    ("Accord", ["LX", "Sport", "EX", "EX-L", "Touring"], "Sedan"),
                    ("Civic", ["LX", "Sport", "EX", "EX-L", "Touring", "Type R"], "Sedan"),
                    ("CR-V", ["LX", "EX", "EX-L", "Touring"], "SUV"),
                    ("Pilot", ["LX", "EX", "EX-L", "Touring", "Elite"], "SUV"),
                    ("Ridgeline", ["Sport", "RTL", "RTL-E", "Black Edition"], "Truck")
                ],
                "Ford": [
                    ("F-150", ["Regular Cab", "SuperCab", "SuperCrew", "Lightning"], "Truck"),
                    ("Escape", ["S", "SE", "SEL", "Titanium"], "SUV"),
                    ("Explorer", ["Base", "XLT", "Limited", "Platinum", "ST"], "SUV"),
                    ("Mustang", ["EcoBoost", "GT", "Mach-E"], "Coupe"),
                    ("Edge", ["SE", "SEL", "Titanium", "ST"], "SUV")
                ],
                "Chevrolet": [
                    ("Silverado", ["Work Truck", "Custom", "LT", "RST", "LTZ", "High Country"], "Truck"),
                    ("Equinox", ["L", "LS", "LT", "Premier"], "SUV"),
                    ("Malibu", ["L", "LS", "LT", "Premier"], "Sedan"),
                    ("Tahoe", ["LS", "LT", "RST", "Premier", "High Country"], "SUV"),
                    ("Camaro", ["1LS", "1LT", "2LT", "1SS", "2SS", "ZL1"], "Coupe")
                ],
                "Nissan": [
                    ("Altima", ["S", "SV", "SL", "Platinum"], "Sedan"),
                    ("Sentra", ["S", "SV", "SR"], "Sedan"),
                    ("Rogue", ["S", "SV", "SL", "Platinum"], "SUV"),
                    ("Pathfinder", ["S", "SV", "SL", "Platinum"], "SUV"),
                    ("Frontier", ["S", "SV", "Pro-4X"], "Truck")
                ],
                "BMW": [
                    ("3 Series", ["330i", "M340i", "330i xDrive", "M3"], "Sedan"),
                    ("X3", ["sDrive30i", "xDrive30i", "M40i", "X3 M"], "SUV"),
                    ("5 Series", ["530i", "540i", "M550i", "M5"], "Sedan"),
                    ("X5", ["sDrive40i", "xDrive40i", "xDrive50i", "X5 M"], "SUV")
                ],
                "Mercedes-Benz": [
                    ("C-Class", ["C300", "C43 AMG", "C63 AMG"], "Sedan"),
                    ("E-Class", ["E350", "E450", "E53 AMG", "E63 AMG"], "Sedan"),
                    ("GLC", ["GLC300", "GLC43 AMG", "GLC63 AMG"], "SUV"),
                    ("GLE", ["GLE350", "GLE450", "GLE53 AMG", "GLE63 AMG"], "SUV")
                ]
            }
        }
        
        # Common makes and models for older years
        self.older_vehicles = {
            "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Tacoma", "Tundra", "4Runner"],
            "Honda": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Fit", "HR-V", "Ridgeline"],
            "Ford": ["F-150", "Focus", "Fusion", "Escape", "Explorer", "Mustang", "Edge", "Expedition"],
            "Chevrolet": ["Silverado", "Cruze", "Malibu", "Equinox", "Tahoe", "Suburban", "Camaro", "Corvette"],
            "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Frontier", "Titan", "Maxima", "Murano"],
            "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Compass", "Renegade", "Gladiator"],
            "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Genesis", "Veloster", "Palisade"],
            "Kia": ["Forte", "Optima", "Sorento", "Sportage", "Soul", "Stinger", "Telluride"],
            "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf", "Beetle", "Touareg"],
            "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-9", "MX-5 Miata", "CX-3", "CX-30"],
            "Subaru": ["Impreza", "Legacy", "Outback", "Forester", "Ascent", "WRX", "Crosstrek"],
            "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series", "X1", "4 Series"],
            "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC", "GLE", "A-Class", "CLA"],
            "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7", "A8", "TT"],
            "Lexus": ["ES", "IS", "RX", "NX", "GX", "LX", "LS", "GS"],
            "Acura": ["ILX", "TLX", "RDX", "MDX", "NSX", "TL", "TSX"],
            "Infiniti": ["Q50", "Q60", "QX50", "QX60", "QX80", "G35", "G37"],
            "Cadillac": ["ATS", "CTS", "XTS", "XT4", "XT5", "XT6", "Escalade"],
            "Lincoln": ["MKZ", "Continental", "MKX", "Navigator", "MKC", "Corsair"],
            "Buick": ["Encore", "Envision", "Enclave", "Regal", "LaCrosse", "Verano"],
            "GMC": ["Sierra", "Terrain", "Acadia", "Yukon", "Canyon", "Savana"],
            "Ram": ["1500", "2500", "3500", "ProMaster", "ProMaster City"],
            "Mitsubishi": ["Mirage", "Lancer", "Outlander", "Eclipse Cross", "Montero"],
            "Volvo": ["S60", "S90", "XC40", "XC60", "XC90", "V60", "V90"]
        }
        
        # Engine types
        self.engines = {
            "4-cylinder": ["2.0L I4", "2.4L I4", "1.8L I4", "2.5L I4", "1.6L I4 Turbo", "2.0L I4 Turbo"],
            "6-cylinder": ["3.5L V6", "3.0L V6", "2.7L V6 Turbo", "3.6L V6", "2.5L V6"],
            "8-cylinder": ["5.0L V8", "6.2L V8", "5.7L V8", "4.6L V8", "3.5L V8 Twin Turbo"],
            "Electric": ["Electric Motor", "Dual Motor AWD", "Single Motor RWD", "Triple Motor"],
            "Hybrid": ["2.5L I4 Hybrid", "3.5L V6 Hybrid", "2.0L I4 Plug-in Hybrid"]
        }
        
        # Colors
        self.exterior_colors = [
            "White", "Black", "Silver", "Gray", "Red", "Blue", "Green", "Brown",
            "Pearl White", "Metallic Black", "Gunmetal Gray", "Navy Blue", "Forest Green",
            "Burgundy", "Gold", "Orange", "Yellow", "Purple", "Bronze", "Beige"
        ]
        
        self.interior_colors = [
            "Black", "Gray", "Beige", "Tan", "Brown", "Charcoal", "Ivory", "Saddle",
            "Espresso", "Stone", "Parchment", "Ebony", "Cashmere", "Mocha"
        ]
        
        # Fuel types
        self.fuel_types = ["Gasoline", "Diesel", "Hybrid", "Electric", "Plug-in Hybrid", "E85", "CNG"]
        
        # License plate patterns by state
        self.license_patterns = {
            "CA": "1ABC234",  # California
            "TX": "ABC1234",  # Texas
            "FL": "123ABC",   # Florida
            "NY": "ABC1234",  # New York
            "PA": "ABC1234",  # Pennsylvania
            "IL": "AB12345",  # Illinois
            "OH": "ABC1234",  # Ohio
            "GA": "ABC1234",  # Georgia
            "NC": "ABC1234",  # North Carolina
            "MI": "ABC1234",  # Michigan
            "NJ": "A12BCD",   # New Jersey
            "VA": "ABC1234",  # Virginia
            "WA": "ABC1234",  # Washington
            "AZ": "ABC1234",  # Arizona
            "MA": "123ABC",   # Massachusetts
            "TN": "ABC123",   # Tennessee
            "IN": "123ABC",   # Indiana
            "MO": "AB1C2D",   # Missouri
            "MD": "1AB2345",  # Maryland
            "WI": "ABC1234"   # Wisconsin
        }
        
        # Insurance companies
        self.insurance_companies = [
            "State Farm", "GEICO", "Progressive", "Allstate", "USAA", "Liberty Mutual",
            "Farmers", "Nationwide", "American Family", "Erie", "Auto-Owners",
            "Travelers", "The General", "Esurance", "Root", "Lemonade"
        ]
        
        # Service providers
        self.service_providers = [
            "Jiffy Lube", "Valvoline Instant Oil Change", "Midas", "Meineke",
            "Firestone Complete Auto Care", "Mavis Discount Tire", "NTB",
            "Pep Boys", "AutoZone", "Dealership Service Center", "Local Garage",
            "Costco Auto Service", "Sam's Club Auto Service", "Walmart Auto Care"
        ]
        
        # Violation types
        self.violation_types = [
            ("Speeding", 150, 3, 0.15),
            ("Running Red Light", 200, 3, 0.05),
            ("Improper Lane Change", 125, 2, 0.08),
            ("Following Too Closely", 100, 2, 0.03),
            ("Failure to Yield", 175, 3, 0.04),
            ("Parking Violation", 25, 0, 0.20),
            ("Expired Registration", 75, 0, 0.06),
            ("Seatbelt Violation", 50, 0, 0.08),
            ("Cell Phone Use", 100, 1, 0.10),
            ("Reckless Driving", 300, 4, 0.02),
            ("DUI", 1500, 6, 0.01),
            ("No Insurance", 500, 0, 0.03)
        ]
        
        # License classes
        self.license_classes = {
            "Class D": 0.85,  # Regular driver's license
            "Class M": 0.10,  # Motorcycle
            "Class A": 0.03,  # Commercial - Tractor-trailers
            "Class B": 0.015, # Commercial - Large trucks
            "Class C": 0.005  # Commercial - Small trucks
        }
        
        # CDL Endorsements
        self.cdl_endorsements = [
            "H - Hazmat", "N - Tank Vehicles", "P - Passenger", "S - School Bus",
            "T - Double/Triple Trailers", "X - Hazmat + Tank"
        ]
    
    def generate_vin(self) -> str:
        """Generate a realistic but fake VIN"""
        # VIN format: WMI(3) + VDS(6) + VIS(8) = 17 characters
        # Using fake manufacturer codes to avoid real VINs
        wmi_codes = ["1FA", "1G1", "1HG", "1N4", "2T1", "3VW", "4T1", "5NP"]
        wmi = random.choice(wmi_codes)
        
        # Vehicle descriptor section (6 chars)
        vds = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Vehicle identifier section (8 chars) - last 4 are always numeric
        vis_alpha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        vis_numeric = ''.join(random.choices(string.digits, k=4))
        
        return wmi + vds + vis_alpha + vis_numeric
    
    def generate_license_plate(self, state: str) -> str:
        """Generate license plate based on state pattern"""
        pattern = self.license_patterns.get(state, "ABC1234")
        
        plate = ""
        for char in pattern:
            if char.isalpha():
                plate += random.choice(string.ascii_uppercase)
            elif char.isdigit():
                plate += random.choice(string.digits)
            else:
                plate += char
        
        return plate
    
    def generate_vehicle(self, owner_age: int, income: float, state: str) -> Vehicle:
        """Generate a realistic vehicle based on demographics"""
        # Determine vehicle age preference based on income and age
        if income > 80000 and random.random() < 0.4:
            # Higher income - newer vehicles
            vehicle_year = random.randint(2020, 2024)
        elif income > 50000:
            # Middle income - mix of ages
            vehicle_year = random.randint(2015, 2023)
        elif owner_age < 25:
            # Young drivers - older/cheaper vehicles
            vehicle_year = random.randint(2005, 2018)
        else:
            # Lower income - older vehicles
            vehicle_year = random.randint(2008, 2020)
        
        # Select make/model based on year and income
        if vehicle_year >= 2020 and income > 70000:
            # Luxury brands more likely for newer/higher income
            luxury_brands = ["BMW", "Mercedes-Benz", "Audi", "Lexus", "Acura", "Infiniti", "Cadillac"]
            if random.random() < 0.3:
                make = random.choice(luxury_brands)
            else:
                make = random.choice(list(self.older_vehicles.keys()))
        else:
            # Mainstream brands
            mainstream = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Hyundai", "Kia"]
            make = random.choice(mainstream)
        
        # Get model for the make
        if vehicle_year == 2024 and make in self.vehicles_by_year[2024]:
            model_data = random.choice(self.vehicles_by_year[2024][make])
            model = model_data[0]
            trim_level = random.choice(model_data[1])
            body_style = model_data[2]
        else:
            model = random.choice(self.older_vehicles.get(make, ["Unknown"]))
            trim_level = random.choice(["Base", "S", "SE", "SL", "EX", "LX", "Limited", "Premium"])
            body_styles = ["Sedan", "SUV", "Truck", "Hatchback", "Coupe", "Wagon", "Convertible"]
            body_style = random.choice(body_styles)
        
        # Generate engine based on body style and year
        if body_style == "Truck":
            engine_type = random.choice(["6-cylinder", "8-cylinder"])
        elif body_style == "SUV":
            engine_type = random.choice(["4-cylinder", "6-cylinder", "8-cylinder"])
        elif make in ["BMW", "Mercedes-Benz", "Audi", "Lexus"] and vehicle_year >= 2020:
            engine_type = random.choice(["4-cylinder", "6-cylinder", "8-cylinder", "Hybrid"])
        else:
            engine_type = random.choice(["4-cylinder", "6-cylinder"])
        
        if vehicle_year >= 2020 and random.random() < 0.15:
            # Electric vehicles more common in recent years
            engine_type = "Electric"
            fuel_type = "Electric"
        elif random.random() < 0.08:
            engine_type = "Hybrid"
            fuel_type = "Hybrid"
        else:
            fuel_type = "Gasoline"
        
        engine = random.choice(self.engines[engine_type])
        
        # Generate other specifications
        transmission = random.choices(
            ["Automatic", "Manual", "CVT"],
            weights=[0.85, 0.10, 0.05]
        )[0]
        
        drivetrain = random.choices(
            ["FWD", "RWD", "AWD", "4WD"],
            weights=[0.40, 0.25, 0.25, 0.10]
        )[0]
        
        # Colors
        exterior_color = random.choice(self.exterior_colors)
        interior_color = random.choice(self.interior_colors)
        
        # MPG based on engine type and vehicle type
        if fuel_type == "Electric":
            mpg_city = mpg_highway = 0  # Electric vehicles don't use MPG
        elif engine_type == "Hybrid":
            mpg_city = random.randint(35, 55)
            mpg_highway = random.randint(38, 58)
        elif engine_type == "8-cylinder":
            mpg_city = random.randint(15, 22)
            mpg_highway = random.randint(20, 28)
        elif engine_type == "6-cylinder":
            mpg_city = random.randint(20, 28)
            mpg_highway = random.randint(25, 35)
        else:  # 4-cylinder
            mpg_city = random.randint(25, 35)
            mpg_highway = random.randint(30, 42)
        
        # Purchase details
        vehicle_age = 2024 - vehicle_year
        purchase_date = date.today() - timedelta(days=vehicle_age * 365 + random.randint(0, 364))
        
        # Purchase price based on year, make, and body style
        base_price = 25000  # Starting point
        if make in ["BMW", "Mercedes-Benz", "Audi", "Lexus"]:
            base_price = 45000
        elif body_style == "Truck":
            base_price = 35000
        elif body_style == "SUV":
            base_price = 30000
        
        # Depreciation
        depreciation = 0.15 * vehicle_age  # 15% per year
        purchase_price = base_price * (1 - depreciation) * random.uniform(0.8, 1.2)
        
        # Current mileage
        annual_miles = random.randint(8000, 18000)
        current_mileage = vehicle_age * annual_miles + random.randint(0, 5000)
        
        # License plate and registration
        license_plate = self.generate_license_plate(state)
        registration_expiry = date.today() + timedelta(days=random.randint(30, 365))
        
        # Lease vs own
        is_leased = random.random() < 0.25  # 25% leased
        lease_payment = None
        lease_end = None
        
        if is_leased:
            lease_payment = purchase_price * 0.025  # Rough monthly lease calculation
            lease_end = purchase_date + timedelta(days=random.randint(1095, 1460))  # 3-4 years
        
        return Vehicle(
            vin=self.generate_vin(),
            year=vehicle_year,
            make=make,
            model=model,
            trim_level=trim_level,
            body_style=body_style,
            engine=engine,
            transmission=transmission,
            drivetrain=drivetrain,
            exterior_color=exterior_color,
            interior_color=interior_color,
            fuel_type=fuel_type,
            mpg_city=mpg_city,
            mpg_highway=mpg_highway,
            purchase_date=purchase_date,
            purchase_price=round(purchase_price, 2),
            current_mileage=current_mileage,
            license_plate=license_plate,
            registration_state=state,
            registration_expiry=registration_expiry,
            is_leased=is_leased,
            lease_monthly_payment=round(lease_payment, 2) if lease_payment else None,
            lease_end_date=lease_end
        )
    
    def generate_insurance_policy(self, vehicle: Vehicle, owner_age: int, 
                                primary_driver: str) -> InsurancePolicy:
        """Generate insurance policy for vehicle"""
        company = random.choice(self.insurance_companies)
        policy_number = f"{company[:3].upper()}{random.randint(1000000, 9999999)}"
        
        # Coverage type based on vehicle value and age
        vehicle_value = vehicle.purchase_price
        if vehicle_value > 30000 or vehicle.is_leased:
            policy_type = "Full Coverage"
            deductible = random.choice([250, 500, 1000])
            coverage_limits = {
                "bodily_injury_per_person": random.choice([100000, 250000, 500000]),
                "bodily_injury_per_accident": random.choice([300000, 500000, 1000000]),
                "property_damage": random.choice([100000, 250000, 500000]),
                "comprehensive": deductible,
                "collision": deductible,
                "uninsured_motorist": random.choice([100000, 250000])
            }
        elif vehicle_value > 15000:
            policy_type = random.choice(["Comprehensive", "Full Coverage"])
            deductible = random.choice([500, 1000, 2500])
            coverage_limits = {
                "bodily_injury_per_person": random.choice([50000, 100000, 250000]),
                "bodily_injury_per_accident": random.choice([100000, 300000, 500000]),
                "property_damage": random.choice([50000, 100000, 250000]),
                "comprehensive": deductible if policy_type == "Full Coverage" else 0,
                "collision": deductible if policy_type == "Full Coverage" else 0,
                "uninsured_motorist": random.choice([50000, 100000])
            }
        else:
            policy_type = "Liability Only"
            deductible = 0
            coverage_limits = {
                "bodily_injury_per_person": random.choice([25000, 50000, 100000]),
                "bodily_injury_per_accident": random.choice([50000, 100000, 300000]),
                "property_damage": random.choice([25000, 50000, 100000]),
                "comprehensive": 0,
                "collision": 0,
                "uninsured_motorist": 0
            }
        
        # Premium based on multiple factors
        base_premium = 100
        
        # Age factor
        if owner_age < 25:
            base_premium *= 1.8
        elif owner_age < 35:
            base_premium *= 1.2
        elif owner_age > 65:
            base_premium *= 1.1
        
        # Vehicle factor
        if vehicle.make in ["BMW", "Mercedes-Benz", "Audi"]:
            base_premium *= 1.5
        elif vehicle.body_style == "Sports Car":
            base_premium *= 1.8
        elif vehicle.body_style == "SUV":
            base_premium *= 1.1
        
        # Coverage factor
        if policy_type == "Full Coverage":
            base_premium *= 1.8
        elif policy_type == "Comprehensive":
            base_premium *= 1.4
        
        monthly_premium = base_premium * random.uniform(0.8, 1.2)
        
        # Policy dates
        policy_start = vehicle.purchase_date + timedelta(days=random.randint(0, 30))
        policy_end = policy_start + timedelta(days=random.randint(180, 365))
        
        return InsurancePolicy(
            policy_number=policy_number,
            insurance_company=company,
            policy_type=policy_type,
            monthly_premium=round(monthly_premium, 2),
            deductible=deductible,
            coverage_limits=coverage_limits,
            policy_start_date=policy_start,
            policy_end_date=policy_end,
            primary_driver=primary_driver,
            additional_drivers=[]  # Could add family members
        )
    
    def generate_maintenance_records(self, vehicle: Vehicle) -> List[MaintenanceRecord]:
        """Generate maintenance history for vehicle"""
        records = []
        vehicle_age = 2024 - vehicle.year
        
        # Regular maintenance based on mileage and age
        current_mileage = vehicle.current_mileage
        service_interval = 5000  # Oil change interval
        
        # Generate oil changes
        for mileage in range(service_interval, current_mileage, service_interval):
            # Calculate approximate date based on mileage
            miles_since_purchase = mileage - (current_mileage - vehicle_age * 12000)
            if miles_since_purchase > 0:
                days_since_purchase = (miles_since_purchase / 12000) * 365
                service_date = vehicle.purchase_date + timedelta(days=days_since_purchase)
                
                if service_date <= date.today():
                    cost = random.uniform(35, 85)
                    records.append(MaintenanceRecord(
                        service_date=service_date,
                        mileage_at_service=mileage,
                        service_type="Oil Change",
                        description="Regular oil and filter change",
                        cost=round(cost, 2),
                        service_provider=random.choice(self.service_providers),
                        next_service_due=service_date + timedelta(days=90),
                        next_service_mileage=mileage + service_interval
                    ))
        
        # Major services based on mileage
        major_services = [
            (30000, "30K Service", "Transmission service, brake inspection, belts/hoses", 300, 500),
            (60000, "60K Service", "Major service - timing belt, spark plugs, coolant flush", 800, 1200),
            (90000, "90K Service", "Transmission flush, brake service, fuel system cleaning", 600, 900),
            (120000, "120K Service", "Major overhaul - timing chain, water pump, belts", 1500, 2500)
        ]
        
        for milestone, service_name, description, min_cost, max_cost in major_services:
            if current_mileage >= milestone:
                # Calculate service date
                miles_at_service = milestone + random.randint(-2000, 5000)
                miles_since_purchase = miles_at_service - (current_mileage - vehicle_age * 12000)
                if miles_since_purchase > 0:
                    days_since_purchase = (miles_since_purchase / 12000) * 365
                    service_date = vehicle.purchase_date + timedelta(days=days_since_purchase)
                    
                    if service_date <= date.today():
                        cost = random.uniform(min_cost, max_cost)
                        records.append(MaintenanceRecord(
                            service_date=service_date,
                            mileage_at_service=miles_at_service,
                            service_type=service_name,
                            description=description,
                            cost=round(cost, 2),
                            service_provider=random.choice(self.service_providers)
                        ))
        
        # Random repairs
        if vehicle_age > 3 and random.random() < 0.4:
            repair_types = [
                ("Brake Replacement", "Front brake pads and rotors replaced", 400, 800),
                ("Tire Replacement", "Four new tires installed", 600, 1200),
                ("Battery Replacement", "New battery and testing", 120, 200),
                ("AC Repair", "A/C compressor and refrigerant service", 500, 1000),
                ("Transmission Repair", "Transmission service and minor repairs", 300, 800)
            ]
            
            num_repairs = random.randint(1, 3)
            for _ in range(num_repairs):
                repair = random.choice(repair_types)
                repair_date = vehicle.purchase_date + timedelta(days=random.randint(365, vehicle_age * 365))
                if repair_date <= date.today():
                    cost = random.uniform(repair[2], repair[3])
                    mileage = vehicle.current_mileage - random.randint(0, 20000)
                    
                    records.append(MaintenanceRecord(
                        service_date=repair_date,
                        mileage_at_service=max(0, mileage),
                        service_type="Repair",
                        description=repair[1],
                        cost=round(cost, 2),
                        service_provider=random.choice(self.service_providers)
                    ))
        
        return sorted(records, key=lambda x: x.service_date)
    
    def generate_violations(self, driver_age: int, years_driving: int) -> List[Violation]:
        """Generate traffic violations based on demographics"""
        violations = []
        
        # Calculate violation probability based on age and experience
        base_rate = 0.15  # 15% chance per year
        if driver_age < 25:
            violation_rate = base_rate * 2.0
        elif driver_age < 35:
            violation_rate = base_rate * 1.5
        elif driver_age > 65:
            violation_rate = base_rate * 0.7
        else:
            violation_rate = base_rate
        
        # Reduce rate for experienced drivers
        if years_driving > 10:
            violation_rate *= 0.8
        
        # Generate violations for each year of driving
        for year in range(min(years_driving, 10)):  # Look back max 10 years
            if random.random() < violation_rate:
                violation_type, base_fine, points, _ = random.choices(
                    self.violation_types,
                    weights=[v[3] for v in self.violation_types]
                )[0]
                
                violation_date = date.today() - timedelta(days=year * 365 + random.randint(0, 364))
                fine = base_fine * random.uniform(0.8, 1.5)
                
                # Generate location
                states = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI"]
                location = f"{random.choice(['Main St', 'Highway 101', 'Interstate 95', 'Broadway', 'Oak Ave'])}, {random.choice(states)}"
                
                # Officer badge
                officer_badge = f"#{random.randint(1000, 9999)}"
                
                # Court date for major violations
                court_date = None
                if violation_type in ["DUI", "Reckless Driving"] or fine > 200:
                    court_date = violation_date + timedelta(days=random.randint(30, 90))
                
                # Payment status
                paid = random.random() < 0.85  # 85% paid
                
                violations.append(Violation(
                    violation_date=violation_date,
                    violation_type=violation_type,
                    fine_amount=round(fine, 2),
                    location=location,
                    officer_badge=officer_badge,
                    court_date=court_date,
                    points_assessed=points,
                    paid=paid
                ))
        
        return sorted(violations, key=lambda x: x.violation_date, reverse=True)
    
    def generate_drivers_license(self, age: int, state: str) -> Tuple[str, str, date, date, List[str]]:
        """Generate driver's license information"""
        # License number pattern varies by state
        license_patterns = {
            "CA": "A1234567",  # California
            "TX": "12345678",  # Texas
            "FL": "A123456789123",  # Florida
            "NY": "123456789",  # New York
            "default": "A1234567890"
        }
        
        pattern = license_patterns.get(state, license_patterns["default"])
        license_number = ""
        for char in pattern:
            if char.isalpha():
                license_number += random.choice(string.ascii_uppercase)
            else:
                license_number += random.choice(string.digits)
        
        # License class
        license_class = random.choices(
            list(self.license_classes.keys()),
            weights=list(self.license_classes.values())
        )[0]
        
        # Issue and expiry dates
        years_held = min(age - 16, random.randint(1, 20))
        issue_date = date.today() - timedelta(days=years_held * 365 + random.randint(0, 364))
        expiry_date = date.today() + timedelta(days=random.randint(30, 1095))
        
        # CDL endorsements for commercial licenses
        endorsements = []
        if license_class in ["Class A", "Class B", "Class C"]:
            num_endorsements = random.randint(0, 3)
            endorsements = random.sample(self.cdl_endorsements, min(num_endorsements, len(self.cdl_endorsements)))
        
        return license_number, license_class, issue_date, expiry_date, endorsements
    
    def generate_vehicle_profile(self, age: int, income: float, state: str, 
                               full_name: str) -> VehicleProfile:
        """Generate complete vehicle profile"""
        vehicles = []
        insurance_policies = []
        maintenance_records = []
        
        # Number of vehicles based on age and income
        if income > 100000:
            num_vehicles = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        elif income > 60000:
            num_vehicles = random.choices([1, 2], weights=[0.6, 0.4])[0]
        elif age < 25 or income < 30000:
            num_vehicles = random.choices([0, 1], weights=[0.3, 0.7])[0]
        else:
            num_vehicles = 1
        
        # Generate vehicles
        for _ in range(num_vehicles):
            vehicle = self.generate_vehicle(age, income, state)
            vehicles.append(vehicle)
            
            # Generate insurance for each vehicle
            insurance = self.generate_insurance_policy(vehicle, age, full_name)
            insurance_policies.append(insurance)
            
            # Generate maintenance records
            maintenance = self.generate_maintenance_records(vehicle)
            maintenance_records.extend(maintenance)
        
        # Driver's license info
        years_driving = max(0, age - 16)
        license_num, license_class, issue_date, expiry_date, endorsements = self.generate_drivers_license(age, state)
        
        # Generate violations
        violations = self.generate_violations(age, years_driving)
        
        return VehicleProfile(
            vehicles=vehicles,
            insurance_policies=insurance_policies,
            maintenance_records=maintenance_records,
            violations=violations,
            drivers_license_number=license_num,
            drivers_license_state=state,
            drivers_license_class=license_class,
            drivers_license_expiry=expiry_date,
            drivers_license_issue_date=issue_date,
            cdl_endorsements=endorsements
        )