import requests
import sys
import json

def get_cves_for_product(vendor, product, version):
    # Define base URL for the NVD API
    # old # base_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "cpeName" : f"cpe:2.3:a:{vendor}:{product}:{version}:*:*:*:*:*:*:*",  # Define CPE name
        # old #"cpeMatchString": f"cpe:2.3:a:*:{product}:{version}:*:*:*:*:*:*:*",  # Define CPE name
        "resultsPerPage": 2000  # Request a large number of results per page
    }

    # print generated url and params
    print(f"GET: {base_url}")
    print(params)
    
    # Send a GET request to the NVD API
    response = requests.get(base_url, params=params)

    # Ensure the request was successful
    response.raise_for_status()

    # Decode the response
    data = response.json()

    # save to file and append version to the filename
    # how to append the version ? 
    with open(f"data.{vendor}.{product}.{version}.raw.json", 'w') as outfile:
        json.dump(data, outfile)


# run the script if it is called from the command line
if __name__ == "__main__":
    # get the version and product from the command line
    vendor = sys.argv[1]
    product = sys.argv[2]
    version = sys.argv[3]
    # Call with the product and version
    # e.g. atlassian jira_data_center 8.19
    get_cves_for_product(vendor, product, version)
