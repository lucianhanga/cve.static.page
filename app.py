import json
import sys
from datetime import datetime
import time
from flask import Flask, jsonify, request
from jinja2 import Template
import uuid
import threading

# import a file from the current folder 
from get_cves import get_cves_for_product
from process_cves import process_cves_for_product

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
    if not 'product' in data or not 'version' in data or not 'vendor' in data:
        return jsonify({'error': 'Missing data'}), 400
    # check if does not exist already in the database
    for software in software_db:
        if  software['product'] == data['product'] and \
            software['version'] == data['version'] and \
            software['vendor']  == data['vendor']:
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


# return the web page with the registered software and version
@app.route('/web/v1/registered/<string:vendor>/<string:product>/<string:version>', methods=['GET'])
def get_software_web(vendor, product, version):
    try:
        # read the template from the file composed by poroduct and version
        with open(f"./data.{vendor}.{product}.{version}.html") as f:  
            template = Template(f.read())
    except:
        # return not found web page
        return 'Not found', 404

    # return the rendered template
    return template.render()


# read the data from the file into the json object
software_db = read_software_from_file(software_db_filename)

# create a thread to update the database
def update_database():
    while True:
        # read the data from the CVE database for the software in the database
        for software in software_db:
            print(software['vendor'], software['product'], software['version'])
            get_cves_for_product(software['vendor'], software['product'], software['version'])
            process_cves_for_product(software['vendor'], software['product'], software['version'])
                        
        # wait 1 hour
        print('Waiting 1 hour...')
        time.sleep(5*60)

# start the thread
thread = threading.Thread(target=update_database)
thread.start()

# run the app
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=80)
