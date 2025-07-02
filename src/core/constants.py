from typing import List, Dict, Tuple
import string

# Name data
COMMON_FIRST_NAMES = {
    "M": ["James", "Robert", "John", "Michael", "William", "David", "Richard", "Joseph", 
          "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
          "Donald", "Kenneth", "Steven", "Edward", "Paul", "Joshua", "Kevin", "Brian",
          "George", "Timothy", "Ronald", "Andrew", "Eric", "Jeffrey", "Ryan"],
    "F": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
          "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
          "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda",
          "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura"]
}

ETHNIC_FIRST_NAMES = {
    "hispanic": {
        "M": ["Miguel", "Carlos", "Juan", "Luis", "Jose", "Antonio", "Francisco", "Manuel",
              "Pedro", "Alejandro", "Ricardo", "Fernando", "Diego", "Roberto", "Eduardo"],
        "F": ["Maria", "Carmen", "Ana", "Isabel", "Sofia", "Lucia", "Elena", "Rosa",
              "Patricia", "Laura", "Claudia", "Andrea", "Gabriela", "Valentina", "Camila"]
    },
    "asian": {
        "M": ["Wei", "Jin", "Chen", "Li", "Yang", "Zhang", "Wang", "Hiroshi", "Takeshi",
              "Kenji", "Raj", "Arjun", "Vikram", "Amit", "Ravi", "Muhammad", "Ahmed"],
        "F": ["Mei", "Ling", "Xiu", "Yuki", "Sakura", "Priya", "Anjali", "Deepa",
              "Fatima", "Aisha", "Min", "Hye", "Yeon", "Ji", "Soo"]
    },
    "african": {
        "M": ["Kwame", "Jamal", "Malik", "Darius", "Andre", "Tyrone", "Marcus",
              "DeShawn", "Terrell", "Antoine", "Omar", "Kareem", "Tariq"],
        "F": ["Aisha", "Nia", "Keisha", "Latoya", "Shaniqua", "Jasmine", "Aaliyah",
              "Imani", "Zara", "Amara", "Khadija", "Fatou", "Amina"]
    }
}

COMMON_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster",
    "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman",
    "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero",
    "Jordan", "Patterson", "Alexander", "Hamilton", "Graham", "Reynolds", "Griffin",
    "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson", "Ellis",
    "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro", "Marshall",
    "Owens", "Harrison", "Fernandez", "McDonald", "Woods", "Washington", "Kennedy",
    "Wells", "Vargas", "Henry", "Freeman", "Webb", "Tucker", "Guzman", "Burns", "Crawford",
    "Olson", "Simpson", "Porter", "Hunter", "Gordon", "Mendez", "Silva", "Shaw", "Snyder",
    "Mason", "Dixon", "Munoz", "Hunt", "Hicks", "Holmes", "Palmer", "Wagner", "Black",
    "Robertson", "Boyd", "Rose", "Stone", "Salazar", "Fox", "Warren", "Mills", "Meyer",
    "Rice", "Schmidt", "Garza", "Daniels", "Ferguson", "Nichols", "Stephens", "Soto",
    "Weaver", "Ryan", "Gardner", "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins"
]

HYPHENATED_LAST_NAMES = [
    ("Smith", "Johnson"), ("Garcia", "Lopez"), ("Brown", "Davis"), ("Wilson", "Moore"),
    ("Martinez", "Rodriguez"), ("Anderson", "Thompson"), ("Taylor", "White"), 
    ("Thomas", "Harris"), ("Martin", "Jackson"), ("Lee", "Walker")
]

NAME_PREFIXES = ["Dr.", "Prof.", "Mr.", "Mrs.", "Ms.", "Miss", "Rev.", "Hon.", "Capt.", "Lt.", "Col.", "Gen.", "Sen.", "Rep."]
NAME_SUFFIXES = ["Jr.", "Sr.", "II", "III", "IV", "PhD", "MD", "JD", "CPA", "MBA", "RN", "DDS", "DVM", "Esq."]

# Address data
STREET_TYPES = ["Street", "St", "Avenue", "Ave", "Road", "Rd", "Drive", "Dr", "Lane", "Ln",
                "Boulevard", "Blvd", "Circle", "Cir", "Court", "Ct", "Place", "Pl", "Way",
                "Parkway", "Pkwy", "Highway", "Hwy", "Trail", "Trl", "Square", "Sq"]

STREET_NAMES = ["Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Jefferson",
                "Lincoln", "Park", "First", "Second", "Third", "Fourth", "Fifth", "Sixth",
                "Seventh", "Eighth", "Ninth", "Tenth", "Church", "Market", "High", "Center",
                "Union", "Spring", "Grove", "Ridge", "Lake", "Hill", "River", "Forest",
                "Sunset", "Meadow", "Valley", "Grand", "College", "School", "Prospect",
                "Broadway", "Franklin", "Jackson", "Adams", "Madison", "Liberty"]

