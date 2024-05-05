API_IXP_URL = "https://www.pch.net/api/ixp/directory/Active"
API_SUBNET_URL = "https://www.pch.net/api/ixp/subnets/"
OUTPUT_IPV4_FILE = "ix_ip4.csv"
OUTPUT_IPV6_FILE = "ix_ip6.csv"

from urllib.request import urlopen
import json
import csv
import ipaddress

# Get the active IX Points
activeIxs = json.loads(urlopen(API_IXP_URL).read())
print(f'Found {len(activeIxs)} active IXs.')

# Use dictionaries to remove duplicates
ixPrefixesIP4 = {}
ixPrefixesIP6 = {}

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

        # Add manually the mask to LUBIX v4
        if subnet['subnet'] == '196.60.64.0' and subnet['short_name'] == 'LUBIX v4':
            subnet['subnet'] = '196.60.64.0/24'
        
        # Detect the IP version from the address because the reported version doesn't always match
        ip_version = 0
        try:
            network = ipaddress.ip_network(subnet['subnet'], strict=False)
            ip_version = network.version # 4 or 6
        except ValueError:
            print(f"Warning! '{subnet['subnet']}' not recognized as a valid IP v4 or v6 address. Skipping.")
            continue

        # Add the subnet
        if ip_version == 4:
            ixPrefixesIP4[subnet['subnet']] = subnet['short_name']
        elif ip_version == 6:
            ixPrefixesIP6[subnet['subnet']] = subnet['short_name']
    print(f'Processed {index+1}/{len(activeIxs)} IXs')

# Save the subnets to a file
def save(dictionary, file):
    print(f'Saving to file {file}')
    csvFile = open(file, 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvFile)
    # Write the headings
    writer.writerow(['Prefix', 'Name'])
    # Write the subnets in sorted order
    writer.writerows(map(lambda key: [key, dictionary[key]] , sorted(dictionary)))
save(ixPrefixesIP4, OUTPUT_IPV4_FILE)
save(ixPrefixesIP6, OUTPUT_IPV6_FILE)

print('Done')
