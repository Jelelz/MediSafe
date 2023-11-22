from flask import Flask, render_template, request, jsonify
'''redirect, url_for'''
import json
from pymongo import MongoClient
import hashlib
from datetime import datetime
import urllib.parse
# for password hashing
import bcrypt
# for encryption
from cryptography.fernet import Fernet

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


# Blockchain class for managing blocks
class Blockchain:
    def __init__(self, collection1):
        self.chain = []
        self.collection1 = collection1

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
            new_block = Block(previous_block.hash, data)
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


# This class will represent each block in the chain
class Block:
    def __init__(self, previous_hash, data):
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = datetime.utcnow()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        if self.data is not None:
            block_data = json.dumps(self.data, sort_keys=True).encode('utf-8')
            block_hash = hashlib.sha256(block_data).hexdigest()
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


# Generate a key for encryption (keep this secret and don't share it)
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)


# Function to encrypt data
def encrypt_data(data):
    if data is not None:
        encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
        return encrypted_data
    else:
        return None


# Function to decrypt data
def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/physician')
def physician_view():
    return render_template('physician.html')


# Create an instance of Blockchain
blockchain = Blockchain(collection1)


@app.route('/patient_auth', methods=['GET', 'POST'])
def patient_auth():
    if request.method == 'GET':
        return render_template('patient_auth.html')

    elif request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            # Extract login data from request
            email = request.form.get('email')
            password = request.form.get('password')

            # Retrieve corresponding hashed password from the database
            patient_record = collection1.find_one({'email': encrypt_data(email)})
            if patient_record is not None:
                stored_password_hash = patient_record['password']

                # Verify the password
                if bcrypt.check_password_hash(stored_password_hash, password):
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
            email = request.form.get('email')
            password = request.form.get('password')
            medical_records = request.form.get('medical_records')
            allergies = request.form.get('allergies')
            insurance_provider = request.form.get('insurance_provider')

            # Encrypt sensitive data
            encrypted_name = encrypt_data(name)
            encrypted_gender = encrypt_data(gender)
            encrypted_email = encrypt_data(email)
            encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            encrypted_medical_records = encrypt_data(medical_records)
            encrypted_allergies = encrypt_data(allergies)
            encrypted_insurance_provider = encrypt_data(insurance_provider)

            # Patient registration data
            patient_data = {
                'name': encrypted_name,
                'gender': encrypted_gender,
                'email': encrypted_email,
                'password': encrypted_password,
                'medical_records': encrypted_medical_records,
                'allergies': encrypted_allergies,
                'insurance_provider': encrypted_insurance_provider
            }

            # Check if there is a previous block for the patient
            previous_block = collection1.find_one({'email': encrypted_email})

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


# I want to see the structure of the blockchain
def print_blockchain_structure():
    for i, block in enumerate(blockchain.chain):
        print(f"Block {i + 1}:")
        print(json.dumps(block.data, indent=2))
        print("Hash: ", block.hash)
        print("Previous Hash: ", block.previous_hash)
        print("Timestamp: ", block.timestamp)
        print("=" * 30)


if __name__ == "__main__":
    app.run(debug=True)
