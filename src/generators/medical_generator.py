import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import string

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field
from pydantic import validator


class MedicalCondition(BaseModel):
    condition_name: str
    icd10_code: str
    diagnosis_date: date
    severity: str  # mild, moderate, severe
    is_chronic: bool
    is_active: bool
    treating_physician: str
    medications: List[str] = Field(default_factory=list)


class Medication(BaseModel):
    medication_name: str
    generic_name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    prescribing_doctor: str
    reason: str
    refills_remaining: int


class Allergy(BaseModel):
    allergen: str
    reaction_type: str  # mild, moderate, severe, anaphylactic
    discovered_date: date
    notes: Optional[str] = None


class MedicalProcedure(BaseModel):
    procedure_name: str
    cpt_code: str
    procedure_date: date
    performing_physician: str
    facility: str
    outcome: str
    complications: Optional[str] = None


class VitalSigns(BaseModel):
    measurement_date: date
    height_cm: float
    weight_kg: float
    bmi: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    temperature_celsius: float
    respiratory_rate: int
    oxygen_saturation: int


class MedicalProfile(BaseModel):
    blood_type: str
    primary_care_physician: str
    insurance_provider: str
    insurance_policy_number: str
    medical_record_number: str
    conditions: List[MedicalCondition] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    allergies: List[Allergy] = Field(default_factory=list)
    procedures: List[MedicalProcedure] = Field(default_factory=list)
    vital_signs_history: List[VitalSigns] = Field(default_factory=list)
    immunizations: Dict[str, date] = Field(default_factory=dict)
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str


