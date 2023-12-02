from flask import Flask, render_template, request, jsonify
import json
from pymongo import MongoClient
import hashlib
from datetime import datetime, timezone
import urllib.parse
from werkzeug.security import generate_password_hash, check_password_hash

# Creating a new Flask app for MediSafe
app: Flask = Flask(__name__)

# Escaping the username and password
username = urllib.parse.quote_plus("faithkimokiy")
password = urllib.parse.quote_plus("Winner2001")

# Creating a Mongodb connection
client = MongoClient(
    "mongodb+srv://{}:{}@ehr.sihily9.mongodb.net/?retryWrites=true&w=majority".format(username, password))
db = client["ehr"]
collection1 = db['patient_record']
collection2 = db['physician_record']
collection3 = db['physician_access']
collection4 = db['access_requests']


# PATIENT MODULE
# Blockchain class for managing patients' blocks
class Blockchain:
    def __init__(self, collection1):
        self.chain = []
        self.collection1 = collection1
        self.collection3 = collection3
        self.collection4 = collection4
        self.current_id = 1  # Used to uniquely identify patients

    def create_genesis_block(self, data):
        genesis_block = Block('0', data)
        self.chain.append(genesis_block)
        store_block(genesis_block, self.collection1)

    def add_block(self, data):
        if not self.chain:
            # Create a genesis block if the chain is empty
            self.create_genesis_block(data)
        else:
            previous_block = self.chain[-1]
            new_block = Block(self.current_id, previous_block.hash, data)
            self.current_id += 1  # Incrementing the ID for the next block
            self.chain.append(new_block)
            store_block(new_block, self.collection1)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_patient_data_by_email(self, patient_email):
        block_data = collection1.find_one({'data.patient_email': {'$regex': f'^{patient_email}$', '$options': 'i'}})
        if block_data is not None:
            return block_data['data']
        return None


