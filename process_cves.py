# include the necessary libraries
import json
import sys
from datetime import datetime
from jinja2 import Template
import numpy as np

# function to create the file name from the product and version
def build_input_file_name(vendor, product, version):
  return f"data.{vendor}.{product}.{version}.raw.json"

def build_output_html_file_name(vendor, product, version):
  return f"data.{vendor}.{product}.{version}.html"

def build_output_json_file_name(vendor, product, version):
  return f"data.{vendor}.{product}.{version}.json"

# read the data from the file into the raw json object
def read_data_from_raw_file(file_name):
  with open(file_name) as f:
    return json.load(f)

def filter_the_data(vendor, product, version):
  # read the data from the file
  try:
    cves = read_data_from_raw_file(build_input_file_name(vendor, product, version))
  except:
    print(f"Error reading file {build_input_file_name(vendor, product, version)}")
    return []
  
  # create an empty array
  cves_list = []
  # iterate over the CVEs and select the signigicat fields
  for cve in cves['vulnerabilities']:
      # append to the array
      cves_list.append(
        # a list of objects
        {
          # the CVE ID
          'id' : cve['cve']['id'],
          # the last modified date
          'lastModified' : cve['cve']['lastModified'],
          # the description
          'description' : cve['cve']['descriptions'][0]['value'],
          # the base score
          'baseScore' : cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore'],
          # the base severity
          'baseSeverity' : cve['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseSeverity'],
          # build the URL for the CVE in MITRE
          'url' : f"https://www.cve.org/CVERecord?id={cve['cve']['id']}",
        }
      )		
    # print(cves_list)
  # write it into the output json file
  print("Writing data to " + build_output_json_file_name(vendor, product, version))
  with open(build_output_json_file_name(vendor, product, version), 'w') as outfile:
    json.dump(obj = cves_list, fp=outfile, indent=2)
  return cves_list

# calculate the CVESS score
def calculate_cvss_score(cves_list):
  # get all the scores into a list
  cvss_scores = [float(cve['baseScore']) for cve in cves_list]
  # group the scores by severity
  # cvss_scores_critical = [float(cve[2]) for cve in cves_list if cve[3] == 'CRITICAL']
  # cvss_scores_high = [float(cve[2]) for cve in cves_list if cve[3] == 'HIGH']
  # cvss_scores_medium = [float(cve[2]) for cve in cves_list if cve[3] == 'MEDIUM']
  # cvss_scores_low = [float(cve[2]) for cve in cves_list if cve[3] == 'LOW']
  # # print all the scores
  # print("all: " + cvss_scores)
  # print(cvss_scores_critical)
  # print(cvss_scores_high)
  # print(cvss_scores_medium)
  # print(cvss_scores_low)
  # Average CVSS score reduce number of decimal places to two
  if len(cvss_scores) == 0:
    return 0
  return round(np.mean(cvss_scores), 2)


def update_the_data(vendor, product, version, sscore, cves_list):
  # rewrite the extended json file
  software_db = { 'software': [ ] }
  try:
    with open('software.extended.json') as f:
      software_db = json.load(f)
  except:
    print("Error reading file software.extended.json")
    software_db = { 'software': [ ] }

  # update the software.json file
  # print(software_db)
  for software in software_db['software']:
    # check if the currently processed product is in the database
    if  software['product'] == product and \
        software['version'] == version and \
        software['vendor'] == vendor:
      print(f"Updating data for {vendor}.{product}.{version}")
      # print(software)
      # update the data
      software['sscore'] = sscore
      software['cves'] = len(cves_list)
      # html file name
      software['html'] = build_output_html_file_name(vendor, product, version)
      # json file name
      software['json'] = build_output_json_file_name(vendor, product, version)
      # raw json file name
      software['raw'] = build_input_file_name(vendor, product, version)
      # write the output to a file
      with open('software.extended.json', 'w') as f:
        json.dump(obj = software_db, fp = f, indent=2)
      return
  # if the product is not in the database, add it
  print(f"Adding data for {vendor}.{product}.{version}")
  software_db['software'].append(
    {
      'vendor': vendor,
      'product': product,
      'version': version,
      'sscore': sscore,
      'cves': len(cves_list),
      'html': build_output_html_file_name(vendor, product, version),
      'json': build_output_json_file_name(vendor, product, version),
      'raw': build_input_file_name(vendor, product, version)
    }
  )
  # write the output to a file
  with open('software.extended.json', 'w') as f:
    json.dump(obj = software_db, fp = f, indent=2)

# process the data
def process_cves_for_product(vendor, product, version):
  # filter the data
  print(f"Filtering data for {vendor}.{product}.{version}")
  cves_list = filter_the_data(vendor, product, version)
  print(f"Found {len(cves_list)} CVEs")
  # calculate the CVSS score
  sscore = calculate_cvss_score(cves_list)
  # jinja2 template rendering
  template = Template(open('./templates/software.jinja2.html').read())
  # write the output to a file
  with open(build_output_html_file_name(vendor, product, version), 'w') as f:
    f.write(template.render(
      current_date = datetime.now(),
      sscore = sscore,
      product = product, 
      version = version,
      cves_list=cves_list
    ))
  # update the software.json file
  update_the_data(vendor, product, version, sscore, cves_list)


# execute the code if the file is run directly
if __name__ == "__main__":
  # get the product and version from command line
  vendor = sys.argv[1]
  product = sys.argv[2]
  version = sys.argv[3]    
  # process the data
  process_cves_for_product(vendor, product, version)


