import requests
import sys
import json

def get_cves_for_product(product, version):
    # Define base URL for the NVD API
    base_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
    params = {
        "cpeMatchString": f"cpe:2.3:a:*:{product}:{version}:*:*:*:*:*:*:*",  # Define CPE name
        "resultsPerPage": 2000  # Request a large number of results per page
    }

    # Send a GET request to the NVD API
    response = requests.get(base_url, params=params)

    # Ensure the request was successful
    response.raise_for_status()

    # Decode the response
    data = response.json()

    # save to file and append version to the filename
    # how to append the version ? 
    with open('data.'+ product + '.' + version + '.raw.json', 'w') as outfile:
        json.dump(data, outfile)

    # Extract the CVEs
    cves = [item['cve']['CVE_data_meta']['ID'] for item in data['result']['CVE_Items']]
    return cves


# run the script if it is called from the command line
if __name__ == "__main__":
    # get the version and product from the command line
    product = sys.argv[1]
    version = sys.argv[2]
    # Call with the product and version
    # e.g. jira_data_center 8.19
    # e.g. jira 8.19
    cves = get_cves_for_product(product, version)
    print(f"The CVEs for {product} version {version} are: {cves}")
