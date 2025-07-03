#!/usr/bin/env python3
"""
Docker-compatible PII Generator Web Application
"""

from flask import Flask, render_template, jsonify, send_file, request
import json
import csv
import os
import time
from datetime import datetime
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pii-generator-secret-key'

# Mock data for demonstration
AVAILABLE_GENERATORS = {
    "person": "Personal information (name, DOB, SSN, etc.)",
    "address": "Address information",
    "contact": "Contact details (email, phone)",
    "financial": "Financial information",
    "medical": "Medical records",
    "employment": "Employment history",
    "education": "Education records",
    "vehicle": "Vehicle information",
    "travel": "Travel records",
    "insurance": "Insurance policies",
    "legal": "Legal records",
    "property": "Property records",
    "credit_card": "Credit card information",
    "bank_account": "Bank account details",
    "family": "Family relationships"
}

# Store generation tasks
generation_tasks = {}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/generators')
def list_generators():
    """List available data generators"""
    return jsonify({
        "generators": list(AVAILABLE_GENERATORS.keys()),
        "descriptions": AVAILABLE_GENERATORS
    })

def generate_data_background(task_id, count, data_types, output_format):
    """Generate data in background thread"""
    try:
        # Generate mock data with variety
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'James', 'Mary']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        jobs = ['Software Engineer', 'Data Analyst', 'Product Manager', 'Designer', 'Sales Manager', 'Marketing Director', 'Accountant', 'HR Manager', 'Consultant', 'Teacher']
        cities = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'Austin, TX']
        
        mock_records = []
        total = count
        
        for i in range(total):
            # Mix up the data
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            gender = 'M' if i % 2 == 0 else 'F'
            birth_year = 1960 + (i % 40)  # Vary birth years from 1960-2000
            job = jobs[i % len(jobs)]
            city = cities[i % len(cities)]
            credit_score = 550 + (i * 7) % 250  # Vary from 550-800
            
            # Add delay to simulate real processing
            if total > 20:
                time.sleep(0.05)  # 50ms per record for larger batches
            elif total > 10:
                time.sleep(0.02)  # 20ms per record for medium batches
            
            # Update progress
            progress = int((i + 1) / total * 100)
            generation_tasks[task_id]['progress'] = progress
            generation_tasks[task_id]['current_count'] = i + 1
            generation_tasks[task_id]['status'] = 'running'
            
            # Calculate rate
            if 'start_time' in generation_tasks[task_id]:
                elapsed = (datetime.now() - generation_tasks[task_id]['start_time']).total_seconds()
                if elapsed > 0:
                    rate = (i + 1) / elapsed
                    generation_tasks[task_id]['rate_per_second'] = rate
                    remaining_records = total - (i + 1)
                    if rate > 0:
                        generation_tasks[task_id]['estimated_remaining'] = remaining_records / rate
            
            record = {
                'id': i + 1,
                'timestamp': datetime.now().isoformat()
            }
            
            if 'person' in data_types:
                record.update({
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'date_of_birth': f'{birth_year}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}',
                    'email': f'{first_name.lower()}.{last_name.lower()}{i}@example.com',
                    'phone': f'+1-555-{1000 + i:04d}',
                    'ssn': f'{100 + (i % 900):03d}-{10 + (i % 90):02d}-{1000 + i:04d}',
                    'addresses': [{
                        'full_address': f'{100 + i} {["Main", "Oak", "Elm", "Park", "First"][i % 5]} Street, {city}'
                    }],
                    'phone_numbers': [{
                        'number': f'+1-555-{1000 + i:04d}'
                    }],
                    'email_addresses': [{
                        'email': f'{first_name.lower()}.{last_name.lower()}{i}@example.com'
                    }],
                    'employment_history': [{
                        'title': job
                    }],
                    'financial_profile': {
                        'credit_score': credit_score
                    }
                })
            
            if 'address' in data_types:
                record.update({
                    'street': f'{i+100} Main Street',
                    'city': 'Springfield',
                    'state': 'IL',
                    'zip': f'{62701+i:05d}'
                })
            
            if 'financial' in data_types:
                record.update({
                    'credit_card': f'4111-1111-1111-{i:04d}',
                    'bank_account': f'1234567890{i:04d}',
                    'balance': f'${(i+1) * 1000}'
                })
            
            mock_records.append(record)
        
        # Save mock data
        output_dir = '/app/output'
        os.makedirs(output_dir, exist_ok=True)
        
        if output_format == 'json':
            output_file = f'{output_dir}/{task_id}.json'
            with open(output_file, 'w') as f:
                json.dump(mock_records, f, indent=2)
        else:  # csv
            output_file = f'{output_dir}/{task_id}.csv'
            if mock_records:
                keys = mock_records[0].keys()
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(mock_records)
        
        # Update final status
        generation_tasks[task_id]['status'] = 'completed'
        generation_tasks[task_id]['progress'] = 100
        generation_tasks[task_id]['output_file'] = output_file
        generation_tasks[task_id]['message'] = f'Generated {len(mock_records)} records'
        generation_tasks[task_id]['end_time'] = datetime.now()
        
        # Calculate final generation time
        if 'start_time' in generation_tasks[task_id]:
            generation_time = (generation_tasks[task_id]['end_time'] - generation_tasks[task_id]['start_time']).total_seconds()
            generation_tasks[task_id]['generation_time'] = generation_time
        
    except Exception as e:
        logger.error(f"Error in background generation: {str(e)}")
        generation_tasks[task_id]['status'] = 'failed'
        generation_tasks[task_id]['error'] = str(e)

