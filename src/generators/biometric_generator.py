import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import math

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field


class PhysicalCharacteristics(BaseModel):
    height_cm: float
    height_ft_in: str
    weight_kg: float
    weight_lbs: float
    bmi: float
    bmi_category: str
    body_type: str
    eye_color: str
    hair_color: str
    hair_type: str
    skin_tone: str
    ethnicity: str
    build: str
    shoe_size_us: float
    clothing_size: str
    distinguishing_marks: List[str] = Field(default_factory=list)


class BiometricData(BaseModel):
    fingerprint_pattern: str
    iris_pattern: str
    facial_structure: Dict[str, float]
    voice_characteristics: Dict[str, str]
    gait_pattern: Dict[str, float]
    hand_geometry: Dict[str, float]


class MedicalMeasurements(BaseModel):
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    resting_heart_rate: int
    body_fat_percentage: float
    muscle_mass_percentage: float
    bone_density: str
    vision_left_eye: str
    vision_right_eye: str
    hearing_left_ear: str
    hearing_right_ear: str
    dominant_hand: str
    flexibility_score: int  # 1-10 scale
    endurance_level: str


class FitnessProfile(BaseModel):
    activity_level: str
    preferred_exercises: List[str]
    max_heart_rate: int
    target_heart_rate_zone: Tuple[int, int]
    vo2_max: Optional[float] = None
    strength_level: str
    cardiovascular_fitness: str
    flexibility_rating: str
    fitness_goals: List[str]
    workout_frequency: str
    gym_membership: bool


class PhysicalProfile(BaseModel):
    physical_characteristics: PhysicalCharacteristics
    biometric_data: BiometricData
    medical_measurements: MedicalMeasurements
    fitness_profile: FitnessProfile
    physical_limitations: List[str] = Field(default_factory=list)
    allergies_environmental: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)


