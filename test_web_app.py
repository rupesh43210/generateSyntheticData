#!/usr/bin/env python3
"""Test script for the web application"""

import requests
import json
import time

def test_web_app():
    base_url = "http://localhost:8080"
    
    print("Testing web application...")
    
    # Test system status
    try:
        response = requests.get(f"{base_url}/api/system/status", timeout=5)
        if response.status_code == 200:
            print("✅ System status endpoint working")
        else:
            print(f"❌ System status failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to web app: {e}")
        return
    
    # Test data generation
    generation_request = {
        "records": 2,
        "variability_profile": "realistic",
        "threads": 1,
        "batch_size": 2,
        "enable_validation": True,
        "include_families": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=generation_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                task_id = result.get("task_id")
                print(f"✅ Generation started with task ID: {task_id}")
                
                # Wait for completion and check results
                time.sleep(5)  # Give it some time to process
                
                task_response = requests.get(f"{base_url}/api/task/{task_id}", timeout=10)
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    print(f"✅ Task status: {task_data.get('status')}")
                    
                    if task_data.get('status') == 'completed':
                        results_response = requests.get(f"{base_url}/api/task/{task_id}/results", timeout=10)
                        if results_response.status_code == 200:
                            results = results_response.json()
                            print(f"✅ Generated {results.get('total_records')} records successfully!")
                            
                            # Check if preview data contains new fields
                            preview_data = results.get('preview_data', [])
                            if preview_data:
                                person = preview_data[0]
                                new_fields = []
                                if 'travel_profile' in person:
                                    new_fields.append('travel_profile')
                                if 'enhanced_financial_profile' in person:
                                    new_fields.append('enhanced_financial_profile')
                                if 'communication_profile' in person:
                                    new_fields.append('communication_profile')
                                
                                if new_fields:
                                    print(f"✅ New enhanced fields present: {', '.join(new_fields)}")
                                else:
                                    print("⚠️ New enhanced fields not found in preview data")
                        else:
                            print(f"❌ Failed to get results: {results_response.status_code}")
                    else:
                        print(f"⚠️ Task not completed yet: {task_data.get('status')}")
                else:
                    print(f"❌ Failed to get task status: {task_response.status_code}")
            else:
                print(f"❌ Generation failed: {result.get('error')}")
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Generation test failed: {e}")

if __name__ == "__main__":
    test_web_app()