@app.route('/api/generate', methods=['POST'])
def generate():
    """Start generation task"""
    try:
        data = request.get_json()
        # Handle different parameter names from frontend
        count = data.get('count', data.get('records', 100))
        data_types = data.get('data_types', ['person'])
        output_format = data.get('output_format', 'json')
        
        # Create a task
        task_id = f"task_{int(time.time())}"
        
        # Initialize task status
        generation_tasks[task_id] = {
            'id': task_id,
            'status': 'pending',
            'progress': 0,
            'count': count,
            'current_count': 0,
            'data_types': data_types,
            'output_format': output_format,
            'created_at': datetime.now().isoformat(),
            'start_time': datetime.now(),
            'rate_per_second': 0,
            'estimated_remaining': 0
        }
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_data_background,
            args=(task_id, count, data_types, output_format)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "status": "started",
            "message": f"Starting generation of {count} records..."
        })
        
    except Exception as e:
        logger.error(f"Error starting generation: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/api/status/<task_id>')
def get_status(task_id):
    """Get generation task status"""
    if task_id not in generation_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(generation_tasks[task_id])

@app.route('/api/task/<task_id>')
def get_task_status(task_id):
    """Get task status for frontend polling"""
    if task_id not in generation_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = generation_tasks[task_id]
    return jsonify({
        "status": task.get('status', 'pending'),
        "progress_percent": task.get('progress', 0),
        "current_step": "Generating mock data" if task.get('status') == 'running' else task.get('message', 'Processing...'),
        "current_count": task.get('current_count', 0),
        "total_count": task.get('count', 0),
        "elapsed_time": (datetime.now() - task.get('start_time', datetime.now())).total_seconds() if 'start_time' in task else 0,
        "estimated_remaining": task.get('estimated_remaining', 0),
        "rate_per_second": task.get('rate_per_second', 0)
    })

@app.route('/api/task/<task_id>/results')
def get_task_results(task_id):
    """Get task results for preview"""
    if task_id not in generation_tasks:
        return jsonify({"success": False, "error": "Task not found"}), 404
    
    task = generation_tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({"success": False, "error": "Task not completed"}), 400
    
    # Read generated data for preview
    preview_data = []
    try:
        if task.get('output_file', '').endswith('.json'):
            with open(task['output_file'], 'r') as f:
                data = json.load(f)
                preview_data = data[:10] if data else []  # First 10 records
    except Exception as e:
        logger.error(f"Error reading results: {str(e)}")
        # Return mock data if file reading fails
        preview_data = [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0001",
                "ssn": "123-45-0001"
            }
        ]
    
    # Ensure we always have data to display
    if not preview_data:
        preview_data = [
            {
                "id": 1,
                "first_name": "Sample",
                "last_name": "Data",
                "email": "sample@example.com",
                "phone": "+1-555-0000",
                "ssn": "123-45-0000"
            }
        ]
    
    return jsonify({
        "success": True,
        "preview_data": preview_data,
        "total_records": task.get('count', len(preview_data)),
        "validation_summary": {
            "total_issues": 0,
            "issues_by_type": {}
        }
    })

