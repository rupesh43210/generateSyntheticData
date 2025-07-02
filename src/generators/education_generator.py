import random
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
import string

from src.core.variability import VariabilityEngine
from pydantic import BaseModel, Field
from enum import Enum


class DegreeType(str, Enum):
    HIGH_SCHOOL = "High School Diploma"
    GED = "GED"
    CERTIFICATE = "Certificate"
    ASSOCIATE = "Associate Degree"
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    DOCTORATE = "Doctorate"
    PROFESSIONAL = "Professional Degree"


class EducationLevel(str, Enum):
    ELEMENTARY = "Elementary"
    MIDDLE_SCHOOL = "Middle School"
    HIGH_SCHOOL = "High School"
    UNDERGRADUATE = "Undergraduate"
    GRADUATE = "Graduate"
    POSTGRADUATE = "Postgraduate"


class Institution(BaseModel):
    name: str
    type: str  # Public, Private, Community College, Technical School, etc.
    location_city: str
    location_state: str
    established_year: int
    accreditation: str
    ranking: Optional[int] = None
    website: str


class Degree(BaseModel):
    degree_type: DegreeType
    major: str
    minor: Optional[str] = None
    specialization: Optional[str] = None
    institution: Institution
    start_date: date
    graduation_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: Optional[str] = None  # Magna Cum Laude, Phi Beta Kappa, etc.
    thesis_title: Optional[str] = None
    advisor: Optional[str] = None
    is_completed: bool = True


class Course(BaseModel):
    course_code: str
    course_name: str
    credit_hours: int
    semester: str
    year: int
    grade: str
    professor: str
    description: str


class Certification(BaseModel):
    certification_name: str
    issuing_organization: str
    issue_date: date
    expiry_date: Optional[date] = None
    certification_id: str
    verification_url: Optional[str] = None
    is_active: bool = True


class ScholarshipAward(BaseModel):
    scholarship_name: str
    amount: float
    academic_year: str
    criteria: str
    sponsor: str


class ExtracurricularActivity(BaseModel):
    activity_name: str
    activity_type: str  # Sports, Club, Volunteer, etc.
    role: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    achievements: List[str] = Field(default_factory=list)


class AcademicAchievement(BaseModel):
    achievement_name: str
    achievement_type: str  # Award, Recognition, Publication, etc.
    date_received: date
    description: str
    issuing_body: str


class StudentLoan(BaseModel):
    loan_type: str  # Federal, Private, PLUS
    lender: str
    principal_amount: float
    current_balance: float
    interest_rate: float
    monthly_payment: float
    start_date: date
    status: str  # Active, Deferred, Forbearance, Paid Off


class EducationProfile(BaseModel):
    highest_education_level: DegreeType
    degrees: List[Degree] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    courses: List[Course] = Field(default_factory=list)
    scholarships: List[ScholarshipAward] = Field(default_factory=list)
    extracurricular_activities: List[ExtracurricularActivity] = Field(default_factory=list)
    academic_achievements: List[AcademicAchievement] = Field(default_factory=list)
    student_loans: List[StudentLoan] = Field(default_factory=list)
    student_id_numbers: Dict[str, str] = Field(default_factory=dict)  # Institution -> ID
    transcripts_gpa: Dict[str, float] = Field(default_factory=dict)  # Institution -> GPA