class BiometricGenerator:
    """Generator for comprehensive biometric and physical characteristics"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Height/weight distributions by gender and ethnicity
        self.height_weight_data = {
            "M": {
                "Caucasian": {"height_mean": 175.7, "height_std": 7.1, "weight_mean": 82.0, "weight_std": 15.0},
                "African American": {"height_mean": 175.5, "height_std": 7.3, "weight_mean": 85.0, "weight_std": 16.0},
                "Hispanic": {"height_mean": 170.2, "height_std": 6.8, "weight_mean": 78.0, "weight_std": 14.0},
                "Asian": {"height_mean": 168.0, "height_std": 6.5, "weight_mean": 70.0, "weight_std": 12.0},
                "Native American": {"height_mean": 173.0, "height_std": 7.0, "weight_mean": 80.0, "weight_std": 15.0},
                "Middle Eastern": {"height_mean": 172.0, "height_std": 6.9, "weight_mean": 77.0, "weight_std": 13.0}
            },
            "F": {
                "Caucasian": {"height_mean": 162.1, "height_std": 6.4, "weight_mean": 68.0, "weight_std": 13.0},
                "African American": {"height_mean": 162.0, "height_std": 6.6, "weight_mean": 72.0, "weight_std": 15.0},
                "Hispanic": {"height_mean": 157.8, "height_std": 6.2, "weight_mean": 65.0, "weight_std": 12.0},
                "Asian": {"height_mean": 156.0, "height_std": 5.8, "weight_mean": 57.0, "weight_std": 10.0},
                "Native American": {"height_mean": 160.0, "height_std": 6.3, "weight_mean": 67.0, "weight_std": 13.0},
                "Middle Eastern": {"height_mean": 159.0, "height_std": 6.1, "weight_mean": 63.0, "weight_std": 11.0}
            }
        }
        
        # Eye colors by ethnicity
        self.eye_colors = {
            "Caucasian": [
                ("Brown", 0.45), ("Blue", 0.27), ("Hazel", 0.18), ("Green", 0.09), ("Gray", 0.01)
            ],
            "African American": [
                ("Brown", 0.95), ("Hazel", 0.04), ("Green", 0.01)
            ],
            "Hispanic": [
                ("Brown", 0.85), ("Hazel", 0.12), ("Green", 0.02), ("Blue", 0.01)
            ],
            "Asian": [
                ("Brown", 0.98), ("Hazel", 0.02)
            ],
            "Native American": [
                ("Brown", 0.90), ("Hazel", 0.08), ("Green", 0.02)
            ],
            "Middle Eastern": [
                ("Brown", 0.75), ("Hazel", 0.15), ("Green", 0.08), ("Blue", 0.02)
            ]
        }
        
        # Hair colors by ethnicity
        self.hair_colors = {
            "Caucasian": [
                ("Brown", 0.35), ("Blonde", 0.20), ("Black", 0.15), ("Auburn", 0.10),
                ("Red", 0.04), ("Gray", 0.10), ("White", 0.06)
            ],
            "African American": [
                ("Black", 0.85), ("Brown", 0.10), ("Gray", 0.04), ("White", 0.01)
            ],
            "Hispanic": [
                ("Black", 0.65), ("Brown", 0.25), ("Gray", 0.08), ("Auburn", 0.02)
            ],
            "Asian": [
                ("Black", 0.90), ("Brown", 0.08), ("Gray", 0.02)
            ],
            "Native American": [
                ("Black", 0.80), ("Brown", 0.15), ("Gray", 0.05)
            ],
            "Middle Eastern": [
                ("Black", 0.60), ("Brown", 0.30), ("Auburn", 0.05), ("Gray", 0.05)
            ]
        }
        
        # Hair types
        self.hair_types = {
            "Caucasian": [("Straight", 0.45), ("Wavy", 0.40), ("Curly", 0.15)],
            "African American": [("Curly", 0.60), ("Coily", 0.35), ("Wavy", 0.05)],
            "Hispanic": [("Wavy", 0.50), ("Straight", 0.30), ("Curly", 0.20)],
            "Asian": [("Straight", 0.80), ("Wavy", 0.18), ("Curly", 0.02)],
            "Native American": [("Straight", 0.70), ("Wavy", 0.25), ("Curly", 0.05)],
            "Middle Eastern": [("Wavy", 0.50), ("Curly", 0.30), ("Straight", 0.20)]
        }
        
        # Skin tones by ethnicity
        self.skin_tones = {
            "Caucasian": ["Fair", "Light", "Medium", "Olive", "Tan"],
            "African American": ["Dark", "Deep", "Medium-Dark", "Medium", "Light-Medium"],
            "Hispanic": ["Olive", "Medium", "Tan", "Light", "Medium-Dark"],
            "Asian": ["Light", "Medium", "Olive", "Fair", "Tan"],
            "Native American": ["Medium", "Tan", "Olive", "Medium-Dark", "Light"],
            "Middle Eastern": ["Olive", "Medium", "Tan", "Medium-Dark", "Light"]
        }
        
        # Body types
        self.body_types = {
            "M": [
                ("Ectomorph", 0.25),  # Lean, hard to gain weight
                ("Mesomorph", 0.40),  # Muscular, athletic
                ("Endomorph", 0.35)   # Stocky, easy to gain weight
            ],
            "F": [
                ("Ectomorph", 0.30),
                ("Mesomorph", 0.35),
                ("Endomorph", 0.35)
            ]
        }
        
        # Build descriptions
        self.builds = {
            "M": ["Slim", "Athletic", "Muscular", "Heavy", "Average", "Stocky", "Lean"],
            "F": ["Petite", "Slim", "Athletic", "Curvy", "Average", "Full-figured", "Lean"]
        }
        
        # Fingerprint patterns
        self.fingerprint_patterns = [
            ("Loop", 0.65), ("Whorl", 0.30), ("Arch", 0.05)
        ]
        
        # Vision categories
        self.vision_categories = [
            ("20/20", 0.35), ("20/25", 0.20), ("20/30", 0.15), ("20/40", 0.12),
            ("20/50", 0.08), ("20/60", 0.05), ("20/80", 0.03), ("20/100", 0.02)
        ]
        
        # Hearing categories
        self.hearing_categories = [
            ("Normal", 0.85), ("Mild Loss", 0.10), ("Moderate Loss", 0.04), ("Severe Loss", 0.01)
        ]
        
        # Activity levels
        self.activity_levels = [
            ("Sedentary", 0.25), ("Lightly Active", 0.35), ("Moderately Active", 0.25), ("Very Active", 0.15)
        ]
        
        # Exercise types
        self.exercise_types = {
            "Cardio": ["Running", "Cycling", "Swimming", "Walking", "Elliptical", "Rowing", "Dancing"],
            "Strength": ["Weight Lifting", "Bodyweight", "Resistance Bands", "CrossFit", "Powerlifting"],
            "Flexibility": ["Yoga", "Pilates", "Stretching", "Tai Chi", "Ballet"],
            "Sports": ["Tennis", "Basketball", "Soccer", "Golf", "Volleyball", "Baseball", "Hockey"],
            "Outdoor": ["Hiking", "Rock Climbing", "Skiing", "Surfing", "Kayaking", "Mountain Biking"]
        }
        
        # Dietary restrictions
        self.dietary_restrictions = [
            "None", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut Allergies",
            "Shellfish Allergy", "Keto", "Paleo", "Low-Sodium", "Diabetic", "Kosher", "Halal"
        ]
        
        # Environmental allergies
        self.environmental_allergies = [
            "Pollen", "Dust Mites", "Pet Dander", "Mold", "Ragweed", "Tree Pollen",
            "Grass Pollen", "Cockroach Allergens", "Latex", "Perfumes", "Smoke", "Chemicals"
        ]
        
        # Physical limitations
        self.physical_limitations = [
            "None", "Back Problems", "Knee Issues", "Shoulder Problems", "Arthritis",
            "Vision Impairment", "Hearing Impairment", "Mobility Issues", "Chronic Pain",
            "Heart Condition", "Respiratory Issues", "Balance Problems"
        ]
    
    def cm_to_feet_inches(self, cm: float) -> str:
        """Convert centimeters to feet and inches"""
        total_inches = cm / 2.54
        feet = int(total_inches // 12)
        inches = round(total_inches % 12)
        if inches == 12:
            feet += 1
            inches = 0
        return f"{feet}'{inches}\""
    
    def kg_to_lbs(self, kg: float) -> float:
        """Convert kilograms to pounds"""
        return round(kg * 2.20462, 1)
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> Tuple[float, str]:
        """Calculate BMI and category"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return round(bmi, 1), category
    
    def generate_height_weight(self, gender: str, ethnicity: str, age: int) -> Tuple[float, float]:
        """Generate realistic height and weight based on demographics"""
        # Map non-binary genders to binary for data lookup
        lookup_gender = gender
        if gender in ['O', 'U']:  # Other/Unknown
            lookup_gender = random.choice(['M', 'F'])
        
        data = self.height_weight_data[lookup_gender][ethnicity]
        
        # Generate height (normal distribution)
        height = random.gauss(data["height_mean"], data["height_std"])
        height = max(140, min(220, height))  # Reasonable bounds
        
        # Generate weight (normal distribution with BMI constraints)
        base_weight = random.gauss(data["weight_mean"], data["weight_std"])
        
        # Age adjustments (people tend to gain weight with age)
        if age > 30:
            age_factor = (age - 30) * 0.3  # 0.3kg per year after 30
            base_weight += age_factor
        
        # Ensure reasonable BMI range
        height_m = height / 100
        min_weight = 18.5 * (height_m ** 2)  # Minimum healthy BMI
        max_weight = 35 * (height_m ** 2)    # Maximum reasonable BMI
        
        weight = max(min_weight, min(max_weight, base_weight))
        
        return round(height, 1), round(weight, 1)
    
    def select_by_probability(self, options: List[Tuple[str, float]]) -> str:
        """Select option based on probability weights"""
        items, weights = zip(*options)
        return random.choices(items, weights=weights)[0]
    
    def generate_clothing_size(self, gender: str, height_cm: float, weight_kg: float) -> str:
        """Generate clothing size based on measurements"""
        bmi, _ = self.calculate_bmi(weight_kg, height_cm)
        
        if gender == "M":
            if bmi < 20:
                sizes = ["XS", "S"]
            elif bmi < 23:
                sizes = ["S", "M"]
            elif bmi < 26:
                sizes = ["M", "L"]
            elif bmi < 30:
                sizes = ["L", "XL"]
            else:
                sizes = ["XL", "XXL", "XXXL"]
        else:  # Female
            if bmi < 19:
                sizes = ["XS", "S"]
            elif bmi < 22:
                sizes = ["S", "M"]
            elif bmi < 25:
                sizes = ["M", "L"]
            elif bmi < 29:
                sizes = ["L", "XL"]
            else:
                sizes = ["XL", "XXL", "XXXL"]
        
        return random.choice(sizes)
    
    def generate_shoe_size(self, gender: str, height_cm: float) -> float:
        """Generate shoe size based on height and gender"""
        if gender == "M":
            # Men's sizes typically range from 7-14
            base_size = 8.5 + (height_cm - 175) * 0.1
            size = max(7, min(14, base_size + random.uniform(-1.5, 1.5)))
        else:
            # Women's sizes typically range from 5-11
            base_size = 7.5 + (height_cm - 162) * 0.08
            size = max(5, min(11, base_size + random.uniform(-1, 1)))
        
        # Round to nearest half size
        return round(size * 2) / 2
    
    def generate_distinguishing_marks(self, age: int) -> List[str]:
        """Generate distinguishing marks like scars, tattoos, etc."""
        marks = []
        
        # Scars (more likely with age)
        scar_probability = min(0.3 + (age - 18) * 0.01, 0.6)
        if random.random() < scar_probability:
            scar_types = [
                "Small scar on forehead", "Scar on left hand", "Surgical scar on abdomen",
                "Scar on right knee", "Small facial scar", "Scar on left arm"
            ]
            marks.append(random.choice(scar_types))
        
        # Tattoos (age and cultural dependent)
        tattoo_probability = 0.3 if age < 40 else 0.2
        if random.random() < tattoo_probability:
            tattoo_locations = [
                "Tattoo on right arm", "Small tattoo on wrist", "Tattoo on back",
                "Tattoo on left shoulder", "Small tattoo on ankle"
            ]
            num_tattoos = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            marks.extend(random.sample(tattoo_locations, min(num_tattoos, len(tattoo_locations))))
        
        # Birthmarks
        if random.random() < 0.15:
            birthmark_types = [
                "Birthmark on left cheek", "Small birthmark on neck", "Birthmark on right hand"
            ]
            marks.append(random.choice(birthmark_types))
        
        # Piercings
        piercing_probability = 0.4 if age < 35 else 0.2
        if random.random() < piercing_probability:
            piercing_types = [
                "Ear piercings", "Nose piercing", "Multiple ear piercings"
            ]
            marks.append(random.choice(piercing_types))
        
        return marks
    
    def generate_biometric_data(self, gender: str, ethnicity: str) -> BiometricData:
        """Generate biometric identifiers"""
        # Fingerprint pattern
        fingerprint = self.select_by_probability(self.fingerprint_patterns)
        
        # Iris pattern (simplified)
        iris_patterns = ["Crypts", "Furrows", "Pigment spots", "Complex pattern"]
        iris = random.choice(iris_patterns)
        
        # Facial structure measurements (normalized)
        facial_structure = {
            "face_width": round(random.uniform(0.4, 0.6), 3),
            "face_length": round(random.uniform(0.5, 0.7), 3),
            "nose_width": round(random.uniform(0.3, 0.5), 3),
            "mouth_width": round(random.uniform(0.4, 0.6), 3),
            "eye_distance": round(random.uniform(0.3, 0.4), 3),
            "forehead_height": round(random.uniform(0.3, 0.5), 3)
        }
        
        # Voice characteristics
        voice_pitch = "Low" if gender == "M" else random.choice(["High", "Medium"])
        voice_characteristics = {
            "pitch": voice_pitch,
            "tone": random.choice(["Smooth", "Rough", "Nasal", "Clear"]),
            "accent": random.choice(["None", "Regional", "Slight", "Pronounced"]),
            "speech_rate": random.choice(["Slow", "Normal", "Fast"])
        }
        
        # Gait pattern
        gait_pattern = {
            "stride_length": round(random.uniform(0.6, 0.8), 2),
            "cadence": round(random.uniform(90, 130), 1),  # steps per minute
            "foot_angle": round(random.uniform(-10, 10), 1),
            "balance": round(random.uniform(0.7, 1.0), 2)
        }
        
        # Hand geometry
        hand_geometry = {
            "hand_length": round(random.uniform(16, 22), 1),  # cm
            "hand_width": round(random.uniform(7, 10), 1),   # cm
            "finger_ratio": round(random.uniform(0.9, 1.1), 2),
            "palm_ratio": round(random.uniform(0.8, 1.2), 2)
        }
        
        return BiometricData(
            fingerprint_pattern=fingerprint,
            iris_pattern=iris,
            facial_structure=facial_structure,
            voice_characteristics=voice_characteristics,
            gait_pattern=gait_pattern,
            hand_geometry=hand_geometry
        )
    
    def generate_medical_measurements(self, age: int, bmi: float, fitness_level: str) -> MedicalMeasurements:
        """Generate medical measurements and health indicators"""
        # Blood pressure (age and fitness dependent)
        if fitness_level in ["Very Active", "Moderately Active"]:
            bp_systolic = random.randint(105, 125)
            bp_diastolic = random.randint(65, 80)
        elif age > 50:
            bp_systolic = random.randint(120, 140)
            bp_diastolic = random.randint(75, 90)
        else:
            bp_systolic = random.randint(110, 130)
            bp_diastolic = random.randint(70, 85)
        
        # Resting heart rate (fitness dependent)
        if fitness_level == "Very Active":
            rhr = random.randint(45, 65)
        elif fitness_level == "Moderately Active":
            rhr = random.randint(55, 75)
        elif fitness_level == "Lightly Active":
            rhr = random.randint(65, 80)
        else:  # Sedentary
            rhr = random.randint(70, 85)
        
        # Body fat percentage (BMI and fitness dependent)
        if bmi < 20:
            body_fat = random.uniform(8, 15)
        elif bmi < 25:
            body_fat = random.uniform(12, 20)
        elif bmi < 30:
            body_fat = random.uniform(18, 30)
        else:
            body_fat = random.uniform(25, 40)
        
        # Adjust for fitness level
        if fitness_level == "Very Active":
            body_fat *= 0.8
        elif fitness_level == "Moderately Active":
            body_fat *= 0.9
        
        # Muscle mass (inverse relationship with body fat)
        muscle_mass = max(25, 50 - (body_fat * 0.8) + random.uniform(-5, 5))
        
        # Bone density
        if age > 50:
            bone_density = random.choice(["Normal", "Osteopenia", "Osteoporosis"])
        else:
            bone_density = random.choice(["Normal", "Above Average"])
        
        # Vision
        vision_left = self.select_by_probability(self.vision_categories)
        vision_right = self.select_by_probability(self.vision_categories)
        
        # Hearing
        hearing_left = self.select_by_probability(self.hearing_categories)
        hearing_right = self.select_by_probability(self.hearing_categories)
        
        # Dominant hand
        dominant_hand = random.choices(["Right", "Left", "Ambidextrous"], weights=[0.89, 0.10, 0.01])[0]
        
        # Flexibility (1-10 scale)
        if fitness_level in ["Very Active", "Moderately Active"]:
            flexibility = random.randint(6, 10)
        else:
            flexibility = random.randint(3, 7)
        
        # Endurance level
        endurance_levels = ["Poor", "Fair", "Good", "Excellent"]
        if fitness_level == "Very Active":
            endurance = random.choice(["Good", "Excellent"])
        elif fitness_level == "Moderately Active":
            endurance = random.choice(["Fair", "Good"])
        else:
            endurance = random.choice(["Poor", "Fair"])
        
        return MedicalMeasurements(
            blood_pressure_systolic=bp_systolic,
            blood_pressure_diastolic=bp_diastolic,
            resting_heart_rate=rhr,
            body_fat_percentage=round(body_fat, 1),
            muscle_mass_percentage=round(muscle_mass, 1),
            bone_density=bone_density,
            vision_left_eye=vision_left,
            vision_right_eye=vision_right,
            hearing_left_ear=hearing_left,
            hearing_right_ear=hearing_right,
            dominant_hand=dominant_hand,
            flexibility_score=flexibility,
            endurance_level=endurance
        )
    
    def generate_fitness_profile(self, age: int, activity_level: str, health_conditions: List[str]) -> FitnessProfile:
        """Generate comprehensive fitness profile"""
        # Preferred exercises based on age and activity level
        preferred_exercises = []
        num_exercises = {"Sedentary": 1, "Lightly Active": 2, "Moderately Active": 3, "Very Active": 4}[activity_level]
        
        exercise_pool = []
        for category, exercises in self.exercise_types.items():
            if age > 60 and category in ["Flexibility", "Cardio"]:
                exercise_pool.extend(exercises[:3])  # Gentler exercises
            elif activity_level == "Very Active":
                exercise_pool.extend(exercises)
            else:
                exercise_pool.extend(exercises[:4])
        
        preferred_exercises = random.sample(exercise_pool, min(num_exercises, len(exercise_pool)))
        
        # Max heart rate (220 - age formula)
        max_hr = 220 - age
        
        # Target heart rate zone (50-85% of max)
        target_zone = (int(max_hr * 0.5), int(max_hr * 0.85))
        
        # VO2 max (if very active)
        vo2_max = None
        if activity_level == "Very Active":
            if age < 30:
                vo2_max = random.uniform(45, 65)
            elif age < 50:
                vo2_max = random.uniform(35, 55)
            else:
                vo2_max = random.uniform(25, 45)
        
        # Strength level
        strength_levels = ["Beginner", "Intermediate", "Advanced", "Elite"]
        if activity_level == "Very Active":
            strength = random.choice(["Intermediate", "Advanced", "Elite"])
        elif activity_level == "Moderately Active":
            strength = random.choice(["Beginner", "Intermediate"])
        else:
            strength = "Beginner"
        
        # Cardiovascular fitness
        cardio_fitness = {
            "Very Active": random.choice(["Good", "Excellent"]),
            "Moderately Active": random.choice(["Fair", "Good"]),
            "Lightly Active": random.choice(["Poor", "Fair"]),
            "Sedentary": "Poor"
        }[activity_level]
        
        # Flexibility rating
        flexibility_rating = random.choice(["Poor", "Fair", "Good", "Excellent"])
        
        # Fitness goals
        goal_options = [
            "Weight Loss", "Muscle Gain", "Endurance", "Strength", "Flexibility",
            "General Health", "Sport Performance", "Stress Relief", "Rehabilitation"
        ]
        num_goals = random.randint(1, 3)
        fitness_goals = random.sample(goal_options, num_goals)
        
        # Workout frequency
        frequency_map = {
            "Very Active": random.choice(["5-6 times/week", "Daily"]),
            "Moderately Active": random.choice(["3-4 times/week", "4-5 times/week"]),
            "Lightly Active": random.choice(["1-2 times/week", "2-3 times/week"]),
            "Sedentary": random.choice(["Rarely", "1-2 times/week"])
        }
        workout_frequency = frequency_map[activity_level]
        
        # Gym membership
        gym_membership = random.random() < {"Very Active": 0.8, "Moderately Active": 0.6, "Lightly Active": 0.3, "Sedentary": 0.1}[activity_level]
        
        return FitnessProfile(
            activity_level=activity_level,
            preferred_exercises=preferred_exercises,
            max_heart_rate=max_hr,
            target_heart_rate_zone=target_zone,
            vo2_max=round(vo2_max, 1) if vo2_max else None,
            strength_level=strength,
            cardiovascular_fitness=cardio_fitness,
            flexibility_rating=flexibility_rating,
            fitness_goals=fitness_goals,
            workout_frequency=workout_frequency,
            gym_membership=gym_membership
        )
    
    def generate_physical_profile(self, gender: str, age: int, ethnicity: str = "Caucasian") -> PhysicalProfile:
        """Generate complete physical profile"""
        # Generate height and weight
        height_cm, weight_kg = self.generate_height_weight(gender, ethnicity, age)
        height_ft_in = self.cm_to_feet_inches(height_cm)
        weight_lbs = self.kg_to_lbs(weight_kg)
        
        # Calculate BMI
        bmi, bmi_category = self.calculate_bmi(weight_kg, height_cm)
        
        # Generate physical characteristics
        # Map non-binary genders to binary for data lookup
        lookup_gender = gender
        if gender in ['O', 'U']:  # Other/Unknown
            lookup_gender = random.choice(['M', 'F'])
        
        body_type = self.select_by_probability(self.body_types[lookup_gender])
        eye_color = self.select_by_probability(self.eye_colors.get(ethnicity, self.eye_colors["Caucasian"]))
        hair_color = self.select_by_probability(self.hair_colors.get(ethnicity, self.hair_colors["Caucasian"]))
        hair_type = self.select_by_probability(self.hair_types.get(ethnicity, self.hair_types["Caucasian"]))
        skin_tone = random.choice(self.skin_tones.get(ethnicity, self.skin_tones["Caucasian"]))
        build = random.choice(self.builds[lookup_gender])
        
        shoe_size = self.generate_shoe_size(lookup_gender, height_cm)
        clothing_size = self.generate_clothing_size(lookup_gender, height_cm, weight_kg)
        distinguishing_marks = self.generate_distinguishing_marks(age)
        
        physical_characteristics = PhysicalCharacteristics(
            height_cm=height_cm,
            height_ft_in=height_ft_in,
            weight_kg=weight_kg,
            weight_lbs=weight_lbs,
            bmi=bmi,
            bmi_category=bmi_category,
            body_type=body_type,
            eye_color=eye_color,
            hair_color=hair_color,
            hair_type=hair_type,
            skin_tone=skin_tone,
            ethnicity=ethnicity,
            build=build,
            shoe_size_us=shoe_size,
            clothing_size=clothing_size,
            distinguishing_marks=distinguishing_marks
        )
        
        # Generate biometric data
        biometric_data = self.generate_biometric_data(gender, ethnicity)
        
        # Determine activity level
        activity_level = self.select_by_probability(self.activity_levels)
        
        # Generate medical measurements
        medical_measurements = self.generate_medical_measurements(age, bmi, activity_level)
        
        # Generate fitness profile
        fitness_profile = self.generate_fitness_profile(age, activity_level, [])
        
        # Generate limitations and restrictions
        limitations = []
        if age > 50 and random.random() < 0.3:
            limitations.append(random.choice([
                "Arthritis", "Back Problems", "Knee Issues", "Shoulder Problems"
            ]))
        if random.random() < 0.1:
            limitations.append(random.choice(self.physical_limitations[1:]))  # Exclude "None"
        
        # Environmental allergies
        allergies = []
        if random.random() < 0.4:  # 40% have some environmental allergies
            num_allergies = random.randint(1, 3)
            allergies = random.sample(self.environmental_allergies, num_allergies)
        
        # Dietary restrictions
        dietary = []
        if random.random() < 0.3:  # 30% have dietary restrictions
            dietary.append(random.choice(self.dietary_restrictions[1:]))  # Exclude "None"
        
        return PhysicalProfile(
            physical_characteristics=physical_characteristics,
            biometric_data=biometric_data,
            medical_measurements=medical_measurements,
            fitness_profile=fitness_profile,
            physical_limitations=limitations,
            allergies_environmental=allergies,
            dietary_restrictions=dietary
        )