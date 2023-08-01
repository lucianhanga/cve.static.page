# include the necessary libraries
import json
import sys
from jinja2 import Template 

# function to create the file name from the product and version
def get_file_name(product, version):
  return 'data.'+ product + '.' + version + '.json'

# read the data from the file into the json object
def read_data_from_file(file_name):
  with open(file_name) as f:
    return json.load(f)
    
# get the product and version from command line
product = sys.argv[1]
version = sys.argv[2]    

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
print(cves_list)

# jinja2 template rendering
# read the template from the file
template = Template(open('./templates/example1.jinja2').read())
# render the template
print(template.render(cves_list=cves_list))
# write the output to a file
with open('output.html', 'w') as f:
  f.write(template.render(cves_list=cves_list))




