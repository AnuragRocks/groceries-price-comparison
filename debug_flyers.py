"""
Debug script to see what flyers are available
"""

import requests
import json

base_url = "https://cdn-gateflipp.flippback.com/bf/flipp"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://flipp.com/'
}

postal_code = "M5H2N2"

# Get flyers
url = f"{base_url}/flyers"
params = {
    'postal_code': postal_code,
    'locale': 'en-CA'
}

try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    flyers = data.get('flyers', [])
    
    print(f"Found {len(flyers)} flyers\n")
    print("Available stores:")
    print("-" * 80)
    
    stores = {}
    for flyer in flyers:
        merchant = flyer.get('merchant_name', 'Unknown')
        if merchant not in stores:
            stores[merchant] = 0
        stores[merchant] += 1
    
    for store, count in sorted(stores.items()):
        print(f"  {store}: {count} flyer(s)")
    
    print("\n" + "=" * 80)
    print("Target stores we're looking for:")
    print("  - Food Basics")
    print("  - Walmart")
    print("  - FreshCo")
    print("  - Metro")
    print("  - No Frills")
    
except Exception as e:
    print(f"Error: {e}")
