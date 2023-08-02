import json
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from jinja2 import Template
import uuid

software_db_filename = 'software.json'
software_db = []

# read all the registered software from a file
def read_software_from_file(filename):
    try:
        with open(filename) as f:
            return json.load(f).get('software', [])
    except:
        # create the file if it does not exist
        with open(filename, 'w') as f:
            json.dump({'software': []}, f)
    return []

# create the Flask app
app = Flask(__name__)

# the home page
@app.route('/')
def home():
    return 'Welcome to the Vulnerability API!'

# POST to add a new software and its version
@app.route('/api/v1/register', methods=['POST'])
def register_software():
    # get the data from the request
    data = request.get_json()
    # print(data)
    # check if the json is a valid json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    # check if the json has the required fields
    if not 'product' in data or not 'version' in data:
        return jsonify({'error': 'Missing data'}), 400
    # check if does not exist already in the database
    for software in software_db:
        if software['product'] == data['product'] and software['version'] == data['version']:
            return jsonify({'error': 'Software already registered'}), 400
    # generate a UIID to the software
    data['id'] = str(uuid.uuid4())
    # add the software to the database
    software_db.append(data)
    # write the database to a file
    with open(software_db_filename, 'w') as f:
        json.dump({'software': software_db}, f)
    # print the database
    print(software_db)
    # return ok
    return jsonify({'status': 'ok'}), 200

# GET all the registered software
@app.route('/api/v1/registered', methods=['GET'])
def get_software():
    # return the software
    return jsonify({'software': software_db}), 200


# DELETE a registered software by its id
@app.route('/api/v1/registered-id/<string:id>', methods=['DELETE'])
def delete_software_id(id):
    # check if the software exists
    for software in software_db:
        if software['id'] == id:
            # delete the software
            software_db.remove(software)
            # write the database to a file
            with open(software_db_filename, 'w') as f:
                json.dump({'software': software_db}, f)
            # return ok
            return jsonify({'status': 'ok'}), 200
    # return not found
    return jsonify({'error': 'Software not found'}), 404

# DELETE all the registered software by its product
@app.route('/api/v1/registered-product/<string:product>', methods=['DELETE'])
def delete_software_product(product):
    # check if the software exists
    count = 0
    for software in software_db:
        if software['product'] == product:
            # delete the software
            software_db.remove(software)
            count += 1
    if count > 0:
        # write the database to a file
        with open(software_db_filename, 'w') as f:
            json.dump({'software': software_db}, f)
        # return ok
        return jsonify({'status': 'ok', 'count' : count}), 200 
    # return not found
    return jsonify({'error': 'Software not found'}), 404

# read the data from the file into the json object
software_db = read_software_from_file(software_db_filename)


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)