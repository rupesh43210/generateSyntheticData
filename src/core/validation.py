"""
Advanced data validation and consistency checking system
"""

import re
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import logging

class ValidationSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    FORMAT = "format"
    RANGE = "range"
    CONSISTENCY = "consistency"
    BUSINESS_LOGIC = "business_logic"
    REFERENCE_INTEGRITY = "reference_integrity"

@dataclass
class ValidationResult:
    is_valid: bool
    severity: ValidationSeverity
    category: ValidationCategory
    field_name: str
    message: str
    suggested_fix: Optional[str] = None
    original_value: Any = None
    corrected_value: Any = None

class DataValidator:
    """Comprehensive data validation system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Validation patterns
        self.ssn_pattern = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')
        self.zip_code_pattern = re.compile(r'^\d{5}(-\d{4})?$')
        self.phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
        
        # US states for validation
        self.us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        
        # Blood types
        self.blood_types = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        
        # Gender values
        self.valid_genders = {'M', 'F', 'O', 'U'}
    
    def validate_person(self, person_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate a complete person record"""
        results = []
        
        # Basic field validation
        results.extend(self._validate_ssn(person_data.get('ssn')))
        results.extend(self._validate_name_fields(person_data))
        results.extend(self._validate_date_of_birth(person_data.get('date_of_birth')))
        results.extend(self._validate_gender(person_data.get('gender')))
        
        # Address validation
        if 'addresses' in person_data:
            for i, address in enumerate(person_data['addresses']):
                results.extend(self._validate_address(address, f"addresses[{i}]"))
        
        # Phone validation
        if 'phone_numbers' in person_data:
            for i, phone in enumerate(person_data['phone_numbers']):
                results.extend(self._validate_phone(phone, f"phone_numbers[{i}]"))
        
        # Email validation
        if 'email_addresses' in person_data:
            for i, email in enumerate(person_data['email_addresses']):
                results.extend(self._validate_email(email, f"email_addresses[{i}]"))
        
        # Financial validation
        if 'financial_profile' in person_data:
            results.extend(self._validate_financial_profile(person_data['financial_profile']))
        
        # Medical validation
        if 'medical_profile' in person_data:
            results.extend(self._validate_medical_profile(person_data['medical_profile']))
        
        # Consistency checks
        results.extend(self._validate_consistency(person_data))
        
        return results
    
    def _validate_ssn(self, ssn: Any) -> List[ValidationResult]:
        """Validate Social Security Number"""
        results = []
        
        if ssn is None:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.FORMAT,
                field_name='ssn',
                message='SSN is required',
                suggested_fix='Generate a valid SSN'
            ))
            return results
        
        if not isinstance(ssn, str):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name='ssn',
                message='SSN must be a string',
                original_value=ssn,
                suggested_fix='Convert to string format'
            ))
            return results
        
        # Remove formatting for validation
        clean_ssn = re.sub(r'[^0-9]', '', ssn)
        
        if len(clean_ssn) != 9:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name='ssn',
                message=f'SSN must be 9 digits, got {len(clean_ssn)}',
                original_value=ssn,
                suggested_fix='Use XXX-XX-XXXX format'
            ))
        
        # Check for invalid SSN patterns
        if clean_ssn in ['000000000', '123456789', '111111111']:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.BUSINESS_LOGIC,
                field_name='ssn',
                message='SSN contains invalid pattern',
                original_value=ssn,
                suggested_fix='Generate a realistic SSN'
            ))
        
        # Check area number (first 3 digits)
        if clean_ssn and clean_ssn[:3] in ['000', '666'] or clean_ssn[:3] >= '900':
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.BUSINESS_LOGIC,
                field_name='ssn',
                message='SSN area number is invalid',
                original_value=ssn,
                suggested_fix='Use valid area number (001-665, 667-899)'
            ))
        
        return results
    
    def _validate_name_fields(self, person_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate name fields"""
        results = []
        
        for field in ['first_name', 'last_name']:
            value = person_data.get(field)
            if not value:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.FORMAT,
                    field_name=field,
                    message=f'{field} is required',
                    suggested_fix='Provide a valid name'
                ))
            elif not isinstance(value, str):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.FORMAT,
                    field_name=field,
                    message=f'{field} must be a string',
                    original_value=value
                ))
            elif len(value.strip()) < 2:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.RANGE,
                    field_name=field,
                    message=f'{field} is too short',
                    original_value=value,
                    suggested_fix='Use at least 2 characters'
                ))
        
        # Middle name validation (optional but should be valid if present)
        middle_name = person_data.get('middle_name')
        if middle_name and not isinstance(middle_name, str):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.FORMAT,
                field_name='middle_name',
                message='Middle name must be a string',
                original_value=middle_name
            ))
        
        return results
    
    def _validate_date_of_birth(self, dob: Any) -> List[ValidationResult]:
        """Validate date of birth"""
        results = []
        
        if dob is None:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.FORMAT,
                field_name='date_of_birth',
                message='Date of birth is required'
            ))
            return results
        
        # Convert string to date if needed
        if isinstance(dob, str):
            try:
                dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.FORMAT,
                    field_name='date_of_birth',
                    message='Invalid date format',
                    original_value=dob,
                    suggested_fix='Use YYYY-MM-DD format'
                ))
                return results
        
        if not isinstance(dob, datetime.date):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name='date_of_birth',
                message='Date of birth must be a date object',
                original_value=dob
            ))
            return results
        
        # Check realistic date ranges
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 0:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.BUSINESS_LOGIC,
                field_name='date_of_birth',
                message='Date of birth cannot be in the future',
                original_value=dob
            ))
        elif age > 150:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.BUSINESS_LOGIC,
                field_name='date_of_birth',
                message='Age exceeds realistic maximum',
                original_value=dob,
                suggested_fix='Use a more recent birth date'
            ))
        elif age < 18 and age > 0:
            results.append(ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.BUSINESS_LOGIC,
                field_name='date_of_birth',
                message='Person is a minor',
                original_value=dob
            ))
        
        return results
    
    def _validate_gender(self, gender: Any) -> List[ValidationResult]:
        """Validate gender field"""
        results = []
        
        if gender is None:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name='gender',
                message='Gender is required'
            ))
            return results
        
        # Handle enum values
        gender_value = gender.value if hasattr(gender, 'value') else gender
        
        if gender_value not in self.valid_genders:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.RANGE,
                field_name='gender',
                message=f'Invalid gender value: {gender_value}',
                original_value=gender,
                suggested_fix='Use M, F, O, or U'
            ))
        
        return results
    
    def _validate_address(self, address: Dict[str, Any], field_prefix: str) -> List[ValidationResult]:
        """Validate address information"""
        results = []
        
        # Required fields
        required_fields = ['street_1', 'city', 'state', 'zip_code']
        for field in required_fields:
            if not address.get(field):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.FORMAT,
                    field_name=f'{field_prefix}.{field}',
                    message=f'{field} is required for address'
                ))
        
        # State validation
        state = address.get('state')
        if state and state not in self.us_states:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.RANGE,
                field_name=f'{field_prefix}.state',
                message=f'Invalid state code: {state}',
                original_value=state,
                suggested_fix='Use valid 2-letter state code'
            ))
        
        # ZIP code validation
        zip_code = address.get('zip_code')
        if zip_code and not self.zip_code_pattern.match(str(zip_code)):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name=f'{field_prefix}.zip_code',
                message='Invalid ZIP code format',
                original_value=zip_code,
                suggested_fix='Use XXXXX or XXXXX-XXXX format'
            ))
        
        return results
    
    def _validate_phone(self, phone: Dict[str, Any], field_prefix: str) -> List[ValidationResult]:
        """Validate phone number"""
        results = []
        
        area_code = phone.get('area_code')
        number = phone.get('number')
        
        if not area_code or not number:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name=f'{field_prefix}',
                message='Phone number missing area code or number'
            ))
            return results
        
        # Construct full number for validation
        full_number = f"{area_code}{number}"
        
        try:
            parsed = phonenumbers.parse(f"+1{full_number}", "US")
            if not phonenumbers.is_valid_number(parsed):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.FORMAT,
                    field_name=f'{field_prefix}',
                    message='Invalid phone number',
                    original_value=full_number
                ))
        except:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name=f'{field_prefix}',
                message='Phone number format error',
                original_value=full_number
            ))
        
        return results
    
    def _validate_email(self, email: Dict[str, Any], field_prefix: str) -> List[ValidationResult]:
        """Validate email address"""
        results = []
        
        email_address = email.get('email')
        if not email_address:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name=f'{field_prefix}.email',
                message='Email address is required'
            ))
            return results
        
        try:
            validate_email(email_address)
        except EmailNotValidError as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.FORMAT,
                field_name=f'{field_prefix}.email',
                message=f'Invalid email: {str(e)}',
                original_value=email_address
            ))
        
        return results
    
    def _validate_financial_profile(self, financial: Dict[str, Any]) -> List[ValidationResult]:
        """Validate financial information"""
        results = []
        
        # Credit score validation
        credit_score = financial.get('credit_score')
        if credit_score is not None:
            if not isinstance(credit_score, (int, float)):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.FORMAT,
                    field_name='financial_profile.credit_score',
                    message='Credit score must be numeric',
                    original_value=credit_score
                ))
            elif credit_score < 300 or credit_score > 850:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.RANGE,
                    field_name='financial_profile.credit_score',
                    message=f'Credit score out of range: {credit_score}',
                    original_value=credit_score,
                    suggested_fix='Use range 300-850'
                ))
        
        # Income validation
        income = financial.get('annual_income')
        if income is not None and income < 0:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.RANGE,
                field_name='financial_profile.annual_income',
                message='Income cannot be negative',
                original_value=income
            ))
        
        # Debt-to-income ratio validation
        debt_ratio = financial.get('debt_to_income_ratio')
        if debt_ratio is not None:
            if debt_ratio < 0 or debt_ratio > 10:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.RANGE,
                    field_name='financial_profile.debt_to_income_ratio',
                    message=f'Debt-to-income ratio out of range: {debt_ratio}',
                    original_value=debt_ratio,
                    suggested_fix='Use range 0-10'
                ))
        
        return results
    
    def _validate_medical_profile(self, medical: Dict[str, Any]) -> List[ValidationResult]:
        """Validate medical information"""
        results = []
        
        # Blood type validation
        blood_type = medical.get('blood_type')
        if blood_type and blood_type not in self.blood_types:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.RANGE,
                field_name='medical_profile.blood_type',
                message=f'Invalid blood type: {blood_type}',
                original_value=blood_type,
                suggested_fix='Use valid blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)'
            ))
        
        return results
    
    def _validate_consistency(self, person_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data consistency across fields"""
        results = []
        
        # Age consistency with employment
        dob = person_data.get('date_of_birth')
        if dob:
            if isinstance(dob, str):
                try:
                    dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    return results  # Skip if date is invalid
            
            age = datetime.date.today().year - dob.year
            
            employment_history = person_data.get('employment_history', [])
            for i, job in enumerate(employment_history):
                start_date = job.get('start_date')
                if start_date:
                    if isinstance(start_date, str):
                        try:
                            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                        except:
                            continue
                    
                    age_at_start = start_date.year - dob.year
                    if age_at_start < 14:
                        results.append(ValidationResult(
                            is_valid=False,
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.CONSISTENCY,
                            field_name=f'employment_history[{i}].start_date',
                            message=f'Employment started at unrealistic age: {age_at_start}',
                            suggested_fix='Adjust employment start date'
                        ))
        
        # Email domain consistency
        email_addresses = person_data.get('email_addresses', [])
        domains = set()
        for email in email_addresses:
            email_addr = email.get('email', '')
            if '@' in email_addr:
                domain = email_addr.split('@')[1]
                domains.add(domain)
        
        if len(domains) > 3:
            results.append(ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.CONSISTENCY,
                field_name='email_addresses',
                message=f'Person has many different email domains ({len(domains)})',
                suggested_fix='Consider consolidating email providers'
            ))
        
        return results
    
    def generate_validation_report(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate a comprehensive validation report"""
        if not validation_results:
            return {
                "overall_status": "VALID",
                "total_issues": 0,
                "summary": "No validation issues found"
            }
        
        report = {
            "overall_status": "INVALID",
            "total_issues": len(validation_results),
            "by_severity": {},
            "by_category": {},
            "critical_issues": [],
            "errors": [],
            "warnings": [],
            "suggested_fixes": []
        }
        
        for result in validation_results:
            # Count by severity
            severity = result.severity.value
            report["by_severity"][severity] = report["by_severity"].get(severity, 0) + 1
            
            # Count by category
            category = result.category.value
            report["by_category"][category] = report["by_category"].get(category, 0) + 1
            
            # Organize by severity
            if result.severity == ValidationSeverity.CRITICAL:
                report["critical_issues"].append({
                    "field": result.field_name,
                    "message": result.message,
                    "suggested_fix": result.suggested_fix
                })
            elif result.severity == ValidationSeverity.ERROR:
                report["errors"].append({
                    "field": result.field_name,
                    "message": result.message,
                    "suggested_fix": result.suggested_fix
                })
            else:
                report["warnings"].append({
                    "field": result.field_name,
                    "message": result.message,
                    "suggested_fix": result.suggested_fix
                })
            
            # Collect suggested fixes
            if result.suggested_fix:
                report["suggested_fixes"].append({
                    "field": result.field_name,
                    "fix": result.suggested_fix
                })
        
        # Determine overall status
        if not any(r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] for r in validation_results):
            report["overall_status"] = "VALID_WITH_WARNINGS"
        
        return report