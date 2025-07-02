"""
Travel and Location History Generator - Creates comprehensive travel patterns and location data
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import uuid

class TravelPurpose(Enum):
    BUSINESS = "business"
    VACATION = "vacation"
    FAMILY_VISIT = "family_visit"
    MEDICAL = "medical"
    EDUCATION = "education"
    CONFERENCE = "conference"
    PERSONAL = "personal"
    EMERGENCY = "emergency"

class TransportationMode(Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    CAR = "car"
    BUS = "bus"
    SHIP = "ship"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    WALKING = "walking"

class AccommodationType(Enum):
    HOTEL = "hotel"
    AIRBNB = "airbnb"
    FAMILY_HOME = "family_home"
    HOSTEL = "hostel"
    RESORT = "resort"
    CAMPING = "camping"
    BUSINESS_TRAVEL = "business_travel"
    VACATION_RENTAL = "vacation_rental"

class TravelEntry(BaseModel):
    entry_id: str
    departure_date: datetime
    return_date: Optional[datetime]
    origin_city: str
    origin_state: str
    origin_country: str
    destination_city: str
    destination_state: str
    destination_country: str
    purpose: TravelPurpose
    transportation_mode: TransportationMode
    accommodation_type: Optional[AccommodationType]
    accommodation_name: Optional[str]
    booking_reference: Optional[str]
    total_cost: Optional[float]
    travel_companions: List[str]
    notes: Optional[str]

class LocationVisit(BaseModel):
    visit_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    location_name: str
    location_type: str  # restaurant, shop, park, office, etc.
    duration_minutes: int
    activity: Optional[str]
    expense_amount: Optional[float]

class TravelProfile(BaseModel):
    total_trips: int
    travel_frequency: str  # frequent, moderate, occasional, rare
    preferred_destinations: List[str]
    travel_style: str  # luxury, budget, mid-range, backpacker
    international_travel: bool
    passport_countries: List[str]
    loyalty_programs: List[Dict[str, Any]]
    travel_insurance: bool
    recent_travels: List[TravelEntry]
    location_history: List[LocationVisit]
    home_coordinates: Dict[str, float]

class TravelGenerator:
    def __init__(self):
        self.cities = {
            "US": {
                "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "Oakland"],
                "NY": ["New York City", "Buffalo", "Rochester", "Syracuse", "Albany"],
                "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
                "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"],
                "IL": ["Chicago", "Springfield", "Rockford", "Peoria", "Naperville"],
                "WA": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue"],
                "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood"],
                "NV": ["Las Vegas", "Reno", "Henderson", "Carson City", "Sparks"]
            },
            "International": {
                "UK": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool"],
                "France": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
                "Germany": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"],
                "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya"],
                "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
                "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
                "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
                "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"]
            }
        }
        
        self.travel_styles = {
            "luxury": {"budget_multiplier": 3.0, "accommodation_types": ["hotel", "resort"]},
            "mid-range": {"budget_multiplier": 1.5, "accommodation_types": ["hotel", "airbnb", "vacation_rental"]},
            "budget": {"budget_multiplier": 0.7, "accommodation_types": ["hostel", "airbnb", "family_home"]},
            "backpacker": {"budget_multiplier": 0.4, "accommodation_types": ["hostel", "camping", "family_home"]}
        }
        
        self.loyalty_programs = [
            {"airline": "United Airlines", "program": "MileagePlus", "tier": "Silver"},
            {"airline": "Delta", "program": "SkyMiles", "tier": "Gold"},
            {"airline": "American Airlines", "program": "AAdvantage", "tier": "Platinum"},
            {"hotel": "Marriott", "program": "Bonvoy", "tier": "Gold Elite"},
            {"hotel": "Hilton", "program": "Honors", "tier": "Diamond"},
            {"rental": "Hertz", "program": "Gold Plus Rewards", "tier": "President's Circle"}
        ]
        
        self.location_types = [
            "restaurant", "cafe", "shopping_mall", "park", "gym", "office",
            "hospital", "school", "library", "bank", "gas_station", "grocery_store",
            "pharmacy", "cinema", "museum", "church", "hotel", "airport"
        ]

    def generate_travel_profile(self, age: int, income: float, lifestyle: str) -> TravelProfile:
        """Generate comprehensive travel profile based on demographics"""
        
        # Determine travel frequency based on age and income
        travel_frequency = self._determine_travel_frequency(age, income)
        total_trips = self._calculate_total_trips(travel_frequency, age)
        
        # Determine travel style
        travel_style = self._determine_travel_style(income, lifestyle)
        
        # International travel likelihood
        international_travel = income > 50000 and random.random() < 0.6
        
        # Generate passport countries if international traveler
        passport_countries = []
        if international_travel:
            passport_countries = random.sample(
                list(self.cities["International"].keys()), 
                random.randint(1, min(6, max(1, int(income / 30000))))
            )
        
        # Generate loyalty programs
        loyalty_programs = self._generate_loyalty_programs(travel_frequency, travel_style)
        
        # Generate recent travels
        recent_travels = self._generate_recent_travels(
            total_trips, travel_style, international_travel, age
        )
        
        # Generate location history
        location_history = self._generate_location_history(lifestyle, age)
        
        # Generate home coordinates
        home_coordinates = {
            "latitude": round(random.uniform(25.0, 49.0), 6),
            "longitude": round(random.uniform(-125.0, -66.0), 6)
        }
        
        # Preferred destinations
        preferred_destinations = self._generate_preferred_destinations(
            international_travel, travel_style
        )
        
        return TravelProfile(
            total_trips=total_trips,
            travel_frequency=travel_frequency,
            preferred_destinations=preferred_destinations,
            travel_style=travel_style,
            international_travel=international_travel,
            passport_countries=passport_countries,
            loyalty_programs=loyalty_programs,
            travel_insurance=income > 40000 and random.random() < 0.7,
            recent_travels=recent_travels,
            location_history=location_history,
            home_coordinates=home_coordinates
        )

    def _determine_travel_frequency(self, age: int, income: float) -> str:
        """Determine how frequently person travels"""
        if income > 100000 and age < 65:
            return random.choice(["frequent", "frequent", "moderate"])
        elif income > 60000:
            return random.choice(["moderate", "moderate", "occasional"])
        elif age < 30:
            return random.choice(["moderate", "occasional", "occasional"])
        else:
            return random.choice(["occasional", "rare", "rare"])

    def _calculate_total_trips(self, frequency: str, age: int) -> int:
        """Calculate total lifetime trips"""
        base_trips = {
            "frequent": max(5, age - 15),
            "moderate": max(3, (age - 18) // 2),
            "occasional": max(1, (age - 18) // 4),
            "rare": max(0, (age - 18) // 8)
        }
        return base_trips.get(frequency, 1) + random.randint(0, 10)

    def _determine_travel_style(self, income: float, lifestyle: str) -> str:
        """Determine travel style based on income and lifestyle"""
        if income > 150000:
            return random.choice(["luxury", "luxury", "mid-range"])
        elif income > 75000:
            return random.choice(["mid-range", "mid-range", "budget"])
        elif income > 40000:
            return random.choice(["budget", "budget", "backpacker"])
        else:
            return random.choice(["budget", "backpacker"])

    def _generate_loyalty_programs(self, frequency: str, style: str) -> List[Dict[str, Any]]:
        """Generate loyalty program memberships"""
        if frequency in ["rare", "occasional"]:
            return []
        
        program_count = {"frequent": 3, "moderate": 2}.get(frequency, 1)
        return random.sample(self.loyalty_programs, min(program_count, len(self.loyalty_programs)))

    def _generate_recent_travels(self, total_trips: int, style: str, international: bool, age: int) -> List[TravelEntry]:
        """Generate recent travel history"""
        if total_trips == 0:
            return []
        
        recent_count = min(5, max(1, total_trips // 3))
        travels = []
        
        for i in range(recent_count):
            # Generate travel dates (within last 2 years)
            departure_date = datetime.now() - timedelta(days=random.randint(30, 730))
            duration_days = random.randint(2, 14)
            return_date = departure_date + timedelta(days=duration_days)
            
            # Choose destination
            is_international_trip = international and random.random() < 0.3
            
            if is_international_trip:
                country = random.choice(list(self.cities["International"].keys()))
                dest_state = ""
                dest_country = country
                dest_city = random.choice(self.cities["International"][country])
            else:
                dest_state = random.choice(list(self.cities["US"].keys()))
                dest_country = "US"
                dest_city = random.choice(self.cities["US"][dest_state])
            
            # Origin (assume home base)
            origin_state = random.choice(list(self.cities["US"].keys()))
            origin_city = random.choice(self.cities["US"][origin_state])
            origin_country = "US"
            
            # Travel details
            purpose = random.choice(list(TravelPurpose))
            transportation = self._select_transportation(is_international_trip, duration_days)
            accommodation = self._select_accommodation(style)
            
            # Cost calculation
            base_cost = self._calculate_travel_cost(
                duration_days, is_international_trip, style, transportation
            )
            
            travel_entry = TravelEntry(
                entry_id=str(uuid.uuid4()),
                departure_date=departure_date,
                return_date=return_date,
                origin_city=origin_city,
                origin_state=origin_state,
                origin_country=origin_country,
                destination_city=dest_city,
                destination_state=dest_state,
                destination_country=dest_country,
                purpose=purpose,
                transportation_mode=transportation,
                accommodation_type=accommodation,
                accommodation_name=self._generate_accommodation_name(accommodation),
                booking_reference=self._generate_booking_reference(),
                total_cost=base_cost,
                travel_companions=self._generate_companions(),
                notes=None
            )
            
            travels.append(travel_entry)
        
        return sorted(travels, key=lambda x: x.departure_date, reverse=True)

    def _generate_location_history(self, lifestyle: str, age: int) -> List[LocationVisit]:
        """Generate recent location visit history"""
        # Generate 20-50 location visits in last month
        visit_count = random.randint(20, 50)
        visits = []
        
        for i in range(visit_count):
            # Random date in last 30 days
            visit_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Random coordinates (within reasonable area)
            latitude = round(random.uniform(25.0, 49.0), 6)
            longitude = round(random.uniform(-125.0, -66.0), 6)
            
            location_type = random.choice(self.location_types)
            location_name = self._generate_location_name(location_type)
            
            # Duration based on location type
            duration = self._get_typical_duration(location_type)
            
            # Expense amount (optional)
            expense = self._calculate_location_expense(location_type) if random.random() < 0.6 else None
            
            visit = LocationVisit(
                visit_id=str(uuid.uuid4()),
                timestamp=visit_date,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                location_type=location_type,
                duration_minutes=duration,
                activity=self._generate_activity(location_type),
                expense_amount=expense
            )
            
            visits.append(visit)
        
        return sorted(visits, key=lambda x: x.timestamp, reverse=True)

    def _select_transportation(self, international: bool, duration: int) -> TransportationMode:
        """Select appropriate transportation mode"""
        if international:
            return TransportationMode.FLIGHT
        elif duration > 7:
            return random.choice([TransportationMode.FLIGHT, TransportationMode.CAR])
        else:
            return random.choice([
                TransportationMode.CAR, TransportationMode.FLIGHT,
                TransportationMode.TRAIN, TransportationMode.BUS
            ])

    def _select_accommodation(self, style: str) -> Optional[AccommodationType]:
        """Select accommodation based on travel style"""
        style_accommodations = self.travel_styles[style]["accommodation_types"]
        return AccommodationType(random.choice(style_accommodations))

    def _calculate_travel_cost(self, duration: int, international: bool, style: str, transport: TransportationMode) -> float:
        """Calculate realistic travel cost"""
        base_cost = 200  # Base daily cost
        
        if international:
            base_cost *= 2.5
        
        if transport == TransportationMode.FLIGHT:
            base_cost += 400 if international else 200
        elif transport == TransportationMode.CAR:
            base_cost += 50
        
        style_multiplier = self.travel_styles[style]["budget_multiplier"]
        total_cost = base_cost * duration * style_multiplier
        
        return round(total_cost * random.uniform(0.8, 1.3), 2)

    def _generate_accommodation_name(self, acc_type: Optional[AccommodationType]) -> Optional[str]:
        """Generate realistic accommodation names"""
        if not acc_type:
            return None
        
        hotel_names = ["Marriott", "Hilton", "Hyatt", "Holiday Inn", "Best Western"]
        airbnb_names = ["Downtown Loft", "Cozy Apartment", "Modern Studio", "Family Home"]
        
        if acc_type == AccommodationType.HOTEL:
            return f"{random.choice(hotel_names)} {random.choice(['Downtown', 'Airport', 'Convention Center'])}"
        elif acc_type == AccommodationType.AIRBNB:
            return random.choice(airbnb_names)
        else:
            return f"Local {acc_type.value.replace('_', ' ').title()}"

    def _generate_booking_reference(self) -> str:
        """Generate realistic booking reference"""
        return f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{random.randint(1000, 9999)}"

    def _generate_companions(self) -> List[str]:
        """Generate travel companions"""
        if random.random() < 0.4:  # 40% chance of traveling alone
            return []
        
        companion_count = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
        companions = []
        
        for i in range(companion_count):
            relationship = random.choice([
                "spouse", "partner", "friend", "colleague", "family_member", "child"
            ])
            companions.append(relationship)
        
        return companions

    def _generate_preferred_destinations(self, international: bool, style: str) -> List[str]:
        """Generate preferred travel destinations"""
        destinations = []
        
        # Add US destinations
        us_cities = []
        for state_cities in self.cities["US"].values():
            us_cities.extend(state_cities)
        destinations.extend(random.sample(us_cities, min(3, len(us_cities))))
        
        # Add international if applicable
        if international:
            intl_cities = []
            for country_cities in self.cities["International"].values():
                intl_cities.extend(country_cities)
            destinations.extend(random.sample(intl_cities, min(2, len(intl_cities))))
        
        return destinations[:5]

    def _generate_location_name(self, location_type: str) -> str:
        """Generate realistic location names"""
        location_names = {
            "restaurant": ["The Garden Bistro", "Mama's Kitchen", "Downtown Grill", "Sunset Cafe"],
            "cafe": ["Starbucks", "Local Coffee Co.", "Bean There", "Morning Brew"],
            "shopping_mall": ["Westfield Mall", "Town Center", "Plaza Shopping", "Outlet Mall"],
            "park": ["Central Park", "Riverside Park", "Oak Grove", "Memorial Park"],
            "gym": ["Planet Fitness", "24 Hour Fitness", "Local Gym", "CrossFit Box"],
            "office": ["Corporate Plaza", "Business Center", "Main Office", "Regional HQ"],
            "hospital": ["General Hospital", "Medical Center", "Regional Health", "City Hospital"],
            "school": ["Elementary School", "High School", "Community College", "University"],
            "library": ["Public Library", "Central Library", "Branch Library", "University Library"],
            "bank": ["Chase Bank", "Bank of America", "Wells Fargo", "Local Credit Union"],
            "gas_station": ["Shell", "Chevron", "BP", "Exxon"],
            "grocery_store": ["Whole Foods", "Safeway", "Kroger", "Local Market"],
            "pharmacy": ["CVS", "Walgreens", "Rite Aid", "Local Pharmacy"],
            "cinema": ["AMC Theater", "Regal Cinema", "Local Theater", "Drive-In"],
            "museum": ["Art Museum", "History Museum", "Science Center", "Cultural Center"],
            "church": ["First Baptist", "St. Mary's", "Community Church", "Temple"],
            "hotel": ["Downtown Hotel", "Airport Inn", "Business Lodge", "Resort"],
            "airport": ["International Airport", "Regional Airport", "Municipal Airport"]
        }
        
        names = location_names.get(location_type, ["Generic Location"])
        return random.choice(names)

    def _get_typical_duration(self, location_type: str) -> int:
        """Get typical visit duration in minutes"""
        durations = {
            "restaurant": random.randint(45, 120),
            "cafe": random.randint(15, 60),
            "shopping_mall": random.randint(60, 180),
            "park": random.randint(30, 120),
            "gym": random.randint(45, 90),
            "office": random.randint(240, 480),  # 4-8 hours
            "hospital": random.randint(30, 180),
            "school": random.randint(60, 360),
            "library": random.randint(30, 120),
            "bank": random.randint(10, 30),
            "gas_station": random.randint(5, 15),
            "grocery_store": random.randint(20, 60),
            "pharmacy": random.randint(10, 30),
            "cinema": random.randint(120, 180),
            "museum": random.randint(60, 180),
            "church": random.randint(60, 120),
            "hotel": random.randint(480, 720),  # 8-12 hours
            "airport": random.randint(60, 240)
        }
        
        return durations.get(location_type, random.randint(15, 60))

    def _calculate_location_expense(self, location_type: str) -> float:
        """Calculate typical expense for location type"""
        expense_ranges = {
            "restaurant": (15, 80),
            "cafe": (4, 15),
            "shopping_mall": (20, 200),
            "park": (0, 10),
            "gym": (0, 0),  # Membership
            "gas_station": (25, 60),
            "grocery_store": (30, 150),
            "pharmacy": (10, 50),
            "cinema": (12, 25),
            "museum": (8, 20),
            "hotel": (80, 300)
        }
        
        if location_type in expense_ranges:
            min_cost, max_cost = expense_ranges[location_type]
            return round(random.uniform(min_cost, max_cost), 2)
        
        return round(random.uniform(5, 50), 2)

    def _generate_activity(self, location_type: str) -> Optional[str]:
        """Generate activity description for location"""
        activities = {
            "restaurant": "dining",
            "cafe": "coffee meeting",
            "shopping_mall": "shopping",
            "park": "walking",
            "gym": "workout",
            "office": "work",
            "hospital": "appointment",
            "school": "class",
            "library": "studying",
            "bank": "banking",
            "gas_station": "refueling",
            "grocery_store": "shopping",
            "pharmacy": "pickup",
            "cinema": "movie",
            "museum": "visit",
            "church": "service",
            "hotel": "staying",
            "airport": "travel"
        }
        
        return activities.get(location_type)