class MedicalGenerator:
    """Generator for comprehensive medical and health data"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Common medical conditions by age group
        self.conditions_by_age = {
            "young": [  # 18-35
                ("Asthma", "J45.9", 0.08),
                ("Anxiety Disorder", "F41.9", 0.15),
                ("Depression", "F32.9", 0.12),
                ("Allergic Rhinitis", "J30.9", 0.20),
                ("ADHD", "F90.9", 0.05),
                ("Migraine", "G43.9", 0.10),
                ("Back Pain", "M54.5", 0.15),
                ("Irritable Bowel Syndrome", "K58.9", 0.08),
                ("Eczema", "L20.9", 0.10),
                ("Sleep Disorder", "G47.9", 0.12)
            ],
            "middle": [  # 36-55
                ("Hypertension", "I10", 0.25),
                ("Type 2 Diabetes", "E11.9", 0.15),
                ("High Cholesterol", "E78.5", 0.20),
                ("Depression", "F32.9", 0.15),
                ("Back Pain", "M54.5", 0.25),
                ("Sleep Apnea", "G47.33", 0.10),
                ("Arthritis", "M19.9", 0.12),
                ("GERD", "K21.9", 0.15),
                ("Thyroid Disorder", "E03.9", 0.08),
                ("Kidney Stones", "N20.0", 0.05)
            ],
            "senior": [  # 56+
                ("Hypertension", "I10", 0.50),
                ("Type 2 Diabetes", "E11.9", 0.25),
                ("Heart Disease", "I25.9", 0.20),
                ("Arthritis", "M19.9", 0.35),
                ("COPD", "J44.9", 0.10),
                ("Dementia", "F03.9", 0.08),
                ("Osteoporosis", "M81.9", 0.15),
                ("Prostate Issues", "N40.9", 0.30),  # for males
                ("Cataracts", "H25.9", 0.20),
                ("Hearing Loss", "H91.9", 0.25)
            ]
        }
        
        # Common medications
        self.medications_db = {
            "Hypertension": [
                ("Lisinopril", "Lisinopril", "10mg", "Once daily"),
                ("Amlodipine", "Amlodipine", "5mg", "Once daily"),
                ("Metoprolol", "Metoprolol tartrate", "50mg", "Twice daily"),
                ("Losartan", "Losartan", "50mg", "Once daily"),
                ("Hydrochlorothiazide", "HCTZ", "25mg", "Once daily")
            ],
            "Type 2 Diabetes": [
                ("Metformin", "Metformin HCl", "1000mg", "Twice daily"),
                ("Glipizide", "Glipizide", "10mg", "Once daily"),
                ("Januvia", "Sitagliptin", "100mg", "Once daily"),
                ("Lantus", "Insulin glargine", "20 units", "Once daily at bedtime"),
                ("Jardiance", "Empagliflozin", "10mg", "Once daily")
            ],
            "Depression": [
                ("Sertraline", "Sertraline HCl", "100mg", "Once daily"),
                ("Fluoxetine", "Fluoxetine HCl", "20mg", "Once daily"),
                ("Escitalopram", "Escitalopram", "10mg", "Once daily"),
                ("Wellbutrin", "Bupropion", "150mg", "Twice daily"),
                ("Venlafaxine", "Venlafaxine ER", "75mg", "Once daily")
            ],
            "Pain": [
                ("Ibuprofen", "Ibuprofen", "800mg", "Three times daily as needed"),
                ("Acetaminophen", "Acetaminophen", "500mg", "Every 6 hours as needed"),
                ("Naproxen", "Naproxen sodium", "500mg", "Twice daily"),
                ("Tramadol", "Tramadol HCl", "50mg", "Every 6 hours as needed"),
                ("Gabapentin", "Gabapentin", "300mg", "Three times daily")
            ],
            "Allergies": [
                ("Zyrtec", "Cetirizine", "10mg", "Once daily"),
                ("Allegra", "Fexofenadine", "180mg", "Once daily"),
                ("Flonase", "Fluticasone", "2 sprays", "Once daily in each nostril"),
                ("Claritin", "Loratadine", "10mg", "Once daily"),
                ("Singulair", "Montelukast", "10mg", "Once daily at bedtime")
            ]
        }
        
        # Common allergies
        self.common_allergies = [
            ("Penicillin", "anaphylactic", 0.08),
            ("Peanuts", "severe", 0.02),
            ("Tree nuts", "moderate", 0.03),
            ("Shellfish", "severe", 0.025),
            ("Eggs", "mild", 0.02),
            ("Milk", "moderate", 0.03),
            ("Soy", "mild", 0.01),
            ("Wheat/Gluten", "moderate", 0.015),
            ("Fish", "severe", 0.01),
            ("Latex", "moderate", 0.04),
            ("Sulfa drugs", "moderate", 0.03),
            ("Aspirin", "mild", 0.02),
            ("Iodine", "moderate", 0.01),
            ("Bee stings", "severe", 0.03),
            ("Dust mites", "mild", 0.20),
            ("Pollen", "mild", 0.30),
            ("Pet dander", "moderate", 0.15),
            ("Mold", "mild", 0.10)
        ]
        
        # Blood types with distribution
        self.blood_types = [
            ("O+", 0.374),
            ("O-", 0.066),
            ("A+", 0.357),
            ("A-", 0.063),
            ("B+", 0.085),
            ("B-", 0.015),
            ("AB+", 0.034),
            ("AB-", 0.006)
        ]
        
        # Insurance providers
        self.insurance_providers = [
            "Blue Cross Blue Shield",
            "UnitedHealth",
            "Kaiser Permanente",
            "Anthem",
            "Aetna",
            "Cigna",
            "Humana",
            "Centene",
            "Health Care Service Corporation",
            "CVS Health",
            "Molina Healthcare",
            "Independence Health Group",
            "GuideWell",
            "Highmark",
            "Blue Shield of California"
        ]
        
        # Medical facilities
        self.medical_facilities = [
            "General Hospital",
            "Regional Medical Center",
            "Community Hospital",
            "University Hospital",
            "Memorial Hospital",
            "St. Mary's Hospital",
            "Presbyterian Hospital",
            "Methodist Hospital",
            "Baptist Medical Center",
            "Mercy Hospital"
        ]
        
        # Common procedures
        self.common_procedures = [
            ("Colonoscopy", "45380", "routine", ["No polyps found", "Small polyp removed", "Multiple polyps removed"]),
            ("Upper Endoscopy", "43235", "diagnostic", ["Normal", "Mild gastritis", "GERD confirmed"]),
            ("Mammogram", "77067", "screening", ["Normal", "Benign finding", "Requires follow-up"]),
            ("MRI Brain", "70553", "diagnostic", ["Normal", "Age-related changes", "Abnormality detected"]),
            ("CT Chest", "71260", "diagnostic", ["Normal", "Small nodule noted", "Requires follow-up"]),
            ("Echocardiogram", "93306", "diagnostic", ["Normal heart function", "Mild dysfunction", "Moderate dysfunction"]),
            ("Knee Arthroscopy", "29881", "therapeutic", ["Successful repair", "Partial improvement", "Complex repair"]),
            ("Cataract Surgery", "66984", "therapeutic", ["Successful", "Minor complications", "Good outcome"]),
            ("Gallbladder Removal", "47562", "therapeutic", ["Laparoscopic success", "Converted to open", "Routine"]),
            ("Hernia Repair", "49505", "therapeutic", ["Successful repair", "Mesh placed", "No complications"])
        ]
        
        # Immunizations
        self.immunizations = [
            "Influenza",
            "Tdap (Tetanus, Diphtheria, Pertussis)",
            "MMR (Measles, Mumps, Rubella)",
            "Varicella (Chickenpox)",
            "Hepatitis A",
            "Hepatitis B",
            "HPV",
            "Pneumococcal",
            "Meningococcal",
            "COVID-19",
            "Shingles",
            "Polio"
        ]
        
        # Physician name patterns
        self.physician_prefixes = ["Dr.", "Dr.", "Dr.", "Dr.", "Dr."]  # Always Dr.
        self.physician_first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
            "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
            "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"
        ]
        self.physician_last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
            "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Patel", "Chen", "Kumar", "Singh", "Ahmed", "Kim"
        ]
        self.physician_suffixes = ["MD", "MD", "MD", "MD, PhD", "DO", "MD, FACC", "MD, FACS"]
    
    def generate_physician_name(self) -> str:
        """Generate a realistic physician name"""
        prefix = random.choice(self.physician_prefixes)
        first = random.choice(self.physician_first_names)
        last = random.choice(self.physician_last_names)
        suffix = random.choice(self.physician_suffixes)
        return f"{prefix} {first} {last}, {suffix}"
    
    def generate_blood_type(self) -> str:
        """Generate blood type based on real distribution"""
        types, weights = zip(*self.blood_types)
        return random.choices(types, weights=weights)[0]
    
    def generate_medical_conditions(self, age: int, gender: str) -> List[MedicalCondition]:
        """Generate age-appropriate medical conditions"""
        conditions = []
        
        # Determine age group
        if age < 36:
            age_group = "young"
        elif age < 56:
            age_group = "middle"
        else:
            age_group = "senior"
        
        # Select conditions based on probability
        for condition_name, icd_code, probability in self.conditions_by_age[age_group]:
            # Skip gender-specific conditions
            if condition_name == "Prostate Issues" and gender != "M":
                continue
                
            if random.random() < probability:
                # Generate diagnosis date (could be years ago)
                years_since_diagnosis = random.randint(0, min(10, age - 18))
                diagnosis_date = date.today() - timedelta(days=years_since_diagnosis * 365 + random.randint(0, 364))
                
                # Determine severity
                severity = random.choices(
                    ["mild", "moderate", "severe"],
                    weights=[0.5, 0.35, 0.15]
                )[0]
                
                # Generate medications for this condition
                medications = []
                if condition_name in ["Hypertension", "Type 2 Diabetes", "Depression"]:
                    # These conditions usually have medications
                    if random.random() < 0.8:
                        med_options = self.medications_db.get(condition_name, [])
                        if med_options:
                            num_meds = random.randint(1, min(3, len(med_options)))
                            selected_meds = random.sample(med_options, num_meds)
                            medications = [f"{med[0]} {med[2]}" for med in selected_meds]
                
                condition = MedicalCondition(
                    condition_name=condition_name,
                    icd10_code=icd_code,
                    diagnosis_date=diagnosis_date,
                    severity=severity,
                    is_chronic=condition_name not in ["Back Pain", "Kidney Stones", "Migraine"],
                    is_active=random.random() < 0.85,  # Most conditions remain active
                    treating_physician=self.generate_physician_name(),
                    medications=medications
                )
                conditions.append(condition)
        
        # Apply variability
        if self.variability and self.variability.should_apply(0.1):
            # Sometimes add rare conditions
            rare_conditions = [
                ("Lupus", "M32.9"),
                ("Multiple Sclerosis", "G35"),
                ("Crohn's Disease", "K50.9"),
                ("Psoriasis", "L40.9"),
                ("Fibromyalgia", "M79.7")
            ]
            if random.random() < 0.05:
                rare = random.choice(rare_conditions)
                conditions.append(MedicalCondition(
                    condition_name=rare[0],
                    icd10_code=rare[1],
                    diagnosis_date=date.today() - timedelta(days=random.randint(180, 1825)),
                    severity="moderate",
                    is_chronic=True,
                    is_active=True,
                    treating_physician=self.generate_physician_name(),
                    medications=[]
                ))
        
        return conditions
    
    def generate_medications(self, conditions: List[MedicalCondition], age: int) -> List[Medication]:
        """Generate medication list based on conditions"""
        medications = []
        physicians = [self.generate_physician_name() for _ in range(3)]
        
        # Medications for conditions
        for condition in conditions:
            if condition.medications:
                physician = condition.treating_physician
                for med_string in condition.medications:
                    # Parse medication string
                    parts = med_string.split()
                    med_name = parts[0]
                    dosage = parts[1] if len(parts) > 1 else "Unknown"
                    
                    # Find full medication info
                    med_info = None
                    for meds in self.medications_db.values():
                        for m in meds:
                            if m[0] == med_name:
                                med_info = m
                                break
                        if med_info:
                            break
                    
                    if med_info:
                        start_date = condition.diagnosis_date + timedelta(days=random.randint(0, 30))
                        medication = Medication(
                            medication_name=med_info[0],
                            generic_name=med_info[1],
                            dosage=med_info[2],
                            frequency=med_info[3],
                            start_date=start_date,
                            end_date=None if condition.is_active else start_date + timedelta(days=random.randint(30, 365)),
                            prescribing_doctor=physician,
                            reason=condition.condition_name,
                            refills_remaining=random.randint(0, 11)
                        )
                        medications.append(medication)
        
        # Add common OTC medications
        if random.random() < 0.6:
            otc_meds = [
                ("Vitamin D", "Cholecalciferol", "2000 IU", "Once daily", "Supplement"),
                ("Multivitamin", "Multiple vitamins", "1 tablet", "Once daily", "Supplement"),
                ("Omega-3", "Fish oil", "1000mg", "Once daily", "Heart health"),
                ("Calcium", "Calcium carbonate", "600mg", "Twice daily", "Bone health"),
                ("Vitamin B12", "Cyanocobalamin", "1000mcg", "Once daily", "Energy"),
                ("Probiotic", "Mixed cultures", "10 billion CFU", "Once daily", "Digestive health")
            ]
            
            num_otc = random.randint(1, 3)
            selected_otc = random.sample(otc_meds, num_otc)
            
            for otc in selected_otc:
                start_date = date.today() - timedelta(days=random.randint(30, 730))
                medication = Medication(
                    medication_name=otc[0],
                    generic_name=otc[1],
                    dosage=otc[2],
                    frequency=otc[3],
                    start_date=start_date,
                    end_date=None,
                    prescribing_doctor="OTC",
                    reason=otc[4],
                    refills_remaining=0
                )
                medications.append(medication)
        
        return medications
    
    def generate_allergies(self, age: int) -> List[Allergy]:
        """Generate allergies based on probability"""
        allergies = []
        
        for allergen, reaction, probability in self.common_allergies:
            if random.random() < probability:
                # Determine when allergy was discovered
                max_years_ago = min(age - 5, 40)  # Discovered after age 5
                years_ago = random.randint(0, max_years_ago)
                discovered_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 364))
                
                # Add notes for severe reactions
                notes = None
                if reaction in ["severe", "anaphylactic"]:
                    notes = random.choice([
                        "Carries EpiPen",
                        "Requires immediate medical attention",
                        "Previous hospitalization",
                        "Avoid all exposure"
                    ])
                
                allergy = Allergy(
                    allergen=allergen,
                    reaction_type=reaction,
                    discovered_date=discovered_date,
                    notes=notes
                )
                allergies.append(allergy)
        
        return allergies
    
    def generate_procedures(self, age: int, conditions: List[MedicalCondition]) -> List[MedicalProcedure]:
        """Generate medical procedures based on age and conditions"""
        procedures = []
        
        # Age-based screening procedures
        if age >= 50:
            # Colonoscopy every 10 years
            last_colonoscopy_years = (age - 50) % 10
            if last_colonoscopy_years < 2:
                proc_date = date.today() - timedelta(days=last_colonoscopy_years * 365 + random.randint(0, 364))
                procedures.append(MedicalProcedure(
                    procedure_name="Colonoscopy",
                    cpt_code="45380",
                    procedure_date=proc_date,
                    performing_physician=self.generate_physician_name(),
                    facility=random.choice(self.medical_facilities),
                    outcome=random.choice(["No polyps found", "Small polyp removed", "Benign polyps removed"]),
                    complications=None if random.random() < 0.95 else "Minor bleeding"
                ))
        
        if age >= 40:
            # Annual mammogram for females
            if random.random() < 0.7:  # Assuming some gender distribution
                years_of_mammograms = min(5, age - 40)
                for i in range(years_of_mammograms):
                    proc_date = date.today() - timedelta(days=i * 365 + random.randint(0, 60))
                    procedures.append(MedicalProcedure(
                        procedure_name="Mammogram",
                        cpt_code="77067",
                        procedure_date=proc_date,
                        performing_physician=self.generate_physician_name(),
                        facility=random.choice(self.medical_facilities),
                        outcome="Normal - BIRADS 1" if random.random() < 0.9 else "Benign finding - BIRADS 2",
                        complications=None
                    ))
        
        # Condition-based procedures
        for condition in conditions:
            if condition.condition_name == "Heart Disease" and random.random() < 0.5:
                proc_date = condition.diagnosis_date + timedelta(days=random.randint(30, 180))
                procedures.append(MedicalProcedure(
                    procedure_name="Cardiac Catheterization",
                    cpt_code="93458",
                    procedure_date=proc_date,
                    performing_physician=self.generate_physician_name(),
                    facility=random.choice(self.medical_facilities),
                    outcome=random.choice(["No significant blockage", "Stent placed", "Medical management"]),
                    complications=None if random.random() < 0.9 else "Access site hematoma"
                ))
            
            if condition.condition_name == "Cataracts" and random.random() < 0.7:
                proc_date = condition.diagnosis_date + timedelta(days=random.randint(90, 365))
                procedures.append(MedicalProcedure(
                    procedure_name="Cataract Surgery",
                    cpt_code="66984",
                    procedure_date=proc_date,
                    performing_physician=self.generate_physician_name(),
                    facility=random.choice(self.medical_facilities),
                    outcome="Successful - vision improved",
                    complications=None
                ))
        
        # Random other procedures
        if random.random() < 0.3:
            proc_choice = random.choice(self.common_procedures)
            proc_date = date.today() - timedelta(days=random.randint(30, 1095))
            procedures.append(MedicalProcedure(
                procedure_name=proc_choice[0],
                cpt_code=proc_choice[1],
                procedure_date=proc_date,
                performing_physician=self.generate_physician_name(),
                facility=random.choice(self.medical_facilities),
                outcome=random.choice(proc_choice[3]),
                complications=None if random.random() < 0.9 else "Minor complication"
            ))
        
        return procedures
    
    def generate_vital_signs(self, age: int, conditions: List[MedicalCondition], 
                           height_cm: float, weight_kg: float) -> List[VitalSigns]:
        """Generate vital signs history"""
        vital_signs = []
        
        # Generate last 5 visits
        for i in range(5):
            measurement_date = date.today() - timedelta(days=i * 180 + random.randint(0, 30))
            
            # Weight can fluctuate
            visit_weight = weight_kg + random.uniform(-3, 3)
            bmi = visit_weight / ((height_cm / 100) ** 2)
            
            # Blood pressure affected by conditions
            has_hypertension = any(c.condition_name == "Hypertension" for c in conditions)
            if has_hypertension:
                systolic = random.randint(130, 160)
                diastolic = random.randint(80, 100)
            else:
                systolic = random.randint(110, 130)
                diastolic = random.randint(65, 85)
            
            # Heart rate
            heart_rate = random.randint(60, 90)
            if age > 60:
                heart_rate += random.randint(0, 10)
            
            # Temperature (usually normal)
            temp = random.uniform(36.3, 37.1)
            if random.random() < 0.05:  # Occasionally elevated
                temp = random.uniform(37.5, 38.5)
            
            vitals = VitalSigns(
                measurement_date=measurement_date,
                height_cm=height_cm,
                weight_kg=round(visit_weight, 1),
                bmi=round(bmi, 1),
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                heart_rate=heart_rate,
                temperature_celsius=round(temp, 1),
                respiratory_rate=random.randint(12, 18),
                oxygen_saturation=random.randint(95, 100)
            )
            vital_signs.append(vitals)
        
        return vital_signs
    
    def generate_immunizations(self, age: int) -> Dict[str, date]:
        """Generate immunization history"""
        immunizations = {}
        
        # Childhood vaccines (assumed if adult)
        if age >= 18:
            childhood_vaccines = ["MMR", "Varicella", "Hepatitis B", "Polio"]
            for vaccine in childhood_vaccines:
                # Received in childhood
                years_ago = age - random.randint(2, 16)
                immunizations[vaccine] = date.today() - timedelta(days=years_ago * 365)
        
        # Annual flu shot
        if random.random() < 0.6:
            # Last flu shot within past year
            immunizations["Influenza"] = date.today() - timedelta(days=random.randint(30, 365))
        
        # COVID-19 vaccine
        if random.random() < 0.75:
            # Primary series 2-3 years ago
            immunizations["COVID-19"] = date.today() - timedelta(days=random.randint(730, 1095))
            if random.random() < 0.6:
                # Booster
                immunizations["COVID-19 Booster"] = date.today() - timedelta(days=random.randint(180, 365))
        
        # Age-specific vaccines
        if age >= 65:
            if random.random() < 0.7:
                immunizations["Pneumococcal"] = date.today() - timedelta(days=random.randint(365, 1825))
            if random.random() < 0.6:
                immunizations["Shingles"] = date.today() - timedelta(days=random.randint(180, 1095))
        
        # Tdap every 10 years
        if age >= 18:
            last_tdap_years = random.randint(0, 9)
            immunizations["Tdap"] = date.today() - timedelta(days=last_tdap_years * 365 + random.randint(0, 364))
        
        return immunizations
    
    def generate_medical_profile(self, age: int, gender: str, height_cm: float, 
                               weight_kg: float, emergency_contact: Tuple[str, str, str]) -> MedicalProfile:
        """Generate complete medical profile"""
        # Generate base components
        conditions = self.generate_medical_conditions(age, gender)
        medications = self.generate_medications(conditions, age)
        allergies = self.generate_allergies(age)
        procedures = self.generate_procedures(age, conditions)
        vital_signs = self.generate_vital_signs(age, conditions, height_cm, weight_kg)
        immunizations = self.generate_immunizations(age)
        
        # Generate identifiers
        mrn = f"MRN{random.randint(100000, 999999)}"
        policy_number = f"{random.choice(string.ascii_uppercase)}{random.randint(100000000, 999999999)}"
        
        # Apply variability to missing data
        if self.variability:
            if self.variability.should_apply(self.variability.missing_data_rate):
                # Sometimes missing insurance
                insurance_provider = "Unknown"
                policy_number = "Unknown"
            else:
                insurance_provider = random.choice(self.insurance_providers)
            
            if self.variability.should_apply(0.02):
                # Rarely missing PCP
                pcp = "No PCP assigned"
            else:
                pcp = self.generate_physician_name()
        else:
            insurance_provider = random.choice(self.insurance_providers)
            pcp = self.generate_physician_name()
        
        return MedicalProfile(
            blood_type=self.generate_blood_type(),
            primary_care_physician=pcp,
            insurance_provider=insurance_provider,
            insurance_policy_number=policy_number,
            medical_record_number=mrn,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            procedures=procedures,
            vital_signs_history=vital_signs,
            immunizations=immunizations,
            emergency_contact_name=emergency_contact[0],
            emergency_contact_phone=emergency_contact[1],
            emergency_contact_relationship=emergency_contact[2]
        )