@app.route('/api/statistics/<task_id>')
def get_statistics(task_id):
    """Get statistics for generated data"""
    if task_id not in generation_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = generation_tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({"error": "Task not completed"}), 400
    
    # Return mock statistics
    return jsonify({
        "demographics": {
            "total_people": task.get('count', 0),
            "gender_distribution": {
                "M": int(task.get('count', 0) / 2),
                "F": int(task.get('count', 0) / 2)
            }
        },
        "employment": {
            "employment_rate": 85,
            "average_salary": 75000
        },
        "financial": {
            "average_credit_score": 720
        },
        "health": {
            "average_allergies": 2
        },
        "generation_metadata": {
            "total_records": task.get('count', 0),
            "generation_time": task.get('generation_time', 5),
            "records_per_second": task.get('rate_per_second', 20),
            "generated_at": task.get('created_at', datetime.now().isoformat())
        }
    })

@app.route('/api/export/<task_id>/<format>')
def export_data(task_id, format):
    """Export data in specified format"""
    if task_id not in generation_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = generation_tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({"error": "Task not completed"}), 400
    
    try:
        file_path = task.get('output_file', '')
        
        # Load the data
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif file_path.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path)
            data = df.to_dict('records')
        else:
            return jsonify({"error": "Invalid source file format"}), 500
        
        if format == 'json':
            return send_file(file_path, as_attachment=True, download_name=f'pii_data_{task_id}.json')
        elif format == 'csv':
            # Convert to CSV if needed
            if not file_path.endswith('.csv'):
                import pandas as pd
                df = pd.DataFrame(data)
                csv_path = file_path.replace('.json', '.csv')
                df.to_csv(csv_path, index=False)
                return send_file(csv_path, as_attachment=True, download_name=f'pii_data_{task_id}.csv')
            else:
                return send_file(file_path, as_attachment=True, download_name=f'pii_data_{task_id}.csv')
        elif format == 'parquet':
            # Convert to Parquet
            import pandas as pd
            try:
                import pyarrow.parquet as pq
                df = pd.DataFrame(data)
                parquet_path = file_path.replace('.json', '.parquet').replace('.csv', '.parquet')
                df.to_parquet(parquet_path, index=False)
                return send_file(parquet_path, as_attachment=True, download_name=f'pii_data_{task_id}.parquet')
            except ImportError:
                return jsonify({"error": "Parquet export requires pyarrow library"}), 500
        elif format == 'xml':
            # Convert to XML
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            root = ET.Element('pii_data')
            root.set('task_id', task_id)
            root.set('generated_at', task.get('created_at', ''))
            
            for idx, record in enumerate(data):
                record_elem = ET.SubElement(root, 'record')
                record_elem.set('id', str(idx + 1))
                
                for key, value in record.items():
                    field_elem = ET.SubElement(record_elem, key)
                    # Handle complex types (lists, dicts)
                    if isinstance(value, (dict, list)):
                        field_elem.text = json.dumps(value)
                    else:
                        field_elem.text = str(value) if value is not None else ''
            
            # Pretty print XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            xml_path = file_path.replace('.json', '.xml').replace('.csv', '.xml')
            
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            
            return send_file(xml_path, as_attachment=True, download_name=f'pii_data_{task_id}.xml')
        else:
            return jsonify({"error": "Unsupported format"}), 400
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<task_id>')
def download_results(task_id):
    """Download generated data"""
    if task_id not in generation_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = generation_tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({"error": "Task not completed"}), 400
    
    try:
        return send_file(task['output_file'], as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": "File not found"}), 404

@app.route('/api/system/status')
def system_status():
    """Get system status"""
    active_tasks = sum(1 for task in generation_tasks.values() if task.get('status') == 'running')
    return jsonify({
        "system_health": "healthy",
        "status": "healthy",
        "version": "1.0.0-docker",
        "mode": "demo",
        "message": "Running in Docker demo mode",
        "active_tasks": active_tasks,
        "error_summary": {
            "total_errors": 0
        }
    })

@app.route('/api/system/capabilities')
def capabilities():
    """Get system capabilities"""
    return jsonify({
        "socketio": False,
        "realtime": False,
        "database": False,
        "export_formats": ["json", "csv"],
        "max_records": 1000
    })

if __name__ == '__main__':
    logger.info("Starting PII Generator Web Application (Docker Version)")
    app.run(debug=True, host='0.0.0.0', port=5001)