# Recursive function to convert sets to lists
def convert_sets_to_lists(data):
    if isinstance(data, set):
        return list(data)
    elif isinstance(data, dict):
        return {key: convert_sets_to_lists(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_sets_to_lists(item) for item in data]
    else:
        return data


# This class will represent each patient's block in the chain
class Block:
    def __init__(self, previous_hash, data):
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = datetime.now(timezone.utc)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        if self.data is not None:
            # Convert sets to lists before hashing
            data_for_hashing = convert_sets_to_lists(self.data)

            # Serializing the data to JSON, and handling non-serializable types (some of the self.data cannot be
            # serialized to JSON) The default=str will use the str function to convert non-serializable types to strings
            block_data_str = json.dumps(data_for_hashing, default=str, sort_keys=True)
            block_data_bytes = block_data_str.encode('utf-8')
            block_hash = hashlib.sha256(block_data_bytes).hexdigest()
            return block_hash
        else:
            return None


# This function stores block data in the mongodb
def store_block(block, collection1):
    collection1.insert_one({
        'hash': block.hash,
        'data': block.data
    })


# This function will retrieve block data from MongoDB
def get_block_data(block_hash, collection1):
    block_data = collection1.find_one({'hash': block_hash})
    if block_data is not None:
        return block_data['data']
    else:
        return None


# PHYSICIAN MODULE
# Blockchain class for managing physicians' blocks
class Blockchain1:
    def __init__(self, collection2):
        self.chain = []
        self.collection2 = collection2
        self.current_id = 1  # Initialize with 1, you can adjust as needed

    def create_genesis_block1(self, data):
        genesis_block = Block1('0', data)
        self.chain.append(genesis_block)
        store_block(genesis_block, self.collection2)

    def add_block1(self, data):
        if not self.chain:
            # Create a genesis block if the chain is empty
            self.create_genesis_block1(data)
        else:
            previous_block = self.chain[-1]
            new_block = Block1(self.current_id, previous_block.hash, data)
            self.current_id += 1  # Incrementing the ID for the next block
            self.chain.append(new_block)
            store_block(new_block, self.collection2)

    def is_valid1(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_physician_data_by_email(self, physician_email):
        block_data = collection2.find_one({'data.physician_email': {'$regex': f'^{physician_email}$', '$options': 'i'}})
        if block_data is not None:
            return block_data['data']
        return None


    def search_patient_by_id(self, patient_id):
        for block in self.chain:
            if block.data.get('id') == patient_id:
                return block.data
            return None


# This class will represent each block in the physician chain
class Block1:
    def __init__(self, previous_hash, data):
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = datetime.now(timezone.utc)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        if self.data is not None:
            # Convert sets to lists before hashing
            data_for_hashing = convert_sets_to_lists(self.data)

            # Serializing the data to JSON, and handling non-serializable types (some of the self.data cannot be
            # serialized to JSON) The default=str will use the str function to convert non-serializable types to strings
            block_data_str = json.dumps(data_for_hashing, default=str, sort_keys=True)
            block_data_bytes = block_data_str.encode('utf-8')
            block_hash = hashlib.sha256(block_data_bytes).hexdigest()
            return block_hash
        else:
            return None


# This function stores block data in the mongodb
def store_block1(block, collection2):
    collection2.insert_one({
        'hash': block.hash,
        'data': block.data
    })


# This function will retrieve block data from MongoDB
def get_block1_data(block_hash, collection2):
    block_data = collection2.find_one({'hash': block_hash})
    if block_data is not None:
        return block_data['data']
    else:
        return None


@app.route('/')
def home():
    return render_template('home.html')


# Create an instance of Blockchain
blockchain = Blockchain(collection1)
blockchain1 = Blockchain1(collection2)


# PATIENT AUTHENTICATION
@app.route('/patient_auth', methods=['GET', 'POST'])
def patient_auth():
    if request.method == 'GET':
        return render_template('patient_auth.html')

    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            # Extract login data from request
            patient_email = request.form.get('patient_email')
            password = request.form.get('password')

            # Retrieve corresponding hashed password and email from the database
            patient_records = blockchain.get_patient_data_by_email(patient_email)
            print("Retrieved patient records", patient_records)

            if patient_records is not None:
                stored_password_hash = patient_records['password']
                # Verify the password
                if check_password_hash(stored_password_hash, password):
                    return jsonify({'message': 'Login successful'})
                else:
                    return jsonify({'message': 'Invalid credentials'})
            else:
                return jsonify({'message': 'Invalid email address'})

        # Handle registration action
        elif action == 'register':
            # Extract registration data from request
            name = request.form.get('name')
            gender = request.form.get('gender')
            patient_email = request.form.get('patient_email')
            password = request.form.get('password')
            medical_records = request.form.get('medical_records')
            allergies = request.form.get('allergies')
            insurance_provider = request.form.get('insurance_provider')

            # Hash the password for storage
            hashed_password = generate_password_hash(password)

            # Patient registration data
            patient_data = {
                'name': name,
                'gender': gender,
                'patient_email': patient_email.lower(),
                'password': hashed_password,
                'medical_records': medical_records,
                'allergies': allergies,
                'insurance_provider': insurance_provider
            }

            # Debug print
            print("Patient Data:", patient_data)

            # Check if there is a previous block for the patient
            previous_block = collection1.find_one({'patient_email': patient_email})

            # If there is no previous block, set the previous_hash to the genesis block hash
            if previous_block is None:
                previous_hash = '0'
            else:
                previous_hash = previous_block['hash']

            # Create a new block with patient data
            patient_block = Block(previous_hash, patient_data)

            # Store the block in the patient_blocks collection
            blockchain.add_block(patient_data)

            # Return success message
            return jsonify({'message': 'Registration successful'})

        else:
            raise ValueError('Invalid action: {}'.format(action))

    return jsonify({'message': 'NO POST/GET'})


# Physician Authentication
@app.route('/physician_auth', methods=['GET', 'POST'])
def physician_auth():
    if request.method == 'GET':
        return render_template('physician_auth.html')

    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            # Extract login data from request
            physician_email = request.form.get('physician_email')
            password = request.form.get('password')

            # Retrieve corresponding hashed password and email from the database
            physician_records = blockchain1.get_physician_data_by_email(physician_email)
            print("Retrieved physician records", physician_records)

            if physician_records is not None:
                stored_password_hash = physician_records['password']
                # Verify the password
                if check_password_hash(stored_password_hash, password):
                    return jsonify({'message': 'Login successful'})
                else:
                    return jsonify({'message': 'Invalid credentials'})
            else:
                return jsonify({'message': 'Invalid email address'})

        # Handle registration action
        elif action == 'register':
            # Extract registration data from request
            name = request.form.get('name')
            physician_email = request.form.get('physician_email')
            password = request.form.get('password')
            specialty = request.form.get('specialty')

            # Hash the password for storage
            hashed_password = generate_password_hash(password)

            # Physician registration data
            physician_data = {
                'name': name,
                'physician_email': physician_email.lower(),
                'password': hashed_password,
                'specialty': specialty
            }

            # Debug print
            print("Physician Data:", physician_data)

            # Check if there is a previous block for the physician
            previous_block = collection2.find_one({'physician_email': physician_email})

            # If there is no previous block, set the previous_hash to the genesis block hash
            if previous_block is None:
                previous_hash = '0'
            else:
                previous_hash = previous_block['hash']

            # Create a new block with physician data
            physician_block = Block1(previous_hash, physician_data)

            # Store the block in the physician_blocks collection
            blockchain1.add_block1(physician_data)

            # Return success message
            return jsonify({'message': 'Registration successful'})

        else:
            raise ValueError('Invalid action: {}'.format(action))

    return jsonify({'message': 'NO POST/GET'})


@app.route('/patient_dashboard')
def patient_dash():
    return render_template('patient_dash.html')


@app.route('/patient_account')
def patient_account():
    return render_template('patient_account.html')


@app.route('/edit_patient_account')
def edit_patient():
    return render_template('edit_patient_account.html')




if __name__ == "__main__":
    app.run(debug=True)