class EducationGenerator:
    """Generator for comprehensive education and academic data"""
    
    def __init__(self, variability_engine: Optional[VariabilityEngine] = None):
        self.variability = variability_engine
        
        # Education level probabilities by age group
        self.education_by_age = {
            "18-24": {
                DegreeType.HIGH_SCHOOL: 0.40,
                DegreeType.CERTIFICATE: 0.15,
                DegreeType.ASSOCIATE: 0.25,
                DegreeType.BACHELOR: 0.18,
                DegreeType.MASTER: 0.02
            },
            "25-34": {
                DegreeType.HIGH_SCHOOL: 0.25,
                DegreeType.CERTIFICATE: 0.12,
                DegreeType.ASSOCIATE: 0.18,
                DegreeType.BACHELOR: 0.35,
                DegreeType.MASTER: 0.08,
                DegreeType.DOCTORATE: 0.02
            },
            "35-44": {
                DegreeType.HIGH_SCHOOL: 0.30,
                DegreeType.CERTIFICATE: 0.10,
                DegreeType.ASSOCIATE: 0.15,
                DegreeType.BACHELOR: 0.30,
                DegreeType.MASTER: 0.12,
                DegreeType.DOCTORATE: 0.03
            },
            "45+": {
                DegreeType.HIGH_SCHOOL: 0.35,
                DegreeType.CERTIFICATE: 0.08,
                DegreeType.ASSOCIATE: 0.12,
                DegreeType.BACHELOR: 0.28,
                DegreeType.MASTER: 0.14,
                DegreeType.DOCTORATE: 0.03
            }
        }
        
        # Major fields of study
        self.majors = {
            "Business": [
                "Business Administration", "Marketing", "Finance", "Accounting",
                "Management", "Economics", "International Business", "Supply Chain Management",
                "Human Resources", "Entrepreneurship", "Business Analytics"
            ],
            "Engineering": [
                "Computer Engineering", "Electrical Engineering", "Mechanical Engineering",
                "Civil Engineering", "Chemical Engineering", "Industrial Engineering",
                "Aerospace Engineering", "Biomedical Engineering", "Environmental Engineering",
                "Software Engineering", "Materials Engineering"
            ],
            "Computer Science": [
                "Computer Science", "Information Technology", "Computer Information Systems",
                "Cybersecurity", "Data Science", "Software Development", "Information Systems",
                "Computer Programming", "Web Development", "Network Administration"
            ],
            "Health Sciences": [
                "Nursing", "Biology", "Chemistry", "Pre-Med", "Public Health",
                "Health Administration", "Physical Therapy", "Occupational Therapy",
                "Pharmacy", "Medical Technology", "Nutrition", "Exercise Science"
            ],
            "Education": [
                "Elementary Education", "Secondary Education", "Special Education",
                "Educational Leadership", "Curriculum and Instruction", "School Counseling",
                "Early Childhood Education", "Physical Education", "Mathematics Education"
            ],
            "Liberal Arts": [
                "English", "History", "Psychology", "Sociology", "Political Science",
                "Philosophy", "Literature", "Communications", "Journalism", "Art History",
                "Anthropology", "Religious Studies", "Gender Studies"
            ],
            "Sciences": [
                "Biology", "Chemistry", "Physics", "Mathematics", "Statistics",
                "Environmental Science", "Geology", "Astronomy", "Biotechnology",
                "Neuroscience", "Marine Biology", "Genetics"
            ],
            "Arts": [
                "Fine Arts", "Graphic Design", "Music", "Theater", "Dance",
                "Creative Writing", "Film Studies", "Photography", "Interior Design",
                "Fashion Design", "Art Education", "Digital Media"
            ],
            "Social Work": [
                "Social Work", "Criminal Justice", "Human Services", "Community Development",
                "Public Administration", "Non-Profit Management", "Gerontology"
            ]
        }
        
        # Universities and colleges
        self.institutions = {
            "R1_Universities": [  # Top research universities
                ("Harvard University", "Private", "Cambridge", "MA", 1636, 1),
                ("Stanford University", "Private", "Stanford", "CA", 1885, 2),
                ("MIT", "Private", "Cambridge", "MA", 1861, 3),
                ("University of California, Berkeley", "Public", "Berkeley", "CA", 1868, 4),
                ("Yale University", "Private", "New Haven", "CT", 1701, 5),
                ("Princeton University", "Private", "Princeton", "NJ", 1746, 6),
                ("Columbia University", "Private", "New York", "NY", 1754, 7),
                ("University of Chicago", "Private", "Chicago", "IL", 1890, 8),
                ("University of Pennsylvania", "Private", "Philadelphia", "PA", 1740, 9),
                ("Cornell University", "Private", "Ithaca", "NY", 1865, 10)
            ],
            "State_Universities": [
                ("University of California, Los Angeles", "Public", "Los Angeles", "CA", 1919, 20),
                ("University of Michigan", "Public", "Ann Arbor", "MI", 1817, 25),
                ("University of Texas at Austin", "Public", "Austin", "TX", 1883, 30),
                ("University of Florida", "Public", "Gainesville", "FL", 1853, 35),
                ("Ohio State University", "Public", "Columbus", "OH", 1870, 40),
                ("Penn State University", "Public", "University Park", "PA", 1855, 45),
                ("University of Washington", "Public", "Seattle", "WA", 1861, 50),
                ("University of Wisconsin-Madison", "Public", "Madison", "WI", 1848, 55),
                ("University of Illinois at Urbana-Champaign", "Public", "Urbana", "IL", 1867, 60),
                ("University of Georgia", "Public", "Athens", "GA", 1785, 65)
            ],
            "Regional_Universities": [
                ("San Diego State University", "Public", "San Diego", "CA", 1897, 150),
                ("Arizona State University", "Public", "Tempe", "AZ", 1885, 180),
                ("Florida International University", "Public", "Miami", "FL", 1965, 200),
                ("George Mason University", "Public", "Fairfax", "VA", 1972, 220),
                ("Portland State University", "Public", "Portland", "OR", 1946, 250),
                ("University of Nevada, Las Vegas", "Public", "Las Vegas", "NV", 1957, 280),
                ("University of Alabama at Birmingham", "Public", "Birmingham", "AL", 1969, 300),
                ("University of South Florida", "Public", "Tampa", "FL", 1956, 320),
                ("California State University, Long Beach", "Public", "Long Beach", "CA", 1949, 350),
                ("Virginia Commonwealth University", "Public", "Richmond", "VA", 1838, 380)
            ],
            "Community_Colleges": [
                ("Valencia College", "Community College", "Orlando", "FL", 1967, None),
                ("Northern Virginia Community College", "Community College", "Annandale", "VA", 1965, None),
                ("Miami Dade College", "Community College", "Miami", "FL", 1959, None),
                ("Austin Community College", "Community College", "Austin", "TX", 1972, None),
                ("Houston Community College", "Community College", "Houston", "TX", 1971, None),
                ("Broward College", "Community College", "Fort Lauderdale", "FL", 1959, None),
                ("Santa Monica College", "Community College", "Santa Monica", "CA", 1929, None),
                ("Tarrant County College", "Community College", "Fort Worth", "TX", 1965, None),
                ("Phoenix College", "Community College", "Phoenix", "AZ", 1920, None),
                ("Montgomery College", "Community College", "Rockville", "MD", 1946, None)
            ],
            "Technical_Schools": [
                ("DeVry University", "Technical School", "Downers Grove", "IL", 1931, None),
                ("ITT Technical Institute", "Technical School", "Indianapolis", "IN", 1946, None),
                ("Full Sail University", "Technical School", "Winter Park", "FL", 1979, None),
                ("The Art Institute", "Technical School", "Pittsburgh", "PA", 1921, None),
                ("Lincoln Technical Institute", "Technical School", "Union", "NJ", 1946, None),
                ("Universal Technical Institute", "Technical School", "Phoenix", "AZ", 1965, None),
                ("Wyotech", "Technical School", "Laramie", "WY", 1966, None),
                ("Pittsburgh Institute of Aeronautics", "Technical School", "Pittsburgh", "PA", 1929, None),
                ("National College", "Technical School", "Salem", "VA", 1886, None),
                ("Fortis College", "Technical School", "Centerville", "OH", 1893, None)
            ]
        }
        
        # Professional certifications by field
        self.certifications = {
            "IT": [
                ("CompTIA A+", "CompTIA", 3, "https://www.comptia.org/"),
                ("Cisco CCNA", "Cisco", 3, "https://www.cisco.com/"),
                ("Microsoft Azure Fundamentals", "Microsoft", 2, "https://docs.microsoft.com/"),
                ("AWS Certified Solutions Architect", "Amazon", 3, "https://aws.amazon.com/"),
                ("Certified Information Systems Security Professional (CISSP)", "ISC2", 3, "https://www.isc2.org/"),
                ("Project Management Professional (PMP)", "PMI", 3, "https://www.pmi.org/"),
                ("Certified Ethical Hacker (CEH)", "EC-Council", 3, "https://www.eccouncil.org/"),
                ("Google Cloud Professional", "Google", 2, "https://cloud.google.com/")
            ],
            "Healthcare": [
                ("Basic Life Support (BLS)", "American Heart Association", 2, "https://www.heart.org/"),
                ("Advanced Cardiac Life Support (ACLS)", "American Heart Association", 2, "https://www.heart.org/"),
                ("Certified Medical Assistant (CMA)", "AAMA", 5, "https://www.aama-ntl.org/"),
                ("Registered Health Information Administrator (RHIA)", "AHIMA", None, "https://www.ahima.org/"),
                ("Certified Pharmacy Technician (CPhT)", "PTCB", 2, "https://www.ptcb.org/"),
                ("Licensed Practical Nurse (LPN)", "State Board", None, ""),
                ("Certified Nursing Assistant (CNA)", "State Board", 2, ""),
                ("Medical Laboratory Scientist (MLS)", "ASCP", None, "https://www.ascp.org/")
            ],
            "Finance": [
                ("Certified Public Accountant (CPA)", "AICPA", None, "https://www.aicpa.org/"),
                ("Chartered Financial Analyst (CFA)", "CFA Institute", None, "https://www.cfainstitute.org/"),
                ("Financial Risk Manager (FRM)", "GARP", None, "https://www.garp.org/"),
                ("Certified Financial Planner (CFP)", "CFP Board", None, "https://www.cfp.net/"),
                ("Series 7 - General Securities Representative", "FINRA", None, "https://www.finra.org/"),
                ("Series 66 - Investment Advisor Representative", "FINRA", None, "https://www.finra.org/"),
                ("Certified Management Accountant (CMA)", "IMA", None, "https://www.imanet.org/")
            ],
            "Education": [
                ("Teaching License", "State Department of Education", 5, ""),
                ("National Board Certification", "NBPTS", 10, "https://www.nbpts.org/"),
                ("Google for Education Certified Trainer", "Google", 2, "https://edu.google.com/"),
                ("Microsoft Certified Educator", "Microsoft", 2, "https://docs.microsoft.com/"),
                ("Substitute Teaching Certificate", "State Department", 3, "")
            ],
            "General": [
                ("First Aid/CPR", "Red Cross", 2, "https://www.redcross.org/"),
                ("Food Safety Manager", "ServSafe", 5, "https://www.servsafe.com/"),
                ("OSHA 10-Hour", "OSHA", None, "https://www.osha.gov/"),
                ("Real Estate License", "State Commission", 2, ""),
                ("Notary Public", "State Government", 4, "")
            ]
        }
        
        # Honors and academic achievements
        self.honors = [
            "Summa Cum Laude", "Magna Cum Laude", "Cum Laude", "Dean's List",
            "Phi Beta Kappa", "Honor Society", "President's List", "Academic Excellence Award",
            "Valedictorian", "Salutatorian", "National Merit Scholar", "Outstanding Student Award"
        ]
        
        # Extracurricular activities
        self.extracurricular_activities = {
            "Sports": [
                "Football", "Basketball", "Soccer", "Tennis", "Swimming", "Track and Field",
                "Baseball", "Softball", "Volleyball", "Cross Country", "Wrestling", "Golf",
                "Lacrosse", "Field Hockey", "Gymnastics", "Rowing"
            ],
            "Academic": [
                "Debate Team", "Model UN", "Academic Decathlon", "Math Team", "Science Olympiad",
                "National Honor Society", "Robotics Club", "Quiz Bowl", "Mock Trial", "Chess Club"
            ],
            "Arts": [
                "Drama Club", "Music Band", "Orchestra", "Choir", "Art Club", "Photography Club",
                "Creative Writing", "Film Club", "Dance Team", "Marching Band"
            ],
            "Service": [
                "Key Club", "Interact Club", "National Honor Society", "Student Government",
                "Peer Tutoring", "Community Service Club", "Environmental Club", "Red Cross Club"
            ],
            "Special Interest": [
                "Computer Club", "Gaming Club", "Anime Club", "Book Club", "Language Club",
                "Cultural Club", "Religious Group", "Political Club", "Entrepreneurship Club"
            ]
        }
        
        # Student loan providers
        self.loan_providers = {
            "Federal": ["Federal Direct Loans", "Federal PLUS Loans", "Federal Perkins Loans"],
            "Private": ["Sallie Mae", "Wells Fargo", "Discover Student Loans", "College Ave",
                       "Citizens Bank", "SoFi", "CommonBond", "Earnest", "LendKey", "MPOWER"]
        }
    
    def generate_institution(self, institution_type: str) -> Institution:
        """Generate a realistic educational institution"""
        institutions = self.institutions.get(institution_type, self.institutions["Regional_Universities"])
        name, inst_type, city, state, established, ranking = random.choice(institutions)
        
        # Generate website
        domain = name.lower().replace(" ", "").replace(",", "").replace("university", "").replace("college", "")
        if len(domain) > 15:
            domain = domain[:15]
        website = f"https://www.{domain}.edu"
        
        # Accreditation
        accreditations = {
            "R1_Universities": "Regional Accreditation + Professional Accreditations",
            "State_Universities": "Regional Accreditation",
            "Regional_Universities": "Regional Accreditation",
            "Community_Colleges": "Regional Accreditation",
            "Technical_Schools": "National Accreditation"
        }
        
        return Institution(
            name=name,
            type=inst_type,
            location_city=city,
            location_state=state,
            established_year=established,
            accreditation=accreditations.get(institution_type, "Regional Accreditation"),
            ranking=ranking,
            website=website
        )
    
    def generate_student_id(self, institution_name: str) -> str:
        """Generate a student ID number"""
        # Different formats for different institution types
        id_formats = [
            "S{:08d}",      # S12345678
            "{:09d}",       # 123456789
            "ID{:07d}",     # ID1234567
            "{:03d}-{:03d}-{:03d}"  # 123-456-789
        ]
        
        format_choice = random.choice(id_formats)
        if "{:03d}-{:03d}-{:03d}" in format_choice:
            return format_choice.format(
                random.randint(100, 999),
                random.randint(100, 999),
                random.randint(100, 999)
            )
        else:
            return format_choice.format(random.randint(10000000, 99999999))
    
    def determine_education_level(self, age: int, income: float) -> DegreeType:
        """Determine highest education level based on age and income"""
        # Get age group
        if age < 25:
            age_group = "18-24"
        elif age < 35:
            age_group = "25-34"
        elif age < 45:
            age_group = "35-44"
        else:
            age_group = "45+"
        
        # Base probabilities
        probabilities = self.education_by_age[age_group]
        
        # Adjust based on income
        if income > 100000:
            # Higher income correlates with higher education
            if DegreeType.MASTER in probabilities:
                probabilities[DegreeType.MASTER] *= 2
            if DegreeType.DOCTORATE in probabilities:
                probabilities[DegreeType.DOCTORATE] *= 3
            if DegreeType.BACHELOR in probabilities:
                probabilities[DegreeType.BACHELOR] *= 1.5
        elif income < 30000:
            # Lower income correlates with lower education
            if DegreeType.HIGH_SCHOOL in probabilities:
                probabilities[DegreeType.HIGH_SCHOOL] *= 1.5
            if DegreeType.CERTIFICATE in probabilities:
                probabilities[DegreeType.CERTIFICATE] *= 1.3
        
        # Normalize probabilities
        total = sum(probabilities.values())
        normalized_probs = {k: v/total for k, v in probabilities.items()}
        
        # Select education level
        levels = list(normalized_probs.keys())
        weights = list(normalized_probs.values())
        return random.choices(levels, weights=weights)[0]
    
    def generate_major(self, degree_type: DegreeType, previous_major: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """Generate major and optional minor"""
        # Select field of study
        if degree_type == DegreeType.CERTIFICATE:
            # Technical certificates - use keys that exist in self.majors
            tech_fields = ["Computer Science", "Health Sciences", "Business"]
            field_choice = random.choice(tech_fields)
        elif degree_type in [DegreeType.MASTER, DegreeType.DOCTORATE]:
            # Graduate degrees often continue from undergrad
            if previous_major:
                # 70% chance to continue in same field
                if random.random() < 0.7:
                    for field, majors in self.majors.items():
                        if previous_major in majors:
                            field_choice = field
                            break
                    else:
                        field_choice = random.choice(list(self.majors.keys()))
                else:
                    field_choice = random.choice(list(self.majors.keys()))
            else:
                field_choice = random.choice(list(self.majors.keys()))
        else:
            field_choice = random.choice(list(self.majors.keys()))
        
        major = random.choice(self.majors[field_choice])
        
        # Minor (only for bachelor's degrees, 30% chance)
        minor = None
        if degree_type == DegreeType.BACHELOR and random.random() < 0.3:
            # Different field for minor
            other_fields = [f for f in self.majors.keys() if f != field_choice]
            if other_fields:
                minor_field = random.choice(other_fields)
                minor = random.choice(self.majors[minor_field])
        
        return major, minor
    
    def generate_gpa(self, degree_type: DegreeType, honors: Optional[str]) -> float:
        """Generate realistic GPA based on degree type and honors"""
        if honors:
            if "Summa Cum Laude" in honors:
                gpa = random.uniform(3.85, 4.0)
            elif "Magna Cum Laude" in honors:
                gpa = random.uniform(3.7, 3.89)
            elif "Cum Laude" in honors:
                gpa = random.uniform(3.5, 3.74)
            elif "Dean's List" in honors:
                gpa = random.uniform(3.4, 3.8)
            else:
                gpa = random.uniform(3.2, 3.7)
        else:
            # Normal distribution around 3.0
            if degree_type == DegreeType.DOCTORATE:
                gpa = random.uniform(3.4, 4.0)  # PhD students typically high achievers
            elif degree_type == DegreeType.MASTER:
                gpa = random.uniform(3.2, 3.9)
            elif degree_type == DegreeType.BACHELOR:
                gpa = random.uniform(2.5, 3.8)
            else:
                gpa = random.uniform(2.0, 3.5)
        
        return round(gpa, 2)
    
    def generate_degree(self, degree_type: DegreeType, age: int, 
                       previous_degree: Optional[Degree] = None) -> Degree:
        """Generate a degree with realistic details"""
        # Determine institution type based on degree type
        if degree_type == DegreeType.DOCTORATE:
            inst_type = random.choice(["R1_Universities", "State_Universities"])
        elif degree_type == DegreeType.MASTER:
            inst_type = random.choices(
                ["R1_Universities", "State_Universities", "Regional_Universities"],
                weights=[0.4, 0.4, 0.2]
            )[0]
        elif degree_type == DegreeType.BACHELOR:
            inst_type = random.choices(
                ["R1_Universities", "State_Universities", "Regional_Universities"],
                weights=[0.2, 0.4, 0.4]
            )[0]
        elif degree_type == DegreeType.ASSOCIATE:
            inst_type = "Community_Colleges"
        else:  # Certificate
            inst_type = "Technical_Schools"
        
        institution = self.generate_institution(inst_type)
        
        # Generate major/minor
        previous_major = previous_degree.major if previous_degree else None
        major, minor = self.generate_major(degree_type, previous_major)
        
        # Generate dates
        if degree_type == DegreeType.HIGH_SCHOOL:
            # High school graduation around age 18
            graduation_age = 18
            start_age = 14
        elif degree_type == DegreeType.ASSOCIATE:
            start_age = random.randint(18, 25)
            graduation_age = start_age + 2
        elif degree_type == DegreeType.BACHELOR:
            start_age = random.randint(18, 30)
            graduation_age = start_age + 4
        elif degree_type == DegreeType.MASTER:
            start_age = random.randint(22, 40)
            graduation_age = start_age + 2
        elif degree_type == DegreeType.DOCTORATE:
            start_age = random.randint(24, 45)
            graduation_age = start_age + random.randint(4, 7)
        else:  # Certificate
            start_age = random.randint(18, 50)
            graduation_age = start_age + 1
        
        # Calculate actual dates
        years_since_graduation = age - graduation_age
        if years_since_graduation < 0:
            # Still in school
            years_since_start = age - start_age
            start_date = date.today() - timedelta(days=years_since_start * 365 + random.randint(0, 364))
            graduation_date = None
            is_completed = False
        else:
            start_date = date.today() - timedelta(days=(years_since_graduation + (graduation_age - start_age)) * 365 + random.randint(0, 364))
            graduation_date = date.today() - timedelta(days=years_since_graduation * 365 + random.randint(0, 364))
            is_completed = True
        
        # Generate honors (20% chance)
        honors = None
        if is_completed and random.random() < 0.2:
            honors = random.choice(self.honors)
        
        # Generate GPA
        gpa = None
        if degree_type not in [DegreeType.HIGH_SCHOOL, DegreeType.GED]:
            gpa = self.generate_gpa(degree_type, honors)
        
        # Thesis for graduate degrees
        thesis_title = None
        advisor = None
        if degree_type in [DegreeType.MASTER, DegreeType.DOCTORATE] and is_completed:
            if random.random() < 0.8:  # 80% have thesis
                thesis_keywords = [
                    "Analysis", "Study", "Investigation", "Examination", "Research",
                    "Development", "Implementation", "Evaluation", "Assessment", "Design"
                ]
                thesis_title = f"An {random.choice(thesis_keywords)} of {major} in Modern Context"
                
                # Generate advisor name
                first_names = ["Dr. John", "Dr. Sarah", "Dr. Michael", "Dr. Jennifer", "Dr. David", "Dr. Lisa"]
                last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
                advisor = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Specialization for advanced degrees
        specialization = None
        if degree_type in [DegreeType.MASTER, DegreeType.DOCTORATE]:
            specializations = {
                "Computer Science": ["Machine Learning", "Cybersecurity", "Software Engineering", "Data Science"],
                "Business": ["Finance", "Marketing", "Operations", "Strategy"],
                "Engineering": ["Design", "Systems", "Materials", "Process"],
                "Health Sciences": ["Clinical Practice", "Research", "Administration", "Public Health"]
            }
            # Find field for the major
            for field, majors in self.majors.items():
                if major in majors and field in specializations:
                    if random.random() < 0.6:  # 60% have specialization
                        specialization = random.choice(specializations[field])
                    break
        
        return Degree(
            degree_type=degree_type,
            major=major,
            minor=minor,
            specialization=specialization,
            institution=institution,
            start_date=start_date,
            graduation_date=graduation_date,
            gpa=gpa,
            honors=honors,
            thesis_title=thesis_title,
            advisor=advisor,
            is_completed=is_completed
        )
    
    def generate_certifications(self, degrees: List[Degree], age: int) -> List[Certification]:
        """Generate professional certifications based on education and field"""
        certifications = []
        
        # Determine relevant certification fields
        relevant_fields = set()
        for degree in degrees:
            major = degree.major.lower()
            if any(keyword in major for keyword in ["computer", "information", "technology", "software"]):
                relevant_fields.add("IT")
            elif any(keyword in major for keyword in ["nursing", "medical", "health", "biology", "chemistry"]):
                relevant_fields.add("Healthcare")
            elif any(keyword in major for keyword in ["business", "finance", "accounting", "economics"]):
                relevant_fields.add("Finance")
            elif any(keyword in major for keyword in ["education", "teaching"]):
                relevant_fields.add("Education")
        
        # Always consider general certifications
        relevant_fields.add("General")
        
        # Generate certifications for each relevant field
        for field in relevant_fields:
            field_certs = self.certifications.get(field, [])
            num_certs = random.choices([0, 1, 2, 3], weights=[0.4, 0.4, 0.15, 0.05])[0]
            
            if num_certs > 0:
                selected_certs = random.sample(field_certs, min(num_certs, len(field_certs)))
                
                for cert_name, issuer, validity_years, url in selected_certs:
                    # Generate issue date - only for people old enough for certifications
                    if age < 18:
                        continue  # Skip certifications for minors
                    years_ago = random.randint(0, min(10, age - 18))
                    issue_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 364))
                    
                    # Calculate expiry date
                    expiry_date = None
                    is_active = True
                    if validity_years:
                        expiry_date = issue_date + timedelta(days=validity_years * 365)
                        is_active = expiry_date > date.today()
                    
                    # Generate certification ID
                    cert_id = f"{issuer[:3].upper()}{random.randint(100000, 999999)}"
                    
                    certification = Certification(
                        certification_name=cert_name,
                        issuing_organization=issuer,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        certification_id=cert_id,
                        verification_url=url if url else None,
                        is_active=is_active
                    )
                    certifications.append(certification)
        
        return certifications
    
    def generate_student_loans(self, degrees: List[Degree], income: float) -> List[StudentLoan]:
        """Generate student loans based on education level"""
        loans = []
        
        # Only generate loans for degrees that typically require them
        loan_degrees = [d for d in degrees if d.degree_type in [
            DegreeType.BACHELOR, DegreeType.MASTER, DegreeType.DOCTORATE, DegreeType.PROFESSIONAL
        ]]
        
        if not loan_degrees:
            return loans
        
        # Calculate total education cost
        total_cost = 0
        for degree in loan_degrees:
            if degree.institution.type == "Private":
                annual_cost = random.randint(40000, 60000)
            elif degree.institution.type == "Public":
                annual_cost = random.randint(15000, 25000)
            else:
                annual_cost = random.randint(8000, 15000)
            
            years = 4 if degree.degree_type == DegreeType.BACHELOR else 2
            if degree.degree_type == DegreeType.DOCTORATE:
                years = random.randint(4, 6)
            
            degree_cost = annual_cost * years
            total_cost += degree_cost
        
        # Determine loan coverage (typically 60-80% of costs)
        loan_coverage = random.uniform(0.6, 0.8)
        total_loan_amount = total_cost * loan_coverage
        
        # Generate different types of loans
        if total_loan_amount > 0:
            # Federal loans (usually the primary source)
            federal_amount = min(total_loan_amount * 0.7, 57500)  # Federal loan limits
            
            if federal_amount > 0:
                # Split into subsidized and unsubsidized
                subsidized_amount = min(federal_amount * 0.6, 23000)
                unsubsidized_amount = federal_amount - subsidized_amount
                
                if subsidized_amount > 0:
                    loans.append(self.generate_single_loan(
                        "Federal Subsidized", subsidized_amount, 
                        loan_degrees[0].start_date, income
                    ))
                
                if unsubsidized_amount > 0:
                    loans.append(self.generate_single_loan(
                        "Federal Unsubsidized", unsubsidized_amount,
                        loan_degrees[0].start_date, income
                    ))
            
            # Private loans for remaining amount
            remaining_amount = total_loan_amount - federal_amount
            if remaining_amount > 5000:  # Only if significant amount
                private_lender = random.choice(self.loan_providers["Private"])
                loans.append(self.generate_single_loan(
                    "Private", remaining_amount, loan_degrees[0].start_date,
                    income, private_lender
                ))
            
            # Graduate PLUS loans for advanced degrees
            grad_degrees = [d for d in loan_degrees if d.degree_type in [DegreeType.MASTER, DegreeType.DOCTORATE]]
            if grad_degrees and random.random() < 0.4:
                plus_amount = random.uniform(10000, 30000)
                loans.append(self.generate_single_loan(
                    "Graduate PLUS", plus_amount, grad_degrees[0].start_date, income
                ))
        
        return loans
    
    def generate_single_loan(self, loan_type: str, amount: float, start_date: date, 
                           income: float, lender: str = None) -> StudentLoan:
        """Generate a single student loan"""
        if not lender:
            if "Federal" in loan_type:
                lender = "Federal Direct Loans"
            else:
                lender = random.choice(self.loan_providers["Private"])
        
        # Interest rates based on loan type and date
        if "Federal" in loan_type:
            if "Subsidized" in loan_type:
                interest_rate = random.uniform(3.73, 5.50)  # Historical range
            elif "PLUS" in loan_type:
                interest_rate = random.uniform(6.28, 7.60)
            else:
                interest_rate = random.uniform(3.73, 6.60)
        else:  # Private
            interest_rate = random.uniform(4.25, 12.99)
        
        # Calculate current balance (with interest accrual)
        years_since_start = (date.today() - start_date).days / 365
        # Simple interest calculation for demo purposes
        current_balance = amount * (1 + (interest_rate / 100) * years_since_start)
        
        # Determine loan status
        if income > 80000 and random.random() < 0.3:
            # Higher income, more likely to be paying or paid off
            if random.random() < 0.2:
                status = "Paid Off"
                current_balance = 0
                monthly_payment = 0
            else:
                status = "Active"
                monthly_payment = current_balance * 0.01  # Rough 1% monthly payment
        elif income < 30000:
            # Lower income, more likely to be deferred
            status = random.choice(["Active", "Deferred", "Forbearance"])
            if status == "Active":
                monthly_payment = current_balance * 0.005  # Lower payment
            else:
                monthly_payment = 0
        else:
            status = "Active"
            monthly_payment = current_balance * 0.008  # Standard payment
        
        return StudentLoan(
            loan_type=loan_type,
            lender=lender,
            principal_amount=round(amount, 2),
            current_balance=round(max(0, current_balance), 2),
            interest_rate=round(interest_rate, 2),
            monthly_payment=round(monthly_payment, 2),
            start_date=start_date,
            status=status
        )
    
    def generate_education_profile(self, age: int, income: float) -> EducationProfile:
        """Generate complete education profile"""
        degrees = []
        
        # Determine highest education level
        highest_level = self.determine_education_level(age, income)
        
        # Generate education progression
        if highest_level == DegreeType.HIGH_SCHOOL:
            degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
        
        elif highest_level == DegreeType.CERTIFICATE:
            if random.random() < 0.8:  # 80% have high school first
                degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
            degrees.append(self.generate_degree(DegreeType.CERTIFICATE, age))
        
        elif highest_level == DegreeType.ASSOCIATE:
            if random.random() < 0.9:  # 90% have high school first
                degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
            degrees.append(self.generate_degree(DegreeType.ASSOCIATE, age))
        
        elif highest_level == DegreeType.BACHELOR:
            if random.random() < 0.95:  # 95% have high school first
                degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
            # Some have associate degree first
            if random.random() < 0.3:
                degrees.append(self.generate_degree(DegreeType.ASSOCIATE, age))
            degrees.append(self.generate_degree(DegreeType.BACHELOR, age))
        
        elif highest_level == DegreeType.MASTER:
            if random.random() < 0.98:
                degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
            degrees.append(self.generate_degree(DegreeType.BACHELOR, age))
            degrees.append(self.generate_degree(DegreeType.MASTER, age, degrees[-1]))
        
        elif highest_level == DegreeType.DOCTORATE:
            degrees.append(self.generate_degree(DegreeType.HIGH_SCHOOL, age))
            degrees.append(self.generate_degree(DegreeType.BACHELOR, age))
            if random.random() < 0.7:  # 70% get Master's first
                degrees.append(self.generate_degree(DegreeType.MASTER, age, degrees[-1]))
            degrees.append(self.generate_degree(DegreeType.DOCTORATE, age, degrees[-1]))
        
        # Generate certifications
        certifications = self.generate_certifications(degrees, age)
        
        # Generate student loans
        student_loans = self.generate_student_loans(degrees, income)
        
        # Generate student IDs
        student_ids = {}
        transcripts_gpa = {}
        for degree in degrees:
            if degree.institution.name not in student_ids:
                student_ids[degree.institution.name] = self.generate_student_id(degree.institution.name)
            if degree.gpa:
                transcripts_gpa[degree.institution.name] = degree.gpa
        
        return EducationProfile(
            highest_education_level=highest_level,
            degrees=degrees,
            certifications=certifications,
            courses=[],  # Could be expanded to generate individual courses
            scholarships=[],  # Could be expanded to generate scholarships
            extracurricular_activities=[],  # Could be expanded
            academic_achievements=[],  # Could be expanded
            student_loans=student_loans,
            student_id_numbers=student_ids,
            transcripts_gpa=transcripts_gpa
        )