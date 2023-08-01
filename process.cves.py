# include the necessary libraries
import json
import sys
from datetime import datetime
from jinja2 import Template

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


# get the product and version from command line
product = sys.argv[1]
version = sys.argv[2]    
# call the function
cves_list = filter_the_data(product = product, version = version)
# print(cves_list)

# get the current date
current_date = datetime.now()


# jinja2 template rendering
# read the template from the file
# template = Template(open('./templates/example1.jinja2').read())
template = Template(open('./templates/example3.jinja2').read())

# write the output to a file
with open('output.html', 'w') as f:
  f.write(template.render(
    current_date = current_date,
    product = product, 
    version = version,
    cves_list=cves_list
  ))




