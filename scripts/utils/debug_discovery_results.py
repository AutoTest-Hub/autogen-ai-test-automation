import json
import os
from pathlib import Path

# Find the latest discovery results file
discovery_dir = Path("./work_dir/RealDiscoveryIntegration")
discovery_files = list(discovery_dir.glob("discovery_results_*.json"))
latest_file = max(discovery_files, key=os.path.getctime)

print(f"Reading file: {latest_file}")

# Load and analyze the file
with open(latest_file, 'r') as f:
    data = json.load(f)

print("\nDiscovery Results Structure:")
print(f"- application_url: {data.get('application_url')}")
print(f"- discovered_pages: {len(data.get('discovered_pages', []))} pages")
print(f"- page_elements: {len(data.get('page_elements', {}))} pages with elements")
print(f"- workflows: {len(data.get('workflows', []))} workflows")

print("\nPage Elements Structure:")
for page_name, page_data in data.get('page_elements', {}).items():
    print(f"\n- {page_name}:")
    print(f"  - url: {page_data.get('url')}")
    print(f"  - total_elements: {page_data.get('total_elements')}")
    
    elements = page_data.get('elements', {})
    print(f"  - elements: {list(elements.keys())}")
    
    for element_type, type_elements in elements.items():
        print(f"    - {element_type}: {len(type_elements)} elements")
        
        # Print first element of each type for inspection
        if type_elements:
            first_element = type_elements[0]
            print(f"      First {element_type} element keys: {list(first_element.keys())}")
            
            # Check for CSS selector
            if 'css' in first_element:
                print(f"      CSS selector example: {first_element.get('css')}")

