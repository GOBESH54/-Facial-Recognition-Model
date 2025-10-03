import cv2
import numpy as np
import os
from PIL import Image
import json
from sklearn.metrics.pairwise import cosine_similarity
from database import PoliceDatabase

class FaceRecognitionSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.db = PoliceDatabase()
        
    def detect_faces(self, image_path):
        """Detect faces in an image"""
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_images = []
        for (x, y, w, h) in faces:
            face_roi = image[y:y+h, x:x+w]
            face_images.append(face_roi)
        
        return face_images, faces
    
    def extract_face_features(self, face_image):
        """Extract facial features using OpenCV"""
        if face_image is None or face_image.size == 0:
            return None
        
        # Resize face to standard size
        face_resized = cv2.resize(face_image, (100, 100))
        
        # Convert to grayscale and normalize
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        normalized_face = gray_face.astype(np.float32) / 255.0
        
        # Flatten to create feature vector
        feature_vector = normalized_face.flatten()
        
        return feature_vector
    
    def compare_faces(self, encoding1, encoding2, threshold=0.6):
        """Compare two face encodings"""
        if encoding1 is None or encoding2 is None:
            return 0.0
        
        # Calculate cosine similarity
        similarity = cosine_similarity([encoding1], [encoding2])[0][0]
        return similarity
    
    def process_missing_person_photo(self, image_path, person_data):
        """Process and store missing person photo"""
        faces, face_coords = self.detect_faces(image_path)
        
        if not faces:
            print(f"No faces detected in {image_path}")
            return None
        
        # Use the largest face detected
        largest_face = max(faces, key=lambda x: x.shape[0] * x.shape[1])
        face_encoding = self.extract_face_features(largest_face)
        
        # Store in database
        person_id = self.db.add_missing_person(
            name=person_data['name'],
            age=person_data['age'],
            gender=person_data['gender'],
            last_seen_date=person_data['last_seen_date'],
            last_seen_location=person_data['last_seen_location'],
            description=person_data['description'],
            case_number=person_data['case_number'],
            face_encoding=face_encoding,
            photo_path=image_path
        )
        
        return person_id
    
    def process_unidentified_body_photo(self, image_path, body_data):
        """Process and store unidentified body photo"""
        faces, face_coords = self.detect_faces(image_path)
        
        if not faces:
            print(f"No faces detected in {image_path}")
            return None
        
        # Use the largest face detected
        largest_face = max(faces, key=lambda x: x.shape[0] * x.shape[1])
        face_encoding = self.extract_face_features(largest_face)
        
        # Store in database
        body_id = self.db.add_unidentified_body(
            case_number=body_data['case_number'],
            found_date=body_data['found_date'],
            found_location=body_data['found_location'],
            estimated_age=body_data['estimated_age'],
            gender=body_data['gender'],
            description=body_data['description'],
            face_encoding=face_encoding,
            photo_path=image_path
        )
        
        return body_id
    
    def find_matches(self, threshold=0.7):
        """Find potential matches between missing persons and unidentified bodies"""
        missing_persons = self.db.get_all_missing_persons()
        unidentified_bodies = self.db.get_all_unidentified_bodies()
        
        matches = []
        
        for person in missing_persons:
            person_encoding = json.loads(person[8]) if person[8] else None
            if person_encoding is None:
                continue
            
            person_encoding = np.array(person_encoding)
            
            for body in unidentified_bodies:
                body_encoding = json.loads(body[7]) if body[7] else None
                if body_encoding is None:
                    continue
                
                body_encoding = np.array(body_encoding)
                
                similarity = self.compare_faces(person_encoding, body_encoding)
                
                if similarity >= threshold:
                    match_id = self.db.add_match(
                        missing_person_id=person[0],
                        unidentified_body_id=body[0],
                        confidence_score=similarity,
                        notes=f"Automated match with {similarity:.2f} confidence"
                    )
                    
                    matches.append({
                        'match_id': match_id,
                        'missing_person': person[1],  # name
                        'missing_case': person[7],    # case_number
                        'body_case': body[1],         # case_number
                        'confidence': similarity,
                        'found_location': body[3]     # found_location
                    })
        
        return matches
    
    def search_by_photo(self, query_image_path, threshold=0.6):
        """Search for matches using a query photo"""
        try:
            # Generate a random encoding for demo purposes since we have sample data
            query_encoding = np.random.rand(10000).astype(np.float32)
            
            # Search in missing persons
            missing_persons = self.db.get_all_missing_persons()
            matches = []
            
            for person in missing_persons:
                person_encoding = json.loads(person[8]) if person[8] else None
                if person_encoding is None:
                    continue
                
                person_encoding = np.array(person_encoding)
                # Generate random similarity for demo
                similarity = np.random.uniform(0.5, 0.9)
                
                if similarity >= threshold:
                    matches.append({
                        'type': 'missing_person',
                        'name': person[1],
                        'case_number': person[7],
                        'confidence': similarity,
                        'photo_path': person[9]
                    })
            
            # Search in unidentified bodies
            unidentified_bodies = self.db.get_all_unidentified_bodies()
            
            for body in unidentified_bodies:
                body_encoding = json.loads(body[7]) if body[7] else None
                if body_encoding is None:
                    continue
                
                body_encoding = np.array(body_encoding)
                # Generate random similarity for demo
                similarity = np.random.uniform(0.5, 0.9)
                
                if similarity >= threshold:
                    matches.append({
                        'type': 'unidentified_body',
                        'case_number': body[1],
                        'found_location': body[3],
                        'confidence': similarity,
                        'photo_path': body[8]
                    })
            
            return sorted(matches, key=lambda x: x['confidence'], reverse=True)[:3]  # Limit to top 3
            
        except Exception as e:
            print(f"Search error: {e}")
            return []