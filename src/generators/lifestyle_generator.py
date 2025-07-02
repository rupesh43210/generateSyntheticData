import random
from datetime import date, timedelta, datetime, time
from typing import List, Dict, Optional, Tuple
from enum import Enum

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field


class LifestyleCategory(str, Enum):
    MINIMALIST = "Minimalist"
    LUXURY = "Luxury"
    OUTDOORSY = "Outdoorsy"
    URBAN = "Urban"
    SUBURBAN = "Suburban"
    RURAL = "Rural"
    BOHEMIAN = "Bohemian"
    TRADITIONAL = "Traditional"
    MODERN = "Modern"
    TECH_SAVVY = "Tech Savvy"


class PersonalityTraits(BaseModel):
    big_five_personality: Dict[str, int]  # Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism (1-10)
    myers_briggs_type: str
    dominant_traits: List[str]
    communication_style: str
    conflict_resolution: str
    decision_making_style: str
    stress_response: str


class Preferences(BaseModel):
    food_preferences: Dict[str, List[str]]
    music_genres: List[str]
    movie_genres: List[str]
    book_genres: List[str]
    travel_style: str
    vacation_preferences: List[str]
    shopping_habits: Dict[str, str]
    entertainment_preferences: List[str]
    social_preferences: List[str]
    weather_preferences: str
    pet_preferences: List[str]


class DailyRoutine(BaseModel):
    wake_up_time: time
    bedtime: time
    morning_routine: List[str]
    evening_routine: List[str]
    work_schedule: str
    lunch_preference: str
    exercise_time: Optional[str] = None
    relaxation_activities: List[str]
    weekend_activities: List[str]
    productivity_peak: str  # Morning, Afternoon, Evening, Night


class Hobbies(BaseModel):
    primary_hobbies: List[str]
    secondary_hobbies: List[str]
    creative_pursuits: List[str]
    sports_activities: List[str]
    collecting_interests: List[str]
    skill_level: Dict[str, str]  # Hobby -> Skill Level
    time_investment: Dict[str, str]  # Hobby -> Time per week
    equipment_owned: Dict[str, List[str]]  # Hobby -> Equipment list


class Values(BaseModel):
    core_values: List[str]
    political_leaning: str
    religious_beliefs: str
    environmental_consciousness: str
    social_causes: List[str]
    charitable_giving: str
    volunteer_activities: List[str]
    family_importance: str
    career_priorities: List[str]


class ConsumerBehavior(BaseModel):
    shopping_frequency: Dict[str, str]  # Category -> Frequency
    brand_loyalty: str
    price_sensitivity: str
    research_behavior: str
    impulse_buying_tendency: str
    preferred_shopping_channels: List[str]
    payment_methods: List[str]
    subscription_services: List[str]
    luxury_spending_categories: List[str]


class TechnologyUsage(BaseModel):
    device_preferences: Dict[str, str]
    social_media_usage: Dict[str, str]  # Platform -> Usage Level
    app_categories: List[str]
    gaming_preferences: List[str]
    streaming_services: List[str]
    smart_home_adoption: str
    privacy_concerns: str
    tech_adoption_speed: str


class LifestyleProfile(BaseModel):
    lifestyle_category: LifestyleCategory
    personality_traits: PersonalityTraits
    preferences: Preferences
    daily_routine: DailyRoutine
    hobbies: Hobbies
    values: Values
    consumer_behavior: ConsumerBehavior
    technology_usage: TechnologyUsage
    life_satisfaction: int  # 1-10 scale
    stress_level: int  # 1-10 scale
    work_life_balance: str
    future_goals: List[str]