APARTMENT_PREFIXES = ["Apt", "Suite", "Unit", "#", "Bldg"]

# Major US cities with state and common zip prefixes
CITY_STATE_ZIP_DATA = [
    ("New York", "NY", ["100", "101", "102", "103", "104", "111", "112", "113", "114"]),
    ("Los Angeles", "CA", ["900", "901", "902", "903", "904", "905", "906", "907", "908"]),
    ("Chicago", "IL", ["606", "607", "608"]),
    ("Houston", "TX", ["770", "771", "772", "773", "774", "775"]),
    ("Phoenix", "AZ", ["850", "851", "852", "853"]),
    ("Philadelphia", "PA", ["190", "191", "192", "193", "194"]),
    ("San Antonio", "TX", ["782", "783", "784", "785", "786", "787", "788"]),
    ("San Diego", "CA", ["919", "920", "921"]),
    ("Dallas", "TX", ["750", "751", "752", "753"]),
    ("San Jose", "CA", ["950", "951", "952", "953"]),
    ("Austin", "TX", ["786", "787", "788", "789"]),
    ("Jacksonville", "FL", ["320", "321", "322"]),
    ("Fort Worth", "TX", ["760", "761", "762"]),
    ("Columbus", "OH", ["430", "431", "432", "433", "434"]),
    ("San Francisco", "CA", ["940", "941", "942", "943", "944"]),
    ("Charlotte", "NC", ["280", "281", "282", "283", "284"]),
    ("Indianapolis", "IN", ["460", "461", "462", "463", "464"]),
    ("Seattle", "WA", ["980", "981", "982", "983", "984"]),
    ("Denver", "CO", ["800", "801", "802", "803", "804"]),
    ("Washington", "DC", ["200", "201", "202", "203", "204"]),
    ("Boston", "MA", ["021", "022", "023", "024", "025"]),
    ("Nashville", "TN", ["370", "371", "372", "373", "374"]),
    ("Baltimore", "MD", ["210", "211", "212", "213", "214"]),
    ("Oklahoma City", "OK", ["730", "731", "732", "733", "734"]),
    ("Louisville", "KY", ["400", "401", "402", "403", "404"]),
    ("Portland", "OR", ["970", "971", "972", "973", "974"]),
    ("Las Vegas", "NV", ["890", "891", "892", "893", "894"]),
    ("Milwaukee", "WI", ["530", "531", "532", "533", "534"]),
    ("Albuquerque", "NM", ["870", "871", "872", "873", "874"]),
    ("Tucson", "AZ", ["856", "857"]),
    ("Fresno", "CA", ["936", "937", "938"]),
    ("Sacramento", "CA", ["942", "956", "957", "958", "959"]),
    ("Mesa", "AZ", ["852", "853"]),
    ("Kansas City", "MO", ["640", "641", "642", "643", "644"]),
    ("Atlanta", "GA", ["300", "301", "302", "303", "304"]),
    ("Miami", "FL", ["330", "331", "332", "333", "334"]),
    ("Tampa", "FL", ["335", "336", "337"]),
    ("Orlando", "FL", ["327", "328", "329"]),
    ("Minneapolis", "MN", ["553", "554", "555", "556", "557"]),
    ("Cleveland", "OH", ["440", "441", "442", "443", "444"]),
    ("Detroit", "MI", ["480", "481", "482", "483", "484"]),
    ("St. Louis", "MO", ["630", "631", "632", "633", "634"]),
    ("Pittsburgh", "PA", ["150", "151", "152", "153", "154"]),
    ("Cincinnati", "OH", ["450", "451", "452", "453", "454"]),
    ("Salt Lake City", "UT", ["840", "841", "842", "843", "844"]),
    ("Raleigh", "NC", ["275", "276", "277", "278", "279"]),
    ("Memphis", "TN", ["380", "381", "382", "383", "384"]),
    ("Richmond", "VA", ["230", "231", "232", "233", "234"]),
    ("New Orleans", "LA", ["700", "701", "702", "703", "704"])
]

# Phone and Email data
AREA_CODES_BY_STATE = {
    "NY": ["212", "315", "347", "516", "518", "585", "607", "631", "646", "716", "718", "845", "914", "917", "929"],
    "CA": ["209", "213", "310", "323", "408", "415", "424", "442", "510", "530", "559", "562", "619", "626", "628", "650", "657", "661", "669", "707", "714", "747", "760", "805", "818", "831", "858", "909", "916", "925", "949", "951"],
    "TX": ["210", "214", "254", "281", "325", "346", "361", "409", "430", "432", "469", "512", "682", "713", "726", "737", "806", "817", "830", "832", "903", "915", "936", "940", "956", "972", "979"],
    "FL": ["239", "305", "321", "352", "386", "407", "561", "727", "754", "772", "786", "813", "850", "863", "904", "941", "954"],
    "IL": ["217", "224", "309", "312", "331", "618", "630", "708", "773", "779", "815", "847", "872"],
    "PA": ["215", "223", "267", "272", "412", "445", "484", "570", "610", "717", "724", "814", "878"],
    "OH": ["216", "220", "234", "330", "380", "419", "440", "513", "567", "614", "740", "937"],
    "GA": ["229", "404", "470", "478", "678", "706", "762", "770", "912"],
    "NC": ["252", "336", "704", "743", "828", "910", "919", "980", "984"],
    "MI": ["231", "248", "269", "313", "517", "586", "616", "734", "810", "906", "947", "989"]
}

