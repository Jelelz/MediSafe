from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from pymongo import MongoClient
import hashlib
import urllib.parse

# Creating a new Flask app for MediSafe
app: Flask = Flask(__name__)

# Escape the username and password
username = urllib.parse.quote_plus("faithkimokiy")
password = urllib.parse.quote_plus("Winner2001")

# Creating a Mongodb connection
client = MongoClient(
    "mongodb+srv://{}:{}@ehr.sihily9.mongodb.net/?retryWrites=true&w=majority".format(username, password))
db = client["ehr"]
collection = db['patient_record']


# a new blockchain function to store the data in blockchain format
def blockchain(data):
    # Generating a hash of the data.
    hash1 = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()

    # Storing the hash of the data in MongoDB.
    collection.insert_one({
        'hash': hash1
    })


# a new registration function to get the patient's data from the registration form.
def registration(name, gender, email, password, previous_records, allergies, insurance_provider):
    # Create a new data object.
    data = {
        'name': name,
        'gender': gender,
        'email': email,
        'password': password,
        'previous_records': previous_records,
        'allergies': allergies,
        'insurance_provider': insurance_provider
    }

    # To store the data in blockchain format
    blockchain(data)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.args.get('name')
    gender = request.args.get('gender')
    email = request.args.get('email')
    password = request.args.get('password')
    previous_records = request.args.get('previous_records')
    allergies = request.args.get('allergies')
    insurance_provider = request.args.get('insurance_provider')

    # Registering the patient.
    registration(name, gender, email, password, previous_records, allergies, insurance_provider)

    # Return a success message.
    return jsonify({'success': True})


@app.route('/patient_auth', methods=['GET', 'POST'])
def patient_auth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find the user record in the database.
        user = collection.find_one({'email': email})

        # Check if the user exists and the password is correct.
        if user and user['password'] == password:
            # Retrieve the EHR record from MongoDB
            ehr_record = collection.find_one({'hash': user['hash']})

            # Return the EHR record to the user
            return jsonify({'ehr_record': ehr_record})
        else:
            # User not found or password incorrect, display error message
            return jsonify({'error': 'Invalid email or password'})
    else:
        return render_template('patient_auth.html')


# Define a list of registered patients
registered_patients = [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"},
    {"id": 3, "name": "Peter Jones"},
]

# Define a dictionary to store patient medical records
patient_records = {
    1: {"medical_history": "Lorem ipsum dolor sit amet"},
    2: {"medical_history": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua"},
    3: {
        "medical_history": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"},
}


# Route for the physician app
@app.route('/physician', methods=['GET', 'POST'])
def physician_app():
    if request.method == 'POST':
        patient_id = int(request.form['patient_id'])

        # Check if the patient is registered
        if patient_id in patient_records:
            # Grant access to the patient's medical record
            return redirect(url_for('physician_view', patient_id=patient_id))
        else:
            error_message = "Patient not found"
            return render_template('physician.html', registered_patients=registered_patients,
                                   error_message=error_message)

    return render_template('physician.html', registered_patients=registered_patients)


# Route for viewing a patient's medical record
@app.route('/physician_view/<int:patient_id>')
def view_records(patient_id):
    # Retrieve the patient's medical record
    medical_history = patient_records[patient_id]['medical_history']

    return render_template('physician_view.html', patient_id=patient_id, medical_history=medical_history)


@app.route('/records')
def records():
    return render_template('records.html')


if __name__ == "__main__":
    app.run(debug=True)
