#!/usr/bin/env python3
"""
PII Generator Web Application - Flask backend
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
import io
import os
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

# Import all model classes to ensure they're loaded before rebuilding
from src.generators.medical_generator import MedicalProfile
from src.generators.vehicle_generator import VehicleProfile  
from src.generators.education_generator import EducationProfile
from src.generators.social_generator import OnlinePresence
from src.generators.biometric_generator import PhysicalProfile
from src.generators.lifestyle_generator import LifestyleProfile

from src.core.models import GenerationConfig, DataQualityProfile, Person
from src.core.performance import PerformanceOptimizer
from src.generators.person_generator import PersonGenerator
from src.db.azure_sql import AzureSQLDatabase

# Import the rebuild function and execute it
from src.core.models import rebuild_person_model
rebuild_person_model()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pii-generator-secret-key'

# Global executor for background tasks
executor = ThreadPoolExecutor(max_workers=4)

# Store generation tasks
generation_tasks = {}

@app.route('/')
def index():
    """Render the main web interface"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_data():
    """Generate synthetic PII data"""
    try:
        data = request.json
        
        # Extract parameters
        num_records = data.get('records', 1000)
        variability_profile = data.get('variability_profile', 'realistic')
        num_threads = data.get('threads', 4)
        batch_size = data.get('batch_size', 1000)
        include_families = data.get('include_families', False)
        num_families = data.get('num_families', 0)
        
        # Create data quality profile based on selection
        profiles = {
            'minimal': DataQualityProfile(
                missing_data_rate=0.01,
                typo_rate=0.005,
                duplicate_rate=0.0001,
                outlier_rate=0.001,
                inconsistency_rate=0.01
            ),
            'realistic': DataQualityProfile(
                missing_data_rate=0.05,
                typo_rate=0.02,
                duplicate_rate=0.001,
                outlier_rate=0.01,
                inconsistency_rate=0.03
            ),
            'messy': DataQualityProfile(
                missing_data_rate=0.15,
                typo_rate=0.05,
                duplicate_rate=0.005,
                outlier_rate=0.03,
                inconsistency_rate=0.08
            ),
            'extreme': DataQualityProfile(
                missing_data_rate=0.25,
                typo_rate=0.10,
                duplicate_rate=0.01,
                outlier_rate=0.05,
                inconsistency_rate=0.15
            )
        }
        
        # Create generation config
        config = GenerationConfig(
            num_records=num_records,
            batch_size=batch_size,
            num_threads=num_threads,
            data_quality_profile=profiles[variability_profile]
        )
        
        # Initialize generators
        person_gen = PersonGenerator(config)
        performance_opt = PerformanceOptimizer(config)
        
        start_time = time.time()
        
        # Generate data
        all_people = []
        
        if include_families and num_families > 0:
            # Generate family clusters
            family_clusters = person_gen.create_family_clusters(num_families)
            all_people = [person for family in family_clusters for person in family]
            
            # Generate additional individual records if needed
            remaining = num_records - len(all_people)
            if remaining > 0:
                for batch in performance_opt.generate_parallel(
                    person_gen.generate_person, remaining, batch_size, num_threads
                ):
                    all_people.extend(batch)
        else:
            # Generate individual records
            for batch in performance_opt.generate_parallel(
                person_gen.generate_person, num_records, batch_size, num_threads
            ):
                all_people.extend(batch)
        
        elapsed = time.time() - start_time
        rate = len(all_people) / elapsed if elapsed > 0 else 0
        
        # Convert to JSON-serializable format
        people_data = []
        for person in all_people[:100]:  # Limit to first 100 for preview
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
            
            # Add financial profile
            if person.financial_profile:
                person_dict['financial_profile'] = {
                    'credit_score': person.financial_profile.credit_score,
                    'annual_income': person.financial_profile.annual_income,
                    'debt_to_income_ratio': person.financial_profile.debt_to_income_ratio
                }
            
            # Add physical characteristics
            if person.physical_profile:
                person_dict['physical_profile'] = {
                    'height': person.physical_profile.physical_characteristics.height_ft_in,
                    'weight': f"{person.physical_profile.physical_characteristics.weight_lbs} lbs",
                    'bmi': person.physical_profile.physical_characteristics.bmi,
                    'eye_color': person.physical_profile.physical_characteristics.eye_color,
                    'hair_color': person.physical_profile.physical_characteristics.hair_color,
                    'ethnicity': person.physical_profile.physical_characteristics.ethnicity
                }
            
            # Add medical profile highlights
            if person.medical_profile:
                person_dict['medical_profile'] = {
                    'blood_type': person.medical_profile.blood_type,
                    'allergies': len(person.medical_profile.allergies),
                    'conditions': len(person.medical_profile.conditions),
                    'medications': len(person.medical_profile.medications)
                }
            
            # Add education highlights
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
            
            # Add vehicle information
            if person.vehicle_profile and person.vehicle_profile.vehicles:
                primary_vehicle = person.vehicle_profile.vehicles[0]
                person_dict['vehicle_profile'] = {
                    'primary_vehicle': f"{primary_vehicle.year} {primary_vehicle.make} {primary_vehicle.model}",
                    'total_vehicles': len(person.vehicle_profile.vehicles)
                }
            
            # Add online presence highlights
            if person.online_presence:
                person_dict['online_presence'] = {
                    'social_media_accounts': len(person.online_presence.social_media_accounts),
                    'online_accounts': len(person.online_presence.online_accounts),
                    'activity_level': person.online_presence.online_activity_level,
                    'tech_savviness': person.online_presence.tech_savviness
                }
            
            # Add lifestyle highlights
            if person.lifestyle_profile:
                person_dict['lifestyle_profile'] = {
                    'lifestyle_category': person.lifestyle_profile.lifestyle_category.value,
                    'primary_hobbies': person.lifestyle_profile.hobbies.primary_hobbies[:3],  # Top 3
                    'personality_type': person.lifestyle_profile.personality_traits.myers_briggs_type,
                    'values': person.lifestyle_profile.values.core_values[:3]  # Top 3
                }
            
            people_data.append(person_dict)
        
        # Store full dataset in session for export
        task_id = str(int(time.time() * 1000))
        generation_tasks[task_id] = all_people
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'total_records': len(all_people),
            'generation_time': round(elapsed, 2),
            'records_per_second': round(rate),
            'preview_data': people_data,
            'statistics': {
                'total_people': len(all_people),
                'unique_addresses': len(set(a.address_id for p in all_people for a in p.addresses)),
                'unique_employers': len(set(e.employer_name for p in all_people for e in p.employment_history)),
                'average_addresses_per_person': round(sum(len(p.addresses) for p in all_people) / len(all_people), 2),
                'average_jobs_per_person': round(sum(len(p.employment_history) for p in all_people) / len(all_people), 2)
            }
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in generate_data: {error_trace}")  # Log to console
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace if app.debug else None
        }), 500

