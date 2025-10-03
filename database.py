import sqlite3
import os
import json
from datetime import datetime
import numpy as np

class PoliceDatabase:
    def __init__(self, db_path="police_records.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Missing persons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missing_persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                last_seen_date TEXT,
                last_seen_location TEXT,
                description TEXT,
                case_number TEXT UNIQUE,
                face_encoding TEXT,
                photo_path TEXT,
                status TEXT DEFAULT 'MISSING',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Unidentified bodies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unidentified_bodies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE,
                found_date TEXT,
                found_location TEXT,
                estimated_age INTEGER,
                gender TEXT,
                description TEXT,
                face_encoding TEXT,
                photo_path TEXT,
                status TEXT DEFAULT 'UNIDENTIFIED',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                missing_person_id INTEGER,
                unidentified_body_id INTEGER,
                confidence_score REAL,
                match_date TEXT DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                FOREIGN KEY (missing_person_id) REFERENCES missing_persons (id),
                FOREIGN KEY (unidentified_body_id) REFERENCES unidentified_bodies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_missing_person(self, name, age, gender, last_seen_date, last_seen_location, 
                          description, case_number, face_encoding, photo_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encoding_str = json.dumps(face_encoding.tolist()) if face_encoding is not None else None
        
        cursor.execute('''
            INSERT INTO missing_persons 
            (name, age, gender, last_seen_date, last_seen_location, description, 
             case_number, face_encoding, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, last_seen_date, last_seen_location, description, 
              case_number, encoding_str, photo_path))
        
        conn.commit()
        person_id = cursor.lastrowid
        conn.close()
        return person_id
    
    def add_unidentified_body(self, case_number, found_date, found_location, 
                             estimated_age, gender, description, face_encoding, photo_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encoding_str = json.dumps(face_encoding.tolist()) if face_encoding is not None else None
        
        cursor.execute('''
            INSERT INTO unidentified_bodies 
            (case_number, found_date, found_location, estimated_age, gender, 
             description, face_encoding, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (case_number, found_date, found_location, estimated_age, gender, 
              description, encoding_str, photo_path))
        
        conn.commit()
        body_id = cursor.lastrowid
        conn.close()
        return body_id
    
    def get_all_missing_persons(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM missing_persons WHERE status = "MISSING"')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_unidentified_bodies(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM unidentified_bodies WHERE status = "UNIDENTIFIED"')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_match(self, missing_person_id, unidentified_body_id, confidence_score, notes=""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO matches 
            (missing_person_id, unidentified_body_id, confidence_score, notes)
            VALUES (?, ?, ?, ?)
        ''', (missing_person_id, unidentified_body_id, confidence_score, notes))
        
        conn.commit()
        match_id = cursor.lastrowid
        conn.close()
        return match_id
    
    def get_matches(self, threshold=0.6):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, mp.name, mp.case_number as mp_case, 
                   ub.case_number as ub_case, ub.found_location
            FROM matches m
            JOIN missing_persons mp ON m.missing_person_id = mp.id
            JOIN unidentified_bodies ub ON m.unidentified_body_id = ub.id
            WHERE m.confidence_score >= ?
            ORDER BY m.confidence_score DESC
        ''', (threshold,))
        
        results = cursor.fetchall()
        conn.close()
        return results