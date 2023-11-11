from flask import Flask, request, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import hashlib
import datetime
import urllib.parse


class Block:
    def __init__(self, index, previous_hash, data, timestamp):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.previous_hash) + str(self.data) + str(self.timestamp)).encode())
        return sha.hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", datetime.datetime.now())

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True



blockchain = Blockchain()
app = Flask(__name__)

# Encode the special characters in the password
password = urllib.parse.quote("Winner@2001")

uri = "mongodb+srv://faithkimokiy:{password}@ehr.esz8clu.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['EHR']  # Use the name of your database

# Define a collection to store patient data
patientsauth_collection = db['patientsauth']


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/patient_auth', methods=['GET'])
def patient_auth():
    return render_template('patient_auth.html')


@app.route('/patient_auth', methods=['POST'])
def patient_auth_post():
    name = request.form['name']
    gender = request.form['gender']
    previous_records = request.form['previous_records']
    allergies = request.form['allergies']
    insurance_provider = request.form['insurance_provider']

    patient_data = {
        'name': name,
        'gender': gender,
        'previous_records': previous_records,
        'allergies': allergies,
        'insurance_provider': insurance_provider
    }

    # Add patient data to the blockchain
    new_block = Block(len(blockchain.chain), '', patient_data, datetime.datetime.now())
    blockchain.add_block(new_block)

    # Store patient data in MongoDB
    patientsauth_collection.insert_one(patient_data)

    return "Patient data registered successfully!"


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/physician')
def physician():
    return render_template('physician.html')


@app.route('/records')
def records():
    return render_template('records.html')


if __name__ == "__main__":
    app.run(debug=True)