EMAIL_DOMAINS = {
    "personal": [
        ("gmail.com", 0.35),
        ("yahoo.com", 0.15),
        ("hotmail.com", 0.10),
        ("outlook.com", 0.10),
        ("aol.com", 0.05),
        ("icloud.com", 0.05),
        ("mail.com", 0.03),
        ("protonmail.com", 0.02),
        ("ymail.com", 0.02),
        ("live.com", 0.02),
        ("msn.com", 0.02),
        ("comcast.net", 0.02),
        ("verizon.net", 0.02),
        ("att.net", 0.02),
        ("sbcglobal.net", 0.01),
        ("cox.net", 0.01),
        ("charter.net", 0.01)
    ],
    "work": [
        ("company.com", 0.20),
        ("corporation.com", 0.15),
        ("business.com", 0.10),
        ("enterprise.com", 0.10),
        ("group.com", 0.08),
        ("solutions.com", 0.07),
        ("services.com", 0.07),
        ("consulting.com", 0.05),
        ("tech.com", 0.05),
        ("global.com", 0.05),
        ("partners.com", 0.03),
        ("associates.com", 0.03),
        ("industries.com", 0.02)
    ]
}

# Employment data
JOB_TITLES_BY_LEVEL = {
    "entry": [
        "Junior Developer", "Assistant Manager", "Analyst", "Coordinator", "Associate",
        "Specialist", "Representative", "Clerk", "Technician", "Assistant"
    ],
    "mid": [
        "Developer", "Manager", "Senior Analyst", "Supervisor", "Team Lead",
        "Project Manager", "Account Manager", "Operations Manager", "Product Manager"
    ],
    "senior": [
        "Senior Developer", "Senior Manager", "Director", "Principal Engineer",
        "Senior Director", "Vice President", "Senior Vice President", "Partner"
    ],
    "executive": [
        "Chief Executive Officer", "Chief Financial Officer", "Chief Technology Officer",
        "Chief Operating Officer", "President", "Executive Vice President"
    ]
}

INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Education", "Retail", "Manufacturing",
    "Construction", "Real Estate", "Hospitality", "Transportation", "Energy",
    "Telecommunications", "Media", "Entertainment", "Government", "Non-Profit",
    "Consulting", "Legal", "Insurance", "Agriculture"
]

COMPANY_NAMES = [
    "Tech Solutions Inc", "Global Enterprises", "Innovative Systems Corp", "Digital Dynamics",
    "Premier Services LLC", "Advanced Technologies", "Strategic Partners", "Unified Solutions",
    "NextGen Industries", "Pinnacle Group", "Apex Corporation", "Synergy Systems",
    "Quantum Innovations", "Vertex Holdings", "Meridian Enterprises", "Catalyst Corp",
    "Nexus Technologies", "Paradigm Solutions", "Zenith Industries", "Vanguard Group"
]

# Financial data distributions
CREDIT_SCORE_DISTRIBUTION = [
    (300, 579, 0.16),   # Poor
    (580, 669, 0.17),   # Fair
    (670, 739, 0.21),   # Good
    (740, 799, 0.25),   # Very Good
    (800, 850, 0.21)    # Excellent
]

INCOME_BY_AGE_RANGE = {
    (18, 24): (15000, 45000),
    (25, 34): (30000, 75000),
    (35, 44): (40000, 100000),
    (45, 54): (45000, 120000),
    (55, 64): (40000, 110000),
    (65, 99): (25000, 80000)
}

# Data quality patterns
TYPO_PATTERNS = [
    ("ie", "ei"), ("ou", "uo"), ("th", "ht"), ("er", "re"), ("an", "na"),
    ("in", "ni"), ("ed", "de"), ("on", "no"), ("at", "ta"), ("or", "ro")
]

COMMON_MISSPELLINGS = {
    "Street": ["Stret", "Streat", "Sreet"],
    "Avenue": ["Avenu", "Aveneu", "Avnue"],
    "Drive": ["Drv", "Driv", "Dirve"],
    "Boulevard": ["Boulvard", "Blvrd", "Boulevrd"],
    "Apartment": ["Apt", "Aptment", "Apparment"],
    "Suite": ["Ste", "Suit", "Suiet"]
}