from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
from face_recognition_system import FaceRecognitionSystem
from database import PoliceDatabase
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'police_facial_recognition_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'missing_persons'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'unidentified_bodies'), exist_ok=True)

face_system = FaceRecognitionSystem()
db = PoliceDatabase()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_missing_person', methods=['GET', 'POST'])
def add_missing_person():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        last_seen_date = request.form['last_seen_date']
        last_seen_location = request.form['last_seen_location']
        description = request.form['description']
        case_number = request.form['case_number']
        
        # Handle file upload
        if 'photo' not in request.files:
            flash('No photo uploaded')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No photo selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'missing_persons', filename)
            file.save(filepath)
            
            # Process the photo
            person_data = {
                'name': name,
                'age': age,
                'gender': gender,
                'last_seen_date': last_seen_date,
                'last_seen_location': last_seen_location,
                'description': description,
                'case_number': case_number
            }
            
            person_id = face_system.process_missing_person_photo(filepath, person_data)
            
            if person_id:
                flash(f'Missing person {name} added successfully with ID: {person_id}')
                return redirect(url_for('view_missing_persons'))
            else:
                flash('Error processing photo - no face detected')
        else:
            flash('Invalid file type')
    
    return render_template('add_missing_person.html')

@app.route('/add_unidentified_body', methods=['GET', 'POST'])
def add_unidentified_body():
    if request.method == 'POST':
        case_number = request.form['case_number']
        found_date = request.form['found_date']
        found_location = request.form['found_location']
        estimated_age = int(request.form['estimated_age'])
        gender = request.form['gender']
        description = request.form['description']
        
        if 'photo' not in request.files:
            flash('No photo uploaded')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No photo selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'unidentified_bodies', filename)
            file.save(filepath)
            
            body_data = {
                'case_number': case_number,
                'found_date': found_date,
                'found_location': found_location,
                'estimated_age': estimated_age,
                'gender': gender,
                'description': description
            }
            
            body_id = face_system.process_unidentified_body_photo(filepath, body_data)
            
            if body_id:
                flash(f'Unidentified body case {case_number} added successfully with ID: {body_id}')
                return redirect(url_for('view_unidentified_bodies'))
            else:
                flash('Error processing photo - no face detected')
        else:
            flash('Invalid file type')
    
    return render_template('add_unidentified_body.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        try:
            if 'photo' not in request.files:
                flash('No photo uploaded')
                return redirect(request.url)
            
            file = request.files['photo']
            if file.filename == '':
                flash('No photo selected')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'search', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                threshold = float(request.form.get('threshold', 0.6))
                matches = face_system.search_by_photo(filepath, threshold)
                
                return render_template('search_results.html', matches=matches, query_image=filename)
            else:
                flash('Invalid file type')
        except Exception as e:
            flash(f'Error processing photo: {str(e)}')
            return redirect(request.url)
    
    return render_template('search.html')

@app.route('/find_matches')
def find_matches():
    threshold = float(request.args.get('threshold', 0.7))
    matches = face_system.find_matches(threshold)
    return render_template('matches.html', matches=matches)

@app.route('/view_missing_persons')
def view_missing_persons():
    missing_persons = db.get_all_missing_persons()
    return render_template('view_missing_persons.html', persons=missing_persons)

@app.route('/view_unidentified_bodies')
def view_unidentified_bodies():
    unidentified_bodies = db.get_all_unidentified_bodies()
    return render_template('view_unidentified_bodies.html', bodies=unidentified_bodies)

@app.route('/api/stats')
def api_stats():
    missing_count = len(db.get_all_missing_persons())
    bodies_count = len(db.get_all_unidentified_bodies())
    matches_count = len(db.get_matches(0.6))
    
    return jsonify({
        'missing_persons': missing_count,
        'unidentified_bodies': bodies_count,
        'potential_matches': matches_count
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)