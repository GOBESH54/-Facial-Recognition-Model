#!/usr/bin/env python3
"""
Populate sample data for Police Facial Recognition System
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
import random

def generate_fake_face_encoding():
    """Generate a fake face encoding for demo purposes"""
    return np.random.rand(10000).astype(np.float32)

def populate_sample_data():
    """Add sample missing persons and unidentified bodies"""
    
    # Connect to database
    conn = sqlite3.connect('police_records.db')
    cursor = conn.cursor()
    
    # Sample missing persons data
    missing_persons = [
        {
            'name': 'Sarah Johnson',
            'age': 28,
            'gender': 'Female',
            'last_seen_date': '2024-01-15',
            'last_seen_location': 'Downtown Seattle, WA',
            'description': '5\'6", brown hair, blue eyes, wearing red jacket',
            'case_number': 'MP-2024-001'
        },
        {
            'name': 'Michael Rodriguez',
            'age': 34,
            'gender': 'Male',
            'last_seen_date': '2024-02-03',
            'last_seen_location': 'Portland, OR',
            'description': '6\'0", black hair, brown eyes, tattoo on left arm',
            'case_number': 'MP-2024-002'
        },
        {
            'name': 'Emily Chen',
            'age': 22,
            'gender': 'Female',
            'last_seen_date': '2024-01-28',
            'last_seen_location': 'University District, Seattle',
            'description': '5\'4", black hair, brown eyes, student at UW',
            'case_number': 'MP-2024-003'
        },
        {
            'name': 'David Thompson',
            'age': 45,
            'gender': 'Male',
            'last_seen_date': '2024-02-10',
            'last_seen_location': 'Spokane, WA',
            'description': '5\'10", gray hair, green eyes, beard',
            'case_number': 'MP-2024-004'
        },
        {
            'name': 'Lisa Martinez',
            'age': 31,
            'gender': 'Female',
            'last_seen_date': '2024-01-20',
            'last_seen_location': 'Tacoma, WA',
            'description': '5\'7", blonde hair, hazel eyes, scar on forehead',
            'case_number': 'MP-2024-005'
        }
    ]
    
    # Sample unidentified bodies data
    unidentified_bodies = [
        {
            'case_number': 'UB-2024-001',
            'found_date': '2024-02-15',
            'found_location': 'Green Lake Park, Seattle',
            'estimated_age': 30,
            'gender': 'Female',
            'description': 'Caucasian female, brown hair, approximately 5\'5"'
        },
        {
            'case_number': 'UB-2024-002',
            'found_date': '2024-02-08',
            'found_location': 'Columbia River, Portland',
            'estimated_age': 35,
            'gender': 'Male',
            'description': 'Hispanic male, black hair, approximately 6\'0"'
        },
        {
            'case_number': 'UB-2024-003',
            'found_date': '2024-02-01',
            'found_location': 'Discovery Park, Seattle',
            'estimated_age': 25,
            'gender': 'Female',
            'description': 'Asian female, black hair, approximately 5\'4"'
        },
        {
            'case_number': 'UB-2024-004',
            'found_date': '2024-02-12',
            'found_location': 'Riverfront Park, Spokane',
            'estimated_age': 45,
            'gender': 'Male',
            'description': 'Caucasian male, gray hair, approximately 5\'10"'
        }
    ]
    
    print("Adding sample missing persons...")
    for person in missing_persons:
        face_encoding = generate_fake_face_encoding()
        encoding_str = json.dumps(face_encoding.tolist())
        
        cursor.execute('''
            INSERT INTO missing_persons 
            (name, age, gender, last_seen_date, last_seen_location, description, 
             case_number, face_encoding, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (person['name'], person['age'], person['gender'], 
              person['last_seen_date'], person['last_seen_location'], 
              person['description'], person['case_number'], 
              encoding_str, f"sample_photos/{person['case_number']}.jpg"))
        
        print(f"Added: {person['name']} ({person['case_number']})")
    
    print("\nAdding sample unidentified bodies...")
    for body in unidentified_bodies:
        face_encoding = generate_fake_face_encoding()
        encoding_str = json.dumps(face_encoding.tolist())
        
        cursor.execute('''
            INSERT INTO unidentified_bodies 
            (case_number, found_date, found_location, estimated_age, gender, 
             description, face_encoding, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (body['case_number'], body['found_date'], body['found_location'],
              body['estimated_age'], body['gender'], body['description'],
              encoding_str, f"sample_photos/{body['case_number']}.jpg"))
        
        print(f"Added: {body['case_number']} - {body['gender']}, age {body['estimated_age']}")
    
    # Add some sample matches
    print("\nAdding sample potential matches...")
    sample_matches = [
        (1, 1, 0.85, "High confidence match - facial features align"),
        (3, 3, 0.72, "Probable match - age and location consistent"),
        (5, 4, 0.68, "Possible match - requires further investigation")
    ]
    
    for mp_id, ub_id, confidence, notes in sample_matches:
        cursor.execute('''
            INSERT INTO matches 
            (missing_person_id, unidentified_body_id, confidence_score, notes)
            VALUES (?, ?, ?, ?)
        ''', (mp_id, ub_id, confidence, notes))
        
        print(f"Added match: MP-ID {mp_id} <-> UB-ID {ub_id} ({confidence:.0%} confidence)")
    
    conn.commit()
    conn.close()
    
    print("\nSample data populated successfully!")
    print("\nDatabase now contains:")
    print("- 5 Missing Persons")
    print("- 4 Unidentified Bodies") 
    print("- 3 Potential Matches")
    print("\nYou can now test the system with this sample data.")

if __name__ == "__main__":
    print("Police Facial Recognition System - Sample Data Populator")
    print("=" * 60)
    
    # Initialize database first
    from database import PoliceDatabase
    db = PoliceDatabase()
    
    populate_sample_data()