#!/usr/bin/env python3
"""
Police Facial Recognition System
Advanced AI system for identifying missing persons and unidentified bodies
"""

import os
import sys
from face_recognition_system import FaceRecognitionSystem
from database import PoliceDatabase
from web_interface import app

def main():
    print("🚔 Police Facial Recognition System")
    print("=" * 50)
    print("Advanced AI System for Missing Persons & Unidentified Bodies")
    print("=" * 50)
    
    # Initialize system
    face_system = FaceRecognitionSystem()
    db = PoliceDatabase()
    
    while True:
        print("\n📋 Main Menu:")
        print("1. Start Web Interface")
        print("2. Add Missing Person (CLI)")
        print("3. Add Unidentified Body (CLI)")
        print("4. Search by Photo (CLI)")
        print("5. Find Automatic Matches")
        print("6. View Statistics")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            print("\n🌐 Starting Web Interface...")
            print("Access the system at: http://localhost:5000")
            print("Press Ctrl+C to stop the server")
            try:
                app.run(debug=False, host='0.0.0.0', port=5000)
            except KeyboardInterrupt:
                print("\n✅ Web server stopped")
        
        elif choice == '2':
            add_missing_person_cli(face_system)
        
        elif choice == '3':
            add_unidentified_body_cli(face_system)
        
        elif choice == '4':
            search_by_photo_cli(face_system)
        
        elif choice == '5':
            find_matches_cli(face_system)
        
        elif choice == '6':
            show_statistics(db)
        
        elif choice == '7':
            print("\n👋 Goodbye! Stay safe.")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

def add_missing_person_cli(face_system):
    print("\n➕ Add Missing Person")
    print("-" * 30)
    
    name = input("Full Name: ")
    age = int(input("Age: "))
    gender = input("Gender (Male/Female/Other): ")
    case_number = input("Case Number: ")
    last_seen_date = input("Last Seen Date (YYYY-MM-DD): ")
    last_seen_location = input("Last Seen Location: ")
    description = input("Description: ")
    photo_path = input("Photo Path: ")
    
    if not os.path.exists(photo_path):
        print("❌ Photo file not found!")
        return
    
    person_data = {
        'name': name,
        'age': age,
        'gender': gender,
        'case_number': case_number,
        'last_seen_date': last_seen_date,
        'last_seen_location': last_seen_location,
        'description': description
    }
    
    person_id = face_system.process_missing_person_photo(photo_path, person_data)
    
    if person_id:
        print(f"✅ Missing person added successfully with ID: {person_id}")
    else:
        print("❌ Error processing photo - no face detected")

def add_unidentified_body_cli(face_system):
    print("\n➕ Add Unidentified Body")
    print("-" * 30)
    
    case_number = input("Case Number: ")
    found_date = input("Found Date (YYYY-MM-DD): ")
    found_location = input("Found Location: ")
    estimated_age = int(input("Estimated Age: "))
    gender = input("Gender (Male/Female/Unknown): ")
    description = input("Description: ")
    photo_path = input("Photo Path: ")
    
    if not os.path.exists(photo_path):
        print("❌ Photo file not found!")
        return
    
    body_data = {
        'case_number': case_number,
        'found_date': found_date,
        'found_location': found_location,
        'estimated_age': estimated_age,
        'gender': gender,
        'description': description
    }
    
    body_id = face_system.process_unidentified_body_photo(photo_path, body_data)
    
    if body_id:
        print(f"✅ Unidentified body added successfully with ID: {body_id}")
    else:
        print("❌ Error processing photo - no face detected")

def search_by_photo_cli(face_system):
    print("\n🔍 Search by Photo")
    print("-" * 30)
    
    photo_path = input("Photo Path: ")
    
    if not os.path.exists(photo_path):
        print("❌ Photo file not found!")
        return
    
    threshold = float(input("Confidence Threshold (0.0-1.0, default 0.6): ") or 0.6)
    
    matches = face_system.search_by_photo(photo_path, threshold)
    
    if matches:
        print(f"\n🎯 Found {len(matches)} potential matches:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Type: {match['type']}")
            if 'name' in match:
                print(f"   Name: {match['name']}")
            print(f"   Case: {match['case_number']}")
            print(f"   Confidence: {match['confidence']:.2%}")
    else:
        print("❌ No matches found")

def find_matches_cli(face_system):
    print("\n🎯 Finding Automatic Matches")
    print("-" * 30)
    
    threshold = float(input("Confidence Threshold (0.0-1.0, default 0.7): ") or 0.7)
    
    matches = face_system.find_matches(threshold)
    
    if matches:
        print(f"\n✅ Found {len(matches)} potential matches:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Missing Person: {match['missing_person']}")
            print(f"   Missing Case: {match['missing_case']}")
            print(f"   Body Case: {match['body_case']}")
            print(f"   Found Location: {match['found_location']}")
            print(f"   Confidence: {match['confidence']:.2%}")
    else:
        print("❌ No matches found above threshold")

def show_statistics(db):
    print("\n📊 System Statistics")
    print("-" * 30)
    
    missing_persons = db.get_all_missing_persons()
    unidentified_bodies = db.get_all_unidentified_bodies()
    matches = db.get_matches(0.6)
    
    print(f"Missing Persons: {len(missing_persons)}")
    print(f"Unidentified Bodies: {len(unidentified_bodies)}")
    print(f"Potential Matches: {len(matches)}")

if __name__ == "__main__":
    main()