API_IXP_URL = "https://www.pch.net/api/ixp/directory/Active"
API_SUBNET_URL = "https://www.pch.net/api/ixp/subnets/"
OUTPUT_IPV4_FILE = "ix_ip4.csv"
OUTPUT_IPV6_FILE = "ix_ip6.csv"

from urllib.request import urlopen
import json
import csv

# Get the active IX Points
activeIxs = json.loads(urlopen(API_IXP_URL).read())
print(f'Found {len(activeIxs)} active IXs.')

ixPrefixesIP4 = []
ixPrefixesIP6 = []

# Get all active subnets for IXs
for index, ix in enumerate(activeIxs):
    requestUrl = API_SUBNET_URL + ix['id']
    subnets = json.loads(urlopen(requestUrl).read())
    print(f"Loaded {len(subnets)} prefixes for {ix['name']}")
    for subnet in subnets:
        # Ignore if required fields do not exist
        if not 'status' in subnet or subnet['status'] == None: continue
        if not 'subnet' in subnet or subnet['subnet'] == None: continue
        if not 'short_name' in subnet or subnet['short_name'] == None: continue

        # Ignore inactive subnets
        if subnet['status'] != 'Active': continue

        # Trim out whitespace
        subnet['subnet'] = subnet['subnet'].strip()
        subnet['short_name'] = subnet['short_name'].strip()

        # Ignore subnet if it is empty
        if subnet['subnet'] == '': continue
        if subnet['short_name'] == '': continue

        # Add the subnet
        prefix = [subnet['subnet'], subnet['short_name']]
        if subnet['version'] == 'IPv4':
            ixPrefixesIP4.append(prefix)
        else:
            ixPrefixesIP6.append(prefix)
    print(f'Processed {index+1}/{len(activeIxs)} IXs')

# Save the subnets to a file
def save(array, file):
    print(f'Saving to file {file}')
    csvFile = open(file, 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvFile)
    # Write the headings
    writer.writerow(['Prefix', 'Name'])
    # Write the subnets
    writer.writerows(array)
save(ixPrefixesIP4, OUTPUT_IPV4_FILE)
save(ixPrefixesIP6, OUTPUT_IPV6_FILE)

print('Done')
