#!/usr/bin/env python3
"""
Enhanced PII Generator Web Application with robust features
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import csv
import io
import os
import time
import threading
from datetime import datetime, date
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging

# Import all model classes to ensure they're loaded before rebuilding
from src.generators.medical_generator import MedicalProfile
from src.generators.vehicle_generator import VehicleProfile  
from src.generators.education_generator import EducationProfile
from src.generators.social_generator import OnlinePresence
from src.generators.biometric_generator import PhysicalProfile
from src.generators.lifestyle_generator import LifestyleProfile
from src.generators.travel_generator import TravelProfile
from src.generators.financial_transactions_generator import FinancialProfile as EnhancedFinancialProfile
from src.generators.communication_generator import CommunicationProfile

from src.core.models import GenerationConfig, DataQualityProfile, Person, rebuild_person_model
from src.core.performance import PerformanceOptimizer

# Force model rebuild here before any other imports
rebuild_person_model()

from src.generators.person_generator import PersonGenerator
from src.db.azure_sql import EnhancedAzureSQLDatabase as AzureSQLDatabase

# Import new enhanced modules
from src.core.error_handling import error_handler, ErrorCategory, ErrorSeverity
from src.core.validation import DataValidator
from src.core.progress_tracker import (
    progress_tracker, WebSocketProgressNotifier, 
    TaskType, TaskStatus
)

# Configure enhanced logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/pii_generator_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model already rebuilt above
logger.info("Person model rebuild completed during imports")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pii-generator-enhanced-secret-key'

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global executor for background tasks
executor = ThreadPoolExecutor(max_workers=8)

# Store generation tasks with enhanced metadata
generation_tasks = {}

# Initialize enhanced components
data_validator = DataValidator()

def send_progress_update(task_id, status, progress_percent, current_step, current_count, total_count, elapsed_time=0, rate_per_second=0, estimated_remaining=0):
    """Send WebSocket progress update safely from main thread"""
    try:
        socketio.emit('progress_update', {
            'task_id': task_id,
            'task_type': 'generation',
            'status': status,
            'progress_percent': progress_percent,
            'current_step': current_step,
            'current_count': current_count,
            'total_count': total_count,
            'elapsed_time': elapsed_time,
            'estimated_remaining': estimated_remaining,
            'rate_per_second': rate_per_second
        })
    except Exception as e:
        # Don't let WebSocket errors break generation
        logger.warning(f"Failed to send WebSocket update: {e}")

# Logger will be configured above

@app.route('/')
def index():
    """Render the enhanced web interface"""
    return render_template('index_enhanced.html')

@app.route('/api/generate', methods=['POST'])
def generate_data():
    """Enhanced data generation with robust error handling and progress tracking"""
    try:
        data = request.json
        
        # Extract and validate parameters
        num_records = min(data.get('records', 1000), 100000)  # Cap at 100k for safety
        variability_profile = data.get('variability_profile', 'realistic')
        num_threads = min(data.get('threads', 4), 16)  # Cap at 16 threads
        batch_size = min(data.get('batch_size', 1000), 10000)  # Cap batch size
        include_families = data.get('include_families', False)
        num_families = data.get('num_families', 0)
        enable_validation = data.get('enable_validation', True)
        
        # Create task for progress tracking
        task_id = progress_tracker.create_task(
            TaskType.GENERATION,
            num_records,
            f"Generating {num_records} PII records"
        )
        
        # Submit generation to background thread
        future = executor.submit(
            _generate_data_background,
            task_id, num_records, variability_profile, num_threads, 
            batch_size, include_families, num_families, enable_validation
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Generation started',
            'estimated_time': _estimate_generation_time(num_records, num_threads)
        })
        
    except Exception as e:
        error_context = error_handler.handle_error(
            e, ErrorCategory.GENERATION, ErrorSeverity.HIGH,
            context_data={'request_data': data}
        )
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_id': error_context.error_id,
            'recovery_attempted': error_context.recovery_attempted
        }), 500

def _generate_data_background(task_id, num_records, variability_profile, 
                            num_threads, batch_size, include_families, 
                            num_families, enable_validation):
    """Background generation with enhanced error handling"""
    try:
        # Only use progress tracker - avoid WebSocket calls from background thread
        progress_tracker.start_task(task_id, "Initializing generators")
        
        # Create data quality profile based on selection
        profiles = {
            'minimal': DataQualityProfile(
                missing_data_rate=0.01, typo_rate=0.005, duplicate_rate=0.0001,
                outlier_rate=0.001, inconsistency_rate=0.01
            ),
            'realistic': DataQualityProfile(
                missing_data_rate=0.05, typo_rate=0.02, duplicate_rate=0.001,
                outlier_rate=0.01, inconsistency_rate=0.03
            ),
            'messy': DataQualityProfile(
                missing_data_rate=0.15, typo_rate=0.05, duplicate_rate=0.005,
                outlier_rate=0.03, inconsistency_rate=0.08
            ),
            'extreme': DataQualityProfile(
                missing_data_rate=0.25, typo_rate=0.10, duplicate_rate=0.01,
                outlier_rate=0.05, inconsistency_rate=0.15
            )
        }
        
        # Create generation config with error recovery
        config = GenerationConfig(
            num_records=num_records,
            batch_size=batch_size,
            num_threads=num_threads,
            data_quality_profile=profiles[variability_profile]
        )
        
        # Initialize generators with error handling
        try:
            person_gen = PersonGenerator(config)
            performance_opt = PerformanceOptimizer(config)
        except Exception as e:
            error_handler.handle_error(
                e, ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL,
                context_data={'config': config.__dict__}
            )
            progress_tracker.fail_task(task_id, f"Failed to initialize generators: {str(e)}")
            return
        
        start_time = time.time()
        progress_tracker.update_progress(task_id, 0, "Starting data generation")
        
        # Generate data with progress tracking
        all_people = []
        validation_results = []
        
        if include_families and num_families > 0:
            progress_tracker.update_progress(task_id, 0, "Generating family clusters")
            try:
                family_clusters = person_gen.create_family_clusters(num_families)
                all_people = [person for family in family_clusters for person in family]
                
                progress_tracker.update_progress(
                    task_id, len(all_people), 
                    f"Generated {len(all_people)} family members"
                )
            except Exception as e:
                error_handler.handle_error(
                    e, ErrorCategory.GENERATION, ErrorSeverity.HIGH,
                    context_data={'num_families': num_families}
                )
                progress_tracker.fail_task(task_id, f"Family generation failed: {str(e)}")
                return
            
            # Generate additional individual records if needed
            remaining = num_records - len(all_people)
            if remaining > 0:
                all_people.extend(_generate_individual_records(
                    task_id, performance_opt, person_gen, remaining, 
                    batch_size, num_threads, len(all_people)
                ))
        else:
            all_people = _generate_individual_records(
                task_id, performance_opt, person_gen, num_records, 
                batch_size, num_threads, 0
            )
        
        elapsed = time.time() - start_time
        rate = len(all_people) / elapsed if elapsed > 0 else 0
        
        # Validation phase
        if enable_validation and all_people:
            progress_tracker.update_progress(
                task_id, len(all_people), 
                "Running data validation", 
                {'validation_started': True}
            )
            
            validation_results = _validate_generated_data(task_id, all_people[:100])  # Sample validation
        
        # Store results with enhanced metadata (make JSON serializable)
        config_dict = {
            'num_records': config.num_records,
            'batch_size': config.batch_size,
            'num_threads': config.num_threads,
            'data_quality_profile': {
                'missing_data_rate': config.data_quality_profile.missing_data_rate,
                'typo_rate': config.data_quality_profile.typo_rate,
                'duplicate_rate': config.data_quality_profile.duplicate_rate,
                'outlier_rate': config.data_quality_profile.outlier_rate,
                'inconsistency_rate': config.data_quality_profile.inconsistency_rate
            }
        }
        
        generation_tasks[task_id] = {
            'people': all_people,
            'metadata': {
                'generation_time': elapsed,
                'records_per_second': rate,
                'total_records': len(all_people),
                'config': config_dict,
                'validation_enabled': enable_validation,
                'validation_results': validation_results,
                'generated_at': datetime.now().isoformat(),
                'task_id': task_id
            }
        }
        
        # WebSocket updates will be sent via polling mechanism
        
        # Complete task
        progress_tracker.complete_task(task_id, {
            'total_generated': len(all_people),
            'generation_rate': rate,
            'validation_issues': len(validation_results) if validation_results else 0
        })
        
        logger.info(f"Successfully generated {len(all_people)} records in {elapsed:.2f}s")
        
    except Exception as e:
        error_context = error_handler.handle_error(
            e, ErrorCategory.GENERATION, ErrorSeverity.CRITICAL,
            context_data={'task_id': task_id, 'num_records': num_records}
        )
        progress_tracker.fail_task(task_id, str(e), {'error_id': error_context.error_id})
        logger.error(f"Generation failed for task {task_id}: {str(e)}")

def _generate_individual_records(task_id, performance_opt, person_gen, 
                               num_records, batch_size, num_threads, start_count):
    """Generate individual records with progress tracking"""
    people = []
    processed = 0
    start_time = time.time()
    
    try:
        for batch in performance_opt.generate_parallel(
            person_gen.generate_person, num_records, batch_size, num_threads
        ):
            people.extend(batch)
            processed += len(batch)
            
            # Calculate progress metrics
            elapsed = time.time() - start_time
            progress_percent = ((start_count + processed) / (start_count + num_records)) * 100
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = (num_records - processed) / rate if rate > 0 else None
            
            # Update progress tracker only (WebSocket updates via polling)
            progress_tracker.update_progress(
                task_id, 
                start_count + processed,
                f"Generated {processed}/{num_records} individual records"
            )
    except Exception as e:
        error_handler.handle_error(
            e, ErrorCategory.GENERATION, ErrorSeverity.HIGH,
            context_data={'processed': processed, 'target': num_records}
        )
        raise
    
    return people

def _validate_generated_data(task_id, sample_people):
    """Validate generated data quality"""
    validation_results = []
    
    try:
        for i, person in enumerate(sample_people[:50]):  # Validate first 50
            if hasattr(person, 'model_dump'):
                person_dict = person.model_dump()
            elif hasattr(person, 'dict'):
                person_dict = person.dict()
            else:
                person_dict = person.__dict__
            results = data_validator.validate_person(person_dict)
            
            # Convert validation results to JSON-serializable format
            for result in results:
                serializable_result = {
                    'is_valid': result.is_valid,
                    'severity': result.severity.value,
                    'category': result.category.value,
                    'field_name': result.field_name,
                    'message': result.message,
                    'suggested_fix': result.suggested_fix,
                    'original_value': str(result.original_value) if result.original_value is not None else None,
                    'corrected_value': str(result.corrected_value) if result.corrected_value is not None else None
                }
                validation_results.append(serializable_result)
            
            if i % 10 == 0:
                progress_tracker.update_progress(
                    task_id, len(sample_people) + i,
                    f"Validating record {i+1}/50"
                )
    except Exception as e:
        error_handler.handle_error(
            e, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM,
            context_data={'validation_progress': len(validation_results)}
        )
    
    return validation_results

def _estimate_generation_time(num_records, num_threads):
    """Estimate generation time based on historical performance"""
    base_rate = 800  # records per second per thread (conservative estimate)
    estimated_rate = base_rate * min(num_threads, 8)  # Diminishing returns after 8 threads
    estimated_seconds = num_records / estimated_rate
    return max(1, int(estimated_seconds))

@app.route('/api/task/<task_id>')
def get_task_status(task_id):
    """Get real-time task status"""
    task = progress_tracker.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Convert to dict for JSON serialization
    task_dict = {
        'task_id': task.task_id,
        'task_type': task.task_type.value,
        'status': task.status.value,
        'progress_percent': task.progress_percent,
        'current_step': task.current_step,
        'current_count': task.current_count,
        'total_count': task.total_count,
        'elapsed_time': task.elapsed_time,
        'estimated_remaining': task.estimated_remaining,
        'rate_per_second': task.rate_per_second,
        'error_message': task.error_message,
        'metadata': task.metadata
    }
    
    return jsonify(task_dict)

@app.route('/api/task/<task_id>/results')
def get_task_results(task_id):
    """Get completed task results"""
    task = progress_tracker.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task.status != TaskStatus.COMPLETED:
        return jsonify({'error': 'Task not completed yet'}), 400
    
    if task_id not in generation_tasks:
        return jsonify({'error': 'Results not available'}), 404
    
    task_data = generation_tasks[task_id]
    people = task_data['people']
    metadata = task_data['metadata']
    
    # Convert to preview format (first 100 records)
    people_data = []
    for person in people[:100]:
        person_dict = _convert_person_to_dict(person)
        people_data.append(person_dict)
    
    # Ensure metadata is JSON serializable
    serializable_metadata = _make_json_serializable(metadata)
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'total_records': len(people),
        'preview_data': people_data,
        'metadata': serializable_metadata,
        'validation_summary': _get_validation_summary(metadata.get('validation_results', []))
    })

def _make_json_serializable(obj):
    """Convert object to JSON serializable format"""
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Convert objects with __dict__ to dictionaries
        if hasattr(obj, 'model_dump'):
            # Pydantic model
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            # Pydantic model with old method
            return obj.dict()
        else:
            # Regular object
            return {k: _make_json_serializable(v) for k, v in obj.__dict__.items()}
    elif hasattr(obj, 'value'):
        # Enum values
        return obj.value
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Convert other types to string
        return str(obj)

def _convert_person_to_dict(person):
    """Convert person object to dictionary for API response"""
    person_dict = {
        'person_id': person.person_id,
        'ssn': person.ssn,
        'first_name': person.first_name,
        'middle_name': person.middle_name,
        'last_name': person.last_name,
        'date_of_birth': str(person.date_of_birth),
        'gender': person.gender.value if hasattr(person.gender, 'value') else person.gender,
        'addresses': [],
        'phone_numbers': [],
        'email_addresses': [],
        'employment_history': []
    }
    
    # Add current address
    current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
    if current_addr:
        person_dict['addresses'].append({
            'type': 'current',
            'full_address': f"{current_addr.street_1}, {current_addr.city}, {current_addr.state} {current_addr.zip_code}"
        })
    
    # Add primary phone
    primary_phone = next((p for p in person.phone_numbers if p.is_primary), None)
    if primary_phone:
        person_dict['phone_numbers'].append({
            'type': primary_phone.phone_type,
            'number': f"({primary_phone.area_code}) {primary_phone.number[:3]}-{primary_phone.number[3:]}"
        })
    
    # Add primary email
    primary_email = next((e for e in person.email_addresses if e.is_primary), None)
    if primary_email:
        person_dict['email_addresses'].append({
            'type': primary_email.email_type,
            'email': primary_email.email
        })
    
    # Add current employment
    current_job = next((e for e in person.employment_history if e.is_current), None)
    if current_job:
        person_dict['employment_history'].append({
            'employer': current_job.employer_name,
            'title': current_job.job_title,
            'industry': current_job.industry,
            'salary': current_job.salary
        })
    
    # Add enhanced profile summaries
    if person.financial_profile:
        person_dict['financial_profile'] = {
            'credit_score': person.financial_profile.credit_score,
            'annual_income': person.financial_profile.annual_income,
            'debt_to_income_ratio': person.financial_profile.debt_to_income_ratio
        }
    
    if person.physical_profile:
        person_dict['physical_profile'] = {
            'height': person.physical_profile.physical_characteristics.height_ft_in,
            'weight': f"{person.physical_profile.physical_characteristics.weight_lbs} lbs",
            'bmi': person.physical_profile.physical_characteristics.bmi,
            'eye_color': person.physical_profile.physical_characteristics.eye_color,
            'hair_color': person.physical_profile.physical_characteristics.hair_color,
            'ethnicity': person.physical_profile.physical_characteristics.ethnicity
        }
    
    if person.medical_profile:
        person_dict['medical_profile'] = {
            'blood_type': person.medical_profile.blood_type,
            'allergies': len(person.medical_profile.allergies),
            'conditions': len(person.medical_profile.conditions),
            'medications': len(person.medical_profile.medications)
        }
    
    if person.education_profile:
        highest_degree = max(person.education_profile.degrees, 
                           key=lambda d: ['High School Diploma', 'Certificate', 'Associate Degree', 
                                        'Bachelor\'s Degree', 'Master\'s Degree', 'Doctorate'].index(d.degree_type.value) 
                                        if d.degree_type.value in ['High School Diploma', 'Certificate', 'Associate Degree', 
                                                                 'Bachelor\'s Degree', 'Master\'s Degree', 'Doctorate'] else 0,
                           default=None)
        person_dict['education_profile'] = {
            'highest_degree': highest_degree.degree_type.value if highest_degree else 'Unknown',
            'major': highest_degree.major if highest_degree else None,
            'gpa': highest_degree.gpa if highest_degree else None
        }
    
    if person.vehicle_profile and person.vehicle_profile.vehicles:
        primary_vehicle = person.vehicle_profile.vehicles[0]
        person_dict['vehicle_profile'] = {
            'primary_vehicle': f"{primary_vehicle.year} {primary_vehicle.make} {primary_vehicle.model}",
            'total_vehicles': len(person.vehicle_profile.vehicles)
        }
    
    if person.online_presence:
        person_dict['online_presence'] = {
            'social_media_accounts': len(person.online_presence.social_media_accounts),
            'online_accounts': len(person.online_presence.online_accounts),
            'activity_level': person.online_presence.online_activity_level,
            'tech_savviness': person.online_presence.tech_savviness
        }
    
    if person.lifestyle_profile:
        person_dict['lifestyle_profile'] = {
            'lifestyle_category': person.lifestyle_profile.lifestyle_category.value,
            'primary_hobbies': person.lifestyle_profile.hobbies.primary_hobbies[:3],
            'personality_type': person.lifestyle_profile.personality_traits.myers_briggs_type,
            'values': person.lifestyle_profile.values.core_values[:3]
        }
    
    # Add new enhanced profiles
    if person.travel_profile:
        person_dict['travel_profile'] = {
            'total_trips': person.travel_profile.total_trips,
            'travel_frequency': person.travel_profile.travel_frequency,
            'travel_style': person.travel_profile.travel_style,
            'international_travel': person.travel_profile.international_travel,
            'recent_travels': len(person.travel_profile.recent_travels),
            'preferred_destinations': person.travel_profile.preferred_destinations[:3],
            'loyalty_programs': len(person.travel_profile.loyalty_programs)
        }
    
    if person.enhanced_financial_profile:
        person_dict['enhanced_financial_profile'] = {
            'total_assets': person.enhanced_financial_profile.total_assets,
            'total_liabilities': person.enhanced_financial_profile.total_liabilities,
            'net_worth': person.enhanced_financial_profile.net_worth,
            'monthly_income': person.enhanced_financial_profile.monthly_income,
            'monthly_expenses': person.enhanced_financial_profile.monthly_expenses,
            'cash_flow': person.enhanced_financial_profile.cash_flow,
            'bank_accounts': len(person.enhanced_financial_profile.bank_accounts),
            'transactions': len(person.enhanced_financial_profile.transactions),
            'investments': len(person.enhanced_financial_profile.investments),
            'loans': len(person.enhanced_financial_profile.loans),
            'credit_cards': len(person.enhanced_financial_profile.credit_cards),
            'risk_tolerance': person.enhanced_financial_profile.risk_tolerance
        }
    
    if person.communication_profile:
        person_dict['communication_profile'] = {
            'total_contacts': person.communication_profile.total_contacts,
            'active_contacts_30_days': person.communication_profile.active_contacts_30_days,
            'communication_records': len(person.communication_profile.communication_records),
            'daily_call_volume': person.communication_profile.communication_patterns.daily_call_volume,
            'daily_text_volume': person.communication_profile.communication_patterns.daily_text_volume,
            'daily_email_volume': person.communication_profile.communication_patterns.daily_email_volume,
            'response_time_minutes': person.communication_profile.communication_patterns.response_time_minutes,
            'communication_style': person.communication_profile.communication_patterns.communication_style,
            'emergency_contacts': len(person.communication_profile.emergency_contacts)
        }
    
    return person_dict

def _get_validation_summary(validation_results):
    """Generate validation summary from results"""
    if not validation_results:
        return {"status": "no_validation", "message": "Validation was not performed"}
    
    # Generate a simple summary since results are already serialized
    total_issues = len(validation_results)
    if total_issues == 0:
        return {
            "overall_status": "VALID",
            "total_issues": 0,
            "summary": "No validation issues found"
        }
    
    # Count by severity
    by_severity = {}
    critical_issues = []
    errors = []
    warnings = []
    
    for result in validation_results:
        severity = result.get('severity', 'unknown')
        by_severity[severity] = by_severity.get(severity, 0) + 1
        
        issue_info = {
            "field": result.get('field_name'),
            "message": result.get('message'),
            "suggested_fix": result.get('suggested_fix')
        }
        
        if severity == 'critical':
            critical_issues.append(issue_info)
        elif severity == 'error':
            errors.append(issue_info)
        else:
            warnings.append(issue_info)
    
    # Determine overall status
    has_critical_or_errors = any(result.get('severity') in ['critical', 'error'] for result in validation_results)
    overall_status = "INVALID" if has_critical_or_errors else "VALID_WITH_WARNINGS"
    
    return {
        "overall_status": overall_status,
        "total_issues": total_issues,
        "by_severity": by_severity,
        "critical_issues": critical_issues,
        "errors": errors,
        "warnings": warnings
    }

@app.route('/api/export/<task_id>/<format>')
def export_data(task_id, format):
    """Enhanced export with multiple formats"""
    if task_id not in generation_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_data = generation_tasks[task_id]
    people = task_data['people']
    metadata = task_data['metadata']
    
    try:
        if format == 'csv':
            return _export_csv(people, task_id, metadata)
        elif format == 'json':
            return _export_json(people, task_id, metadata)
        elif format == 'parquet':
            return _export_parquet(people, task_id, metadata)
        elif format == 'xml':
            return _export_xml(people, task_id, metadata)
        else:
            return jsonify({'error': 'Invalid format'}), 400
    
    except Exception as e:
        error_handler.handle_error(
            e, ErrorCategory.SERIALIZATION, ErrorSeverity.MEDIUM,
            context_data={'task_id': task_id, 'format': format}
        )
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

def _export_csv(people, task_id, metadata):
    """Export to enhanced CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Enhanced header with more fields
    writer.writerow([
        'person_id', 'ssn', 'first_name', 'middle_name', 'last_name',
        'date_of_birth', 'gender', 'address', 'city', 'state', 'zip_code',
        'phone', 'email', 'employer', 'job_title', 'salary', 'credit_score',
        'height', 'weight', 'eye_color', 'blood_type', 'highest_degree',
        'primary_vehicle', 'lifestyle_category', 'personality_type',
        'bmi', 'allergies_count', 'conditions_count', 'medications_count'
    ])
    
    # Write enhanced data
    for person in people:
        current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
        primary_phone = next((p for p in person.phone_numbers if p.is_primary), None)
        primary_email = next((e for e in person.email_addresses if e.is_primary), None)
        current_job = next((e for e in person.employment_history if e.is_current), None)
        
        # Enhanced data extraction
        height = person.physical_profile.physical_characteristics.height_ft_in if person.physical_profile else ''
        weight = f"{person.physical_profile.physical_characteristics.weight_lbs} lbs" if person.physical_profile else ''
        bmi = person.physical_profile.physical_characteristics.bmi if person.physical_profile else ''
        eye_color = person.physical_profile.physical_characteristics.eye_color if person.physical_profile else ''
        blood_type = person.medical_profile.blood_type if person.medical_profile else ''
        
        allergies_count = len(person.medical_profile.allergies) if person.medical_profile else 0
        conditions_count = len(person.medical_profile.conditions) if person.medical_profile else 0
        medications_count = len(person.medical_profile.medications) if person.medical_profile else 0
        
        highest_degree = ''
        if person.education_profile and person.education_profile.degrees:
            highest = max(person.education_profile.degrees, 
                        key=lambda d: ['High School Diploma', 'Certificate', 'Associate Degree', 
                                     'Bachelor\'s Degree', 'Master\'s Degree', 'Doctorate'].index(d.degree_type.value) 
                                     if d.degree_type.value in ['High School Diploma', 'Certificate', 'Associate Degree', 
                                                              'Bachelor\'s Degree', 'Master\'s Degree', 'Doctorate'] else 0,
                        default=None)
            highest_degree = highest.degree_type.value if highest else ''
        
        primary_vehicle = ''
        if person.vehicle_profile and person.vehicle_profile.vehicles:
            vehicle = person.vehicle_profile.vehicles[0]
            primary_vehicle = f"{vehicle.year} {vehicle.make} {vehicle.model}"
        
        lifestyle_category = person.lifestyle_profile.lifestyle_category.value if person.lifestyle_profile else ''
        personality_type = person.lifestyle_profile.personality_traits.myers_briggs_type if person.lifestyle_profile else ''
        
        writer.writerow([
            person.person_id, person.ssn, person.first_name, person.middle_name or '',
            person.last_name, person.date_of_birth,
            person.gender.value if hasattr(person.gender, 'value') else person.gender,
            current_addr.street_1 if current_addr else '',
            current_addr.city if current_addr else '',
            current_addr.state if current_addr else '',
            current_addr.zip_code if current_addr else '',
            f"({primary_phone.area_code}) {primary_phone.number[:3]}-{primary_phone.number[3:]}" if primary_phone else '',
            primary_email.email if primary_email else '',
            current_job.employer_name if current_job else '',
            current_job.job_title if current_job else '',
            current_job.salary if current_job else '',
            person.financial_profile.credit_score if person.financial_profile else '',
            height, weight, eye_color, blood_type, highest_degree,
            primary_vehicle, lifestyle_category, personality_type,
            bmi, allergies_count, conditions_count, medications_count
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'pii_data_enhanced_{task_id}.csv'
    )

def _convert_datetimes_to_strings(obj):
    """Recursively convert datetime objects to strings for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _convert_datetimes_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetimes_to_strings(item) for item in obj]
    else:
        return obj

def _export_json(people, task_id, metadata):
    """Export to enhanced JSON format"""
    json_data = {
        'metadata': metadata,
        'records': []
    }
    
    for person in people:
        if hasattr(person, 'model_dump'):
            person_dict = person.model_dump()
        elif hasattr(person, 'dict'):
            person_dict = person.dict()
        else:
            person_dict = person.__dict__
        
        # Convert all datetime objects recursively
        person_dict = _convert_datetimes_to_strings(person_dict)
        json_data['records'].append(person_dict)
    
    return send_file(
        io.BytesIO(json.dumps(json_data, indent=2).encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'pii_data_enhanced_{task_id}.json'
    )

def _export_parquet(people, task_id, metadata):
    """Export to Parquet format for analytics"""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
        
        # Convert to flat DataFrame
        records = []
        for person in people:
            record = _convert_person_to_dict(person)
            # Flatten nested structures
            flat_record = {}
            for key, value in record.items():
                if isinstance(value, list) and value:
                    if isinstance(value[0], dict):
                        # Take first item from lists of dicts
                        for sub_key, sub_value in value[0].items():
                            flat_record[f"{key}_{sub_key}"] = sub_value
                    else:
                        flat_record[f"{key}_count"] = len(value)
                        flat_record[f"{key}_first"] = value[0] if value else None
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_record[f"{key}_{sub_key}"] = sub_value
                else:
                    flat_record[key] = value
            records.append(flat_record)
        
        df = pd.DataFrame(records)
        
        # Write to parquet
        output = io.BytesIO()
        df.to_parquet(output, engine='pyarrow')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'pii_data_enhanced_{task_id}.parquet'
        )
    
    except ImportError:
        return jsonify({'error': 'Parquet export requires pyarrow package'}), 400

def _export_xml(people, task_id, metadata):
    """Export to XML format"""
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    
    root = Element('PII_Dataset')
    metadata_elem = SubElement(root, 'Metadata')
    for key, value in metadata.items():
        meta_item = SubElement(metadata_elem, key)
        meta_item.text = str(value)
    
    records_elem = SubElement(root, 'Records')
    
    for person in people[:1000]:  # Limit to 1000 for XML size
        person_elem = SubElement(records_elem, 'Person')
        person_dict = _convert_person_to_dict(person)
        
        for key, value in person_dict.items():
            elem = SubElement(person_elem, key)
            elem.text = str(value) if value is not None else ''
    
    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    return send_file(
        io.BytesIO(pretty_xml.encode()),
        mimetype='application/xml',
        as_attachment=True,
        download_name=f'pii_data_enhanced_{task_id}.xml'
    )

@app.route('/api/statistics/<task_id>')
def get_statistics(task_id):
    """Enhanced statistics with validation insights"""
    if task_id not in generation_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_data = generation_tasks[task_id]
    people = task_data['people']
    metadata = task_data['metadata']
    
    # Calculate enhanced statistics
    stats = _calculate_enhanced_statistics(people)
    
    # Add validation insights
    if metadata.get('validation_results'):
        stats['validation'] = _get_validation_summary(metadata['validation_results'])
    
    # Add generation metadata
    stats['generation_metadata'] = {
        'generation_time': metadata.get('generation_time'),
        'records_per_second': metadata.get('records_per_second'),
        'generated_at': metadata.get('generated_at'),
        'config': metadata.get('config')
    }
    
    return jsonify(stats)

def _calculate_enhanced_statistics(people):
    """Calculate comprehensive statistics"""
    stats = {
        'demographics': {
            'total_people': len(people),
            'gender_distribution': {},
            'age_distribution': {},
            'state_distribution': {},
            'ethnicity_distribution': {}
        },
        'employment': {
            'employment_rate': 0,
            'average_salary': 0,
            'industry_distribution': {},
            'top_employers': []
        },
        'financial': {
            'average_credit_score': 0,
            'credit_score_distribution': {},
            'income_distribution': {}
        },
        'health': {
            'blood_type_distribution': {},
            'average_allergies': 0,
            'common_conditions': {}
        },
        'data_quality': {
            'missing_ssn': 0,
            'missing_phone': 0,
            'missing_email': 0,
            'duplicate_ssn': 0
        }
    }
    
    # Enhanced demographic analysis
    current_year = datetime.now().year
    for person in people:
        # Gender distribution
        gender = person.gender.value if hasattr(person.gender, 'value') else person.gender
        stats['demographics']['gender_distribution'][gender] = stats['demographics']['gender_distribution'].get(gender, 0) + 1
        
        # Age distribution
        age = current_year - person.date_of_birth.year
        age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
        stats['demographics']['age_distribution'][age_group] = stats['demographics']['age_distribution'].get(age_group, 0) + 1
        
        # State distribution
        current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
        if current_addr:
            state = current_addr.state
            stats['demographics']['state_distribution'][state] = stats['demographics']['state_distribution'].get(state, 0) + 1
        
        # Ethnicity distribution
        if person.physical_profile:
            ethnicity = person.physical_profile.physical_characteristics.ethnicity
            stats['demographics']['ethnicity_distribution'][ethnicity] = stats['demographics']['ethnicity_distribution'].get(ethnicity, 0) + 1
        
        # Health statistics
        if person.medical_profile:
            blood_type = person.medical_profile.blood_type
            stats['health']['blood_type_distribution'][blood_type] = stats['health']['blood_type_distribution'].get(blood_type, 0) + 1
    
    # Calculate averages and rates
    employed_count = 0
    total_salary = 0
    salary_count = 0
    total_credit_score = 0
    credit_score_count = 0
    total_allergies = 0
    allergy_count = 0
    
    for person in people:
        # Employment statistics
        current_job = next((e for e in person.employment_history if e.is_current), None)
        if current_job:
            employed_count += 1
            if current_job.salary:
                total_salary += current_job.salary
                salary_count += 1
        
        # Financial statistics
        if person.financial_profile and person.financial_profile.credit_score:
            total_credit_score += person.financial_profile.credit_score
            credit_score_count += 1
        
        # Health statistics
        if person.medical_profile:
            total_allergies += len(person.medical_profile.allergies)
            allergy_count += 1
    
    # Calculate rates and averages
    stats['employment']['employment_rate'] = round((employed_count / len(people)) * 100, 2)
    if salary_count > 0:
        stats['employment']['average_salary'] = round(total_salary / salary_count, 2)
    if credit_score_count > 0:
        stats['financial']['average_credit_score'] = round(total_credit_score / credit_score_count)
    if allergy_count > 0:
        stats['health']['average_allergies'] = round(total_allergies / allergy_count, 2)
    
    return stats

@app.route('/api/system/status')
def system_status():
    """Get system status and health metrics"""
    active_tasks = progress_tracker.get_active_tasks()
    error_summary = error_handler.get_error_summary()
    
    return jsonify({
        'active_tasks': len(active_tasks),
        'total_tasks_in_memory': len(generation_tasks),
        'error_summary': error_summary,
        'system_health': 'healthy' if error_summary['total_errors'] == 0 else 'issues_detected'
    })

@app.route('/api/system/errors')
def get_error_log():
    """Get system error log"""
    return jsonify(error_handler.get_error_summary())

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to PII Generator'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    # WebSocket subscription not needed since we use polling

@socketio.on('subscribe_task')
def handle_subscribe_task(data):
    task_id = data.get('task_id')
    if task_id:
        # Just acknowledge - progress is tracked via polling
        emit('subscribed', {'task_id': task_id})

@socketio.on('unsubscribe_task')
def handle_unsubscribe_task(data):
    task_id = data.get('task_id')
    if task_id:
        # Just acknowledge - no actual subscription to remove
        emit('unsubscribed', {'task_id': task_id})

@socketio.on('join_progress')
def handle_join_progress():
    join_room('progress_updates')
    emit('joined_progress', {'message': 'Joined progress updates room'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    logger.info("Starting enhanced PII Generator with robust features")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)