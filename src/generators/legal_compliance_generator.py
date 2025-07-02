"""
Legal and Compliance Records Generator - Creates comprehensive legal history and compliance data
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import uuid

class LegalRecordType(Enum):
    TRAFFIC_VIOLATION = "traffic_violation"
    CIVIL_LAWSUIT = "civil_lawsuit"
    CRIMINAL_CHARGE = "criminal_charge"
    BANKRUPTCY = "bankruptcy"
    DIVORCE = "divorce"
    PROPERTY_DEED = "property_deed"
    BUSINESS_LICENSE = "business_license"
    PROFESSIONAL_LICENSE = "professional_license"
    PATENT = "patent"
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    COURT_JUDGMENT = "court_judgment"
    RESTRAINING_ORDER = "restraining_order"
    PROBATE = "probate"
    TAX_LIEN = "tax_lien"

class ComplianceArea(Enum):
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    EMPLOYMENT = "employment"
    ENVIRONMENTAL = "environmental"
    DATA_PRIVACY = "data_privacy"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    TAX = "tax"
    IMMIGRATION = "immigration"
    INTELLECTUAL_PROPERTY = "intellectual_property"

class RecordStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    PENDING = "pending"
    DISMISSED = "dismissed"
    SEALED = "sealed"
    EXPUNGED = "expunged"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LegalRecord(BaseModel):
    record_id: str
    record_type: LegalRecordType
    date_filed: datetime
    jurisdiction: str  # court, agency, or authority
    case_number: str
    title: str
    description: str
    status: RecordStatus
    severity: SeverityLevel
    parties_involved: List[str]
    legal_representation: Optional[str]
    outcome: Optional[str]
    financial_impact: Optional[float]
    resolved_date: Optional[datetime]
    appeal_filed: bool
    public_record: bool

class ComplianceRecord(BaseModel):
    compliance_id: str
    area: ComplianceArea
    regulation_name: str
    compliance_date: datetime
    status: str  # compliant, non_compliant, pending_review
    audit_date: Optional[datetime]
    audit_result: Optional[str]
    remediation_required: bool
    remediation_deadline: Optional[datetime]
    responsible_party: str
    documentation_path: Optional[str]
    next_review_date: Optional[datetime]

class IntellectualProperty(BaseModel):
    ip_id: str
    type: str  # patent, trademark, copyright, trade_secret
    title: str
    description: str
    registration_number: Optional[str]
    filing_date: datetime
    grant_date: Optional[datetime]
    expiration_date: Optional[datetime]
    status: str  # pending, granted, expired, abandoned
    inventors_authors: List[str]
    assignee: str
    categories: List[str]
    estimated_value: Optional[float]

class ProfessionalLicense(BaseModel):
    license_id: str
    license_type: str
    profession: str
    license_number: str
    issuing_authority: str
    issue_date: datetime
    expiration_date: datetime
    status: str  # active, expired, suspended, revoked
    continuing_education_required: bool
    continuing_education_hours: Optional[int]
    disciplinary_actions: List[Dict[str, Any]]
    renewal_history: List[Dict[str, datetime]]

class BusinessEntity(BaseModel):
    entity_id: str
    business_name: str
    entity_type: str  # LLC, Corporation, Partnership, etc.
    registration_number: str
    state_of_incorporation: str
    incorporation_date: datetime
    registered_agent: str
    business_address: str
    status: str  # active, dissolved, suspended
    annual_report_filed: bool
    tax_id: Optional[str]
    officers: List[Dict[str, Any]]
    business_licenses: List[str]

class LegalComplianceProfile(BaseModel):
    legal_records: List[LegalRecord]
    compliance_records: List[ComplianceRecord]
    intellectual_property: List[IntellectualProperty]
    professional_licenses: List[ProfessionalLicense]
    business_entities: List[BusinessEntity]
    background_check_clear: bool
    security_clearance_level: Optional[str]
    watchlist_status: str  # clear, flagged, under_investigation
    risk_score: int  # 1-100, 100 being highest risk
    last_background_check: Optional[datetime]
    compliance_officer: Optional[str]

class LegalComplianceGenerator:
    def __init__(self):
        self.jurisdictions = [
            "Superior Court of California",
            "New York Supreme Court", 
            "Texas District Court",
            "Florida Circuit Court",
            "Illinois Cook County Court",
            "Federal District Court",
            "US Tax Court",
            "State Labor Department",
            "SEC",
            "EPA",
            "FDA",
            "OSHA"
        ]
        
        self.professional_licenses = {
            "Healthcare": ["Medical License", "Nursing License", "Pharmacy License", "Physical Therapy License"],
            "Legal": ["Bar License", "Paralegal Certification"],
            "Education": ["Teaching License", "Administrator License"],
            "Finance": ["CPA License", "Series 7", "Insurance License"],
            "Real Estate": ["Real Estate License", "Broker License"],
            "Engineering": ["Professional Engineer License"],
            "Technology": ["IT Certifications", "Security Clearance"]
        }
        
        self.business_types = [
            "LLC", "Corporation", "S-Corporation", "Partnership", 
            "Sole Proprietorship", "Non-Profit", "Professional Corporation"
        ]
        
        self.traffic_violations = [
            "Speeding", "Running Red Light", "Illegal Parking", "DUI", 
            "Reckless Driving", "Driving Without License", "Expired Registration"
        ]
        
        self.compliance_regulations = {
            ComplianceArea.FINANCIAL: ["SOX", "GDPR", "PCI DSS", "Anti-Money Laundering"],
            ComplianceArea.HEALTHCARE: ["HIPAA", "FDA Regulations", "Medicare Compliance"],
            ComplianceArea.EMPLOYMENT: ["OSHA", "Equal Employment Opportunity", "Family Medical Leave Act"],
            ComplianceArea.ENVIRONMENTAL: ["EPA Regulations", "Clean Air Act", "Waste Management"],
            ComplianceArea.DATA_PRIVACY: ["GDPR", "CCPA", "COPPA", "FERPA"],
            ComplianceArea.PROFESSIONAL: ["Professional Ethics", "Continuing Education", "License Maintenance"],
            ComplianceArea.BUSINESS: ["Business License", "Sales Tax", "Worker's Compensation"],
            ComplianceArea.TAX: ["IRS Compliance", "State Tax", "Payroll Tax"],
            ComplianceArea.IMMIGRATION: ["I-9 Verification", "Visa Compliance"],
            ComplianceArea.INTELLECTUAL_PROPERTY: ["Patent Filing", "Trademark Registration", "Copyright Protection"]
        }

    def generate_legal_compliance_profile(self, age: int, occupation: str, income: float, business_owner: bool = False) -> LegalComplianceProfile:
        """Generate comprehensive legal and compliance profile"""
        
        # Generate legal records (most people have some minor records)
        legal_records = self._generate_legal_records(age, income)
        
        # Generate compliance records based on occupation and business ownership
        compliance_records = self._generate_compliance_records(occupation, business_owner)
        
        # Generate intellectual property (if applicable)
        intellectual_property = self._generate_intellectual_property(occupation, income, age)
        
        # Generate professional licenses based on occupation
        professional_licenses = self._generate_professional_licenses(occupation, age)
        
        # Generate business entities (if business owner)
        business_entities = []
        if business_owner or random.random() < 0.1:  # 10% chance of owning business
            business_entities = self._generate_business_entities(age, income)
        
        # Background check status (most people are clear)
        background_check_clear = random.random() < 0.95
        
        # Security clearance (rare, mostly for government/defense workers)
        security_clearance = None
        if "government" in occupation.lower() or "defense" in occupation.lower() or random.random() < 0.05:
            security_clearance = random.choice(["Confidential", "Secret", "Top Secret"])
        
        # Watchlist status (extremely rare)
        watchlist_status = "clear"
        if random.random() < 0.001:  # 0.1% chance
            watchlist_status = random.choice(["flagged", "under_investigation"])
        
        # Risk score calculation
        risk_score = self._calculate_risk_score(legal_records, compliance_records, background_check_clear)
        
        # Last background check date
        last_background_check = None
        if age > 18 and random.random() < 0.7:  # 70% of adults have had background check
            last_background_check = datetime.now() - timedelta(days=random.randint(30, 1095))
        
        return LegalComplianceProfile(
            legal_records=legal_records,
            compliance_records=compliance_records,
            intellectual_property=intellectual_property,
            professional_licenses=professional_licenses,
            business_entities=business_entities,
            background_check_clear=background_check_clear,
            security_clearance_level=security_clearance,
            watchlist_status=watchlist_status,
            risk_score=risk_score,
            last_background_check=last_background_check,
            compliance_officer=f"Compliance Officer {random.randint(1000, 9999)}" if business_owner else None
        )

    def _generate_legal_records(self, age: int, income: float) -> List[LegalRecord]:
        """Generate legal records based on demographics"""
        records = []
        
        # Base probability of having legal records
        base_probability = 0.3  # 30% of people have some legal record
        
        # Age adjustments
        if age < 25:
            base_probability *= 0.6  # Young people less likely to have records
        elif age > 60:
            base_probability *= 0.8  # Older people less likely to get new records
        
        # Income adjustments (lower income slightly higher probability)
        if income < 30000:
            base_probability *= 1.2
        elif income > 100000:
            base_probability *= 0.8
        
        if random.random() > base_probability:
            return records
        
        # Number of records (most people have 1-3)
        num_records = random.choices([1, 2, 3, 4], weights=[0.6, 0.25, 0.10, 0.05])[0]
        
        for _ in range(num_records):
            record = self._create_legal_record(age)
            records.append(record)
        
        return records

    def _create_legal_record(self, age: int) -> LegalRecord:
        """Create a single legal record"""
        # Most common types are traffic violations
        record_types_weights = {
            LegalRecordType.TRAFFIC_VIOLATION: 0.7,
            LegalRecordType.CIVIL_LAWSUIT: 0.1,
            LegalRecordType.CRIMINAL_CHARGE: 0.05,
            LegalRecordType.DIVORCE: 0.08,
            LegalRecordType.BANKRUPTCY: 0.03,
            LegalRecordType.PROPERTY_DEED: 0.02,
            LegalRecordType.TAX_LIEN: 0.02
        }
        
        record_type = random.choices(
            list(record_types_weights.keys()),
            weights=list(record_types_weights.values())
        )[0]
        
        # Date (sometime in the past)
        years_back = random.randint(1, min(age - 16, 20))  # Up to 20 years or since age 16
        date_filed = datetime.now() - timedelta(days=years_back * 365 + random.randint(0, 365))
        
        # Generate record details based on type
        if record_type == LegalRecordType.TRAFFIC_VIOLATION:
            violation = random.choice(self.traffic_violations)
            title = f"Traffic Violation - {violation}"
            description = f"Cited for {violation.lower()}"
            severity = SeverityLevel.LOW if violation not in ["DUI", "Reckless Driving"] else SeverityLevel.HIGH
            financial_impact = random.uniform(50, 500) if violation != "DUI" else random.uniform(1000, 5000)
            
        elif record_type == LegalRecordType.CIVIL_LAWSUIT:
            lawsuit_types = ["Contract Dispute", "Personal Injury", "Property Dispute", "Employment Dispute"]
            lawsuit_type = random.choice(lawsuit_types)
            title = f"Civil Lawsuit - {lawsuit_type}"
            description = f"Civil litigation regarding {lawsuit_type.lower()}"
            severity = SeverityLevel.MEDIUM
            financial_impact = random.uniform(1000, 50000)
            
        elif record_type == LegalRecordType.CRIMINAL_CHARGE:
            charges = ["Misdemeanor Theft", "Public Intoxication", "Disorderly Conduct", "Simple Assault"]
            charge = random.choice(charges)
            title = f"Criminal Charge - {charge}"
            description = f"Charged with {charge.lower()}"
            severity = SeverityLevel.MEDIUM
            financial_impact = random.uniform(500, 2000)
            
        else:
            title = f"{record_type.value.replace('_', ' ').title()}"
            description = f"Legal matter involving {record_type.value.replace('_', ' ')}"
            severity = SeverityLevel.MEDIUM
            financial_impact = random.uniform(100, 10000)
        
        # Status and resolution
        status_weights = [0.7, 0.2, 0.05, 0.03, 0.02]
        status = random.choices(list(RecordStatus), weights=status_weights)[0]
        
        resolved_date = None
        outcome = None
        if status == RecordStatus.RESOLVED:
            resolved_date = date_filed + timedelta(days=random.randint(30, 730))
            outcomes = ["Guilty", "Not Guilty", "Settled", "Dismissed", "Plea Agreement"]
            outcome = random.choice(outcomes)
        
        return LegalRecord(
            record_id=str(uuid.uuid4()),
            record_type=record_type,
            date_filed=date_filed,
            jurisdiction=random.choice(self.jurisdictions),
            case_number=f"{random.randint(2020, 2025)}-{random.randint(100000, 999999)}",
            title=title,
            description=description,
            status=status,
            severity=severity,
            parties_involved=[f"Party {i+1}" for i in range(random.randint(1, 3))],
            legal_representation=f"Attorney {random.randint(1000, 9999)}" if random.random() < 0.6 else None,
            outcome=outcome,
            financial_impact=round(financial_impact, 2) if financial_impact else None,
            resolved_date=resolved_date,
            appeal_filed=random.random() < 0.1,
            public_record=random.random() < 0.8
        )

    def _generate_compliance_records(self, occupation: str, business_owner: bool) -> List[ComplianceRecord]:
        """Generate compliance records based on occupation"""
        records = []
        
        # Determine relevant compliance areas
        relevant_areas = []
        
        if "healthcare" in occupation.lower() or "medical" in occupation.lower():
            relevant_areas.append(ComplianceArea.HEALTHCARE)
        if "finance" in occupation.lower() or "bank" in occupation.lower():
            relevant_areas.append(ComplianceArea.FINANCIAL)
        if "engineer" in occupation.lower() or "environment" in occupation.lower():
            relevant_areas.append(ComplianceArea.ENVIRONMENTAL)
        if "tech" in occupation.lower() or "software" in occupation.lower():
            relevant_areas.append(ComplianceArea.DATA_PRIVACY)
        
        # Everyone has some basic compliance
        relevant_areas.append(ComplianceArea.TAX)
        if business_owner:
            relevant_areas.extend([ComplianceArea.BUSINESS, ComplianceArea.EMPLOYMENT])
        
        # Generate records for each area
        for area in relevant_areas:
            if random.random() < 0.7:  # 70% chance of having compliance record
                record = self._create_compliance_record(area)
                records.append(record)
        
        return records

    def _create_compliance_record(self, area: ComplianceArea) -> ComplianceRecord:
        """Create a single compliance record"""
        regulations = self.compliance_regulations.get(area, ["General Compliance"])
        regulation = random.choice(regulations)
        
        compliance_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        # Most compliance is good
        status = random.choices(
            ["compliant", "non_compliant", "pending_review"],
            weights=[0.8, 0.15, 0.05]
        )[0]
        
        # Audit information
        audit_date = None
        audit_result = None
        if random.random() < 0.3:  # 30% chance of recent audit
            audit_date = compliance_date + timedelta(days=random.randint(30, 90))
            audit_result = "Passed" if status == "compliant" else "Failed"
        
        # Remediation
        remediation_required = status == "non_compliant"
        remediation_deadline = None
        if remediation_required:
            remediation_deadline = datetime.now() + timedelta(days=random.randint(30, 180))
        
        return ComplianceRecord(
            compliance_id=str(uuid.uuid4()),
            area=area,
            regulation_name=regulation,
            compliance_date=compliance_date,
            status=status,
            audit_date=audit_date,
            audit_result=audit_result,
            remediation_required=remediation_required,
            remediation_deadline=remediation_deadline,
            responsible_party=f"Officer {random.randint(1000, 9999)}",
            documentation_path=f"/compliance/{area.value}/{regulation.replace(' ', '_').lower()}.pdf" if random.random() < 0.6 else None,
            next_review_date=datetime.now() + timedelta(days=random.randint(90, 365))
        )

    def _generate_intellectual_property(self, occupation: str, income: float, age: int) -> List[IntellectualProperty]:
        """Generate intellectual property records"""
        ip_records = []
        
        # Higher probability for certain occupations
        ip_probability = 0.05  # Base 5%
        
        if any(term in occupation.lower() for term in ["engineer", "scientist", "researcher", "developer", "artist", "writer"]):
            ip_probability = 0.3
        elif income > 100000:
            ip_probability = 0.15
        
        if random.random() > ip_probability:
            return ip_records
        
        # Number of IP records
        num_records = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        
        for _ in range(num_records):
            ip_record = self._create_ip_record(occupation)
            ip_records.append(ip_record)
        
        return ip_records

    def _create_ip_record(self, occupation: str) -> IntellectualProperty:
        """Create an intellectual property record"""
        # Type based on occupation
        if "software" in occupation.lower() or "tech" in occupation.lower():
            ip_type = random.choice(["patent", "copyright", "trade_secret"])
        elif "artist" in occupation.lower() or "writer" in occupation.lower():
            ip_type = "copyright"
        elif "business" in occupation.lower():
            ip_type = random.choice(["trademark", "trade_secret"])
        else:
            ip_type = random.choice(["patent", "trademark", "copyright"])
        
        filing_date = datetime.now() - timedelta(days=random.randint(30, 1095))
        
        # Grant date (if applicable)
        grant_date = None
        status = "pending"
        if random.random() < 0.7:  # 70% chance of being granted
            grant_date = filing_date + timedelta(days=random.randint(180, 730))
            status = "granted"
        
        # Expiration date
        expiration_date = None
        if grant_date:
            if ip_type == "patent":
                expiration_date = grant_date + timedelta(days=20*365)  # 20 years
            elif ip_type == "trademark":
                expiration_date = grant_date + timedelta(days=10*365)  # 10 years, renewable
            elif ip_type == "copyright":
                expiration_date = grant_date + timedelta(days=70*365)  # Life + 70 years (simplified)
        
        return IntellectualProperty(
            ip_id=str(uuid.uuid4()),
            type=ip_type,
            title=f"{ip_type.title()} Application {random.randint(1000, 9999)}",
            description=f"Innovative {ip_type} related to {occupation.lower()}",
            registration_number=f"{ip_type.upper()[:3]}{random.randint(100000, 999999)}" if status == "granted" else None,
            filing_date=filing_date,
            grant_date=grant_date,
            expiration_date=expiration_date,
            status=status,
            inventors_authors=[f"Inventor {random.randint(1, 3)}"],
            assignee=f"Company {random.randint(1000, 9999)}",
            categories=[f"Category {random.randint(1, 10)}"],
            estimated_value=random.uniform(5000, 100000) if status == "granted" else None
        )

    def _generate_professional_licenses(self, occupation: str, age: int) -> List[ProfessionalLicense]:
        """Generate professional licenses based on occupation"""
        licenses = []
        
        # Determine if occupation requires licenses
        for profession, license_types in self.professional_licenses.items():
            if profession.lower() in occupation.lower():
                # Generate 1-2 licenses for this profession
                num_licenses = random.randint(1, 2)
                for _ in range(num_licenses):
                    license = self._create_professional_license(profession, random.choice(license_types), age)
                    licenses.append(license)
                break
        
        return licenses

    def _create_professional_license(self, profession: str, license_type: str, age: int) -> ProfessionalLicense:
        """Create a professional license"""
        # License obtained sometime after age 18
        years_since_18 = max(0, age - 18)
        years_licensed = random.randint(1, min(years_since_18, 30))
        
        issue_date = datetime.now() - timedelta(days=years_licensed * 365)
        expiration_date = datetime.now() + timedelta(days=random.randint(365, 1095))  # 1-3 years
        
        # License status
        status = "active"
        if random.random() < 0.05:  # 5% chance of issues
            status = random.choice(["expired", "suspended"])
        
        # Continuing education
        ce_required = random.random() < 0.8  # 80% require continuing education
        ce_hours = random.randint(10, 40) if ce_required else None
        
        # Disciplinary actions (rare)
        disciplinary_actions = []
        if random.random() < 0.05:  # 5% chance
            disciplinary_actions.append({
                "date": (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                "action": random.choice(["Warning", "Fine", "Probation"]),
                "reason": "Professional misconduct"
            })
        
        # Renewal history
        renewal_history = []
        for i in range(years_licensed):
            renewal_date = issue_date + timedelta(days=i * 365)
            renewal_history.append({"renewal_date": renewal_date})
        
        return ProfessionalLicense(
            license_id=str(uuid.uuid4()),
            license_type=license_type,
            profession=profession,
            license_number=f"{license_type[:3].upper()}{random.randint(100000, 999999)}",
            issuing_authority=f"{profession} Board",
            issue_date=issue_date,
            expiration_date=expiration_date,
            status=status,
            continuing_education_required=ce_required,
            continuing_education_hours=ce_hours,
            disciplinary_actions=disciplinary_actions,
            renewal_history=renewal_history
        )

    def _generate_business_entities(self, age: int, income: float) -> List[BusinessEntity]:
        """Generate business entities for business owners"""
        entities = []
        
        # Number of businesses (most have 1, some have more)
        num_businesses = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
        
        for _ in range(num_businesses):
            entity = self._create_business_entity(age)
            entities.append(entity)
        
        return entities

    def _create_business_entity(self, age: int) -> BusinessEntity:
        """Create a business entity"""
        business_names = [
            "Consulting Services LLC", "Tech Solutions Inc", "Marketing Group",
            "Construction Co", "Real Estate Holdings", "Investment Partners"
        ]
        
        business_name = f"{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Prime'])} {random.choice(business_names)}"
        entity_type = random.choice(self.business_types)
        
        # Incorporation date (sometime after person turned 18)
        years_since_18 = max(0, age - 18)
        years_in_business = random.randint(1, min(years_since_18, 20))
        incorporation_date = datetime.now() - timedelta(days=years_in_business * 365)
        
        states = ["DE", "CA", "NY", "TX", "FL", "NV"]
        state = random.choice(states)
        
        # Business status
        status = "active"
        if random.random() < 0.1:  # 10% chance of being dissolved
            status = random.choice(["dissolved", "suspended"])
        
        return BusinessEntity(
            entity_id=str(uuid.uuid4()),
            business_name=business_name,
            entity_type=entity_type,
            registration_number=f"{state}{random.randint(1000000, 9999999)}",
            state_of_incorporation=state,
            incorporation_date=incorporation_date,
            registered_agent=f"Agent Services {random.randint(100, 999)}",
            business_address=f"{random.randint(100, 9999)} Business St, {random.choice(['New York', 'Los Angeles', 'Chicago'])}, {state}",
            status=status,
            annual_report_filed=random.random() < 0.9,  # 90% file annual reports
            tax_id=f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}",
            officers=[
                {
                    "name": f"Officer {random.randint(1, 5)}",
                    "title": random.choice(["President", "Secretary", "Treasurer", "Manager"]),
                    "appointment_date": incorporation_date.isoformat()
                }
            ],
            business_licenses=[f"License {random.randint(1000, 9999)}"]
        )

    def _calculate_risk_score(self, legal_records: List[LegalRecord], compliance_records: List[ComplianceRecord], background_clear: bool) -> int:
        """Calculate overall risk score"""
        risk_score = 10  # Base low risk
        
        # Add risk for legal records
        for record in legal_records:
            if record.severity == SeverityLevel.HIGH:
                risk_score += 30
            elif record.severity == SeverityLevel.MEDIUM:
                risk_score += 15
            else:
                risk_score += 5
        
        # Add risk for compliance issues
        for record in compliance_records:
            if record.status == "non_compliant":
                risk_score += 20
            elif record.status == "pending_review":
                risk_score += 10
        
        # Background check impact
        if not background_clear:
            risk_score += 40
        
        return min(100, risk_score)  # Cap at 100