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
software_db_filename_extended = 'software.extended.json'

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

# POST multiple/all softwares to the database
@app.route('/api/v1/registerall', methods=['POST'])
def register_software_all():
    # get the data from the request
    data = request.get_json()
    # print(data)
    # check if the json is a valid json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    # the json must be a list
    list_software = data.get('software', [])
    if not list_software:
        return jsonify({'error': 'Invalid data'}), 400
    # go through the list of software
    already_registered = False
    for sw in list_software:
        # check if the json has the required fields
        if  not 'product' in sw or \
            not 'version' in sw or \
            not 'vendor' in sw:
            # just print the error and continue
            print('Missing data')
            continue
        # read the software from the file
        software_db = read_software_from_file(software_db_filename)
        # check if does not exist already in the database
        for software in software_db:
            if  software['product'] == sw['product'] and \
                software['version'] == sw['version'] and \
                software['vendor']  == sw['vendor']:
                # just print the error and continue
                print('Software already registered')
                already_registered = True
                break
        # if the software is already registered, continue
        if already_registered:
            continue
        # generate a UIID to the software
        sw['id'] = str(uuid.uuid4())
        # add the software to the database
        software_db.append(sw)
    # write the database to a file
    with open(software_db_filename, 'w') as f:
        json.dump({'software': software_db}, f)
    # print the database
    # print(software_db)
    # return ok
    return jsonify({'status': 'ok'}), 200

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
    # read the software from the file
    software_db = read_software_from_file(software_db_filename)
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
    # read the software from the file
    software_db = read_software_from_file(software_db_filename)
    # return the software
    return jsonify({'software': software_db}), 200


# DELETE a registered software by its id
@app.route('/api/v1/registered-id/<string:id>', methods=['DELETE'])
def delete_software_id(id):
    # read the software from the file
    software_db = read_software_from_file(software_db_filename)
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
    # read the software from the file
    software_db = read_software_from_file(software_db_filename)
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


# the home page
@app.route('/')
def home():
    return 'Welcome to the Vulnerability API!'

# return the web page with the list of registered software and links to the vluernability page
@app.route('/web/v1/toc', methods=['GET'])
def get_software_web_list():
    try:
        # read the template from the file
        with open('./toc.html') as f:  
            template = Template(f.read())
    except:
        # return not found web page
        return 'Not found', 404

    # return the rendered template
    return template.render()


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

# generate the toc file
def generate_toc():
    # read the software from the file
    software_db = read_software_from_file(software_db_filename_extended)
    # regenerate the toc.html file
    print("Regenerating toc.html")
    toc_template = Template(open('./templates/toc.jinja2.html').read())
    with open('data.toc.html', 'w') as f:
        f.write(toc_template.render(
            current_date = datetime.now(),
            software_list = software_db
        ))


# create a thread to update the database
def update_data():
    while True:
        # read the software from the file
        software_db = read_software_from_file(software_db_filename)
        # read the data from the CVE database for the software in the database
        for software in software_db:    
            print(software['vendor'], software['product'], software['version'])
            get_cves_for_product(software['vendor'], software['product'], software['version'])
            process_cves_for_product(software['vendor'], software['product'], software['version'])
        # generate the toc file
        generate_toc()
        # wait 1 hour
        print('Waiting 1 hour...')
        time.sleep(5*60)

# start the thread
thread = threading.Thread(target=update_data)
thread.start()

# run the app
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=80)