@app.route('/api/export/<task_id>/<format>')
def export_data(task_id, format):
    """Export generated data in various formats"""
    if task_id not in generation_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    people = generation_tasks[task_id]
    
    if format == 'csv':
        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'person_id', 'ssn', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'gender', 'address', 'city', 'state', 'zip_code',
            'phone', 'email', 'employer', 'job_title', 'salary', 'credit_score',
            'height', 'weight', 'eye_color', 'blood_type', 'highest_degree',
            'primary_vehicle', 'lifestyle_category', 'personality_type'
        ])
        
        # Write data
        for person in people:
            current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
            primary_phone = next((p for p in person.phone_numbers if p.is_primary), None)
            primary_email = next((e for e in person.email_addresses if e.is_primary), None)
            current_job = next((e for e in person.employment_history if e.is_current), None)
            
            # Extract additional data
            height = person.physical_profile.physical_characteristics.height_ft_in if person.physical_profile else ''
            weight = f"{person.physical_profile.physical_characteristics.weight_lbs} lbs" if person.physical_profile else ''
            eye_color = person.physical_profile.physical_characteristics.eye_color if person.physical_profile else ''
            blood_type = person.medical_profile.blood_type if person.medical_profile else ''
            
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
                person.person_id,
                person.ssn,
                person.first_name,
                person.middle_name or '',
                person.last_name,
                person.date_of_birth,
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
                height,
                weight,
                eye_color,
                blood_type,
                highest_degree,
                primary_vehicle,
                lifestyle_category,
                personality_type
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'pii_data_{task_id}.csv'
        )
    
    elif format == 'json':
        # Convert to JSON
        json_data = []
        for person in people:
            person_dict = person.dict()
            # Convert dates to strings
            person_dict['date_of_birth'] = str(person_dict['date_of_birth'])
            for addr in person_dict['addresses']:
                addr['effective_date'] = str(addr['effective_date'])
                if addr.get('end_date'):
                    addr['end_date'] = str(addr['end_date'])
            for emp in person_dict['employment_history']:
                emp['start_date'] = str(emp['start_date'])
                if emp.get('end_date'):
                    emp['end_date'] = str(emp['end_date'])
            json_data.append(person_dict)
        
        return send_file(
            io.BytesIO(json.dumps(json_data, indent=2).encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'pii_data_{task_id}.json'
        )
    
    else:
        return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/statistics/<task_id>')
def get_statistics(task_id):
    """Get detailed statistics for generated data"""
    if task_id not in generation_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    people = generation_tasks[task_id]
    
    # Calculate statistics
    stats = {
        'demographics': {
            'total_people': len(people),
            'gender_distribution': {},
            'age_distribution': {},
            'state_distribution': {}
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
        'data_quality': {
            'missing_ssn': 0,
            'missing_phone': 0,
            'missing_email': 0,
            'duplicate_ssn': 0
        }
    }
    
    # Gender distribution
    for person in people:
        gender = person.gender.value if hasattr(person.gender, 'value') else person.gender
        stats['demographics']['gender_distribution'][gender] = stats['demographics']['gender_distribution'].get(gender, 0) + 1
    
    # Age distribution
    current_year = datetime.now().year
    for person in people:
        age = current_year - person.date_of_birth.year
        age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
        stats['demographics']['age_distribution'][age_group] = stats['demographics']['age_distribution'].get(age_group, 0) + 1
    
    # State distribution
    for person in people:
        current_addr = next((a for a in person.addresses if a.address_type == "current"), None)
        if current_addr:
            state = current_addr.state
            stats['demographics']['state_distribution'][state] = stats['demographics']['state_distribution'].get(state, 0) + 1
    
    # Employment statistics
    employed_count = 0
    total_salary = 0
    salary_count = 0
    industry_count = {}
    employer_count = {}
    
    for person in people:
        current_job = next((e for e in person.employment_history if e.is_current), None)
        if current_job:
            employed_count += 1
            if current_job.salary:
                total_salary += current_job.salary
                salary_count += 1
            
            industry = current_job.industry
            industry_count[industry] = industry_count.get(industry, 0) + 1
            
            employer = current_job.employer_name
            employer_count[employer] = employer_count.get(employer, 0) + 1
    
    stats['employment']['employment_rate'] = round((employed_count / len(people)) * 100, 2)
    if salary_count > 0:
        stats['employment']['average_salary'] = round(total_salary / salary_count, 2)
    stats['employment']['industry_distribution'] = industry_count
    stats['employment']['top_employers'] = sorted(employer_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Financial statistics
    total_credit_score = 0
    credit_score_count = 0
    
    for person in people:
        if person.financial_profile and person.financial_profile.credit_score:
            score = person.financial_profile.credit_score
            total_credit_score += score
            credit_score_count += 1
            
            # Credit score ranges
            if score < 580:
                range_key = 'Poor (300-579)'
            elif score < 670:
                range_key = 'Fair (580-669)'
            elif score < 740:
                range_key = 'Good (670-739)'
            elif score < 800:
                range_key = 'Very Good (740-799)'
            else:
                range_key = 'Excellent (800-850)'
            
            stats['financial']['credit_score_distribution'][range_key] = stats['financial']['credit_score_distribution'].get(range_key, 0) + 1
    
    if credit_score_count > 0:
        stats['financial']['average_credit_score'] = round(total_credit_score / credit_score_count)
    
    # Data quality metrics
    ssn_set = set()
    for person in people:
        if not person.ssn:
            stats['data_quality']['missing_ssn'] += 1
        else:
            if person.ssn in ssn_set:
                stats['data_quality']['duplicate_ssn'] += 1
            ssn_set.add(person.ssn)
        
        if not person.phone_numbers:
            stats['data_quality']['missing_phone'] += 1
        
        if not person.email_addresses:
            stats['data_quality']['missing_email'] += 1
    
    return jsonify(stats)

@app.route('/api/cleanup/<task_id>', methods=['DELETE'])
def cleanup_task(task_id):
    """Clean up stored generation task"""
    if task_id in generation_tasks:
        del generation_tasks[task_id]
        return jsonify({'success': True})
    return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5001)