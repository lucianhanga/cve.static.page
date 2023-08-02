# include the necessary libraries
import json
import sys
from datetime import datetime
from jinja2 import Template
import numpy as np

# function to create the file name from the product and version
def get_file_name(product, version):
  return 'data.'+ product + '.' + version + '.json'

# read the data from the file into the json object
def read_data_from_file(file_name):
  with open(file_name) as f:
    return json.load(f)

def filter_the_data(product, version):
  # read the data from the file
  cves = read_data_from_file(get_file_name(product, version))
  # the emrty array
  cves_list = []
  # iterate over the CVEs and select the signigicat fields
  for cve in cves['result']['CVE_Items']:
      # append to the array
      # Create an empty list
      cves_list.append(
        # a list of lists
        [
          # the CVE ID
          cve['cve']['CVE_data_meta']['ID'],
          # the last modified date
          cve['lastModifiedDate'],
          # the base score
          cve['impact']['baseMetricV3']['cvssV3']['baseScore'],
          # the base severity
          cve['impact']['baseMetricV3']['cvssV3']['baseSeverity'],
          # the description
          cve['cve']['description']['description_data'][0]['value'],
          # build the URL for the CVE in MITRE
          "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve['cve']['CVE_data_meta']['ID'],
        ]	
      )		
  # print(cves_list)
  return cves_list

# calculate the CVESS score
def calculate_cvss_score(cves_list):
  # get all the scores into a list
  cvss_scores = [float(cve[2]) for cve in cves_list]
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

# get the product and version from command line
product = sys.argv[1]
version = sys.argv[2]    
# call the function
cves_list = filter_the_data(product = product, version = version)
# print(cves_list)

# calculate the CVSS score
sscore = calculate_cvss_score(cves_list)
# print(sscore)

# jinja2 template rendering
template = Template(open('./templates/example3.jinja2').read())

# write the output to a file
with open('output.html', 'w') as f:
  f.write(template.render(
    current_date = datetime.now(),
    sscore = sscore,
    product = product, 
    version = version,
    cves_list=cves_list
  ))




