from flask import Flask, render_template, request, jsonify
import json
from pymongo import MongoClient
import hashlib
import urllib.parse

# Creating a new Flask app for MediSafe
app = Flask(__name__)

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
    # Generate a hash of the data.
    hash1 = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()

    # Store the hash of the data in MongoDB.
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


@app.route('/patient_auth', methods=['GET'])
def patient_auth():
    return render_template('patient_auth.html')


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


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Find the user record in the database.
    user = collection.find_one({'email': email})

    # Check if the user exists and the password is correct.
    if user and user['password'] == password:
        # Retrieve the record hash from the database
        record_hash = user['hash']

        # Generate the hash from the provided email and password
        provided_hash = hashlib.sha256(email.encode('utf-8') + password.encode('utf-8')).hexdigest()

        # Compare the hashes to validate the email and password
        if record_hash == provided_hash:
            # Login the user and display success message
            return render_template('patient_dash.html')
        else:
            # Hash mismatch, display error message
            return render_template('error.html', message="Invalid email or password")
    else:
        # User not found or password incorrect, display error message
        return render_template('error.html', message="Invalid email or password")


@app.route('/physician')
def physician():
    return render_template('physician.html')


@app.route('/records')
def records():
    return render_template('records.html')


if __name__ == "__main__":
    app.run(debug=True)
