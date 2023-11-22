# Import necessary libraries
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from pymongo import MongoClient
from cryptography.fernet import Fernet
import hashlib
import urllib.parse
import datetime
import subprocess

# Escape the username and password
username = urllib.parse.quote_plus("faithkimokiy")
password = urllib.parse.quote_plus("Winner2001")

# Creating a Mongodb connection
client = MongoClient("mongodb+srv://{}:{}@ehr.sihily9.mongodb.net/?retryWrites=true&w=majority".format(username, password))
db = client["ehr"]
collection1 = db['patient_record']


# Creating a new Flask app for MediSafe
app: Flask = Flask(__name__)


# A BLOCKCHAIN CLASS FOR MANAGING BLOCKS
class Blockchain:
    def __init__(self):
        self.chain = []

    def create_genesis_block(self, data):
        genesis_block = Block('0', data)
        self.chain.append(genesis_block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(previous_block.hash, data)
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


# A BLOCK CLASS FOR REPRESENTING EACH BLOCK IN THE CHAIN
class Block:
    def __init__(self, previous_hash, data):
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = datetime.utcnow()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = json.dumps(self.data, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_data).hexdigest()
        return block_hash


# Generate a Fernet key using openssl
fernet_key_process = subprocess.Popen(['openssl', 'rand', '-base64', '32'], stdout=subprocess.PIPE)
fernet_key = fernet_key_process.communicate()[0].decode('utf-8').strip()

# Define Fernet key for encryption
fernet = Fernet(fernet_key)


# Function to encrypt data using Fernet key
def encrypt_data(data):
    encrypted_data = fernet.encrypt(json.dumps(data).encode('utf-8'))
    return encrypted_data


# Function to decrypt data using Fernet key
def decrypt_data(encrypted_data):
    data = json.loads(fernet.decrypt(encrypted_data).decode('utf-8'))
    return data


# Function to store block data in MongoDB
def store_block(block, collection1):
    db[collection1].insert_one({
        'hash': block.hash,
        'data': block.data
    })


# Function to retrieve block data from MongoDB
def get_block_data(block_hash, collection1):
    block_data = db[collection1].find_one({'hash': block_hash})
    if block_data is not None:
        return block_data['data']
    else:
        return None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    # Extract registration data from request
    data = request.get_json()
    name = data['name']
    gender = data['gender']
    email = data['email']
    password = data['password']
    previous_records = data['previous_records']
    allergies = data['allergies']
    insurance_provider = data['insurance_provider']

    # ... Generate unique hash for patient record ...
    hash_value = hashlib.sha256(data.encode('utf-8')).hexdigest()

    # ... Encrypt patient data using Fernet key ...
    encrypted_data = encrypt_data(data)

    # Check if there is a previous block for the patient
    previous_block = db['patient_blocks'].find_one({'hash': hash_value})

    # If there is no previous block, set the previous_hash to the genesis block hash
    if previous_block is None:
        previous_hash = '0'
    else:
        previous_hash = previous_block['hash']

    # Create a new block with encrypted patient data
    patient_block = Block(previous_hash, encrypted_data)

    # Store the block in the patient_blocks collection
    store_block(patient_block, 'patient_blocks')

    # Return success message
    return jsonify({'message': 'Registration successful'})


@app.route('/patient_auth')
def patient_auth():
    return render_template('patient_auth.html')


if __name__ == "__main__":
    app.run(debug=True)