class LifestyleGenerator:
    """Generator for comprehensive lifestyle and personality data"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Lifestyle categories by demographics
        self.lifestyle_by_age_income = {
            "young_low": [  # 18-30, <50k
                (LifestyleCategory.URBAN, 0.4),
                (LifestyleCategory.MINIMALIST, 0.25),
                (LifestyleCategory.BOHEMIAN, 0.2),
                (LifestyleCategory.TECH_SAVVY, 0.15)
            ],
            "young_high": [  # 18-30, >75k
                (LifestyleCategory.URBAN, 0.35),
                (LifestyleCategory.LUXURY, 0.25),
                (LifestyleCategory.TECH_SAVVY, 0.25),
                (LifestyleCategory.MODERN, 0.15)
            ],
            "middle_low": [  # 31-50, <75k
                (LifestyleCategory.SUBURBAN, 0.4),
                (LifestyleCategory.TRADITIONAL, 0.25),
                (LifestyleCategory.MINIMALIST, 0.2),
                (LifestyleCategory.OUTDOORSY, 0.15)
            ],
            "middle_high": [  # 31-50, >75k
                (LifestyleCategory.SUBURBAN, 0.3),
                (LifestyleCategory.LUXURY, 0.3),
                (LifestyleCategory.MODERN, 0.25),
                (LifestyleCategory.OUTDOORSY, 0.15)
            ],
            "older_low": [  # 51+, <75k
                (LifestyleCategory.TRADITIONAL, 0.4),
                (LifestyleCategory.SUBURBAN, 0.3),
                (LifestyleCategory.RURAL, 0.2),
                (LifestyleCategory.MINIMALIST, 0.1)
            ],
            "older_high": [  # 51+, >75k
                (LifestyleCategory.LUXURY, 0.4),
                (LifestyleCategory.TRADITIONAL, 0.3),
                (LifestyleCategory.SUBURBAN, 0.2),
                (LifestyleCategory.MODERN, 0.1)
            ]
        }
        
        # Myers-Briggs types with frequencies
        self.mbti_types = [
            ("ISFJ", 0.138), ("ESFJ", 0.123), ("ISTJ", 0.118), ("ISFP", 0.088),
            ("ESTJ", 0.087), ("ESFP", 0.082), ("ENFP", 0.081), ("ISTP", 0.054),
            ("INFP", 0.044), ("ESTP", 0.043), ("INTP", 0.033), ("ENTP", 0.032),
            ("ENFJ", 0.025), ("INFJ", 0.015), ("INTJ", 0.021), ("ENTJ", 0.018)
        ]
        
        # Food preferences by lifestyle
        self.food_preferences = {
            LifestyleCategory.LUXURY: {
                "cuisines": ["French", "Italian", "Japanese", "Mediterranean", "Fine Dining"],
                "dietary_style": ["Gourmet", "Wine Connoisseur", "Organic", "Farm-to-Table"],
                "dining_out": "Frequently"
            },
            LifestyleCategory.MINIMALIST: {
                "cuisines": ["Simple", "Asian", "Mediterranean", "Vegetarian"],
                "dietary_style": ["Clean Eating", "Plant-Based", "Whole Foods"],
                "dining_out": "Occasionally"
            },
            LifestyleCategory.OUTDOORSY: {
                "cuisines": ["American", "Mexican", "BBQ", "Comfort Food"],
                "dietary_style": ["High Protein", "Energy Foods", "Camping Food"],
                "dining_out": "Rarely"
            },
            LifestyleCategory.TECH_SAVVY: {
                "cuisines": ["International", "Fusion", "Fast-Casual", "Delivery"],
                "dietary_style": ["Convenient", "Meal Kits", "Food Apps"],
                "dining_out": "Frequently"
            },
            LifestyleCategory.TRADITIONAL: {
                "cuisines": ["American", "Italian", "Mexican", "Chinese", "Comfort Food"],
                "dietary_style": ["Balanced", "Home Cooked", "Family Recipes"],
                "dining_out": "Occasionally"
            }
        }
        
        # Hobbies by lifestyle and age
        self.hobbies_by_lifestyle = {
            LifestyleCategory.OUTDOORSY: {
                "primary": ["Hiking", "Camping", "Fishing", "Hunting", "Rock Climbing", "Kayaking"],
                "secondary": ["Photography", "Bird Watching", "Gardening", "Survival Skills"],
                "sports": ["Mountain Biking", "Trail Running", "Skiing", "Surfing"]
            },
            LifestyleCategory.URBAN: {
                "primary": ["Art Galleries", "Concerts", "Theater", "Food Tours", "Networking"],
                "secondary": ["Street Photography", "Urban Exploration", "Coffee Culture"],
                "sports": ["Cycling", "Running", "Gym", "Rock Climbing"]
            },
            LifestyleCategory.TECH_SAVVY: {
                "primary": ["Gaming", "Programming", "3D Printing", "Robotics", "VR"],
                "secondary": ["Electronics", "App Development", "Crypto", "AI/ML"],
                "sports": ["Esports", "Drone Racing", "Virtual Sports"]
            },
            LifestyleCategory.LUXURY: {
                "primary": ["Wine Collecting", "Art Collecting", "Luxury Travel", "Fine Dining"],
                "secondary": ["Fashion", "Jewelry", "Classic Cars", "Yacht Club"],
                "sports": ["Golf", "Tennis", "Sailing", "Polo"]
            },
            LifestyleCategory.TRADITIONAL: {
                "primary": ["Cooking", "Gardening", "Reading", "Family Activities"],
                "secondary": ["Crafts", "Church Activities", "Community Service"],
                "sports": ["Bowling", "Golf", "Walking", "Swimming"]
            }
        }
        
        # Values by lifestyle
        self.values_by_lifestyle = {
            LifestyleCategory.TRADITIONAL: {
                "core": ["Family", "Stability", "Tradition", "Responsibility", "Loyalty"],
                "political": "Conservative",
                "religious": "Religious",
                "causes": ["Family Values", "Community Support", "Education"]
            },
            LifestyleCategory.LUXURY: {
                "core": ["Success", "Quality", "Exclusivity", "Achievement", "Status"],
                "political": "Moderate",
                "religious": "Spiritual",
                "causes": ["Arts Funding", "Education", "Healthcare"]
            },
            LifestyleCategory.OUTDOORSY: {
                "core": ["Adventure", "Freedom", "Nature", "Authenticity", "Health"],
                "political": "Independent",
                "religious": "Nature-Spiritual",
                "causes": ["Environmental Protection", "Conservation", "Animal Rights"]
            },
            LifestyleCategory.TECH_SAVVY: {
                "core": ["Innovation", "Efficiency", "Progress", "Knowledge", "Connectivity"],
                "political": "Liberal",
                "religious": "Agnostic",
                "causes": ["Digital Rights", "Education", "Climate Change"]
            }
        }
        
        # Music genres by age and lifestyle
        self.music_by_age = {
            "18-25": ["Pop", "Hip-Hop", "Electronic", "Indie", "Alternative", "R&B"],
            "26-35": ["Pop", "Rock", "Hip-Hop", "Electronic", "Indie", "Alternative"],
            "36-45": ["Rock", "Pop", "Country", "Hip-Hop", "Alternative", "Classical"],
            "46-55": ["Rock", "Country", "Pop", "Blues", "Jazz", "Classical"],
            "56+": ["Classic Rock", "Country", "Jazz", "Blues", "Classical", "Folk"]
        }
        
        # Technology preferences by age
        self.tech_by_age = {
            "18-30": {
                "devices": {"smartphone": "iPhone", "computer": "MacBook", "tablet": "iPad"},
                "adoption": "Early Adopter",
                "privacy": "Low Concern",
                "smart_home": "High Adoption"
            },
            "31-45": {
                "devices": {"smartphone": "Mixed", "computer": "PC/Mac", "tablet": "Optional"},
                "adoption": "Mainstream",
                "privacy": "Moderate Concern",
                "smart_home": "Moderate Adoption"
            },
            "46+": {
                "devices": {"smartphone": "Android", "computer": "PC", "tablet": "Rarely"},
                "adoption": "Late Adopter",
                "privacy": "High Concern",
                "smart_home": "Low Adoption"
            }
        }
        
        # Daily routines by lifestyle
        self.routines = {
            "Early Bird": {
                "wake_up": (5, 30, 7, 0),  # Between 5:30 and 7:00
                "bedtime": (21, 0, 22, 30),
                "peak": "Morning"
            },
            "Standard": {
                "wake_up": (6, 30, 8, 0),
                "bedtime": (22, 0, 23, 30),
                "peak": "Morning"
            },
            "Night Owl": {
                "wake_up": (8, 0, 10, 0),
                "bedtime": (23, 30, 1, 30),
                "peak": "Evening"
            }
        }
        
        # Consumer behavior patterns
        self.shopping_patterns = {
            "Researcher": {
                "research": "Extensive",
                "impulse": "Low",
                "brand_loyalty": "High",
                "price_sensitivity": "High"
            },
            "Impulse Buyer": {
                "research": "Minimal",
                "impulse": "High",
                "brand_loyalty": "Low",
                "price_sensitivity": "Low"
            },
            "Practical": {
                "research": "Moderate",
                "impulse": "Low",
                "brand_loyalty": "Moderate",
                "price_sensitivity": "High"
            },
            "Brand Loyal": {
                "research": "Moderate",
                "impulse": "Moderate",
                "brand_loyalty": "High",
                "price_sensitivity": "Low"
            }
        }
    
    def determine_lifestyle_category(self, age: int, income: float) -> LifestyleCategory:
        """Determine lifestyle category based on age and income"""
        if age < 31:
            category = "young_low" if income < 50000 else "young_high"
        elif age < 51:
            category = "middle_low" if income < 75000 else "middle_high"
        else:
            category = "older_low" if income < 75000 else "older_high"
        
        categories = self.lifestyle_by_age_income[category]
        lifestyles, weights = zip(*categories)
        return random.choices(lifestyles, weights=weights)[0]
    
    def generate_big_five_personality(self, lifestyle: LifestyleCategory) -> Dict[str, int]:
        """Generate Big Five personality traits"""
        # Base scores (1-10 scale)
        base_scores = {
            "Openness": 5,
            "Conscientiousness": 5,
            "Extraversion": 5,
            "Agreeableness": 5,
            "Neuroticism": 5
        }
        
        # Lifestyle adjustments
        adjustments = {
            LifestyleCategory.OUTDOORSY: {"Openness": 2, "Extraversion": 1, "Conscientiousness": 1},
            LifestyleCategory.TECH_SAVVY: {"Openness": 3, "Conscientiousness": 1, "Extraversion": -1},
            LifestyleCategory.LUXURY: {"Extraversion": 2, "Conscientiousness": 2, "Neuroticism": -1},
            LifestyleCategory.TRADITIONAL: {"Conscientiousness": 2, "Agreeableness": 2, "Openness": -2},
            LifestyleCategory.MINIMALIST: {"Conscientiousness": 2, "Neuroticism": -1, "Openness": 1},
            LifestyleCategory.URBAN: {"Openness": 2, "Extraversion": 2, "Neuroticism": 1}
        }
        
        if lifestyle in adjustments:
            for trait, adjustment in adjustments[lifestyle].items():
                base_scores[trait] += adjustment
        
        # Add randomness and constrain to 1-10
        for trait in base_scores:
            base_scores[trait] += random.randint(-2, 2)
            base_scores[trait] = max(1, min(10, base_scores[trait]))
        
        return base_scores
    
    def generate_mbti_type(self, big_five: Dict[str, int]) -> str:
        """Generate MBTI type based on Big Five traits"""
        # Simple mapping from Big Five to MBTI dimensions
        E_vs_I = "E" if big_five["Extraversion"] > 5 else "I"
        S_vs_N = "N" if big_five["Openness"] > 5 else "S"
        T_vs_F = "F" if big_five["Agreeableness"] > 5 else "T"
        J_vs_P = "J" if big_five["Conscientiousness"] > 5 else "P"
        
        return E_vs_I + S_vs_N + T_vs_F + J_vs_P
    
    def generate_preferences(self, lifestyle: LifestyleCategory, age: int) -> Preferences:
        """Generate lifestyle preferences"""
        # Food preferences
        food_data = self.food_preferences.get(lifestyle, self.food_preferences[LifestyleCategory.TRADITIONAL])
        food_prefs = {
            "favorite_cuisines": random.sample(food_data["cuisines"], random.randint(2, 4)),
            "dietary_restrictions": random.sample(food_data["dietary_style"], random.randint(1, 2)),
            "dining_frequency": [food_data["dining_out"]]
        }
        
        # Music preferences based on age
        age_group = self.get_age_group_for_music(age)
        music_genres = random.sample(self.music_by_age[age_group], random.randint(3, 5))
        
        # Movie preferences
        movie_genres = random.sample([
            "Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller",
            "Documentary", "Animation", "Mystery", "Adventure", "Fantasy"
        ], random.randint(3, 6))
        
        # Book preferences
        book_genres = random.sample([
            "Fiction", "Non-Fiction", "Mystery", "Romance", "Sci-Fi", "Biography",
            "History", "Self-Help", "Business", "Fantasy", "Thriller", "Poetry"
        ], random.randint(2, 4))
        
        # Travel style
        travel_styles = {
            LifestyleCategory.LUXURY: "Luxury Resort",
            LifestyleCategory.OUTDOORSY: "Adventure Travel",
            LifestyleCategory.MINIMALIST: "Backpacking",
            LifestyleCategory.URBAN: "City Exploration",
            LifestyleCategory.TRADITIONAL: "Family Vacation"
        }
        travel_style = travel_styles.get(lifestyle, "Mixed")
        
        # Vacation preferences
        vacation_prefs = random.sample([
            "Beach", "Mountains", "Cities", "Countryside", "Adventure", "Relaxation",
            "Cultural Sites", "Food Tours", "National Parks", "International Travel"
        ], random.randint(3, 5))
        
        # Shopping habits
        shopping_habits = {
            "preferred_method": random.choice(["Online", "In-Store", "Mixed"]),
            "frequency": random.choice(["Weekly", "Bi-weekly", "Monthly", "As Needed"]),
            "budget_consciousness": random.choice(["Budget-Conscious", "Moderate", "Price-Insensitive"])
        }
        
        # Entertainment preferences
        entertainment = random.sample([
            "Movies", "TV Shows", "Concerts", "Theater", "Sports Events", "Museums",
            "Gaming", "Reading", "Podcasts", "Music", "Live Comedy", "Festivals"
        ], random.randint(4, 7))
        
        # Social preferences
        social = random.sample([
            "Small Groups", "Large Parties", "One-on-One", "Family Gatherings",
            "Work Events", "Hobby Groups", "Online Communities", "Outdoor Groups"
        ], random.randint(2, 4))
        
        # Weather preferences
        weather = random.choice([
            "Warm/Sunny", "Cool/Crisp", "Mild/Temperate", "Varied Seasons",
            "Dry Climate", "Rainy/Cozy", "Snowy/Winter"
        ])
        
        # Pet preferences
        pet_prefs = []
        if random.random() < 0.6:  # 60% like pets
            pet_prefs = random.sample([
                "Dogs", "Cats", "Birds", "Fish", "Small Mammals", "Reptiles", "No Pets"
            ], random.randint(1, 2))
        else:
            pet_prefs = ["No Pets"]
        
        return Preferences(
            food_preferences=food_prefs,
            music_genres=music_genres,
            movie_genres=movie_genres,
            book_genres=book_genres,
            travel_style=travel_style,
            vacation_preferences=vacation_prefs,
            shopping_habits=shopping_habits,
            entertainment_preferences=entertainment,
            social_preferences=social,
            weather_preferences=weather,
            pet_preferences=pet_prefs
        )
    
    def get_age_group_for_music(self, age: int) -> str:
        """Get age group for music preferences"""
        if age < 26:
            return "18-25"
        elif age < 36:
            return "26-35"
        elif age < 46:
            return "36-45"
        elif age < 56:
            return "46-55"
        else:
            return "56+"
    
    def generate_daily_routine(self, lifestyle: LifestyleCategory, work_schedule: str) -> DailyRoutine:
        """Generate daily routine based on lifestyle"""
        # Determine routine type
        if lifestyle in [LifestyleCategory.TRADITIONAL, LifestyleCategory.OUTDOORSY]:
            routine_type = "Early Bird"
        elif lifestyle in [LifestyleCategory.TECH_SAVVY, LifestyleCategory.URBAN]:
            routine_type = random.choice(["Standard", "Night Owl"])
        else:
            routine_type = "Standard"
        
        routine_data = self.routines[routine_type]
        
        # Generate wake up and bedtime
        wake_start_h, wake_start_m, wake_end_h, wake_end_m = routine_data["wake_up"]
        wake_up_time = time(
            random.randint(wake_start_h, wake_end_h),
            random.choice([0, 15, 30, 45]) if wake_start_h == wake_end_h else 0
        )
        
        bed_start_h, bed_start_m, bed_end_h, bed_end_m = routine_data["bedtime"]
        # Handle midnight crossing
        if bed_end_h < bed_start_h:
            bed_hour = random.choice([bed_start_h, bed_start_h + 1, bed_end_h + 24])
            if bed_hour >= 24:
                bed_hour -= 24
        else:
            bed_hour = random.randint(bed_start_h, bed_end_h)
        
        bedtime = time(bed_hour, random.choice([0, 15, 30, 45]))
        
        # Morning routine
        morning_activities = [
            "Shower", "Coffee/Tea", "Breakfast", "Check Phone", "Exercise", "Meditation",
            "News Reading", "Planning Day", "Email Check", "Grooming"
        ]
        morning_routine = random.sample(morning_activities, random.randint(3, 6))
        
        # Evening routine
        evening_activities = [
            "Dinner", "TV/Streaming", "Reading", "Family Time", "Exercise", "Relaxation",
            "Planning Tomorrow", "Social Media", "Hobbies", "Bedtime Prep"
        ]
        evening_routine = random.sample(evening_activities, random.randint(3, 5))
        
        # Lunch preference
        lunch_prefs = ["Home-cooked", "Restaurant", "Meal Prep", "Delivery", "Cafeteria", "Skipped"]
        lunch_pref = random.choice(lunch_prefs)
        
        # Exercise time
        exercise_time = None
        if random.random() < 0.6:  # 60% exercise regularly
            exercise_time = random.choice(["Morning", "Lunch Break", "Evening", "Weekend"])
        
        # Relaxation activities
        relaxation = random.sample([
            "Reading", "TV", "Music", "Meditation", "Bath", "Walking", "Gaming",
            "Crafts", "Cooking", "Gardening", "Socializing"
        ], random.randint(2, 4))
        
        # Weekend activities
        weekend = random.sample([
            "Sleeping In", "Exercise", "Hobbies", "Socializing", "Errands", "Family Time",
            "Outdoor Activities", "Entertainment", "Relaxation", "Projects", "Travel"
        ], random.randint(4, 7))
        
        return DailyRoutine(
            wake_up_time=wake_up_time,
            bedtime=bedtime,
            morning_routine=morning_routine,
            evening_routine=evening_routine,
            work_schedule=work_schedule,
            lunch_preference=lunch_pref,
            exercise_time=exercise_time,
            relaxation_activities=relaxation,
            weekend_activities=weekend,
            productivity_peak=routine_data["peak"]
        )
    
    def generate_hobbies(self, lifestyle: LifestyleCategory, age: int, income: float) -> Hobbies:
        """Generate hobbies based on lifestyle and demographics"""
        hobby_data = self.hobbies_by_lifestyle.get(lifestyle, {
            "primary": ["Reading", "TV", "Cooking", "Gardening"],
            "secondary": ["Walking", "Music", "Movies", "Shopping"],
            "sports": ["Walking", "Swimming", "Cycling"]
        })
        
        # Select hobbies
        primary = random.sample(hobby_data.get("primary", []), random.randint(2, 4))
        secondary = random.sample(hobby_data.get("secondary", []), random.randint(1, 3))
        sports = random.sample(hobby_data.get("sports", []), random.randint(0, 2))
        
        # Creative pursuits based on age and lifestyle
        creative_options = [
            "Photography", "Painting", "Writing", "Music", "Crafts", "Design",
            "Cooking", "Baking", "Woodworking", "Knitting", "Pottery"
        ]
        creative = random.sample(creative_options, random.randint(0, 3))
        
        # Collecting based on income and age
        collecting = []
        if income > 50000 and random.random() < 0.3:
            collecting_options = [
                "Books", "Art", "Coins", "Stamps", "Wine", "Antiques", "Comics",
                "Music", "Movies", "Sports Memorabilia", "Vintage Items"
            ]
            collecting = random.sample(collecting_options, random.randint(1, 2))
        
        # Generate skill levels
        all_hobbies = primary + secondary + creative
        skill_levels = {}
        time_investment = {}
        equipment = {}
        
        for hobby in all_hobbies:
            # Skill level
            skill_levels[hobby] = random.choice(["Beginner", "Intermediate", "Advanced", "Expert"])
            
            # Time investment
            time_investment[hobby] = random.choice([
                "1-2 hours/week", "3-5 hours/week", "6-10 hours/week", "10+ hours/week"
            ])
            
            # Equipment (simplified)
            equipment[hobby] = [f"Basic {hobby} equipment", f"Intermediate {hobby} gear"]
        
        return Hobbies(
            primary_hobbies=primary,
            secondary_hobbies=secondary,
            creative_pursuits=creative,
            sports_activities=sports,
            collecting_interests=collecting,
            skill_level=skill_levels,
            time_investment=time_investment,
            equipment_owned=equipment
        )
    
    def generate_values(self, lifestyle: LifestyleCategory, age: int) -> Values:
        """Generate values and beliefs"""
        values_data = self.values_by_lifestyle.get(lifestyle, {
            "core": ["Family", "Health", "Happiness", "Security", "Friendship"],
            "political": "Moderate",
            "religious": "Spiritual",
            "causes": ["Education", "Health", "Community"]
        })
        
        core_values = values_data["core"].copy()
        # Add some random values
        additional_values = [
            "Adventure", "Creativity", "Independence", "Learning", "Service",
            "Achievement", "Balance", "Integrity", "Peace", "Growth"
        ]
        core_values.extend(random.sample(additional_values, random.randint(1, 3)))
        
        # Political leaning with age adjustment
        political = values_data["political"]
        if age > 50:
            political = random.choice(["Conservative", "Moderate"])
        elif age < 30:
            political = random.choice(["Liberal", "Progressive", "Independent"])
        
        # Religious beliefs
        religious_options = [
            "Christian", "Jewish", "Muslim", "Hindu", "Buddhist", "Spiritual",
            "Agnostic", "Atheist", "Non-Religious", "Other"
        ]
        religious = random.choice(religious_options)
        
        # Environmental consciousness
        env_consciousness = random.choice([
            "Very High", "High", "Moderate", "Low", "Very Low"
        ])
        
        # Social causes
        cause_options = [
            "Education", "Healthcare", "Environment", "Poverty", "Human Rights",
            "Animal Rights", "Arts", "Veterans", "Children", "Elderly Care",
            "Mental Health", "Climate Change", "Social Justice"
        ]
        social_causes = random.sample(cause_options, random.randint(2, 5))
        
        # Charitable giving
        giving_levels = ["None", "Occasional", "Regular", "Generous", "Major Donor"]
        charitable_giving = random.choice(giving_levels)
        
        # Volunteer activities
        volunteer = []
        if random.random() < 0.4:  # 40% volunteer
            volunteer_options = [
                "Religious Organization", "School/Education", "Healthcare", "Environment",
                "Community Center", "Sports/Youth", "Animal Shelter", "Food Bank"
            ]
            volunteer = random.sample(volunteer_options, random.randint(1, 2))
        
        # Family importance
        family_importance = random.choice([
            "Extremely Important", "Very Important", "Important", "Moderately Important", "Less Important"
        ])
        
        # Career priorities
        career_priorities = random.sample([
            "Work-Life Balance", "Financial Security", "Career Growth", "Job Satisfaction",
            "Making a Difference", "Creativity", "Stability", "Recognition", "Flexibility"
        ], random.randint(3, 5))
        
        return Values(
            core_values=core_values,
            political_leaning=political,
            religious_beliefs=religious,
            environmental_consciousness=env_consciousness,
            social_causes=social_causes,
            charitable_giving=charitable_giving,
            volunteer_activities=volunteer,
            family_importance=family_importance,
            career_priorities=career_priorities
        )
    
    def generate_consumer_behavior(self, lifestyle: LifestyleCategory, income: float, age: int) -> ConsumerBehavior:
        """Generate consumer behavior patterns"""
        # Choose shopping pattern
        pattern_name = random.choice(list(self.shopping_patterns.keys()))
        pattern = self.shopping_patterns[pattern_name]
        
        # Shopping frequency by category
        shopping_freq = {
            "Groceries": random.choice(["Weekly", "Bi-weekly", "Daily"]),
            "Clothing": random.choice(["Monthly", "Seasonally", "As Needed", "Rarely"]),
            "Electronics": random.choice(["Rarely", "As Needed", "Annually"]),
            "Home Items": random.choice(["Monthly", "As Needed", "Seasonally"]),
            "Entertainment": random.choice(["Weekly", "Monthly", "As Needed"])
        }
        
        # Preferred shopping channels
        if age < 35:
            channels = random.sample(["Online", "Mobile App", "Social Media", "In-Store"], random.randint(2, 3))
        elif age < 55:
            channels = random.sample(["Online", "In-Store", "Catalog", "Mobile App"], random.randint(2, 3))
        else:
            channels = random.sample(["In-Store", "Catalog", "Phone", "Online"], random.randint(1, 2))
        
        # Payment methods
        if age < 35:
            payments = random.sample(["Credit Card", "Debit Card", "Mobile Pay", "Buy Now Pay Later"], random.randint(2, 3))
        elif age < 55:
            payments = random.sample(["Credit Card", "Debit Card", "Cash", "Mobile Pay"], random.randint(2, 3))
        else:
            payments = random.sample(["Credit Card", "Debit Card", "Cash", "Check"], random.randint(2, 3))
        
        # Subscription services
        subscription_options = [
            "Netflix", "Spotify", "Amazon Prime", "Gym Membership", "Meal Kit",
            "Software", "News", "Gaming", "Beauty Box", "Wine Club"
        ]
        num_subscriptions = 3 if income > 75000 else 2 if income > 50000 else 1
        subscriptions = random.sample(subscription_options, random.randint(1, num_subscriptions))
        
        # Luxury spending
        luxury_categories = []
        if income > 100000:
            luxury_options = [
                "Fashion", "Jewelry", "Travel", "Dining", "Electronics", "Home Decor",
                "Cars", "Art", "Wine", "Experiences"
            ]
            luxury_categories = random.sample(luxury_options, random.randint(2, 4))
        
        return ConsumerBehavior(
            shopping_frequency=shopping_freq,
            brand_loyalty=pattern["brand_loyalty"],
            price_sensitivity=pattern["price_sensitivity"],
            research_behavior=pattern["research"],
            impulse_buying_tendency=pattern["impulse"],
            preferred_shopping_channels=channels,
            payment_methods=payments,
            subscription_services=subscriptions,
            luxury_spending_categories=luxury_categories
        )
    
    def generate_technology_usage(self, age: int, lifestyle: LifestyleCategory) -> TechnologyUsage:
        """Generate technology usage patterns"""
        # Get age-based preferences
        age_group = "18-30" if age < 31 else "31-45" if age < 46 else "46+"
        tech_data = self.tech_by_age[age_group]
        
        # Device preferences
        device_prefs = tech_data["devices"].copy()
        
        # Social media usage
        social_usage = {}
        if age < 30:
            platforms = ["Instagram", "TikTok", "Snapchat", "Twitter", "Facebook"]
            usage_levels = ["Heavy", "Moderate", "Light", "None"]
        elif age < 50:
            platforms = ["Facebook", "Instagram", "LinkedIn", "Twitter", "YouTube"]
            usage_levels = ["Moderate", "Light", "Heavy", "None"]
        else:
            platforms = ["Facebook", "LinkedIn", "YouTube", "Email", "News Apps"]
            usage_levels = ["Light", "Moderate", "None", "Heavy"]
        
        for platform in platforms:
            social_usage[platform] = random.choice(usage_levels)
        
        # App categories
        app_categories = random.sample([
            "Social Media", "News", "Entertainment", "Productivity", "Health",
            "Finance", "Shopping", "Travel", "Food", "Gaming", "Education", "Weather"
        ], random.randint(5, 10))
        
        # Gaming preferences
        gaming_prefs = []
        if age < 40 and random.random() < 0.6:
            gaming_prefs = random.sample([
                "Mobile Games", "Console Games", "PC Games", "VR Games", "Social Games"
            ], random.randint(1, 3))
        
        # Streaming services
        streaming = random.sample([
            "Netflix", "YouTube", "Hulu", "Disney+", "Amazon Prime", "Apple TV+",
            "Spotify", "Apple Music", "Podcasts", "Twitch"
        ], random.randint(3, 6))
        
        return TechnologyUsage(
            device_preferences=device_prefs,
            social_media_usage=social_usage,
            app_categories=app_categories,
            gaming_preferences=gaming_prefs,
            streaming_services=streaming,
            smart_home_adoption=tech_data["smart_home"],
            privacy_concerns=tech_data["privacy"],
            tech_adoption_speed=tech_data["adoption"]
        )
    
    def generate_lifestyle_profile(self, age: int, income: float, profession: str,
                                 relationship_status: str = "Single") -> LifestyleProfile:
        """Generate comprehensive lifestyle profile"""
        # Determine lifestyle category
        lifestyle = self.determine_lifestyle_category(age, income)
        
        # Generate personality traits
        big_five = self.generate_big_five_personality(lifestyle)
        mbti_type = self.generate_mbti_type(big_five)
        
        # Dominant traits
        sorted_traits = sorted(big_five.items(), key=lambda x: x[1], reverse=True)
        dominant_traits = [trait for trait, score in sorted_traits[:3]]
        
        # Communication and behavior styles
        comm_style = random.choice(["Direct", "Diplomatic", "Casual", "Formal", "Assertive"])
        conflict_res = random.choice(["Avoid", "Confront", "Compromise", "Collaborate", "Accommodate"])
        decision_style = random.choice(["Analytical", "Intuitive", "Consensus", "Quick", "Deliberate"])
        stress_response = random.choice(["Exercise", "Socialize", "Isolate", "Problem-Solve", "Seek Support"])
        
        personality = PersonalityTraits(
            big_five_personality=big_five,
            myers_briggs_type=mbti_type,
            dominant_traits=dominant_traits,
            communication_style=comm_style,
            conflict_resolution=conflict_res,
            decision_making_style=decision_style,
            stress_response=stress_response
        )
        
        # Generate other components
        preferences = self.generate_preferences(lifestyle, age)
        work_schedule = random.choice(["9-5 Weekdays", "Flexible", "Shift Work", "Remote", "Part-time"])
        daily_routine = self.generate_daily_routine(lifestyle, work_schedule)
        hobbies = self.generate_hobbies(lifestyle, age, income)
        values = self.generate_values(lifestyle, age)
        consumer_behavior = self.generate_consumer_behavior(lifestyle, income, age)
        technology_usage = self.generate_technology_usage(age, lifestyle)
        
        # Life satisfaction and stress (influenced by various factors)
        base_satisfaction = 6  # Baseline happiness
        if income > 100000:
            base_satisfaction += 1
        elif income < 30000:
            base_satisfaction -= 1
        
        if relationship_status in ["Married", "Partnership"]:
            base_satisfaction += 1
        
        if lifestyle in [LifestyleCategory.LUXURY, LifestyleCategory.OUTDOORSY]:
            base_satisfaction += 1
        
        life_satisfaction = max(1, min(10, base_satisfaction + random.randint(-2, 2)))
        
        # Stress level (inverse relationship with satisfaction)
        stress_level = max(1, min(10, 11 - life_satisfaction + random.randint(-2, 2)))
        
        # Work-life balance
        if work_schedule in ["Flexible", "Remote", "Part-time"]:
            balance = random.choice(["Excellent", "Good"])
        elif age > 50:
            balance = random.choice(["Good", "Fair"])
        else:
            balance = random.choice(["Fair", "Poor", "Good"])
        
        # Future goals
        goal_options = [
            "Career Advancement", "Financial Security", "Home Ownership", "Travel More",
            "Start Family", "Education", "Health Improvement", "Hobby Development",
            "Retirement Planning", "Personal Growth", "Community Involvement"
        ]
        future_goals = random.sample(goal_options, random.randint(3, 6))
        
        return LifestyleProfile(
            lifestyle_category=lifestyle,
            personality_traits=personality,
            preferences=preferences,
            daily_routine=daily_routine,
            hobbies=hobbies,
            values=values,
            consumer_behavior=consumer_behavior,
            technology_usage=technology_usage,
            life_satisfaction=life_satisfaction,
            stress_level=stress_level,
            work_life_balance=balance,
            future_goals=future_goals
        )