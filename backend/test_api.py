import requests
import json

# Test the search API
url = "http://127.0.0.1:5000/search"
payload = {
    "search_term": "chicken breast",
    "sort_by": "price"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFound {data['count']} results for '{data['search_term']}'\n")
        
        if data['results']:
            print("Top 5 results:")
            for i, product in enumerate(data['results'][:5], 1):
                print(f"\n{i}. {product['product_name']}")
                print(f"   Price: {product['price_display']}")
                print(f"   Store: {product['store']}")
                print(f"   Quantity: {product['quantity']} {product['unit']}")
        else:
            print("No results found!")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
